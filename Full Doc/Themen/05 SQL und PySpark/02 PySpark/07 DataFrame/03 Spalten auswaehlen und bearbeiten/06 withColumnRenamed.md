# `DataFrame.withColumnRenamed()`

Gibt einen neuen DataFrame zurück, in dem eine bestehende Spalte umbenannt ist. Enthält das Schema den Spaltennamen nicht, passiert nichts (No-op).

## Signatur

```python
withColumnRenamed(existing: str, new: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `existing` | `str` | Name der bestehenden, umzubenennenden Spalte. |
| `new` | `str` | Neuer Name der Spalte. |

## Rückgabewert

`DataFrame`: Neuer DataFrame mit umbenannter Spalte.

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])

df.withColumnRenamed("age", "age2").show()
# +----+-----+
# |age2| name|
# +----+-----+
# |   2|Alice|
# |   5|  Bob|
# +----+-----+

df.withColumnRenamed("non_existing", "new_name").show()
# +---+-----+
# |age| name|
# +---+-----+
# |  2|Alice|
# |  5|  Bob|
# +---+-----+

df.withColumnRenamed("age", "age2").withColumnRenamed("name", "name2").show()
# +----+-----+
# |age2|name2|
# +----+-----+
# |   2|Alice|
# |   5|  Bob|
# +----+-----+
```

Siehe auch [`withColumnsRenamed`](07%20withColumnsRenamed.md).

## Quellen

- DataFrame.withColumnRenamed: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/withColumnRenamed

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
