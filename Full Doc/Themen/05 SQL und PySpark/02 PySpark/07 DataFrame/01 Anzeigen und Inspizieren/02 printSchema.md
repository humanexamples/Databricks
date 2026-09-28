# `DataFrame.printSchema()`

Gibt das Schema in Baumform aus. Optional lässt sich bei verschachtelten Schemas festlegen, wie viele Ebenen ausgegeben werden.

## Signatur

```python
printSchema(level: Optional[int] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `level` | `int`, optional | Wie viele Ebenen bei verschachtelten Schemas ausgegeben werden. |

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df.printSchema()
# root
#  |-- age: long (nullable = true)
#  |-- name: string (nullable = true)

df = spark.createDataFrame([(1, (2, 2))], ["a", "b"])
df.printSchema(1)
# root
#  |-- a: long (nullable = true)
#  |-- b: struct (nullable = true)

df.printSchema(2)
# root
#  |-- a: long (nullable = true)
#  |-- b: struct (nullable = true)
#  |    |-- _1: long (nullable = true)
#  |    |-- _2: long (nullable = true)
```

Siehe auch [`schema`](05%20schema.md), [`dtypes`](04%20dtypes.md).

## Quellen

- DataFrame.printSchema: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/printSchema

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
