# cloudFiles.privateKey

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, GCS) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String (PEM-Private-Key) |
| **`read_files`-Parameter** | `privateKey` |

## Beschreibung

Private Key des Google-Service-Accounts. Über Databricks-Secrets referenzieren, nicht im Klartext angeben. Teil der GCS-Service-Account-Zugangsdaten (siehe [cloudFiles.client](cloudFiles.client.md)).

*(Beschreibung sinngemäß nach der Spark API options reference; GCS-Tabelle beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.privateKey", dbutils.secrets.get("scope", "gcs-private-key"))
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
