# `DataFrameWriter.csv()`

Speichert den Inhalt des DataFrames im CSV-Format am angegebenen Pfad.

## Signatur

```python
csv(path, mode=None, compression=None, sep=None, quote=None, escape=None,
    header=None, nullValue=None, escapeQuotes=None, quoteAll=None,
    dateFormat=None, timestampFormat=None, ignoreLeadingWhiteSpace=None,
    ignoreTrailingWhiteSpace=None, charToEscapeQuoteEscaping=None,
    encoding=None, emptyValue=None, lineSep=None)
```

## Parameter (Auswahl)

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str` | Der Pfad in einem Hadoop-kompatiblen Dateisystem. |
| `mode` | `str`, optional | Verhalten, wenn Daten bereits existieren. Zulässige Werte: `'append'`, `'overwrite'`, `'ignore'`, `'error'`/`'errorifexists'` (Standard). |

Die restlichen Parameter (`sep`, `quote`, `escape`, `header`, `nullValue`, `escapeQuotes`, `quoteAll`, `dateFormat`, `timestampFormat`, `ignoreLeadingWhiteSpace`, `ignoreTrailingWhiteSpace`, `charToEscapeQuoteEscaping`, `encoding`, `emptyValue`, `lineSep`) entsprechen den gleichnamigen CSV-Schreiboptionen und können alternativ über `.option()`/`.options()` gesetzt werden.

## Rückgabewert

`None`

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="csv") as d:
    df = spark.createDataFrame([{"age": 100, "name": "Alice"}])
    df.write.csv(d, mode="overwrite")
    spark.read.schema(df.schema).format("csv").option(
        "nullValue", "Alice").load(d).show()
    # +---+----+
    # |age|name|
    # +---+----+
    # |100|NULL|
    # +---+----+
```

## Quellen

- DataFrameWriter.csv: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/csv

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
