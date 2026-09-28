# DataFrameReader options — Excel

Bereich: **DataFrameReader options › Excel** (Batch-Lesen von Excel-Arbeitsmappen).

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `dataAddress` | None | Zellbereich / Blattname | „The cell range to read in Excel syntax." |
| `headerRows` | `0` | enum | „Number of initial rows to use as column name headers." |
| `ignoreMissingSheet` | `false` | boolean | „Whether to silently skip files that do not contain the sheet specified by `dataAddress`." |
| `includePhoneticRuns` | `false` | boolean | „Whether to include phonetic annotations concatenated to cell string values when reading XLSX files." |
| `operation` | `readSheet` | enum | „The operation to perform on the Excel workbook." |
| `timestampNTZFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS]` | Timestamp-Format | „Custom format string for timestamp-without-timezone values stored as strings in Excel." |
| `dateFormat` | `yyyy-MM-dd` | Datumsformat | „Custom format string for string values read as `Date`." |

## Beispiel

```python
df = (spark.read.format("com.crealytics.spark.excel")
  .option("dataAddress", "'Sheet1'!A1")
  .option("headerRows", 1)
  .load("/Volumes/analytics/bronze/report.xlsx"))
```

## Siehe auch

- [`../04 Dateitypen/04 Ingesting Excel.md`](../04%20Dateitypen/04%20Ingesting%20Excel.md)
