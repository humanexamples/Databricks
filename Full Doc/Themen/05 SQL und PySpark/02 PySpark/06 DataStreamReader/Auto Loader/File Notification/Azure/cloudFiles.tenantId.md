# `cloudFiles.tenantId`

Azure Tenant ID des Service Principals.

## Beschreibung

> *"The Azure Tenant ID in which the service principal is created."*

Teil einer Authentifizierungsalternative über einen Microsoft-Entra-ID-Service-Principal, falls kein Databricks-Service-Credential (`databricks.serviceCredential`) verwendet wird. Wird zusammen mit [`cloudFiles.clientId`](cloudFiles.clientId.md) und [`cloudFiles.clientSecret`](cloudFiles.clientSecret.md) verwendet.

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
