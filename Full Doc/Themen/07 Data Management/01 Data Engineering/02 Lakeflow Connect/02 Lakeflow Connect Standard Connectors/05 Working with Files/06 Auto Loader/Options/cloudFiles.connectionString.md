# cloudFiles.connectionString

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, Azure ADLS/Blob) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | Connection-String |
| **`read_files`-Parameter** | `connectionString` |

## Beschreibung

> „The connection string for the storage account, based on either account access key or shared access signature (SAS)."

Authentifizierungsalternative zum Databricks-Service-Credential bzw. Service Principal. Über Databricks-Secrets referenzieren.

## Beispiel

```python
.option("cloudFiles.connectionString", dbutils.secrets.get("scope", "adls-conn-str"))
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
