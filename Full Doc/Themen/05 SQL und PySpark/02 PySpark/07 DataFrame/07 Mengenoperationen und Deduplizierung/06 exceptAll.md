# `DataFrame.exceptAll()`

Gibt einen neuen DataFrame mit den Zeilen zurück, die in diesem, aber nicht im anderen DataFrame vorkommen – Duplikate bleiben erhalten.

## Signatur

```python
exceptAll(other: "DataFrame")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `other` | `DataFrame` | Der andere DataFrame, mit dem verglichen wird. |

## Rückgabewert

`DataFrame`

## Hinweise

Entspricht `EXCEPT ALL` in SQL. Wie in SQL üblich, löst diese Funktion Spalten **nach Position** (nicht nach Name) auf.

## Beispiel

```python
df1 = spark.createDataFrame(
        [("a", 1), ("a", 1), ("a", 1), ("a", 2), ("b",  3), ("c", 4)], ["C1", "C2"])
df2 = spark.createDataFrame([("a", 1), ("b", 3)], ["C1", "C2"])
df1.exceptAll(df2).show()
# +---+---+
# | C1| C2|
# +---+---+
# |  a|  1|
# |  a|  1|
# |  a|  2|
# |  c|  4|
# +---+---+
```

Siehe auch [`subtract`](05%20subtract.md).

## Quellen

- DataFrame.exceptAll: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/exceptAll

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
