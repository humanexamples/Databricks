# databricks.serviceCredential

| | |
|---|---|
| **Kategorie** | File Notification Mode option — **kein `cloudFiles.*`**, aber mit Auto Loader verwendet |
| **Seite** | `spark.readStream` (`DataStreamReader`) bzw. Cloud Resource Manager |
| **Standardwert** | None |
| **Datentyp** | String (Name eines UC-Service-Credentials) |
| **`read_files`-Parameter** | `databricks.serviceCredential` |
| **Seit** | Databricks Runtime 16.1 und höher |

## Beschreibung

> „The name of your Databricks service credential."

Empfohlene Authentifizierung für den klassischen File-Notification-Modus (Azure ab DBR 16.1) und für den Cloud Resource Manager (`CloudFilesAWSResourceManager` / `…Azure…` / `…GCP…`). Ersetzt die direkte Angabe von Access Keys / Client Secrets / Private Keys.

## Beispiel

```python
.option("cloudFiles.useNotifications", "true")
.option("databricks.serviceCredential", "my-service-credential")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md) — Cloud Resource Manager
- [../08 Migration zu File Events.md](../08%20Migration%20zu%20File%20Events.md)
