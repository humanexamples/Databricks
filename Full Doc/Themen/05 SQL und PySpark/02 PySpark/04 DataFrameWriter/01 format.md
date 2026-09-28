# `DataFrameWriter.format()`

Legt fest, in welchem Format ein `DataFrameWriter` die Daten schreiben soll.

## Signatur

```python
format(source)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `source` | `str` | Name der Datenquelle, z. B. `'json'` oder `'parquet'`. |

## Rückgabewert

`DataFrameWriter`

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="format") as d:
    spark.createDataFrame(
        [{"age": 100, "name": "Alice"}]
    ).write.mode("overwrite").format("parquet").save(d)
    spark.read.format('parquet').load(d).show()
    # +---+------------+
    # |age|        name|
    # +---+------------+
    # |100|Alice|
    # +---+------------+
```

## Quellen

- DataFrameWriter.format: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/format

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
