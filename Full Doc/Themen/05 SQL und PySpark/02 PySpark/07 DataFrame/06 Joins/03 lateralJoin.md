# `DataFrame.lateralJoin()`

Führt einen Lateral Join mit einem anderen DataFrame über den angegebenen Join-Ausdruck aus.

## Signatur

```python
lateralJoin(other: "DataFrame", on: Optional[Column] = None, how: Optional[str] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `other` | `DataFrame` | Rechte Seite des Joins. |
| `on` | `Column`, optional | Ein Join-Ausdruck (`Column`). |
| `how` | `str`, optional | Standard `inner`. Muss einer der folgenden Werte sein: `inner`, `cross`, `left`, `leftouter` und `left_outer`. |

## Rückgabewert

`DataFrame`: Gejointer DataFrame.

## Hinweise

Ein Lateral Join (auch korrelierter Join) ist ein Join, bei dem jede Zeile des einen DataFrames als Eingabe für eine Subquery bzw. abgeleitete Tabelle dient, die ein zeilenspezifisches Ergebnis berechnet. Der rechte `DataFrame` kann Spalten der aktuellen Zeile des linken `DataFrame` referenzieren. Das ermöglicht komplexere, kontextabhängige Ergebnisse als ein Standard-Join.

## Beispiel

```python
from pyspark.sql import functions as sf
from pyspark.sql import Row
customers_data = [
    Row(customer_id=1, name="Alice"), Row(customer_id=2, name="Bob"),
    Row(customer_id=3, name="Charlie"), Row(customer_id=4, name="Diana")
]
customers = spark.createDataFrame(customers_data)
orders_data = [
    Row(order_id=101, customer_id=1, order_date="2024-01-10",
        items=[Row(product="laptop", quantity=5), Row(product="mouse", quantity=12)]),
    Row(order_id=102, customer_id=1, order_date="2024-02-15",
        items=[Row(product="phone", quantity=2), Row(product="charger", quantity=15)]),
    Row(order_id=105, customer_id=1, order_date="2024-03-20",
        items=[Row(product="tablet", quantity=4)]),
    Row(order_id=103, customer_id=2, order_date="2024-01-12",
        items=[Row(product="tablet", quantity=8)]),
    Row(order_id=104, customer_id=2, order_date="2024-03-05",
        items=[Row(product="laptop", quantity=7)]),
    Row(order_id=106, customer_id=3, order_date="2024-04-05",
        items=[Row(product="monitor", quantity=1)]),
]
orders = spark.createDataFrame(orders_data)

customers.join(orders, "customer_id").lateralJoin(
    spark.tvf.explode(sf.col("items").outer()).select("col.*")
).select(
    "customer_id", "name", "order_id", "order_date", "product", "quantity"
).orderBy("customer_id", "order_id", "product").show()
# +-----------+-------+--------+----------+-------+--------+
# |customer_id|   name|order_id|order_date|product|quantity|
# +-----------+-------+--------+----------+-------+--------+
# |          1|  Alice|     101|2024-01-10| laptop|       5|
# |          1|  Alice|     101|2024-01-10|  mouse|      12|
# ...
# +-----------+-------+--------+----------+-------+--------+
```

Siehe auch [`join`](01%20join.md).

## Quellen

- DataFrame.lateralJoin: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/lateralJoin

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
