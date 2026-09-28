# `cloudFiles.backfillInterval`

Löst asynchrone Backfills in festem Intervall aus.

## Beschreibung

> *"Auto Loader can trigger asynchronous backfills at a given interval. […] Do not use when `cloudFiles.useManagedFileEvents` is set to `true`."*

Löst in festem Intervall eine vollständige Verzeichnisauflistung aus, um sicherzustellen, dass keine Dateien übersehen wurden — z. B. weil eine File-Notification verloren ging. Regelmäßige Backfills auf diese Weise erzeugen dabei keine doppelten Datensätze. Die Option stammt aus dem klassischen File-Notification-Modus; beim neueren File-Events-Modus (`cloudFiles.useManagedFileEvents = true`) werden Backfills automatisch gehandhabt, und die Option darf dort nicht gesetzt werden.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.backfillInterval", "1 week")
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
