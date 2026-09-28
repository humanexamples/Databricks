# `DataFrame.checkpoint()`

Gibt eine gecheckpointete Version dieses DataFrames zurück. Checkpointing kann genutzt werden, um den logischen Plan des DataFrames abzuschneiden – besonders nützlich in iterativen Algorithmen, in denen der Plan exponentiell wachsen kann. Gespeichert wird in Dateien im Checkpoint-Verzeichnis, das über `SparkContext.setCheckpointDir` oder die Konfiguration `spark.checkpoint.dir` gesetzt wird.

## Signatur

```python
checkpoint(eager: bool = True)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `eager` | `bool`, optional, Standard `True` | Ob der DataFrame sofort gecheckpointet werden soll. |

## Rückgabewert

`DataFrame`: Gecheckpointeter DataFrame.

## Hinweise

Diese API ist experimentell.

> **Serverless-Kompatibilität:** Databricks empfiehlt, auf `DataFrame.checkpoint()` zu verzichten, da es nicht mit der Serverless-Compute-Architektur von Databricks kompatibel ist. Den DataFrame stattdessen in eine Delta-Tabelle schreiben.

## Beispiel

```python
df = spark.createDataFrame([
    (14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df.checkpoint(False)
# DataFrame[age: bigint, name: string]
```

Siehe auch [`localCheckpoint`](06%20localCheckpoint.md).

## Quellen

- DataFrame.checkpoint: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/checkpoint

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
