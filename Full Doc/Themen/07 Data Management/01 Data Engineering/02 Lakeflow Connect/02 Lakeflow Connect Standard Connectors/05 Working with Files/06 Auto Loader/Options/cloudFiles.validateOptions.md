# cloudFiles.validateOptions

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `true` |
| **Gültige Werte** | `true`, `false` |
| **`read_files`-Parameter** | `validateOptions` |
| **Seit** | alle Versionen |

## Beschreibung

> „Whether to validate Auto Loader options and return an error for unknown or inconsistent options."

Bei `false` werden unbekannte/inkonsistente Optionen nicht als Fehler gemeldet — u. a. Teil des Workarounds für den Fehler `CF_MANAGED_FILE_EVENTS_INVALID_CONTINUATION_TOKEN`.

## Beispiel

```python
.option("cloudFiles.validateOptions", False)
```

## Siehe auch

- [../15 FAQ.md](../15%20FAQ.md) — Frage zu `CF_MANAGED_FILE_EVENTS_INVALID_CONTINUATION_TOKEN`
- [cloudFiles.listOnStart.md](cloudFiles.listOnStart.md)
