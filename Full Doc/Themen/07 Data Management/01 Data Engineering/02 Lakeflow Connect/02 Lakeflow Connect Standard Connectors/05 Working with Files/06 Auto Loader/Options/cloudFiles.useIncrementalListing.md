# cloudFiles.useIncrementalListing  *(veraltet)*

| | |
|---|---|
| **Kategorie** | Directory Listing Mode option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `auto` (Databricks Runtime 17.2 und darunter); `false` (Databricks Runtime 17.3 und höher) |
| **Gültige Werte** | `auto`, `true`, `false` |
| **`read_files`-Parameter** | `useIncrementalListing` |
| **Seit** | Databricks Runtime 9.1 LTS und höher |

## Beschreibung

> „This feature has been deprecated. Databricks recommends using file notification mode with file events instead of `cloudFiles.useIncrementalListing`. Whether to use the incremental listing rather than the full listing in directory listing mode. By default, Auto Loader makes the best effort to automatically detect if a given directory is applicable for the incremental listing. […] Incorrectly enabling incremental listing on a non-lexically ordered directory prevents Auto Loader from discovering new files. Works with Azure Data Lake Storage (`abfss://`), S3 (`s3://`), and GCS (`gs://`)."

Bei `auto` löst Auto Loader nach 7 aufeinanderfolgenden inkrementellen Auflistungen automatisch eine vollständige Auflistung aus.

## Beispiel

```python
.option("cloudFiles.useIncrementalListing", "auto")
```

## Siehe auch

- [../05 Directory Listing Mode.md](../05%20Directory%20Listing%20Mode.md)
- [cloudFiles.useManagedFileEvents.md](cloudFiles.useManagedFileEvents.md)
