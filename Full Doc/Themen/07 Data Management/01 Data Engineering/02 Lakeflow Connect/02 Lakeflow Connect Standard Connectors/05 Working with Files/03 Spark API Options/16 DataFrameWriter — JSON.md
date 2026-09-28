# DataFrameWriter options — JSON

Bereich: **DataFrameWriter options › JSON** (Batch-Schreiben von JSON-Dateien).

Quelle: [Spark API options reference](https://learn.microsoft.com/en-us/azure/databricks/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `compression` | `none` | `none`, `bzip2`, `gzip`, `lz4`, `snappy`, `deflate`, `zstd` | „Compression codec to use when writing." |
| `dateFormat` | `yyyy-MM-dd` | Datumsformat-String | „Format string for date column values." |
| `encoding` | `UTF-8` | `java.nio.charset.Charset`-Name | „The character encoding for the output files." |
| `ignoreNullFields` | Wert von `spark.sql.jsonGenerator.ignoreNullFields` | `true`, `false` | „Whether to omit fields with null values from the JSON output." |
| `lineSep` | `\n` | String | „The line separator string used between records." |
| `locale` | `en-US` | `java.util.Locale`-Identifier | „A Java locale identifier that affects default date, timestamp, and decimal parsing within the JSON." |
| `pretty` | `false` | `true`, `false` | „Whether to enable pretty (indented, multiline) JSON output." |
| `sortKeys` | `false` | `true`, `false` | „Whether to sort the keys of JSON objects alphabetically in the output. Useful for producing deterministic output." |
| `timestampFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]` | Timestamp-Format-String | „The format string for timestamp column values." |
| `timestampNTZFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS]` | Timestamp-Format-String | „Format string for timestamp without timezone (`TimestampNTZType`) column values." |
| `writeNonAsciiCharacterAsCodePoint` | `false` | `true`, `false` | „Whether to encode non-ASCII characters as `\uXXXX` Unicode escape sequences instead of literal UTF-8 characters in the output." |

## Beispiel

```python
(df.write.format("json")
  .option("compression", "gzip")
  .option("ignoreNullFields", "false")
  .save("/Volumes/analytics/silver/json_out"))
```
