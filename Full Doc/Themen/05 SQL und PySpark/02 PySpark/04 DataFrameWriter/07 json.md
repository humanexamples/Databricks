# `DataFrameWriter.json()`

Speichert den Inhalt des DataFrames im JSON-Format (JSON Lines / newline-delimited JSON) am angegebenen Pfad.

## Signatur

```python
json(path, mode=None, compression=None, dateFormat=None, timestampFormat=None,
     lineSep=None, encoding=None, ignoreNullFields=None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str` | Der Pfad in einem beliebigen Hadoop-kompatiblen Dateisystem. |
| `mode` | `str`, optional | Verhalten, wenn Daten bereits existieren. Zulässige Werte: `'append'`, `'overwrite'`, `'ignore'`, `'error'`/`'errorifexists'` (Standard). |
| `compression`, `dateFormat`, `timestampFormat`, `lineSep`, `encoding`, `ignoreNullFields` | optional | Weitere JSON-Schreiboptionen, entsprechen den gleichnamigen Optionen bei `.option()`/`.options()`. |

## Rückgabewert

`None`

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="json") as d:
    spark.createDataFrame(
        [{"age": 100, "name": "Alice"}]
    ).write.json(d, mode="overwrite")
    spark.read.format("json").load(d).show()
    # +---+------------+
    # |age|        name|
    # +---+------------+
    # |100|Alice|
    # +---+------------+
```

## Quellen

- DataFrameWriter.json: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/json

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
