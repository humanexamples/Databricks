# DataFrameWriter options — Parquet

Bereich: **DataFrameWriter options › Parquet** (Batch-Schreiben von Parquet-Dateien).

Quelle: [Spark API options reference](https://learn.microsoft.com/en-us/azure/databricks/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `compression` | `snappy` | `none`, `uncompressed`, `snappy`, `gzip`, `lzo`, `brotli`, `lz4`, `lz4_raw`, `zstd` | „Compression codec to use when writing." |
| `spark.sql.parquet.outputTimestampType` | `INT96` | `INT96`, `TIMESTAMP_MICROS`, `TIMESTAMP_MILLIS` | „The physical type used to encode timestamp columns. Use `INT96` for compatibility with legacy Parquet readers that do not support the standard timestamp types." |

## Beispiel

```python
(df.write.format("parquet")
  .option("compression", "zstd")
  .save("/Volumes/analytics/silver/parquet_out"))
```
