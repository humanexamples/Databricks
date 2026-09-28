# cloudFiles.queueName

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, Azure ADLS/Blob) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String |
| **`read_files`-Parameter** | `queueName` |

## Beschreibung

> „The name of the Azure queue. If specified, the cloud files source directly consumes events from this queue instead of setting up its own Azure Event Grid and Queue Storage services. In that case, your `databricks.serviceCredential` or `cloudFiles.connectionString` requires only read permissions on the queue."

Azure-Gegenstück zu [cloudFiles.queueUrl](cloudFiles.queueUrl.md) (AWS) bzw. [cloudFiles.subscription](cloudFiles.subscription.md) (GCS).

## Beispiel

```python
.option("cloudFiles.useNotifications", "true")
.option("cloudFiles.queueName", "my-existing-queue")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
