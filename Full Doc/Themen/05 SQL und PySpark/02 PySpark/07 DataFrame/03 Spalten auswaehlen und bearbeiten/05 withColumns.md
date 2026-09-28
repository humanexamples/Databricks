# `DataFrame.withColumns()`

Gibt einen neuen DataFrame zurück, in dem mehrere Spalten hinzugefügt bzw. bestehende Spalten gleichen Namens ersetzt werden.

## Signatur

```python
withColumns(*colsMap: Dict[str, Column])
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `colsMap` | `dict` | Ein `dict` aus Spaltenname und `Column`. Aktuell wird nur eine einzelne Map unterstützt. |

## Rückgabewert

`DataFrame`: DataFrame mit neuen bzw. ersetzten Spalten.

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.withColumns({'age2': df.age + 2, 'age3': df.age + 3}).show()
# +---+-----+----+----+
# |age| name|age2|age3|
# +---+-----+----+----+
# |  2|Alice|   4|   5|
# |  5|  Bob|   7|   8|
# +---+-----+----+----+
```

Siehe auch [`withColumn`](04%20withColumn.md).

## Quellen

- DataFrame.withColumns: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/withColumns

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
