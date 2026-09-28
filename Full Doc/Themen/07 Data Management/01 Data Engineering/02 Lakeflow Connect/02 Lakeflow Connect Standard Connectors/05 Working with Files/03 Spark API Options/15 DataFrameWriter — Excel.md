# DataFrameWriter options — Excel

Bereich: **DataFrameWriter options › Excel** (Batch-Schreiben von Excel-Arbeitsmappen).

Quelle: [Spark API options reference](https://learn.microsoft.com/en-us/azure/databricks/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `dataAddress` | None | Blattname oder Zellreferenz-String | „The sheet name or starting cell for the write. If omitted, writes to a sheet named `Sheet1` starting at cell `A1`. Accepts a sheet name (`SheetName`) or a single cell reference (`SheetName!A1`). Cell ranges are not supported for writes." |
| `dateFormatInWrite` | `yyyy-mm-dd` | Excel-Datumsformat-String | „Excel cell format string applied to `Date` columns. Uses Excel format syntax." |
| `headerRows` | `0` | `0`, `1` | „Whether to write column names as the first row." |
| `timestampNTZFormat` | `yyyy-mm-dd hh:mm:ss` | Excel-Timestamp-Format-String | „Excel cell format string applied to `TimestampNTZ` and `Timestamp` columns. Uses Excel format syntax." |
| `version` | `xlsx` | `xlsx`, `xls` | „The Excel file format version to write." |

## Beispiel

```python
(df.write.format("com.crealytics.spark.excel")
  .option("dataAddress", "'Report'!A1")
  .option("headerRows", 1)
  .save("/Volumes/analytics/silver/report.xlsx"))
```
