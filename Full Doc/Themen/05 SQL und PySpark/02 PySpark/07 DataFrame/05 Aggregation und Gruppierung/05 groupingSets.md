# `DataFrame.groupingSets()`

Erstellt eine mehrdimensionale Aggregation für den aktuellen DataFrame über die angegebenen Grouping Sets, auf der Aggregationen ausgeführt werden können.

## Signatur

```python
groupingSets(groupingSets: Sequence[Sequence["ColumnOrName"]], *cols: "ColumnOrName")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `groupingSets` | Sequenz von Sequenzen aus Spalten oder `str` | Die einzelnen Spaltenmengen, nach denen gruppiert wird. |
| `cols` | `Column` oder `str` | Zusätzliche vom Benutzer angegebene Gruppierungsspalten. Diese erscheinen nach der Aggregation als Ausgabespalten. |

## Rückgabewert

`GroupedData`: Grouping Sets der Daten auf Basis der angegebenen Spalten.

## Beispiel

```python
from pyspark.sql import functions as sf
df = spark.createDataFrame([
    (100, 'Fremont', 'Honda Civic', 10),
    (100, 'Fremont', 'Honda Accord', 15),
    (100, 'Fremont', 'Honda CRV', 7),
    (200, 'Dublin', 'Honda Civic', 20),
    (200, 'Dublin', 'Honda Accord', 10),
    (200, 'Dublin', 'Honda CRV', 3),
    (300, 'San Jose', 'Honda Civic', 5),
    (300, 'San Jose', 'Honda Accord', 8)
], schema="id INT, city STRING, car_model STRING, quantity INT")

df.groupingSets(
    [("city", "car_model"), ("city",), ()],
    "city", "car_model"
).agg(sf.sum(sf.col("quantity")).alias("sum")).sort("city", "car_model").show()
# +--------+------------+---+
# |    city|   car_model|sum|
# +--------+------------+---+
# |    NULL|        NULL| 78|
# |  Dublin|        NULL| 33|
# |  Dublin|Honda Accord| 10|
# |  Dublin|   Honda CRV|  3|
# |  Dublin| Honda Civic| 20|
# | Fremont|        NULL| 32|
# | Fremont|Honda Accord| 15|
# | Fremont|   Honda CRV|  7|
# | Fremont| Honda Civic| 10|
# |San Jose|        NULL| 13|
# |San Jose|Honda Accord|  8|
# |San Jose| Honda Civic|  5|
# +--------+------------+---+
```

Siehe auch [`rollup`](03%20rollup.md), [`cube`](04%20cube.md).

## Quellen

- DataFrame.groupingSets: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/groupingSets

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
