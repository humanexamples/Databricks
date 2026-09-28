# `DataFrame.isLocal()`

Gibt `True` zurück, wenn die Methoden `collect` und `take` lokal (ohne Spark-Executors) ausgeführt werden können.

## Signatur

```python
isLocal()
```

## Rückgabewert

`bool`

## Beispiel

```python
df = spark.sql("SHOW TABLES")
df.isLocal()
# True
```

## Quellen

- DataFrame.isLocal: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/isLocal

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
