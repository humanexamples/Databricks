# `DataFrameWriter.text()`

Speichert den Inhalt des DataFrames als Textdatei am angegebenen Pfad.

## Signatur

```python
text(path, compression=None, lineSep=None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str` | Der Pfad in einem beliebigen Hadoop-kompatiblen Dateisystem. |
| `compression` | `str`, optional | Zu verwendender Compression-Codec. |
| `lineSep` | `str`, optional | Zu verwendendes Zeilentrennzeichen. |

## Rückgabewert

`None`

## Wichtige Einschränkung

> Das DataFrame darf nur **eine** Spalte vom Typ String besitzen. Jede Zeile wird zu einer neuen Zeile in der Ausgabedatei.

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="text") as d:
    df = spark.createDataFrame([("a",), ("b",), ("c",)], schema=["alphabets"])
    df.write.mode("overwrite").text(d)
    spark.read.schema(df.schema).format("text").load(d).sort("alphabets").show()
    # +---------+
    # |alphabets|
    # +---------+
    # |        a|
    # |        b|
    # |        c|
    # +---------+
```

## Quellen

- DataFrameWriter.text: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/text

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
