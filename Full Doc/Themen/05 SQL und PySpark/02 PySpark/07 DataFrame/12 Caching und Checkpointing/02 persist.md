# `DataFrame.persist()`

Legt das Storage-Level fest, mit dem der Inhalt des DataFrames nach der ersten Berechnung über Operationen hinweg persistiert wird. Ein neues Storage-Level kann nur zugewiesen werden, wenn der DataFrame noch keines gesetzt hat. Ohne Angabe wird `MEMORY_AND_DISK_DESER` verwendet.

## Signatur

```python
persist(storageLevel: StorageLevel = StorageLevel.MEMORY_AND_DISK_DESER)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `storageLevel` | `StorageLevel` | Storage-Level für die Persistierung. Standard ist `MEMORY_AND_DISK_DESER`. |

## Rückgabewert

`DataFrame`: Persistierter DataFrame.

## Hinweise

- Das Standard-Storage-Level wurde in Spark 3.0 auf `MEMORY_AND_DISK_DESER` geändert, um mit Scala übereinzustimmen.
- Gecachte Daten werden von allen Spark-Sessions auf dem Cluster gemeinsam genutzt.

> **Serverless-Kompatibilität:** Databricks empfiehlt, auf `DataFrame.persist()` zu verzichten, da es nicht mit der Serverless-Compute-Architektur von Databricks kompatibel ist. Wenn die Wiederverwendung teuer ist, Zwischenergebnisse stattdessen in eine Delta-Tabelle materialisieren.

## Beispiel

```python
df = spark.range(1)
df.persist()
# DataFrame[id: bigint]

df.explain()
# == Physical Plan ==
# InMemoryTableScan ...

from pyspark.storagelevel import StorageLevel
df.persist(StorageLevel.DISK_ONLY)
# DataFrame[id: bigint]
```

Siehe auch [`cache`](01%20cache.md), [`unpersist`](03%20unpersist.md), [`storageLevel`](04%20storageLevel.md).

## Quellen

- DataFrame.persist: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/persist

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
