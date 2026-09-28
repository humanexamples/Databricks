# `DataFrame.unionByName()`

Gibt einen neuen DataFrame mit der Vereinigung der Zeilen dieses und eines anderen DataFrames zurück, wobei Spalten nach Namen zugeordnet werden.

## Signatur

```python
unionByName(other: "DataFrame", allowMissingColumns: bool = False)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `other` | `DataFrame` | Der andere DataFrame, der kombiniert wird. |
| `allowMissingColumns` | `bool`, optional, Standard `False` | Ob fehlende Spalten erlaubt sind. |

## Rückgabewert

`DataFrame`: Neuer DataFrame mit den kombinierten Zeilen und den entsprechenden Spalten beider DataFrames.

## Hinweise

Die Methode vereinigt beide Eingabe-DataFrames und löst Spalten **nach Namen** (statt nach Position) auf. Ist `allowMissingColumns` `True`, werden fehlende Spalten mit NULL aufgefüllt.

## Beispiel

```python
df1 = spark.createDataFrame([[1, 2, 3]], ["col0", "col1", "col2"])
df2 = spark.createDataFrame([[4, 5, 6]], ["col1", "col2", "col0"])
df1.unionByName(df2).show()
# +----+----+----+
# |col0|col1|col2|
# +----+----+----+
# |   1|   2|   3|
# |   6|   4|   5|
# +----+----+----+

df1 = spark.createDataFrame([[1, 2, 3]], ["col0", "col1", "col2"])
df2 = spark.createDataFrame([[4, 5, 6]], ["col1", "col2", "col3"])
df1.unionByName(df2, allowMissingColumns=True).show()
# +----+----+----+----+
# |col0|col1|col2|col3|
# +----+----+----+----+
# |   1|   2|   3|NULL|
# |NULL|   4|   5|   6|
# +----+----+----+----+
```

Siehe auch [`union`](01%20union.md).

## Quellen

- DataFrame.unionByName: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/unionByName

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
