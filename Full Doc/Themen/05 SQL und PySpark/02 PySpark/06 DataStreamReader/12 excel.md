# `DataStreamReader.excel()`

Lädt einen Excel-Datei-Stream und gibt das Ergebnis als DataFrame zurück.

## Signatur

```python
excel(path, **options)
```

## Beschreibung

*"Loads an Excel file stream and returns the result as a DataFrame."*

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str` | Pfad zum Excel-Datensatz. |
| `**options` | | Weitere Formatoptionen (`dataAddress`, `header`, …), siehe [Spark-API-Optionsreferenz](https://docs.databricks.com/aws/en/spark/api-options). |

## Rückgabewert

`DataFrame`

## Beispiel

```python
import tempfile
import time
with tempfile.TemporaryDirectory(prefix="excel") as d:
    spark.range(10).write.mode("overwrite").excel(d)
    q = spark.readStream.schema("id LONG").excel(d).writeStream.format("console").start()
    time.sleep(3)
    q.stop()
```

## Quellen

- DataStreamReader.excel: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/excel

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
