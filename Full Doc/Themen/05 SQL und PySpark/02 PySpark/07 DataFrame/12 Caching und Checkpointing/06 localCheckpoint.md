# `DataFrame.localCheckpoint()`

Gibt eine lokal gecheckpointete Version dieses DataFrames zurück. Checkpointing kann genutzt werden, um den logischen Plan abzuschneiden – besonders nützlich in iterativen Algorithmen, in denen der Plan exponentiell wachsen kann. Lokale Checkpoints werden über das Caching-Subsystem in den Executors gespeichert und sind daher **nicht zuverlässig**.

## Signatur

```python
localCheckpoint(eager: bool = True, storageLevel: Optional[StorageLevel] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `eager` | `bool`, optional, Standard `True` | Ob der DataFrame sofort gecheckpointet werden soll. |
| `storageLevel` | `StorageLevel`, optional, Standard `None` | Storage-Level, mit dem der Checkpoint gespeichert wird. Ohne Angabe wird der Standard für lokale RDD-Checkpoints verwendet. |

## Rückgabewert

`DataFrame`: Gecheckpointeter DataFrame.

## Hinweise

Diese API ist experimentell.

## Beispiel

```python
df = spark.createDataFrame([
    (14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df.localCheckpoint(False)
# DataFrame[age: bigint, name: string]
```

Siehe auch [`checkpoint`](05%20checkpoint.md).

## Quellen

- DataFrame.localCheckpoint: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/localCheckpoint

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
