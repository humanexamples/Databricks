# cloudFiles.client

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, GCS) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String |
| **`read_files`-Parameter** | `client` |

## Beschreibung

Client-ID des Google-Service-Accounts, mit dem Auto Loader auf Pub/Sub (und GCS) zugreift. Teil der GCS-Service-Account-Zugangsdaten zusammen mit [cloudFiles.clientEmail](cloudFiles.clientEmail.md), [cloudFiles.privateKey](cloudFiles.privateKey.md) und [cloudFiles.privateKeyId](cloudFiles.privateKeyId.md).

*(Beschreibung sinngemäß nach der Spark API options reference; GCS-Tabelle beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.client", "<service-account-client-id>")
.option("cloudFiles.clientEmail", "<sa>@<project>.iam.gserviceaccount.com")
.option("cloudFiles.privateKey", dbutils.secrets.get("scope", "gcs-private-key"))
.option("cloudFiles.privateKeyId", "<private-key-id>")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
