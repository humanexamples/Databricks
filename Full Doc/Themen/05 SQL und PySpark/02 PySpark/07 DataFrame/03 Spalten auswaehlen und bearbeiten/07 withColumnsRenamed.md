# `DataFrame.withColumnsRenamed()`

Gibt einen neuen DataFrame zurück, in dem mehrere Spalten umbenannt sind. Enthält das Schema die Spaltennamen nicht, passiert nichts (No-op).

## Signatur

```python
withColumnsRenamed(colsMap: Dict[str, str])
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `colsMap` | `dict` | Ein `dict` aus bestehenden Spaltennamen und den gewünschten neuen Namen. Aktuell wird nur eine einzelne Map unterstützt. |

## Rückgabewert

`DataFrame`: DataFrame mit umbenannten Spalten.

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])

df.withColumnsRenamed({"age": "age2"}).show()
# +----+-----+
# |age2| name|
# +----+-----+
# |   2|Alice|
# |   5|  Bob|
# +----+-----+

df.withColumnsRenamed({"age": "age2", "name": "name2"}).show()
# +----+-----+
# |age2|name2|
# +----+-----+
# |   2|Alice|
# |   5|  Bob|
# +----+-----+

df.withColumnsRenamed({"non_existing": "new_name"}).show()
# +---+-----+
# |age| name|
# +---+-----+
# |  2|Alice|
# |  5|  Bob|
# +---+-----+
```

Siehe auch [`withColumnRenamed`](06%20withColumnRenamed.md), [`toDF`](08%20toDF.md).

## Quellen

- DataFrame.withColumnsRenamed: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/withColumnsRenamed

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
