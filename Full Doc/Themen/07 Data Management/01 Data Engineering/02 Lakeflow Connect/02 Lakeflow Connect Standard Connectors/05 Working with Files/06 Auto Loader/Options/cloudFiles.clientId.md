# cloudFiles.clientId

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, Azure ADLS/Blob) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String |
| **`read_files`-Parameter** | `clientId` |

## Beschreibung

> „The client ID or application ID of the service principal."

Authentifizierungsalternative über Service Principal (mit [cloudFiles.tenantId](cloudFiles.tenantId.md) und [cloudFiles.clientSecret](cloudFiles.clientSecret.md)).

## Beispiel

```python
.option("cloudFiles.clientId", "<client-id>")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
