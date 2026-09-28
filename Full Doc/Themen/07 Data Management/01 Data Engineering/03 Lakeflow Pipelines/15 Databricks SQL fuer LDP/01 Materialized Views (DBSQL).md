# Standalone Materialized Views (Databricks SQL)

Dieses Dokument beschreibt Materialized Views, die außerhalb einer Lakeflow-Pipeline über Databricks SQL bzw. Notebooks erstellt werden.

## Abschnittsübersicht

1. [Grundkonzept](#grundkonzept)
2. [Erstellungsmethoden](#erstellung)
3. [Refresh-Mechanismen](#refresh-mechanismen)
4. [Einschränkungen](#einschraenkungen)
5. [Kostenstruktur](#kosten)
6. [Verwaltung](#verwaltung)
7. [Quellen](#quellen)

---

## <a id="grundkonzept">1. Grundkonzept</a>

Standalone Materialized Views sind verwaltete Tabellen, die Abfrageergebnisse vorab berechnen und zwischenspeichern ("pre-compute and cache query results"), um Performance zu verbessern und Kosten für Datenverarbeitungs- und Analyse-Workloads zu reduzieren.

## <a id="erstellung">2. Erstellungsmethoden</a>

Es gibt drei primäre Ansätze:

### Ad-hoc (ohne Zeitplan)

```sql
CREATE OR REPLACE MATERIALIZED VIEW mv1
AS SELECT
  date,
  sum(sales) AS sum_of_sales
FROM
  base_table1
GROUP BY
  date;
```

### Trigger-basiert (automatischer Refresh bei Quelldatenänderung)

```sql
CREATE OR REPLACE MATERIALIZED VIEW mv_trigger
  TRIGGER ON UPDATE
AS SELECT
  date,
  sum(sales) AS sum_of_sales
FROM
  base_table1
GROUP BY
  date;
```

### Zeitplan-basiert (CRON)

```sql
CREATE OR REPLACE MATERIALIZED VIEW daily_revenue_by_region
  SCHEDULE CRON '0 30 3 * * ?' AT TIME ZONE 'UTC'
AS SELECT
  date_trunc('day', order_time) AS sales_date,
  region,
  sum(revenue) AS total_revenue,
  count(*) AS order_count
FROM
  orders
GROUP BY sales_date, region;
```

Details zu den Zeitplan-Optionen (`SCHEDULE EVERY`, `SCHEDULE CRON`, `TRIGGER ON UPDATE`) siehe Datei "Refresh-Zeitplaene.md".

## <a id="refresh-mechanismen">3. Refresh-Mechanismen</a>

Materialized Views nutzen Serverless-Pipelines für Refresh-Vorgänge. Das System unterstützt:

- **Inkrementeller Refresh** — aktualisiert nur geänderte Daten; setzt Delta-Tabellen mit aktiviertem Row Tracking voraus:

  ```sql
  ALTER TABLE source_table SET TBLPROPERTIES (delta.enableRowTracking = true);
  ```

- **Vollständiger Refresh** — ersetzt den gesamten Datensatz, wenn inkrementeller Refresh nicht kosteneffizient ist.

Refreshes können synchron (blockierend) oder asynchron (im Hintergrund) erfolgen:

```sql
REFRESH MATERIALIZED VIEW mv1;
```

```sql
REFRESH MATERIALIZED VIEW mv1 ASYNC;
```

## <a id="einschraenkungen">4. Einschränkungen</a>

Laut Doku bestehen folgende wesentliche Einschränkungen:

- Keine Identity Columns oder Surrogate Keys
- Keine Unterstützung für Time-Travel-Abfragen
- Change Data Feed lässt sich aus Materialized Views nicht lesen, sofern nicht explizit aktiviert
- Zugrunde liegende Dateien können Upstream-Daten enthalten, die in der View-Definition selbst nicht sichtbar sind

## <a id="kosten">5. Kostenstruktur</a>

Refreshes laufen auf Serverless Compute und werden separat vom SQL-Warehouse abgerechnet: "cost scales with the volume of data processed, not the size of your SQL warehouse."

## <a id="verwaltung">6. Verwaltung</a>

Refreshes lassen sich über den Catalog Explorer überwachen (Details siehe Datei "Materialized Views ueberwachen.md"). Löschen erfolgt per SQL-Befehl oder über die UI:

```sql
DROP MATERIALIZED VIEW mv1;
```

---

## <a id="quellen">7. Quellen</a>

1. Use standalone materialized views (AWS): https://docs.databricks.com/aws/en/ldp/dbsql/materialized
