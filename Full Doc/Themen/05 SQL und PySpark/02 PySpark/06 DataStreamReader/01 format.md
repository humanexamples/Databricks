# `DataStreamReader.format()`

Legt das Format der Eingabe-Datenquelle fest.

## Signatur

```python
format(source)
```

## Beschreibung

*"Specifies the input data source format."*

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `source` | `str` | Name der Datenquelle, z. B. `'json'` oder `'parquet'`. |

## Rückgabewert

`DataStreamReader`

## Beispiele

```python
spark.readStream.format("text")
# <...streaming.readwriter.DataStreamReader object ...>
```

```python
import tempfile
import time
with tempfile.TemporaryDirectory(prefix="format") as d:
    spark.createDataFrame(
        [("hello",), ("this",)]).write.mode("overwrite").format("text").save(d)
    q = spark.readStream.format("text").load(d).writeStream.format("console").start()
    time.sleep(3)
    q.stop()
```

## Quellen

- DataStreamReader.format: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/format

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
