# cloudFiles.subscriptionId

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, Azure ADLS/Blob) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String |
| **`read_files`-Parameter** | `subscriptionId` |

## Beschreibung

> „The Azure Subscription ID in which the resource group is created."

Erforderlich, wenn Auto Loader die Benachrichtigungsdienste selbst einrichten soll.

## Beispiel

```python
.option("cloudFiles.subscriptionId", "00000000-0000-0000-0000-000000000000")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
