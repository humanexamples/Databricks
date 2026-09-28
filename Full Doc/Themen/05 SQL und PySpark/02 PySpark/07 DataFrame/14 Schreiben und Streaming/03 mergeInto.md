# `DataFrame.mergeInto()`

Führt eine Menge von Updates, Inserts und Deletes auf Basis einer Quelltabelle (dieses DataFrames) in eine Zieltabelle zusammen (MERGE).

## Signatur

```python
mergeInto(table: str, condition: Column)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `table` | `str` | Name der Zieltabelle, in die gemergt wird. |
| `condition` | `Column` | Bedingung, die festlegt, ob eine Zeile der Zieltabelle zu einer Zeile des Quell-DataFrames passt. |

## Rückgabewert

`MergeIntoWriter`: Writer, mit dem anschließend festgelegt wird, wie der Quell-DataFrame in die Zieltabelle gemergt wird (z. B. `whenMatched()`, `whenNotMatched()`, dann `merge()`).

## Beispiel

```python
from pyspark.sql.functions import expr
source = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["id", "name"])
(source.mergeInto("target", "id")
    .whenMatched().update({ "name": source.name })
    .whenNotMatched().insertAll()
    .whenNotMatchedBySource().delete()
    .merge())
```

Siehe auch [`writeTo`](02%20writeTo.md).

## Quellen

- DataFrame.mergeInto: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/mergeInto

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
