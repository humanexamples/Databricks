# `DataFrame.cache()`

Persistiert den DataFrame mit dem Standard-Storage-Level (`MEMORY_AND_DISK_DESER`).

## Signatur

```python
cache()
```

## Rückgabewert

`DataFrame`: Gecachter DataFrame.

## Hinweise

- Das Standard-Storage-Level wurde in Spark 3.0 auf `MEMORY_AND_DISK_DESER` geändert, um mit Scala übereinzustimmen.
- Gecachte Daten werden von allen Spark-Sessions auf dem Cluster gemeinsam genutzt.

> **Serverless-Kompatibilität:** Databricks empfiehlt, auf `DataFrame.cache()` zu verzichten, da es nicht mit der Serverless-Compute-Architektur von Databricks kompatibel ist. Zwischenergebnisse stattdessen in eine Delta-Tabelle materialisieren.

## Beispiel

```python
df = spark.range(1)
df.cache()
# DataFrame[id: bigint]

df.explain()
# == Physical Plan ==
# InMemoryTableScan ...
```

Siehe auch [`persist`](02%20persist.md), [`unpersist`](03%20unpersist.md), [`storageLevel`](04%20storageLevel.md).

## Quellen

- DataFrame.cache: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/cache

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
