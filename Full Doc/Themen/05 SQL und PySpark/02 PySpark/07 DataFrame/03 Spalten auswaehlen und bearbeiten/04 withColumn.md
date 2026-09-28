# `DataFrame.withColumn()`

Gibt einen neuen DataFrame zurück, in dem eine Spalte hinzugefügt oder eine bestehende Spalte gleichen Namens ersetzt wird.

## Signatur

```python
withColumn(colName: str, col: Column)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `colName` | `str` | Name der neuen Spalte. |
| `col` | `Column` | `Column`-Ausdruck für die neue Spalte. |

## Rückgabewert

`DataFrame`: DataFrame mit neuer bzw. ersetzter Spalte.

## Hinweise

Die Methode führt intern eine Projektion ein. Wird sie mehrfach aufgerufen – etwa in Schleifen, um mehrere Spalten hinzuzufügen –, können große Pläne entstehen, die Performanceprobleme und sogar eine `StackOverflowException` verursachen. Um das zu vermeiden, [`select`](01%20select.md) mit mehreren Spalten auf einmal (oder [`withColumns`](05%20withColumns.md)) verwenden.

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.withColumn('age2', df.age + 2).show()
# +---+-----+----+
# |age| name|age2|
# +---+-----+----+
# |  2|Alice|   4|
# |  5|  Bob|   7|
# +---+-----+----+
```

## Quellen

- DataFrame.withColumn: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/withColumn

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
