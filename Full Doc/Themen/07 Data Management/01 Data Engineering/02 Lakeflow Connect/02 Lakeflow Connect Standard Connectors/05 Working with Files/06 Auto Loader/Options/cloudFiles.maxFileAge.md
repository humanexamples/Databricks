# cloudFiles.maxFileAge

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | Dauer-String (Mindestwert `"14 days"`) |
| **`read_files`-Parameter** | `maxFileAge` |
| **Seit** | alle Versionen |

## Beschreibung

> „How long a file event is tracked for deduplication purposes. Databricks does not recommend tuning this parameter unless you are ingesting data at the order of millions of files an hour. […] Tuning `cloudFiles.maxFileAge` too aggressively can cause data quality issues such as duplicate ingestion or missing files. Therefore, Databricks recommends a conservative setting for `cloudFiles.maxFileAge`, such as 90 days, which is similar to what comparable data ingestion solutions recommend."

Kostenkontrollmechanismus zur Begrenzung des RocksDB-Zustandswachstums bei sehr großen Streams — **keine Standardeinstellung**. Deletes erscheinen in RocksDB zunächst als Tombstones (vorübergehend höherer Speicherverbrauch).

## Beispiel

```python
.option("cloudFiles.maxFileAge", "90 days")
```

## Siehe auch

- [../09 Datei-Tracking und Checkpoints.md](../09%20Datei-Tracking%20und%20Checkpoints.md)
- [../13 Observability.md](../13%20Observability.md) — Troubleshooting doppelte Verarbeitung
