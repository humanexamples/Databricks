# `DataFrame.intersectAll()`

Gibt einen neuen DataFrame mit den Zeilen zurück, die sowohl in diesem als auch im anderen DataFrame vorkommen – Duplikate bleiben erhalten.

## Signatur

```python
intersectAll(other: "DataFrame")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `other` | `DataFrame` | Der andere DataFrame, mit dem kombiniert wird. |

## Rückgabewert

`DataFrame`: Kombinierter DataFrame.

## Hinweise

Entspricht `INTERSECT ALL` in SQL. Wie in SQL üblich, löst diese Funktion Spalten **nach Position** (nicht nach Name) auf.

## Beispiel

```python
df1 = spark.createDataFrame([("a", 1), ("a", 1), ("b", 3), ("c", 4)], ["C1", "C2"])
df2 = spark.createDataFrame([("a", 1), ("a", 1), ("b", 3)], ["C1", "C2"])
result_df = df1.intersectAll(df2).sort("C1", "C2")
result_df.show()
# +---+---+
# | C1| C2|
# +---+---+
# |  a|  1|
# |  a|  1|
# |  b|  3|
# +---+---+

df1 = spark.createDataFrame([(1, "A"), (2, "B")], ["id", "value"])
df2 = spark.createDataFrame([(2, "B"), (3, "C")], ["id", "value"])
result_df = df1.intersectAll(df2).sort("id", "value")
result_df.show()
# +---+-----+
# | id|value|
# +---+-----+
# |  2|    B|
# +---+-----+
```

Siehe auch [`intersect`](03%20intersect.md).

## Quellen

- DataFrame.intersectAll: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/intersectAll

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
