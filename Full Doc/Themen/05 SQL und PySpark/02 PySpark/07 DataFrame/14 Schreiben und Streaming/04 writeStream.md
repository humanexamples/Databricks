# `DataFrame.writeStream` (Eigenschaft)

Schnittstelle zum Speichern des Inhalts eines Streaming-`DataFrame` in externe Speichersysteme.

## Rückgabewert

`DataStreamWriter` – Details siehe [../05 DataStreamWriter/00 Uebersicht.md](../../05%20DataStreamWriter/00%20Uebersicht.md).

## Beispiel

```python
import time
import tempfile
df = spark.readStream.format("rate").load()
type(df.writeStream)
# <class '...streaming.readwriter.DataStreamWriter'>

with tempfile.TemporaryDirectory(prefix="writeStream") as d:
    query = df.writeStream.toTable("my_table", checkpointLocation=d)
    time.sleep(3)
    query.stop()
```

Siehe auch [`write`](01%20write.md), [`isStreaming`](05%20isStreaming.md), [`withWatermark`](06%20withWatermark.md).

## Quellen

- DataFrame.writeStream: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/writeStream

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
