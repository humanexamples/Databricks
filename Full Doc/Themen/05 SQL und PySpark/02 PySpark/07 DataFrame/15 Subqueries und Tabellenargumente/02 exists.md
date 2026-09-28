# `DataFrame.exists()`

Gibt ein `Column`-Objekt für eine EXISTS-Subquery zurück.

## Signatur

```python
exists()
```

## Rückgabewert

`Column`: Ein `Column`-Objekt, das eine EXISTS-Subquery repräsentiert.

## Hinweise

`exists` erzeugt eine boolesche Spalte, die prüft, ob in einer Subquery zugehörige Datensätze vorhanden sind. Innerhalb eines `DataFrame` lassen sich damit Zeilen danach filtern, ob passende Datensätze im verbundenen Datenbestand existieren. Das resultierende `Column`-Objekt kann direkt in Filterbedingungen oder als berechnete Spalte verwendet werden. Für korrelierte Subqueries werden Spalten des äußeren DataFrames mit `.outer()` referenziert.

## Beispiel

```python
data_customers = [
    (101, "Alice", "USA"), (102, "Bob", "Canada"), (103, "Charlie", "USA"),
    (104, "David", "Australia")
]
data_orders = [
    (1, 101, "2023-01-15", 250), (2, 102, "2023-01-20", 300),
    (3, 103, "2023-01-25", 400), (4, 101, "2023-02-05", 150)
]
customers = spark.createDataFrame(
    data_customers, ["customer_id", "customer_name", "country"])
orders = spark.createDataFrame(
    data_orders, ["order_id", "customer_id", "order_date", "total_amount"])

from pyspark.sql import functions as sf
customers.alias("c").where(
    orders.alias("o").where(
        sf.col("o.customer_id") == sf.col("c.customer_id").outer()
    ).exists()
).orderBy("customer_id").show()
# +-----------+-------------+-------+
# |customer_id|customer_name|country|
# +-----------+-------------+-------+
# |        101|        Alice|    USA|
# |        102|          Bob| Canada|
# |        103|      Charlie|    USA|
# +-----------+-------------+-------+

customers.alias("c").where(
    ~orders.alias("o").where(
        sf.col("o.customer_id") == sf.col("c.customer_id").outer()
    ).exists()
).orderBy("customer_id").show()
# +-----------+-------------+---------+
# |customer_id|customer_name|  country|
# +-----------+-------------+---------+
# |        104|        David|Australia|
# +-----------+-------------+---------+
```

Siehe auch [`scalar`](01%20scalar.md).

## Quellen

- DataFrame.exists: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/exists

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
