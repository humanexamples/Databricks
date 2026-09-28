# cloudFiles.resourceGroup

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, Azure ADLS/Blob) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String |
| **`read_files`-Parameter** | `resourceGroup` |

## Beschreibung

> „The Azure Resource Group in which the storage account is created."

Erforderlich, wenn Auto Loader die Benachrichtigungsdienste (Event Grid + Queue Storage) selbst einrichten soll (`cloudFiles.useNotifications = true`).

## Beispiel

```python
.option("cloudFiles.useNotifications", "true")
.option("cloudFiles.resourceGroup", "my-rg")
.option("cloudFiles.subscriptionId", "00000000-0000-0000-0000-000000000000")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
- [databricks.serviceCredential.md](databricks.serviceCredential.md)
