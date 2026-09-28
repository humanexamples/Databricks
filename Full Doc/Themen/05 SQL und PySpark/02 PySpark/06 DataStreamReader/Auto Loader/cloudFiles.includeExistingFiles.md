# `cloudFiles.includeExistingFiles`

Steuert, ob beim Erststart bereits vorhandene Dateien mitverarbeitet werden.

## Beschreibung

> *"Whether to include existing files in the stream processing input path or to only process new files arriving after initial setup. This option is evaluated only when you start a stream for the first time. Changing this option after restarting the stream has no effect."*

Bei `true` (Standard) verarbeitet der Stream beim ersten Start auch bereits im Quellverzeichnis liegende Dateien. Bei `false` werden nur Dateien verarbeitet, die **nach** dem Start neu hinzukommen. Die Option wird ausschließlich beim allerersten Start mit frischem Checkpoint ausgewertet — ein späteres Ändern hat keine Wirkung mehr. Wichtig: Selbst bei `false` führt Auto Loader beim Erststart trotzdem eine Verzeichnisauflistung durch, um danach neu erstellte Dateien erkennen zu können — eine anfängliche Auflistung lässt sich also nicht vollständig vermeiden.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.includeExistingFiles", False)
      .load("/Volumes/analytics/bronze/events"))
```

```sql
CREATE OR REFRESH STREAMING TABLE events_new_only
AS SELECT * FROM STREAM read_files('/Volumes/analytics/bronze/events',
  format => 'json', includeExistingFiles => false);
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
