# `DataFrame.dtypes` (Eigenschaft)

Gibt alle Spaltennamen und ihre Datentypen als Liste zurück.

## Rückgabewert

`list` (von Tupeln `(Spaltenname, Typ)`)

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df.dtypes
# [('age', 'bigint'), ('name', 'string')]
```

Siehe auch [`schema`](05%20schema.md), [`printSchema`](02%20printSchema.md).

## Quellen

- DataFrame.dtypes: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/dtypes

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
