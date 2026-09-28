# `DataStreamWriter.clusterBy()`

Clustert die Ausgabe nach den angegebenen Spalten. Datensätze mit ähnlichen Werten in den Cluster-Spalten landen in derselben Datei. Clustering verbessert die Query-Effizienz, weil Queries mit Prädikaten auf den Cluster-Spalten unnötige Daten überspringen können. Anders als Partitionierung eignet sich Clustering auch für Spalten mit hoher Kardinalität.

## Signatur

```python
clusterBy(*cols)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `*cols` | `str` oder `list` | Namen der Spalten, nach denen geclustert werden soll. |

## Rückgabewert

`DataStreamWriter`

## Beispiele

### Cluster-Spalte setzen

```python
df = spark.readStream.format("rate").load()
df.writeStream.clusterBy("value")
# <...streaming.readwriter.DataStreamWriter object ...>
```

### Rate-Source-Stream nach `timestamp` geclustert als Parquet schreiben

```python
import tempfile
import time
with tempfile.TemporaryDirectory(prefix="clusterBy1") as d:
    with tempfile.TemporaryDirectory(prefix="clusterBy2") as cp:
        df = spark.readStream.format("rate").option("rowsPerSecond", 10).load()
        q = df.writeStream.clusterBy(
            "timestamp").format("parquet").option("checkpointLocation", cp).start(d)
        time.sleep(5)
        q.stop()
        spark.read.schema(df.schema).parquet(d).show()
```

## Quellen

- DataStreamWriter.clusterBy: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/clusterBy

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
