# Streaming auf Serverless Compute

> Quelle: <https://docs.databricks.com/aws/en/compute/serverless/streaming>

Serverless Compute unterstützt zwei Streaming-Muster: **kontinuierliche** Pipelines (Latenz in Sekunden) und **inkrementelle/getriggerte** Pipelines (Latenz in Minuten). Kontinuierliche Streams laufen ohne Stopp; inkrementelle verarbeiten Daten nach Zeitplan und beenden sich.

## Unterstützte Streaming-Trigger

> *"Time-based Structured Streaming triggers (`Trigger.ProcessingTime(interval)` and `Trigger.Continuous(interval)`) are not available in serverless notebooks or jobs."*

- **Nur `Trigger.AvailableNow()` wird unterstützt.**
- Abfragen **ohne** expliziten Trigger schlagen fehl mit `INFINITE_STREAMING_TRIGGER_NOT_SUPPORTED` — weil *"Apache Spark defaults to `Trigger.ProcessingTime("0 seconds")`, which is not supported on serverless compute."*

## Empfohlene Ansätze nach Anwendungsfall

| Anwendungsfall | Empfohlener Ansatz |
|---|---|
| Kontinuierliche Low-Latency-ETL | Lakeflow Pipelines im Continuous Mode mit Streaming Tables |
| Cloud-Storage-Ingestion | Auto Loader in Lakeflow Pipelines (niedrige Latenz) **oder** Serverless Jobs mit `Trigger.AvailableNow()` |
| SaaS-/Datenbank-CDC | Lakeflow Connect Managed Connectors |
| SQL-basiertes Streaming | Streaming Tables mit SQL-Statements |
| Periodische Micro-Batches | Serverless Jobs mit `Trigger.AvailableNow()` nach Zeitplan |

## Inkrementelles Streaming (Beispiel)

```python
(spark.readStream
   .format("cloudFiles")
   .option("cloudFiles.format", "json")
   .option("cloudFiles.maxFilesPerTrigger", 1000)
   .load(source_path)
   .writeStream
   .trigger(availableNow=True)
   .option("checkpointLocation", checkpoint_path)
   .toTable("catalog.schema.target_table"))
```

Liest neue Dateien aus dem Cloud-Speicher, verarbeitet alle verfügbaren Daten und schreibt mit Checkpoint-Verwaltung in Delta-Tabellen.

## Micro-Batch-Tuning

> *"Tune batch size with `maxFilesPerTrigger` or `maxBytesPerTrigger` to keep memory predictable."*

Jeder Trigger verarbeitet **alle** in der Quelle verfügbaren Daten — das kann zu größeren Micro-Batches führen als bei einem zeitbasierten Trigger.

## Einschränkungen

- Zeitbasierte Trigger nicht unterstützt.
- Abfragen müssen explizit `Trigger.AvailableNow()` angeben **oder** Lakeflow Pipelines im Continuous Mode verwenden.
- Alle Streaming-Limitierungen des Standard Access Mode gelten ebenfalls.

## Nicht-Streaming-Workloads

Für Dienste mit langlebigen Verbindungen oder HTTP-Endpunkten empfiehlt die Doku **Databricks Apps** (unterstützt FastAPI, Flask, Streamlit u. a.) — nicht Serverless-Streaming.

## Verwandte Themen

- [06 Migration von Classic zu Serverless.md](06%20Migration%20von%20Classic%20zu%20Serverless.md) (Trigger-Migrationstabelle) · [09 Einschraenkungen.md](09%20Einschraenkungen.md)
