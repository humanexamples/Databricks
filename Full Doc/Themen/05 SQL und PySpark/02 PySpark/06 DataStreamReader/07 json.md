# `DataStreamReader.json()`

Lädt einen JSON-Datei-Stream und gibt das Ergebnis als DataFrame zurück.

## Signatur

```python
json(path, schema=None, **options)
```

## Beschreibung

*"Loads a JSON file stream and returns the results as a DataFrame. JSON Lines (newline-delimited JSON) is supported by default. For JSON with one record per file, set the `multiLine` option to `true`. If `schema` is not specified, the input schema is inferred from the data."*

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str` | Pfad zum JSON-Datensatz. |
| `schema` | `StructType` oder `str`, optional | Schema als `StructType` oder DDL-String (z. B. `col0 INT, col1 DOUBLE`). |
| `**options` | | Weitere Formatoptionen (z. B. `multiLine`), siehe [Spark-API-Optionsreferenz](https://docs.databricks.com/aws/en/spark/api-options). |

## Rückgabewert

`DataFrame`

## Beispiel

```python
import tempfile
import time
with tempfile.TemporaryDirectory(prefix="json") as d:
    spark.createDataFrame(
        [(100, "Hyukjin Kwon"),], ["age", "name"]
    ).write.mode("overwrite").format("json").save(d)
    q = spark.readStream.schema(
        "age INT, name STRING"
    ).json(d).writeStream.format("console").start()
    time.sleep(3)
    q.stop()
```

## Quellen

- DataStreamReader.json: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/json

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
