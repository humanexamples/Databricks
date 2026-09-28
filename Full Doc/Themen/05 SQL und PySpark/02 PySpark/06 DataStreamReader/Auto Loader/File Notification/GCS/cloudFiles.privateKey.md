# `cloudFiles.privateKey`

Private Key des Google-Service-Accounts.

## Beschreibung

Private Key (im PEM-Format) des Google-Service-Accounts. Teil der GCS-Service-Account-Zugangsdaten (siehe [`cloudFiles.client`](cloudFiles.client.md)). Sollte über Databricks-Secrets referenziert werden statt im Klartext im Code zu stehen.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.privateKey", dbutils.secrets.get("scope", "gcs-private-key"))
      .load("gs://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
