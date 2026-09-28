# DataStreamReader options — Common

Bereich: **DataStreamReader options › Common** — Optionen der dateibasierten Streaming-Quelle (`spark.readStream.format("<file-format>")`), unabhängig von Auto Loader.

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `cleanSource` | `off` | enum (`off`, `archive`, `delete`) | „How to handle source files after they are processed by the stream." |
| `fileNameOnly` | `false` | boolean | „Whether to identify already-processed files by filename only rather than by full path." |
| `latestFirst` | `false` | boolean | „Whether to process the most recently modified files first within each micro-batch." |
| `maxBytesPerTrigger` | None | Ganzzahl | „Soft maximum for the amount of data processed for each micro-batch." |
| `maxCachedFiles` | `10000` | Ganzzahl | „Maximum number of unprocessed files to cache for subsequent micro-batches." |
| `maxFileAge` | `7d` | Dauer | „Maximum age of files considered for processing." |
| `maxFilesPerTrigger` | `1000` (Delta / Auto Loader); kein Maximum (andere Quellen) | Ganzzahl | „Upper bound for the number of new files processed in each micro-batch." |
| `sourceArchiveDir` | None | Pfad | „Path to the archive directory when `cleanSource` is set to `archive`." |

> Für die **Auto-Loader**-Quelle (`format("cloudFiles")`) gelten stattdessen die `cloudFiles.*`-Optionen — siehe [22 DataStreamReader — Auto Loader.md](22%20DataStreamReader%20%E2%80%94%20Auto%20Loader.md). Das dateibasierte `cleanSource`/`sourceArchiveDir` hier ist **nicht** dasselbe wie `cloudFiles.cleanSource`.

## Beispiel

```python
df = (spark.readStream.format("json")
  .schema(schema)
  .option("maxFilesPerTrigger", 100)
  .option("latestFirst", "true")
  .load("/Volumes/analytics/bronze/events"))
```
