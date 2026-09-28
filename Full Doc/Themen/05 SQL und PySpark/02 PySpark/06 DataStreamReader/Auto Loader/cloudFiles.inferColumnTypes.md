# `cloudFiles.inferColumnTypes`

Steuert, ob exakte Spaltentypen inferiert werden.

## Beschreibung

> *"Whether to infer exact column types when leveraging schema inference. By default, columns are inferred as strings when inferring JSON and CSV datasets."*

Bei `false` (Standard für das native `cloudFiles`) inferiert Auto Loader alle Spalten in JSON/CSV/XML als `string`, um Schema-Evolution-Probleme durch spätere Typkonflikte von vornherein zu vermeiden. Bei `true` wählt Auto Loader stattdessen konkrete Datentypen anhand von Stichprobendaten — dasselbe Verhalten wie beim normalen Apache-Spark-`DataFrameReader`. Bei bereits typisierten Formaten wie Parquet und Avro hat die Option keine Wirkung, da deren Typinformation schon im Dateiformat kodiert ist.

**Wichtig:** Die SQL-Funktion `read_files` — sowohl im Batch (`SELECT * FROM read_files(...)`) als auch im Streaming-Modus (`STREAM read_files(...)`) — hat für dieselbe Option den **umgekehrten** Default `true`. Nur das native `cloudFiles` über `spark.readStream.format("cloudFiles")` (ohne den Umweg über `read_files`) hat den hier beschriebenen Default `false`.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.inferColumnTypes", True)
      .load("/Volumes/analytics/bronze/events"))
```

```sql
CREATE OR REFRESH STREAMING TABLE events
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaLocation => '/Volumes/analytics/bronze/_schema',
  inferColumnTypes => false   -- explizit nötig: Default bei STREAM read_files ist sonst true
);
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options
- read_files: https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files

**Stand:** 2026-09-15
