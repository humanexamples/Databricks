# cloudFiles.tenantId

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, Azure ADLS/Blob) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String |
| **`read_files`-Parameter** | `tenantId` |

## Beschreibung

> „The Azure Tenant ID in which the service principal is created."

Authentifizierungsalternative über Microsoft-Entra-ID-Service-Principal, wenn kein Databricks-Service-Credential verwendet wird. Zusammen mit [cloudFiles.clientId](cloudFiles.clientId.md) und [cloudFiles.clientSecret](cloudFiles.clientSecret.md).

## Beispiel

```python
.option("cloudFiles.tenantId", "<tenant-id>")
.option("cloudFiles.clientId", "<client-id>")
.option("cloudFiles.clientSecret", dbutils.secrets.get("scope", "sp-secret"))
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
