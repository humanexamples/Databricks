# `DataFrameReader.json()`

Lädt JSON-Dateien (oder eine RDD von JSON-Strings) und gibt das Ergebnis als DataFrame zurück.

## Signatur

```python
json(path, schema=None, **options)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str`, `list` oder RDD | Ein Pfad zum JSON-Dataset, eine Liste von Pfaden, oder eine RDD von Strings, die JSON-Objekte enthält. |
| `schema` | `StructType` oder `str`, optional | Eingabeschema als `StructType`-Objekt oder DDL-formatierter String (z. B. `'col0 INT, col1 DOUBLE'`). |

## Rückgabewert

`DataFrame`

## Beispiele

**JSON schreiben und lesen:**

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="json") as d:
    spark.createDataFrame(
        [{"age": 100, "name": "Hyukjin"}]
    ).write.mode("overwrite").format("json").save(d)
    spark.read.json(d).show()
```

**Aus mehreren Verzeichnissen lesen:**

```python
from tempfile import TemporaryDirectory
with TemporaryDirectory(prefix="json2") as d1, TemporaryDirectory(prefix="json3") as d2:
    spark.createDataFrame(
        [{"age": 30, "name": "Bob"}]
    ).write.mode("overwrite").format("json").save(d1)
    spark.createDataFrame(
        [{"age": 25, "name": "Alice"}]
    ).write.mode("overwrite").format("json").save(d2)
    spark.read.json([d1, d2]).show()
```

**Mit explizitem Schema lesen:**

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="json") as d:
    spark.createDataFrame(
       [{"age": 30, "name": "Bob"}]
    ).write.mode("overwrite").format("json").save(d)
    spark.read.json(d, schema="name STRING, age INT").show()
```

## Quellen

- DataFrameReader.json: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader/json

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
