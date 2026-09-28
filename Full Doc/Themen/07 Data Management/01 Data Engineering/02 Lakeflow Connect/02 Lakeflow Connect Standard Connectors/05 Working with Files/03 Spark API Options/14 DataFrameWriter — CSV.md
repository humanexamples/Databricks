# DataFrameWriter options — CSV

Bereich: **DataFrameWriter options › CSV** (Batch-Schreiben von CSV-Dateien).

Quelle: [Spark API options reference](https://learn.microsoft.com/en-us/azure/databricks/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `charToEscapeQuoteEscaping` | `\0` (nicht aktiviert) | einzelnes Zeichen | „The character used to escape the escape character when it differs from the quote character." |
| `compression` | `none` | `none`, `bzip2`, `gzip`, `lz4`, `snappy`, `deflate`, `zstd` | „Compression codec to use when writing." |
| `dateFormat` | `yyyy-MM-dd` | Datumsformat-String | „Format string for date column values." |
| `emptyValue` | Leerstring | String | „The string written for empty (non-null) values." |
| `encoding` | `UTF-8` | `java.nio.charset.Charset`-Name | „The character encoding for the output files." |
| `escape` | `\` | einzelnes Zeichen | „The character used to escape quoted values." |
| `escapeQuotes` | `true` | `true`, `false` | „Whether to escape quote characters inside quoted field values." |
| `header` | `false` | `true`, `false` | „Whether to write column names as the first line of the output." |
| `ignoreLeadingWhiteSpace` | `false` | `true`, `false` | „Whether to trim leading whitespace from values when writing." |
| `ignoreTrailingWhiteSpace` | `false` | `true`, `false` | „Whether to trim trailing whitespace from values when writing." |
| `lineSep` | `\n` | String | „The line separator string used between records." |
| `locale` | `en-US` | `java.util.Locale`-Identifier | „A Java locale identifier that affects default date, timestamp, and decimal parsing within the CSV." |
| `nullValue` | Leerstring | String | „String written for null values." |
| `quote` | `"` | einzelnes Zeichen | „The character used to quote field values that contain the separator." |
| `quoteAll` | `false` | `true`, `false` | „Whether to enclose all field values in quotes regardless of content." |
| `sep` | `,` | String | „The field delimiter character." |
| `timestampFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]` | Timestamp-Format-String | „The format string for timestamp column values." |
| `timestampNTZFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS]` | Timestamp-Format-String | „Format string for timestamp without timezone (`TimestampNTZType`) column values." |

## Beispiel

```python
(df.write.format("csv")
  .option("header", "true")
  .option("compression", "gzip")
  .save("/Volumes/analytics/silver/csv_out"))
```
