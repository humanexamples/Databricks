# `cloudFiles.privateKeyId`

Private-Key-ID des Google-Service-Accounts.

## Beschreibung

ID des Private Keys des Google-Service-Accounts. Teil der GCS-Service-Account-Zugangsdaten (siehe [`cloudFiles.client`](cloudFiles.client.md)).

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.privateKeyId", "<private-key-id>")
      .load("gs://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
