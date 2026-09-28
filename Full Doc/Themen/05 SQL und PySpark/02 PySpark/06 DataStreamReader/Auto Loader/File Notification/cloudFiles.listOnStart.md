# `cloudFiles.listOnStart`

Erzwingt eine vollständige Verzeichnisauflistung beim Stream-Start.

## Beschreibung

> *"When set to `true`, Auto Loader performs a full directory listing when the stream starts, instead of starting with the continuation token in the checkpoint. Use this option to recover from errors, such as `CF_MANAGED_FILE_EVENTS_INVALID_CONTINUATION_TOKEN`."*

Standardwert ist `false`. Bei `true` ignoriert Auto Loader beim Start den im Checkpoint gespeicherten Fortsetzungspunkt (continuation token) und listet das Quellverzeichnis stattdessen komplett neu auf. Gedacht als Recovery-Mechanismus bei bestimmten Fehlern im File-Events-Modus, nicht als Dauerkonfiguration.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.listOnStart", "true")
      .option("cloudFiles.validateOptions", False)
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
