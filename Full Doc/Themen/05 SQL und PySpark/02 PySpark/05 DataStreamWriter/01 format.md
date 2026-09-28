# `DataStreamWriter.format()`

Legt die zugrunde liegende Ausgabe-Datenquelle (die Senke) fest.

## Signatur

```python
format(source)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `source` | `str` | Name der Datenquelle, z. B. `'parquet'` oder `'console'`. |

## Rückgabewert

`DataStreamWriter`

## Beispiele

### Format setzen

```python
df = spark.readStream.format("rate").load()
df.writeStream.format("text")
# <...streaming.readwriter.DataStreamWriter object ...>
```

### Rate-Source-Stream als CSV schreiben

```python
import tempfile
import time
with tempfile.TemporaryDirectory(prefix="format1") as d:
    with tempfile.TemporaryDirectory(prefix="format2") as cp:
        df = spark.readStream.format("rate").load()
        q = df.writeStream.format("csv").option("checkpointLocation", cp).start(d)
        time.sleep(5)
        q.stop()
        spark.read.schema("timestamp TIMESTAMP, value STRING").csv(d).show()
```

## Quellen

- DataStreamWriter.format: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/format

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
