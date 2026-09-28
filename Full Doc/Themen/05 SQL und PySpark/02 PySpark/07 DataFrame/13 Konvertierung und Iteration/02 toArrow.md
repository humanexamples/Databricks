# `DataFrame.toArrow()`

Gibt den Inhalt dieses DataFrames als PyArrow-`pyarrow.Table` zurück.

*Hinzugefügt in Databricks Runtime 15.3*

## Signatur

```python
toArrow()
```

## Rückgabewert

`pyarrow.Table`

## Hinweise

- Nur verwenden, wenn die resultierende `pyarrow.Table` voraussichtlich klein ist, da alle Daten in den Speicher des Drivers geladen werden.
- Nur verfügbar, wenn PyArrow installiert und verfügbar ist.
- Dies ist eine Developer-API.

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.coalesce(1).toArrow()
# pyarrow.Table
# age: int64
# name: string
# ----
# age: [[2,5]]
# name: [["Alice","Bob"]]
```

Siehe auch [`toPandas`](01%20toPandas.md).

## Quellen

- DataFrame.toArrow: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/toArrow

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
