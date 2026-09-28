# DataFrameReader options — XML

Bereich: **DataFrameReader options › XML** (Batch-Lesen von XML-Dateien).

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `rowTag` | None (erforderlich) | String | „The row tag of the XML files to treat as a row." |
| `samplingRatio` | `1.0` | float | „Defines a fraction of rows used for schema inference." |
| `excludeAttribute` | `false` | boolean | „Whether to exclude attributes in elements." |
| `mode` | None | enum | „Mode for dealing with corrupt records during parsing." |
| `inferSchema` | `true` | boolean | „If `true`, attempts to infer an appropriate type for each resulting DataFrame column." |
| `columnNameOfCorruptRecord` | `spark.sql.columnNameOfCorruptRecord` | Spaltenname | „Allows renaming the new field that contains a malformed string." |
| `attributePrefix` | None | String | „The prefix for attributes to differentiate attributes from elements." |
| `valueTag` | `_VALUE` | String | „The tag used for the character data within elements." |
| `encoding` | `UTF-8` | Charset-Name | „For reading, decodes the XML files by the given encoding type." |
| `ignoreSurroundingSpaces` | `true` | boolean | „Whether white spaces surrounding values must be skipped." |
| `rowValidationXSDPath` | None | Dateipfad | „Path to an optional XSD file for validating XML for each row." |
| `ignoreNamespace` | `false` | boolean | „If `true`, namespaces' prefixes on XML elements and attributes are ignored." |
| `timestampFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]` | Timestamp-Format | „Custom timestamp format string." |
| `timestampNTZFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS]` | Timestamp-Format | „Custom format string for timestamp without timezone." |
| `dateFormat` | `yyyy-MM-dd` | Datumsformat | „Custom date format string." |
| `locale` | `en-US` | BCP-47-Tag | „Sets a locale as a language tag in IETF BCP 47 format." |
| `nullValue` | String `null` | String | „Sets the string representation of a null value." |
| `readerCaseSensitive` | `true` | boolean | „Specifies the case sensitivity behavior when `rescuedDataColumn` is enabled." |
| `rescuedDataColumn` | None | Spaltenname | „Whether to collect all data that can't be parsed due to data type or schema mismatch." |
| `singleVariantColumn` | `none` | Spaltenname | „Specifies the name of the single variant column." |
| `useLegacyXMLParser` | `true` | boolean | „Whether to use the legacy XML parser." |
| `wildcardColName` | `xs_any` | Spaltenname | „The column name used to capture XML elements that match the wildcard schema element." |

## Beispiel

```python
df = (spark.read.format("xml")
  .option("rowTag", "book")
  .option("rescuedDataColumn", "_rescued_data")
  .load("/Volumes/analytics/bronze/books.xml"))
```

## Siehe auch

- [`../04 Dateitypen/05 Ingesting XML.md`](../04%20Dateitypen/05%20Ingesting%20XML.md)
