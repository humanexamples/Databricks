# cloudFiles.roleExternalId

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, AWS S3) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String |
| **`read_files`-Parameter** | `roleExternalId` |

## Beschreibung

External ID, die beim `AssumeRole` mit [cloudFiles.roleArn](cloudFiles.roleArn.md) mitgegeben wird (schützt vor dem "Confused Deputy"-Problem bei Cross-Account-Zugriff).

*(Beschreibung sinngemäß nach der Spark API options reference; AWS-Tabelle beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.roleArn", "arn:aws:iam::123456789012:role/AutoLoaderRole")
.option("cloudFiles.roleExternalId", "my-external-id")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
