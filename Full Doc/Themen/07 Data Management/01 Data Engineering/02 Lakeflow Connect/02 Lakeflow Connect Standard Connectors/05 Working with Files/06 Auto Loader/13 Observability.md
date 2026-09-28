# Auto Loader — Observability

Quelle: [Monitor and observe Auto Loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/observability); Feldreferenz: [cloud_files_state table-valued function](https://docs.databricks.com/aws/en/sql/language-manual/functions/cloud_files_state).

## Abschnitte

1. [Voraussetzungen](#voraussetzungen)
2. [Wichtige Metriken und Warnsignale](#metriken)
3. [`cloud_files_state`: Feldreferenz](#cloud-files-state)
4. [`cloud_files_state`: Abfragebeispiele](#abfragen)
5. [`StreamingQueryListener`-Metriken](#listener)
6. [Monitoring in Lakeflow-Pipelines](#lakeflow)
7. [Observability-Dashboard](#dashboard)
8. [Schema-Evolution-Ereignisse überwachen](#schema-evolution)
9. [Alarme einrichten](#alarme)
10. [Troubleshooting](#troubleshooting)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

- **Databricks Runtime 18.2+** für automatische `discovery_time`-, `processed_time`- und `commit_time`-Felder.
- **Runtime 16.4–18.1** benötigt aktiviertes `cloudFiles.cleanSource` für diese Zeitstempel.
- **Runtime 16.4+** mit `cloudFiles.cleanSource` liefert `archive_time`, `archive_mode` und `move_location`.
- Ingestierte Daten mit `_metadata`-Spalte annotieren (mindestens `file_path`, `file_modification_time`).
- `_rescued_data`- und `_corrupt_record`-Spalten für Datenqualitäts-Tracking aktivieren.

---

## <a id="metriken">2. Wichtige Metriken und Warnsignale</a>

| Metrik | Zweck |
|---|---|
| `numFilesOutstanding` | Dateien im Backlog, die auf Verarbeitung warten |
| `numBytesOutstanding` | Backlog-Größe in Bytes |
| `approximateQueueSize` | Cloud-Queue-Tiefe (nur File-Notification-Modus, ab DBR 10.4 LTS, AWS/Azure) |
| `numInputRows` | Zeilen pro Batch |
| `inputRowsPerSecond` | Datenankunftsrate |
| `processedRowsPerSecond` | Verarbeitungsdurchsatz |
| `durationMs`-Aufschlüsselung | Zeitverteilung über die Batch-Phasen |

### Warnsignale

- **Wachsendes `numFilesOutstanding`:** *"The backlog is building up. Your pipeline is falling behind incoming data."*
- **`processedRowsPerSecond` < `inputRowsPerSecond`:** Pipeline verarbeitet langsamer, als Daten eintreffen.
- **Großes `durationMs.latestOffset`:** Datei-Erkennung ist der Engpass — File Events erwägen.
- **Großes `durationMs.addBatch`:** Datenverarbeitung ist der Engpass — Compute skalieren oder Transformationen optimieren.

---

## <a id="cloud-files-state">3. `cloud_files_state`: Feldreferenz</a>

Die Tabellenfunktion `cloud_files_state` (Databricks SQL und ab **Databricks Runtime 11.3 LTS**) liefert den dateibezogenen Zustand eines Auto-Loader- oder `read_files`-Streams. Aufrufsyntax: `cloud_files_state( { TABLE ( table_name ) | checkpoint } )` — als Argument entweder der Name einer Streaming Table (ab DBR 13.3 LTS) oder ein Checkpoint-Pfad als String-Literal.

| Feld | Typ | Beschreibung | Verfügbarkeit |
|---|---|---|---|
| `path` | `STRING NOT NULL PRIMARY KEY` | Der Pfad einer Datei. | Ab DBR 11.3 LTS |
| `size` | `BIGINT NOT NULL` | Die Größe einer Datei in Bytes. | Ab DBR 11.3 LTS |
| `create_time` | `TIMESTAMP NOT NULL` | Zeitpunkt, an dem eine Datei erstellt wurde. | Ab DBR 11.3 LTS |
| `discovery_time` | `TIMESTAMP NOT NULL` | Zeitpunkt, an dem eine Datei entdeckt wurde. | Ab DBR 16.4 |
| `processed_time` | `TIMESTAMP NOT NULL` | Zeitpunkt, an dem eine Datei verarbeitet wurde. Bei Batch-Fehlschlag mit Retry: jüngster Verarbeitungszeitpunkt. | Streams auf DBR 16.4+ mit `cloudFiles.cleanSource`, oder DBR 18.2+ |
| `commit_time` | `TIMESTAMP` | Zeitpunkt, an dem eine Datei nach der Verarbeitung im Checkpoint committet wurde. `NULL`, falls noch nicht verarbeitet. Keine garantierte Latenz bis zur Markierung. | Streams auf DBR 16.4+ mit `cloudFiles.cleanSource`, oder DBR 18.2+ |
| `archive_time` | `TIMESTAMP` | Zeitpunkt der Archivierung. `NULL`, falls nicht archiviert. | Ab DBR 16.4, wenn `cloudFiles.cleanSource` aktiviert |
| `archive_mode` | `STRING` | `MOVE` / `DELETE` je nach `cloudFiles.cleanSource`; `NULL` bei `OFF`. | Ab DBR 16.4, wenn `cloudFiles.cleanSource` aktiviert |
| `move_location` | `STRING` | Vollständiger Zielpfad bei `cloudFiles.cleanSource = MOVE`. `NULL` sonst. | Ab DBR 16.4, wenn `cloudFiles.cleanSource` aktiviert |
| `source_id` | `STRING` | ID der Auto-Loader-Quelle in der Streaming-Abfrage. Bei nur einer Cloud-Objektspeicher-Quelle: `'0'`. | Ab DBR 11.3 LTS |
| `flow_name` | `STRING` | Bestimmter Streaming-Flow in Lakeflow-Pipelines, der eine oder mehrere `cloudFiles`-Quellen enthält. `NULL`, falls kein `table_name` angegeben. | Ab DBR 13.3 |
| `ingestion_state` | `STRING` | Ingestion-Zustand der Datei (Werte siehe unten). | Ab DBR 16.4 |

**Berechtigungen:** Bei Verwendung eines Streaming-Table-Bezeichners: auf DBR 17.1 und darunter `OWNER`-Rechte auf der Streaming Table; auf Databricks SQL und DBR 17.2+ `SELECT`- und `MODIFY`-Rechte. Wird ein Checkpoint innerhalb einer External Location angegeben: `READ FILES`-Rechte auf dem Checkpoint-Speicherort. Nutzer, die eine View lesen, die auf `cloud_files_state` über eine Streaming Table verweist, benötigen sowohl `SELECT` auf der View als auch die erforderlichen Rechte auf der Streaming Table selbst.

**Mögliche Werte von `ingestion_state`:**

- `NULL` — Datei noch nicht verarbeitet, oder Zustand nicht bestimmbar.
- `PROCESSING` — Datei wird gerade verarbeitet.
- `SKIPPED_CORRUPTED` — Datei nicht aufgenommen, weil beschädigt.
- `SKIPPED_MISSING` — Datei nicht aufgenommen, weil während der Verarbeitung nicht gefunden.
- `INGESTED` — Datei mindestens einmal von der Senke verarbeitet. Kann bei nicht-idempotenten Senken wie `foreachBatch` bei Stream-Fehlern erneut verarbeitet werden. Nur Dateien mit nicht-null `commit_time` **und** Zustand `INGESTED` haben die Verarbeitung vollständig abgeschlossen.
- `NOT_RECOGNIZED_BY_DBR` — Reserviert für Versionskompatibilität.

```sql
-- Beispiele aus der Sprachreferenz
SELECT path FROM CLOUD_FILES_STATE('/some/checkpoint');
SELECT path FROM CLOUD_FILES_STATE('/some/checkpoint/sources/0');
SELECT path FROM CLOUD_FILES_STATE(TABLE(my_streaming_table));
```

> **Auffälligkeit (Doku-Inkonsistenz):** Die Observability-Seite selbst verwendet in einem Beispiel den Filterwert `ingestion_state != 'COMMITTED'` — dieser Wert ist in der Feldreferenz **nicht** als gültiger `ingestion_state`-Wert dokumentiert (der Erfolgszustand heißt `INGESTED`). Dieses Dokument verwendet konsequent `'INGESTED'`.

---

## <a id="abfragen">4. `cloud_files_state`: Abfragebeispiele</a>

```sql
-- Unverarbeitete Dateien (aktueller Backlog)
SELECT * FROM cloud_files_state('path/to/checkpoint')
WHERE ingestion_state != 'INGESTED';
```

```sql
-- Durchschnittliche Ingestion-Latenz
SELECT avg(unix_timestamp(commit_time) - unix_timestamp(create_time))
  AS avg_latency_seconds
FROM cloud_files_state('path/to/checkpoint')
WHERE commit_time IS NOT NULL AND create_time IS NOT NULL;
```

```sql
-- Beschädigte oder übersprungene Dateien
SELECT path, ingestion_state, size, create_time
FROM cloud_files_state('path/to/checkpoint')
WHERE ingestion_state LIKE 'SKIPPED%';
```

```sql
-- Archivierungsfortschritt
SELECT archive_mode, count(*) AS file_count
FROM cloud_files_state('path/to/checkpoint')
GROUP BY archive_mode;
```

```sql
-- Dateien mit hoher Latenz (Engpässe identifizieren)
SELECT
  path,
  size,
  unix_timestamp(commit_time) - unix_timestamp(discovery_time)
    AS processing_latency_seconds,
  unix_timestamp(commit_time) - unix_timestamp(create_time)
    AS end_to_end_latency_seconds
FROM cloud_files_state('path/to/checkpoint')
WHERE commit_time IS NOT NULL
ORDER BY end_to_end_latency_seconds DESC
LIMIT 20;
```

---

## <a id="listener">5. `StreamingQueryListener`-Metriken</a>

Metriken: `numFilesOutstanding`, `numBytesOutstanding`, `approximateQueueSize` (nur File-Notification-Modus, ab DBR 10.4 LTS, AWS/Azure), `numInputRows`, `inputRowsPerSecond`, `processedRowsPerSecond`, sowie eine Aufschlüsselung von `durationMs` über die Batch-Phasen.

```python
from pyspark.sql.streaming import StreamingQueryListener

class AutoLoaderMonitor(StreamingQueryListener):
    def onQueryStarted(self, event):
        pass

    def onQueryProgress(self, event):
        for source in event.progress.sources:
            if "CloudFilesSource" in source.description:
                metrics = source.metrics
                files_outstanding = metrics.get("numFilesOutstanding", "0")
                bytes_outstanding = metrics.get("numBytesOutstanding", "0")
                rows_per_sec = source.processedRowsPerSecond
                # Push metrics to monitoring system

    def onQueryIdle(self, event):
        pass

    def onQueryTerminated(self, event):
        pass

spark.streams.addListener(AutoLoaderMonitor())
```

**Datenqualitäts-Metriken per `df.observe()`** (erscheinen in Listener-Progress-Events unter `observedMetrics`):

```python
from pyspark.sql.functions import count, lit, col

observed_df = df.observe(
    "auto_loader_quality",
    count(lit(1)).alias("total_rows"),
    count(col("_rescued_data")).alias("rescued_rows"),
    count(col("_corrupt_record")).alias("corrupt_rows"))
```

Außerhalb von Lakeflow-Pipelines: `StreamingQueryListener` implementieren, `df.observe()` nutzen und Streams über `.queryName()` eindeutig benennen.

---

## <a id="lakeflow">6. Monitoring in Lakeflow-Pipelines</a>

Event-Log in einer Delta-Tabelle speichern, um es abfragbar zu machen.

```sql
-- Ingestion-Durchsatz pro Flow
SELECT
  origin.flow_name,
  origin.update_id,
  timestamp,
  TRY_CAST(details:flow_progress.metrics.num_output_rows AS BIGINT)
    AS rows_written
FROM event_log_raw
WHERE event_type = 'flow_progress'
ORDER BY timestamp DESC;
```

```sql
-- Daten-Backlog
SELECT
  origin.flow_name,
  timestamp,
  DOUBLE(details:flow_progress.metrics.backlog_bytes) AS backlog_bytes
FROM event_log_raw
WHERE event_type = 'flow_progress'
  AND details:flow_progress.metrics.backlog_bytes IS NOT NULL
ORDER BY timestamp DESC;
```

```sql
-- Zusammenfassung von Expectation-Verletzungen
SELECT
  origin.flow_name,
  explode(from_json(
    details:flow_progress.data_quality.expectations,
    'array<struct<name:string, dataset:string, passed_records:bigint,
      failed_records:bigint>>'
  )) AS expectation
FROM event_log_raw
WHERE event_type = 'flow_progress'
  AND details:flow_progress.data_quality.expectations IS NOT NULL;
```

---

## <a id="dashboard">7. Observability-Dashboard</a>

| Datenquelle | Inhalt |
|---|---|
| `cloud_files_state()` | Dateibezogene Zeitstempel: Discovery, Verarbeitung, Commit, Archivierung |
| Lakeflow Event-Log | Pipeline-Lauf-Historie, Flow-Metriken pro Batch, Datenqualitäts-Ergebnisse |
| Ausgabetabellen | Zeilenanzahlen, geschriebenes Datenvolumen pro Zieltabelle |

**Empfohlene Panels:** Pipeline-Laufstatus-Zeitverlauf, Ingestion-Backlog-Trend, Durchsatz-Trend, Verteilung der Ingestion-Latenz, Datenqualitäts-Metriken, Schema-Evolution-Ereignisse, Datei-Archivierungsstatus.

---

## <a id="schema-evolution">8. Schema-Evolution-Ereignisse überwachen</a>

Erkennungsansätze: nicht-`NULL`-Werte in `_rescued_data` überwachen; das `_schemas`-Verzeichnis in `cloudFiles.schemaLocation` auf neue Dateien pollen; `_metadata.file_path` nutzen, um Schema-Änderungen mit bestimmten Dateien zu korrelieren.

```sql
-- Schema-Drift über Expectation-Verletzungen erkennen
SELECT
  timestamp,
  origin.flow_name,
  exp.name AS expectation_name,
  exp.failed_records
FROM (
  SELECT
    timestamp,
    origin,
    explode(from_json(
      details:flow_progress.data_quality.expectations,
      'array<struct<name:string, dataset:string, passed_records:bigint,
        failed_records:bigint>>'
    )) AS exp
  FROM event_log_raw
  WHERE event_type = 'flow_progress'
    AND details:flow_progress.data_quality.expectations IS NOT NULL
)
WHERE exp.name = '<rescued-data expectation name>'
  AND exp.failed_records > 0
ORDER BY timestamp DESC;
```

---

## <a id="alarme">9. Alarme einrichten</a>

```sql
-- Wachsenden Backlog erkennen
WITH recent_backlog AS (
  SELECT
    origin.flow_name,
    timestamp,
    DOUBLE(details:flow_progress.metrics.backlog_bytes) AS backlog_bytes,
    ROW_NUMBER() OVER (PARTITION BY origin.flow_name
      ORDER BY timestamp DESC) AS rn
  FROM event_log_raw
  WHERE event_type = 'flow_progress'
    AND details:flow_progress.metrics.backlog_bytes IS NOT NULL
)
SELECT flow_name, backlog_bytes, timestamp
FROM recent_backlog
WHERE rn = 1
  AND backlog_bytes > 1073741824; -- Alarm bei Backlog > 1 GB
```

| Problem | Erkennungsmethode | Alarm-Auslöser |
|---|---|---|
| Wachsender Backlog | `numFilesOutstanding`-Trend | Anhaltender Anstieg über mehrere Batches |
| Gestoppter Stream | Keine Progress-Events | N Minuten ohne Events |
| Hohe Latenz | `commit_time - create_time` | Überschreitet SLA-Schwellwert |
| Datenqualität verschlechtert sich | Expectation-Fehlerrate | Steigender Verletzungsanteil |
| Schema-Evolution | `_rescued_data IS NOT NULL` | Beliebige nicht-`NULL`-Werte |
| Langsame Datei-Erkennung | `durationMs.latestOffset` | Deutlich über dem Ausgangswert |

---

## <a id="troubleshooting">10. Troubleshooting häufiger Probleme</a>

| Problem | Ursache | Lösung |
|---|---|---|
| Backlog wächst schneller als die Verarbeitung | Zu klein dimensionierte Compute, Datenschiefe, gedrosselte Rate-Limits | Compute skalieren, Schiefe in der Spark-UI prüfen, `maxFilesPerTrigger` überprüfen |
| Dateien werden nicht entdeckt | Fehlkonfigurierte File Events, Berechtigungsproblem, Stream lief >7 Tage nicht | External-Location-Berechtigungen prüfen, File-Events-Setup in der Unity-Catalog-UI kontrollieren, wöchentliche Läufe sicherstellen |
| Lange Stream-Startzeit | Großer RocksDB-Checkpoint-Zustand | Upgrade auf Runtime mit asynchronem State-Loading (ab DBR 15.4 LTS, siehe [12 Produktionsbetrieb.md](12%20Produktionsbetrieb.md)) |
| Doppelte Dateiverarbeitung | Aggressives `cloudFiles.maxFileAge`, Checkpoint-Beschädigung | Konservatives `maxFileAge` (mind. 90 Tage), Checkpoint-Integrität prüfen, keine Lifecycle-Richtlinien auf Checkpoint-Speicher |
| Schema-Änderungen verursachen Pipeline-Neustarts | Häufige/inkompatible Schema-Änderungen | `schemaEvolutionMode` überprüfen, `addNewColumnsWithTypeWidening` oder `Variant`-Typ nutzen |
| Beschädigte Daten häufen sich in der Senke an | Datenqualitätsprobleme in der Quelle | `_corrupt_record`-Quarantäne-Senke prüfen, Quelldatengenerierung überprüfen, vorgelagerte Validierung erwägen |
| Fehlende `discovery_time`/`commit_time` | Runtime <18.2 ohne `cleanSource` | Upgrade auf DBR 18.2+ oder `cloudFiles.cleanSource` auf DBR 16.4–18.1 aktivieren |

> **Hinweis:** Eine `WebFetch`-Zusammenfassung der Troubleshooting-Sektion nannte für die Startzeit-Optimierung "Databricks Runtime 15.3"; die Produktions-Seite nennt zweifach bestätigt **15.4 LTS**. Dieses Dokument übernimmt 15.4 LTS.
