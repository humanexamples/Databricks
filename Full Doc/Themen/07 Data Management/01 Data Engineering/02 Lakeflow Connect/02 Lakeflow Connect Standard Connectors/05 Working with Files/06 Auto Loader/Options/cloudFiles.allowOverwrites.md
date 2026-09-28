# cloudFiles.allowOverwrites

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `false` |
| **Gültige Werte** | `true`, `false` |
| **`read_files`-Parameter** | `allowOverwrites` |
| **Seit** | alle Versionen |

## Beschreibung

> „Whether to allow input directory file changes to overwrite existing data."

Bei `false` (Standard) wird jede Datei genau einmal anhand ihres **Dateipfads** verarbeitet; angehängte/überschriebene Dateien werden nicht erneut aufgenommen. Bei `true` wird zusätzlich der **letzte Änderungszeitpunkt** ins Tracking aufgenommen — die neueste Version wird garantiert verarbeitet, doppelte Datensätze müssen aber selbst behandelt werden. Auto Loader verarbeitet dabei die gesamte Datei erneut, selbst bei nur teilweiser Änderung. Databricks empfiehlt, ausschließlich unveränderliche Dateien aufzunehmen und den Standardwert zu belassen.

## Beispiel

```python
.option("cloudFiles.allowOverwrites", "true")
```

## Siehe auch

- [../09 Datei-Tracking und Checkpoints.md](../09%20Datei-Tracking%20und%20Checkpoints.md)
- [../15 FAQ.md](../15%20FAQ.md)
