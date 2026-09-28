# `DataFrame.intersect()`

Gibt einen neuen DataFrame mit den Zeilen zurück, die sowohl in diesem als auch im anderen DataFrame vorkommen. Duplikate werden entfernt; um Duplikate zu erhalten, [`intersectAll`](04%20intersectAll.md) verwenden.

## Signatur

```python
intersect(other: "DataFrame")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `other` | `DataFrame` | Der andere DataFrame, mit dem kombiniert wird. |

## Rückgabewert

`DataFrame`: Kombinierter DataFrame.

## Hinweise

Entspricht `INTERSECT` in SQL.

## Beispiel

```python
df1 = spark.createDataFrame([("a", 1), ("a", 1), ("b", 3), ("c", 4)], ["C1", "C2"])
df2 = spark.createDataFrame([("a", 1), ("a", 1), ("b", 3)], ["C1", "C2"])
result_df = df1.intersect(df2).sort("C1", "C2")
result_df.show()
# +---+---+
# | C1| C2|
# +---+---+
# |  a|  1|
# |  b|  3|
# +---+---+

df1 = spark.createDataFrame([(1, "A"), (2, "B")], ["id", "value"])
df2 = spark.createDataFrame([(2, "B"), (3, "C")], ["id", "value"])
result_df = df1.intersect(df2).sort("id", "value")
result_df.show()
# +---+-----+
# | id|value|
# +---+-----+
# |  2|    B|
# +---+-----+
```

## Quellen

- DataFrame.intersect: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/intersect

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
