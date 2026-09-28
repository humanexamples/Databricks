# `DataStreamReader.text()`

Lädt einen Text-Datei-Stream und gibt das Ergebnis als DataFrame zurück.

## Signatur

```python
text(path, **options)
```

## Beschreibung

*"Loads a text file stream and returns a DataFrame whose schema starts with a string column named `value`, followed by any partitioned columns."*

UTF-8-Kodierung ist erforderlich; standardmäßig wird jede Zeile zu einer Zeile im DataFrame.

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str` | Pfad für die Text-Eingabe. |
| `**options` | | Weitere Formatoptionen (`wholeText`, `lineSep`), siehe [Spark-API-Optionsreferenz](https://docs.databricks.com/aws/en/spark/api-options). |

## Rückgabewert

`DataFrame`

## Beispiel

```python
import tempfile
import time
with tempfile.TemporaryDirectory(prefix="text") as d:
    spark.createDataFrame(
        [("hello",), ("this",)]).write.mode("overwrite").format("text").save(d)
    q = spark.readStream.text(d).writeStream.format("console").start()
    time.sleep(3)
    q.stop()
```

## Quellen

- DataStreamReader.text: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/text

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
