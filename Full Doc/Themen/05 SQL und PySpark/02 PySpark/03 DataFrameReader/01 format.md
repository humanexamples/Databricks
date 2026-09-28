# `DataFrameReader.format()`

Legt fest, welches Datenquellenformat ein `DataFrameReader` beim Lesen verwenden soll.

## Signatur

```python
format(source)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `source` | `str` | Name der Datenquelle, z. B. `'json'` oder `'parquet'`. |

## Rückgabewert

`DataFrameReader`

## Beispiel

```python
import tempfile

with tempfile.TemporaryDirectory(prefix="format") as d:
    spark.createDataFrame(
        [{"age": 100, "name": "Alice"}]
    ).write.mode("overwrite").format("json").save(d)
    spark.read.format('json').load(d).show()
    # +---+------------+
    # |age|        name|
    # +---+------------+
    # |100|       Alice|
    # +---+------------+
```

## Quellen

- DataFrameReader.format: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader/format

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
