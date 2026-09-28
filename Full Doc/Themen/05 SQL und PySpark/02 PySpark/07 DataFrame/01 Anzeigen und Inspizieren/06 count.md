# `DataFrame.count()`

Gibt die Anzahl der Zeilen dieses DataFrames zurück.

## Signatur

```python
count()
```

## Rückgabewert

`int`: Anzahl der Zeilen.

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])

df.count()
# 3
```

## Quellen

- DataFrame.count: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/count

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
