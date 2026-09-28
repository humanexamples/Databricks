# `cloudFiles.roleSessionName`

Session-Name beim `AssumeRole` mit `cloudFiles.roleArn`.

## Beschreibung

Frei wählbarer Session-Name, der bei der `AssumeRole`-Operation mit [`cloudFiles.roleArn`](cloudFiles.roleArn.md) verwendet wird. Er erscheint in den AWS-CloudTrail-Logs und erleichtert dort die Nachverfolgung, welcher Auto-Loader-Stream welche Aktion ausgelöst hat.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.roleArn", "arn:aws:iam::123456789012:role/AutoLoaderRole")
      .option("cloudFiles.roleSessionName", "autoloader-bronze-events")
      .load("s3://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
