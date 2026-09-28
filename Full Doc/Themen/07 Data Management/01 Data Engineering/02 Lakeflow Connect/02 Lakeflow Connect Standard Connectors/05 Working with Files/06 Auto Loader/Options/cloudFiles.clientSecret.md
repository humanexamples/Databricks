# cloudFiles.clientSecret

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, Azure ADLS/Blob) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String |
| **`read_files`-Parameter** | `clientSecret` |

## Beschreibung

> „The client secret of the service principal."

Über Databricks-Secrets referenzieren, nicht im Klartext angeben. Zusammen mit [cloudFiles.tenantId](cloudFiles.tenantId.md) und [cloudFiles.clientId](cloudFiles.clientId.md).

## Beispiel

```python
.option("cloudFiles.clientSecret", dbutils.secrets.get("scope", "sp-secret"))
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
