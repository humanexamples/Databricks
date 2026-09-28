# `cloudFiles.clientId`

Client-/Application-ID des Service Principals.

## Beschreibung

> *"The client ID or application ID of the service principal."*

Teil der Service-Principal-Authentifizierung, zusammen mit [`cloudFiles.tenantId`](cloudFiles.tenantId.md) und [`cloudFiles.clientSecret`](cloudFiles.clientSecret.md).

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.clientId", "<client-id>")
      .load("abfss://container@storageaccount.dfs.core.windows.net/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
