# `cloudFiles.roleArn`

ARN einer per `AssumeRole` zu übernehmenden IAM-Rolle.

## Beschreibung

Amazon Resource Name (ARN) einer IAM-Rolle, die Auto Loader für den Zugriff auf SNS/SQS (und ggf. S3) per `AssumeRole` übernimmt — typischerweise für Cross-Account-Ingestion, bei der Bucket und Databricks-Workspace in unterschiedlichen AWS-Konten liegen. Optional kombinierbar mit [`cloudFiles.roleExternalId`](cloudFiles.roleExternalId.md), [`cloudFiles.roleSessionName`](cloudFiles.roleSessionName.md) und [`cloudFiles.stsEndpoint`](cloudFiles.stsEndpoint.md).

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.roleArn", "arn:aws:iam::123456789012:role/AutoLoaderRole")
      .option("cloudFiles.roleExternalId", "databricks")
      .load("s3://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
