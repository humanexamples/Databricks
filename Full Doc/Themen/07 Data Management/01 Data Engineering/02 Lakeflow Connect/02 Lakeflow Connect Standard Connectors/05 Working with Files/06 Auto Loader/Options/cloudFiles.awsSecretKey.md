# cloudFiles.awsSecretKey

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, AWS S3) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None (sonst Instance-Profile/Cluster-Rolle) |
| **Datentyp** | String |
| **`read_files`-Parameter** | `awsSecretKey` |

## Beschreibung

AWS Secret Access Key, passend zu [cloudFiles.awsAccessKey](cloudFiles.awsAccessKey.md). Über Databricks-Secrets referenzieren, nicht im Klartext angeben.

*(Beschreibung sinngemäß nach der Spark API options reference; AWS-Tabelle beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.awsSecretKey", dbutils.secrets.get("scope", "aws-secret-key"))
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
