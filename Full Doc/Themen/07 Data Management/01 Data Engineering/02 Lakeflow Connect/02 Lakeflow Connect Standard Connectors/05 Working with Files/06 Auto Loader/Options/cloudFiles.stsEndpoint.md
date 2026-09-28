# cloudFiles.stsEndpoint

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, AWS S3) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None (globaler STS-Endpunkt) |
| **Datentyp** | URL |
| **`read_files`-Parameter** | `stsEndpoint` |

## Beschreibung

Benutzerdefinierter AWS-STS-Endpunkt für die `AssumeRole`-Operation (z. B. regionaler STS-Endpunkt oder VPC-Endpunkt). Wird zusammen mit [cloudFiles.roleArn](cloudFiles.roleArn.md) verwendet.

*(Beschreibung sinngemäß nach der Spark API options reference; AWS-Tabelle beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.stsEndpoint", "https://sts.us-east-1.amazonaws.com")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
