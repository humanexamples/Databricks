# cloudFiles.maxBytesPerTrigger

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | Byte-String (z. B. `10g`) |
| **`read_files`-Parameter** | `maxBytesPerTrigger` |
| **Seit** | alle Versionen; ab Databricks Runtime 18.0 dynamisch konfiguriert |

## Beschreibung

> „The maximum number of new bytes to be processed in every trigger. This is a soft maximum. If you have files that are 3 GB each, Azure Databricks processes 12 GB in a micro-batch. An individual file is never split across micro-batches; it is always processed in full within a single one, even when its size exceeds this limit. When used together with `cloudFiles.maxFilesPerTrigger`, Azure Databricks consumes up to the lower limit of `cloudFiles.maxFilesPerTrigger` or `cloudFiles.maxBytesPerTrigger`, whichever is reached first. This option has no effect when used with `Trigger.Once()` (`Trigger.Once()` is deprecated). In Databricks Runtime 18.0 and above, this option is dynamically configured and does not need to be set manually."

**Weiche** Byte-Obergrenze pro Micro-Batch.

## Beispiel

```python
.option("cloudFiles.maxBytesPerTrigger", "10g")
```

## Siehe auch

- [cloudFiles.maxFilesPerTrigger.md](cloudFiles.maxFilesPerTrigger.md)
- [../12 Produktionsbetrieb.md](../12%20Produktionsbetrieb.md)
