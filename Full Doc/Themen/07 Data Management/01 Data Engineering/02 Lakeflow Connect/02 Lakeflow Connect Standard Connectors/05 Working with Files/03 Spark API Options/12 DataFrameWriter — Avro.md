# DataFrameWriter options — Avro

Bereich: **DataFrameWriter options › Avro** (Batch-Schreiben von Avro-Dateien).

Quelle: [Spark API options reference](https://learn.microsoft.com/en-us/azure/databricks/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `avroSchema` | None | JSON-Schema-String | „The full Avro schema as a JSON string. Use this option to convert Spark SQL types to specific Avro types." |
| `avroSchemaUrl` | None | URL-String | „A URL pointing to an Avro schema file. Use instead of `avroSchema` when the schema is stored externally. Mutually exclusive with `avroSchema`." |
| `compression` | `snappy` | `uncompressed`, `deflate`, `snappy`, `bzip2`, `xz`, `zstandard` | „Compression codec to use when writing." |
| `recordName` | `topLevelRecord` | String | „The top-level record name in the output Avro schema." |
| `positionalFieldMatching` | `false` | `true`, `false` | „Whether to match columns between the Spark schema and the Avro schema by field position instead of by name." |
| `recordNamespace` | Leerstring | String | „The namespace for the top-level record in the output Avro schema." |

## Beispiel

```python
(df.write.format("avro")
  .option("compression", "deflate")
  .save("/Volumes/analytics/silver/avro_out"))
```
