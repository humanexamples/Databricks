# `DataFrame.union()`

Gibt einen neuen DataFrame mit der Vereinigung der Zeilen dieses und eines anderen DataFrames zurück.

## Signatur

```python
union(other: "DataFrame")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `other` | `DataFrame` | Der andere DataFrame, der vereinigt wird. |

## Rückgabewert

`DataFrame`: Neuer DataFrame mit den kombinierten Zeilen und den entsprechenden Spalten.

## Hinweise

- Die Methode führt eine Vereinigung der Zeilen beider `DataFrame`-Objekte im SQL-Stil durch – **ohne** automatische Deduplizierung (entspricht `UNION ALL`).
- Zur Deduplizierung [`distinct`](07%20distinct.md) verwenden.
- Spalten werden **nach Position** (nicht nach Name) aufgelöst, wie in SQL üblich. Für namensbasierte Auflösung [`unionByName`](02%20unionByName.md) verwenden.

## Beispiel

```python
df1 = spark.createDataFrame([(1, 'A'), (2, 'B')], ['id', 'value'])
df2 = spark.createDataFrame([(3, 'C'), (4, 'D')], ['id', 'value'])
df3 = df1.union(df2)
df3.show()
# +---+-----+
# | id|value|
# +---+-----+
# |  1|    A|
# |  2|    B|
# |  3|    C|
# |  4|    D|
# +---+-----+

df1 = spark.createDataFrame([(1, 'A'), (2, 'B'), (3, 'C')], ['id', 'value'])
df2 = spark.createDataFrame([(3, 'C'), (4, 'D')], ['id', 'value'])
df3 = df1.union(df2).distinct().sort("id")
df3.show()
# +---+-----+
# | id|value|
# +---+-----+
# |  1|    A|
# |  2|    B|
# |  3|    C|
# |  4|    D|
# +---+-----+
```

## Quellen

- DataFrame.union: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/union

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
