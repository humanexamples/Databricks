# `DataFrame.createTempView()`

Erstellt eine lokale temporäre View aus diesem DataFrame.

## Signatur

```python
createTempView(name: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `name` | `str` | Name der View. |

## Hinweise

Die Lebensdauer dieser temporären Tabelle ist an die `SparkSession` gebunden, mit der dieser DataFrame erstellt wurde. Existiert der View-Name bereits im Katalog, wird eine `TempTableAlreadyExistsException` ausgelöst – für idempotentes Anlegen [`createOrReplaceTempView`](02%20createOrReplaceTempView.md) verwenden.

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.createTempView("people")
spark.sql("SELECT * FROM people").show()
# +---+-----+
# |age| name|
# +---+-----+
# |  2|Alice|
# |  5|  Bob|
# +---+-----+

df.createTempView("people")  # doctest: +IGNORE_EXCEPTION_DETAIL
# Traceback (most recent call last):
# ...
# AnalysisException: "Temporary table 'people' already exists;"

spark.catalog.dropTempView("people")
# True
df.createTempView("people")

df1 = spark.createDataFrame([(1, "John"), (2, "Jane")], schema=["id", "name"])
df2 = spark.createDataFrame([(3, "Jake"), (4, "Jill")], schema=["id", "name"])
df1.createTempView("table1")
df2.createTempView("table2")
result_df = spark.table("table1").union(spark.table("table2"))
result_df.show()
# +---+----+
# | id|name|
# +---+----+
# |  1|John|
# |  2|Jane|
# |  3|Jake|
# |  4|Jill|
# +---+----+
```

## Quellen

- DataFrame.createTempView: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/createTempView

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
