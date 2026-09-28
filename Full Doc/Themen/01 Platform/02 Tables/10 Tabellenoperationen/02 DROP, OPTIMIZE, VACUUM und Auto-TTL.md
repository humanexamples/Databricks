# DROP, OPTIMIZE, VACUUM und Auto-TTL

Vier zentrale Wartungsoperationen für Databricks-Tabellen: das kontrollierte Löschen von Tabellen, das Kompaktieren von Dateien, das Bereinigen alter Dateiversionen und die automatische, zeitgesteuerte Löschung einzelner Zeilen. `OPTIMIZE` und `VACUUM` sind bereits ausführlich in der Performance-Optimization-Dokumentation behandelt — dieses Dokument fasst sie kurz zusammen und ergänzt Details, die dort noch nicht erfasst wurden, bevor es sich `DROP TABLE` und dem neuen Auto-TTL-Feature widmet.

## Abschnittsübersicht

1. [DROP TABLE und UNDROP](#drop-table)
2. [OPTIMIZE: Kurzüberblick](#optimize)
3. [VACUUM: Ergänzende Details](#vacuum)
4. [Auto-TTL: automatische zeitgesteuerte Zeilenlöschung](#auto-ttl)
5. [Zusammenfassung](#zusammenfassung)

---

## <a id="drop-table">1. DROP TABLE und UNDROP</a>

### 1.1 Grundsyntax

```sql
DROP TABLE table_name;
```

### 1.2 Verhalten nach Tabellentyp und Metastore

| Konfiguration | Ergebnis |
|---|---|
| **Managed + Unity Catalog** | Tabelle wird aus dem Metastore entfernt, zugrunde liegende Daten werden zur Löschung markiert. Wiederherstellbar über `UNDROP` innerhalb des standardmäßigen 7-Tage-Recovery-Fensters (siehe [Managed Tables.md](../Managed%20Tables.md), Abschnitt 3). |
| **Managed + Hive** | Entfernung aus dem Metastore löst sofortige Löschung der zugrunde liegenden Daten aus. |
| **External + Unity Catalog** | Metastore-Eintrag entfernt, Daten bleiben bestehen. Zugriffs-Governance geht auf die External-Location-Einstellungen über. |
| **External + Hive** | Metastore-Eintrag entfernt, Daten bleiben mit unveränderten URI-Zugriffsberechtigungen bestehen. |

**Wichtig:** Nur Managed Tables in Unity Catalog unterstützen Wiederherstellung — „eine Managed Table lässt sich innerhalb der konfigurierten Recovery-Frist (Standard: 7 Tage) über `UNDROP` wiederherstellen."

### 1.3 Anti-Pattern-Warnung

Databricks rät ausdrücklich von folgendem Muster ab:

```sql
-- NICHT EMPFOHLEN
DROP TABLE IF EXISTS table_name;
CREATE TABLE table_name AS SELECT ...
```

Dieses Muster riskiert Fehler, Datenverlust oder Korruption bei nebenläufigen Operationen.

**Empfohlene Alternative:**

```sql
CREATE OR REPLACE TABLE table_name AS SELECT * FROM parquet.`/path/to/files`;
```

Vorteile: atomare Operation (es gibt nie einen Zeitpunkt, an dem die Tabelle nicht existiert), erhaltene Tabellenidentität, erhaltene Column Masks bestehender Spalten, erhaltene Historie (inkl. `RESTORE`-Fähigkeit), ununterbrochener nebenläufiger Zugriff.

---

## <a id="optimize">2. OPTIMIZE: Kurzüberblick</a>

`OPTIMIZE` schreibt Datendateien um, um das Layout sowohl für Delta-Lake- als auch für Apache-Iceberg-Tabellen zu verbessern. Bei Liquid-geclusterten Tabellen gruppiert es Daten nach Clustering-Keys; bei partitionierten Tabellen arbeitet es innerhalb der Partitionsgrenzen. Für Delta-Lake-Tabellen ist optional `ZORDER BY` nutzbar — Apache-Iceberg-Tabellen verwenden stattdessen eigene Clustering- und Sortierstrategien. Auf Unity-Catalog-Managed-Tables führt Predictive Optimization `OPTIMIZE` automatisch aus.

```sql
OPTIMIZE table_name;
OPTIMIZE table_name WHERE date >= '2022-11-18';
```

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "table_name")
deltaTable.optimize().executeCompaction()
```

**Eigenschaften:** idempotente Operation (wiederholte Ausführungen ändern nichts weiter), erzeugt gleichmäßig ausbalancierte Dateien nach Speichergröße (nicht notwendigerweise nach Tupel-Anzahl), Reader-Isolation über Snapshot Isolation, Rückgabe von Datei-Statistiken (Min, Max, Total) und Z-Ordering-Details.

**Empfehlungen:** täglich ausführen, idealerweise außerhalb der Spitzenzeiten; Compute-optimierte Instanzen mit angehängten SSDs nutzen (CPU-intensive Parquet-Operationen).

**Ausführliche Behandlung** von `OPTIMIZE FULL`, Z-Ordering-Details, Konfigurationsparametern und dem Zusammenspiel mit Liquid Clustering in [Z-Ordering.md](../../../Performance%20Optimization/Foundation%20Design/Z-Ordering.md) und [Liquid Clustering.md](../../../Performance%20Optimization/Foundation%20Design/Liquid%20Clustering.md), Abschnitt 7.

---

## <a id="vacuum">3. VACUUM: Ergänzende Details</a>

`VACUUM` ist bereits ausführlich in [Liquid Clustering.md](../../../Performance%20Optimization/Foundation%20Design/Liquid%20Clustering.md), Abschnitt 11.4, behandelt (Grundsyntax, DRY RUN, LITE-Modus, FULL-Modus, REORG). Ergänzend dazu folgende Details von der dedizierten Tabellenoperationen-Seite:

### 3.1 Retention-Konfiguration

Der Standard-Retention-Zeitraum beträgt **7 Tage**. Anpassbar über die Tabelleneigenschaft `delta.deletedFileRetentionDuration` (Delta, ab Databricks Runtime 18.0+ allgemein bzw. ab 13.3 LTS+ für Unity-Catalog-Managed-Tables) bzw. `iceberg.deletedFileRetentionDuration` (Iceberg), oder über die allgemeinen Data-Retention-Einstellungen für Time-Travel-Queries.

**Wichtige Nebenwirkung:** Nach Ausführung von `VACUUM` geht die Fähigkeit verloren, Tabellenversionen abzufragen, die älter als der Retention-Zeitraum sind (Time-Travel-Verlust).

**Sicherheitsschwelle unterschreiten:** Databricks rät dringend von einem Retention-Zeitraum unter 7 Tagen ab (Gefahr, dass noch nicht committete Dateien lang laufender Jobs gelöscht werden). Zum expliziten Deaktivieren dieser Sicherheitsprüfung:

```sql
SET spark.databricks.delta.retentionDurationCheck.enabled = false;   -- Delta
SET spark.databricks.iceberg.retentionDurationCheck.enabled = false; -- Iceberg
```

### 3.2 LITE-Modus im Detail

**Voraussetzung:** Ab Databricks Runtime 16.4 LTS+; innerhalb der Transaktionslog-Retention-Schwelle (Standard: 30 Tage) muss mindestens ein erfolgreicher `VACUUM`-Lauf stattgefunden haben.

**Einschränkung:** „`VACUUM` im `LITE`-Modus löscht keine Dateien, die nicht im Transaktionslog referenziert werden." Bei Bedarf liefert der Fehler `VACUUM <tableName> LITE cannot delete all eligible files as some files are not referenced by the log. Please run VACUUM FULL.` den Hinweis, auf `FULL` auszuweichen.

### 3.3 Verzeichnis- und Dateiverhalten

- `VACUUM` entfernt Dateien aus Verzeichnissen, die nicht von Databricks verwaltet werden, überspringt dabei aber Verzeichnisse, die mit `_` oder `.` beginnen (z. B. eigene Metadaten-Verzeichnisse wie `_checkpoints`).
- Spezielle, von `VACUUM` mit-bereinigte Unterverzeichnisse: `_change_data` (Change-Data-Feed-Speicher) und `_delta_index` (veraltete Bloom-Filter-Indizes).
- Nach dem Entfernen aller Dateien können leere Verzeichnisse zurückbleiben — nachfolgende `VACUUM`-Läufe löschen diese leeren Verzeichnisse.
- Transaktionslog-Dateien werden automatisch und asynchron nach Checkpoint-Vorgängen gelöscht und unterliegen **nicht** `VACUUM`.
- Bereits im Disk-Cache liegende Parquet-Daten können auch nach dem Löschen noch abfragbar sein, bis ein Cluster-Neustart den Cache leert.

### 3.4 REORG TABLE für Soft-Deletes

```sql
REORG TABLE table_name APPLY (PURGE);
```

Schreibt Daten physisch neu, um Soft-Deletes zu entfernen, die durch Column Mapping oder Deletion Vectors entstanden sind.

### 3.5 Cluster-Empfehlungen

- Autoscaling: 1–4 Worker mit je 8 Kernen.
- Driver: 8–32 Kerne (erhöhen, um OOM-Fehler zu vermeiden).
- Bei Tabellen, die 10.000+ Dateien löschen: zusätzliche Worker-Knoten für die Identifikationsphase, oder größerer Driver für die Löschphase.

### 3.6 Audit-Logging aktivieren

```sql
SET spark.databricks.delta.vacuum.logging.enabled = true;
SET spark.databricks.iceberg.vacuum.logging.enabled = true;
```

Für Unity-Catalog-Managed-Tables standardmäßig aktiviert. **AWS-S3-External-Tables:** Audit-Logging ist hier standardmäßig deaktiviert (S3-Konsistenz-Einschränkungen) — nur aktivieren, wenn sichergestellt ist, dass keine externen Clients in den Speicherort schreiben.

---

## <a id="auto-ttl">4. Auto-TTL: automatische zeitgesteuerte Zeilenlöschung</a>

Auto-TTL (Time-to-Live) entfernt automatisch Zeilen aus Unity-Catalog-Managed-Tables nach einer konfigurierbaren Dauer, basierend auf den Werten einer Timestamp-Spalte. Das System führt dazu im Hintergrund drei Operationen in Sequenz aus: **1. `DELETE`** entfernt abgelaufene Zeilen (nur Metadaten-Markierung), **2. `PURGE`** schreibt Datendateien physisch neu (nur falls Deletion Vectors aktiviert sind), **3. `VACUUM`** entfernt die gelöschten Daten endgültig aus dem Storage.

**Typische Anwendungsfälle:**

- Daten älter als 1 Jahr entfernen, um Storage-Kosten zu senken (365-Tage-Ablauf auf `created_at`).
- Zeilen löschen, die durch Geschäftsprozesse zur Löschung markiert wurden (20-Tage-Ablauf auf einer benutzerdefinierten Spalte `del_request_approved`).

**Wichtiger Hinweis:** „Der exakte Löschzeitpunkt ist nicht garantiert und kann je nach Systemlast variieren."

### 4.1 Voraussetzungen

1. **Predictive Optimization** muss aktiviert sein — bei Deaktivierung führt Auto-TTL keine Löschungen mehr aus.
2. **Berechtigungen:** `MODIFY`-Berechtigung auf der Tabelle.
3. **Runtime:** Databricks Runtime 17.3+ (17.2 und darunter können Auto-TTL-Tabellen lesen/schreiben).
4. **Tabellentypen:** Unity-Catalog-Managed-Delta-Lake-, Apache-Iceberg- und Streaming-Tables mit Lakeflow-Pipelines.
5. **Spaltentyp:** Die Timestamp-Spalte muss vom Typ `DATE`, `TIMESTAMP` oder `TIMESTAMP_NTZ` sein. Eine Umbenennung dieser Spalte ist bei aktiviertem Auto-TTL nicht unterstützt (auch nicht bei aktiviertem Column Mapping).

### 4.2 Konfiguration

**Delta-Lake- und Apache-Iceberg-Tabellen — neue Tabelle:**

```sql
CREATE TABLE table_name DELETE ROWS <expiration_days> DAYS AFTER <time_column_name>;
```

**Bestehende Tabelle:**

```sql
ALTER TABLE my_catalog.my_schema.my_table DELETE ROWS 30 DAYS AFTER created_at;
```

**Streaming Tables mit Lakeflow-Pipelines (SQL):**

```sql
CREATE STREAMING TABLE table_name
DELETE ROWS <expiration_days> DAYS AFTER <time_column_name>
AS SELECT * FROM STREAM(source);
```

**Streaming Tables mit Lakeflow-Pipelines (Python):**

```python
from pyspark import pipelines as dp

@dp.table(
  auto_ttl={"timestamp_column": <time_column_name>,
            "expire_in_days": <expiration_days>}
)
def function_name():
  return (query)
```

**Streaming-Reads von Auto-TTL-Tabellen** — `skipChangeCommits` setzen (Structured Streaming, Lakeflow-Pipelines oder Streaming Tables als Leser):

```python
spark.readStream.format("delta") \
  .option("skipChangeCommits", "true") \
  .table("source_table")
```

```sql
CREATE OR REFRESH STREAMING TABLE my_table AS
SELECT * FROM STREAM(source_table) OPTIONS (skipChangeCommits);
```

### 4.3 Verifikation und Verwaltung

**Aktivierung prüfen:**

```sql
DESCRIBE TABLE EXTENDED table_name;
SHOW TBLPROPERTIES table_name;
```

Auf die Eigenschaften `autottl.expireInDays` und `autottl.timestampColumn` achten.

**Deaktivieren:**

```sql
ALTER TABLE table_name DROP ROW DELETION;
```

Bei Streaming Tables `auto_ttl=None` im Pipeline-Code setzen.

### 4.4 Daten-Lebenszyklus-Phasen

| Phase | Dauer | Beschreibung |
|---|---|---|
| **Expiration Period** | benutzerdefiniert | Tage nach dem Timestamp, ab denen eine Zeile zur Löschung berechtigt ist |
| **Buffer Time** | bis zu 3 Tage je Befehl | asynchrone Verzögerung für `DELETE` und `VACUUM` (bis zu 6 Tage insgesamt) |
| **Data Retention Duration** | benutzerdefiniert (Standard 7 Tage) | Zeit, in der gelöschte Zeilen weiterhin über Time Travel zugänglich bleiben |
| **Permanente Löschung** | sofort | Nach Abschluss von `VACUUM` sind die Zeilen nicht mehr zugänglich (auch nicht über Time Travel) |

Mit Standardwerten (Buffer bis zu 6 Tage, Retention 7 Tage) beträgt die maximale Gesamtverzögerung bis zur endgültigen Löschung somit bis zu 13 Tage zusätzlich zur konfigurierten Expiration Period.

**Zeitleisten-Formel:**

```
Gesamtzeit = Expiration_Days + 6 (Buffer) + Retention_Days
```

**Ziel-Expiration-Einstellung berechnen** (um Zeilen innerhalb eines bestimmten Zeitraums zu entfernen):

```
target_expiration_days = target_days - 6 - deletedFileRetentionDuration
```

**Beispiel 1:** Entfernung nach 30 Tagen bei 7-Tage-Standard-Retention → `30 - 6 - 7 = 17 DAYS`

**Beispiel 2:** Entfernung nach 90 Tagen bei 30-Tage-Retention → `90 - 6 - 30 = 54 DAYS`

### 4.5 Monitoring

**Operationen der letzten 7 Tage überwachen:**

```sql
WITH tables_with_deletes AS (
  SELECT DISTINCT catalog_name, schema_name, table_name
  FROM system.storage.predictive_optimization_operations_history
  WHERE operation_type = 'DELETE'
    AND timestampdiff(day, start_time, now()) < 7
)
SELECT hist.*
FROM system.storage.predictive_optimization_operations_history AS hist
INNER JOIN tables_with_deletes AS t
  ON hist.catalog_name = t.catalog_name
  AND hist.schema_name = t.schema_name
  AND hist.table_name = t.table_name
WHERE hist.operation_type IN ('DELETE', 'PURGE', 'VACUUM')
  AND timestampdiff(day, hist.start_time, now()) < 7
ORDER BY hist.start_time DESC;
```

**Kostenschätzung (30 Tage):**

```sql
WITH tables_with_deletes AS (
  SELECT DISTINCT table_name
  FROM system.storage.predictive_optimization_operations_history
  WHERE operation_type = 'DELETE'
    AND timestampdiff(day, start_time, now()) < 30
)
SELECT SUM(usage_quantity) AS total_estimated_dbu
FROM system.storage.predictive_optimization_operations_history AS hist
INNER JOIN tables_with_deletes AS t
  ON hist.table_name = t.table_name
WHERE hist.operation_type IN ('DELETE', 'PURGE', 'VACUUM')
  AND hist.usage_unit = 'ESTIMATED_DBU'
  AND timestampdiff(day, hist.start_time, now()) < 30;
```

**Historie einer bestimmten Tabelle prüfen:**

```sql
DESCRIBE HISTORY table_name;
```

### 4.6 Wichtige Einschränkungen

- Nicht unterstützt auf Materialized Views.
- Kann in seltenen Fällen zu Transaktionskonflikten führen — Liquid Clustering reduziert dieses Risiko.
- Serverless-Compute-S3-Zugriff über Private Link kann zu Fehlschlägen führen.
- `ALTER TABLE`-Syntax für Streaming Tables nicht unterstützt.

---

## <a id="zusammenfassung">5. Zusammenfassung</a>

- **`DROP TABLE`** verhält sich je nach Tabellentyp und Metastore unterschiedlich — nur Managed Tables in Unity Catalog sind über `UNDROP` innerhalb von 7 Tagen wiederherstellbar. `CREATE OR REPLACE TABLE` ist dem Anti-Pattern `DROP` + `CREATE` vorzuziehen.
- **`OPTIMIZE`** kompaktiert Dateien idempotent, täglich empfohlen, im Detail bereits in der Performance-Optimization-Dokumentation behandelt.
- **`VACUUM`** entfernt nicht mehr referenzierte Dateien nach der Retention-Frist — ergänzend hier: konfigurierbare Retention über `deletedFileRetentionDuration` (Delta/Iceberg), Time-Travel-Verlust nach dem Lauf, LITE-Modus-Voraussetzungen (Runtime 16.4 LTS+), Sonderverzeichnisse (`_change_data`, `_delta_index`), Low-Retention-Override und Audit-Logging (inkl. S3-External-Table-Ausnahme).
- **Auto-TTL** automatisiert zeitgesteuerte Zeilenlöschung vollständig über `DELETE ROWS ... DAYS AFTER <spalte>` — mit einer klaren Formel zur Berechnung der Ziel-Expiration-Einstellung und integriertem Monitoring über die Predictive-Optimization-Systemtabelle.

---

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### OPTIMIZE

Vollständiges Syntax-Diagramm: `OPTIMIZE table_name [FULL] [WHERE predicate] [ZORDER BY (col_name1 [, ...])]`

```sql
OPTIMIZE events;
OPTIMIZE events FULL;
OPTIMIZE events WHERE date >= '2017-01-01';

OPTIMIZE events
WHERE date >= current_timestamp() - INTERVAL 1 day
ZORDER BY (eventType);
```

**Kompressions-Codec ändern und Tabelle neu komprimieren:**

```sql
ALTER TABLE table_name SET TBLPROPERTIES ('delta.parquet.compression.codec' = 'ZSTD');
OPTIMIZE table_name FULL;
```

### REORG TABLE

Vollständiges Syntax-Diagramm — über die bereits behandelte `APPLY (PURGE)`-Variante hinaus unterstützt `REORG TABLE` auch Iceberg-Kompatibilitäts-Upgrades, manuelle Checkpoints und Parquet-Format-Versionen:

```sql
REORG [ TABLE ] table_name { [ WHERE predicate ] APPLY ( PURGE ) |
                             APPLY ( UPGRADE UNIFORM ( ICEBERG_COMPAT_VERSION = version ) |
                                     CHECKPOINT |
                                     SET PARQUET ( FORMAT_VERSION = version ) ) }
```

```sql
REORG TABLE events WHERE date >= '2022-01-01' APPLY (PURGE);

-- Auf Iceberg-Kompatibilität upgraden
REORG TABLE events APPLY (UPGRADE UNIFORM(ICEBERG_COMPAT_VERSION=2));

-- Manuellen Checkpoint auslösen (z. B. nach Checkpoint-V2-Umstellung)
REORG TABLE events APPLY (CHECKPOINT);
```

### VACUUM

Vollständiges Syntax-Diagramm: `VACUUM table_name { { FULL | LITE } | DRY RUN } [...]`

```sql
VACUUM table_name;

ALTER TABLE table_name SET TBLPROPERTIES ('delta.deletedFileRetentionDuration' = '30 days');
```

`DRY RUN` liefert eine Liste von bis zu 1000 Dateien, die gelöscht würden, ohne sie tatsächlich zu entfernen — nützlich zur Kontrolle vor einem produktiven `VACUUM`-Lauf.

### FSCK REPAIR TABLE

Bisher nicht in dieser Datei behandelt: `FSCK REPAIR TABLE` prüft und repariert Inkonsistenzen zwischen Transaktionslog und tatsächlichem Storage-Zustand (fehlende Dateien, korrupte Checkpoints, ungültige Deletion Vectors).

```sql
FSCK REPAIR TABLE t METADATA ONLY DRY RUN;
FSCK REPAIR TABLE t DRY RUN;
FSCK REPAIR TABLE t VERIFY ALL FILES DRY RUN;
```

Syntax: `FSCK REPAIR TABLE table_name [METADATA ONLY | VERIFY ALL FILES | VERIFY FILES MODIFIED BETWEEN start_timestamp AND end_timestamp] [DRY RUN]`. `METADATA ONLY` prüft nur auf Checkpoint-Korruption, der Default-Modus erkennt fehlende Datendateien und ungültige Partitionswerte, `VERIFY ALL FILES` führt eine vollständige Dateiintegritätsprüfung inklusive Deletion Vectors durch.

### GENERATE

Ebenfalls neu: `GENERATE` erzeugt Manifest-Dateien, die den Zugriff auf Delta-Tabellen aus Presto und Athena ermöglichen (Systeme ohne native Delta-Lake-Unterstützung).

```sql
GENERATE symlink_format_manifest FOR TABLE table_name;
```
