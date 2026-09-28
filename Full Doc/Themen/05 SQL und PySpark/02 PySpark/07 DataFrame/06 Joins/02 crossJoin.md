# `DataFrame.crossJoin()`

Gibt das kartesische Produkt mit einem anderen DataFrame zurück.

## Signatur

```python
crossJoin(other: "DataFrame")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `other` | `DataFrame` | Rechte Seite des kartesischen Produkts. |

## Rückgabewert

`DataFrame`: Gejointer DataFrame.

## Beispiel

```python
from pyspark.sql import Row
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df2 = spark.createDataFrame(
    [Row(height=80, name="Tom"), Row(height=85, name="Bob")])
df.crossJoin(df2.select("height")).select("age", "name", "height"
    ).orderBy("age", "name", "height").show()
# +---+-----+------+
# |age| name|height|
# +---+-----+------+
# | 14|  Tom|    80|
# | 14|  Tom|    85|
# | 16|  Bob|    80|
# | 16|  Bob|    85|
# | 23|Alice|    80|
# | 23|Alice|    85|
# +---+-----+------+
```

Siehe auch [`join`](01%20join.md).

## Quellen

- DataFrame.crossJoin: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/crossJoin

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
