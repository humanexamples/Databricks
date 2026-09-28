# `DataFrameReader.load()`

Lädt Daten aus einer Datenquelle und gibt sie als DataFrame zurück — die allgemeinste Lademethode, meist in Kombination mit `.format(...)`, `.schema(...)` und `.option(...)` verwendet.

## Signatur

```python
load(path=None, format=None, schema=None, **options)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str` oder `list`, optional | Ein oder mehrere Pfade in einer dateisystembasierten Datenquelle. |
| `format` | `str`, optional | Format der Datenquelle. Standardmäßig `'parquet'`. |
| `schema` | `StructType` oder `str`, optional | Eingabeschema als `StructType`-Objekt oder DDL-formatierter String (z. B. `'col0 INT, col1 DOUBLE'`). |
| `**options` | `dict` | Zusätzliche String-Optionen. |

## Rückgabewert

`DataFrame`

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="load") as d:
    df = spark.createDataFrame([{"age": 100, "name": "Alice"}])
    df.write.option("header", True).mode("overwrite").format("csv").save(d)
    df = spark.read.load(
        d, schema=df.schema, format="csv", nullValue="Alice", header=True)
    df.printSchema()
    # root
    #  |-- age: long (nullable = true)
    #  |-- name: string (nullable = true)
    df.show()
    # +---+----+
    # |age|name|
    # +---+----+
    # |100|NULL|
    # +---+----+
```

## Quellen

- DataFrameReader.load: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader/load

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
