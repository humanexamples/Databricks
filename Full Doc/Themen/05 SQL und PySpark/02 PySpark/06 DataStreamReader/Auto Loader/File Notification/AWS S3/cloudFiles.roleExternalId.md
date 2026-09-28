# `cloudFiles.roleExternalId`

External ID beim `AssumeRole` mit `cloudFiles.roleArn`.

## Beschreibung

Wird zusammen mit [`cloudFiles.roleArn`](cloudFiles.roleArn.md) bei der `AssumeRole`-Operation mitgegeben und schützt dabei vor dem sogenannten "Confused Deputy"-Problem bei Cross-Account-Zugriff — also davor, dass die Rolle versehentlich von einem anderen, nicht autorisierten Konto übernommen wird.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.roleArn", "arn:aws:iam::123456789012:role/AutoLoaderRole")
      .option("cloudFiles.roleExternalId", "my-external-id")
      .load("s3://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
