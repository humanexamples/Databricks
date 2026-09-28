# `cloudFiles.queueUrl`

URL einer bereits bestehenden SQS-Queue.

## Beschreibung

URL einer **bereits bestehenden** SQS-Queue. Ist sie angegeben, konsumiert Auto Loader Ereignisse direkt aus dieser Queue, statt eigene SNS-/SQS-Ressourcen anzulegen — die verwendeten Zugangsdaten benötigen dann nur Lese- und Löschrechte auf der Queue. Empfängt die Queue Benachrichtigungen aus mehreren Buckets und sollen dabei Mount-Points verwendet werden, ist zusätzlich [`cloudFiles.pathRewrites`](../cloudFiles.pathRewrites.md) nötig.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.queueUrl", "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue")
      .load("s3://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options
- File notification mode: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-notification-mode

**Stand:** 2026-09-15
