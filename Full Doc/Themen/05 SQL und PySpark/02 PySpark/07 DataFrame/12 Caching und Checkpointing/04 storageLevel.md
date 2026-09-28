# `DataFrame.storageLevel` (Eigenschaft)

Liefert das aktuelle Storage-Level des `DataFrame`.

## Rückgabewert

`StorageLevel`

> **Serverless-Kompatibilität:** Databricks empfiehlt, auf `df.cache()` und `df.persist()` zu verzichten, da sie nicht mit der Serverless-Compute-Architektur von Databricks kompatibel sind. Zwischenergebnisse stattdessen in Delta-Tabellen materialisieren.

## Beispiel

```python
df1 = spark.range(10)
df1.storageLevel
# StorageLevel(False, False, False, False, 1)
df1.cache().storageLevel
# StorageLevel(True, True, False, True, 1)

df2 = spark.range(5)
df2.persist(StorageLevel.DISK_ONLY_2).storageLevel
# StorageLevel(True, False, False, False, 2)
```

Siehe auch [`cache`](01%20cache.md), [`persist`](02%20persist.md), [`unpersist`](03%20unpersist.md).

## Quellen

- DataFrame.storageLevel: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/storageLevel

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
