# cloudFiles.roleArn

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, AWS S3) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | IAM-Rollen-ARN |
| **`read_files`-Parameter** | `roleArn` |

## Beschreibung

ARN einer IAM-Rolle, die für den Zugriff auf SNS/SQS (und ggf. S3) per `AssumeRole` übernommen wird — u. a. für Cross-Account-Ingestion. Optional kombinierbar mit [cloudFiles.roleExternalId](cloudFiles.roleExternalId.md), [cloudFiles.roleSessionName](cloudFiles.roleSessionName.md) und [cloudFiles.stsEndpoint](cloudFiles.stsEndpoint.md).

*(Beschreibung sinngemäß nach der Spark API options reference; AWS-Tabelle beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.roleArn", "arn:aws:iam::123456789012:role/AutoLoaderRole")
.option("cloudFiles.roleExternalId", "databricks")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md) — Cross-Account-Ingestion (AWS)
