# `cloudFiles.awsSecretKey`

AWS Secret Access Key, passend zu `cloudFiles.awsAccessKey`.

## Beschreibung

AWS Secret Access Key, der zusammen mit [`cloudFiles.awsAccessKey`](cloudFiles.awsAccessKey.md) die Authentifizierung gegenüber SNS/SQS im klassischen File-Notification-Modus vervollständigt. Sollte über Databricks-Secrets referenziert werden statt im Klartext im Code zu stehen.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.awsAccessKey", dbutils.secrets.get("scope", "aws-access-key"))
      .option("cloudFiles.awsSecretKey", dbutils.secrets.get("scope", "aws-secret-key"))
      .load("s3://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
