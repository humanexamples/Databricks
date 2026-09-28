# cloudFiles.privateKeyId

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, GCS) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String |
| **`read_files`-Parameter** | `privateKeyId` |

## Beschreibung

Private-Key-ID des Google-Service-Accounts. Teil der GCS-Service-Account-Zugangsdaten (siehe [cloudFiles.client](cloudFiles.client.md)).

*(Beschreibung sinngemäß nach der Spark API options reference; GCS-Tabelle beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.privateKeyId", "<private-key-id>")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
