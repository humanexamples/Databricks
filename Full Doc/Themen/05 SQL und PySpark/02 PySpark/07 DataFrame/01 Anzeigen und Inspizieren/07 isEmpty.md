# `DataFrame.isEmpty()`

Prüft, ob der DataFrame leer ist, und gibt einen booleschen Wert zurück.

## Signatur

```python
isEmpty()
```

## Rückgabewert

`bool`: `True`, wenn der DataFrame leer ist, sonst `False`.

## Hinweise

Ein leerer DataFrame hat keine Zeilen. Er kann Spalten haben, aber keine Daten.

## Beispiel

```python
df_empty = spark.createDataFrame([], 'a STRING')
df_empty.isEmpty()
# True

df_non_empty = spark.createDataFrame(["a"], 'STRING')
df_non_empty.isEmpty()
# False

df_nulls = spark.createDataFrame([(None, None)], 'a STRING, b INT')
df_nulls.isEmpty()
# False

df_no_rows = spark.createDataFrame([], 'id INT, value STRING')
df_no_rows.isEmpty()
# True
```

## Quellen

- DataFrame.isEmpty: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/isEmpty

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
