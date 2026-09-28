# cloudFiles.clientEmail

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, GCS) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String (E-Mail) |
| **`read_files`-Parameter** | `clientEmail` |

## Beschreibung

E-Mail-Adresse des Google-Service-Accounts. Teil der GCS-Service-Account-Zugangsdaten (siehe [cloudFiles.client](cloudFiles.client.md)).

*(Beschreibung sinngemäß nach der Spark API options reference; GCS-Tabelle beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.clientEmail", "<sa>@<project>.iam.gserviceaccount.com")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
