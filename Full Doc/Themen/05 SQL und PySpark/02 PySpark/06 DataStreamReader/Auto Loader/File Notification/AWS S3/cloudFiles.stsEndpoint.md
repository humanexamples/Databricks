# `cloudFiles.stsEndpoint`

Benutzerdefinierter AWS-STS-Endpunkt für `AssumeRole`.

## Beschreibung

Erlaubt, einen alternativen AWS-STS-Endpunkt für die `AssumeRole`-Operation anzugeben — etwa einen regionalen STS-Endpunkt oder einen VPC-Endpunkt, statt des globalen Standard-Endpunkts. Wird zusammen mit [`cloudFiles.roleArn`](cloudFiles.roleArn.md) verwendet. Ohne diese Option nutzt Auto Loader den globalen STS-Endpunkt.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.roleArn", "arn:aws:iam::123456789012:role/AutoLoaderRole")
      .option("cloudFiles.stsEndpoint", "https://sts.us-east-1.amazonaws.com")
      .load("s3://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
