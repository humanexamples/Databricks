# `cloudFiles.queueName`

Name einer bereits bestehenden Azure-Queue.

## Beschreibung

> *"The name of the Azure queue. If specified, the cloud files source directly consumes events from this queue instead of setting up its own Azure Event Grid and Queue Storage services. In that case, your `databricks.serviceCredential` or `cloudFiles.connectionString` requires only read permissions on the queue."*

Azure-Gegenstück zu `cloudFiles.queueUrl` (AWS) bzw. `cloudFiles.subscription` (GCS). Ist der Name angegeben, konsumiert Auto Loader Ereignisse direkt aus dieser bestehenden Queue, statt eigene Event-Grid- und Queue-Storage-Ressourcen einzurichten — die verwendeten Zugangsdaten benötigen dann nur Leserechte auf der Queue.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.queueName", "my-existing-queue")
      .load("abfss://container@storageaccount.dfs.core.windows.net/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
