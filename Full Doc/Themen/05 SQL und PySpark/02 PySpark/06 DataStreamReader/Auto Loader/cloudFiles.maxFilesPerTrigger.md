# `cloudFiles.maxFilesPerTrigger`

Harte Datei-Obergrenze pro Micro-Batch.

## Beschreibung

> *"The maximum number of new files to be processed in every trigger. When used together with `cloudFiles.maxBytesPerTrigger`, Azure Databricks consumes up to the lower limit of `cloudFiles.maxFilesPerTrigger` or `cloudFiles.maxBytesPerTrigger`, whichever is reached first. This option has no effect when used with `Trigger.Once()` (deprecated). In Databricks Runtime 18.0 and above, this option is dynamically configured and does not need to be set manually."*

Standardwert ist `1000` Dateien pro Micro-Batch. Wird zusammen mit `cloudFiles.maxBytesPerTrigger` verwendet, greift jeweils die niedrigere der beiden Grenzen zuerst. Ab Databricks Runtime 18.0 wird dieser Wert dynamisch verwaltet und muss in der Regel nicht mehr manuell gesetzt werden.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.maxFilesPerTrigger", 500)
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
