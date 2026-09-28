# `DataFrame.createGlobalTempView()`

Erstellt eine globale temporäre View aus diesem DataFrame.

## Signatur

```python
createGlobalTempView(name: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `name` | `str` | Name der View. |

## Hinweise

Die Lebensdauer dieser temporären View ist an die Spark-Anwendung gebunden. Existiert der View-Name bereits im Katalog, wird eine `TempTableAlreadyExistsException` ausgelöst. Globale temporäre Views liegen im Schema `global_temp`.

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.createGlobalTempView("people")
df2 = spark.sql("SELECT * FROM global_temp.people")
df2.show()
# +---+-----+
# |age| name|
# +---+-----+
# |  2|Alice|
# |  5|  Bob|
# +---+-----+

df.createGlobalTempView("people")
# Traceback (most recent call last):
# ...
# AnalysisException: "Temporary table 'people' already exists;"

spark.catalog.dropGlobalTempView("people")
# True
```

Siehe auch [`createOrReplaceGlobalTempView`](04%20createOrReplaceGlobalTempView.md), [`createTempView`](01%20createTempView.md).

## Quellen

- DataFrame.createGlobalTempView: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/createGlobalTempView

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
