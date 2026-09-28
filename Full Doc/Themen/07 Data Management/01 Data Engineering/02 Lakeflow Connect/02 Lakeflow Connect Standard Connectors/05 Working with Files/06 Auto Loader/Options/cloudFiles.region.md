# cloudFiles.region

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, AWS S3) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | Region der EC2-Instanz standardmäßig; ansonsten anzugeben |
| **Datentyp** | AWS-Regions-String (z. B. `us-east-1`) |
| **`read_files`-Parameter** | `region` |

## Beschreibung

Die AWS-Region, in der der Quell-S3-Bucket liegt und in der die SNS- und SQS-Dienste angelegt werden. Erforderlich beim klassischen File-Notification-Modus (`cloudFiles.useNotifications = true`), wenn Auto Loader die Benachrichtigungsdienste selbst einrichten soll. Nicht relevant bei File Events.

*(Beschreibung sinngemäß nach [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options) und [File notification mode](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-notification-mode); die AWS-Optionstabelle war beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.useNotifications", "true")
.option("cloudFiles.region", "us-east-1")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
