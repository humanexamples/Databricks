# cloudFiles.awsAccessKey

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, AWS S3) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None (sonst Instance-Profile/Cluster-Rolle) |
| **Datentyp** | String |
| **`read_files`-Parameter** | `awsAccessKey` |

## Beschreibung

AWS Access Key ID für die Authentifizierung gegenüber SNS/SQS im klassischen File-Notification-Modus. Zusammen mit [cloudFiles.awsSecretKey](cloudFiles.awsSecretKey.md) zu verwenden. Alternativen: Instance Profile der Compute-Ressource oder eine per [cloudFiles.roleArn](cloudFiles.roleArn.md) übernommene Rolle. Databricks empfiehlt, Secrets über Databricks-Secrets zu referenzieren statt sie im Klartext anzugeben.

*(Beschreibung sinngemäß nach der Spark API options reference; AWS-Tabelle beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.awsAccessKey", dbutils.secrets.get("scope", "aws-access-key"))
.option("cloudFiles.awsSecretKey", dbutils.secrets.get("scope", "aws-secret-key"))
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
