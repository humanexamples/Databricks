# `cloudFiles.connectionString`

Connection String des Storage Accounts.

## Beschreibung

> *"The connection string for the storage account, based on either account access key or shared access signature (SAS)."*

Authentifizierungsalternative zum Databricks-Service-Credential bzw. zur Service-Principal-Authentifizierung, basierend entweder auf einem Account Access Key oder einer Shared Access Signature (SAS). Sollte über Databricks-Secrets referenziert werden statt im Klartext im Code zu stehen.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.connectionString", dbutils.secrets.get("scope", "adls-conn-str"))
      .load("abfss://container@storageaccount.dfs.core.windows.net/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
