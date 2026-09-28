# `DataFrame.sameSemantics()`

Gibt `True` zurück, wenn die logischen Query-Pläne beider DataFrames gleich sind und daher dieselben Ergebnisse liefern.

## Signatur

```python
sameSemantics(other: "DataFrame")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `other` | `DataFrame` | Der andere DataFrame, mit dem verglichen wird. |

## Rückgabewert

`bool`: Ob die beiden DataFrames gleich sind.

## Hinweise

- Der Gleichheitsvergleich ist vereinfacht: Kosmetische Unterschiede wie Attributnamen werden toleriert.
- Die API vergleicht sehr schnell, kann aber für DataFrames, die dieselben Ergebnisse liefern (etwa aus unterschiedlichen Plänen), trotzdem `False` zurückgeben. Solche False Negatives können z. B. beim Caching nützlich sein.
- Dies ist eine Developer-API.

## Beispiel

```python
df1 = spark.range(10)
df2 = spark.range(10)
df1.withColumn("col1", df1.id * 2).sameSemantics(df2.withColumn("col1", df2.id * 2))
# True
df1.withColumn("col1", df1.id * 2).sameSemantics(df2.withColumn("col1", df2.id + 2))
# False
df1.withColumn("col1", df1.id * 2).sameSemantics(df2.withColumn("col0", df2.id * 2))
# True
```

Siehe auch [`semanticHash`](08%20semanticHash.md).

## Quellen

- DataFrame.sameSemantics: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/sameSemantics

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
