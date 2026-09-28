# Best Practices für Lakeflow Pipelines — Übersicht

Dieses Dokument ist das erste von fünf in der Reihe "Best Practices" für Lakeflow Declarative Pipelines. Es fasst die zentrale Best-Practices-Seite zusammen, die auf die vier vertiefenden Unterseiten (siehe Dateien "Dimensionale Modellierung.md", "Verarbeitungsgarantien.md", "Datasets organisieren.md", "Produktionsreife.md") sowie zahlreiche weitere Konzeptseiten verweist.

## Abschnittsübersicht

1. [Dataset-Typ wählen](#dataset-typ)
2. [Deklaratives CDC statt imperativem MERGE](#cdc)
3. [Datenqualität mit Expectations durchsetzen](#expectations)
4. [Pipelines parametrisieren](#parametrisieren)
5. [Liquid Clustering für das Daten-Layout](#liquid-clustering)
6. [Streaming Best Practices](#streaming)
7. [Pipeline-Performance optimieren](#performance)
8. [Pipelines überwachen](#monitoring)
9. [Infrastruktur und Architektur](#infrastruktur)
10. [Referenzierte Unterseiten und Konzeptseiten](#referenzen)
11. [Quellen](#quellen)

---

## <a id="dataset-typ">1. Dataset-Typ wählen</a>

Die Doku empfiehlt, zwischen drei Dataset-Typen zu wählen:

- **Streaming Tables** für Dateningestion und Low-Latency-Transformationen
- **Materialized Views** für komplexe Transformationen mit inkrementellem Refresh
- **Temporäre Views** für Zwischenlogik innerhalb der Pipeline, ohne Speicherkosten

## <a id="cdc">2. Deklaratives CDC statt imperativem MERGE</a>

Databricks empfiehlt, deklarative `AUTO CDC`-Anweisungen statt imperativem `MERGE` für Change Data Capture zu verwenden.

## <a id="expectations">3. Datenqualität mit Expectations durchsetzen</a>

Datenqualität wird über Expectations mit drei Verletzungsrichtlinien durchgesetzt: `warn`, `drop`, `fail`. Ein Quarantäne-Muster erlaubt es, verworfene Datensätze für die spätere Untersuchung zu erhalten.

**SQL:**

```sql
CREATE OR REFRESH STREAMING TABLE orders_raw (
  CONSTRAINT valid_order_id EXPECT (order_id IS NOT NULL)) AS
SELECT * FROM STREAM read_files("/volumes/raw/orders", format => "json");

CREATE OR REFRESH STREAMING TABLE orders_clean (
  CONSTRAINT non_negative_amount EXPECT (amount >= 0) ON VIOLATION DROP ROW) AS
SELECT * FROM STREAM(orders_raw);

CREATE OR REFRESH STREAMING TABLE orders_critical (
  CONSTRAINT required_customer_id EXPECT (customer_id IS NOT NULL) ON VIOLATION FAIL UPDATE) AS
SELECT * FROM STREAM(orders_clean);
```

**Python:**

```python
from pyspark import pipelines as dp

@dp.table
@dp.expect("valid_order_id", "order_id IS NOT NULL")
def orders_raw():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .load("/volumes/raw/orders")

@dp.table
@dp.expect_or_drop("non_negative_amount", "amount >= 0")
def orders_clean():
    return spark.readStream.table("orders_raw")

@dp.table
@dp.expect_or_fail("required_customer_id", "customer_id IS NOT NULL")
def orders_critical():
    return spark.readStream.table("orders_clean")
```

## <a id="parametrisieren">4. Pipelines parametrisieren</a>

Empfohlen wird, Pipelines zu parametrisieren, um mehrere Umgebungen zu unterstützen, ohne Werte fest im Code zu verankern.

**SQL:**

```sql
CREATE OR REFRESH MATERIALIZED VIEW transaction_summary AS
SELECT account_id, COUNT(txn_id) AS txn_count, SUM(amount) AS total_amount
FROM ${source_catalog}.sales.transactions
GROUP BY account_id;
```

**Python:**

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import count, sum

@dp.materialized_view
def transaction_summary():
    source_catalog = spark.conf.get("source_catalog")
    return spark.read.table(f"{source_catalog}.sales.transactions") \
        .groupBy("account_id") \
        .agg(
            count("txn_id").alias("txn_count"),
            sum("amount").alias("total_amount")
        )
```

## <a id="liquid-clustering">5. Liquid Clustering für das Daten-Layout</a>

Empfohlen für selbstoptimierendes Daten-Layout, entweder automatisch (`CLUSTER BY AUTO`) oder manuell mit expliziten Spalten.

**SQL (automatisch):**

```sql
CREATE OR REFRESH STREAMING TABLE events
CLUSTER BY AUTO
AS SELECT * FROM STREAM read_files("/volumes/raw/events", format => "parquet");
```

**Python (automatisch):**

```python
from pyspark import pipelines as dp

@dp.table(cluster_by_auto=True)
def events():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "parquet") \
        .load("/volumes/raw/events")
```

**SQL (manuell):**

```sql
CREATE OR REFRESH STREAMING TABLE events
CLUSTER BY (event_date, region)
AS SELECT * FROM STREAM read_files("/volumes/raw/events", format => "parquet");
```

**Python (manuell):**

```python
from pyspark import pipelines as dp

@dp.table(cluster_by=["event_date", "region"])
def events():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "parquet") \
        .load("/volumes/raw/events")
```

## <a id="streaming">6. Streaming Best Practices</a>

### Watermarks für zustandsbehaftete Operationen

**SQL:**

```sql
CREATE OR REFRESH STREAMING TABLE event_counts AS
SELECT window(event_time, '1 minute') AS time_window, region, COUNT(*) AS cnt
FROM STREAM(events_raw)
  WATERMARK event_time DELAY OF INTERVAL 3 MINUTES
GROUP BY time_window, region;
```

**Python:**

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import window

@dp.table
def event_counts():
    return (
        spark.readStream.table("events_raw")
            .withWatermark("event_time", "3 minutes")
            .groupBy(window("event_time", "1 minute"), "region")
            .count()
    )
```

### Stream-Stream-Joins

**SQL:**

```sql
CREATE OR REFRESH STREAMING TABLE impression_clicks AS
SELECT imp.ad_id, imp.impression_time, clk.click_time
FROM STREAM(ad_impressions)
    WATERMARK impression_time DELAY OF INTERVAL 3 MINUTES AS imp
JOIN STREAM(user_clicks)
    WATERMARK click_time DELAY OF INTERVAL 3 MINUTES AS clk
ON imp.ad_id = clk.ad_id
  AND clk.click_time BETWEEN imp.impression_time
    AND imp.impression_time + INTERVAL 3 MINUTES;
```

**Python:**

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import expr

dp.create_streaming_table("impression_clicks")

@dp.append_flow(target="impression_clicks")
def join_impressions_and_clicks():
    impressions = spark.readStream.table("ad_impressions") \
        .withWatermark("impression_time", "3 minutes")
    clicks = spark.readStream.table("user_clicks") \
        .withWatermark("click_time", "3 minutes")
    return impressions.alias("imp").join(
        clicks.alias("clk"),
        expr("""
            imp.ad_id = clk.ad_id AND
            clk.click_time BETWEEN imp.impression_time AND imp.impression_time + INTERVAL 3 MINUTES
        """),
        "leftOuter"
    )
```

Erfordert Watermarks und zeitlich begrenzte Bedingungen bei Stream-Stream-Joins.

## <a id="performance">7. Pipeline-Performance optimieren</a>

Empfehlungen umfassen: Vermeidung kleiner Dateien durch geeignete Trigger-Intervalle, Behandlung von Daten-Skew mit Liquid Clustering, inkrementeller Refresh für Materialized Views, sowie Join-Optimierung über Broadcast-Hinweise.

**SQL:**

```sql
CREATE OR REFRESH MATERIALIZED VIEW enriched_orders AS
SELECT o.*, /*+ BROADCAST(p) */ p.product_name, p.category
FROM orders o
JOIN products p ON o.product_id = p.product_id;
```

**Python:**

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import broadcast

@dp.materialized_view
def enriched_orders():
    orders = spark.read.table("orders")
    products = spark.read.table("products")
    return orders.join(broadcast(products), "product_id")
```

## <a id="monitoring">8. Pipelines überwachen</a>

```sql
SELECT * FROM event_log('<pipeline-id>')
WHERE event_type = 'flow_progress'
ORDER BY timestamp DESC
LIMIT 100;
```

## <a id="infrastruktur">9. Infrastruktur und Architektur</a>

Weitere Empfehlungen: Serverless Compute verwenden; Pipeline-Code über Declarative Automation Bundles versionieren; Daten nach dem Medaillon-Architektur-Muster (Bronze/Silber/Gold) organisieren; bewusste Wahl zwischen Triggered-Modus (verarbeitet Daten und stoppt) für die meisten Anwendungsfälle und Continuous-Modus für Sub-Minuten-Latenzanforderungen.

## <a id="referenzen">10. Referenzierte Unterseiten und Konzeptseiten</a>

Am Seitenanfang referenzierte vertiefende Unterseiten (siehe eigene Dateien in diesem Ordner):

- Dimensional modeling in Lakeflow pipelines → "Dimensionale Modellierung.md"
- Processing guarantees in Lakeflow pipelines → "Verarbeitungsgarantien.md"
- Organize datasets across Lakeflow pipelines → "Datasets organisieren.md"
- Production readiness for Lakeflow pipelines → "Produktionsreife.md"

Im Fließtext zusätzlich referenzierte Konzeptseiten (außerhalb der Zuständigkeit dieser Dateireihe, zur Einordnung aufgeführt): Streaming tables; Materialized views; What are Lakeflow pipelines?; Change data capture and snapshots; The AUTO CDC APIs; Manage data quality with pipeline expectations; Expectation recommendations and advanced patterns; Use parameters with pipelines; Triggered vs. continuous pipeline mode; Configure pipelines; Use liquid clustering for tables; Create a source-controlled pipeline; Convert a pipeline into a bundle project; Declarative Automation Bundles; Optimize stateful processing with watermarks; Recover a pipeline from streaming checkpoint failure; Backfilling historical data with pipelines; Incremental refresh for materialized views; Monitor pipelines; Pipeline event log; Define custom monitoring of pipelines with event hooks; Serverless vs. classic compute for pipelines; Configure a serverless pipeline; Use real-time mode in Lakeflow pipelines.

---

## <a id="quellen">11. Quellen</a>

1. Lakeflow pipelines best practices (AWS): https://docs.databricks.com/aws/en/ldp/best-practices/
