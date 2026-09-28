# DataFrameReader options — JSON

Bereich: **DataFrameReader options › JSON** (Batch-Lesen von JSON-Dateien).

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `allowBackslashEscapingAnyCharacter` | `false` | boolean | „Whether to allow backslashes to escape any character that succeeds it." |
| `allowComments` | `false` | boolean | „Whether to allow the use of Java, C, and C++ style comments within parsed content." |
| `allowNonNumericNumbers` | `true` | boolean | „Whether to allow the set of not-a-number (`NaN`) tokens as legal floating number values." |
| `allowNumericLeadingZeros` | `false` | boolean | „Whether to allow integral numbers to start with additional (ignorable) zeroes." |
| `allowSingleQuotes` | `true` | boolean | „Whether to allow use of single quotes (apostrophe, character `'`)." |
| `allowUnquotedControlChars` | `false` | boolean | „Whether to allow JSON strings to contain unescaped control characters." |
| `allowUnquotedFieldNames` | `false` | boolean | „Whether to allow use of unquoted field names." |
| `alternateVariantEncoding` | None | enum | „The encoding used for Variant values in the source JSON." |
| `badRecordsPath` | None | Pfad-String | „The path to store files for recording the information about bad JSON records." |
| `columnNameOfCorruptRecord` | `_corrupt_record` | Spaltenname | „The column for storing records that are malformed and cannot be parsed." |
| `dateFormat` | `yyyy-MM-dd` | Datumsformat | „The format for parsing date strings." |
| `dropFieldIfAllNull` | `false` | boolean | „Whether to ignore columns of all null values or empty arrays and structs during schema inference." |
| `encoding` / `charset` | `UTF-8` | Charset-Name | „The name of the encoding of the JSON files." |
| `inferTimestamp` | `false` | boolean | „Whether to try and infer timestamp strings as a `TimestampType`." |
| `lineSep` | None | String | „A string between two consecutive JSON records." |
| `locale` | `US` | Locale-Identifier | „A Java locale identifier that affects default date, timestamp, and decimal parsing." |
| `maxNestingDepth` | `500` | Ganzzahl | „The maximum allowed nesting depth for JSON objects and arrays." |
| `maxNumLen` | `1000` | Ganzzahl | „The maximum length of number tokens in the JSON input." |
| `maxStringLen` | unbegrenzt | Ganzzahl | „The maximum length of string values in the JSON input." |
| `mode` | `PERMISSIVE` | enum | „Parser mode around handling malformed records." |
| `multiLine` | `false` | boolean | „Whether the JSON records span multiple lines." |
| `prefersDecimal` | `false` | boolean | „Attempts to infer strings as `DecimalType` instead of float or double type when possible." |
| `primitivesAsString` | `false` | boolean | „Whether to infer primitive types like numbers and booleans as `StringType`." |
| `readerCaseSensitive` | `true` | boolean | „Specifies the case sensitivity behavior when `rescuedDataColumn` is enabled" (ab Databricks Runtime 13.3). |
| `rescuedDataColumn` | None | Spaltenname | „Whether to collect all data that can't be parsed due to data type or schema mismatch." |
| `singleVariantColumn` | None | Spaltenname | „When set to a column name, ingests the entire JSON record as a single VARIANT column." |
| `timestampFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]` | Timestamp-Format | „The format for parsing timestamp strings." |
| `timestampNTZFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS]` | Timestamp-Format | „The format for parsing timestamp without timezone (`TimestampNTZType`) strings." |
| `timeZone` | None | ZoneId-String | „The `java.time.ZoneId` to use when parsing timestamps and dates." |
| `upgradeExceptionAsBadRecord` | `false` | boolean | „Whether to treat type upgrade exceptions as bad records rather than throwing an exception." |

## Beispiel

```python
df = (spark.read.format("json")
  .option("multiLine", "true")
  .option("rescuedDataColumn", "_rescued_data")
  .load("/Volumes/analytics/bronze/json_data"))
```

## Siehe auch

- [`../04 Dateitypen/02 Ingesting JSON.md`](../04%20Dateitypen/02%20Ingesting%20JSON.md)
