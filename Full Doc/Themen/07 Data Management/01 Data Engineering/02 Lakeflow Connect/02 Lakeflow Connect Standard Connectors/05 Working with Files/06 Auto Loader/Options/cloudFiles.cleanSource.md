# cloudFiles.cleanSource

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `OFF` |
| **Gültige Werte** | `OFF`, `DELETE`, `MOVE` |
| **`read_files`-Parameter** | `cleanSource` |
| **Seit** | Databricks Runtime 16.4 und höher |

## Beschreibung

> „Whether to automatically delete or move processed files from the input directory. When set to `OFF` (default), no files are deleted. When set to `DELETE` or `MOVE`, Auto Loader deletes or moves files after they are processed."

Setzt exklusiven Zugriff des Streams auf das Quellverzeichnis voraus. Bei `foreachBatch` gelten Dateien bereits als Kandidaten, sobald der Aufruf erfolgreich zurückkehrt. Aktivierung erhöht den Checkpoint-Overhead, ermöglicht aber die Archiv-Felder in `cloud_files_state`.

## Beispiel

```python
.option("cloudFiles.cleanSource", "MOVE")
.option("cloudFiles.cleanSource.moveDestination", "s3://my-bucket/archive/landing/")
.option("cloudFiles.cleanSource.retentionDuration", "14 days")
```

## Siehe auch

- [../10 Clean Source (Quelldateien aufräumen).md](../10%20Clean%20Source%20%28Quelldateien%20aufräumen%29.md)
- [cloudFiles.cleanSource.retentionDuration.md](cloudFiles.cleanSource.retentionDuration.md)
- [cloudFiles.cleanSource.moveDestination.md](cloudFiles.cleanSource.moveDestination.md)
