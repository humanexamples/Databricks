# `DataStreamReader.parquet()`

Lädt einen Parquet-Datei-Stream und gibt das Ergebnis als DataFrame zurück.

## Signatur

```python
parquet(path, **options)
```

## Beschreibung

*"Loads a Parquet file stream and returns the result as a DataFrame."*

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str` | Pfad in einem beliebigen von Hadoop unterstützten Dateisystem. |
| `**options` | | Weitere Formatoptionen (z. B. `mergeSchema`, `datetimeRebaseMode`), siehe [Spark-API-Optionsreferenz](https://docs.databricks.com/aws/en/spark/api-options). |

## Rückgabewert

`DataFrame`

## Beispiel

```python
import tempfile
import time
with tempfile.TemporaryDirectory(prefix="parquet") as d:
    spark.range(10).write.mode("overwrite").format("parquet").save(d)
    q = spark.readStream.schema(
        "id LONG").parquet(d).writeStream.format("console").start()
    time.sleep(3)
    q.stop()
```

## Quellen

- DataStreamReader.parquet: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/parquet

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
