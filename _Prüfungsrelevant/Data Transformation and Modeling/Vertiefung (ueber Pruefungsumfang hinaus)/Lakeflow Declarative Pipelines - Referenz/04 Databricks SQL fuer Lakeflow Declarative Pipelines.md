# Databricks SQL für Lakeflow Declarative Pipelines (Standalone Pipelines)

## 1. Grundkonzept

- Standalone Pipelines = "standalone materialized views and streaming tables outside of a Lakeflow pipeline using simple query syntax" — Databricks verwaltet die Pipeline automatisch.
- Erstellbar über SQL-Warehouse oder Notebook auf Serverless General Compute.
- Früherer Name: "Pipelines for Databricks SQL".

## 2. Anforderungen und Compute

- **Voraussetzung:** serverless-fähiger, Unity-Catalog-fähiger Workspace + SQL-Warehouse oder Notebook auf Serverless General Compute.
- **Berechtigungen (Owner):** `SELECT` auf Basistabellen, `USE CATALOG`/`USE SCHEMA` auf Quell- und Ziel-Schema, `CREATE MATERIALIZED VIEW` (MV) bzw. `CREATE TABLE` (ST) auf Ziel-Schema; für Refresh: `REFRESH`-Privileg.
- **Inkrementeller Refresh (MV):** setzt Row Tracking auf Delta-Quellen voraus.
- **SQL-Warehouse:** Unity-Catalog-fähiges Pro-/Serverless-Warehouse, Serverless-fähige Region, akzeptierte Nutzungsbedingungen.
- **Notebook (Beta):** Serverless General Compute, DBR **18.1+**, eingeschränkte Regionen. Einschränkungen: nur Owner refresht, kein async Refresh, kein Preview-Channel, Refresh nur auf gleichem Compute-Typ wie Erstellung, keine Kostenzuordnung, kein vertikales Autoscaling bei Fehlern, keine Retry bei Schema-Upgrades, kein Performance-Modus wählbar.
- **Abfrage:** SQL-Warehouse/Lakeflow-UI/Standard-Compute mit `SELECT` + `USE CATALOG`/`USE SCHEMA`.

## 3. Standalone Materialized Views

```sql
-- Ad-hoc
CREATE OR REPLACE MATERIALIZED VIEW mv1
AS SELECT date, sum(sales) AS sum_of_sales FROM base_table1 GROUP BY date;

-- Trigger-basiert (Refresh bei Quelländerung)
CREATE OR REPLACE MATERIALIZED VIEW mv_trigger
  TRIGGER ON UPDATE
AS SELECT date, sum(sales) AS sum_of_sales FROM base_table1 GROUP BY date;

-- Zeitplan-basiert (CRON)
CREATE OR REPLACE MATERIALIZED VIEW daily_revenue_by_region
  SCHEDULE CRON '0 30 3 * * ?' AT TIME ZONE 'UTC'
AS SELECT date_trunc('day', order_time) AS sales_date, region,
  sum(revenue) AS total_revenue, count(*) AS order_count
FROM orders GROUP BY sales_date, region;
```

**Refresh:** inkrementell (nur geänderte Daten, braucht `ALTER TABLE source_table SET TBLPROPERTIES (delta.enableRowTracking = true);` auf der Quelle) oder vollständig; synchron/asynchron:

```sql
REFRESH MATERIALIZED VIEW mv1;
REFRESH MATERIALIZED VIEW mv1 ASYNC;
```

**Einschränkungen:** keine Identity Columns/Surrogate Keys, kein Time-Travel, kein CDF ohne explizite Aktivierung, Dateien können nicht in der Definition sichtbare Upstream-Daten enthalten.

**Kosten:** Refresh läuft auf Serverless (separat vom Warehouse abgerechnet) — *"cost scales with the volume of data processed, not the size of your SQL warehouse."*

```sql
DROP MATERIALIZED VIEW mv1;
```

## 4. Standalone Materialized Views konfigurieren

```sql
DESCRIBE TABLE EXTENDED sales;   -- Owner, Speicherort, Refresh-Status etc. (oder Catalog Explorer)
```

**Definition ändern:** erneutes `CREATE OR REPLACE MATERIALIZED VIEW` → löst vollständigen Refresh mit neuer Definition aus:

```sql
CREATE OR REPLACE MATERIALIZED VIEW sales
TBLPROPERTIES ('pipelines.channel' = 'preview') AS ...
```

**Zugriffskontrolle:** Owner/`MANAGE`-Privileg vergibt `SELECT`/`REFRESH`, Empfänger braucht keinen Zugriff auf Basistabellen:

```sql
CREATE MATERIALIZED VIEW mv_name AS SELECT * FROM source_table;
GRANT SELECT ON mv_name TO read_only_user;
GRANT REFRESH ON mv_name TO refresh_user;
REVOKE SELECT ON mv_name FROM read_only_user;
```

- Owner-Wechsel: nur über Catalog-Explorer-UI.
- Runtime-Channel: Standard = "current"; Preview über `TBLPROPERTIES ('pipelines.channel' = 'preview')`.
- Verliert Owner Zugriff auf Quelltabellen: View bleibt lesbar, Refresh schlägt fehl → View wird "stale".

## 5. Standalone Materialized Views überwachen

- **Catalog Explorer:** Refresh-Status, letzter Lauf, Zeitpläne, Tags, Fehlerdetails ("See refresh details").
- **`DESCRIBE EXTENDED`:** liefert Refresh-Status/-Zeitplan, Spalten, Refresh-Typ, Datengröße, Speicherort, Clustering, Deletion-Vector-/Row-Tracking-Status.

```sql
DESCRIBE TABLE EXTENDED sales AS JSON;

-- Event-Log (Owner-only)
CREATE VIEW my_event_log_view AS
SELECT * FROM event_log(TABLE(<catalog>.<schema>.<mv_name>));

SELECT * FROM my_event_log_view WHERE event_type = "update_progress" ORDER BY timestamp desc;

-- Refresh-Typ (inkrementell vs. vollständig)
SELECT timestamp, message FROM event_log(TABLE(my_catalog.my_schema.sales))
WHERE event_type = 'planning_information' ORDER BY timestamp desc;
-- Ergebnis-Beispiel: "Flow 'sales' has been planned to be executed as ROW_BASED."
```

- **Läufe überwachen:** Jobs & Pipelines-Seite (Filter "MV/ST"), Query-History-Tab (`REFRESH`-Statements + Pläne), Benachrichtigungen für Scheduled Refreshes.
- **Fehlgeschlagene Refreshes:** Pipeline-Monitoring-Seite (letzter Status + Historie + Event-Logs).

**Kostenzuordnung** über `system.billing.usage`:

```sql
-- Warehouse-Tags (automatisch vererbt)
SELECT usage_metadata.dlt_pipeline_id, custom_tags, SUM(usage_quantity) AS dbus
FROM system.billing.usage
WHERE billing_origin_product = 'SQL' AND usage_metadata.dlt_pipeline_id IS NOT NULL
  AND usage_date >= DATEADD(day, -30, current_date)
GROUP BY ALL ORDER BY dbus DESC;

-- Objekt-Level-Tags (manueller Join)
SELECT u.*, tag_info.tags
FROM system.billing.usage u
LEFT JOIN (
  SELECT t.catalog_name, t.schema_name, t.table_name,
    collect_list(named_struct('tag_name', t.tag_name, 'tag_value', t.tag_value)) AS tags
  FROM main.information_schema.table_tags t
  GROUP BY t.catalog_name, t.schema_name, t.table_name) tag_info
  ON tag_info.catalog_name = u.usage_metadata.uc_table_catalog
  AND tag_info.schema_name = u.usage_metadata.uc_table_schema
  AND tag_info.table_name = u.usage_metadata.uc_table_name
WHERE usage_metadata.uc_table_name is not null;
```

## 6. Standalone Streaming Tables

- "table registered to Unity Catalog with extra support for streaming or incremental data processing, defined outside of a Lakeflow pipeline" — automatisch erzeugte Serverless-Pipeline, Ersteller = Owner. Erstbefüllung = Quellbestand, danach nur neue Daten.
- Erstellung/Refresh: SQL-Warehouse oder Serverless General Compute.

```sql
CREATE OR REFRESH STREAMING TABLE sales
  SCHEDULE EVERY 1 hour
  AS SELECT product, price FROM STREAM raw_data;
-- Ergebnis: initialer Refresh startet sofort, verbraucht kein SQL-Warehouse-Compute (läuft auf Serverless-Pipeline)

-- Auto Loader via read_files
CREATE OR REFRESH STREAMING TABLE sales
  SCHEDULE EVERY 1 hour
  AS SELECT * FROM STREAM read_files("/Volumes/my_catalog/my_schema/my_volume/path/to/data", format => "json");

CREATE OR REFRESH STREAMING TABLE sales
  SCHEDULE EVERY 1 hour
  AS SELECT * FROM STREAM read_files('s3://mybucket/analysis/*/*/*.json', format => "json");
```

- **Kafka:** über `read_kafka`-Tabellenfunktion.

**CDC mit `AUTO CDC`:**

```sql
-- SCD Type 1
CREATE OR REFRESH STREAMING TABLE target
  FLOW AUTO CDC
  FROM stream(cdc_data.users)
  KEYS (userId)
  SEQUENCE BY sequenceNum
  STORED AS SCD TYPE 1;

-- SCD Type 2
CREATE OR REFRESH STREAMING TABLE target
  FLOW AUTO CDC
  FROM stream(cdc_data.users)
  KEYS (userId)
  APPLY AS DELETE WHEN operation = "DELETE"
  SEQUENCE BY sequenceNum
  COLUMNS * EXCEPT (operation, sequenceNum)
  STORED AS SCD TYPE 2;
```

- **`FLOW REPLACE WHERE`** — selektive Batch-Ersetzung eines Teilbereichs, keine vollständige Neuverarbeitung; für Joins/Aggregationen, späte Daten, Reprocessing, Schema-Evolution, Backfills (Details: Abschnitt 8).
- **`FLOW REPLACE USING`** (Beta) — hält Tabelle mit partiellen Snapshot-Streams synchron, ersetzt Zeilen je Key-Spalten:

```sql
CREATE OR REFRESH STREAMING TABLE payments_current
FLOW REPLACE USING (payment_id) SEQUENCE BY payment_date BY NAME
SELECT payment_id, booking_id, status, payment_date
FROM STREAM(samples.wanderbricks.payments);
```

  `BY NAME` Pflicht. Unterschied zur Pipeline-Variante: nur Definitionsweg (Inline-SQL) + automatisch verwaltetes Serverless-Compute. Abgrenzung: `REPLACE USING` = Snapshot-/Key-basiert, `REPLACE WHERE` = Prädikat-basiert.

- **Nur neue Daten:** `includeExistingFiles => false` überspringt beim Erstanlauf vorhandene Dateien:

```sql
CREATE OR REFRESH STREAMING TABLE sales
  SCHEDULE EVERY 1 hour
  AS SELECT * FROM STREAM read_files('/path/to/files', includeExistingFiles => false);
```

- **Runtime:** immer aktuellste Databricks-SQL-Runtime; `TBLPROPERTIES ('pipelines.channel' = 'preview')` bei Standalone-ST **nicht mehr unterstützt**.
- **Sensible Daten:** über Query-Definition ausschließen, oder Column Masks/Row Filters (`ROW FILTER`/`MASK`).

**Refresh-Verhalten:**

```sql
REFRESH STREAMING TABLE sales;   -- inkrementell: nur neue Zeilen seit letztem Update
REFRESH STREAMING TABLE sales FULL;   -- verarbeitet alle Quelldaten mit aktueller Definition neu
```

- Definitionsänderungen wirken **nicht rückwirkend**: entfernte Filter verarbeiten alte Zeilen nicht nach, geänderte Projektionen wirken nicht auf bereits verarbeitete Daten, Joins mit statischen Snapshots nutzen den Stand der Erstverarbeitung, geänderte `CAST` auf Bestandsspalten → Refresh-**Fehler**.
- `FULL` bei kurzlebigen Quellen (z. B. Kafka) nicht empfohlen — Daten werden abgeschnitten.

- **Zugriffskontrolle:**

| Privileg | Bedeutung |
|---|---|
| `SELECT` | Tabelle abfragen |
| `REFRESH` | Aktualisieren (mit Owner-Berechtigungen) |

```sql
CREATE OR REFRESH STREAMING TABLE st_name AS SELECT * FROM source_table;
GRANT SELECT ON st_name TO read_only_user;
GRANT REFRESH ON st_name TO refresh_user;
REVOKE SELECT ON st_name FROM read_only_user;
```

- Entzogener Quellzugriff: bestehende Daten bleiben lesbar, `REFRESH` schlägt fehl → Tabelle veraltet.
- Owner ändern: Catalog Explorer → Streaming Table → "About this streaming table" → Owner bearbeiten (Service Principals: Rolle "Service Principal User"). Verweis auf **Run as**-Nutzer in Pipeline-Einstellungen = Tabelle ist Teil einer Lakeflow-Pipeline, nicht Standalone.

**Hard-Delete (`REORG … PURGE`, Public Preview):** DBR 15.4+, nur bei aktivierten Deletion Vectors. Ablauf: Zeilen ändern/löschen → `REORG TABLE <st> APPLY (PURGE);` → Retention abwarten (Standard 7 Tage, `delta.deletedFileRetentionDuration`) → `REFRESH` → `VACUUM` automatisch binnen 24h.

**Query History (Public Preview):** zeigt alle ST-Anweisungen inkl. `CREATE` und async `REFRESH`, mit Query-Plänen.

**Compatibility Mode:** schreibgeschützte Version für externe Delta-/Iceberg-Clients ohne offene-API-Unterstützung.

## 7. Refresh-Zeitpläne

| Methode | Beschreibung | Anwendungsfall |
|---|---|---|
| Manuell | `REFRESH`-Statement / UI | Entwicklung, Tests, Ad-hoc |
| `TRIGGER ON UPDATE` | Auto-Refresh bei Upstream-Änderung | Produktion mit Frische-SLA |
| `SCHEDULE` | Feste Zeitintervalle | Vorhersehbare, zeitbasierte Anforderungen |
| SQL-Task in Job | Orchestrierung über Lakeflow Jobs | Komplexe, systemübergreifende Abhängigkeiten |

Manueller Refresh jederzeit zusätzlich möglich.

```sql
REFRESH MATERIALIZED VIEW <table-name>;
REFRESH STREAMING TABLE <table-name>;
-- Alternativ: Workspace-UI "Jobs & Pipelines" -> Pipeline -> "Start"
```

**`TRIGGER ON UPDATE`** — Auto-Refresh bei Upstream-Änderung, kein manuelles Zeitplan-Koordinieren nötig. **Limits:** max. 10 Upstream-Tabellen + 30 Upstream-Views je Pipeline, max. 1.000 Pipelines mit `TRIGGER ON UPDATE` je Workspace, min. Trigger-Intervall 1 Minute.

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.customer_orders
  TRIGGER ON UPDATE
AS SELECT o.customer_id, o.name, o.order_id FROM catalog.schema.orders o;

-- Drosselung
CREATE OR REFRESH STREAMING TABLE catalog.schema.customer_orders
  TRIGGER ON UPDATE AT MOST EVERY INTERVAL 5 MINUTES
AS SELECT o.customer_id, o.name, o.order_id FROM catalog.schema.orders o;
```

**`SCHEDULE`** — `SCHEDULE EVERY` (Intervalle) oder `SCHEDULE CRON` (präzise, auch sub-stündlich); `SCHEDULE`/`SCHEDULE REFRESH` äquivalent; legt automatisch einen Databricks-Job an.

```sql
CREATE OR REPLACE MATERIALIZED VIEW catalog.schema.hourly_metrics
  SCHEDULE EVERY 1 HOUR
AS SELECT date_trunc('hour', event_time) AS hour, count(*) AS events
FROM catalog.schema.raw_events GROUP BY 1;

-- sub-stündlich braucht CRON
CREATE OR REPLACE MATERIALIZED VIEW catalog.schema.regular_metrics
  SCHEDULE CRON '0 */15 * * * ?' AT TIME ZONE 'UTC'
AS SELECT date_trunc('minute', event_time) AS minute, count(*) AS events
FROM catalog.schema.raw_events
WHERE event_time > current_timestamp() - INTERVAL 1 HOUR GROUP BY 1;
```

Zeitplan einsehen: `DESCRIBE EXTENDED` oder Catalog Explorer ("Overview" → "Refresh status").

**SQL-Task in einem Job** — Refresh via Lakeflow Jobs orchestrieren (SQL-Editor "Schedule"-Button oder Jobs-UI SQL-Task):

```sql
REFRESH STREAMING TABLE catalog.schema.sales;
```

**Wichtig:** führt **nicht** zu kontinuierlicher Ausführung — jeder Job-Lauf = ein einzelner getriggerter Refresh (kontinuierlich nur bei vollständigen Lakeflow-Pipelines). Geeignet für mehrstufige Pipelines, bestehende Job-Orchestrierung, Job-Level-Alerting.

**Zeitplan ändern:**

```sql
ALTER STREAMING TABLE sales ADD TRIGGER ON UPDATE;
ALTER STREAMING TABLE catalog.schema.my_table ALTER SCHEDULE CRON '0 */5 * * * ?';   -- sub-stündlich braucht CRON
ALTER STREAMING TABLE catalog.schema.my_table DROP SCHEDULE;
```

System-Job selbst nicht direkt editierbar — nur über `CREATE OR REFRESH`/`ALTER`.

- **Status/Stop/Historie:** `DESCRIBE TABLE EXTENDED` oder Catalog Explorer; Stop über "Pipeline details" ("Stop"), CLI, oder `POST /api/2.0/pipelines/{pipeline_id}/stop`; Historie über Catalog Explorer → "Refresh schedule" → Job-Seite (48h-Graph).

**Timeouts:** Pipelines ab **14.08.2025**: `STATEMENT_TIMEOUT` falls gesetzt, sonst Warehouse-Timeout, sonst **Standard 2 Tage**. Ältere ST (letztes Update vor 14.08.2025): fest 2 Tage.

```sql
SET STATEMENT_TIMEOUT = '6h';
CREATE OR REFRESH MATERIALIZED VIEW my_catalog.my_schema.my_mv
  SCHEDULE EVERY 12 HOURS
AS SELECT * FROM large_source_table;
```

Sync nur bei explizitem `CREATE OR REFRESH` — nach Warehouse-Timeout-Änderung erneut ausführen, damit künftige Refreshes den neuen Wert nutzen.

**Benachrichtigungen (Beta):** über Job (SQL-Task) oder `SCHEDULE`-Klausel (Catalog Explorer → Overview → Refresh schedule → More options); Start/Erfolg/Fehlschlag; Standard = Owner nur bei Fehlschlag.

**Performance-Modus (Beta):** UI-Ausführung = Standard **Performance-optimiert**; SQL-geplant = wählbar ("Performance optimized" im Catalog Explorer); Standard-Modus = günstiger, aber höhere Startlatenz (**4–6 Minuten**). Gleiche SKU, Standard-Modus verbraucht weniger DBUs.

## 8. `REPLACE WHERE`-Flows für Standalone Streaming Tables

Selektive Neuberechnung eines Datenausschnitts statt gesamter Historie: passende Zeilen gelöscht + per Quellabfrage neu erzeugt, Rest unverändert.

- **Voraussetzung:** Unity Catalog + Serverless empfohlen; inkrementeller Refresh **nur** auf Serverless.
- **Einsatz:** inkrementelle Batch-Verarbeitung ohne Streaming-Semantik, selektive Prädikat-Neuverarbeitung, Fälle jenseits von MV-Fähigkeiten (Retention, Schema-Evolution, Neuberechnung vermeiden).

```sql
-- BY NAME ist Pflicht
CREATE OR REFRESH STREAMING TABLE orders_enriched
SCHEDULE EVERY 1 DAY
FLOW REPLACE WHERE date >= date_add(current_date(), -7) BY NAME
SELECT o.order_id, o.date, o.region, p.product_name, o.qty, o.price
FROM orders_fct o JOIN product_dim p ON o.product_id = p.product_id;
```

**Backfilling — Prädikat-Override (einmalig):**

```sql
REFRESH STREAMING TABLE orders_enriched
WHERE date BETWEEN '2020-01-01' AND '2024-12-31';

REFRESH STREAMING TABLE orders_enriched
WHERE date >= date_add(current_date(), -30) ASYNC;
```

**Backfilling — DML (umgeht den Flow):**

```sql
INSERT INTO orders_enriched
SELECT * FROM orders_enriched_legacy WHERE date < '2025-01-01';
```

**Full Refresh:** löscht alle Daten, führt Flow nur mit seinem Prädikat neu aus — Beispiel: 1 Jahr Historie + 7-Tage-Prädikat → nach `FULL` bleiben nur die letzten 7 Tage, Rest dauerhaft gelöscht.

```sql
REFRESH STREAMING TABLE orders_enriched FULL;

-- Full Refresh verhindern
CREATE OR REFRESH STREAMING TABLE orders_enriched
  TBLPROPERTIES (pipelines.reset.allowed = 'false')
  FLOW REPLACE WHERE date >= date_add(current_date(), -7) BY NAME
  ...
```

**Inkrementeller Refresh:** nur bei Serverless, unterstützten Query-Formen, Prädikaten auf Basisspalten, deterministischen Ausdrücken, stabilem Prädikatsbereich — sonst Fallback auf volle Neuberechnung (Grund im Event-Log).

```sql
-- Historische Aggregate, begrenzte Quell-Retention
CREATE OR REFRESH STREAMING TABLE events_agg
FLOW REPLACE WHERE date >= date_add(current_date(), -3) BY NAME
SELECT date, key, SUM(val) AS agg FROM events_raw GROUP BY ALL;

-- Neuberechnung bei Dimensionsänderung vermeiden
CREATE OR REFRESH STREAMING TABLE fact_dim_join
FLOW REPLACE WHERE f.date >= date_add(current_date(), -1) BY NAME
SELECT f.date, f.user_id, d.region, f.revenue
FROM fact_table f JOIN dim_users d ON f.user_id = d.user_id;

-- Neue Kennzahl ergänzen
CREATE OR REFRESH STREAMING TABLE clickstream_daily
FLOW REPLACE WHERE event_date >= date_add(current_date(), -7) BY NAME
SELECT event_date, page_id, COUNT(*) AS clicks, COUNT(DISTINCT user_id) AS uniq_users
FROM clickstream_raw GROUP BY ALL;

-- Kleines Fenster + historischer Bereich per DML
CREATE OR REFRESH STREAMING TABLE revenue_attribution
FLOW REPLACE WHERE event_date >= date_add(current_date(), -7) BY NAME
SELECT event_date, campaign_id, SUM(revenue) AS total_revenue
FROM marketing_events GROUP BY ALL;

INSERT INTO revenue_attribution
SELECT event_date, campaign_id, SUM(revenue) AS total_revenue
FROM marketing_events
WHERE event_date < date_add(current_date(), -7) GROUP BY ALL;
```

Empfehlungen: bewegliche untere Grenze (moving lower bound) für dauerhaft inkrementell-fähige Flows; Prädikatsspalten in `GROUP BY`/Join-Bedingungen für Prädikat-Pushdown.

**Unterschied zur Pipeline-Variante:** Standalone nutzt nur `CREATE OR REFRESH STREAMING TABLE ... FLOW REPLACE WHERE ...` (keine separate `CREATE FLOW`), Backfill via `REFRESH ... WHERE`-SQL (statt REST-API-Prädikat-Override), keine dokumentierte Python-API (nur `spark.sql()`-Strings, Abschnitt 9). Konzeptioneller Kern identisch.

## 9. Python für Standalone Pipelines

`spark.sql()` mit denselben SQL-DDL-Statements — kein dekorator-basiertes `pyspark.pipelines`/`@dp.table`.

**Voraussetzung:** Notebook auf Serverless General Compute, DBR **18.1+**, Beta mit regionalen Einschränkungen.

```python
# Materialized View
spark.sql("""
  CREATE OR REPLACE MATERIALIZED VIEW mv1
  AS SELECT date, sum(sales) AS sum_of_sales
  FROM base_table1 GROUP BY date
""")

# Streaming Table
spark.sql("""
  CREATE OR REFRESH STREAMING TABLE sales
  AS SELECT product, price FROM STREAM raw_data
""")

# Refresh (synchron auf Serverless General Compute)
spark.sql("REFRESH MATERIALIZED VIEW mv1")
spark.sql("REFRESH STREAMING TABLE sales")
```

**Parametrisiert** — Named Parameter (`:name`) über `args`; Objektnamen brauchen `IDENTIFIER()`:

```python
mv_name = "main.sales.regional_sales"
min_sales = 1000
spark.sql("""
  CREATE OR REPLACE MATERIALIZED VIEW IDENTIFIER(:mv)
  AS SELECT region, sum(sales) AS sum_of_sales
  FROM base_table1 WHERE sales > :min_sales GROUP BY region
""", args={"mv": mv_name, "min_sales": min_sales})
```

**Einschränkungen:** kein async Refresh auf Serverless General Compute, keine Kostenzuordnung pro Tabelle, benutzerdefinierte Warehouse-Tags werden nicht weitergegeben.

**Stand:** 2026-09-14.
