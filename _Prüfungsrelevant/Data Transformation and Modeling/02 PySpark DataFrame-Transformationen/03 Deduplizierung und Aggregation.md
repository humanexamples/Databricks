# Deduplizierung und Aggregation

```python
from pyspark.sql import Row

orders_raw = spark.createDataFrame([
    Row(order_id=1, customer="Alice", amount=250, updated_at="2024-01-10"),
    Row(order_id=1, customer="Alice", amount=250, updated_at="2024-01-10"),  # exaktes Duplikat von Zeile 1
    Row(order_id=2, customer="Bob",   amount=80,  updated_at="2024-01-05"),
    Row(order_id=2, customer="Bob",   amount=95,  updated_at="2024-02-01"),  # Korrektur zu order_id 2, später
    Row(order_id=3, customer="Alice", amount=60,  updated_at="2024-01-12"),
])
# 5 Zeilen insgesamt
```

**SQL-Äquivalent** (als temporäre View, damit die folgenden SQL-Beispiele darauf referenzieren können):

```sql
CREATE OR REPLACE TEMP VIEW orders_raw AS
SELECT * FROM VALUES
  (1, 'Alice', 250, '2024-01-10'),
  (1, 'Alice', 250, '2024-01-10'),  -- exaktes Duplikat von Zeile 1
  (2, 'Bob',   80,  '2024-01-05'),
  (2, 'Bob',   95,  '2024-02-01'),  -- Korrektur zu order_id 2, später
  (3, 'Alice', 60,  '2024-01-12')
AS t(order_id, customer, amount, updated_at);
```

## Windowing — was ist ein Window?

Ein **Window** (Fenster) definiert für jede Zeile eine Menge **verwandter Zeilen**, über die eine Funktion berechnet wird — **ohne** dass dabei Zeilen zusammengefasst/entfernt werden. Das ist der entscheidende Unterschied zu `.groupBy(...).agg(...)`: `groupBy` fasst *N* Zeilen zu *weniger* Zeilen zusammen (eine pro Gruppe), ein Window behält alle *N* Zeilen und hängt jeder einzelnen nur eine zusätzliche, aus ihrem "Fenster" berechnete Spalte an.

Ein Window besteht aus bis zu drei Teilen:

- **`partitionBy(...)`** — teilt die Zeilen in Gruppen ein (wie bei `GROUP BY`), aber ohne sie zusammenzufassen. Die Fenster-Funktion arbeitet unabhängig **innerhalb** jeder Partition.
- **`orderBy(...)`** — legt die Reihenfolge der Zeilen **innerhalb** jeder Partition fest. Zwingend nötig für alle Funktionen, die von der Reihenfolge abhängen (`row_number`, `rank`, `lag`/`lead`, laufende Summen).
- **`rowsBetween(start, end)`** bzw. **`rangeBetween(start, end)`** (optional) — der **Frame**: welcher Ausschnitt der Partition (relativ zur aktuellen Zeile) tatsächlich in die Berechnung einfließt. `Window.unboundedPreceding`/`Window.unboundedFollowing`/`Window.currentRow` sind die gängigen Grenzwerte dafür.

Angewendet wird eine Fenster-Funktion immer über `.over(fensterSpezifikation)`, meist in Kombination mit `withColumn(...)`.

### Rangfolge-Funktionen: `row_number` vs. `rank` vs. `dense_rank`

Alle drei nummerieren Zeilen **innerhalb jeder Partition** gemäß `orderBy` — der Unterschied zeigt sich erst bei **Gleichständen** (hier: die beiden identischen `250`-Zeilen von Alice):

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, rank, dense_rank, col

w = Window.partitionBy("customer").orderBy(col("amount").desc())

(orders_raw
    .withColumn("rn", row_number().over(w))
    .withColumn("rnk", rank().over(w))
    .withColumn("dense_rnk", dense_rank().over(w))
    .orderBy("customer", col("amount").desc())
    .show())
```
```
+--------+--------+------+----------+---+---+---------+
|order_id|customer|amount|updated_at| rn|rnk|dense_rnk|
+--------+--------+------+----------+---+---+---------+
|       1|   Alice|   250|2024-01-10|  1|  1|        1|
|       1|   Alice|   250|2024-01-10|  2|  1|        1|
|       3|   Alice|    60|2024-01-12|  3|  3|        2|
|       2|     Bob|    95|2024-02-01|  1|  1|        1|
|       2|     Bob|    80|2024-01-05|  2|  2|        2|
+--------+--------+------+----------+---+---+---------+
```

**SQL-Äquivalent:**

```sql
SELECT order_id, customer, amount, updated_at,
  ROW_NUMBER() OVER (PARTITION BY customer ORDER BY amount DESC) AS rn,
  RANK()       OVER (PARTITION BY customer ORDER BY amount DESC) AS rnk,
  DENSE_RANK() OVER (PARTITION BY customer ORDER BY amount DESC) AS dense_rnk
FROM orders_raw
ORDER BY customer, amount DESC;
-- Liefert dieselbe Tabelle wie oben.
```
- **`row_number()`** vergibt **immer eindeutige, fortlaufende** Nummern (1, 2, 3, ...) — auch bei exakten Gleichständen. Welche der beiden `250`-Zeilen die `1` und welche die `2` bekommt, ist hier **nicht deterministisch** (siehe schon oben bei `dropDuplicates`), da beide Zeilen in allen Spalten identisch sind.
- **`rank()`** vergibt bei Gleichständen **denselben** Rang und **lässt danach eine Lücke**: beide `250`-Zeilen bekommen `1`, die nächste Zeile (`60`) bekommt `3` (nicht `2`).
- **`dense_rank()`** vergibt bei Gleichständen ebenfalls denselben Rang, **ohne Lücke**: beide `250`-Zeilen bekommen `1`, `60` bekommt `2`.

### Werte aus Nachbarzeilen: `lag` / `lead`

Greift auf eine **vorherige** (`lag`) bzw. **nachfolgende** (`lead`) Zeile **innerhalb derselben Partition** zu — nützlich z. B. um den vorherigen Bestellwert eines Kunden in derselben Zeile verfügbar zu machen:

```python
from pyspark.sql.functions import lag

w2 = Window.partitionBy("customer").orderBy("updated_at")

(orders_raw
    .withColumn("prev_amount", lag("amount").over(w2))
    .orderBy("customer", "updated_at")
    .show())
```
```
+--------+--------+------+----------+-----------+
|order_id|customer|amount|updated_at|prev_amount|
+--------+--------+------+----------+-----------+
|       1|   Alice|   250|2024-01-10|       null|
|       1|   Alice|   250|2024-01-10|        250|
|       3|   Alice|    60|2024-01-12|        250|
|       2|     Bob|    80|2024-01-05|       null|
|       2|     Bob|    95|2024-02-01|         80|
+--------+--------+------+----------+-----------+
```

**SQL-Äquivalent:**

```sql
SELECT order_id, customer, amount, updated_at,
  LAG(amount) OVER (PARTITION BY customer ORDER BY updated_at) AS prev_amount
FROM orders_raw
ORDER BY customer, updated_at;
-- Liefert dieselbe Tabelle wie oben.
```
- Die jeweils **erste** Zeile pro Partition hat keine Vorgängerzeile → `prev_amount = null`. `lead("amount")` würde analog die **nächste** Zeile liefern (letzte Zeile pro Partition → `null`).

### Laufende Summe: Frame mit `rowsBetween`

Ohne expliziten Frame würde `sum(...).over(w)` bei vorhandenem `orderBy` bereits eine laufende Summe bilden (Default-Frame `rangeBetween(unboundedPreceding, currentRow)`) — zur Verdeutlichung hier explizit mit `rowsBetween`:

```python
from pyspark.sql.functions import sum as _sum

w3 = (Window.partitionBy("customer")
      .orderBy("updated_at")
      .rowsBetween(Window.unboundedPreceding, Window.currentRow))

(orders_raw
    .withColumn("running_total", _sum("amount").over(w3))
    .orderBy("customer", "updated_at")
    .show())
```
```
+--------+--------+------+----------+-------------+
|order_id|customer|amount|updated_at|running_total|
+--------+--------+------+----------+-------------+
|       1|   Alice|   250|2024-01-10|          250|
|       1|   Alice|   250|2024-01-10|          500|
|       3|   Alice|    60|2024-01-12|          560|
|       2|     Bob|    80|2024-01-05|           80|
|       2|     Bob|    95|2024-02-01|          175|
+--------+--------+------+----------+-------------+
```

**SQL-Äquivalent:**

```sql
SELECT order_id, customer, amount, updated_at,
  SUM(amount) OVER (
    PARTITION BY customer ORDER BY updated_at
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_total
FROM orders_raw
ORDER BY customer, updated_at;
-- Liefert dieselbe Tabelle wie oben.
```
- `rowsBetween(Window.unboundedPreceding, Window.currentRow)` heißt: "alle Zeilen von Partitionsbeginn bis einschließlich der aktuellen Zeile". Alices letzter Wert (`560`) und Bobs letzter Wert (`175`) entsprechen genau den Summen aus dem `.groupBy("customer").agg(_sum(...))`-Beispiel weiter unten — der Unterschied ist nur, dass hier **jede Einzelzeile** ihren jeweiligen Zwischenstand behält, statt zu einer einzigen Endsumme pro Kunde zusammengefasst zu werden.

## Deduplizierung — `.dropDuplicates()` vs. `.distinct()`

**Syntax:** `df.dropDuplicates(subset=None)` — entfernt doppelte Zeilen, optional nur bezogen auf `subset`-Spalten (Liste). `distinct()` (ohne Parameter) entspricht `dropDuplicates()` ohne `subset`, d. h. Duplikatprüfung über **alle** Spalten. `drop_duplicates` ist ein Alias für `dropDuplicates`.

**Alle Spalten (Standard):**

```python
orders_raw.dropDuplicates().show()
```
```
+--------+--------+------+----------+
|order_id|customer|amount|updated_at|
+--------+--------+------+----------+
|       1|   Alice|   250|2024-01-10|
|       2|     Bob|    80|2024-01-05|
|       2|     Bob|    95|2024-02-01|
|       3|   Alice|    60|2024-01-12|
+--------+--------+------+----------+
```
- Von 5 Zeilen bleiben **4**: nur die exakt identische zweite Zeile (order_id 1) wird entfernt. Die beiden order_id-2-Zeilen unterscheiden sich in `amount`/`updated_at` und bleiben **beide** erhalten.
- `orders_raw.distinct().show()` liefert dasselbe Ergebnis (4 Zeilen) — Duplikatprüfung über alle Spalten.

**SQL-Äquivalent** (`DISTINCT` bzw. `dropDuplicates()` ohne `subset` sind identisch):

```sql
SELECT DISTINCT * FROM orders_raw;
-- Liefert dieselbe Tabelle wie oben (4 Zeilen).
```

**Nur bestimmte Spalten (`subset`):**

```python
orders_raw.dropDuplicates(["order_id"]).count()
```
```
# Ergebnis: 3   (eine Zeile je order_id: 1, 2, 3)
```

**SQL-Äquivalent:** `SELECT DISTINCT` kennt kein `subset` — für "eine beliebige Zeile je Gruppe" eignet sich `GROUP BY` mit der (laut Doku explizit **nicht-deterministischen**) Aggregatfunktion `first()`:

```sql
SELECT order_id, first(customer) AS customer, first(amount) AS amount, first(updated_at) AS updated_at
FROM orders_raw
GROUP BY order_id;
-- Ergebnis: 3 Zeilen — für order_id=2 wie bei dropDuplicates(["order_id"]) nicht deterministisch garantiert,
-- welcher der beiden amount-Werte (80 oder 95) zurückkommt.
```
- Für `order_id=2` behält Spark **eine beliebige** der beiden Zeilen (80 **oder** 95) — welche, ist **nicht deterministisch garantiert**, sofern keine Sortierung vorgeschaltet wird.

**"Neueste Zeile behalten" — deterministisches Muster mit `row_number()`:**

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, col

w = Window.partitionBy("order_id").orderBy(col("updated_at").desc())

latest = (orders_raw
    .withColumn("rn", row_number().over(w))
    .filter(col("rn") == 1)
    .drop("rn"))
latest.orderBy("order_id").show()
```
```
+--------+--------+------+----------+
|order_id|customer|amount|updated_at|
+--------+--------+------+----------+
|       1|   Alice|   250|2024-01-10|
|       2|     Bob|    95|2024-02-01|
|       3|   Alice|    60|2024-01-12|
+--------+--------+------+----------+
```
- Für `order_id=2` wird deterministisch die Zeile mit dem spätesten `updated_at` (95, 2024-02-01) behalten — im Gegensatz zu `dropDuplicates(["order_id"])`, das hier nicht deterministisch wäre.

**SQL-Äquivalent mit `QUALIFY`:** `QUALIFY` filtert Zeilen **nach** der Auswertung einer Fensterfunktion — dadurch entfällt die sonst nötige Unterabfrage/CTE, um erst `rn` zu berechnen und dann darauf zu filtern:

```sql
SELECT order_id, customer, amount, updated_at
FROM orders_raw
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) = 1
ORDER BY order_id;
-- Liefert dieselbe Tabelle wie oben — die Fensterfunktion steht direkt in QUALIFY,
-- muss also nicht extra in der SELECT-Liste stehen und wieder gedroppt werden.
```

## Aggregation

**`.count()`** — Aktion, liefert die Gesamtzeilenzahl als Python-`int`:

```python
orders_raw.count()
```
```
# Ergebnis: 5
```

**SQL-Äquivalent:**

```sql
SELECT COUNT(*) FROM orders_raw;
-- Ergebnis: 5
```

**`.groupBy(...).count()`** — Transformation, liefert ein `DataFrame` mit Spalte `count`:

```python
orders_raw.groupBy("customer").count().show()
```
```
+--------+-----+
|customer|count|
+--------+-----+
|   Alice|    3|
|     Bob|    2|
+--------+-----+
```

**SQL-Äquivalent:**

```sql
SELECT customer, COUNT(*) AS count
FROM orders_raw
GROUP BY customer;
-- Liefert dieselbe Tabelle wie oben.
```

**`approx_count_distinct(col, rsd=None)`** — geschätzte Anzahl unterschiedlicher Werte (HyperLogLog++). `rsd`: maximal erlaubte relative Standardabweichung, Standard **0,05**. Kleineres `rsd` → genauer, aber mehr Speicher/Rechenaufwand; ab `rsd < 0.01` ist `count_distinct` (exakt) laut Doku effizienter.

```python
from pyspark.sql.functions import approx_count_distinct

orders_raw.agg(approx_count_distinct("customer")).show()
```
```
+-----------------------------+
|approx_count_distinct(customer)|
+-----------------------------+
|                             2|
+-----------------------------+
```
- Bei so kleiner Kardinalität liefert die Schätzung das exakte Ergebnis; der Approximationsfehler wird erst bei großen `distinct`-Mengen relevant.

**SQL-Äquivalent:**

```sql
SELECT approx_count_distinct(customer) FROM orders_raw;
-- Ergebnis: 2
```

Effekt des `rsd`-Parameters bei großer Kardinalität (kanonisches Beispiel aus der PySpark-Dokumentation, `spark.range(100000)`, alle Werte eindeutig):

```python
spark.range(100000).agg(
    approx_count_distinct("id").alias("default_rsd"),
    approx_count_distinct("id", 0.1).alias("rsd_0.1")
).show()
```
```
+-----------+-------+
|default_rsd|rsd_0.1|
+-----------+-------+
|      95546| 102065|
+-----------+-------+
```
- Tatsächlicher Wert wäre 100000 — beide Schätzungen weichen ab, `rsd=0.1` (gröber) stärker als der Standardwert 0,05.

**SQL-Äquivalent** (`range(100000)` als Tabellenfunktion):

```sql
SELECT
  approx_count_distinct(id) AS default_rsd,
  approx_count_distinct(id, 0.1) AS `rsd_0.1`
FROM range(100000);
-- Liefert (bis auf Zufallsschwankungen) dieselben Werte wie oben.
```

**`.agg()` mit `mean`/`avg`:**

```python
from pyspark.sql.functions import mean

orders_raw.agg(mean("amount")).show()
```
```
+-----------+
|avg(amount)|
+-----------+
|      147.0|
+-----------+
```
- `mean` ist ein **Alias** für `avg` (identisches Verhalten, auch identischer Spaltenname `avg(...)` im Ergebnis).

**SQL-Äquivalent:** `MEAN` ist auch in SQL ein offizielles Synonym für `AVG` (nicht nur in der PySpark-API):

```sql
SELECT avg(amount) FROM orders_raw;    -- 147.0
SELECT mean(amount) FROM orders_raw;   -- 147.0, identisch zu avg
```

**`.groupBy(...).agg(...)` — mehrere Aggregatfunktionen in einem Aufruf:**

```python
from pyspark.sql.functions import count, sum as _sum, avg

orders_raw.groupBy("customer").agg(
    count("order_id").alias("n_orders"),
    _sum("amount").alias("total_amount"),
    avg("amount").alias("avg_amount")
).orderBy("customer").show()
```
```
+--------+--------+------------+------------------+
|customer|n_orders|total_amount|        avg_amount|
+--------+--------+------------+------------------+
|   Alice|       3|         560|186.66666666666666|
|     Bob|       2|         175|              87.5|
+--------+--------+------------+------------------+
```
- Alice: 3 Zeilen (250 + 250 + 60 = 560, Ø 560/3 = 186.666...), Bob: 2 Zeilen (80 + 95 = 175, Ø 87.5).

**SQL-Äquivalent:**

```sql
SELECT customer,
  COUNT(order_id) AS n_orders,
  SUM(amount) AS total_amount,
  AVG(amount) AS avg_amount
FROM orders_raw
GROUP BY customer
ORDER BY customer;
-- Liefert dieselbe Tabelle wie oben.
```

## `.summary()` vs. `.describe()`

Beide berechnen Statistiken für numerische und String-Spalten (explorative Analyse, kein Stabilitätsversprechen für das Ergebnisschema). **Kein direktes SQL-Äquivalent:** Beides sind reine DataFrame-API-Komfortmethoden — es gibt in Databricks SQL keinen `DESCRIBE`/`SUMMARY`-artigen Befehl, der dieselbe pivotierte Statistik-Tabelle als Abfrageergebnis liefert (`DESCRIBE TABLE`/`ANALYZE TABLE ... COMPUTE STATISTICS` erzeugen bzw. speichern Tabellenmetadaten, aber nicht dieses Ergebnisformat). Dieselben Kennzahlen ließen sich in SQL nur durch einzelne, manuell zusammengestellte Aggregatfunktionen nachbauen (`COUNT`, `AVG`, `STDDEV`, `MIN`, `MAX`, `PERCENTILE_APPROX`).

- **`.describe(*cols)`**: feste Statistiken **count, mean, stddev, min, max**.
- **`.summary(*statistics)`**: ohne Argumente **count, mean, stddev, min, 25%, 50%, 75%, max** (approximierte Quartile zusätzlich); mit Argumenten frei wählbar aus denselben plus beliebigen Perzentilen (z. B. `"75%"`).

Kanonisches Beispiel aus der PySpark-Dokumentation:

```python
df = spark.createDataFrame(
    [("Bob", 13, 40.3, 150.5), ("Alice", 12, 37.8, 142.3), ("Tom", 11, 44.1, 142.2)],
    ["name", "age", "weight", "height"],
)

df.describe(["age"]).show()
```
```
+-------+----+
|summary| age|
+-------+----+
|  count|   3|
|   mean|12.0|
| stddev| 1.0|
|    min|  11|
|    max|  13|
+-------+----+
```

```python
df.select("age", "weight", "height").summary().show()
```
```
+-------+----+------------------+-----------------+
|summary| age|            weight|           height|
+-------+----+------------------+-----------------+
|  count|   3|                 3|                3|
|   mean|12.0| 40.73333333333333|            145.0|
| stddev| 1.0|3.1722757341273704|4.763402145525822|
|    min|  11|              37.8|            142.2|
|    25%|  11|              37.8|            142.2|
|    50%|  12|              40.3|            142.3|
|    75%|  13|              44.1|            150.5|
|    max|  13|              44.1|            150.5|
+-------+----+------------------+-----------------+
```

```python
df.select("age", "weight", "height").summary("count", "min", "25%", "75%", "max").show()
```
```
+-------+---+------+------+
|summary|age|weight|height|
+-------+---+------+------+
|  count|  3|     3|     3|
|    min| 11|  37.8| 142.2|
|    75%| 13|  44.1| 150.5|
|    max| 13|  44.1| 150.5|
+-------+---+------+------+
```
- `summary()` ist die erweiterte Variante mit frei wählbaren Statistiken; `describe()` deckt nur den festen Standardsatz ab.

**Stand:** 2026-09-17, SQL-Äquivalente ergänzt und per `WebFetch`/`WebSearch` gegen die offizielle Databricks-SQL-Referenz verifiziert.
