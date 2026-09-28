# Spalten-, Zeilen- und Tabellenmanipulation

```python
orders = spark.createDataFrame([
    (1, "Alice", 250, "laptop,mouse"),
    (2, "Bob",    80, "phone"),
    (3, "Alice",  60, "cable,charger,case"),
], ["order_id", "customer", "amount", "products"])
```

## Spalten hinzufügen — `withColumn()`

**Syntax:** `df.withColumn(colName, col)` — fügt eine neue Spalte hinzu oder ersetzt eine bestehende mit demselben Namen.

**Literal-Spalte mit `lit()`:**

```python
from pyspark.sql.functions import lit

orders.withColumn("currency", lit("EUR")).show()
```
```
+--------+--------+------+------------------+--------+
|order_id|customer|amount|          products|currency|
+--------+--------+------+------------------+--------+
|       1|   Alice|   250|      laptop,mouse|     EUR|
|       2|     Bob|    80|             phone|     EUR|
|       3|   Alice|    60|cable,charger,case|     EUR|
+--------+--------+------+------------------+--------+
```

**Berechnete Spalte:**

```python
from pyspark.sql.functions import col

orders.withColumn("amount_plus_fee", col("amount") + 10).select("order_id", "amount", "amount_plus_fee").show()
```
```
+--------+------+----------------+
|order_id|amount|amount_plus_fee|
+--------+------+----------------+
|       1|   250|             260|
|       2|    80|              90|
|       3|    60|              70|
+--------+------+----------------+
```
- Achtung: `withColumn()` in einer Schleife für viele Spalten erzeugt große Ausführungspläne (Performance-Risiko) — stattdessen `select()` mit mehreren Spalten auf einmal verwenden.

## Spalten entfernen — `.drop()`

**Syntax:** `df.drop(*cols)` — Namen oder `Column`-Objekte; kein Fehler, falls eine Spalte nicht existiert (No-op).

```python
orders.drop("products").show()
```
```
+--------+--------+------+
|order_id|customer|amount|
+--------+--------+------+
|       1|   Alice|   250|
|       2|     Bob|    80|
|       3|   Alice|    60|
+--------+--------+------+
```

```python
orders.drop("products", "amount").show()
```
```
+--------+--------+
|order_id|customer|
+--------+--------+
|       1|   Alice|
|       2|     Bob|
|       3|   Alice|
+--------+--------+
```

## Spalten umbenennen

**Einzeln:** `df.withColumnRenamed(existing, new)` — No-op, falls `existing` nicht existiert.

```python
orders.withColumnRenamed("customer", "customer_name").show()
```
```
+--------+-------------+------+------------------+
|order_id|customer_name|amount|          products|
+--------+-------------+------+------------------+
|       1|        Alice|   250|      laptop,mouse|
|       2|          Bob|    80|             phone|
|       3|        Alice|    60|cable,charger,case|
+--------+-------------+------+------------------+
```

**Mehrere gleichzeitig:** `df.withColumnsRenamed(colsMap)` — `dict` von Alt- zu Neu-Namen (seit Spark 3.4.0).

```python
orders.withColumnsRenamed({"customer": "customer_name", "amount": "order_amount"}).show()
```
```
+--------+-------------+------------+------------------+
|order_id|customer_name|order_amount|          products|
+--------+-------------+------------+------------------+
|       1|        Alice|         250|      laptop,mouse|
|       2|          Bob|          80|             phone|
|       3|        Alice|          60|cable,charger,case|
+--------+-------------+------------+------------------+
```

## Spalte splitten — `split()` und `getItem()`

**Syntax:** `split(str, pattern, limit=-1)` → `ARRAY<STRING>`. `limit <= 0` (Standard `-1`): Pattern wird beliebig oft angewendet. `limit > 0`: maximal `limit` Elemente, letztes Element enthält den Rest.

```python
from pyspark.sql.functions import split

orders.withColumn("product_list", split(col("products"), ",")).select("order_id", "product_list").show()
```
```
+--------+-----------------------+
|order_id|           product_list|
+--------+-----------------------+
|       1|    [laptop, mouse]|
|       2|               [phone]|
|       3|[cable, charger, case]|
+--------+-----------------------+
```

**Element per Index (`[...]`) oder `getItem()`:**

```python
split_df = orders.withColumn("product_list", split(col("products"), ","))
split_df.withColumn("first_product", split_df.product_list.getItem(0)).select("order_id", "first_product").show()
```
```
+--------+-------------+
|order_id|first_product|
+--------+-------------+
|       1|       laptop|
|       2|        phone|
|       3|        cable|
+--------+-------------+
```
- `col.getItem(0)` ist äquivalent zu `col[0]`.

## Zeilen filtern — `.filter()` / `.where()`

**Syntax:** `df.filter(condition)` — `condition` ist ein `Column`-Ausdruck (`BooleanType`) oder ein SQL-Ausdruckstring. `.where()` ist ein **Alias** für `.filter()`, identisches Verhalten.

```python
orders.filter(col("amount") > 100).show()
```
```
+--------+--------+------+------------+
|order_id|customer|amount|    products|
+--------+--------+------+------------+
|       1|   Alice|   250|laptop,mouse|
+--------+--------+------+------------+
```

**SQL-Ausdruck als String (äquivalent):**

```python
orders.where("amount > 100").show()
```
```
+--------+--------+------+------------+
|order_id|customer|amount|    products|
+--------+--------+------+------------+
|       1|   Alice|   250|laptop,mouse|
+--------+--------+------+------------+
```

**Kombinierte Bedingungen — `&` (UND), `|` (ODER), `~` (NICHT):**

```python
orders.filter((col("amount") > 50) & (col("customer") == "Alice")).show()
```
```
+--------+--------+------+------------------+
|order_id|customer|amount|          products|
+--------+--------+------+------------------+
|       1|   Alice|   250|      laptop,mouse|
|       3|   Alice|    60|cable,charger,case|
+--------+--------+------+------------------+
```
- Klammern um jede Teilbedingung sind zwingend (Operator-Priorität von `&`/`|` in Python).

## Arrays explodieren — `explode()`, `explode_outer()`, `posexplode()`

```python
from pyspark.sql import Row

basket = spark.createDataFrame([
    Row(id=1, items=["apple", "banana"]),
    Row(id=2, items=[]),
    Row(id=3, items=None),
])
```

**`explode()`** — eine Zeile je Array-Element; `NULL`- oder leere Arrays erzeugen **keine** Zeile:

```python
from pyspark.sql.functions import explode

basket.select("*", explode("items")).show()
```
```
+---+----------------+------+
| id|           items|   col|
+---+----------------+------+
|  1|[apple, banana]| apple|
|  1|[apple, banana]|banana|
+---+----------------+------+
```
- Zeilen `id=2` (leeres Array) und `id=3` (`NULL`) verschwinden komplett.

**`explode_outer()`** — wie `explode()`, aber `NULL`/leeres Array erzeugt eine Zeile mit `NULL`:

```python
from pyspark.sql.functions import explode_outer

basket.select("*", explode_outer("items")).show()
```
```
+---+----------------+------+
| id|           items|   col|
+---+----------------+------+
|  1|[apple, banana]| apple|
|  1|[apple, banana]|banana|
|  2|              []|  NULL|
|  3|            NULL|  NULL|
+---+----------------+------+
```

**`posexplode()`** — zusätzlich die Position (`pos`, 0-basiert) je Element; gleiches Drop-Verhalten wie `explode()` (kein `_outer`):

```python
from pyspark.sql.functions import posexplode

basket.select("*", posexplode("items")).show()
```
```
+---+----------------+---+------+
| id|           items|pos|   col|
+---+----------------+---+------+
|  1|[apple, banana]|  0| apple|
|  1|[apple, banana]|  1|banana|
+---+----------------+---+------+
```
- `posexplode_outer()` kombiniert beides: Position **und** Verhalten bei `NULL`/leerem Array (Zeile mit `pos=NULL, col=NULL`).
- Pro `SELECT`-Klausel ist nur ein `explode`/`posexplode`-Aufruf erlaubt.

## Tabellenstruktur ändern (SQL) — `ALTER TABLE`

Spalten-Äquivalent auf Tabellenebene (Delta-Tabellen):

```sql
-- Spalte hinzufügen
ALTER TABLE orders_silver ADD COLUMN email STRING COMMENT 'Kunden-E-Mail';

-- Spalte entfernen (erfordert Column Mapping)
ALTER TABLE orders_silver DROP COLUMN email;

-- Spalte umbenennen (erfordert Column Mapping)
ALTER TABLE orders_silver RENAME COLUMN customer TO customer_name;
```
- `ADD COLUMN`/`ADD COLUMNS` unterstützt `FIRST`/`AFTER` zur Positionierung.
- `DROP COLUMN`/`RENAME COLUMN` setzen bei Delta-Tabellen Column Mapping voraus.

**Stand:** 2026-09-15.
