# `DataStreamReader.table()`

Definiert einen Streaming-DataFrame auf einer Tabelle.

## Signatur

```python
table(tableName)
```

## Beschreibung

*"Defines a streaming DataFrame on a table. The data source corresponding to the table must support streaming mode."*

Die zugehörige Datenquelle (z. B. Delta) muss den Streaming-Modus unterstützen.

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `tableName` | `str` | Name der Tabelle. |

## Rückgabewert

`DataFrame`

## Beispiel

```python
import tempfile
import time

_ = spark.sql("DROP TABLE IF EXISTS my_table")
with tempfile.TemporaryDirectory(prefix="table") as d:
    q1 = spark.readStream.format("rate").load().writeStream.toTable(
        "my_table", checkpointLocation=d)
    q2 = spark.readStream.table("my_table").writeStream.format("console").start()
    time.sleep(3)
    q1.stop()
    q2.stop()
    _ = spark.sql("DROP TABLE my_table")
```

## Quellen

- DataStreamReader.table: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/table

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
