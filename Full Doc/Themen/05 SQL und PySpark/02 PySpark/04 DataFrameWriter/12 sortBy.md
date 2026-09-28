# `DataFrameWriter.sortBy()`

Sortiert die Ausgabe innerhalb jedes Buckets nach den angegebenen Spalten. Wird ausschließlich in Kombination mit `bucketBy()` und `saveAsTable()` verwendet.

## Signatur

```python
sortBy(col, *cols)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `col` | `str`, `tuple` oder `list` | Ein Spaltenname oder eine Liste von Namen. |
| `*cols` | `str`, optional | Weitere Spaltennamen. Muss leer sein, falls `col` bereits eine Liste ist. |

## Rückgabewert

`DataFrameWriter`

## Beispiel

```python
spark.sql("DROP TABLE IF EXISTS sorted_bucketed_table")
spark.createDataFrame([
    (100, "Alice"), (120, "Alice"), (140, "Bob")],
    schema=["age", "name"]).write.bucketBy(1, "name").sortBy("age").mode(
    "overwrite").saveAsTable("sorted_bucketed_table")
spark.read.table("sorted_bucketed_table").sort("age").show()
# +---+------------+
# |age|        name|
# +---+------------+
# |100|Alice|
# |120|Alice|
# |140| Bob|
# +---+------------+
spark.sql("DROP TABLE sorted_bucketed_table")
```

## Quellen

- DataFrameWriter.sortBy: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/sortBy

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
