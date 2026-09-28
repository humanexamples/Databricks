# `cloudFiles.fetchParallelism`

Anzahl paralleler Threads beim Abrufen aus der Notification-Queue.

## Beschreibung

> *"Number of threads to use when fetching messages from the queueing service. Do not use when `cloudFiles.useManagedFileEvents` is set to `true`."*

Standardwert ist `1`. Gilt nur für den klassischen File-Notification-Modus (`cloudFiles.useNotifications = true`) und darf nicht zusammen mit dem File-Events-Modus (`cloudFiles.useManagedFileEvents = true`) verwendet werden.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.fetchParallelism", 4)
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
