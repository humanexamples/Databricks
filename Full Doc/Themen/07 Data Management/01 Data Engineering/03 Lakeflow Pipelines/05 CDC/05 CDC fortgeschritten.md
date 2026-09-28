# Fortgeschrittene AUTO-CDC-Themen — Referenz

Dieses Dokument vertieft Themen rund um die `AUTO CDC`- und `AUTO CDC FROM SNAPSHOT`-APIs, die über die Grundlagen aus `CDC-Grundlagen.md` (diesem Ordner) hinausgehen: DML auf Zieltabellen, Change Data Feed von CDC-Zielen und Materialized Views lesen, Metriken, partielle Updates und bitemporales Tracking. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/cdc-advanced`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte; die Databricks-Runtime-Versionsangabe (15.2) und der Beta-Status von Bitemporal AUTO CDC wurden zusätzlich per Zweitabruf gegen die AWS-Seite (`docs.databricks.com/aws/en/ldp/cdc-advanced`) wörtlich gegengeprüft.

## Abschnittsübersicht

1. [Daten in einer Ziel-Streaming-Table per DML ändern](#dml)
2. [Change Data Feed vom AUTO-CDC-Ziel lesen](#cdf-target)
3. [Change Data Feed von einer Materialized View lesen (Beta)](#cdf-mv)
4. [Metriken zu verarbeiteten CDC-Datensätzen](#metriken)
5. [Partielle Updates anwenden](#partial-updates)
6. [Bitemporal AUTO CDC (Beta)](#bitemporal)
7. [Welche Datenobjekte werden für CDC-Verarbeitung verwendet?](#datenobjekte)
8. [Quellen](#quellen)

---

## <a id="dml">1. Daten in einer Ziel-Streaming-Table per DML ändern</a>

Wird die Pipeline nach Unity Catalog publiziert, lassen sich DML-Anweisungen (Insert, Update, Delete, Merge) verwenden, um die von `AUTO CDC ... INTO`-Anweisungen erzeugten Ziel-Streaming-Tables zu modifizieren.

**Hinweise laut Doku:**

- DML-Anweisungen, die das Tabellenschema einer Streaming Table ändern, werden nicht unterstützt.
- DML-Anweisungen, die eine Streaming Table aktualisieren, können nur auf einem Shared-Unity-Catalog-Cluster oder einem SQL-Warehouse mit Databricks Runtime 13.3 LTS oder höher ausgeführt werden.
- Da Streaming Append-only-Datenquellen voraussetzt: Wird von einer Quell-Streaming-Table mit Änderungen (z. B. durch DML) gestreamt, muss das `skipChangeCommits`-Flag beim Lesen gesetzt werden (siehe `Daten laden.md` Abschnitt 11 in `04 Ingestion und Laden von Daten`). Bei gesetztem `skipChangeCommits` werden Transaktionen, die Datensätze auf der Quelltabelle löschen oder ändern, ignoriert. Ist keine Streaming Table erforderlich, kann alternativ eine Materialized View (ohne Append-only-Beschränkung) als Zieltabelle verwendet werden.

Da die Pipeline eine angegebene `SEQUENCE BY`-Spalte nutzt und passende Sequenzierungswerte in die `__START_AT`-/`__END_AT`-Spalten der Zieltabelle propagiert (für SCD Typ 2), müssen DML-Anweisungen gültige Werte für diese Spalten verwenden, um die korrekte Reihenfolge der Datensätze zu erhalten.

Beispiel — Einfügen eines aktiven Datensatzes mit Sequenzstart 5:

```sql
INSERT INTO my_streaming_table (id, name, __START_AT, __END_AT) VALUES (123, 'John Doe', 5, NULL);
```

**Tipp:** Um `__START_AT`/`__END_AT` in einer SCD-Typ-2-Zieltabelle umzubenennen (z. B. für nachgelagerte Schema-Anforderungen), lässt sich eine View über die Zieltabelle anlegen:

```sql
CREATE VIEW my_employees_view AS
SELECT
  *,
  __START_AT AS valid_from,
  __END_AT AS valid_to
FROM my_scd2_target_table;
```

## <a id="cdf-target">2. Change Data Feed vom AUTO-CDC-Ziel lesen</a>

Ab **Databricks Runtime 15.2** lässt sich ein Change Data Feed aus einer Streaming Table lesen, die Ziel von `AUTO CDC`- oder `AUTO CDC FROM SNAPSHOT`-Queries ist — auf dieselbe Weise wie bei jeder anderen Delta-Tabelle. Voraussetzungen:

- Die Ziel-Streaming-Table muss nach Unity Catalog publiziert sein.
- Zum Lesen des Change Data Feed aus der Ziel-Streaming-Table wird Databricks Runtime 15.2 oder höher benötigt; soll der Change Data Feed in einer anderen Pipeline gelesen werden, muss auch diese Pipeline auf Databricks Runtime 15.2 oder höher konfiguriert sein.

**Hinweis zu Metadaten:** Der Change-Data-Feed-Datensatz enthält Metadaten, die den Typ des Änderungs-Events identifizieren. Bei einem aktualisierten Datensatz sind die `_change_type`-Werte typischerweise `update_preimage` und `update_postimage`. Werden jedoch Updates an der Ziel-Streaming-Table vorgenommen, die Primärschlüsselwerte ändern, sind die `_change_type`-Metadatenfelder stattdessen `insert` und `delete`. Das kann bei manuellen Updates eines Key-Felds über `UPDATE`/`MERGE` auftreten, oder bei SCD-Typ-2-Tabellen, wenn sich das `__start_at`-Feld auf einen früheren Startsequenzwert ändert.

Die `AUTO CDC`-Query bestimmt die Primärschlüsselwerte — je nach SCD-Typ unterschiedlich:

| SCD-Typ | Primärschlüssel |
|---|---|
| SCD Typ 1 (Python-Schnittstelle) | Der Wert des `keys`-Parameters in `create_auto_cdc_flow()`; für die SQL-Schnittstelle die durch die `KEYS`-Klausel in `AUTO CDC ... INTO` definierten Spalten. |
| SCD Typ 2 | Der `keys`-Parameter bzw. die `KEYS`-Klausel plus der Rückgabewert von `coalesce(__START_AT, __END_AT)` — verwendet `__START_AT`, wenn vorhanden, sonst `__END_AT` (z. B. beim initialen Datensatz). |

## <a id="cdf-mv">3. Change Data Feed von einer Materialized View lesen (Beta)</a>

**Dieses Feature ist in Beta.** Workspace-Admins können den Zugriff über die Previews-Seite steuern. Ein Change Data Feed lässt sich von einer in einer Lakeflow-Pipeline oder in Databricks SQL erzeugten Materialized View lesen — nützlich, um Materialized-View-Änderungen außerhalb von Databricks zu replizieren oder eine Änderungshistorie für Auditing/Reporting zu führen.

Materialized Views nutzen einen automatischen Change Data Feed — er muss nicht separat aktiviert werden. Voraussetzungen:

- Zum Lesen des Change Data Feed wird **Databricks Runtime 18 LTS oder höher** benötigt, auf Classic Compute, Serverless Compute oder Databricks SQL.
- Die Materialized View, die sie erzeugende Pipeline, oder die sie lesende Pipeline muss den `PREVIEW`-Channel verwenden.
- Die Materialized View muss Row Tracking aktiviert haben. Auf Serverless Compute ist Row Tracking standardmäßig aktiviert. Prüfbar über:

  ```sql
  SHOW TBLPROPERTIES my_mv ('delta.enableRowTracking');
  ```

- Die Materialized-View-Metadaten müssen synchronisiert sein, damit sie außerhalb ihrer eigenen Pipeline lesbar sind:
  - Für eine in einer Pipeline erzeugte Materialized View: `pipelines.externalMetadata.enabled` in der Pipeline-Konfiguration setzen:

    ```json
    {
      "configuration": {
        "pipelines.externalMetadata.enabled": "true"
      }
    }
    ```
  - Für eine eigenständige Materialized View: einmalig folgenden Befehl ausführen (benötigt die External-Access-Preview für Materialized Views und Streaming Tables):

    ```sql
    REPAIR TABLE my_mv SYNC METADATA;
    ```

Gelesen wird wie bei jeder anderen Delta-Tabelle (`table_changes()`-Funktion, Streaming Read, oder `readChangeFeed`-Option). Soll ein Materialized-View-Change-Data-Feed innerhalb einer Databricks-SQL-Materialized-View oder Streaming Table gelesen werden, müssen auch diese den `PREVIEW`-Channel verwenden:

```sql
CREATE OR REFRESH STREAMING TABLE sales
TBLPROPERTIES ('pipelines.channel' = 'preview')
  AS SELECT * FROM STREAM my_mv WITH (readChangeFeed=true)
```

### Limitierungen

- Der Change Data Feed enthält unveränderte Zeilen, wenn die Materialized View vollständig neu geschrieben wird, und konsolidiert mehrere Updates derselben Zeile nicht zu einem einzelnen Event. Zum Herausfiltern lässt sich der Change Data Feed über alle Spalten gruppieren, um Inserts/Deletes mit gleichen Zeilenwerten zu finden.
- Nur Databricks selbst kann den Change Data Feed einer Materialized View abfragen — externe Delta-Lake- und Iceberg-Clients nicht.
- Innerhalb von Lakeflow-Pipelines lässt sich der Change Data Feed einer Materialized View nur aus einer **anderen** Pipeline lesen, die zudem den `PREVIEW`-Channel nutzen muss. Das Lesen des Change Data Feed innerhalb derselben Pipeline, die die Materialized View erzeugt, wird nicht unterstützt.
- Aus einer Materialized View lässt sich kein Vector-Search-Index erzeugen.

## <a id="metriken">4. Metriken zu verarbeiteten CDC-Datensätzen</a>

**Hinweis:** Die folgenden Metriken werden nur von `AUTO CDC`-Queries erfasst, nicht von `AUTO CDC FROM SNAPSHOT`-Queries.

- **`num_upserted_rows`:** Anzahl der während eines Updates in das Dataset upgeserteten Ausgabezeilen.
- **`num_deleted_rows`:** Anzahl der während eines Updates aus dem Dataset gelöschten bestehenden Ausgabezeilen.

Die für Nicht-CDC-Flows ausgegebene Metrik `num_output_rows` wird für `AUTO CDC`-Queries nicht erfasst.

## <a id="partial-updates">5. Partielle Updates anwenden</a>

Sendet eine Quelle nur die geänderten Spalten, muss `AUTO CDC` unterscheiden zwischen einer Spalte, die im Change Record **fehlt** (Zielwert soll unverändert bleiben), und einer Spalte, die explizit auf `null` gesetzt ist (Zielwert soll mit `null` überschrieben werden). Standardmäßig behandelt `IGNORE NULL UPDATES` jedes `null` als "nicht aktualisieren"-Marker und kann daher kein explizites `null` anwenden. Zur Auflösung dieser Mehrdeutigkeit stehen drei Methoden zur Verfügung:

| Methode | Einsatz wenn | Verhalten |
|---|---|---|
| `IGNORE NULL UPDATES ON columnList` | Eine kleine, feste Spaltenmenge soll `null`-Werte ignorieren, alle anderen Spalten wenden explizite `null`-Werte an. | Gelistete Spalten behalten ihren bestehenden Zielwert, wenn der eingehende Wert `null` ist. Alle anderen Spalten wenden explizite `null`-Werte an. |
| `IGNORE NULL UPDATES ON * EXCEPT (exceptColumnList)` | Die meisten Spalten sollen `null`-Werte ignorieren, nur wenige sollen explizite `null`-Werte anwenden. | Gelistete Spalten wenden explizite `null`-Werte an. Alle anderen Spalten behalten ihren bestehenden Zielwert bei `null`. |
| `COLUMNS TO UPDATE` | Jeder Change Record aktualisiert eine andere Spaltenmenge, oder die Menge aktualisierbarer Spalten ändert sich über die Zeit. | Eine Quellspalte benennt die für jeden Change Record zu aktualisierenden Spalten. Gelistete Spalten werden aus der Quelle geschrieben (inkl. expliziter `null`-Werte). Nicht gelistete Spalten behalten ihren bestehenden Zielwert. |

`COLUMNS TO UPDATE` lässt sich nicht mit `IGNORE NULL UPDATES` kombinieren und wird für bitemporale Tabellen nicht unterstützt.

Als Faustregel: `COLUMNS TO UPDATE` wählen, wenn der Produzent weiß, welche Spalten sich in jedem Datensatz geändert haben, und diese Information in einer Quellspalte mitführen kann (z. B. bei mehreren Producern auf dieselbe Quelle oder wachsender Menge aktualisierbarer Spalten). `IGNORE NULL UPDATES ON` wählen, wenn der Pipeline-Owner die feste Menge aktualisierbarer Spalten vorab kennt und lieber im Pipeline-Code steuert.

Beispiel mit einer Quellspalte `columnsToUpdate`, die pro Change Record festlegt, welche Spalten aktualisiert werden (inklusive explizit auf `null` gesetzter Spalten):

```python
from pyspark import pipelines as dp

dp.create_streaming_table("target")

dp.create_auto_cdc_flow(
  target = "target",
  source = "cdc_source",
  keys = ["id"],
  sequence_by = "sequenceNum",
  stored_as_scd_type = 1,
  columns_to_update = "columnsToUpdate"
)
```

```sql
CREATE OR REFRESH STREAMING TABLE target;

CREATE FLOW apply_cdc AS AUTO CDC INTO
  target
FROM
  stream(cdc_source)
KEYS
  (id)
SEQUENCE BY
  sequenceNum
STORED AS
  SCD TYPE 1
COLUMNS TO UPDATE
  columnsToUpdate;
```

## <a id="bitemporal">6. Bitemporal AUTO CDC (Beta)</a>

**Bitemporal AUTO CDC ist in Beta.**

SCD Typ 1 und Typ 2 sind unitemporal — sie verfolgen Änderungen über eine einzige Zeitdimension. Bitemporal erweitert die SCD-Typ-2-Historie um eine zweite Zeitdimension und unterscheidet zwei Perspektiven:

- **Business Time:** wann das Ereignis tatsächlich stattfand.
- **System Time:** wann das System das Ereignis erfasste bzw. einlas.

Wie SCD Typ 2 bewahrt Bitemporal eine vollständige Historie der Datensätze. Zusätzlich lässt sich über eine zweite Zeitleiste rekonstruieren, was die Daten zu jedem früheren Zeitpunkt zeigten **und** was das System zu diesem Zeitpunkt glaubte.

**Beispiel aus der Doku:** Ein Hedgefonds liest Aktienkursdaten aus einem Quellsystem ein. Der Aktienkurs der Acme Corp ändert sich am 1. Januar, wird aber erst am 5. Januar eingelesen. Bitemporal AUTO CDC erlaubt zwei unterschiedliche Fragen zu beantworten: Wie war der tatsächliche Aktienkurs am 1. Januar (Business Time)? Und welchen Kurs glaubte das System am 3. Januar, als die Trading-Entscheidung getroffen wurde (System Time)? Diese Unterscheidung ist nützlich für Auditing, regulatorisches Reporting und Finanzentscheidungen.

Um bitemporale Verarbeitung zu aktivieren, wird `STORED AS BITEMPORAL` (SQL) bzw. `stored_as_scd_type="bitemporal"` (Python) gesetzt, `SEQUENCE BY` für die Business-Time-Spalte und `SYSTEM SEQUENCE BY` für die System-Time-Spalte verwendet. Die Zieltabelle ergänzt die Spalten `__SYSTEM_START_AT` und `__SYSTEM_END_AT` neben den SCD-Typ-2-Spalten `__START_AT`/`__END_AT`.

### Bitemporal-AUTO-CDC-Beispiel

Das folgende Beispiel erzeugt eine bitemporale Zieltabelle aus einer kleinen Menge synthetischer CDC-Events. Die Spalte `bt` enthält die Business Time, die Spalte `st` die System Time:

```python
from pyspark import pipelines as dp

# Source: synthetic CDC events
dp.create_streaming_table(name="cdc_source")

@dp.append_flow(target="cdc_source", once=True)
def load_cdc_source():
  return spark.createDataFrame(
    [
      (1, "x10", "y10", 10, 100),
      (1, "x20", "y20", 20, 200)
    ],
    schema="id INT, x STRING, y STRING, bt INT, st INT",
  )

# Target: bitemporal table
dp.create_streaming_table(name="target_bitemporal")

dp.create_auto_cdc_flow(
  target = "target_bitemporal",
  source = "cdc_source",
  keys = ["id"],
  sequence_by = "bt",
  system_sequence_by = "st",
  stored_as_scd_type = "bitemporal"
)
```

```sql
-- Source: synthetic CDC events
CREATE OR REFRESH STREAMING TABLE cdc_source_sql;

CREATE FLOW cdc_source_sql AS INSERT INTO ONCE
  cdc_source_sql BY NAME
SELECT * FROM VALUES
  (1, 'x10', 'y10', 10, 100),
  (1, 'x20', 'y20', 20, 200)
  AS t(id, x, y, bt, st);

-- Target: bitemporal table
CREATE OR REFRESH STREAMING TABLE target_bitemporal_sql;

CREATE FLOW target_bitemporal_sql AS AUTO CDC INTO
  target_bitemporal_sql
FROM
  stream(cdc_source_sql)
KEYS
  (id)
SEQUENCE BY
  bt
SYSTEM SEQUENCE BY
  st
STORED AS
  BITEMPORAL;
```

Spaltenbedeutung:

| Spalte | Bedeutung |
|---|---|
| `__START_AT` | Business Time, ab der diese Zeile gültig wurde. |
| `__END_AT` | Business Time, ab der die Gültigkeit dieser Zeile endet. `null`, falls unbegrenzt gültig. |
| `__SYSTEM_START_AT` | System Time, ab der Daten und Business-Time-Intervall dieser Zeile als wahr bekannt sind. |
| `__SYSTEM_END_AT` | System Time, ab der Daten und Business-Time-Intervall dieser Zeile als ungültig bekannt sind. `null`, falls unbegrenzt als wahr bekannt. |

Das System handhabt Events, die in beliebiger Reihenfolge über beide Zeitleisten hinweg eintreffen. Trifft ein Event mit früherer Business Time oder System Time als bereits verarbeitete Events ein, korrigiert das System die betroffene Historie, statt nur ans Ende anzuhängen.

**Änderung 1 — Insert:** Firma A wird am 18.07.2025 10:01:00 (Business Time) hinzugefügt, aber erst um 10:05:00 (System Time) eingelesen.

Ausgabe: eine Zeile — `XFv1`, `__START_AT=10:01:00`, `__END_AT=NULL`, `__SYSTEM_START_AT=10:05:00`, `__SYSTEM_END_AT=NULL`.

**Änderung 2 — Update:** Firma A wird um 12:15:43 (Business Time) aktualisiert, System nimmt es um 12:20:00 auf. Das System bewahrt sowohl den vorherigen Glaubensstand als auch die korrigierte Business-Historie:

Ausgabe: drei Zeilen — die ursprüngliche `XFv1`-Zeile mit geschlossenem `__SYSTEM_END_AT=12:20:00`, eine korrigierte `XFv1`-Zeile mit `__END_AT=12:15:43`, und eine neue `XFv2`-Zeile ab `12:15:43`.

**Änderung 3 — nicht-geordnetes Update:** Ein verspätet eintreffendes Update (Business Time 12:05:00, System Time 12:25:00) korrigiert die Historie rückwirkend nochmals — das System bewahrt sowohl den vorherigen Glaubensstand als auch die korrigierte Historie.

**Änderung 4 — Delete:** Firma A wird um 12:30:00 gelöscht. Da ein Delete das Ende der Business-Existenz der Entität darstellt, erzeugt das System keine Ersatzzeile — `XFv2` erscheint in zwei Zeilen, die sowohl den Zeitpunkt des Endes als auch den Zeitpunkt der System-Kenntnisnahme dokumentieren.

*(Die vollständigen Tabellen mit allen Zwischenzuständen sind auf der Originalseite dokumentiert — hier aus Platzgründen auf die Kernlogik verdichtet; Details siehe Quelle.)*

## <a id="datenobjekte">7. Welche Datenobjekte werden für CDC-Verarbeitung verwendet?</a>

Wird die Zieltabelle im Hive Metastore deklariert, entstehen zwei Datenstrukturen:

- eine View mit dem Namen der Zieltabelle,
- eine interne Backing Table, die die Pipeline zur Verwaltung der CDC-Verarbeitung nutzt — benannt durch Voranstellen von `__apply_changes_storage_` an den Zieltabellennamen.

Wird z. B. eine Zieltabelle `dp_cdc_target` deklariert, entstehen eine View `dp_cdc_target` und eine Tabelle `__apply_changes_storage_dp_cdc_target` im Metastore. Abgefragt wird die View — die Backing Table sollte nicht direkt modifiziert werden.

**Hinweis:** Diese Datenstrukturen gelten nur für `AUTO CDC`-Verarbeitung, nicht für `AUTO CDC FROM SNAPSHOT`, und nur für den Hive Metastore, nicht für Unity Catalog.

---

## <a id="quellen">8. Quellen</a>

- Advanced AUTO CDC topics (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/ldp/cdc-advanced
- Advanced AUTO CDC topics (AWS, Zweitabruf zur Gegenprüfung von Runtime-Version 15.2 und Beta-Status): https://docs.databricks.com/aws/en/ldp/cdc-advanced

**Stand:** 2026-08-19.
