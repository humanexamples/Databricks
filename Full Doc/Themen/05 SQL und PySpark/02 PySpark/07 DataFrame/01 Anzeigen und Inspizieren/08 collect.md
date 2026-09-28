# `DataFrame.collect()`

Gibt alle Datensätze des DataFrames als Liste von `Row`-Objekten zurück.

## Signatur

```python
collect()
```

## Rückgabewert

`list`: Liste von `Row`-Objekten, von denen jedes eine Zeile des DataFrames darstellt.

## Hinweise

Diese Methode sollte nur verwendet werden, wenn die resultierende Liste voraussichtlich klein ist, da alle Daten in den Speicher des Drivers geladen werden.

## Beispiel

```python
df = spark.createDataFrame([(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df.collect()
# [Row(age=14, name='Tom'), Row(age=23, name='Alice'), Row(age=16, name='Bob')]

df.filter(df.age > 15).collect()
# [Row(age=23, name='Alice'), Row(age=16, name='Bob')]

df.select("name").collect()
# [Row(name='Tom'), Row(name='Alice'), Row(name='Bob')]

from pyspark.sql.functions import upper
df.select(upper(df.name)).collect()
# [Row(upper(name)='TOM'), Row(upper(name)='ALICE'), Row(upper(name)='BOB')]

rows = df.collect()
[row["name"] for row in rows]
# ['Tom', 'Alice', 'Bob']

[row.asDict() for row in rows]
# [{'age': 14, 'name': 'Tom'}, {'age': 23, 'name': 'Alice'}, {'age': 16, 'name': 'Bob'}]
```

Siehe auch [`take`](09%20take.md), [`head`](10%20head.md), [`toLocalIterator`](13%20toLocalIterator.md).

## Quellen

- DataFrame.collect: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/collect

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
