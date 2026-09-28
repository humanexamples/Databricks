# cloudFiles.roleSessionName

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, AWS S3) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String |
| **`read_files`-Parameter** | `roleSessionName` |

## Beschreibung

Session-Name, der beim `AssumeRole` mit [cloudFiles.roleArn](cloudFiles.roleArn.md) verwendet wird (erscheint in CloudTrail-Logs zur Nachverfolgung).

*(Beschreibung sinngemäß nach der Spark API options reference; AWS-Tabelle beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.roleSessionName", "autoloader-bronze-events")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
