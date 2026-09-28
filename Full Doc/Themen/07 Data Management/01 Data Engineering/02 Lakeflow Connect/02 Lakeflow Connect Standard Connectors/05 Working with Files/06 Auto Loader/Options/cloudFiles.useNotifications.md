# cloudFiles.useNotifications

| | |
|---|---|
| **Kategorie** | File Notification Mode option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `false` |
| **Gültige Werte** | `true`, `false` |
| **`read_files`-Parameter** | `useNotifications` |
| **Seit** | alle Versionen |

## Beschreibung

> „Whether to use file notification mode to determine when there are new files. If `false`, use directory listing mode. […] Do not use when `cloudFiles.useManagedFileEvents` is set to `true`."

Aktiviert den **klassischen** File-Notification-Modus. Auto Loader richtet dann (mit den erforderlichen Berechtigungen) selbst Benachrichtigungs- und Queue-Dienste pro Stream ein, oder konsumiert aus einer bestehenden Queue (`cloudFiles.queueUrl` / `cloudFiles.queueName` / `cloudFiles.subscription`). Für File Events stattdessen `cloudFiles.useManagedFileEvents = true` verwenden.

## Beispiel

```python
.option("cloudFiles.useNotifications", "true")
.option("cloudFiles.region", "us-east-1")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
- [cloudFiles.useManagedFileEvents.md](cloudFiles.useManagedFileEvents.md)
