# SQL vs. Python und Entwicklungsumgebung für Lakeflow Declarative Pipelines

## 1. SQL vs. Python — Entscheidungsregel

- Beide Sprachen: "äquivalente Funktionalität für die meisten Anwendungsfälle".
- Regel: *"If you can express your logic in SQL, use SQL. If you need programmatic control or a Python-only feature, use Python."*
- **SQL** — lesbare, deklarative, lineare Transformationsketten.
- **Python** — bei: Schleifen/Bedingungen (`for`, `if`), externe Bibliotheken (`faker`, `boto3`), UDFs, Python-exklusive Features.
- Eine Pipeline kann SQL + Python mischen, aber jede Sprache in eigener Datei.

| Nur in... | Feature |
|---|---|
| SQL | Iceberg-kompatible Materialized Views |
| Python | `create_auto_cdc_from_snapshot_flow()` |
| Python | Sinks allgemein, `foreach_batch_sink()` |

Beide: Streaming Tables, Materialized Views, temporäre Views, private Tabellen, Expectations (unterschiedliche Syntax).

## 2. SQL-Entwicklung

- `CREATE OR REFRESH` erzeugt Pipeline-Datasets; `STREAM`-Keyword = Streaming-Semantik.
- Dataflow-Graph wird **vor** jeder Ausführung aus allen Quelldateien gebaut — Code-Reihenfolge ≠ Ausführungsreihenfolge.

```sql
-- Materialized View
CREATE OR REFRESH MATERIALIZED VIEW basic_mv
AS SELECT * FROM samples.nyctaxi.trips;

-- Streaming Table (STREAM-Keyword erforderlich)
CREATE OR REFRESH STREAMING TABLE basic_st
AS SELECT * FROM STREAM samples.nyctaxi.trips;
-- Ergebnis: MV wird bei Refresh neu berechnet, ST verarbeitet nur neue Zeilen.

-- Änderungscommits in der Quelle überspringen (sonst Fehler)
CREATE OR REFRESH STREAMING TABLE basic_st
AS SELECT * FROM STREAM samples.nyctaxi.trips WITH (SKIPCHANGECOMMITS);

-- Auto Loader via read_files (STREAM = Streaming, ohne STREAM = Batch für MV)
CREATE OR REFRESH STREAMING TABLE ingestion_st
AS SELECT * FROM STREAM read_files("/databricks-datasets/retail-org/sales_orders", format => "json");

CREATE OR REFRESH MATERIALIZED VIEW batch_mv
AS SELECT * FROM read_files("/databricks-datasets/retail-org/sales_orders", format => "json");

-- Expectation
CREATE OR REFRESH STREAMING TABLE orders_valid(
  CONSTRAINT valid_date EXPECT (order_datetime IS NOT NULL AND length(order_datetime) > 0)
  ON VIOLATION DROP ROW
) AS SELECT * FROM STREAM read_files("/databricks-datasets/retail-org/sales_orders");
```

**Verkettete Datasets** (Streaming Table → Join → Aggregation), Katalog/Schema aus Pipeline-Defaults oder explizit; Legacy `LIVE`-Schema-Syntax wird in neuen Pipelines stillschweigend ignoriert:

```sql
CREATE OR REFRESH STREAMING TABLE orders(
  CONSTRAINT valid_date EXPECT (order_datetime IS NOT NULL AND length(order_datetime) > 0) ON VIOLATION DROP ROW
) AS SELECT * FROM STREAM read_files("/databricks-datasets/retail-org/sales_orders");

CREATE OR REFRESH MATERIALIZED VIEW customers
AS SELECT * FROM read_files("/databricks-datasets/retail-org/customers");

CREATE OR REFRESH MATERIALIZED VIEW customer_orders
AS SELECT c.customer_id, o.order_number, c.state,
  date(timestamp(int(o.order_datetime))) order_date
FROM orders o INNER JOIN customers c ON o.customer_id = c.customer_id;

CREATE OR REFRESH MATERIALIZED VIEW daily_orders_by_state
AS SELECT state, order_date, count(*) order_count
FROM customer_orders GROUP BY state, order_date;
-- Ergebnis: 4-stufige Pipeline orders -> customers -> customer_orders -> daily_orders_by_state
```

- **`PRIVATE`** (bei MV/ST) — keine externen Metadaten, nur pipeline-intern, besteht für Pipeline-Lebensdauer, darf Namen eines Katalogobjekts tragen (gewinnt intern). Früher `TEMPORARY`.
- **Hard-Delete** (z. B. DSGVO): bei ST mit Deletion Vectors zusätzliche Delta-Operationen nötig; bei MV Quelle löschen + Refresh.
- **`SET`** parametrisiert nachfolgende Definitionen in derselben Datei, gelesen via `${}`:

```sql
SET startDate='2025-01-01';
CREATE OR REFRESH MATERIALIZED VIEW filtered
AS SELECT * FROM src WHERE date > ${startDate}
-- mehrere Werte = mehrere SET-Statements
```

**Einschränkungen:** kein `PIVOT` (erfordert eager Laden). `CREATE OR REFRESH LIVE TABLE` veraltet → `CREATE OR REFRESH MATERIALIZED VIEW`.

**Nur aus Databricks SQL, nicht aus einer Pipeline:** `ALTER STREAMING TABLE`, `ALTER MATERIALIZED VIEW`, `EXPLAIN CREATE MATERIALIZED VIEW`. Python-UDFs in SQL nutzbar, müssen aber vorab in Python-Dateien definiert sein.

## 3. Python-Entwicklung

Python-Funktionen müssen eine DataFrame zurückgeben; der Dekorator bestimmt den Dataset-Typ.

```python
from pyspark import pipelines as dp

@dp.materialized_view()
def basic_mv():
    return spark.read.table("samples.nyctaxi.trips")   # Batch-Read

@dp.table()
def basic_st():
    return spark.readStream.table("samples.nyctaxi.trips")   # Streaming-Read

# Mit explizitem Namen
@dp.materialized_view(name = "trips_mv")
def basic_mv():
    return spark.read.table("samples.nyctaxi.trips")
```

Verkettung mit Join + Aggregation:

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col

@dp.table()
@dp.expect_or_drop("valid_date", "order_datetime IS NOT NULL AND length(order_datetime) > 0")
def orders():
    return (spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/databricks-datasets/retail-org/sales_orders"))

@dp.materialized_view()
def customers():
    return spark.read.format("csv").option("header", True).load("/databricks-datasets/retail-org/customers")

@dp.materialized_view()
def customer_orders():
    return (spark.read.table("orders")
        .join(spark.read.table("customers"), "customer_id")
        .select("customer_id", "order_number", "state",
            col("order_datetime").cast("int").cast("timestamp").cast("date").alias("order_date")))

@dp.materialized_view()
def daily_orders_by_state():
    return (spark.read.table("customer_orders")
        .groupBy("state", "order_date").count().withColumnRenamed("count", "order_count"))
```

Auto Loader: `cloudFiles`-Format. Data Quality: `@dp.expect_or_drop()` + Expectations-Familie.

### 3.1 Dynamische Tabellenerzeugung (`for`-Schleife)

- Werteliste immer nur ergänzen, nie verkürzen (sonst werden bestehende Datasets gelöscht).

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import collect_list, col

@dp.temporary_view()
def customer_orders():
    orders = spark.read.table("samples.tpch.orders")
    customer = spark.read.table("samples.tpch.customer")
    return (orders.join(customer, orders.o_custkey == customer.c_custkey)
        .select(col("c_custkey").alias("custkey"), col("c_name").alias("name"),
            col("c_nationkey").alias("nationkey"), col("c_phone").alias("phone"),
            col("o_orderkey").alias("orderkey"), col("o_orderstatus").alias("orderstatus"),
            col("o_totalprice").alias("totalprice"), col("o_orderdate").alias("orderdate")))

@dp.temporary_view()
def nation_region():
    nation = spark.read.table("samples.tpch.nation")
    region = spark.read.table("samples.tpch.region")
    return (nation.join(region, nation.n_regionkey == region.r_regionkey)
        .select(col("n_name").alias("nation"), col("r_name").alias("region"), col("n_nationkey").alias("nationkey")))

region_list = spark.read.table("samples.tpch.region").select(collect_list("r_name")).collect()[0][0]

for region in region_list:
    @dp.materialized_view(name=f"{region.lower().replace(' ', '_')}_customer_orders")
    def regional_customer_orders(region_filter=region):
        customer_orders = spark.read.table("customer_orders")
        nation_region = spark.read.table("nation_region")
        return (customer_orders.join(nation_region, customer_orders.nationkey == nation_region.nationkey)
            .select(col("custkey"), col("name"), col("phone"), col("nation"), col("region"),
                col("orderkey"), col("orderstatus"), col("totalprice"), col("orderdate"))
            .filter(f"region = '{region_filter}'"))
# Ergebnis: eine Materialized View pro Region, z. B. europe_customer_orders, asia_customer_orders, ...
```

**Closure-Falle:** Schleifenvariable per Closure eingefangen statt als Default-Parameter → alle Tabellen erhalten am Ende denselben letzten Wert.

```python
# Falsch — alle Tabellen bekommen den letzten Wert ("t3")
tables = ["t1", "t2", "t3"]
for t_name in tables:
    @dp.materialized(name=t_name)
    def create_table():
        return spark.read.table(t_name)

# Richtig 1 — übergeordnete Funktion (eigener Scope je Aufruf)
def create_table(table_name):
    @dp.materialized_view(name=table_name)
    def t():
        return spark.read.table(table_name)

tables = ["t1", "t2", "t3"]
for t_name in tables:
    create_table(t_name)

# Richtig 2 — Default-Parameter (bindet Wert zum Definitionszeitpunkt)
tables = ["t1", "t2", "t3"]
for t_name in tables:
    @dp.materialized_view(name=t_name)
    def create_table(table_name=t_name):
        return spark.read.table(table_name)
```

### 3.2 Python-API — Übersicht

```python
from pyspark import pipelines as dp
```

Funktionen/Dekoratoren: `append_flow`, `create_auto_cdc_flow` (vormals `apply_changes`), `create_auto_cdc_from_snapshot_flow` (vormals `apply_changes_from_snapshot`), `create_table`, `create_sink`, `create_streaming_table`, `expect`/`expect_or_drop`/`expect_or_fail`/`expect_all`/`expect_all_or_drop`/`expect_all_or_fail`, `foreach_batch_sink`, `materialized_view`, `replace_flow`, `table`, `temporary_view`, `update_flow`.

- Funktionskörper: nur der zur Dataset-Definition nötige Code. **Verboten:** `collect()`, `count()`, `toPandas()`, `save()`, `saveAsTable()`, `start()`, `toTable()`; keine außerhalb der Funktion definierten DataFrames referenzieren.
- Legacy-Modul `dlt` weiterhin nutzbar, aber `pyspark.pipelines` empfohlen.

```python
from pyspark import pipelines as dp

@dp.table()
def function_name():
    return (query)
```

Lesevorgänge typischerweise über `spark.read`/`spark.readStream` (Tabellen, Dateipfade) oder `spark.sql()`. Dekoratorwahl bestimmt Ergebnistyp: `@dp.table()` = Streaming, `@dp.materialized_view()` = Batch. Verkettung: in einer Funktion oder über `@dp.temporary_view()`-Zwischenschritte.

## 4. Metaprogrammierung

Innere Funktionen werden **lazy** registriert (Dekorator führt nicht sofort aus) → eine Factory-Funktion mit `@dp.table` innen lässt sich mehrfach mit anderen Parametern aufrufen, ohne Code-Duplizierung. Anders als bei der `for`-Closure-Falle bekommt jeder Aufruf einer äußeren Funktion einen eigenen Scope.

```python
import functools
from pyspark import pipelines as dp
from pyspark.sql.functions import *

@dp.table(name="raw_fire_department", comment="raw table for fire department response")
@dp.expect_or_drop("valid_received", "received IS NOT NULL")
@dp.expect_or_drop("valid_response", "responded IS NOT NULL")
@dp.expect_or_drop("valid_neighborhood", "neighborhood != 'None'")
def get_raw_fire_department():
  return (
    spark.read.format('csv').option('header', 'true').option('multiline', 'true')
      .load('/databricks-datasets/timeseries/Fires/Fire_Department_Calls_for_Service.csv')
      .withColumnRenamed('Call Type', 'call_type')
      .withColumnRenamed('Received DtTm', 'received')
      .withColumnRenamed('Response DtTm', 'responded')
      .withColumnRenamed('Neighborhooods - Analysis Boundaries', 'neighborhood')
      .select('call_type', 'received', 'responded', 'neighborhood'))

all_tables = []
def generate_tables(call_table, response_table, filter):
  @dp.table(name=call_table, comment="top level tables by call type")
  def create_call_table():
    return spark.sql("""
      SELECT unix_timestamp(received,'M/d/yyyy h:m:s a') as ts_received,
        unix_timestamp(responded,'M/d/yyyy h:m:s a') as ts_responded, neighborhood
      FROM raw_fire_department WHERE call_type = '{filter}'
    """.format(filter=filter))
  @dp.table(name=response_table, comment="top 10 neighborhoods with fastest response time")
  def create_response_table():
    return spark.sql("""
      SELECT neighborhood, AVG((ts_received - ts_responded)) as response_time
      FROM {call_table} GROUP BY 1 ORDER BY response_time LIMIT 10
    """.format(call_table=call_table))
  all_tables.append(response_table)

generate_tables("alarms_table", "alarms_response", "Alarms")
generate_tables("fire_table", "fire_response", "Structure Fire")
generate_tables("medical_table", "medical_response", "Medical Incident")

@dp.table(name="best_neighborhoods", comment="which neighbor appears in the best response time list the most")
def summary():
  target_tables = [dp.read(t) for t in all_tables]
  unioned = functools.reduce(lambda x, y: x.union(y), target_tables)
  return (unioned.groupBy(col("neighborhood")).agg(count("*").alias("score")).orderBy(desc("score")))
# Ergebnis: 3x (Roh-Tabelle je Call-Typ + Top-10-Response-Tabelle) + 1 zusammenfassende best_neighborhoods-Tabelle,
# aus einer einzigen generate_tables()-Factory statt dreifacher Code-Duplizierung.
```

## 5. Environment-Versionen

- Fixiert Python-Version + vorinstallierte Bibliotheken, entkoppelt von Databricks-Runtime-Upgrades.
- Voraussetzung: Unity Catalog (kein Hive Metastore). Unterstützt: Version 3 und 4, serverlos + klassisch.
- Konfiguration: UI-Dropdown, REST API (`environment`-Block: `environment_version`, `dependencies`), Bundle-YAML (`environment_version`/`dependencies`).
- **Auto-Migration** ohne explizite `environment_version`: ausgenommen bei ungelösten Spark-Connect-Warnungen, ohne Unity Catalog, oder mit `foreach_batch`-Sinks/Event Hooks/AUTO CDC/Custom Images. Schutz: Verhaltensprüfung (Output-Pläne-Vergleich) + Auto-Rollback bei Fehlschlag. Manuell gesetzte Version wird nie überschrieben. Effektive Version im Event Log: `runtime_details.effective_environment_version`.
- Environment-Versionen führen Code über **Spark Connect** aus → Verhaltensänderungen möglich (siehe unten).

## 6. Environment-Versionskompatibilität (Spark Connect)

- Fehlschlag bei: Mutation des Spark-Session-Zustands innerhalb einer dekorierten Funktion, oder Nutzung von `SparkContext`/`RDD`/`SQLContext`/Py4J.
- **Verschachtelte DataFrame-Konstruktion:** Verhalten hängt vom Zeitpunkt der Session-Zustandsänderung relativ zur DataFrame-Erzeugung ab.
- **Veränderlicher UDF-Zustand:** UDF verwendet den Wert einer globalen Variable zum **Definitionszeitpunkt**, nicht zum Aufrufzeitpunkt.
- Kompatibilitäts-Scan: `pipelines.environmentVersion.enableCompatibilityScan = true` → `BehaviorChangeInSparkConnect`-`WARN`-Event im Event Log, blockiert Aktivierung bis behoben.
- Migrations-Ablauf: Scan aktivieren → Lauf prüfen → Code anpassen → Version aktivieren → verifizieren.
- Betroffene Kategorien: DB-/Katalog-Mutationen, Spark-Config-Mutationen, temporäre-View-Ersetzung, UDF-/UDTF-Mutationen, Eager-Ausführung in Flow-Funktionen.

## 7. Externe Python-Abhängigkeiten

Zwei Muster: (1) Environment-Einstellungen (Pakete für alle Quelldateien), (2) Import von Workspace-Dateien.

- UI: Pipeline-Editor → **Settings** → **Pipeline environment** → **Add dependency** → Paket + fixierte Version (z. B. `simplejson==3.19.*`). Wheel direkt aus UC-Volume installierbar (`/Volumes/.../ldpfns-1.0-py3-none-any.whl`).
- **Keine JVM-Bibliotheken** (nur SQL/Python unterstützt).
- `dbutils.library.restartPython()` nicht unterstützt — Abhängigkeiten nur über Environment-Einstellungen.
- Init-Skripte: nur Classic Compute, nicht Serverless — Environment-Einstellungen bevorzugen.

## 8. DLT-Meta

- Metadatengetriebenes Metaprogrammierungs-Framework: generiert Python-Code aus JSON/YAML statt Bronze/Silver-Pipelines manuell zu schreiben.
- Einsatz: viele Tabellen effizient ingestieren/bereinigen, einheitliche Standards über Pipelines hinweg.
- Ablauf: (1) Metadatendateien (Quellen, Ausgaben, Qualitätsregeln) → (2) Kompilierung zu `DataflowSpec` → (3) Bronze-Pipelines generiert → (4) Silver-Pipelines generiert.
- Status: Databricks-Labs-Open-Source, **nicht offiziell unterstützt**, kein SLA.

**Stand:** 2026-09-14.
