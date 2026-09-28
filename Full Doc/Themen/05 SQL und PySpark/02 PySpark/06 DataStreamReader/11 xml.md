# `DataStreamReader.xml()`

Lädt einen XML-Datei-Stream und gibt das Ergebnis als DataFrame zurück.

## Signatur

```python
xml(path, schema=None, **options)
```

## Beschreibung

*"Loads an XML file stream and returns the result as a DataFrame. If `schema` is not specified, the input schema is inferred from the data."*

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str` | Pfad für die XML-Eingabe. |
| `schema` | `StructType` oder `str`, optional | Schema als `StructType` oder DDL-String (z. B. `col0 INT, col1 DOUBLE`). |
| `**options` | | Weitere Formatoptionen, u. a. `rowTag` (Pflicht-Zeilen-Tag), siehe [Spark-API-Optionsreferenz](https://docs.databricks.com/aws/en/spark/api-options). |

## Rückgabewert

`DataFrame`

## Beispiel

```python
import tempfile
import time
with tempfile.TemporaryDirectory(prefix="xml") as d:
    spark.createDataFrame(
        [{"age": 100, "name": "Hyukjin Kwon"}]
    ).write.mode("overwrite").option("rowTag", "person").xml(d)

    q = spark.readStream.schema(
        "age INT, name STRING"
    ).xml(d, rowTag="person").writeStream.format("console").start()
    time.sleep(3)
    q.stop()
```

## Quellen

- DataStreamReader.xml: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/xml

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
