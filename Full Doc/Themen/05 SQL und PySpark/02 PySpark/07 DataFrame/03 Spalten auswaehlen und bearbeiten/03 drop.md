# `DataFrame.drop()`

Gibt einen neuen DataFrame ohne die angegebenen Spalten zurück. Enthält das Schema den bzw. die Spaltennamen nicht, passiert nichts (No-op).

## Signatur

```python
drop(*cols: "ColumnOrName")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `cols` | `str` oder `Column` | Name der zu entfernenden Spalte oder die `Column` selbst. |

## Rückgabewert

`DataFrame`: Neuer DataFrame ohne die angegebenen Spalten.

## Hinweise

Ist die Eingabe ein Spaltenname, wird er wörtlich und ohne weitere Interpretation behandelt. Andernfalls wird versucht, einen äquivalenten Ausdruck zu finden. Das Entfernen per Name `drop(colName)` hat daher eine andere Semantik als das direkte Entfernen der Spalte `drop(col(colName))`.

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df.drop('age').show()
# +-----+
# | name|
# +-----+
# |  Tom|
# |Alice|
# |  Bob|
# +-----+

df.drop(df.age).show()
# +-----+
# | name|
# +-----+
# |  Tom|
# |Alice|
# |  Bob|
# +-----+

df2 = spark.createDataFrame([(80, "Tom"), (85, "Bob")], ["height", "name"])
df.join(df2, df.name == df2.name).drop('name').sort('age').show()
# +---+------+
# |age|height|
# +---+------+
# | 14|    80|
# | 16|    85|
# +---+------+
```

## Quellen

- DataFrame.drop: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/drop

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
