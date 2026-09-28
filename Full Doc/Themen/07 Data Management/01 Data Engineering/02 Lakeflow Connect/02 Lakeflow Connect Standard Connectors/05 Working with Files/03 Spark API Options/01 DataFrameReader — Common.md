# DataFrameReader options — Common

Bereich: **DataFrameReader options › Common** — Optionen, die für alle bzw. die meisten Dateiformate beim Batch-Lesen (`spark.read`, `read_files`, `COPY INTO`) gelten.

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `ignoreCorruptFiles` | `false` | boolean | „Whether to ignore corrupt files. If true, the Spark jobs will continue to run when encountering corrupted files" (ab Databricks Runtime 11.3 LTS). |
| `ignoredPathSegmentRegex` | `^[._]` | Regex-String | „Controls which files and directories are skipped as hidden during file listing" (ab Databricks Runtime 19). |
| `ignoreMissingFiles` | `false` (Auto Loader); `true` (COPY INTO, Legacy) | boolean | „Whether to ignore missing files. If true, the Spark jobs continue to run when encountering missing files" (ab Databricks Runtime 11.3 LTS). |
| `modifiedAfter` | None | Timestamp | „An optional timestamp as a filter to only ingest files that have a modification timestamp after the specified timestamp." |
| `modifiedBefore` | None | Timestamp | „An optional timestamp as a filter to only ingest files that have a modification timestamp before the specified timestamp." |
| `pathGlobFilter` / `fileNamePattern` | None | Glob-Muster | „A potential glob pattern for choosing files." |
| `recursiveFileLookup` | `false` | boolean | „When `true`, this option searches through nested directories even if their names do not follow a partition naming scheme." |

## Beispiel

```python
df = (spark.read.format("json")
  .option("pathGlobFilter", "*.json")
  .option("modifiedAfter", "2026-01-01T00:00:00")
  .load("/Volumes/analytics/bronze/events"))
```
