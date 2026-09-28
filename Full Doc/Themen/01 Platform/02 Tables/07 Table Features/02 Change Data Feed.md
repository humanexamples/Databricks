# Change Data Feed

„Change Data Feed (CDF) verfolgt zeilenweise Änderungen zwischen Versionen einer Delta-Lake-Tabelle oder Apache-Iceberg-v3-Tabelle." Jeder Änderungsdatensatz enthält Zeilendaten plus Metadaten, die angeben, ob die Zeile eingefügt, aktualisiert oder gelöscht wurde. Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Gängige Anwendungsfälle

- Inkrementelle ETL-Pipelines, die nur seit dem letzten Lauf geänderte Zeilen verarbeiten.
- Audit-Trails für Compliance und Governance-Nachverfolgung.
- Datenreplikation zur Synchronisierung von Änderungen in nachgelagerte Systeme.

## 2. Zwei Ansätze

| Ansatz | Beschreibung |
|---|---|
| **Automatic CDF** (Public Preview) | berechnet Änderungen zur Query-Zeit anhand von Row Lineage; keine tabellenspezifische Konfiguration nötig; funktioniert auf Delta-Lake- und Iceberg-v3-Tabellen |
| **Legacy CDF** | materialisiert Änderungen beim Schreiben; nur Delta Lake; erfordert individuelle Tabellenkonfiguration |

Automatic CDF „verbessert die Schreib-Performance und reduziert Storage-Kosten" gegenüber Legacy CDF, nutzt aber dieselben APIs (`table_changes()`, `readChangeFeed`) und ist mit Batch-Queries, Structured Streaming sowie Databricks-zu-Databricks-Delta-Sharing kompatibel. Legacy und Automatic CDF lassen sich **nicht gleichzeitig** auf derselben Tabelle nutzen.

## 2a. Zwei Lese-APIs: `table_changes()` vs. `readChangeFeed`

Unabhängig davon, ob eine Tabelle Legacy oder Automatic CDF nutzt (nicht zu verwechseln mit der Wahl zwischen den beiden CDF-**Ansätzen** oben) gibt es zwei gleichwertige Wege, die Änderungsdaten zu **lesen** — je nachdem, ob SQL oder Python/Scala genutzt wird.

**`table_changes()`** — eine SQL-**Table-Valued-Function**, direkt in `SELECT` nutzbar:

```sql
SELECT * FROM table_changes('tableName', 0, 10);
```

**`readChangeFeed`** — keine Funktion, sondern eine **Option** des `DataFrameReader`/`DataStreamReader` in Python/Scala, die einen normalen Batch- oder Streaming-Read in einen CDF-Read umschaltet:

```python
spark.read.option("readChangeFeed", "true").option("startingVersion", 0).table("tableName")
```

Beide liefern dasselbe Ergebnis-Schema — die normalen Tabellenspalten plus die drei CDF-Metadatenspalten `_change_type`/`_commit_version`/`_commit_timestamp` (Abschnitt 4) — und funktionieren identisch unabhängig davon, ob die Tabelle Legacy oder Automatic CDF nutzt: Die Migration zwischen beiden (Abschnitt 7) ändert nur, *wie* die Änderungen intern berechnet werden, nicht die Lese-API.

## 3. Automatic Change Data Feed aktivieren

**Voraussetzungen:** Databricks Runtime 18 LTS oder höher; Tabellen müssen in Unity Catalog registriert sein und eines der folgenden Formate haben: Managed- oder External-Delta-Lake-Tabelle mit aktiviertem Row Tracking (siehe [11 Row Tracking.md](11%20Row%20Tracking.md)), oder Iceberg-v3-Tabelle.

**Batch-Lesen (Python):**

```python
spark.read \
  .option("readChangeFeed", "true") \
  .option("startingVersion", 0) \
  .table("<table_name>")
```

**Batch-Lesen (SQL):**

```sql
SELECT * FROM table_changes('<table_name>', 0);
```

**Streaming-Lesen (Python):**

```python
(spark.readStream
  .option("readChangeFeed", "true")
  .table("<table_name>"))
```

## 4. Schema des Change Data Feed

| Spalte | Typ | Werte |
|---|---|---|
| `_change_type` | String | `insert`, `update_preimage`, `update_postimage`, `delete` |
| `_commit_version` | Long | Delta-Log-/Tabellenversion, die die Änderung enthält |
| `_commit_timestamp` | Timestamp | Zeitpunkt der Commit-Erstellung |

## 5. Änderungen mit Versionsbereichen lesen

```sql
-- Batch-Lesen mit Endversion
SELECT * FROM table_changes('tableName', 0, 10);

-- Mit Timestamps
SELECT * FROM table_changes('tableName', '2021-04-21 05:45:46', '2021-05-21 12:00:00');
```

```python
# Batch-Lesen von neuester bis spezifischer Version
spark.read \
  .option("readChangeFeed", "true") \
  .option("startingVersion", 0) \
  .table("myDeltaTable")

# Mit expliziter Endversion (Option "endingVersion")
spark.read \
  .option("readChangeFeed", "true") \
  .option("startingVersion", 0) \
  .option("endingVersion", 10) \
  .table("myDeltaTable")
```

Versionsangaben sind Ganzzahlen, Timestamps folgen dem Format `yyyy-MM-dd[ HH:mm:ss[.SSS]]`. Start- und Endversion sind **inklusiv**; wird die Endversion weggelassen, wird bis zur neuesten Version gelesen. Liegt die angegebene Version vor der CDF-Aktivierung, entsteht standardmäßig ein Fehler (`timestampGreaterThanLatestCommit`).

**Verhalten bei Versionen außerhalb des Bereichs konfigurieren:**

```sql
SET spark.databricks.delta.changeDataFeed.timestampOutOfRange.enabled = true;
```

Mit dieser Einstellung liefert eine Startversion jenseits des letzten Commits ein leeres Ergebnis, eine Endversion jenseits des letzten Commits liefert alle Änderungen bis zum letzten Commit (statt eines Fehlers).

## 5a. Funktionsreferenz: `table_changes()`

`table_changes()` ist eine table-valued function, die die oben gezeigten SQL-Abfragen kapselt (`sql-ref-syntax-ddl-...`/`functions/table_changes`).

**Signatur:**

```sql
table_changes ( table_str, start [, end ] )
```

**Argumente:**

| Argument | Typ | Beschreibung |
|---|---|---|
| `table_str` | STRING-Literal | (optional qualifizierter) Tabellenname. Ohne Qualifikation wird das aktuelle Schema verwendet. Tabellennamen mit Leerzeichen oder Punkten müssen mit Backticks gequotet werden. |
| `start` | BIGINT- oder TIMESTAMP-Literal | erste Version bzw. erster Zeitstempel der abzurufenden Änderungen |
| `end` | BIGINT- oder TIMESTAMP-Literal (optional) | letzte Version bzw. letzter Zeitstempel; wird `end` weggelassen, werden alle Änderungen ab `start` zurückgegeben |

**Rückgabewert:** die Originalspalten der Tabelle plus die drei CDF-Metadatenspalten (`_change_type` STRING NOT NULL, `_commit_version` BIGINT NOT NULL, `_commit_timestamp` TIMESTAMP NOT NULL — siehe Schema-Tabelle oben).

**Voraussetzungen:** `SELECT`-Privileg auf der Tabelle, Eigentümerstatus oder administrative Privilegien; Change Data Feed muss für die Tabelle aktiviert sein.

**Beispiel:**

```sql
CREATE TABLE myschema.t(c1 INT, c2 STRING)
  TBLPROPERTIES(delta.enableChangeDataFeed=true);

INSERT INTO myschema.t VALUES (1, 'Hello'), (2, 'World');
INSERT INTO myschema.t VALUES (3, '!');
UPDATE myschema.t SET c2 = upper(c2) WHERE c1 < 3;
DELETE FROM myschema.t WHERE c1 = 3;

SELECT * FROM table_changes('`myschema`.`t`', 2);
SELECT * FROM table_changes('`myschema`.`t`',
  '2022-09-01T18:32:27.000+0000') ORDER BY _commit_version;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/functions/table_changes

## 6. Änderungen mit Streaming verarbeiten

Empfohlener Ansatz: CDF mit Structured Streaming kombinieren — Databricks empfiehlt dies ausdrücklich, da nur Structured Streaming automatisch Versionen für den Change Data Feed einer Tabelle nachverfolgt. Der initiale Stream liefert den aktuellen Tabellen-Snapshot als `INSERT`-Datensätze, danach folgen zukünftige Änderungen.

**Beispiel: Änderungen archivieren (Python):**

```python
(spark.readStream
  .option("readChangeFeed", "true")
  .table("source_table")
  .writeStream
  .option("checkpointLocation", "<checkpoint-path>")
  .trigger(availableNow=True)
  .toTable("target_table"))
```

**Streaming-Konfigurationsoptionen:** Rate-Limits über `maxFilesPerTrigger` und `maxBytesPerTrigger` (gelten atomar auf ganze Commits, nicht auf einzelne Dateien), Filterung über `excludeRegex`, sowie `startingVersion`/`startingTimestamp` zur Startposition.

**Retention der Änderungsdaten:** Einträge im Change Data Feed sind **transient** und nur innerhalb eines konfigurierten Retention-Fensters abrufbar — das Transaktionslog entfernt Tabellenversionen und die zugehörigen CDF-Versionen in regelmäßigen Abständen. Für eine dauerhafte Historie empfiehlt sich das inkrementelle Schreiben der CDF-Datensätze in eine neue Tabelle (wie im Archivierungs-Beispiel oben, mit `trigger(availableNow=True)`).

**Wiederherstellung nach Checkpoint-Beschädigung:** Einen neuen `checkpointLocation` und eine passende `startingVersion` angeben (z. B. Version 76, wenn das Ziel zuletzt bis Version 75 verarbeitet hat).

## 7. Migration von Legacy CDF

Legacy CDF und Automatic CDF schließen sich auf derselben Tabelle gegenseitig aus (Abschnitt 2). Eine Tabelle mit aktivem Legacy CDF lässt sich nicht einfach zusätzlich auf Automatic CDF umstellen — zuerst muss die Legacy-Property vollständig entfernt werden:

```sql
-- Schritt 1: Legacy CDF abschalten, Property komplett entfernen (nicht nur auf 'false' setzen)
ALTER TABLE <table_name> UNSET TBLPROPERTIES ('delta.enableChangeDataFeed');
```

`UNSET` statt `SET ... = 'false'`, weil die reine Anwesenheit der Property (unabhängig vom Wert) bei manchen internen Prüfungen als "Legacy-CDF-konfiguriert" zählt — erst das vollständige Entfernen macht den Weg für Automatic CDF frei.

**Schritt 2 — Voraussetzung für Automatic CDF sicherstellen** (falls noch nicht aktiviert, siehe [11 Row Tracking.md](11%20Row%20Tracking.md)):

```sql
ALTER TABLE <table_name> SET TBLPROPERTIES (delta.enableRowTracking = true);
```

Danach berechnet Databricks Änderungen für diese Tabelle automatisch über Row Lineage (Automatic CDF) — ohne weitere Konfiguration, mit denselben Lese-APIs (`table_changes()`, `readChangeFeed`) wie zuvor bei Legacy CDF (Abschnitt 3). Bereits mit Legacy CDF aufgezeichnete historische Änderungsversionen bleiben innerhalb ihres Retention-Fensters weiterhin abfragbar; das `UNSET` betrifft nur künftige Schreibvorgänge.

## 8. Legacy Change Data Feed aktivieren

**Neue Tabelle:**

```sql
CREATE TABLE student (id INT, name STRING, age INT)
  TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

**Bestehende Tabelle:**

```sql
ALTER TABLE myDeltaTable
  SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

**Deaktivieren und erneut aktivieren:** Wird Legacy CDF für ein Zeitintervall deaktiviert und danach wieder aktiviert, bleibt dieses Intervall **nicht abfragbar**.

**Storage-Überlegungen bei Legacy CDF:**

- Leicht erhöhte Storage-Kosten durch separate Change-Data-Dateien.
- Reine Insert-Vorgänge oder vollständige Partitions-Löschungen erzeugen **keine** Change-Data-Dateien.
- Change-Data-Dateien unterliegen derselben Tabellen-Retention-Policy.
- `VACUUM` löscht Change-Data-Dateien mit.
- Databricks rät davon ab, CDF durch direktes Abfragen der Change-Data-Dateien selbst zu rekonstruieren.

## 9. Wichtige Einschränkungen

- CDF kann keine Tabellenversionen mit nicht-additiven Schema-Änderungen überspannen (Spaltenumbenennung, -löschung, Typänderung, Nullability-Änderung). Batch-Lesevorgänge nutzen das Schema der Endversion statt des neuesten Schemas, schlagen aber fehl, wenn der abgefragte Bereich eine solche Änderung überspannt.
- Externe Iceberg-Clients können Automatic CDF nicht abfragen (nicht Teil der Iceberg-Spezifikation) — Databricks-Reader können Automatic CDF sowohl für Delta-Lake- als auch für Iceberg-v3-Tabellen lesen, externe Iceberg-Reader jedoch nicht.
- CDF nicht unterstützt auf Tabellen mit Row Filters oder Column Masks.
- Multi-Statement-Transaktionen mit Quelltabellen-Modifikationen unterstützen kein Automatic CDF.
- Spaltennamenskonflikte mit Metadaten-Spalten verhindern die CDF-Nutzung.

## 10. Verwandte Themen

- Automatic CDF baut auf [11 Row Tracking.md](11%20Row%20Tracking.md) auf.
- Runtime-Anforderungen und Protokollversion im Gesamtüberblick: siehe [08 Feature Compatibility.md](08%20Feature%20Compatibility.md).
- Einordnung von CDF im CDC-/Pipeline-Kontext und Abgrenzung zu `AUTO CDC INTO`: siehe [07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/05 CDC/02 Change Data Feed.md](../../../07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/05%20CDC/02%20Change%20Data%20Feed.md).

### Quelle

- https://docs.databricks.com/aws/en/tables/features/change-data-feed
