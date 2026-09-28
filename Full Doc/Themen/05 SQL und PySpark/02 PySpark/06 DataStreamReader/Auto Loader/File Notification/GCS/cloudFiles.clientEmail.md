# `cloudFiles.clientEmail`

E-Mail-Adresse des Google-Service-Accounts.

## Beschreibung

E-Mail-Adresse des Google-Service-Accounts, mit dem Auto Loader im klassischen File-Notification-Modus authentifiziert. Teil der GCS-Service-Account-Zugangsdaten (siehe [`cloudFiles.client`](cloudFiles.client.md)).

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.clientEmail", "<sa>@<project>.iam.gserviceaccount.com")
      .load("gs://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
