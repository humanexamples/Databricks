# `DataStreamWriter.queryName()`

Vergibt den Namen der `StreamingQuery`, die mit `start()` gestartet wird. Der Name muss unter allen aktuell aktiven Queries derselben `SparkSession` eindeutig sein.

## Signatur

```python
queryName(queryName)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `queryName` | `str` | Eindeutiger Name für die Query. |

## Rückgabewert

`DataStreamWriter`

## Beispiel

```python
import time
df = spark.readStream.format("rate").load()
q = df.writeStream.queryName("streaming_query").format("console").start()
q.stop()
q.name
# 'streaming_query'
```

## Quellen

- DataStreamWriter.queryName: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/queryName

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
