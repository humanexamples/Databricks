# Best Practices, Produktionsreife und Einschränkungen von Lakeflow Declarative Pipelines

## 1. Best Practices — Übersicht

### 1.1 Dataset-Typ wählen

- **Streaming Tables** — Dateningestion, Low-Latency-Transformationen.
- **Materialized Views** — komplexe Transformationen mit inkrementellem Refresh.
- **Temporäre Views** — Zwischenlogik in der Pipeline, keine Speicherkosten.

### 1.2 Deklaratives CDC statt imperativem MERGE

Deklarative `AUTO CDC`-Anweisungen statt imperativem `MERGE` (siehe Kapitel CDC).

### 1.3 Datenqualität mit Expectations durchsetzen

Drei Verletzungsrichtlinien: `warn`, `drop`, `fail`. Quarantäne-Muster erhält verworfene Datensätze für spätere Untersuchung (siehe Kapitel Data Quality).

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

### 1.4 Pipelines parametrisieren

Für mehrere Umgebungen ohne fest verankerte Werte:

```sql
CREATE OR REFRESH MATERIALIZED VIEW transaction_summary AS
SELECT account_id, COUNT(txn_id) AS txn_count, SUM(amount) AS total_amount
FROM ${source_catalog}.sales.transactions
GROUP BY account_id;
```

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

### 1.5 Liquid Clustering für das Daten-Layout

Selbstoptimierendes Layout — automatisch (`CLUSTER BY AUTO`) oder manuell:

```sql
-- automatisch
CREATE OR REFRESH STREAMING TABLE events
CLUSTER BY AUTO
AS SELECT * FROM STREAM read_files("/volumes/raw/events", format => "parquet");

-- manuell
CREATE OR REFRESH STREAMING TABLE events
CLUSTER BY (event_date, region)
AS SELECT * FROM STREAM read_files("/volumes/raw/events", format => "parquet");
```

```python
from pyspark import pipelines as dp

# automatisch
@dp.table(cluster_by_auto=True)
def events():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "parquet") \
        .load("/volumes/raw/events")

# manuell
@dp.table(cluster_by=["event_date", "region"])
def events():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "parquet") \
        .load("/volumes/raw/events")
```

### 1.6 Streaming Best Practices

Watermarks für zustandsbehaftete Operationen:

```sql
CREATE OR REFRESH STREAMING TABLE event_counts AS
SELECT window(event_time, '1 minute') AS time_window, region, COUNT(*) AS cnt
FROM STREAM(events_raw)
  WATERMARK event_time DELAY OF INTERVAL 3 MINUTES
GROUP BY time_window, region;
```

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

Stream-Stream-Joins (Watermarks + zeitlich begrenzte Bedingung auf beiden Seiten erforderlich):

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

### 1.7 Pipeline-Performance optimieren

Empfehlungen: kleine Dateien durch geeignete Trigger-Intervalle vermeiden; Daten-Skew mit Liquid Clustering behandeln; inkrementeller Refresh für MVs; Join-Optimierung via Broadcast-Hinweise:

```sql
CREATE OR REFRESH MATERIALIZED VIEW enriched_orders AS
SELECT o.*, /*+ BROADCAST(p) */ p.product_name, p.category
FROM orders o
JOIN products p ON o.product_id = p.product_id;
```

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import broadcast

@dp.materialized_view
def enriched_orders():
    orders = spark.read.table("orders")
    products = spark.read.table("products")
    return orders.join(broadcast(products), "product_id")
```

### 1.8 Pipelines überwachen

```sql
SELECT * FROM event_log('<pipeline-id>')
WHERE event_type = 'flow_progress'
ORDER BY timestamp DESC
LIMIT 100;
```

(siehe ausführlich Kapitel Observability und Monitoring)

### 1.9 Infrastruktur und Architektur

- Serverless Compute verwenden.
- Pipeline-Code über Declarative Automation Bundles versionieren.
- Medaillon-Architektur (Bronze/Silber/Gold).
- Bewusste Wahl Triggered (verarbeitet + stoppt, meiste Fälle) vs. Continuous (Sub-Minuten-Latenz).

---

## 2. Verarbeitungsgarantien (Idempotenz und Exactly-once)

### 2.1 Grundbegriffe

- **Idempotenz:** gleiche Eingabedaten → gleiches Ergebnis, unabhängig von Ausführungsanzahl.
- **At-least-once:** jeder Datensatz verarbeitet, kann bei Wiederholung Duplikate erzeugen.
- **Exactly-once:** jeder Datensatz beeinflusst Ergebnis, als wäre er genau einmal verarbeitet.
- Lakeflow-Pipelines: standardmäßig idempotent, Exactly-once innerhalb eigener verwalteter Tabellen.

### 2.2 Funktionsweise: Exactly-once bei verwalteten Tabellen

Structured-Streaming-Checkpoints + Delta-transaktionale Writes: jeder Micro-Batch committet Quell-Offsets + Ausgabe gemeinsam — wiederholte Batches gelingen vollständig oder rollen vollständig zurück.

### 2.3 `AUTO CDC` statt handgeschriebenem `MERGE`

`AUTO CDC INTO` ist von sich aus idempotent bezüglich `keys`/`sequence_by` — wichtiges Argument gegenüber handgeschriebenem `MERGE`.

### 2.4 Transformationen idempotent halten

- Nicht-deterministische Funktionen in MVs vermeiden.
- Full Refreshes sicher gestalten: Upstream-Quellen müssen vollständige Historie erneut produzieren können.

### 2.5 Umgang mit At-least-once-Quellen

`dropDuplicatesWithinWatermark` — watermark-bewusst, kein unbegrenzter State nötig.

### 2.6 Grenzen der Exactly-once-Garantie

Gilt für **verwaltete Delta-zu-Delta-Flows**. Als At-least-once zu behandeln:

- `foreach_batch_sink` und benutzerdefinierte externe Writes
- Kafka als Sink
- benutzerdefinierte Python-Datenquellen

---

## 3. Produktionsreife

### 3.1 Definition

Produktionsreife = Pipeline läuft unbeaufsichtigt gegen echte Geschäftsdaten, Fehlschläge automatisch erkannt. Sechs Dimensionen: Datenqualität, Zuverlässigkeit, Observability, Deployment, Kosten, Governance.

### 3.2 Datenqualität — Checkliste

- Jedes für schlechte Daten anfällige Dataset hat mindestens eine Expectation (nicht nur Docstring-Annahme).
- Bewusste `warn`/`drop`/`fail`-Wahl: `fail` für Stopp-alles-Bedingungen (z. B. PK gebrochen), `drop` mit Quarantäne-Tabelle für sicher Verwerfbares, `warn` nur bei aktiv beobachtetem Trend.
- Data-Quality-Tab/Event-Log regelmäßig prüfen.

### 3.3 Zuverlässigkeit — Checkliste

- Bewusste Triggered- vs. Continuous-Wahl.
- Pipeline über Job-Scheduler/Lakeflow Job geplant, nicht manuell gestartet.
- Fehlschlag-Benachrichtigungen konfiguriert (E-Mail, Webhook, Event Hook).
- Checkpoint-Fehlschlag-Wiederherstellung getestet (siehe Observability-Kapitel).
- Pipeline läuft unter Service Principal, nicht persönlicher Identität.

### 3.4 Observability — Checkliste

- Event-Log-Speicherort bekannt, mit mindestens einer ausgeführten Abfrage.
- `system.lakeflow.pipelines`-Tabellen verifiziert oder Dashboard für Pipeline-Gesundheit erstellt.
- Trends bei Update-Dauer nachverfolgt.

### 3.5 Deployment und Change Management — Checkliste

- Pipeline über Bundle definiert/deployt (Code-Review, Versionskontrolle).
- Mindestens dev + prod (idealerweise dev/staging/prod).
- Umgebungsspezifische Werte parametrisiert, nicht hartkodiert.

### 3.6 Compute und Kosten — Checkliste

- Explizite Serverless-vs-Classic-Wahl (Classic-Entscheidung dokumentiert).
- Enhanced Autoscaling auf Classic-Clustern aktiviert.
- Regelmäßige Prüfung `system.billing.usage` (DBU-Verbrauch).

### 3.7 Governance — Checkliste

- Zieltabellen in Unity Catalog, bewusstes Layout.
- Least-Privilege: Service Principal liest/schreibt nur notwendige Objekte.

---

## 4. Einschränkungen von Lakeflow Declarative Pipelines

### 4.1 Nebenläufigkeit: Concurrent Pipeline Updates

- Workspace-Limit: **1000 gleichzeitige Pipeline-Updates**.
- Dataset-Anzahl je Pipeline: bestimmt durch Konfiguration + Workload-Komplexität.

### 4.2 Grenzen für Quell-Dateien und -Ordner

- Nur **einzelne** Notebooks/Dateien referenziert: Limit **100 Quell-Dateien**.
- **Ordner** referenziert: bis **50 Quell-Einträge** (Dateien/Ordner); (direkt/indirekt) referenzierte Dateien Limit **1000**.
- Bei > 100 Quell-Dateien: Ordner-Organisation nutzen (Pipeline Asset Browser).

### 4.3 Datasets als Ziel nur einer einzigen Operation

- Pipeline-Datasets können nur einmal definiert werden — nur Ziel einer einzigen Operation über alle Pipelines hinweg. **Ausnahme:** Streaming Tables mit Append-Flow-Verarbeitung erlauben mehrere Streaming-Quellen in dieselbe Streaming Table (siehe Kapitel Flows).

### 4.4 Identity-Columns

- **Gotcha:** Identity-Columns nicht unterstützt bei **AUTO-CDC**-Zieltabellen.
- Identity-Columns können bei MV-Updates neu berechnet werden — Databricks empfiehlt Identity-Columns nur bei Streaming Tables.

### 4.5 Zugriff durch externe Systeme

Standard: MVs/Streaming Tables nur von Databricks-Clients abrufbar (siehe Kapitel Sinks/externer Zugriff — External Data Access, Compatibility Mode).

### 4.6 Unity-Catalog-Compute-Anforderungen

Für UC-Pipelines-Compute gelten separat dokumentierte Anforderungen.

### 4.7 Time Travel

**Gotcha:** Delta-Time-Travel-Abfragen **nur bei Streaming Tables** unterstützt — bei MVs **nicht** unterstützt.

### 4.8 `pivot()`-Funktion nicht unterstützt

`pivot()` erfordert eager Laden der Eingabedaten zur Ausgabeschema-Berechnung — in Pipelines nicht unterstützt.

### 4.9 Ressourcen-Quoten

Für Lakeflow-Pipelines-Ressourcen-Quoten gelten separat dokumentierte Grenzen ("Resource limits").

**Stand:** 2026-09-14.
