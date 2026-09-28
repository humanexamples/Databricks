# DataFrameWriter options — ORC

Bereich: **DataFrameWriter options › ORC** (Batch-Schreiben von ORC-Dateien).

Quelle: [Spark API options reference](https://learn.microsoft.com/en-us/azure/databricks/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `compression` | `zstd` | `none`, `uncompressed`, `snappy`, `zlib`, `lzo`, `zstd`, `lz4`, `brotli` | „Compression codec to use when writing." |

## Beispiel

```python
(df.write.format("orc").option("compression", "zlib").save("/Volumes/analytics/silver/orc_out"))
```
