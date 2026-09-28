# `cloudFiles.awsAccessKey`

AWS Access Key ID für die Authentifizierung gegenüber SNS/SQS.

## Beschreibung

AWS Access Key ID, mit der sich Auto Loader im klassischen File-Notification-Modus gegenüber SNS/SQS authentifiziert. Wird zusammen mit [`cloudFiles.awsSecretKey`](cloudFiles.awsSecretKey.md) verwendet. Alternativen dazu sind das Instance Profile der Compute-Ressource oder eine über [`cloudFiles.roleArn`](cloudFiles.roleArn.md) übernommene IAM-Rolle. Databricks empfiehlt, solche Zugangsdaten über Databricks-Secrets zu referenzieren, statt sie im Klartext im Code anzugeben.

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
