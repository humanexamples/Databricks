# DataFrameReader options — Parquet

Bereich: **DataFrameReader options › Parquet** (Batch-Lesen von Parquet-Dateien).

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `datetimeRebaseMode` | `LEGACY` | enum | „Controls the rebasing of the DATE and TIMESTAMP values between Julian and Proleptic Gregorian calendars." |
| `int96RebaseMode` | `LEGACY` | enum | „Controls the rebasing of the INT96 timestamp values between Julian and Proleptic Gregorian calendars." |
| `mergeSchema` | `false` | boolean | „Whether to infer the schema across multiple files and to merge the schema of each file." |
| `readerCaseSensitive` | `true` | boolean | „Specifies the case sensitivity behavior when `rescuedDataColumn` is enabled." |
| `rescuedDataColumn` | None | Spaltenname | „Whether to collect all data that can't be parsed due to data type or schema mismatch." |

## Beispiel

```python
df = (spark.read.format("parquet")
  .option("mergeSchema", "true")
  .load("/Volumes/dbacademy_ecommerce/v01/raw/users-historical"))
```

```sql
SELECT * FROM parquet.`/Volumes/dbacademy_ecommerce/v01/raw/users-historical`;
```

## Siehe auch

- [`../04 Dateitypen/06 Ingesting Parquet.md`](../04%20Dateitypen/06%20Ingesting%20Parquet.md)
