# `cloudFiles.clientSecret`

Client Secret des Service Principals.

## Beschreibung

> *"The client secret of the service principal."*

Vervollständigt die Service-Principal-Authentifizierung zusammen mit [`cloudFiles.tenantId`](cloudFiles.tenantId.md) und [`cloudFiles.clientId`](cloudFiles.clientId.md). Sollte über Databricks-Secrets referenziert werden statt im Klartext im Code zu stehen.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.tenantId", "<tenant-id>")
      .option("cloudFiles.clientId", "<client-id>")
      .option("cloudFiles.clientSecret", dbutils.secrets.get("scope", "sp-secret"))
      .load("abfss://container@storageaccount.dfs.core.windows.net/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
