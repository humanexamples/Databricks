# DataFrameWriter options — Text

Bereich: **DataFrameWriter options › Text** (Batch-Schreiben von Textdateien; der DataFrame muss genau eine `string`-Spalte haben).

Quelle: [Spark API options reference](https://learn.microsoft.com/en-us/azure/databricks/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `compression` | `none` | `none`, `bzip2`, `gzip`, `lz4`, `snappy`, `deflate`, `zstd` | „Compression codec to use when writing." |
| `encoding` | `UTF-8` | `java.nio.charset.Charset`-Name | „The character encoding for the output files." |
| `lineSep` | `\n` | String | „The line separator string used between records." |

## Beispiel

```python
(df.select("value").write.format("text")
  .option("compression", "gzip")
  .save("/Volumes/analytics/silver/text_out"))
```
