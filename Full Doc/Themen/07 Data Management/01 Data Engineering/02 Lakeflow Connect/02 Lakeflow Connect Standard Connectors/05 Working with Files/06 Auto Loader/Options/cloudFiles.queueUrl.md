# cloudFiles.queueUrl

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, AWS S3) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | SQS-Queue-URL |
| **`read_files`-Parameter** | `queueUrl` |

## Beschreibung

URL einer **bereits bestehenden** SQS-Queue. Ist sie angegeben, konsumiert Auto Loader Ereignisse direkt aus dieser Queue, statt eigene SNS-/SQS-Ressourcen einzurichten; die bereitgestellten Zugangsdaten benötigen dann nur Lese-/Löschrechte auf der Queue. Bei einer Queue, die Benachrichtigungen aus mehreren Buckets erhält, wird zusätzlich [cloudFiles.pathRewrites](cloudFiles.pathRewrites.md) benötigt.

*(Beschreibung sinngemäß nach der Spark API options reference / File-notification-mode-Seite.)*

## Beispiel

```python
.option("cloudFiles.useNotifications", "true")
.option("cloudFiles.queueUrl", "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
- [../08 Migration zu File Events.md](../08%20Migration%20zu%20File%20Events.md)
