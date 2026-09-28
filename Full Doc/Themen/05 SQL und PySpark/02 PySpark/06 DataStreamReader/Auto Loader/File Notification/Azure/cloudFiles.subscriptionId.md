# `cloudFiles.subscriptionId`

Azure Subscription ID der Resource Group.

## Beschreibung

> *"The Azure Subscription ID in which the resource group is created."*

Erforderlich, wenn Auto Loader im klassischen File-Notification-Modus die Benachrichtigungsdienste selbst einrichten soll — zusammen mit [`cloudFiles.resourceGroup`](cloudFiles.resourceGroup.md).

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.subscriptionId", "00000000-0000-0000-0000-000000000000")
      .load("abfss://container@storageaccount.dfs.core.windows.net/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
