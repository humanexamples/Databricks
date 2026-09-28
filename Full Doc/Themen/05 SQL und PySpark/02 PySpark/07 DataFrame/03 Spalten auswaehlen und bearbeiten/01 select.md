# `DataFrame.select()`

Projiziert eine Menge von Ausdrücken und gibt einen neuen DataFrame zurück.

## Signatur

```python
select(*cols: "ColumnOrName")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `cols` | `str`, `Column` oder `list` | Spaltennamen (String) oder Ausdrücke (`Column`). Ist einer der Spaltennamen `'*'`, wird er zu allen Spalten des aktuellen DataFrames expandiert. |

## Rückgabewert

`DataFrame`: DataFrame mit einer Teilmenge (oder allen) Spalten.

## Beispiel

```python
df = spark.createDataFrame([
    (2, "Alice"), (5, "Bob")], schema=["age", "name"])

df.select('*').show()
# +---+-----+
# |age| name|
# +---+-----+
# |  2|Alice|
# |  5|  Bob|
# +---+-----+

df.select(df.name, (df.age + 10).alias('age')).show()
# +-----+---+
# | name|age|
# +-----+---+
# |Alice| 12|
# |  Bob| 15|
# +-----+---+
```

Siehe auch [`selectExpr`](02%20selectExpr.md), [`withColumn`](04%20withColumn.md).

## Quellen

- DataFrame.select: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/select

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
