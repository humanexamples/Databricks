# Bronze-zu-Silver Cleaning-Workflow

End-to-end-Beispiel für Prüfungsziel 1: Bronze-Tabelle lesen, Nulls bereinigen, Typen standardisieren, als Silver-Tabelle schreiben.

## 1. Bronze-Tabelle lesen

```python
bronze_customers = spark.read.table("bronze.customers_raw")
# Alternativ pfadbasiert: spark.read.format("delta").load("/Volumes/.../bronze/customers_raw")
```

Simulierte Rohdaten (typische Bronze-Eigenschaften: Strings statt echter Typen, fehlende Werte):

```python
bronze_customers = spark.createDataFrame([
    (1, "Alice", "34", "2024-01-15"),
    (2, "Bob",   None, "2024-02-20"),
    (3, None,    "29", None),
], ["customer_id", "name", "age_str", "signup_date_str"])
```

## 2. Nulls bereinigen und Typen standardisieren

```python
from pyspark.sql.functions import col, coalesce, lit

silver_customers = (
    bronze_customers
    .withColumn("age", col("age_str").cast("int"))
    .withColumn("signup_date", col("signup_date_str").cast("date"))
    .withColumn("name", coalesce(col("name"), lit("Unbekannt")))
    .na.drop(subset=["age"])
    .drop("age_str", "signup_date_str")
)
silver_customers.show()
```
```
+-----------+---------+---+-----------+
|customer_id|     name|age|signup_date|
+-----------+---------+---+-----------+
|          1|    Alice| 34| 2024-01-15|
|          3|Unbekannt| 29|       NULL|
+-----------+---------+---+-----------+
```
- `.cast("int")`/`.cast("date")`: Typkonvertierung von String auf Zielschema; `NULL`-Werte bleiben nach dem Cast `NULL`.
- `coalesce(col, lit(...))`: ersetzt `NULL` in `name` durch einen Default-Wert, ohne die Zeile zu verlieren.
- `.na.drop(subset=["age"])`: entfernt Zeilen, bei denen `age` (nach Cast) `NULL` ist — hier Zeile `customer_id=2` (leerer `age_str`).
- Alternative statt Verwerfen: fehlende Werte auffüllen — `bronze_customers.na.fill({"age_str": "0"})` würde die Zeile stattdessen mit `age=0` behalten.

## 3. Als Silver-Delta-Tabelle schreiben

```python
(silver_customers.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("silver.customers"))
```
- `.mode(...)`: `"append"`, `"overwrite"`, `"error"`/`"errorifexists"` (Standard), `"ignore"`.
- `saveAsTable(name, format=None, mode=None, partitionBy=None, **options)` registriert die Tabelle im Metastore (Unity Catalog).

```python
spark.read.table("silver.customers").show()
# Ergebnis: identisch zu silver_customers (siehe oben) — 2 Zeilen, Tabelle silver.customers registriert
```

**Stand:** 2026-09-15.
