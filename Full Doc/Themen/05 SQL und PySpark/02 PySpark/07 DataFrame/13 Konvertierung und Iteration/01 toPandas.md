# `DataFrame.toPandas()`

Gibt den Inhalt dieses DataFrames als pandas-`pandas.DataFrame` zurück.

## Signatur

```python
toPandas()
```

## Rückgabewert

`pandas.DataFrame`

## Hinweise

- Nur verwenden, wenn der resultierende `pandas.DataFrame` voraussichtlich klein ist, da alle Daten in den Speicher des Drivers geladen werden.
- Die Verwendung mit `spark.sql.execution.arrow.pyspark.enabled=True` ist experimentell.
- Nur verfügbar, wenn pandas installiert und verfügbar ist.

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.toPandas()
#    age   name
# 0    2  Alice
# 1    5    Bob
```

Siehe auch [`toArrow`](02%20toArrow.md), [`pandas_api`](03%20pandas_api.md).

## Quellen

- DataFrame.toPandas: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/toPandas

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
