# `cloudFiles.region`

AWS-Region des Quell-Buckets.

## Beschreibung

Die AWS-Region, in der der Quell-S3-Bucket liegt und in der Auto Loader die SNS- und SQS-Dienste anlegt. Standardmäßig wird die Region der EC2-Instanz verwendet, ansonsten muss sie angegeben werden. Nur im klassischen File-Notification-Modus relevant (`cloudFiles.useNotifications = true`), wenn Auto Loader die Benachrichtigungsdienste selbst einrichten soll — nicht relevant beim neueren File-Events-Modus.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.region", "us-east-1")
      .load("s3://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options
- File notification mode: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-notification-mode

**Stand:** 2026-09-15
