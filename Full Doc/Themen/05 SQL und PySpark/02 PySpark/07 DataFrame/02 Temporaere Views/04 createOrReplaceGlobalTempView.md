# `DataFrame.createOrReplaceGlobalTempView()`

Erstellt oder ersetzt eine globale temporäre View mit dem angegebenen Namen.

## Signatur

```python
createOrReplaceGlobalTempView(name: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `name` | `str` | Name der View. |

## Hinweise

Die Lebensdauer dieser temporären View ist an die Spark-Anwendung gebunden.

> **Hinweis:** Databricks empfiehlt auf Serverless Compute session-bezogene temporäre Views ([`createOrReplaceTempView`](02%20createOrReplaceTempView.md)), da `global_temp`-Views dort nicht unterstützt werden.

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.createOrReplaceGlobalTempView("people")

df2 = df.filter(df.age > 3)
df2.createOrReplaceGlobalTempView("people")
df3 = spark.table("global_temp.people")
sorted(df3.collect()) == sorted(df2.collect())
# True

spark.catalog.dropGlobalTempView("people")
# True
```

## Quellen

- DataFrame.createOrReplaceGlobalTempView: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/createOrReplaceGlobalTempView

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
