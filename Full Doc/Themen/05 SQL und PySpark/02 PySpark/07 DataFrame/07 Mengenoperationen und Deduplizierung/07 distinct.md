# `DataFrame.distinct()`

Gibt einen neuen DataFrame mit den eindeutigen (distinct) Zeilen dieses DataFrames zurück.

## Signatur

```python
distinct()
```

## Rückgabewert

`DataFrame`: DataFrame mit eindeutigen Datensätzen.

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (23, "Alice")], ["age", "name"])
df.distinct().show()
# +---+-----+
# |age| name|
# +---+-----+
# | 14|  Tom|
# | 23|Alice|
# +---+-----+

df.distinct().count()
# 2

df = spark.createDataFrame(
    [(14, "Tom", "M"), (23, "Alice", "F"), (23, "Alice", "F"), (14, "Tom", "M")],
    ["age", "name", "gender"])
df.distinct().show()
# +---+-----+------+
# |age| name|gender|
# +---+-----+------+
# | 14|  Tom|     M|
# | 23|Alice|     F|
# +---+-----+------+
```

Siehe auch [`dropDuplicates`](08%20dropDuplicates.md).

## Quellen

- DataFrame.distinct: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/distinct

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
