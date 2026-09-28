# `DataStreamReader.load()`

Lädt einen Datenstrom aus einer Datenquelle und gibt ihn als DataFrame zurück.

## Signatur

```python
load(path=None, format=None, schema=None, **options)
```

## Beschreibung

*"Loads a data stream from a data source and returns it as a DataFrame."*

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str`, optional | Pfad für dateisystembasierte Datenquellen. |
| `format` | `str`, optional | Format der Datenquelle. Standard: `'parquet'`. |
| `schema` | `StructType` oder `str`, optional | Schema der Eingabedaten als `StructType` oder DDL-String (z. B. `col0 INT, col1 DOUBLE`). |
| `**options` | | Alle weiteren String-Optionen. |

## Rückgabewert

`DataFrame`

## Beispiel

```python
import tempfile
import time
with tempfile.TemporaryDirectory(prefix="load") as d:
    spark.createDataFrame(
        [(100, "Hyukjin Kwon"),], ["age", "name"]
    ).write.mode("overwrite").format("json").save(d)
    q = spark.readStream.schema(
        "age INT, name STRING"
    ).format("json").load(d).writeStream.format("console").start()
    time.sleep(3)
    q.stop()
```

## Quellen

- DataStreamReader.load: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/load

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
