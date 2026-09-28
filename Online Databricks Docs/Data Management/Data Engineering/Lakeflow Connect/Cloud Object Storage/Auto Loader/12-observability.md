# Auto Loader überwachen (Observability)

Auto-Loader-Pipelines stellen wichtige Metriken über `StreamingQueryListener`-Progress-Events bereit.

## Wichtige Metriken

- **`numFilesOutstanding`**: Anzahl der Dateien im Backlog, die noch verarbeitet werden müssen
- **`numBytesOutstanding`**: Größe des Datei-Backlogs in Bytes
- **`approximateQueueSize`**: Tiefe der Cloud-Queue (nur File Notification Mode)
- **`numInputRows`**: verarbeitete Zeilen pro Batch
- **`inputRowsPerSecond`** und **`processedRowsPerSecond`**: Ankunfts- und Verarbeitungsrate der Daten
- **`durationMs`-Aufschlüsselung**: Zeitverteilung über die Batch-Phasen

## Warnsignale

Wachsende Backlogs (steigendes `numFilesOutstanding`), eine Verarbeitungsrate, die hinter der Ankunftsrate zurückbleibt, sowie erhöhte `durationMs.latestOffset`-Werte deuten auf eine Performance-Verschlechterung hin, die Handlungsbedarf signalisiert.

## Cloud-Files-State-Abfragen

Die Funktion `cloud_files_state()` liefert dateibezogene Ingestion-Details:

```sql
%sql
-- Nicht verarbeitete Dateien finden
SELECT * FROM cloud_files_state('path/to/checkpoint')
WHERE ingestion_state != 'COMMITTED';

-- Durchschnittliche Ingestion-Latenz berechnen
SELECT avg(unix_timestamp(commit_time) - unix_timestamp(create_time))
  AS avg_latency_seconds
FROM cloud_files_state('path/to/checkpoint')
WHERE commit_time IS NOT NULL AND create_time IS NOT NULL;
```

Verfügbare Felder umfassen u. a. Pfad, Größe, Erstellungszeit, Erkennungszeit, Verarbeitungszeit, Commit-Zeit und Ingestion-Status.

## Überwachung mit Structured Streaming

```python
from pyspark.sql.streaming import StreamingQueryListener

class AutoLoaderMonitor(StreamingQueryListener):
    def onQueryProgress(self, event):
        for source in event.progress.sources:
            if "CloudFilesSource" in source.description:
                metrics = source.metrics
                files_outstanding = metrics.get("numFilesOutstanding", "0")
                bytes_outstanding = metrics.get("numBytesOutstanding", "0")
```

## Überwachung von Lakeflow-Pipelines

Über Event-Log-Abfragen lassen sich pipeline-spezifische Einblicke gewinnen:

```sql
%sql
-- Ingestion-Durchsatz pro Flow überwachen
SELECT origin.flow_name, timestamp,
  TRY_CAST(details:flow_progress.metrics.num_output_rows AS BIGINT)
  AS rows_written
FROM event_log_raw
WHERE event_type = 'flow_progress'
ORDER BY timestamp DESC;
```

## Schema-Drift erkennen

Verletzungen der `_rescued_data`-Expectation überwachen, um Schema-Evolution-Ereignisse zu erkennen. Zeitstempel der Verletzungen mit `cloud_files_state()` verknüpfen, um Änderungen bestimmten Dateien zuzuordnen.

## Alarm-Empfehlungen

Alarme einrichten für:

- wachsende Backlogs, die Schwellenwerte überschreiten
- stehengebliebene Streams (keine Progress-Events über N Minuten)
- Ingestion-Latenz, die SLAs überschreitet
- steigende Fehlerquote bei Expectations
- langsame Dateierkennungs-Phasen

## Häufige Probleme und Lösungen

| Problem | Ursache | Lösung |
| --- | --- | --- |
| Wachsender Backlog | Zu klein dimensioniertes Compute oder Datenskew | Ressourcen skalieren; Batch-Größen überprüfen |
| Dateien werden nicht erkannt | Fehlkonfigurierte File Events; Berechtigungen | Zugangsdaten und Einrichtung prüfen |
| Lange Startzeiten | Große Checkpoint-Downloads | Upgrade auf Runtime 15.3+ |
| Doppelte Verarbeitung | Zu aggressive `maxFileAge`-Einstellungen | Konservative Aufbewahrung nutzen (90+ Tage) |

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/observability  
**Stand:** 2026-08-07
