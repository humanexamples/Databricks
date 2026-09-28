# `cloudFiles.useNotifications`

Aktiviert den klassischen File-Notification-Modus.

## Beschreibung

> *"Whether to use file notification mode to determine when there are new files. If `false`, use directory listing mode. […] Do not use when `cloudFiles.useManagedFileEvents` is set to `true`."*

Standardwert ist `false` (dann arbeitet Auto Loader per Directory Listing). Bei `true` aktiviert die Option den klassischen File-Notification-Modus: Auto Loader richtet dann — mit den nötigen Berechtigungen — selbst Benachrichtigungs- und Queue-Dienste für den Stream ein, oder konsumiert stattdessen aus einer bereits bestehenden Queue (je nach Cloud über `cloudFiles.queueUrl`, `cloudFiles.queueName` oder `cloudFiles.subscription`). Für den neueren, empfohlenen File-Events-Modus wird stattdessen `cloudFiles.useManagedFileEvents = true` verwendet — beide Optionen dürfen nicht gleichzeitig gesetzt sein.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.region", "us-east-1")
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
