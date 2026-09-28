# `cloudFiles.subscription`

Name einer bereits bestehenden Google-Pub/Sub-Subscription.

## Beschreibung

Name einer bereits bestehenden Google-Pub/Sub-Subscription. Ist sie angegeben, konsumiert Auto Loader Ereignisse direkt daraus, statt eigene Pub/Sub-Ressourcen einzurichten. GCS-Gegenstück zu `cloudFiles.queueUrl` (AWS) bzw. `cloudFiles.queueName` (Azure).

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.subscription", "my-existing-subscription")
      .load("gs://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
