# `DataFrame.crosstab()`

Berechnet eine paarweise Häufigkeitstabelle der angegebenen Spalten, auch Kontingenztabelle genannt. Die erste Spalte jeder Zeile enthält die eindeutigen Werte von `col1`, die Spaltennamen sind die eindeutigen Werte von `col2`. Die erste Spalte heißt `$col1_$col2`. Kombinationen ohne Vorkommen erhalten die Anzahl 0. `DataFrame.crosstab` und `DataFrameStatFunctions.crosstab` sind Aliase.

## Signatur

```python
crosstab(col1: str, col2: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `col1` | `str` | Name der ersten Spalte. Ihre eindeutigen Werte bilden jeweils das erste Element jeder Zeile. |
| `col2` | `str` | Name der zweiten Spalte. Ihre eindeutigen Werte bilden die Spaltennamen des DataFrames. |

## Rückgabewert

`DataFrame`: Häufigkeitsmatrix der beiden Spalten.

## Beispiel

```python
df = spark.createDataFrame([(1, 11), (1, 11), (3, 10), (4, 8), (4, 8)], ["c1", "c2"])
df.crosstab("c1", "c2").sort("c1_c2").show()
# +-----+---+---+---+
# |c1_c2| 10| 11|  8|
# +-----+---+---+---+
# |    1|  0|  2|  0|
# |    3|  1|  0|  0|
# |    4|  0|  0|  2|
# +-----+---+---+---+
```

## Quellen

- DataFrame.crosstab: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/crosstab

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
