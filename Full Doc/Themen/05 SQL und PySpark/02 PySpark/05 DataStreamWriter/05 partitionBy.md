# `DataStreamWriter.partitionBy()`

Partitioniert die Ausgabe im Dateisystem nach den angegebenen Spalten. Die Ausgabe wird ähnlich dem Partitionierungsschema von Hive abgelegt.

## Signatur

```python
partitionBy(*cols)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `*cols` | `str` oder `list` | Namen der Spalten, nach denen partitioniert werden soll. |

## Rückgabewert

`DataStreamWriter`

## Beispiele

### Partitionierungsspalte setzen

```python
df = spark.readStream.format("rate").load()
df.writeStream.partitionBy("value")
# <...streaming.readwriter.DataStreamWriter object ...>
```

### Rate-Source-Stream nach `timestamp` partitioniert als Parquet schreiben

```python
import tempfile
import time
with tempfile.TemporaryDirectory(prefix="partitionBy1") as d:
    with tempfile.TemporaryDirectory(prefix="partitionBy2") as cp:
        df = spark.readStream.format("rate").option("rowsPerSecond", 10).load()
        q = df.writeStream.partitionBy(
            "timestamp").format("parquet").option("checkpointLocation", cp).start(d)
        time.sleep(5)
        q.stop()
        spark.read.schema(df.schema).parquet(d).show()
```

## Quellen

- DataStreamWriter.partitionBy: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/partitionBy

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
