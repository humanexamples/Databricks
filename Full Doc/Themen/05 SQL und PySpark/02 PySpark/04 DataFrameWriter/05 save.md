# `DataFrameWriter.save()`

Speichert den Inhalt des DataFrames in einer Datenquelle — die allgemeinste Schreibmethode, meist in Kombination mit `.format(...)` und `.mode(...)` verwendet.

## Signatur

```python
save(path=None, format=None, mode=None, partitionBy=None, **options)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str`, optional | Der Pfad in einem Hadoop-kompatiblen Dateisystem. |
| `format` | `str`, optional | Format, in dem gespeichert wird. |
| `mode` | `str`, optional | Verhalten, wenn Daten bereits existieren. Zulässige Werte: `'append'`, `'overwrite'`, `'ignore'`, `'error'`/`'errorifexists'` (Standard). |
| `partitionBy` | `list`, optional | Namen der Partitionierungsspalten. |
| `**options` | `dict` | Zusätzliche String-Optionen. |

## Rückgabewert

`None`

## Beispiel

```python
import tempfile

with tempfile.TemporaryDirectory(prefix="save") as d:
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

- DataFrameWriter.save: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/save

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
