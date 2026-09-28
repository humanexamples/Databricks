# Python-Entwicklung für Lakeflow Declarative Pipelines

## Abschnittsübersicht

1. [Grundprinzip](#grundprinzip)
2. [Materialized View vs. Streaming-Tabelle](#mv-vs-st)
3. [Datenladen mit Auto Loader](#autoloader)
4. [Datenqualität mit Expectations](#expectations)
5. [Dynamische Tabellenerzeugung per `for`-Schleife](#for-loop)
6. [Quellen](#quellen)

---

## <a id="grundprinzip">1. Grundprinzip</a>

Python-Code, der Pipeline-Datasets erzeugt, muss DataFrames zurückgeben — wörtlich: *"Python code that creates pipeline datasets must return DataFrames."* Die Dekoratoren aus dem Modul `pyspark.pipelines` (importiert als `dp`) definieren dabei, welcher Art von Dataset (Materialized View, Streaming-Tabelle, temporäre Sicht) die zurückgegebene DataFrame entspricht.

---

## <a id="mv-vs-st">2. Materialized View vs. Streaming-Tabelle</a>

Der zentrale Unterschied zwischen `@dp.materialized_view()` und `@dp.table()` liegt in der verwendeten Lesemethode:

- `@dp.materialized_view()` — für Batch-Lesevorgänge mit `spark.read`.
- `@dp.table()` — für Streaming-Lesevorgänge mit `spark.readStream`.

Beide unterstützen einen optionalen `name`-Parameter, um den Tabellennamen explizit zu setzen.

```python
from pyspark import pipelines as dp

@dp.materialized_view()
def basic_mv():
    return spark.read.table("samples.nyctaxi.trips")

@dp.table()
def basic_st():
    return spark.readStream.table("samples.nyctaxi.trips")
```

Mit explizitem Namen:

```python
from pyspark import pipelines as dp

@dp.materialized_view(name = "trips_mv")
def basic_mv():
    return spark.read.table("samples.nyctaxi.trips")

@dp.table(name = "trips_st")
def basic_st():
    return spark.readStream.table("samples.nyctaxi.trips")
```

Ein umfangreicheres Beispiel mit Join und Aggregation über mehrere aufeinander aufbauende Datasets:

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col

@dp.table()
@dp.expect_or_drop("valid_date", "order_datetime IS NOT NULL AND length(order_datetime) > 0")
def orders():
    return (spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/databricks-datasets/retail-org/sales_orders")
    )

@dp.materialized_view()
def customers():
    return spark.read.format("csv").option("header", True).load("/databricks-datasets/retail-org/customers")

@dp.materialized_view()
def customer_orders():
    return (spark.read.table("orders")
        .join(spark.read.table("customers"), "customer_id")
        .select("customer_id",
            "order_number",
            "state",
            col("order_datetime").cast("int").cast("timestamp").cast("date").alias("order_date"),
        )
    )

@dp.materialized_view()
def daily_orders_by_state():
    return (spark.read.table("customer_orders")
        .groupBy("state", "order_date")
        .count().withColumnRenamed("count", "order_count")
    )
```

---

## <a id="autoloader">3. Datenladen mit Auto Loader</a>

Die Doku empfiehlt, "Auto Loader und Streaming-Tabellen beim Konfigurieren inkrementeller Ingestion-Workloads gegen in Cloud-Objektspeicher abgelegte Daten" zu verwenden (*"using Auto Loader and streaming tables when configuring incremental ingestion workloads against data stored in cloud object storage"*). Auto Loader wird dabei über das Format `cloudFiles` angesprochen, das flexibles Laden von Daten ermöglicht.

---

## <a id="expectations">4. Datenqualität mit Expectations</a>

Datenvalidierung erfolgt über den Dekorator `@dp.expect_or_drop()`, der Constraints erzwingt — beispielsweise können Expectations Nullwerte herausfiltern oder Feldeigenschaften vor der Weiterverarbeitung validieren (siehe [expectations.md](Python-Referenz/expectations.md) für die vollständige Dekorator-Familie).

---

## <a id="for-loop">5. Dynamische Tabellenerzeugung per `for`-Schleife</a>

Python-`for`-Schleifen ermöglichen die programmatische Erzeugung mehrerer gleichartiger Tabellen. Die Doku warnt ausdrücklich: *"ensure that the list of values passed to the `for` loop is always additive"* — die an die Schleife übergebene Werteliste sollte stets nur ergänzt, nie verkürzt werden, um das versehentliche Löschen zuvor definierter Datasets zu vermeiden.

**Vollständiges Beispiel** — pro Region in `region_list` wird eine eigene Materialized View erzeugt:

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import collect_list, col

@dp.temporary_view()
def customer_orders():
    orders = spark.read.table("samples.tpch.orders")
    customer = spark.read.table("samples.tpch.customer")
    return (orders.join(customer, orders.o_custkey == customer.c_custkey)
        .select(
            col("c_custkey").alias("custkey"),
            col("c_name").alias("name"),
            col("c_nationkey").alias("nationkey"),
            col("c_phone").alias("phone"),
            col("o_orderkey").alias("orderkey"),
            col("o_orderstatus").alias("orderstatus"),
            col("o_totalprice").alias("totalprice"),
            col("o_orderdate").alias("orderdate"))
    )

@dp.temporary_view()
def nation_region():
    nation = spark.read.table("samples.tpch.nation")
    region = spark.read.table("samples.tpch.region")
    return (nation.join(region, nation.n_regionkey == region.r_regionkey)
        .select(
            col("n_name").alias("nation"),
            col("r_name").alias("region"),
            col("n_nationkey").alias("nationkey")
        )
    )

region_list = spark.read.table("samples.tpch.region").select(collect_list("r_name")).collect()[0][0]

for region in region_list:
    @dp.materialized_view(name=f"{region.lower().replace(' ', '_')}_customer_orders")
    def regional_customer_orders(region_filter=region):
        customer_orders = spark.read.table("customer_orders")
        nation_region = spark.read.table("nation_region")
        return (customer_orders.join(nation_region, customer_orders.nationkey == nation_region.nationkey)
            .select(
                col("custkey"),
                col("name"),
                col("phone"),
                col("nation"),
                col("region"),
                col("orderkey"),
                col("orderstatus"),
                col("totalprice"),
                col("orderdate")
            ).filter(f"region = '{region_filter}'")
        )
```

### Die Closure-Falle

Ein kritisches Detail: Funktionen müssen die Schleifenvariable direkt als **Default-Parameter** referenzieren, statt sie per Closure einzufangen — sonst würden am Ende alle erzeugten Tabellen auf den Wert der *letzten* Iteration verweisen.

**Falsch** (Closure-Falle — alle Tabellen erhalten am Ende denselben, letzten `t_name`-Wert):

```python
from pyspark import pipelines as dp

tables = ["t1", "t2", "t3"]
for t_name in tables:
    @dp.materialized(name=t_name)
    def create_table():
        return spark.read.table(t_name)
```

**Richtig — Variante 1: übergeordnete Funktion** (jeder Aufruf erhält einen eigenen, isolierten Funktionsbereich):

```python
from pyspark import pipelines as dp

def create_table(table_name):
    @dp.materialized_view(name=table_name)
    def t():
        return spark.read.table(table_name)

tables = ["t1", "t2", "t3"]
for t_name in tables:
    create_table(t_name)
```

**Richtig — Variante 2: Default-Parameter** (bindet den aktuellen Wert von `t_name` zum Definitionszeitpunkt an den Funktionsparameter):

```python
from pyspark import pipelines as dp

tables = ["t1", "t2", "t3"]
for t_name in tables:
    @dp.materialized_view(name=t_name)
    def create_table(table_name=t_name):
        return spark.read.table(table_name)
```

---

## <a id="quellen">6. Quellen</a>

- Develop pipeline code with Python (Materialized-View-/Streaming-Tabelle-Beispiele, Expectations, `for`-Schleifen-Muster inkl. Closure-Falle): https://docs.databricks.com/aws/en/ldp/developer/python-dev

**Stand:** 2026-08-19.
