# `cloudFiles.client`

Client-ID des Google-Service-Accounts.

## Beschreibung

Client-ID des Google-Service-Accounts, mit dem Auto Loader im klassischen File-Notification-Modus auf Pub/Sub (und GCS) zugreift. Teil der GCS-Service-Account-Zugangsdaten, zusammen mit [`cloudFiles.clientEmail`](cloudFiles.clientEmail.md), [`cloudFiles.privateKey`](cloudFiles.privateKey.md) und [`cloudFiles.privateKeyId`](cloudFiles.privateKeyId.md).

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.client", "<service-account-client-id>")
      .option("cloudFiles.clientEmail", "<sa>@<project>.iam.gserviceaccount.com")
      .option("cloudFiles.privateKey", dbutils.secrets.get("scope", "gcs-private-key"))
      .option("cloudFiles.privateKeyId", "<private-key-id>")
      .load("gs://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
