# Data Quality mit Expectations in Lakeflow Declarative Pipelines

## 1. Was sind Expectations?

- Optionale Klauseln in Erstellungsanweisungen von MVs, Streaming Tables oder Views — prüfen jeden durchfließenden Datensatz per Standard-SQL-Boolean-Ausdruck.
- Mehrere Expectations pro Dataset kombinierbar; über alle Dataset-Deklarationen einer Pipeline hinweg setzbar.
- **Einordnung:** Lakeflow-exklusive Erweiterung — reines Apache Spark Declarative Pipelines (SDP) kennt keine Expectations.
- Auch auf Streaming Tables/MVs einer eigenständigen ("standalone"), in Databricks SQL erstellten Pipeline definierbar: `CONSTRAINT expectation_name EXPECT (expectation_expr)` innerhalb `CREATE STREAMING TABLE`/`CREATE MATERIALIZED VIEW`.

## 2. Die drei Bestandteile einer Expectation

### 2.1 Expectation-Name

Eindeutig je Dataset; über mehrere Datasets einer Pipeline wiederverwendbar.

```python
@dp.table
@dp.expect("valid_customer_age", "age BETWEEN 0 AND 120")
def customers():
  return spark.readStream.table("datasets.samples.raw_customers")
```

```sql
CREATE OR REFRESH STREAMING TABLE customers(
  CONSTRAINT valid_customer_age EXPECT (age BETWEEN 0 AND 120)
) AS SELECT * FROM STREAM(datasets.samples.raw_customers);
```

### 2.2 Constraint-Klausel

- SQL-Bedingung, muss je Datensatz zu `true`/`false` auswerten. **Nicht** erlaubt: benutzerdefinierte Python-Funktionen, externe Dienste, Subqueries auf andere Tabellen.
- Python: `@dp.expect(<name>, <clause>)` — mehrere Decorators stapelbar. SQL: `CONSTRAINT <name> EXPECT (<clause>)` — mehrere per Komma.

```python
# Einfacher Constraint
@dp.expect("non_negative_price", "price >= 0")

# SQL-Funktionen
@dp.expect("valid_date", "year(transaction_date) >= 2020")

# CASE-Anweisungen
@dp.expect("valid_order_status", """
   CASE
     WHEN type = 'ORDER' THEN status IN ('PENDING', 'COMPLETED', 'CANCELLED')
     WHEN type = 'REFUND' THEN status IN ('PENDING', 'APPROVED', 'REJECTED')
     ELSE false
   END
""")

# Mehrere Constraints
@dp.expect("non_negative_price", "price >= 0")
@dp.expect("valid_purchase_date", "date <= current_date()")

# Komplexe Geschäftslogik
@dp.expect(
  "valid_subscription_dates",
  """start_date <= end_date
    AND end_date <= current_date()
    AND start_date >= '2020-01-01'"""
)

# Komplexe Boolean-Logik
@dp.expect("valid_order_state", """
   (status = 'ACTIVE' AND balance > 0)
   OR (status = 'PENDING' AND created_date > current_date() - INTERVAL 7 DAYS)
""")
```

```sql
CONSTRAINT non_negative_price EXPECT (price >= 0)

CONSTRAINT valid_date EXPECT (year(transaction_date) >= 2020)

CONSTRAINT valid_order_status EXPECT (
  CASE
    WHEN type = 'ORDER' THEN status IN ('PENDING', 'COMPLETED', 'CANCELLED')
    WHEN type = 'REFUND' THEN status IN ('PENDING', 'APPROVED', 'REJECTED')
    ELSE false
  END
)

-- Mehrere Constraints
CONSTRAINT non_negative_price EXPECT (price >= 0),
CONSTRAINT valid_purchase_date EXPECT (date <= current_date())

CONSTRAINT valid_subscription_dates EXPECT (
  start_date <= end_date
  AND end_date <= current_date()
  AND start_date >= '2020-01-01'
)

CONSTRAINT valid_order_state EXPECT (
  (status = 'ACTIVE' AND balance > 0)
  OR (status = 'PENDING' AND created_date > current_date() - INTERVAL 7 DAYS)
)
```

### 2.3 Aktion bei Regelverletzung

| Aktion | SQL | Python | Ergebnis |
|---|---|---|---|
| `warn` (Standard) | `EXPECT` | `dp.expect` | ungültige Datensätze trotzdem geschrieben; Metriken erfasst |
| `drop` | `EXPECT ... ON VIOLATION DROP ROW` | `dp.expect_or_drop` | ungültige Datensätze verworfen vor Schreiben; Anzahl protokolliert |
| `fail` | `EXPECT ... ON VIOLATION FAIL UPDATE` | `dp.expect_or_fail` | ungültige Datensätze verhindern Update; manuelles Eingreifen nötig |

- **Faustregel:** `fail` für kritische Geschäftsschlüssel; `drop` für gefahrlos filterbare Probleme; `warn` zur Beobachtung. Für Isolation ohne Fail/Drop: Quarantäne-Pattern (Abschnitt 8.10).

## 3. Retain / Drop / Fail im Detail

**Behalten (Standard):** sammelt Metriken, behält Verletzer.

```python
@dp.expect("valid timestamp", "timestamp > '2012-01-01'")
```

```sql
CONSTRAINT valid_timestamp EXPECT (timestamp > '2012-01-01')
```

**Verwerfen:** entfernt Verletzer aus Ziel.

```python
@dp.expect_or_drop("valid_current_page", "current_page_id IS NOT NULL AND current_page_title IS NOT NULL")
```

```sql
CONSTRAINT valid_current_page EXPECT (current_page_id IS NOT NULL and current_page_title IS NOT NULL) ON VIOLATION DROP ROW
```

**Fehlschlagen:** stoppt sofort bei erstem Verletzer, Transaktion wird atomar zurückgerollt.

```python
@dp.expect_or_fail("valid_count", "count > 0")
```

```sql
CONSTRAINT valid_count EXPECT (count > 0) ON VIOLATION FAIL UPDATE
```

- **Gotcha Triggered vs. Continuous:** Triggered — Fehlschlag eines Flows lässt parallele Flows nicht fehlschlagen. Continuous — Fehlschlag stoppt den Flow **und** alle davon abhängigen Flows.
- Für mehr Kontrolle über Orchestrierung bei Fehlschlag: Validierung und nachgelagerte Arbeit in separate Pipelines aufteilen, über Control-Flow koordinieren (Abschnitt 7).

## 4. Tracking-Metriken

- `warn`/`drop`-Metriken: Pipeline-UI, **Data quality**-Tab je Dataset.
- **Gotcha:** `fail` erfasst keine Metriken (Update schlägt beim ersten ungültigen Datensatz fehl).
- Standalone-Pipeline (Databricks SQL): kein Data-Quality-Tab — Event-Log abfragen.

## 5. Fehlerbehandlung bei fehlgeschlagenen Updates

- Bei Expectation-Verletzung (fail) muss Pipeline-Code korrigiert werden vor erneutem Lauf.
- `fail`-Expectations modifizieren Spark-Query-Plan, um Verletzungen zu erkennen/melden — oft identifizierbar bis zum verursachenden Eingabedatensatz:

```console
[EXPECTATION_VIOLATION.VERBOSITY_ALL] Flow 'sensor-pipeline' failed to meet the expectation. Violated expectations: 'temperature_in_valid_range'. Input data: '{"id":"TEMP_001","temperature":-500,"timestamp_ms":"1710498600"}'. Output record: '{"sensor_id":"TEMP_001","temperature":-500,"change_time":"2024-03-15 10:30:00"}'. Missing input data: false
```

## 6. Mehrere Expectations verwalten

- SQL + Python: mehrere Expectations pro Dataset. **Nur Python:** Gruppierung mit gemeinsamer Aktion via `expect_all`, `expect_all_or_drop`, `expect_all_or_fail` — Dictionary (Name → Constraint), über mehrere Datasets wiederverwendbar.

```python
valid_pages = {"valid_count": "count > 0", "valid_current_page": "current_page_id IS NOT NULL AND current_page_title IS NOT NULL"}

@dp.table
@dp.expect_all(valid_pages)
def raw_data():
  ...

@dp.table
@dp.expect_all_or_drop(valid_pages)
def prepared_data():
  ...

@dp.table
@dp.expect_all_or_fail(valid_pages)
def customer_facing_data():
  ...
```

## 7. Limitierungen

- Nur Streaming Tables, MVs, temporäre Views unterstützen Expectations — nur dort verfügbare Metriken.
- Keine Metriken bei: keinen Expectations definiert; nicht unterstütztem Operator im Flow; nicht unterstütztem Flow-Typ (z. B. **Sinks**); keinen Updates im Flow-Lauf; fehlender Pipeline-Konfiguration (`pipelines.metrics.flowTimeReporter.enabled`).
- `COMPLETED`-Flow evtl. ohne Metriken — stattdessen je Micro-Batch in `flow_progress`-Event mit Status `RUNNING`.
- Views nur bei Abfrage berechnet → Metriken ggf. nicht verfügbar; mehrfach abgefragte View kann mehrere Metrik-Sätze haben.
- **Gotcha:** `AUTO CDC FROM SNAPSHOT` unterstützt keine Expectations.

---

## 8. Erweiterte Expectation-Patterns

### 8.1 Grenzen einfacher Constraints

- `NOT NULL` bestätigt nur *Vorhandensein*, nicht *Korrektheit*. Nicht erkannt: numerische Anomalien (negative Menge), zeitliche Inkonsistenzen (Datum=1970-Default), Bereichsverletzungen (Rabatt=120%), Optionales-Feld-Regeln, Schema-Evolution (neue Spalte bricht Regeln), Datenverlust ohne Audit-Trail.
- Über zeilenbasierte Constraints hinaus: **tabellenübergreifende Validierung** (Row-Count-Abgleich, fehlende Datensätze, PK-Eindeutigkeit über mehrere Datasets).

### 8.2 Portable und wiederverwendbare Expectations

| Empfehlung | Wirkung |
|---|---|
| Expectation-Definitionen getrennt von Pipeline-Logik | leicht auf mehrere Datasets/Pipelines anwendbar |
| benutzerdefinierte Tags zur Gruppierung | Filterung anhand von Tags |
| Expectations konsistent auf ähnliche Datasets | identische Logik über Pipelines hinweg |

- **Gotcha:** dynamisches Laden von Expectations aus einer Datei wird in **SQL nicht** unterstützt.

**Variante: Delta-Tabelle als Regel-Repository.** `rules`-Tabelle hält Name/Constraint/Tag; `get_rules(tag)` liest passendes Dictionary.

```sql
CREATE OR REPLACE TABLE rules
AS SELECT col1 AS name, col2 AS constraint, col3 AS tag
FROM (VALUES
  ("website_not_null","Website IS NOT NULL","validity"),
  ("fresh_data","to_date(updateTime,'M/d/yyyy h:m:s a') > '2010-01-01'","maintained"),
  ("social_media_access","NOT(Facebook IS NULL AND Twitter IS NULL AND Youtube IS NULL)","maintained")
)
```

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import expr, col

def get_rules(tag):
  df = spark.read.table("rules").filter(col("tag") == tag).collect()
  return {row['name']: row['constraint'] for row in df}

@dp.table
@dp.expect_all_or_drop(get_rules('validity'))
def raw_farmers_market():
  return (
    spark.read.format('csv').option("header", "true")
      .load('/databricks-datasets/data.gov/farmers_markets_geographic_data/data-001/')
  )

@dp.table
@dp.expect_all_or_drop(get_rules('maintained'))
def organic_farmers_market():
  return spark.read.table("raw_farmers_market").filter(expr("Organic = 'Y'"))
```

- **Variante: Python-Modul als Regel-Repository** (`rules_module.py` neben Pipeline-Notebook, Liste von Dicts mit `name`/`constraint`/`tag`, gefiltert per `get_rules(tag)`) — funktional äquivalent zur Tabellen-Variante.

### 8.3 Validation-Tabellen und Pipeline-Control-Flow

Row-Count-Validation/PK-Uniqueness: separate **Validation-Tabelle** mit `expect_or_fail`. Wichtige Einschränkungen vor Einsatz als Gatekeeping:

- **Expectations erzwingen Datenqualität, keine Orchestrierung** — bestimmen, welche Datensätze ein Ziel erreichen, nicht ob andere Pipeline-Teile bedingt laufen.
- **`expect_or_fail`-Verhalten hängt vom Modus ab:** Triggered — nur betroffener Flow scheitert, andere laufen unabhängig weiter. Continuous — Flow + alle abhängigen Flows stoppen.
- **Eine Validation-Tabelle blockiert ihre nachgelagerten Tabellen nicht** — Lesen einer Validation-Tabelle lässt andere Datasets nicht auf deren Ergebnis warten.
- Um nachgelagerte Verarbeitung bei Fehlschlag zu stoppen: Validierung und nachgelagerte Arbeit in **separate Pipelines** aufteilen, über Job orchestrieren (nachgelagerter Task abhängig vom Validierungs-Task).

### 8.4 Row-Count-Validation

Zeilenanzahl-Gleichheit zwischen zwei Tabellen (kein Datenverlust bei Transformation):

```python
@dp.materialized_view(
  name="count_verification",
  comment="Validates equal row counts between tables"
)
@dp.expect_or_fail("no_rows_dropped", "a_count == b_count")
def validate_row_counts():
  return spark.sql("""
    SELECT * FROM
      (SELECT COUNT(*) AS a_count FROM table_a),
      (SELECT COUNT(*) AS b_count FROM table_b)""")
```

```sql
CREATE OR REFRESH MATERIALIZED VIEW count_verification(
  CONSTRAINT no_rows_dropped EXPECT (a_count == b_count)
) AS SELECT * FROM
  (SELECT COUNT(*) AS a_count FROM table_a),
  (SELECT COUNT(*) AS b_count FROM table_b)
```

### 8.5 Missing-Record-Detection

`LEFT OUTER JOIN` gegen Referenzkopie prüft, dass alle erwarteten Datensätze vorhanden sind:

```python
@dp.materialized_view(
  name="report_compare_tests",
  comment="Validates no records are missing after joining"
)
@dp.expect_or_fail("no_missing_records", "r_key IS NOT NULL")
def validate_report_completeness():
  return (
    spark.read.table("validation_copy").alias("v")
      .join(spark.read.table("report").alias("r"), on="key", how="left_outer")
      .select("v.*", "r.key as r_key")
  )
```

```sql
CREATE OR REFRESH MATERIALIZED VIEW report_compare_tests(
  CONSTRAINT no_missing_records EXPECT (r_key IS NOT NULL)
)
AS SELECT v.*, r.key as r_key FROM validation_copy v
  LEFT OUTER JOIN report r ON v.key = r.key
```

### 8.6 Primary-Key-Uniqueness

Gruppieren nach Key, prüfen dass jede Gruppe genau einen Eintrag hat:

```python
@dp.materialized_view(
  name="report_pk_tests",
  comment="Validates primary key uniqueness"
)
@dp.expect_or_fail("unique_pk", "num_entries = 1")
def validate_pk_uniqueness():
  return (
    spark.read.table("report")
      .groupBy("pk")
      .count()
      .withColumnRenamed("count", "num_entries")
  )
```

```sql
CREATE OR REFRESH MATERIALIZED VIEW report_pk_tests(
  CONSTRAINT unique_pk EXPECT (num_entries = 1)
)
AS SELECT pk, count(*) as num_entries
  FROM report
  GROUP BY pk
```

### 8.7 Schema-Evolution-Pattern

Zusätzliche Spalten bei Migration/mehreren Upstream-Versionen — Rückwärtskompatibilität + Datenqualität:

```python
@dp.table
@dp.expect_all_or_fail({
  "required_columns": "col1 IS NOT NULL AND col2 IS NOT NULL",
  "valid_col3": "CASE WHEN col3 IS NOT NULL THEN col3 > 0 ELSE TRUE END"
})
def evolving_table():
  legacy_data = spark.read.table("legacy_source")  # V1 Schema
  new_data = spark.read.table("new_source")        # V2 Schema
  return legacy_data.unionByName(new_data, allowMissingColumns=True)
```

```sql
CREATE OR REFRESH MATERIALIZED VIEW evolving_table(
  -- Mehrere Regeln zu einem Constraint zusammengeführt, da expect_all Python-spezifisch ist
  CONSTRAINT valid_migrated_data EXPECT (
    (col1 IS NOT NULL AND col2 IS NOT NULL) AND (CASE WHEN col3 IS NOT NULL THEN col3 > 0 ELSE TRUE END)
  ) ON VIOLATION FAIL UPDATE
) AS
  SELECT * FROM new_source
  UNION
  SELECT *, NULL as col3 FROM legacy_source;
```

- **Gotcha:** in SQL müssen mehrere Regeln zu einem einzigen Constraint zusammengeführt werden, da `expect_all` Python-exklusiv ist.

### 8.8 Resilientes Pipeline-Design: STRING-Ingestion

- Robustestes Bronze-Design lehnt nie einen Datensatz wegen Typkonflikt ab: alle Felder als `STRING`, Typdurchsetzung verschiebt sich auf Silver, wo `TRY_CAST` Fehler zu `NULL` auflöst statt Pipeline-Abbruch.

```sql
CREATE OR REFRESH STREAMING TABLE bronze_events
COMMENT "Bronze: alle Felder als STRING, Schema Rescue aktiviert"
AS SELECT *
FROM STREAM read_files(
  '/path/to/source',
  format => 'json',
  schemaEvolutionMode => 'rescue'
)
```

```sql
CREATE OR REFRESH STREAMING TABLE silver_events (
  CONSTRAINT valid_amount EXPECT (
    CASE WHEN amount IS NOT NULL
    THEN amount >= 0 ELSE TRUE END
  ) ON VIOLATION DROP ROW
)
AS SELECT *,
  TRY_CAST(amount_str AS DOUBLE) AS amount
FROM STREAM bronze_events
```

- **Gotcha (Zusammenspiel mit Schema-Evolution):** neue Spalte per Schema-Evolution → alle davor eingelesenen Datensätze tragen `NULL`. Constraint dafür **muss** das NULL-tolerante `CASE WHEN`-Pattern (Abschnitt 8.11) nutzen — sonst scheitern alle historischen Datensätze und fluten die UI mit falschen Meldungen.

### 8.9 Range-Based-Validation

Neue Datenpunkte gegen historische statistische Bandbreiten (Ausreißer-Erkennung):

```python
@dp.view
def stats_validation_view():
  bounds = spark.sql("""
    SELECT
      avg(amount) - 3 * stddev(amount) as lower_bound,
      avg(amount) + 3 * stddev(amount) as upper_bound
    FROM historical_stats
    WHERE date >= CURRENT_DATE() - INTERVAL 30 DAYS
  """)
  return spark.read.table("new_data").crossJoin(bounds)

@dp.table
@dp.expect_or_drop(
  "within_statistical_range",
  "amount BETWEEN lower_bound AND upper_bound"
)
def validated_amounts():
  return spark.read.table("stats_validation_view")
```

```sql
CREATE OR REFRESH MATERIALIZED VIEW stats_validation_view AS
  WITH bounds AS (
    SELECT
    avg(amount) - 3 * stddev(amount) as lower_bound,
    avg(amount) + 3 * stddev(amount) as upper_bound
    FROM historical_stats
    WHERE date >= CURRENT_DATE() - INTERVAL 30 DAYS
  )
  SELECT new_data.*, bounds.*
  FROM new_data
  CROSS JOIN bounds;

CREATE OR REFRESH MATERIALIZED VIEW validated_amounts (
  CONSTRAINT within_statistical_range EXPECT (amount BETWEEN lower_bound AND upper_bound)
)
AS SELECT * FROM stats_validation_view;
```

### 8.10 Quarantäne-Pattern

- Kombiniert Expectations + temporäre Tabellen/Views: getrennte Pfade für gültige/ungültige Datensätze, kein Datenverlust. Merksatz: **eingehende Datensätze = saubere + Quarantäne-Datensätze**.
- **Gotcha:** Quality-Tracking-Tabelle muss durchgängig `warn` verwenden — mit `drop`/`fail` wären ungültige Datensätze schon entfernt, bevor `is_quarantined` berechnet wird (bricht Zero-Data-Loss-Garantie). `warn` macht nur Metriken sichtbar; Routing übernimmt `is_quarantined`.
- **Partitionierung nach `is_quarantined`:** trennt gültig/ungültig physisch — beide nachgelagerten Views profitieren von Partition Pruning.

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import expr

rules = {
  "valid_pickup_zip": "(pickup_zip IS NOT NULL)",
  "valid_dropoff_zip": "(dropoff_zip IS NOT NULL)",
}
quarantine_rules = "NOT({0})".format(" AND ".join(rules.values()))

@dp.view
def raw_trips_data():
  return spark.readStream.table("samples.nyctaxi.trips")

@dp.table(
  temporary=True,
  partition_cols=["is_quarantined"],
)
@dp.expect_all(rules)
def trips_data_quarantine():
  return (
    spark.readStream.table("raw_trips_data").withColumn("is_quarantined", expr(quarantine_rules))
  )

@dp.view
def valid_trips_data():
  return spark.read.table("trips_data_quarantine").filter("is_quarantined=false")

@dp.view
def invalid_trips_data():
  return spark.read.table("trips_data_quarantine").filter("is_quarantined=true")
```

```sql
CREATE TEMPORARY STREAMING LIVE VIEW raw_trips_data AS
  SELECT * FROM STREAM(samples.nyctaxi.trips);

CREATE OR REFRESH TEMPORARY STREAMING TABLE trips_data_quarantine(
  -- Option 1: alle Regeln zu einem Namen im Event-Log zusammenfassen
  CONSTRAINT quarantined_row EXPECT (pickup_zip IS NOT NULL OR dropoff_zip IS NOT NULL),
  -- Option 2: Regeln separat halten -> mehrere Einträge unter verschiedenen Namen
  CONSTRAINT invalid_pickup_zip EXPECT (pickup_zip IS NOT NULL),
  CONSTRAINT invalid_dropoff_zip EXPECT (dropoff_zip IS NOT NULL)
)
PARTITIONED BY (is_quarantined)
AS
  SELECT
    *,
    NOT ((pickup_zip IS NOT NULL) and (dropoff_zip IS NOT NULL)) as is_quarantined
  FROM STREAM(raw_trips_data);

CREATE TEMPORARY LIVE VIEW valid_trips_data AS
SELECT * FROM trips_data_quarantine WHERE is_quarantined=FALSE;

CREATE TEMPORARY LIVE VIEW invalid_trips_data AS
SELECT * FROM trips_data_quarantine WHERE is_quarantined=TRUE;
```

(SQL-Variante nutzt bewusst Legacy-Bezeichner `CREATE TEMPORARY STREAMING LIVE VIEW`/`CREATE TEMPORARY LIVE VIEW` für temporäre Views.)

**`drop` vs. Quarantäne-Pattern:**

| | `drop` | Quarantäne-Pattern |
|---|---|---|
| Ungültige Datensätze | dauerhaft gelöscht | in Quarantäne-Tabelle erhalten |
| Audit-Trail | keiner | vollständig, abfragbar |
| Wiederherstellung | nicht möglich | Regel korrigieren → aus Quarantäne neu einspeisen |
| Lesbarkeit-Performance | vollständiger Table-Scan | Partition Pruning auf `is_quarantined` |
| Pipeline-Komplexität | gering (eine Tabelle) | moderat (temporäre Tabelle + zwei Views) |
| Geeignet für | unkritische Streams, stabile Regeln | produktive Pipelines mit Compliance-/Audit-Bedarf |

### 8.11 NULL-Toleranz

- **Gotcha:** NULL wertet in SQL zu `NOT TRUE` — ein einfacher Bereichs-Check macht jeden NULL-Wert fälschlich zur Verletzung.

**Naiv — NULLs werden als Verletzung behandelt:**

```sql
CONSTRAINT valid_discount
EXPECT (
  discount_rate >= 0
  AND discount_rate <= 100
)
-- Jeder NULL-Datensatz wird als Verletzung markiert
```

**NULL-tolerant — validiert nur, wenn Wert vorhanden:**

```sql
CONSTRAINT valid_discount EXPECT (
  CASE
    WHEN discount_rate IS NOT NULL
    THEN discount_rate >= 0 AND discount_rate <= 100
    ELSE TRUE
  END
)
```

- NULL-Datensätze bestehen anstandslos; nur vorhandener, außerhalb Bereich liegender Wert wird markiert. **Faustregel:** optionale/per Schema-Evolution hinzugekommene Spalte → immer `CASE WHEN ... IS NOT NULL THEN ... ELSE TRUE END`.
- **Ein Constraint, eine logische Regel** — nicht mehrere Bedingungen bündeln, damit UI präzise Metriken pro Constraint zeigt.

**Stand:** 2026-09-14.
