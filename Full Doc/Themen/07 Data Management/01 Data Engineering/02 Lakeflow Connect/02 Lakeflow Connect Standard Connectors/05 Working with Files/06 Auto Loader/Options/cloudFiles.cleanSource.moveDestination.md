# cloudFiles.cleanSource.moveDestination

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | Cloud-Speicher- oder Unity-Catalog-Volume-Pfad |
| **`read_files`-Parameter** | `cleanSource.moveDestination` |
| **Seit** | Databricks Runtime 16.4 und höher |

## Beschreibung

> „Path to archive processed files to when `cloudFiles.cleanSource` is set to `MOVE`."

Nur erforderlich bei `cloudFiles.cleanSource = MOVE`. Darf **kein Kindverzeichnis** des Quellverzeichnisses sein (sonst Re-Ingestion). Muss in derselben External Location / demselben Volume / DBFS-Mount liegen — Verschiebungen über Buckets/Container hinweg schlagen fehl. Auto Loader benötigt Schreibberechtigung auf dem Ziel.

## Beispiel

```python
.option("cloudFiles.cleanSource", "MOVE")
.option("cloudFiles.cleanSource.moveDestination", "s3://my-bucket/archive/landing/")
```

## Siehe auch

- [../10 Clean Source (Quelldateien aufräumen).md](../10%20Clean%20Source%20%28Quelldateien%20aufräumen%29.md)
