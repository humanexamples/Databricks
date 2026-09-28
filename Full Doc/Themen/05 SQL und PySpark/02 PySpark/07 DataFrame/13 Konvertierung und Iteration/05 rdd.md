# `DataFrame.rdd` (Eigenschaft)

Gibt den Inhalt als `RDD` von `Row` zurück (nur im Classic-Modus, nicht mit Spark Connect).

## Rückgabewert

`RDD`

## Beispiel

```python
df = spark.range(1)
type(df.rdd)
# <class 'pyspark.core.rdd.RDD'>
```

## Quellen

- DataFrame.rdd: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/rdd

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
