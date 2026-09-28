# PySpark auf Databricks — Überblick und Grundlagen

Dieses Dokument fasst die Einstiegsseite der PySpark-Dokumentation (`pyspark/`) sowie die Grundlagenseite (`pyspark/basics`) zusammen. Verifiziert per `WebFetch` gegen die offizielle AWS-Dokumentation.

## Abschnittsübersicht
1. [Was ist PySpark](#ueberblick)
2. [Kernkonzepte: DataFrames](#konzepte)
3. [Verfügbare APIs und Bibliotheken](#apis)
4. [DataFrames erzeugen](#erzeugen)
5. [Mit Spalten arbeiten](#spalten)
6. [Mit Zeilen arbeiten](#zeilen)
7. [DataFrames verbinden (Join)](#join)
8. [Daten aggregieren](#aggregieren)
9. [Methoden verketten (Chaining)](#chaining)
10. [Daten visualisieren](#visualisieren)
11. [Daten schreiben](#schreiben)
12. [Quellen](#quellen)

---

## <a id="ueberblick">1. Was ist PySpark</a>

PySpark ist die Python-Schnittstelle zu Apache Spark. Sie kombiniert die Flexibilität von Python mit der verteilten Big-Data-Verarbeitung von Spark. In Databricks-Notebooks, die mit einem Cluster oder SQL-Warehouse verbunden sind, steht die `SparkSession` bereits als vorkonfigurierte Variable `spark` zur Verfügung.

## <a id="konzepte">2. Kernkonzepte: DataFrames</a>

Das zentrale Objekt in PySpark ist das **DataFrame** — ein Dataset, das in benannten Spalten organisiert ist. Ein DataFrame besteht aus drei Bestandteilen:

| Bestandteil | Beschreibung |
| --- | --- |
| **Schema** | Definiert Spaltennamen und Datentypen. |
| **Rows (Zeilen)** | Einzelne Datensätze innerhalb des DataFrames. |
| **Columns (Spalten)** | Können einfache Typen (String, Integer) oder komplexe Typen (Array, Map) enthalten. |

Zwei Eigenschaften sind für das Verständnis von PySpark zentral:

- **Lazy Evaluation:** Spark verzögert die eigentliche Berechnung, bis eine *Action* aufgerufen wird (z. B. `.show()`, `.collect()`, `.count()`). *Transformations* (z. B. `.select()`, `.filter()`) beschreiben nur die Verarbeitungslogik, ohne sie sofort auszuführen.
- **Unveränderlichkeit (Immutability):** DataFrames sind unveränderlich. Jede Transformation gibt ein **neues** DataFrame zurück, anstatt das bestehende zu verändern.

## <a id="apis">3. Verfügbare APIs und Bibliotheken</a>

| API / Bibliothek | Zweck |
| --- | --- |
| Spark SQL und DataFrames | Verarbeitung strukturierter Daten. |
| Structured Streaming | Kontinuierliche (Streaming-)Datenverarbeitung. |
| Pandas API on Spark | Verteilte Pandas-Workloads. |
| MLlib | Machine-Learning-Algorithmen. |
| GraphX | Graph-Berechnungen. |

---

## <a id="erzeugen">4. DataFrames erzeugen</a>

### Import gängiger Typen und Funktionen

```python
# import select functions and types
from pyspark.sql.types import IntegerType, StringType
from pyspark.sql.functions import floor, round

# import modules using an alias
import pyspark.sql.types as T
import pyspark.sql.functions as F
```

### Mit angegebenen Werten (`createDataFrame`)

```python
df_children = spark.createDataFrame(
  data = [("Mikhail", 15), ("Zaky", 13), ("Zoya", 8)],
  schema = ['name', 'age'])
display(df_children)
```

Optional mit explizitem Schema über `StructType`/`StructField`:

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
df_children_with_schema = spark.createDataFrame(
  data = [("Mikhail", 15), ("Zaky", 13), ("Zoya", 8)],
  schema = StructType([
    StructField('name', StringType(), True),
    StructField('age', IntegerType(), True)
  ]))
display(df_children_with_schema)
```

### Aus einer Unity-Catalog-Tabelle

```python
df_customer = spark.table('samples.tpch.customer')
display(df_customer)
```

### Aus einer hochgeladenen Datei (z. B. CSV in einem Volume)

```python
# Assign this variable your full volume file path
volume_file_path = ""
df_csv = (spark.read
  .format("csv")
  .option("header", True)
  .option("inferSchema", True)
  .load(volume_file_path))
display(df_csv)
```

### Aus einer JSON-API-Antwort

```python
import requests

# Download data from URL
url = "https://api.fda.gov/drug/drugsfda.json?limit=100"
response = requests.get(url)

# Create the DataFrame
df_drugs = spark.createDataFrame(response.json()["results"])
display(df_drugs)
```

Ein JSON-Feld bzw. verschachteltes Objekt auswählen:

```python
display(df_drugs.select(df_drugs["products"]))
```

```python
display(df_drugs.select(df_drugs["products"][0]["brand_name"]))
```

### Aus einer Beispieldatei unter `/databricks-datasets`

```python
display(dbutils.fs.ls('/databricks-datasets'))
```

```python
%fs ls '/databricks-datasets'
```

```python
df_population = (spark.read
  .format("csv")
  .option("header", True)
  .option("inferSchema", True)
  .load("/databricks-datasets/samples/population-vs-price/data_geo.csv"))
display(df_population)
```

---

## <a id="spalten">5. Mit Spalten arbeiten</a>

### Spalten auswählen

Es gibt mehrere gleichwertige Schreibweisen, um Spalten auszuwählen:

```python
from pyspark.sql.functions import col
df_customer.select(
  col("c_custkey"),
  col("c_acctbal"))
```

```python
from pyspark.sql.functions import expr
df_customer.select(
  expr("c_custkey"),
  expr("c_acctbal"))
```

```python
df_customer.selectExpr(
  "c_custkey as key",
  "round(c_acctbal) as account_rounded")
```

```python
df_customer.select(
  "c_custkey",
  "c_acctbal")
```

```python
df_customer.select(
  df_customer["c_custkey"],
  df_customer["c_acctbal"])
```

```python
df_customer.select(
  df_customer.c_custkey,
  df_customer.c_acctbal)
```

### Spalten erzeugen (`withColumn`)

```python
df_customer_flag = df_customer.withColumn("balance_flag", col("c_acctbal") > 1000)
```

### Spalten umbenennen (`withColumnRenamed`)

```python
df_customer_flag_renamed = df_customer_flag.withColumnRenamed("balance_flag", "balance_flag_renamed")
```

```python
from pyspark.sql.functions import avg
df_segment_balance = df_customer.groupBy("c_mktsegment").agg(
    avg(df_customer["c_acctbal"]).alias("avg_account_balance"))
display(df_segment_balance)
```

### Spaltentypen konvertieren (`cast`)

```python
from pyspark.sql.functions import col
df_casted = df_customer.withColumn("c_custkey", col("c_custkey").cast(StringType()))
print(type(df_casted))
```

### Spalten entfernen (`drop`)

```python
df_customer_flag_renamed.drop("balance_flag_renamed")
```

```python
df_customer_flag_renamed.drop("c_phone", "balance_flag_renamed")
```

---

## <a id="zeilen">6. Mit Zeilen arbeiten</a>

### Zeilen filtern (`filter`)

```python
from pyspark.sql.functions import col
df_that_one_customer = df_customer.filter(col("c_custkey") == 412449)
```

Mehrere Bedingungen lassen sich mit `&` (UND) und `|` (ODER) kombinieren:

```python
df_customer.filter((col("c_nationkey") == 20) & (col("c_acctbal") > 1000))
```

```python
df_filtered_customer = df_customer.filter((col("c_custkey") == 412446) | (col("c_custkey") == 412447))
```

### Duplikate entfernen (`distinct`)

```python
df_unique = df_customer.distinct()
```

### Mit Nullwerten umgehen (`na`)

```python
df_customer_no_nulls = df_customer.na.drop()
df_customer_no_nulls = df_customer.na.drop("any")
```

```python
df_customer_no_nulls = df_customer.na.drop("all")
```

```python
df_customer_no_nulls = df_customer.na.drop("all", subset=["c_acctbal", "c_custkey"])
```

```python
df_customer_filled = df_customer.na.fill("0", subset=["c_acctbal"])
```

```python
df_customer_phone_filled = df_customer.na.replace([""], ["UNKNOWN"], subset=["c_phone"])
```

### Zeilen anhängen (`union`)

```python
df_appended_rows = df_that_one_customer.union(df_filtered_customer)
display(df_appended_rows)
```

### Zeilen sortieren (`orderBy` / `sort`)

```python
df_customer.orderBy(col("c_acctbal"))
```

```python
df_customer.sort(col("c_custkey").desc())
```

```python
df_sorted = df_customer.orderBy(col("c_acctbal").desc(), col("c_custkey").asc())
df_sorted = df_customer.sort(col("c_acctbal").desc(), col("c_custkey").asc())
```

```python
display(df_sorted.limit(10))
```

> **Hinweis aus der Dokumentation:** Sortieren kann bei großen Datenmengen teuer sein. Wenn sortierte Daten gespeichert und später wieder mit Spark eingelesen werden, ist die Reihenfolge **nicht garantiert**.

---

## <a id="join">7. DataFrames verbinden (Join)</a>

```python
df_customer = spark.table('samples.tpch.customer')
df_order = spark.table('samples.tpch.orders')
df_joined = df_order.join(
  df_customer,
  on = df_order["o_custkey"] == df_customer["c_custkey"],
  how = "inner")
display(df_joined)
```

Mit zusammengesetzter Join-Bedingung:

```python
df_customer = spark.table('samples.tpch.customer')
df_order = spark.table('samples.tpch.orders')
df_complex_joined = df_order.join(
  df_customer,
  on = ((df_order["o_custkey"] == df_customer["c_custkey"]) & (df_order["o_totalprice"] > 500000)),
  how = "inner")
display(df_complex_joined)
```

`how` unterstützt u. a. `"inner"`, `"left"` und `"outer"`.

---

## <a id="aggregieren">8. Daten aggregieren</a>

Vergleichbar mit `GROUP BY` in SQL:

```python
from pyspark.sql.functions import avg
# group by one column
df_segment_balance = df_customer.groupBy("c_mktsegment").agg(
    avg(df_customer["c_acctbal"]))
display(df_segment_balance)
```

```python
from pyspark.sql.functions import avg
# group by two columns
df_segment_nation_balance = df_customer.groupBy("c_mktsegment", "c_nationkey").agg(
    avg(df_customer["c_acctbal"]))
display(df_segment_nation_balance)
```

```python
df_customer.count()
```

---

## <a id="chaining">9. Methoden verketten (Chaining)</a>

Da Transformationen lazy ausgewertet werden, lassen sich mehrere Operationen in einer einzigen Kette formulieren:

```python
from pyspark.sql.functions import count
df_chained = (
    df_order.filter(col("o_orderstatus") == "F")
    .groupBy(col("o_orderpriority"))
    .agg(count(col("o_orderkey")).alias("n_orders"))
    .sort(col("n_orders").desc()))
display(df_chained)
```

---

## <a id="visualisieren">10. Daten visualisieren</a>

```python
display(df_order)
```

`display()` rendert ein DataFrame in Databricks-Notebooks als interaktive Tabelle bzw. Visualisierung.

---

## <a id="schreiben">11. Daten schreiben</a>

### Als Unity-Catalog-Tabelle speichern

```python
df_joined.write.saveAsTable(f"{catalog_name}.{schema_name}.{table_name}")
```

### Als CSV exportieren

```python
# Assign this variable your file path
file_path = ""
(df_joined.write
  .format("csv")
  .mode("overwrite")
  .write(file_path))
```

Details zu `DataFrameWriter`-Optionen (Schreibmodi, Formate, Partitionierung usw.) siehe [04 DataFrameWriter](../04%20DataFrameWriter/00%20Uebersicht.md).

---

## <a id="quellen">12. Quellen</a>

- PySpark on Databricks (Übersicht): https://docs.databricks.com/aws/en/pyspark/
- PySpark basics: https://docs.databricks.com/aws/en/pyspark/basics

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
