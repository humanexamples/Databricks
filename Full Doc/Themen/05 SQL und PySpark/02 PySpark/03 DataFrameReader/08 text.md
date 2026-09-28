# `DataFrameReader.text()`

Lädt Textdateien und gibt ein DataFrame mit genau einer String-Spalte namens `"value"` zurück — pro Zeile der Datei eine Zeile im DataFrame.

## Signatur

```python
text(paths, wholetext=False, lineSep=None, **options)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `paths` | `str` oder `list` | Ein oder mehrere Eingabepfade. |
| `wholetext` | `bool`, optional | Wenn `True`, wird jede Datei als eine einzige Zeile gelesen. Standard: `False`. |
| `lineSep` | `str`, optional | Zu verwendendes Zeilentrennzeichen. Standard: `'\n'`, `'\r'` oder `'\r\n'`. |

## Rückgabewert

`DataFrame`

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="text") as d:
    df = spark.createDataFrame([("a",), ("b",), ("c",)], schema=["alphabets"])
    df.write.mode("overwrite").format("text").save(d)
    spark.read.schema(df.schema).text(d).sort("alphabets").show()
    # +---------+
    # |alphabets|
    # +---------+
    # |        a|
    # |        b|
    # |        c|
    # +---------+
```

## Quellen

- DataFrameReader.text: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader/text

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
