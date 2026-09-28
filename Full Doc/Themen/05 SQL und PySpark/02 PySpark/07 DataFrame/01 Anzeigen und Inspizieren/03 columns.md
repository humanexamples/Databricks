# `DataFrame.columns` (Eigenschaft)

Liefert die Namen aller Spalten des `DataFrame` als Liste. Die Reihenfolge der Namen entspricht der Spaltenreihenfolge im DataFrame.

## Rückgabewert

`list`

## Beispiele

Spaltennamen eines DataFrames abrufen:

```python
df = spark.createDataFrame(
    [(14, "Tom", "CA"), (23, "Alice", "NY"), (16, "Bob", "TX")],
    ["age", "name", "state"]
)
df.columns
# ['age', 'name', 'state']
```

Spaltennamen nutzen, um bestimmte Spalten zu projizieren:

```python
selected_cols = [col for col in df.columns if col != "age"]
df.select(selected_cols).show()
# +-----+-----+
# | name|state|
# +-----+-----+
# |  Tom|   CA|
# |Alice|   NY|
# |  Bob|   TX|
# +-----+-----+
```

Prüfen, ob eine bestimmte Spalte im DataFrame existiert:

```python
"state" in df.columns
# True
"salary" in df.columns
# False
```

## Quellen

- DataFrame.columns: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/columns

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
