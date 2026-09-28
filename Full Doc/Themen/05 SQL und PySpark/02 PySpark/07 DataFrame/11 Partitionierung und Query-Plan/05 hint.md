# `DataFrame.hint()`

Gibt einen Hint (Optimierungshinweis) für den aktuellen DataFrame an, z. B. `broadcast` für Joins.

## Signatur

```python
hint(name: str, *parameters: Union["PrimitiveType", "Column", List["PrimitiveType"]])
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `name` | `str` | Name des Hints. |
| `parameters` | `str`, `list`, `float` oder `int` | Optionale Parameter. |

## Rückgabewert

`DataFrame`: DataFrame mit Hint.

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df2 = spark.createDataFrame([Row(height=80, name="Tom"), Row(height=85, name="Bob")])
df.join(df2, "name").explain()
# == Physical Plan ==
# ...
# ... +- SortMergeJoin ...
# ...

df.join(df2.hint("broadcast"), "name").explain()
# == Physical Plan ==
# ...
# ... +- BroadcastHashJoin ...
# ...
```

## Quellen

- DataFrame.hint: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/hint

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
