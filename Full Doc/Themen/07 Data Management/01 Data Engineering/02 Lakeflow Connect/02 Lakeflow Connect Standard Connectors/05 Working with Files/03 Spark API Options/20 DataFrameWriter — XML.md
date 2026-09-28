# DataFrameWriter options — XML

Bereich: **DataFrameWriter options › XML** (Batch-Schreiben von XML-Dateien).

Quelle: [Spark API options reference](https://learn.microsoft.com/en-us/azure/databricks/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `arrayElementName` | `item` | String | „The element name for array elements that have no explicit name." |
| `attributePrefix` | `_` | String | „The prefix prepended to field names that correspond to XML attributes." |
| `compression` | `none` | `none`, `bzip2`, `gzip`, `lz4`, `snappy`, `deflate`, `zstd` | „Compression codec to use when writing." |
| `dateFormat` | `yyyy-MM-dd` | Datumsformat-String | „Format string for date column values." |
| `declaration` | `version="1.0" encoding="UTF-8" standalone="yes"` | XML-Deklarations-String (oder Leerstring) | „The XML declaration string written at the top of each output file. Set to an empty string to suppress the declaration." |
| `encoding` | `UTF-8` | `java.nio.charset.Charset`-Name | „The character encoding for the output files." |
| `indent` | 4 Leerzeichen | String | „The string used to indent child elements in the output. Set to an empty string to turn off indentation and write each row on a single line." |
| `locale` | `en-US` | `java.util.Locale`-Identifier | „A Java locale identifier that affects default date, timestamp, and decimal formatting within the XML." |
| `nullValue` | `null` | String | „The string written for null values. When set to `null`, attributes and child elements for null fields are omitted." |
| `rootTag` | `ROWS` | String | „The root element tag that wraps all row elements in the output." |
| `rowTag` | `ROW` | String | „The element tag that represents a row in the output." |
| `singleVariantColumn` | None | Spaltenname-String | „The name of the single Variant column to write to XML files." |
| `timestampFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]` | Timestamp-Format-String | „The format string for timestamp column values." |
| `timestampNTZFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS]` | Timestamp-Format-String | „Format string for timestamp without timezone column values." |

## Beispiel

```python
(df.write.format("xml")
  .option("rootTag", "books")
  .option("rowTag", "book")
  .save("/Volumes/analytics/silver/books_out"))
```
