# cloudFiles.listOnStart

| | |
|---|---|
| **Kategorie** | File Notification Mode option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `false` |
| **Gültige Werte** | `true`, `false` |
| **`read_files`-Parameter** | `listOnStart` |
| **Seit** | — (mit File Events eingeführt) |

## Beschreibung

> „When set to `true`, Auto Loader performs a full directory listing when the stream starts, instead of starting with the continuation token in the checkpoint. Use this option to recover from errors, such as `CF_MANAGED_FILE_EVENTS_INVALID_CONTINUATION_TOKEN`."

## Beispiel

```python
.option("cloudFiles.listOnStart", "true")
.option("cloudFiles.validateOptions", False)
```

## Siehe auch

- [../15 FAQ.md](../15%20FAQ.md)
- [cloudFiles.validateOptions.md](cloudFiles.validateOptions.md)
