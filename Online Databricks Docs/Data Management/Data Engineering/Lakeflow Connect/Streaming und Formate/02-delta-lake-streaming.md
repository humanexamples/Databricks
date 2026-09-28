# Delta Lake als Streaming-Quelle und -Senke

Delta Lake ist eng in Spark Structured Streaming integriert und löst typische Herausforderungen von Streaming-Workloads: Zusammenfassen kleiner Dateien, Exactly-once-Verarbeitung über mehrere Streams hinweg sowie effiziente Erkennung neuer Dateien.

## Vorteile

- Fasst kleine Dateien aus latenzarmer Ingestion zu größeren Dateien zusammen und verbessert so die Performance.
- Garantiert **Exactly-once**-Verarbeitung, auch bei gleichzeitigen Streams oder Batch-Jobs.
- Erkennt neue Dateien effizient, wenn Dateien als Stream-Quelle dienen.

## Delta Lake als Senke: Append-Modus (Standard)

Im Append-Modus werden ausschließlich neue Datensätze angehängt:

```python
(events.writeStream
   .outputMode("append")
   .option("checkpointLocation", "/tmp/delta/events/_checkpoints/")
   .toTable("events"))
```

## Complete-Modus

Ersetzt die gesamte Tabelle nach jedem Batch, z. B. zur Aktualisierung aggregierter Zusammenfassungen:

```python
(spark.readStream
  .table("events")
  .groupBy("customerId")
  .count()
  .writeStream
  .outputMode("complete")
  .option("checkpointLocation", "/tmp/delta/eventsByCustomer/_checkpoints/")
  .toTable("events_by_customer"))
```

## Backlog-Metriken überwachen

Der Streaming-Fortschritt lässt sich über folgende Metriken verfolgen:

- `numBytesOutstanding`: nicht verarbeitete Bytes im Backlog
- `numFilesOutstanding`: nicht verarbeitete Dateien im Backlog
- `numNewListedFiles`: für die Backlog-Berechnung aufgelistete Delta-Dateien
- `backlogEndOffset`: für die Backlog-Berechnung verwendete Tabellenversion

## Umgang mit Änderungen an der Quelltabelle

Standardmäßig erwarten Streaming-Queries, dass Quelltabellen nur angehängte Datensätze enthalten. Für Änderungen (Update/Delete) gibt es vier Ansätze:

| Ansatz | Stärken | Einschränkungen |
| --- | --- | --- |
| `skipChangeCommits` | Einfach, keine komplexe Logik nötig | Verarbeitet nur Appends; Änderungen werden nicht weitergegeben |
| Full Refresh | Einfach umzusetzen | Aufwendig bei großen Datenmengen; komplette Neuverarbeitung nötig |
| Change Data Feed | Behandelt alle Änderungsarten (Insert/Update/Delete) | Erfordert explizite Behandlung mehrerer Änderungsarten |
| Materialisierte Views | Automatische Weitergabe von Änderungen | Höhere Latenz; nur über SQL/Lakeflow |

### skipChangeCommits

Ignoriert Löschungen und Änderungen; verarbeitet nur Appends:

```python
(spark.readStream
  .option("skipChangeCommits", "true")
  .table("source_table"))
```

**Legacy-Optionen:** `ignoreDeletes` behandelt nur Löschungen an Partitionsgrenzen. `ignoreChanges` (verfügbar bis Databricks Runtime 11.3) gibt neu geschriebene Dateien erneut aus – dabei können Duplikate entstehen.

## Idempotente Writes mit foreachBatch

Mit den Optionen `txnAppId` und `txnVersion` lässt sich Idempotenz über mehrere Senken hinweg erreichen:

```python
app_id = ...  # eindeutige Anwendungs-ID
def writeToDeltaLakeTableIdempotent(batch_df, batch_id):
  batch_df.write.format(...).option("txnVersion", batch_id).option("txnAppId", app_id).save(...)  # Ziel 1
  batch_df.write.format(...).option("txnVersion", batch_id).option("txnAppId", app_id).save(...)  # Ziel 2
streamingDF.writeStream.foreachBatch(writeToDeltaLakeTableIdempotent).start()
```

## Upserts mit foreachBatch und MERGE

**SQL-Ansatz (Python):**

```python
def upsertToDelta(microBatchOutputDF, batchId):
  microBatchOutputDF.createOrReplaceTempView("updates")
  microBatchOutputDF.sparkSession.sql("""
    MERGE INTO aggregates t
    USING updates s
    ON s.key = t.key
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
  """)
(streamingAggregatesDF.writeStream
  .foreachBatch(upsertToDelta)
  .outputMode("update")
  .start())
```

**Delta-API-Ansatz (Python):**

```python
from delta.tables import *
deltaTable = DeltaTable.forName(spark, "table_name")
def upsertToDelta(microBatchOutputDF, batchId):
  (deltaTable.alias("t").merge(microBatchOutputDF.alias("s"), "s.key = t.key")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute())
(streamingAggregatesDF.writeStream
  .foreachBatch(upsertToDelta)
  .outputMode("update")
  .start())
```

## Startversion für den Stream festlegen

Mit `startingVersion` oder `startingTimestamp` lässt sich festlegen, ab wann gelesen werden soll, ohne die gesamte Tabellenhistorie zu verarbeiten:

- `startingVersion`: Beginnt ab der angegebenen Version und allen danach committeten Änderungen.
- `startingTimestamp`: Liest Änderungen ab dem angegebenen Zeitstempel (z. B. `"2019-01-01T00:00:00.000Z"`) oder Datum (z. B. `"2019-01-01"`).

## Verarbeitung des initialen Snapshots ohne Datenverlust

Mit `withEventTimeOrder` (ab Databricks Runtime 11.3) lässt sich verhindern, dass beim Verarbeiten des initialen Snapshots Daten durch die Watermark verworfen werden – die Ereigniszeit wird dazu in Buckets aufgeteilt.

**Einschränkungen:** Die Option kann nach Beginn der Snapshot-Verarbeitung nicht mehr geändert werden. Nicht unterstützt bei generierten Ereigniszeit-Spalten oder mehreren Delta-Quellen. Die Performance kann geringer sein; Optimierung über Data Skipping und Partitionierung möglich.

## Rate Limiting

Die Datenmenge pro Micro-Batch lässt sich begrenzen über:

- `maxFilesPerTrigger`: maximale Anzahl neuer Dateien pro Batch (Standard: 1000)
- `maxBytesPerTrigger`: ungefähre Datenmenge pro Batch – ein „weiches“ Maximum, das zur Wahrung des Fortschritts überschritten werden kann

## Wichtige Hinweise

- **Aufbewahrungsfenster:** Die Streaming-Query muss mindestens einmal innerhalb des Aufbewahrungsfensters der Quelltabelle laufen (7 Tage für durch `VACUUM` entfernte Dateien, 30 Tage für das Transaktionsprotokoll), sonst schlägt sie mit `DELTA_FILE_NOT_FOUND_DETAILED` fehl.
- **Konfigurationswarnung:** `spark.sql.files.ignoreMissingFiles` nicht als Workaround auf `true` setzen – das führt still zu falschen Ergebnissen.
- **Leere Commits:** Streams können Commits mit `epochId = -1` beim ersten Batch oder bei Schemaänderungen erzeugen – das ist erwartet und unbedenklich.

---
**Quelle:** https://docs.databricks.com/aws/en/structured-streaming/delta-lake  
**Stand:** 2026-08-07
