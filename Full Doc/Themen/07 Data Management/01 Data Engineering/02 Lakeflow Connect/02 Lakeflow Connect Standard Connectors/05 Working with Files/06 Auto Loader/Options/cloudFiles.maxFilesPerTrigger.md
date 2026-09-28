# cloudFiles.maxFilesPerTrigger

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `1000` |
| **Datentyp** | positive Ganzzahl |
| **`read_files`-Parameter** | `maxFilesPerTrigger` |
| **Seit** | alle Versionen; ab Databricks Runtime 18.0 dynamisch konfiguriert |

## Beschreibung

> „The maximum number of new files to be processed in every trigger. When used together with `cloudFiles.maxBytesPerTrigger`, Azure Databricks consumes up to the lower limit of `cloudFiles.maxFilesPerTrigger` or `cloudFiles.maxBytesPerTrigger`, whichever is reached first. This option has no effect when used with `Trigger.Once()` (deprecated). In Databricks Runtime 18.0 and above, this option is dynamically configured and does not need to be set manually."

**Harte** Datei-Obergrenze pro Micro-Batch (Rate Limiting).

## Beispiel

```python
.option("cloudFiles.maxFilesPerTrigger", 500)
```

## Siehe auch

- [cloudFiles.maxBytesPerTrigger.md](cloudFiles.maxBytesPerTrigger.md)
- [../12 Produktionsbetrieb.md](../12%20Produktionsbetrieb.md)
