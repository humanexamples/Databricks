# Flows mit REPLACE WHERE für Standalone Streaming Tables (Databricks SQL)

Dieses Dokument behandelt die Quelle `docs.databricks.com/aws/en/ldp/dbsql/flows-replace-where` — die DBSQL/Standalone-spezifische Variante von REPLACE-WHERE-Flows. Ein anderer, parallel arbeitender Agent bearbeitet unter "06 Flows/Flows mit REPLACE WHERE.md" die allgemeine Pipeline-Variante (Quelle `ldp/flows-replace-where`, ohne `dbsql/`-Präfix). Siehe Abschnitt 8 für den direkten Vergleich beider Seiten.

## Abschnittsübersicht

1. [Grundkonzept](#grundkonzept)
2. [Voraussetzungen](#voraussetzungen)
3. [Primäre Anwendungsfälle](#anwendungsfaelle)
4. [Erstellungssyntax](#erstellung)
5. [Backfilling: Prädikat-Override und DML](#backfilling)
6. [Verhalten bei Full Refresh](#full-refresh)
7. [Inkrementeller Refresh](#inkrementell)
8. [Vergleich mit der allgemeinen `flows-replace-where`-Seite](#vergleich)
9. [Quellen](#quellen)

---

## <a id="grundkonzept">1. Grundkonzept</a>

REPLACE-WHERE-Flows ermöglichen die selektive Neuberechnung eines gezielten Datenausschnitts einer Streaming Table, ohne die gesamte Tabellenhistorie neu zu verarbeiten. Ist ein Prädikat definiert, werden alle passenden Zeilen gelöscht und durch erneute Auswertung der Quellabfrage für denselben Prädikatsbereich neu erzeugt ("all rows matching the predicate are deleted and replaced by re-evaluating the source query for that same predicate range"). Nicht passende Zeilen bleiben unverändert.

## <a id="voraussetzungen">2. Voraussetzungen</a>

Databricks empfiehlt Unity Catalog und Serverless Compute. **Inkrementeller Refresh wird ausschließlich auf Serverless Compute unterstützt** ("Incremental refresh is only supported on serverless compute").

## <a id="anwendungsfaelle">3. Primäre Anwendungsfälle</a>

- Inkrementelle Batch-Verarbeitung ohne Streaming-Semantik
- Selektive Neuverarbeitung von Zeilen über Prädikate
- Szenarien, die über die Fähigkeiten von Materialized Views hinausgehen: verlängerte Aufbewahrung, Schema-Evolution, Vermeidung unnötiger Neuberechnung

## <a id="erstellung">4. Erstellungssyntax</a>

Standalone Streaming Tables werden über `FLOW REPLACE WHERE` in Kombination mit `CREATE OR REFRESH STREAMING TABLE` erstellt. Die `BY NAME`-Klausel ist erforderlich, damit Spalten nach Namen statt nach Position zugeordnet werden ("BY NAME is required. It ensures columns are matched by name rather than position.").

```sql
CREATE OR REFRESH STREAMING TABLE orders_enriched
SCHEDULE EVERY 1 DAY
FLOW REPLACE WHERE date >= date_add(current_date(), -7) BY NAME
SELECT
  o.order_id,
  o.date,
  o.region,
  p.product_name,
  o.qty,
  o.price
FROM orders_fct o
JOIN product_dim p
  ON o.product_id = p.product_id;
```

## <a id="backfilling">5. Backfilling: Prädikat-Override und DML</a>

Zwei Mechanismen stehen für die Verarbeitung historischer Daten zur Verfügung:

### Prädikat-Override über `REFRESH STREAMING TABLE ... WHERE`

Führt die Quellabfrage einmalig für einen anderen Bereich erneut aus:

```sql
REFRESH STREAMING TABLE orders_enriched
WHERE date BETWEEN '2020-01-01' AND '2024-12-31';
```

```sql
REFRESH STREAMING TABLE orders_enriched
WHERE date >= date_add(current_date(), -30) ASYNC;
```

### DML-Anweisungen (direkter Insert, umgeht den Flow)

Für Daten aus anderen Quellen, die nicht über den Flow selbst eingespielt werden sollen:

```sql
INSERT INTO orders_enriched
SELECT *
FROM orders_enriched_legacy
WHERE date < '2025-01-01';
```

## <a id="full-refresh">6. Verhalten bei Full Refresh</a>

**Warnung laut Doku:** "A full refresh clears all existing data and re-executes the flow using only its defined predicate." Läuft eine Pipeline bereits seit einem Jahr mit einem 7-Tage-Prädikat, enthält die Tabelle nach einem Full Refresh nur noch die letzten 7 Tage — alle älteren Zeilen werden dauerhaft gelöscht.

```sql
REFRESH STREAMING TABLE orders_enriched FULL;
```

Um Full Refreshes zu verhindern, kann `pipelines.reset.allowed` auf `'false'` gesetzt werden:

```sql
CREATE OR REFRESH STREAMING TABLE orders_enriched
  TBLPROPERTIES (pipelines.reset.allowed = 'false')
  FLOW REPLACE WHERE date >= date_add(current_date(), -7) BY NAME
  ...
```

## <a id="inkrementell">7. Inkrementeller Refresh</a>

REPLACE-WHERE-Flows nutzen inkrementellen Refresh, wenn möglich (nur ein geänderter Teilbereich statt des gesamten Ersetzungsfensters wird neu verarbeitet) — verfügbar auf Serverless Compute, wenn unterstützte Query-Formen, auf Basisspalten beruhende Prädikate, deterministische Ausdrücke und ein stabiler Prädikatsbereich vorliegen. Andernfalls erfolgt ein Fallback auf vollständige Neuberechnung; die Gründe dafür werden im Pipeline-Event-Log protokolliert.

**Praxisbeispiele aus der Doku:**

```sql
-- Beispiel 1: Historische Aggregate aus Quelle mit begrenzter Aufbewahrung
CREATE OR REFRESH STREAMING TABLE events_agg
FLOW REPLACE WHERE date >= date_add(current_date(), -3) BY NAME
SELECT
  date,
  key,
  SUM(val) AS agg
FROM events_raw
GROUP BY ALL;
```

```sql
-- Beispiel 2: Neuberechnung bei Dimensionsänderungen vermeiden
CREATE OR REFRESH STREAMING TABLE fact_dim_join
FLOW REPLACE WHERE f.date >= date_add(current_date(), -1) BY NAME
SELECT
  f.date,
  f.user_id,
  d.region,
  f.revenue
FROM fact_table f
JOIN dim_users d
  ON f.user_id = d.user_id;
```

```sql
-- Beispiel 3: Neue Kennzahl ergänzen, ohne die volle Historie neu zu berechnen
-- (aktualisierte Definition, ersetzt die vorherige)
CREATE OR REFRESH STREAMING TABLE clickstream_daily
FLOW REPLACE WHERE event_date >= date_add(current_date(), -7) BY NAME
SELECT
  event_date,
  page_id,
  COUNT(*) AS clicks,
  COUNT(DISTINCT user_id) AS uniq_users
FROM clickstream_raw
GROUP BY ALL;
```

```sql
-- Beispiel 4: Kleines Zeitfenster iterieren, bevor die volle Historie befüllt wird
-- Initiales kurzes Fenster:
CREATE OR REFRESH STREAMING TABLE revenue_attribution
FLOW REPLACE WHERE event_date >= date_add(current_date(), -7) BY NAME
SELECT
  event_date,
  campaign_id,
  SUM(revenue) AS total_revenue
FROM marketing_events
GROUP BY ALL;

-- Historischen Bereich nachträglich befüllen (DML statt Prädikat-Override):
INSERT INTO revenue_attribution
SELECT
  event_date,
  campaign_id,
  SUM(revenue) AS total_revenue
FROM marketing_events
WHERE event_date < date_add(current_date(), -7)
GROUP BY ALL;
```

Empfehlungen: eine bewegliche untere Grenze (moving lower bound) verwenden, damit der Flow dauerhaft inkrementell-fähig bleibt; Prädikatsspalten in `GROUP BY`- und Join-Bedingungen aufnehmen, um die Prädikat-Pushdown-Optimierung zu ermöglichen.

---

## <a id="vergleich">8. Vergleich mit der allgemeinen `flows-replace-where`-Seite</a>

Die beiden Seiten behandeln denselben Grundmechanismus (REPLACE-WHERE-Flows), unterscheiden sich aber in mehreren für den jeweiligen Kontext relevanten Punkten:

| Aspekt | DBSQL/Standalone (`dbsql/flows-replace-where`, diese Datei) | Allgemein/Lakeflow-Pipeline (`ldp/flows-replace-where`) |
|---|---|---|
| Erstellungssyntax | `CREATE OR REFRESH STREAMING TABLE ... FLOW REPLACE WHERE ...` | `CREATE STREAMING TABLE` (ohne `OR REFRESH`) **oder** Langform mit separatem `CREATE FLOW ... INSERT INTO ... BY NAME REPLACE WHERE ...` |
| Python-Syntax | Nicht dokumentiert (Standalone-Objekte werden laut "Python nutzen (DBSQL).md" über `spark.sql()`-Strings angesprochen) | Dokumentiert über den `@dp.table(replace_where=...)`-Dekorator (`pyspark.pipelines`) |
| Backfilling-Mechanismus | SQL-Anweisung `REFRESH STREAMING TABLE ... WHERE ...` (optional `ASYNC`) sowie direkte `INSERT INTO`-DML | REST-API-basierter Prädikat-Override über den Pipelines-Updates-Endpunkt (`POST /api/2.0/pipelines/{pipeline_id}/updates` mit `replace_where_overrides`), zusätzlich ebenfalls direkte `INSERT INTO`-DML |
| Fallback-Gründe (Tabelle mit Enum-Werten wie `EXTERNAL_CHANGE_IN_REPLACE_WINDOW`, `REPLACE_WHERE_NOT_DETERMINISTIC`) | Ebenfalls als Tabelle dokumentiert, inhaltlich identisch zur allgemeinen Seite | Explizit als Tabelle dokumentiert |
| Explizite Limitations-Liste (Zieltabelle muss innerhalb der Pipeline erstellt werden; nur ein REPLACE-WHERE-Flow pro Zieltabelle; die Zieltabelle kann nicht zugleich Ziel eines anderen Flow-Typs sein; keine Expectations auf solchen Tabellen) | Nicht als eigener Abschnitt erfasst (laut Abruf) | Explizit als eigener "Limitations"-Abschnitt dokumentiert |
| Inhaltlicher Kern (Motivation, Full-Refresh-Warnung, Beispiele 1–4, Empfehlungen zu moving lower bound/GROUP BY) | Identisch bzw. nahezu wortgleich zur allgemeinen Seite | Identisch bzw. nahezu wortgleich zur DBSQL-Seite |

**Befund:** Die Seiten sind **nicht identisch** — der konzeptionelle Kern (Motivation, Beispiele, Full-Refresh-Warnung) ist zwischen beiden Seiten praktisch wortgleich, aber die DBSQL-Seite ist konsequent auf den Standalone-Kontext zugeschnitten: Sie verzichtet auf die Python-API und die REST-API-basierte Backfill-Steuerung der allgemeinen Pipeline-Seite und ersetzt Letztere durch eine einfachere, rein SQL-basierte `REFRESH STREAMING TABLE ... WHERE`-Anweisung — passend dazu, dass Standalone-Objekte nicht über die Pipelines-Update-API, sondern direkt per SQL verwaltet werden (vgl. "Refresh-Zeitplaene.md").

**Korrektur (2026-08-20):** Ein erneuter, gezielter Abruf hat die vormals als "Ungeklärt" markierte Frage geklärt: Die Fallback-Gründe-Tabelle existiert auch auf der DBSQL-Seite, mit identischen Enum-Werten. Nur der explizite "Limitations"-Abschnitt bleibt ein echter Unterschied — die DBSQL-Seite dokumentiert die Limitierungen nicht als eigenen, benannten Abschnitt.

---

## <a id="quellen">9. Quellen</a>

1. REPLACE WHERE flows for standalone streaming tables (AWS, DBSQL-spezifisch): https://docs.databricks.com/aws/en/ldp/dbsql/flows-replace-where
2. REPLACE WHERE flows in Lakeflow pipelines (AWS, allgemein, für Vergleich in Abschnitt 8 abgerufen — Haupt-Zuständigkeit liegt beim Agenten für "06 Flows/"): https://docs.databricks.com/aws/en/ldp/flows-replace-where
