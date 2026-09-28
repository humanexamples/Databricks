# DataFrameReader options — CSV

Bereich: **DataFrameReader options › CSV** (Batch-Lesen von CSV-Dateien).

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `badRecordsPath` | None | Pfad-String | „The path to store files for recording the information about bad CSV records." |
| `charToEscapeQuoteEscaping` | `\0` | Zeichen | „The character used to escape the character used for escaping quotes." |
| `columnNameOfCorruptRecord` | `_corrupt_record` | Spaltenname | „The column for storing records that are malformed and cannot be parsed." |
| `comment` | `\0` | Zeichen | „Defines the character that represents a line comment." |
| `dateFormat` | `yyyy-MM-dd` | Datumsformat | „The format for parsing date strings." |
| `emptyValue` | Leerstring | String | „String representation of an empty value." |
| `enableDateTimeParsingFallback` | `false` | boolean | „Whether to fall back to the legacy date and timestamp parsing behavior." |
| `encoding` / `charset` | `UTF-8` | Charset-Name | „The name of the encoding of the CSV files." |
| `enforceSchema` | `true` | boolean | „Whether to forcibly apply the specified or inferred schema to the CSV files." |
| `escape` | `\` | Zeichen | „The escape character to use when parsing the data." |
| `extension` | `csv` | Dateiendung | „The expected filename extension for reads." |
| `failOnUnknownFields` | `false` | boolean | „Whether to fail when the CSV record contains columns not present in the schema." |
| `failOnWidenedFields` | `false` | boolean | „Whether to fail when a field value cannot be parsed as the declared schema type without widening." |
| `header` | `false` | boolean | „Whether the CSV files contain a header." |
| `ignoreLeadingWhiteSpace` | `false` | boolean | „Whether to ignore leading whitespaces for each parsed value." |
| `ignoreTrailingWhiteSpace` | `false` | boolean | „Whether to ignore trailing whitespaces for each parsed value." |
| `inferSchema` | `false` | boolean | „Whether to infer the data types of the parsed CSV records." (Für Auto Loader stattdessen `cloudFiles.inferColumnTypes`.) |
| `inputBufferSize` | `1048576` | Bytes | „The buffer size in bytes for the CSV parser." |
| `lineSep` | None | String | „A string between two consecutive CSV records." |
| `locale` | `US` | Locale-Identifier | „A Java locale identifier that affects default date, timestamp, and decimal parsing." |
| `maxCharsPerColumn` | `-1` | Ganzzahl | „Maximum number of characters expected from a value to parse." |
| `maxColumns` | `20480` | Ganzzahl | „The hard limit of how many columns a record can have." |
| `mergeSchema` | `false` | boolean | „Whether to infer the schema across multiple files and to merge the schema of each file." |
| `mode` | `PERMISSIVE` | enum | „Parser mode around handling malformed records." |
| `multiLine` | `false` | boolean | „Whether the CSV records span multiple lines." |
| `nanValue` | `NaN` | String | „The string representation of a non-a-number value." |
| `negativeInf` | `-Inf` | String | „The string representation of negative infinity." |
| `nullValue` | Leerstring | String | „String representation of a null value." |
| `parserCaseSensitive` *(veraltet)* | `false` | boolean | „(Deprecated) Whether to align columns declared in the header with the schema case sensitively." |
| `positiveInf` | `Inf` | String | „The string representation of positive infinity." |
| `preferDate` | `true` | boolean | „Attempts to infer strings as dates instead of timestamp when possible." |
| `quote` | `"` | Zeichen | „The character used for escaping values where the field delimiter is part of the value." |
| `readerCaseSensitive` | `true` | boolean | „Specifies the case sensitivity behavior when `rescuedDataColumn` is enabled." |
| `rescuedDataColumn` | None | Spaltenname | „Whether to collect all data that can't be parsed due to data type or schema mismatch." |
| `sep` / `delimiter` | `,` | String | „The separator string between columns." |
| `singleVariantColumn` | None | Spaltenname | „When set to a column name, reads the entire CSV record into a single `VariantType` column." |
| `skipRows` | `0` | Ganzzahl | „The number of rows from the beginning of the CSV file that should be ignored." |
| `timeFormat` | `HH:mm:ss` | Zeitformat | „The format for parsing `TimeType` column values." |
| `timestampFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]` | Timestamp-Format | „The format for parsing timestamp strings." |
| `timestampNTZFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS]` | Timestamp-Format | „The format for parsing timestamp without timezone (`TimestampNTZType`) strings." |
| `timeZone` | None | ZoneId-String | „The `java.time.ZoneId` to use when parsing timestamps and dates." |
| `unescapedQuoteHandling` | `STOP_AT_DELIMITER` | enum | „The strategy for handling unescaped quotes." |

## Beispiel

```python
df = (spark.read.format("csv")
  .option("header", "true")
  .option("sep", "|")
  .option("rescuedDataColumn", "_rescued_data")
  .load("/Volumes/analytics/bronze/csv_data"))
```

## Siehe auch

- [`../04 Dateitypen/01 Ingesting CSV.md`](../04%20Dateitypen/01%20Ingesting%20CSV.md)
