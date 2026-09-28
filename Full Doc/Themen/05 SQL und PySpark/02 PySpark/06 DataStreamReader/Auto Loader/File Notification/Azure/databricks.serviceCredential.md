# `databricks.serviceCredential`

Name eines Unity-Catalog-Service-Credentials. Hinweis: Kein `cloudFiles.*`-Präfix, wird aber zusammen mit Auto Loader verwendet.

## Beschreibung

> *"The name of your Databricks service credential."*

Die empfohlene Authentifizierungsmethode für den klassischen File-Notification-Modus auf Azure (ab Databricks Runtime 16.1) und für den Cloud Resource Manager. Ersetzt die direkte Angabe von Access Keys, Client Secrets oder Private Keys durch ein zentral verwaltetes Unity-Catalog-Service-Credential.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("databricks.serviceCredential", "my-service-credential")
      .load("abfss://container@storageaccount.dfs.core.windows.net/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
