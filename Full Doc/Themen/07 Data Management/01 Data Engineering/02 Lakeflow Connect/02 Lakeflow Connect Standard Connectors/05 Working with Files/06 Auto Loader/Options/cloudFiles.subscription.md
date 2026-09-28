# cloudFiles.subscription

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, GCS) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String |
| **`read_files`-Parameter** | `subscription` |

## Beschreibung

Name einer **bereits bestehenden** Google-Pub/Sub-Subscription. Ist sie angegeben, konsumiert Auto Loader Ereignisse direkt daraus, statt eigene Pub/Sub-Ressourcen einzurichten. GCS-Gegenstück zu [cloudFiles.queueUrl](cloudFiles.queueUrl.md) (AWS) bzw. [cloudFiles.queueName](cloudFiles.queueName.md) (Azure).

*(Beschreibung sinngemäß nach der Spark API options reference; GCS-Tabelle beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.useNotifications", "true")
.option("cloudFiles.subscription", "my-existing-subscription")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
