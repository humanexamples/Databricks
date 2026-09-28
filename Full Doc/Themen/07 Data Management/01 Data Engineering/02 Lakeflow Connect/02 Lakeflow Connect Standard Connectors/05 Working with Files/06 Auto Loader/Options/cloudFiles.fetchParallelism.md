# cloudFiles.fetchParallelism

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `1` |
| **Datentyp** | positive Ganzzahl |
| **`read_files`-Parameter** | `fetchParallelism` |
| **Seit** | alle Versionen |

## Beschreibung

> „Number of threads to use when fetching messages from the queueing service. Do not use when `cloudFiles.useManagedFileEvents` is set to `true`."

## Beispiel

```python
.option("cloudFiles.fetchParallelism", 4)
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
