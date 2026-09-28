# `DataFrame.sparkSession` (Eigenschaft)

Gibt die Spark-Session zurück, die diesen DataFrame erstellt hat.

## Rückgabewert

`SparkSession`

## Beispiel

```python
df = spark.range(1)
type(df.sparkSession)
# <class '...session.SparkSession'>
```

## Quellen

- DataFrame.sparkSession: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/sparkSession

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
