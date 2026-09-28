# DataFrameReader options — Avro

Bereich: **DataFrameReader options › Avro** (Batch-Lesen von Avro-Dateien).

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `avroSchema` | None | Avro-Schema-String | „Optional schema specified by a user in Avro format." |
| `avroSchemaEvolutionMode` | `none` | enum | „How to handle schema evolution when using a schema registry." |
| `datetimeRebaseMode` | `LEGACY` | enum | „Controls the rebasing of the DATE and TIMESTAMP values between Julian and Proleptic Gregorian calendars." |
| `enableStableIdentifiersForUnionType` | `false` | boolean | „Whether to use stable field names for Avro Union types." |
| `mergeSchema` | `false` | boolean | „Whether to infer the schema across multiple files and to merge the schema of each file." |
| `mode` | `FAILFAST` | enum | „Parser mode for handling corrupt records." |
| `readerCaseSensitive` | `true` | boolean | „Specifies the case sensitivity behavior when `rescuedDataColumn` is enabled." |
| `recursiveFieldMaxDepth` | None | Ganzzahl (0–15) | „The maximum recursion depth for recursive Avro fields." |
| `rescuedDataColumn` | None | Spaltenname | „Whether to collect all data that can't be parsed due to data type or schema mismatch." |
| `stableIdentifierPrefixForUnionType` | `member_` | String | „The prefix to use for stable union type field names." |

## Beispiel

```python
df = (spark.read.format("avro")
  .option("mergeSchema", "true")
  .load("/Volumes/analytics/bronze/avro_data"))
```
