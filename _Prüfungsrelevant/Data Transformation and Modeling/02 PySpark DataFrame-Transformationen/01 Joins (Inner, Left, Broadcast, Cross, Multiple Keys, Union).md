# Joins (Inner, Left, Broadcast, Cross, Multiple Keys, Union)

## `.join()` — Grundsyntax

**Syntax:** `df.join(other, on=None, how=None)`

- `other`: rechte Seite des Joins (`DataFrame`).
- `on`: Spaltenname (`str`), Liste von Spaltennamen, ein `Column`-Ausdruck oder eine Liste von `Column`-Ausdrücken. Bei String(s) müssen die Spalten auf beiden Seiten existieren (Equi-Join).
- `how`: Standard `"inner"`. Gültige Werte: `inner`, `cross`, `outer`/`full`/`fullouter`/`full_outer`, `left`/`leftouter`/`left_outer`, `right`/`rightouter`/`right_outer`, `semi`/`leftsemi`/`left_semi`, `anti`/`leftanti`/`left_anti`.

```python
from pyspark.sql import Row

df = spark.createDataFrame([Row(name="Alice", age=2), Row(name="Bob", age=5)])
df2 = spark.createDataFrame([Row(name="Tom", height=80), Row(name="Bob", height=85)])
```

## Inner Join (Standard)

```python
df.join(df2, "name").show()
```
```
+----+---+------+
|name|age|height|
+----+---+------+
| Bob|  5|    85|
+----+---+------+
```
- Nur Zeilen mit Treffer auf **beiden** Seiten.
- Join-Spalte als String → nur eine `name`-Spalte im Ergebnis (implizite Bedingung).

## Left / Right / Full Outer Join

```python
df.join(df2, "name", "left_outer").show()
```
```
+-----+---+------+
| name|age|height|
+-----+---+------+
|Alice|  2|  NULL|
|  Bob|  5|    85|
+-----+---+------+
```

```python
df.join(df2, "name", "right_outer").show()
```
```
+----+----+------+
|name| age|height|
+----+----+------+
| Tom|NULL|    80|
| Bob|   5|    85|
+----+----+------+
```
- `how="outer"` (bzw. `"full"`/`"fullouter"`/`"full_outer"`): alle Zeilen aus beiden Seiten, `NULL` wo kein Treffer.

## Left Semi / Left Anti Join

```python
df.join(df2, "name", "left_semi").show()
```
```
+----+---+
|name|age|
+----+---+
| Bob|  5|
+----+---+
```
- **Semi Join:** nur Spalten der linken Seite, nur Zeilen mit Treffer rechts.

```python
df.join(df2, "name", "left_anti").show()
```
```
+-----+---+
| name|age|
+-----+---+
|Alice|  2|
+-----+---+
```
- **Anti Join:** nur Zeilen der linken Seite **ohne** Treffer rechts.

## Join über mehrere Spalten

```python
df3 = spark.createDataFrame([
    Row(name="Alice", age=10, height=80),
    Row(name="Bob", age=5, height=None),
    Row(name="Tom", age=None, height=None),
])

df.join(df3, ["name", "age"]).show()
```
```
+----+---+------+
|name|age|height|
+----+---+------+
| Bob|  5|  NULL|
+----+---+------+
```
- `on` als Liste → Equi-Join über alle genannten Spalten gleichzeitig (nur eine Instanz jeder Join-Spalte im Ergebnis).

## Join mit unterschiedlichen Spaltennamen (explizite Bedingung)

```python
customers = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["cust_id", "name"])
orders = spark.createDataFrame([(100, 1, 250), (101, 2, 80), (102, 1, 60)], ["order_id", "customer_ref", "amount"])

orders.join(customers, orders.customer_ref == customers.cust_id, "inner").show()
```
```
+--------+------------+------+-------+-----+
|order_id|customer_ref|amount|cust_id| name|
+--------+------------+------+-------+-----+
|     100|           1|   250|      1|Alice|
|     101|           2|    80|      2|  Bob|
|     102|           1|    60|      1|Alice|
+--------+------------+------+-------+-----+
```
- Bei explizitem `Column`-Ausdruck bleiben **beide** Join-Spalten im Ergebnis erhalten.
- Kombination mehrerer Bedingungen: `&` (UND), `|` (ODER).

```python
orders.join(customers, (orders.customer_ref == customers.cust_id) & (orders.amount > 100)).show()
```
```
+--------+------------+------+-------+-----+
|order_id|customer_ref|amount|cust_id| name|
+--------+------------+------+-------+-----+
|     100|           1|   250|      1|Alice|
+--------+------------+------+-------+-----+
```

## Broadcast Join

**Syntax:** `from pyspark.sql.functions import broadcast` → `broadcast(df)` markiert ein `DataFrame` als klein genug für einen Broadcast-Join.

```python
from pyspark.sql.functions import broadcast

df_small = spark.range(3)
df_big = spark.createDataFrame([1, 2, 3, 3, 4], "int")

df_big.join(broadcast(df_small), df_big.value == df_small.id).show()
```
```
+-----+---+
|value| id|
+-----+---+
|    1|  1|
|    2|  2|
+-----+---+
```
- Sendet das kleine `DataFrame` vollständig an jeden Executor statt eines Shuffle-Joins — vermeidet teures Shuffling der großen Seite.
- Spark broadcastet automatisch, wenn die geschätzte Tabellengröße unter `spark.sql.autoBroadcastJoinThreshold` liegt (Default **10 MB** = `10485760` Bytes; `-1` deaktiviert Auto-Broadcast).

## Cross Join

**Syntax:** `df.crossJoin(other)` oder `df.join(other, how="cross")` (kein `on`).

```python
df_a = spark.createDataFrame([(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df_h = spark.createDataFrame([Row(height=80, name="Tom"), Row(height=85, name="Bob")])

df_a.crossJoin(df_h.select("height")).select("age", "name", "height").show()
```
```
+---+-----+------+
|age| name|height|
+---+-----+------+
| 14|  Tom|    80|
| 14|  Tom|    85|
| 23|Alice|    80|
| 23|Alice|    85|
| 16|  Bob|    80|
| 16|  Bob|    85|
+---+-----+------+
```
- Kartesisches Produkt: **keine** Join-Bedingung, Ergebnis hat `rows(df_a) × rows(df_h)` = 3 × 2 = **6 Zeilen**.
- Explosionsgefahr bei großen Tabellen — Zeilenzahl wächst multiplikativ.

## `union()` vs. `unionAll()` vs. `unionByName()`

**Syntax:** `df.union(other)` — kombiniert Zeilen **positionsbasiert** (wie SQL `UNION ALL`), keine automatische Deduplizierung.

```python
df1 = spark.createDataFrame([(1, "A"), (2, "B")], ["id", "value"])
df2 = spark.createDataFrame([(3, "C"), (4, "D")], ["id", "value"])

df1.union(df2).show()
```
```
+---+-----+
| id|value|
+---+-----+
|  1|    A|
|  2|    B|
|  3|    C|
|  4|    D|
+---+-----+
```

- `unionAll()` ist ein **Alias** für `union()` — identisches Verhalten, aus SQL-Tradition beibehalten.
- Beide lösen Spalten **nach Position** auf, nicht nach Name — bei unterschiedlicher Spaltenreihenfolge entsteht ein falsches, aber unbemerktes Ergebnis:

```python
df1 = spark.createDataFrame([[1, 2, 3]], ["col0", "col1", "col2"])
df2 = spark.createDataFrame([[4, 5, 6]], ["col1", "col2", "col0"])  # andere Reihenfolge!

df1.union(df2).show()
```
```
+----+----+----+
|col0|col1|col2|
+----+----+----+
|   1|   2|   3|
|   4|   5|   6|
+----+----+----+
```
- Zeile 2 landet **falsch zugeordnet** (Werte 4,5,6 einfach positionsweise übernommen, ohne Rücksicht auf die Spaltennamen col1/col2/col0 aus df2).

**Syntax:** `df.unionByName(other, allowMissingColumns=False)` — löst Spalten **nach Name** auf, nicht nach Position.

```python
df1.unionByName(df2).show()
```
```
+----+----+----+
|col0|col1|col2|
+----+----+----+
|   1|   2|   3|
|   6|   4|   5|
+----+----+----+
```
- Gleiches Beispiel, aber korrekt: Werte landen in der Spalte mit demselben Namen, unabhängig von der Reihenfolge.
- `allowMissingColumns=True`: fehlende Spalten werden mit `NULL` aufgefüllt statt einen Fehler zu werfen.

```python
df1 = spark.createDataFrame([[1, 2, 3]], ["col0", "col1", "col2"])
df2 = spark.createDataFrame([[4, 5, 6]], ["col1", "col2", "col3"])

df1.unionByName(df2, allowMissingColumns=True).show()
```
```
+----+----+----+----+
|col0|col1|col2|col3|
+----+----+----+----+
|   1|   2|   3|NULL|
|NULL|   4|   5|   6|
+----+----+----+----+
```

## Doppelte/mehrdeutige Spaltennamen nach einem Join

```python
df_join = df.join(df, df.name == df.name, "outer")
df_join.select(df.name).show()
```
```
# AnalysisException: Column name#0 are ambiguous ...
```
- Bei Self-Joins (oder Joins mit überlappenden Spaltennamen und expliziter Bedingung) ist der direkte Spaltenverweis mehrdeutig.

**Lösung: Aliasing der DataFrames.**

```python
import pyspark.sql.functions as sf

df.alias("a").join(
    df.alias("b"), sf.col("a.name") == sf.col("b.name"), "outer"
).select("a.name", "b.age").show()
```
```
+-----+---+
| name|age|
+-----+---+
|  Bob|  5|
|Alice|  2|
+-----+---+
```
- `.alias(...)` + `sf.col("alias.spalte")` referenziert eindeutig die gewünschte Seite.

**Stand:** 2026-09-15.
