# `DataFrame.createOrReplaceTempView()`

Erstellt oder ersetzt eine lokale temporäre View aus diesem DataFrame.

## Signatur

```python
createOrReplaceTempView(name: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `name` | `str` | Name der View. |

## Hinweise

Die Lebensdauer dieser temporären Tabelle ist an die `SparkSession` gebunden, mit der dieser DataFrame erstellt wurde.

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.createOrReplaceTempView("people")

df2 = df.filter(df.age > 3)
df2.createOrReplaceTempView("people")
df3 = spark.sql("SELECT * FROM people")
assert sorted(df3.collect()) == sorted(df2.collect())

spark.catalog.dropTempView("people")
# True
```

Siehe auch [`createTempView`](01%20createTempView.md), [`createOrReplaceGlobalTempView`](04%20createOrReplaceGlobalTempView.md).

## Quellen

- DataFrame.createOrReplaceTempView: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/createOrReplaceTempView

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
