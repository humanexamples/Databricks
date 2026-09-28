# `DataStreamWriter.foreachBatch()`

Verarbeitet die Ausgabe der Streaming-Query mit einer bereitgestellten Funktion. Nur im **Micro-Batch-Modus** unterstützt (also wenn der Trigger nicht `continuous` ist). Bei jeder Micro-Batch wird die Funktion mit den Ausgabezeilen als DataFrame und der Batch-ID aufgerufen. Über die Batch-ID lässt sich die Ausgabe deduplizieren und transaktional in externe Systeme schreiben (z. B. `MERGE`/Upsert).

## Signatur

```python
foreachBatch(func)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `func` | `callable` | Eine Funktion, die einen DataFrame und eine Batch-ID (`int`) entgegennimmt. |

## Rückgabewert

`DataStreamWriter`

## Hinweise

Im Spark-Connect-Modus hat die bereitgestellte Funktion **keinen** Zugriff auf Variablen, die außerhalb von ihr definiert sind.

## Beispiel

```python
import time
df = spark.readStream.format("rate").load()
def func(batch_df, batch_id):
    batch_df.collect()
q = df.writeStream.foreachBatch(func).start()
time.sleep(3)
q.stop()
```

## Anwendungsfall: Upsert per `MERGE`

```python
from delta.tables import DeltaTable

def upsert_to_delta(micro_batch_df, batch_id):
    (DeltaTable.forName(spark, "catalog.schema.target").alias("t")
        .merge(micro_batch_df.alias("s"), "t.id = s.id")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute())

(spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_chk/target")
    .load("/Volumes/catalog/schema/landing/")
    .writeStream
    .foreachBatch(upsert_to_delta)
    .option("checkpointLocation", "/Volumes/catalog/schema/_chk/target")
    .trigger(availableNow=True)
    .start())
```

> Der `MERGE` im `foreachBatch` muss **idempotent** sein, da eine Batch bei einem Neustart wiederholt werden kann. Siehe [99 Dedup und Upsert Muster.md](../../../_Ingestion/Datei%20Ingestion%20Varianten/99%20Dedup%20und%20Upsert%20Muster.md).

## Quellen

- DataStreamWriter.foreachBatch: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/foreachBatch

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
