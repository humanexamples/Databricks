# `DataFrame.filter()`

Filtert Zeilen anhand der angegebenen Bedingung.

## Signatur

```python
filter(condition: Union[Column, str])
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `condition` | `Column` oder `str` | Eine `Column` vom Typ `BooleanType` oder ein String mit SQL-Ausdrücken. |

## Rückgabewert

`DataFrame`: Neuer DataFrame mit den Zeilen, die die Bedingung erfüllen.

## Beispiel

```python
df = spark.createDataFrame([
    (2, "Alice", "Math"), (5, "Bob", "Physics"), (7, "Charlie", "Chemistry")],
    schema=["age", "name", "subject"])

df.filter(df.age > 3).show()
# +---+-------+---------+
# |age|   name|  subject|
# +---+-------+---------+
# |  5|    Bob|  Physics|
# |  7|Charlie|Chemistry|
# +---+-------+---------+

df.where(df.age == 2).show()
# +---+-----+-------+
# |age| name|subject|
# +---+-----+-------+
# |  2|Alice|   Math|
# +---+-----+-------+

df.filter("age > 3").show()
# +---+-------+---------+
# |age|   name|  subject|
# +---+-------+---------+
# |  5|    Bob|  Physics|
# |  7|Charlie|Chemistry|
# +---+-------+---------+

df.filter((df.age > 3) & (df.subject == "Physics")).show()
# +---+----+-------+
# |age|name|subject|
# +---+----+-------+
# |  5| Bob|Physics|
# +---+----+-------+
```

Siehe auch [`where`](02%20where.md) (Alias).

## Quellen

- DataFrame.filter: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/filter

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
