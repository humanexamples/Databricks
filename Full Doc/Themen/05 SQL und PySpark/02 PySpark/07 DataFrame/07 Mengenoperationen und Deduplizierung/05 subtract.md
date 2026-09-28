# `DataFrame.subtract()`

Gibt einen neuen DataFrame mit den Zeilen zurück, die in diesem, aber nicht im anderen DataFrame vorkommen.

## Signatur

```python
subtract(other: "DataFrame")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `other` | `DataFrame` | Der andere DataFrame, der abgezogen wird. |

## Rückgabewert

`DataFrame`: DataFrame nach der Subtraktion.

## Hinweise

Entspricht `EXCEPT DISTINCT` in SQL.

## Beispiel

```python
df1 = spark.createDataFrame([("a", 1), ("a", 1), ("b", 3), ("c", 4)], ["C1", "C2"])
df2 = spark.createDataFrame([("a", 1), ("a", 1), ("b", 3)], ["C1", "C2"])
result_df = df1.subtract(df2)
result_df.show()
# +---+---+
# | C1| C2|
# +---+---+
# |  c|  4|
# +---+---+

df1 = spark.createDataFrame([(1, "A"), (2, "B")], ["id", "value"])
df2 = spark.createDataFrame([(2, "B"), (3, "C")], ["id", "value"])
result_df = df1.subtract(df2)
result_df.show()
# +---+-----+
# | id|value|
# +---+-----+
# |  1|    A|
# +---+-----+
```

Siehe auch [`exceptAll`](06%20exceptAll.md).

## Quellen

- DataFrame.subtract: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/subtract

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
