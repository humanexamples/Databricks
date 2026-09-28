# `cloudFiles.maxBytesPerTrigger`

Weiche Byte-Obergrenze pro Micro-Batch.

## Beschreibung

> *"The maximum number of new bytes to be processed in every trigger. This is a soft maximum. If you have files that are 3 GB each, Azure Databricks processes 12 GB in a micro-batch. An individual file is never split across micro-batches; it is always processed in full within a single one, even when its size exceeds this limit. When used together with `cloudFiles.maxFilesPerTrigger`, Azure Databricks consumes up to the lower limit of `cloudFiles.maxFilesPerTrigger` or `cloudFiles.maxBytesPerTrigger`, whichever is reached first. This option has no effect when used with `Trigger.Once()` (`Trigger.Once()` is deprecated). In Databricks Runtime 18.0 and above, this option is dynamically configured and does not need to be set manually."*

Kein Standardwert. Anders als bei `maxFilesPerTrigger` ist dies eine **weiche** Grenze: Eine einzelne Datei wird nie über mehrere Micro-Batches aufgeteilt, sondern immer vollständig in einem Batch verarbeitet, selbst wenn sie dadurch das Limit überschreitet. Zusammen mit `cloudFiles.maxFilesPerTrigger` verwendet, greift jeweils die zuerst erreichte, niedrigere Grenze. Ab Databricks Runtime 18.0 dynamisch verwaltet.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.maxBytesPerTrigger", "10g")
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
