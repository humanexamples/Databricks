# `DataFrameReader.schema()`

Legt das Eingabeschema fest, das ein `DataFrameReader` beim Lesen verwenden soll — nützlich, um automatische Schema-Inferenz zu vermeiden.

## Signatur

```python
schema(schema)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `schema` | `StructType` oder `str` | Ein `StructType`-Objekt oder ein DDL-formatierter String (z. B. `'col0 INT, col1 DOUBLE'`). |

## Rückgabewert

`DataFrameReader`

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="schema") as d:
    spark.read.schema("col0 INT, col1 DOUBLE").format("csv").load(d).printSchema()
    # root
    #  |-- col0: integer (nullable = true)
    #  |-- col1: double (nullable = true)
```

## Quellen

- DataFrameReader.schema: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader/schema

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
