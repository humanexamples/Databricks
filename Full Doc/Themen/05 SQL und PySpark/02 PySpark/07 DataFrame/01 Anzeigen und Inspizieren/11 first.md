# `DataFrame.first()`

Gibt die erste Zeile als `Row` zurück.

## Signatur

```python
first()
```

## Rückgabewert

`Row`: Die erste Zeile, falls der DataFrame nicht leer ist, sonst `None`.

## Beispiel

```python
df = spark.createDataFrame([
    (2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.first()
# Row(age=2, name='Alice')
```

Siehe auch [`head`](10%20head.md), [`take`](09%20take.md).

## Quellen

- DataFrame.first: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/first

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
