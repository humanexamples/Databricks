# `cloudFiles.useIncrementalListing` *(veraltet)*

Schaltet zwischen inkrementeller und vollständiger Verzeichnisauflistung um.

## Beschreibung

> *"This feature has been deprecated. Databricks recommends using file notification mode with file events instead of `cloudFiles.useIncrementalListing`. Whether to use the incremental listing rather than the full listing in directory listing mode. By default, Auto Loader makes the best effort to automatically detect if a given directory is applicable for the incremental listing. […] Incorrectly enabling incremental listing on a non-lexically ordered directory prevents Auto Loader from discovering new files. Works with Azure Data Lake Storage (`abfss://`), S3 (`s3://`), and GCS (`gs://`)."*

Die Option ist offiziell als veraltet markiert — Databricks empfiehlt stattdessen den File-Notification-Modus mit File Events. Der Standardwert ist `auto` bis Databricks Runtime 17.2 (Auto Loader erkennt dann selbst, ob ein Verzeichnis für die inkrementelle Auflistung geeignet ist) und `false` ab Databricks Runtime 17.3. Bei `auto` löst Auto Loader nach 7 aufeinanderfolgenden inkrementellen Auflistungen automatisch wieder eine vollständige Auflistung aus. Wird die Option fälschlich auf einem nicht lexikalisch geordneten Verzeichnis aktiviert, kann Auto Loader neue Dateien übersehen.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useIncrementalListing", "auto")
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
