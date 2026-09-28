# `DataStreamReader.orc()`

Lädt einen ORC-Datei-Stream und gibt das Ergebnis als DataFrame zurück.

## Signatur

```python
orc(path, **options)
```

## Beschreibung

*"Loads an ORC file stream and returns the result as a DataFrame."*

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str` | Pfad zum ORC-Datensatz. |
| `**options` | | Weitere Formatoptionen (z. B. `mergeSchema`), siehe [Spark-API-Optionsreferenz](https://docs.databricks.com/aws/en/spark/api-options). |

## Rückgabewert

`DataFrame`

## Beispiel

```python
import tempfile
import time
with tempfile.TemporaryDirectory(prefix="orc") as d:
    spark.range(10).write.mode("overwrite").format("orc").save(d)
    q = spark.readStream.schema("id LONG").orc(d).writeStream.format("console").start()
    time.sleep(3)
    q.stop()
```

## Quellen

- DataStreamReader.orc: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/orc

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
