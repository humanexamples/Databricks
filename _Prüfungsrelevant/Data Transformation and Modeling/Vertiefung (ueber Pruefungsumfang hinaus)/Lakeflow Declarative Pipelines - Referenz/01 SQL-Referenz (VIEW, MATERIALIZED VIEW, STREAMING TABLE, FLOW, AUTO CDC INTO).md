# SQL-Referenz für Lakeflow Declarative Pipelines

## 1. `CREATE VIEW`

Konstruiert in einer Pipeline eine virtuelle Tabelle ohne physische Daten, basierend auf dem Ergebnis einer SQL-Abfrage.

```sql
CREATE VIEW main.sales.taxi_silver
COMMENT 'Gefilterte Taxifahrten mit positiver Distanz'
-- TBLProperties: benutzerdefinierte Metadaten der Tabelle
TBLPROPERTIES ('quality' = 'silver')
AS SELECT * FROM main.sales.taxi_raw
WHERE distance > 0.0;

-- Create a view from an external data source
CREATE VIEW taxi_raw AS SELECT *
  FROM read_files("/databricks-datasets/nyctaxi/sample/json/");

-- Use a view to create a filtered view:
CREATE VIEW taxi_silver AS SELECT *
  FROM taxi_raw
  WHERE distance > 0.0;
```

**Einschränkungen:**
- Nur Standard-Publishing-Modus (kein Legacy-`LIVE`-Schema), nur Unity-Catalog-Pipeline.
- Kein `CONSTRAINT`/Expectations.
- Keine Streaming-Abfragen, keine Streaming-Quelle.
- Keine Kommentare für pipeline-erstellte Views.

## 2. `CREATE TEMPORARY VIEW`

Erstellt temporäre Views, die nur innerhalb einer Pipeline und über deren Lebensdauer bestehen.

```sql
CREATE TEMPORARY VIEW valid_sales_by_rep (
  sale_day COMMENT 'Verkaufsdatum',
  total_sales COMMENT 'Tagesumsatz',
  sales_rep COMMENT 'Erster Vertriebsmitarbeiter des Tages',
  CONSTRAINT valid_total_sales EXPECT (total_sales > 0) ON VIOLATION DROP ROW
)
COMMENT 'Bereinigte, nach Verkaufstag aggregierte Umsätze'
TBLPROPERTIES ('quality' = 'silver')
AS SELECT date(sales_date) AS sale_day, SUM(sales) AS total_sales, FIRST(sales_rep)
FROM sales GROUP BY date(sales_date), sales_rep;
```

**Einschränkungen:** Lebensdauer = Pipeline-Lebensdauer, privat für die Pipeline, nicht im Katalog registriert (gleicher Name wie Katalogobjekt möglich — View gewinnt intern).

```sql
-- Create a temporary view, and use it
CREATE TEMPORARY VIEW my_view (sales_day, total_sales, sales_rep)
  AS SELECT date(sales_date) AS sale_day, SUM(sales) AS total_sales, FIRST(sales_rep) FROM sales GROUP BY date(sales_date), sales_rep;

CREATE OR REFRESH MATERIALIZED VIEW sales_by_date
  AS SELECT * FROM my_view;

-- Create a temporary view with a data quality expectation
CREATE TEMPORARY VIEW valid_sales (
  CONSTRAINT valid_total_sales EXPECT (total_sales > 0) ON VIOLATION DROP ROW
)
  AS SELECT date(sales_date) AS sales_day, SUM(sales) AS total_sales FROM sales GROUP BY date(sales_date);
```

## 3. `CREATE MATERIALIZED VIEW`

Eine Materialized View hält vorberechnete Ergebnisse verfügbar, die aktualisiert werden können, um Änderungen an den Eingabedaten widerzuspiegeln. Bei jeder Aktualisierung werden die Abfrageergebnisse neu berechnet, um Änderungen in vorgelagerten Datasets widerzuspiegeln — manuell oder nach Zeitplan.

**Formale Syntax:**

```
CREATE [OR REFRESH] [PRIVATE] MATERIALIZED VIEW
  view_name
  [ column_list ]
  [ view_clauses ]
  AS query

column_list
   ( { column_name column_type column_properties } [, ...]
    [ CONSTRAINT expectation_name EXPECT (expectation_expr)
      [ ON VIOLATION { FAIL UPDATE | DROP ROW } ] ] [, ...]
    [ , table_constraint ] [...] )

   column_properties
      { NOT NULL | COMMENT column_comment | column_constraint | MASK clause } [ ... ]

view_clauses
  { USING { DELTA | ICEBERG } |
    PARTITIONED BY (col [, ...]) |
    CLUSTER BY clause |
    LOCATION path |
    COMMENT view_comment |
    TBLPROPERTIES clause |
    REFRESH POLICY refresh_clause |
    WITH { ROW FILTER clause } } [...]
```

Beispiel mit vielen kombinierbaren Bausteinen (`PARTITIONED BY`/`CLUSTER BY` und `USING DELTA`/`USING ICEBERG` schließen sich jeweils gegenseitig aus):

```sql
CREATE OR REFRESH MATERIALIZED VIEW main.sales.customer_orders_summary (
  customer_id STRING NOT NULL PRIMARY KEY COMMENT 'Eindeutige Kunden-ID',
  customer_name STRING MASK main.sales.customer_name_mask_fn,
  order_count LONG,
  total_amount DOUBLE COMMENT 'Summe aller Bestellbeträge',
  CONSTRAINT valid_order_count EXPECT (order_count >= 0) ON VIOLATION DROP ROW,
  CONSTRAINT fk_customer_id FOREIGN KEY (customer_id) REFERENCES main.sales.customers(customer_id)
)
USING DELTA
CLUSTER BY (customer_id)
LOCATION '/mnt/gold/customer_orders_summary'
COMMENT 'Aggregierte Kundenbestellungen'
TBLPROPERTIES ('quality' = 'gold')
REFRESH POLICY INCREMENTAL
WITH ROW FILTER main.sales.region_filter_fn ON (customer_id)
AS SELECT
  customer_id,
  customer_name,
  COUNT(*) AS order_count,
  SUM(amount) AS total_amount
FROM main.sales.orders
GROUP BY customer_id, customer_name;
```

`LOCATION` ist nur beim Publizieren in den Hive Metastore relevant — in Unity Catalog wird der Speicherort automatisch verwaltet.

**Weitere Varianten:**
- **`USING ICEBERG`** (Public Preview) — erzeugt eine mit externen Iceberg-Readern kompatible Materialized View; nach dem Erstellen `REPAIR TABLE <mv_name> SYNC METADATA` ausführen; für externe Reader nur lesbar; Aktivierung erfordert Kontakt zum Databricks-Account-Team.
- **`PRIVATE`** — private Materialized View, nicht im Katalog registriert, nur innerhalb der definierenden Pipeline zugänglich, kann Namen eines Katalogobjekts tragen, besteht über die gesamte Pipeline-Lebensdauer (früher: `TEMPORARY`).
- **`PARTITIONED BY`** als Alternative zu `CLUSTER BY` — Databricks empfiehlt jedoch `CLUSTER BY` (Liquid Clustering); mit `CLUSTER BY AUTO` wählt Databricks die Spalten automatisch.

**Parameter (Auswahl):**
- `REFRESH` — erstellt oder aktualisiert. `PRIVATE` — s. u.
- `column_list` — `column_name`/`column_type`/`column_comment`/`column_constraint` (informationeller PK/FK)/`MASK`/`CONSTRAINT ... EXPECT`. **Wichtig:** Expectations erzwingen bei jedem Update ein **vollständiges** Refresh (kein inkrementelles) — für inkrementelles Refresh Expectations entfernen oder außerhalb der Definition anwenden.
- `table_constraint` — informationeller PK/FK, erfordert Unity-Catalog-Pipeline.
- `view_clauses` — `USING DELTA` (Standard) / `USING ICEBERG`, `PARTITIONED BY`, `CLUSTER BY`, `LOCATION`, `COMMENT`, `TBLPROPERTIES`, `REFRESH POLICY` (Beta, Abschnitt 4), `WITH ROW FILTER` (Zugriffskontroll-Funktion).

**Einschränkungen:**
- Ein `sum`-Aggregat über eine NULL-fähige Spalte, deren letzter Nicht-NULL-Wert verloren ging (nur noch `NULL`-Werte), liefert `null` statt `NULL`.
- Reine Spaltenreferenzen benötigen keinen Alias; andere Ausdrücke schon: `SELECT col1, SUM(col2) AS sum_col2 FROM t GROUP BY col1` erlaubt, `SELECT col1, SUM(col2) FROM t GROUP BY col1` nicht.
- `NOT NULL` muss zusammen mit `PRIMARY KEY` manuell angegeben werden.
- Keine Identity-Spalten oder Surrogatschlüssel.
- `OPTIMIZE`/`VACUUM` nicht unterstützt (Wartung automatisch).
- Umbenennen der Tabelle oder Ändern des Eigentümers nicht unterstützt.
- Generierte Spalten, Identity-Spalten, Default-Spalten nicht unterstützt.

```sql
-- Aus externer Quelle lesen
CREATE OR REFRESH MATERIALIZED VIEW taxi_raw
AS SELECT * FROM read_files("/databricks-datasets/nyctaxi/sample/json/")

-- Aus einem Pipeline-Dataset lesen
CREATE OR REFRESH MATERIALIZED VIEW filtered_data
AS SELECT ... FROM taxi_raw

-- Schema und Clustering-Spalten angeben
CREATE OR REFRESH MATERIALIZED VIEW sales
(customer_id STRING,
  customer_name STRING,
  number_of_line_items STRING,
  order_datetime STRING,
  order_number LONG,
  order_day_of_week STRING GENERATED ALWAYS AS (dayofweek(order_datetime))
) CLUSTER BY (order_day_of_week, customer_id)
COMMENT "Raw data on sales"
AS SELECT * FROM ...

-- Automatisches Liquid Clustering
CREATE OR REFRESH MATERIALIZED VIEW sample_trips
CLUSTER BY AUTO
AS SELECT pickup_zip, fare_amount FROM samples.nyctaxi.trips

-- Primary- und Foreign-Key-Constraint
CREATE OR REFRESH MATERIALIZED VIEW sales
(customer_id STRING NOT NULL PRIMARY KEY,
  customer_name STRING,
  order_number LONG,
  CONSTRAINT fk_customer_id FOREIGN KEY (customer_id) REFERENCES main.default.customers(customer_id)
)
AS SELECT * FROM ...

-- Row Filter und Mask
CREATE OR REFRESH MATERIALIZED VIEW sales (
  customer_id STRING MASK catalog.schema.customer_id_mask_fn,
  order_number LONG
)
WITH ROW FILTER catalog.schema.order_number_filter_fn ON (order_number)
AS SELECT * FROM sales_bronze
```

## 4. `REFRESH POLICY`-Klausel (Materialized View)

**Die Grundfrage, um die es hier geht:** Wenn sich Quelldaten ändern, muss eine Materialized View aktualisiert werden. Dafür gibt es zwei Wege — **Full Refresh** (alles neu berechnen, funktioniert immer, aber teuer) und **inkrementelles Refresh** (nur die neuen/geänderten Zeilen verarbeiten, viel billiger, aber nicht bei jeder Abfrage möglich — z. B. nicht bei `RAND()` oder bestimmten Joins). `REFRESH POLICY` legt fest, welchen der beiden Wege Databricks nehmen soll bzw. wie streng es dabei sein darf.

**Syntax:**

```sql
CREATE OR REFRESH MATERIALIZED VIEW <name>
REFRESH POLICY { AUTO | INCREMENTAL | INCREMENTAL STRICT | FULL }
AS SELECT ...
```

Ob eine Abfrage überhaupt inkrementalisierbar ist, lässt sich vorab prüfen: `EXPLAIN CREATE MATERIALIZED VIEW ...`.

### Die vier Werte, je mit Beispiel

**`AUTO` (Standard) — Databricks entscheidet selbst, nie ein Fehlschlag.**

```sql
CREATE OR REFRESH MATERIALIZED VIEW main.sales.daily_revenue
REFRESH POLICY AUTO
AS SELECT order_date, SUM(amount) AS revenue
FROM main.sales.orders
GROUP BY order_date;
-- Ist die Abfrage inkrementalisierbar UND laut Kostenmodell günstiger inkrementell → inkrementelles Refresh.
-- Sonst → Full Refresh. Schlägt nie fehl, man hat aber keine Garantie, welcher Weg gewählt wird.
```

**`INCREMENTAL` — bevorzugt inkrementell, fällt bei Bedarf still auf Full zurück.**

```sql
CREATE OR REFRESH MATERIALIZED VIEW main.sales.daily_revenue
REFRESH POLICY INCREMENTAL
AS SELECT order_date, SUM(amount) AS revenue
FROM main.sales.orders
GROUP BY order_date;
-- Normalerweise: inkrementelles Refresh.
-- Kann die Abfrage in einem einzelnen Lauf mal nicht inkrementell verarbeitet werden
-- (z. B. weil Quelldaten sich strukturell verändert haben) -> stiller Fallback auf Full Refresh.
-- ABER: Wäre diese Abfrage GRUNDSÄTZLICH nie inkrementalisierbar (siehe RAND()-Beispiel unten),
-- schlägt schon das CREATE selbst fehl.
```

**`INCREMENTAL STRICT` — wie `INCREMENTAL`, aber ohne stillen Fallback.**

```sql
CREATE OR REFRESH MATERIALIZED VIEW main.sales.daily_revenue
REFRESH POLICY INCREMENTAL STRICT
AS SELECT order_date, SUM(amount) AS revenue
FROM main.sales.orders
GROUP BY order_date;
-- Kann ein einzelner Refresh nicht inkrementell laufen, schlägt DIESER Refresh fehl,
-- statt (wie bei INCREMENTAL) unbemerkt auf Full Refresh umzuschalten.
-- Sinnvoll, wenn man sich bewusst auf günstige inkrementelle Refreshes verlässt und
-- lieber einen sichtbaren Fehler sehen will, als überraschend hohe Full-Refresh-Kosten zu zahlen.
```

**`FULL` — immer alles neu berechnen, nie inkrementell.**

```sql
CREATE OR REFRESH MATERIALIZED VIEW main.sales.daily_revenue
REFRESH POLICY FULL
AS SELECT order_date, SUM(amount) AS revenue
FROM main.sales.orders
GROUP BY order_date;
-- Jeder Refresh liest alle Quelldaten neu und schreibt das komplette Ergebnis neu —
-- selbst obwohl diese GROUP-BY-Abfrage eigentlich inkrementalisierbar wäre.
```

### Konkretes Beispiel: dieselbe Abfrage nicht-inkrementalisierbar machen

`RAND()` ist nicht deterministisch — das macht die Abfrage grundsätzlich nicht inkrementalisierbar:

```sql
CREATE OR REFRESH MATERIALIZED VIEW main.sales.sampled_orders
REFRESH POLICY INCREMENTAL
AS SELECT * FROM main.sales.orders WHERE RAND() < 0.1;
-- Schlägt schon beim CREATE fehl: MATERIALIZED_VIEW_NOT_INCREMENTALIZABLE,
-- Detail-Code EXPRESSION_NOT_DETERMINISTIC.
-- Mit REFRESH POLICY AUTO oder FULL wäre dieselbe Abfrage dagegen völlig unproblematisch
-- (sie würde einfach immer per Full Refresh laufen).
```

Weitere Gründe, warum eine Abfrage nicht inkrementalisierbar sein kann (jeweils eigener Detail-Code derselben Fehlerklasse `MATERIALIZED_VIEW_NOT_INCREMENTALIZABLE`): `GROUP BY` mit komplexen Ausdrücken darüber (`AGGREGATE_NOT_TOP_NODE`), die Quelle ist keine Delta-Tabelle (`INPUT_NOT_IN_DELTA`), ein komplexer Join oder anderer Operator (`OPERATOR_NOT_INCREMENTALIZABLE`), Row Tracking fehlt auf der Quelltabelle (`ROW_TRACKING_NOT_ENABLED`), eine nicht inkrementalisierbare Subquery (`SUBQUERY_EXPRESSION_NOT_INCREMENTALIZABLE`), eine UDF ohne Determinismus-Markierung (`UDF_NOT_DETERMINISTIC`), oder ein Window ohne `PARTITION BY` (`WINDOW_WITHOUT_PARTITION_BY`).

## 5. `CREATE STREAMING TABLE`

Eine Streaming Table unterstützt Streaming- bzw. inkrementelle Datenverarbeitung. Bei jeder Aktualisierung werden der Quelltabelle hinzugefügte Daten angefügt — manuell oder nach Zeitplan.

**Formale Syntax:**

```
CREATE [OR REFRESH] [PRIVATE] STREAMING TABLE
  table_name
  [ table_specification ]
  [ table_clauses ]
  [ {flow_clause | AS query} ]

table_specification
  ( { column_identifier column_type [column_properties] } [, ...]
    [ column_constraint ] [, ...]
    [ , table_constraint ] [...] )

   column_properties
      { NOT NULL | GENERATED ALWAYS AS ( expr ) | GENERATED { ALWAYS | BY DEFAULT } AS IDENTITY [ ( [ START WITH start | INCREMENT BY step ] [ ...] ) ] | DEFAULT default_expression | COMMENT column_comment | column_constraint | MASK clause } [ ... ]

table_clauses
  { USING DELTA
    PARTITIONED BY (col [, ...]) |
    CLUSTER BY clause |
    LOCATION path |
    COMMENT view_comment |
    TBLPROPERTIES clause |
    WITH { ROW FILTER clause } } [ ... ]
   } [ ... ]

flow_clause
  FLOW { { INSERT [ONCE] BY NAME query } |
  { AUTO CDC auto_cdc_flow_spec } |
  { REPLACE WHERE predicate BY NAME query } |
  { REPLACE USING ( column_name [, ...] ) SEQUENCE BY sequence_column BY NAME query } }
```

Alternativ lässt sich eine Streaming Table ohne inline-Flow anlegen (`CREATE OR REFRESH STREAMING TABLE table_name;`) und anschließend über separate `CREATE FLOW`-Statements befüllen (Abschnitt 8).

Beispiel mit vielen kombinierbaren Bausteinen (die vier `flow_clause`-Varianten schließen sich gegenseitig aus, ebenso `PARTITIONED BY`/`CLUSTER BY` und `flow_clause`/`AS query`):

```sql
CREATE OR REFRESH PRIVATE STREAMING TABLE main.sales.customers_bronze (
  customer_id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1000 INCREMENT BY 1),
  ssn STRING NOT NULL PRIMARY KEY MASK main.sales.ssn_mask_fn COMMENT 'Sozialversicherungsnummer, maskiert',
  region STRING DEFAULT 'UNKNOWN' COMMENT 'Herkunftsregion',
  status STRING GENERATED ALWAYS AS (upper(region)),
  CONSTRAINT fk_region FOREIGN KEY (region) REFERENCES main.sales.regions(region)
)
CLUSTER BY (region)
LOCATION '/mnt/bronze/customers'
COMMENT 'Rohdaten zu Kunden, einmaliger Backfill'
TBLPROPERTIES ('quality' = 'bronze')
WITH ROW FILTER main.sales.region_filter_fn ON (region)
FLOW INSERT ONCE BY NAME
  SELECT * FROM STREAM read_files('/databricks-datasets/retail-org/customers/*', format => 'csv')
  WITH (SKIPCHANGECOMMITS);
```

**Alternative Kurzform** — `AS query` ist äquivalent zu `FLOW INSERT BY NAME query` (ohne `ONCE`, laufende Streaming-Befüllung):

```sql
CREATE OR REFRESH STREAMING TABLE raw_data
AS SELECT * FROM STREAM read_files('abfss://my_path');
```

**Weitere `flow_clause`-Varianten:**

`FLOW AUTO CDC` (Beta, Databricks Runtime 17.3+, `PREVIEW`-Channel) — CDC-Datensätze inline verarbeiten (vollständige Spezifikation siehe Abschnitt 7):

```sql
CREATE OR REFRESH STREAMING TABLE target
FLOW AUTO CDC
FROM stream(cdc_data.users)
KEYS (userId)
SEQUENCE BY sequenceNum
STORED AS SCD TYPE 1;
```

`FLOW REPLACE WHERE predicate BY NAME query` — berechnet/überschreibt nur `predicate`-entsprechende Zeilen, alle übrigen bleiben unverändert; für inkrementelle Batch-Verarbeitung von Joins/Aggregationen, spät eintreffende Daten, Schema Evolution, Backfills:

```sql
FLOW REPLACE WHERE region = 'EU' BY NAME
SELECT * FROM eu_customers_batch;
```

`FLOW REPLACE USING (column_name [, ...]) SEQUENCE BY sequence_column BY NAME query` (Beta, Databricks Runtime 18.2+) — ersetzt Zeilen anhand Schlüsselspalten, Quelle muss Streaming-Quelle sein:

```sql
FLOW REPLACE USING (payment_id) SEQUENCE BY payment_date BY NAME
SELECT payment_id, booking_id, status, payment_date
FROM STREAM(samples.wanderbricks.payments);
```

**Wichtige Parameter:**

- **`PRIVATE`** — nicht im Katalog registriert, nur innerhalb der Pipeline zugänglich, kann Namen eines Katalogobjekts tragen, besteht über die Pipeline-Lebensdauer (früher `TEMPORARY`).
- **`GENERATED ALWAYS AS (expr)`** — Spaltenwert wird berechnet; `DEFAULT COLLATION` der Tabelle muss `UTF8_BINARY` sein; keine Aggregat-/Window-/Ranking-/Generatorfunktionen, keine Subquery.
- **`GENERATED {ALWAYS|BY DEFAULT} AS IDENTITY [(START WITH start INCREMENT BY step)]`** — ab Databricks SQL/Runtime 10.4 LTS+; nur für Delta-Tabellen, nur `BIGINT`-Spalten; Werte eindeutig, aber nicht garantiert lückenlos; `step` darf nicht 0 sein; `PARTITIONED BY`/`UPDATE` einer Identity-Spalte nicht unterstützt. **Wichtig:** Eine Identity-Spalte deaktiviert nebenläufige Transaktionen auf der Tabelle — nur nutzen, wenn keine nebenläufigen Schreibvorgänge nötig sind.
- **`DEFAULT default_expression`** — ab Databricks SQL/Runtime 11.3 LTS+; Default bei `INSERT`/`UPDATE`/`MERGE ... INSERT`, wenn Spalte nicht angegeben; unterstützt für `CSV`/`JSON`/`PARQUET`/`ORC`-Quellen.
- **`CONSTRAINT ... EXPECT ... ON VIOLATION`** — wie bei anderen Objekten (siehe Kapitel zu Expectations).
- **`CLUSTER BY`** vs. **`PARTITIONED BY`** — exklusiv; `CLUSTER BY AUTO` = automatische Spaltenwahl; ohne Angabe bleibt Tabelle ungeclustert.
  - Ändern: kein `ALTER TABLE`/`ALTER STREAMING TABLE` (deckt nur Schedule/`ALTER COLUMN`/Row-Filter/Tags/Owner ab) — nur per erneutem `CREATE OR REFRESH STREAMING TABLE table_name CLUSTER BY (...)` mit sonst gleicher Definition.
  - Wirkt zunächst nur auf neue Daten; `OPTIMIZE table_name FULL;` reorganisiert Bestandsdateien ohne Neuverarbeitung — schonender als `REFRESH ... FULL` (Truncate + Checkpoint-Löschung + komplette Neuverarbeitung).
- **`FLOW`** — `INSERT BY NAME` (Standard-Append, `STREAM`-Keyword, Fehler bei Update/Delete der Quelle), `ONCE` (Backfill, läuft bei Full Refresh erneut), `AUTO CDC` (Beta), `REPLACE WHERE`, `REPLACE USING`.
- **`AS query`** — Kurzform für `FLOW INSERT BY NAME`; Read-Options als `WITH`-Map: `SELECT * FROM STREAM t WITH (SKIPCHANGECOMMITS=TRUE, STARTINGVERSION=X)` (Runtime 17.3+; für Delta: `maxFilesPerTrigger`, `maxBytesPerTrigger`, `startingVersion`, `startingTimestamp`, `readChangeFeed`, `withEventTimeOrder`, `skipChangeCommits`).

**Berechtigungen:** Erstellen → `SELECT` auf Basistabellen, `USE CATALOG`/`USE SCHEMA`, `CREATE MATERIALIZED VIEW`. Update → `USE CATALOG`/`USE SCHEMA`, Eigentümerschaft oder `REFRESH`-Privileg (+ `SELECT` auf Basistabellen für Eigentümer). Abfragen → `USE CATALOG`/`USE SCHEMA`, `SELECT`.

**Einschränkungen:**
- Nur Tabelleneigentümer aktualisiert. Kein `ALTER TABLE` (nutze `CREATE OR REFRESH`/`ALTER STREAMING TABLE`).
- Keine Schema-Evolution über DML (`INSERT INTO`/`MERGE`).
- Nicht unterstützt: `CLONE`, `COPY INTO`, `ANALYZE TABLE`, `RESTORE`, `TRUNCATE`, `GENERATE MANIFEST`, `[CREATE OR] REPLACE TABLE`, Umbenennen, Eigentümerwechsel.

```sql
-- Aus einem Datei-Volume
CREATE OR REFRESH STREAMING TABLE customers_bronze
AS SELECT * FROM STREAM read_files("/databricks-datasets/retail-org/customers/*", format => "csv")

-- Aus einer streamenden Quelltabelle
CREATE OR REFRESH STREAMING TABLE customers_silver
AS SELECT * FROM STREAM(customers_bronze)

-- Automatisches Liquid Clustering
CREATE OR REFRESH STREAMING TABLE customers_bronze_auto
CLUSTER BY AUTO
AS SELECT * FROM STREAM read_files("/databricks-datasets/retail-org/customers/*", format => "csv")

-- Row Filter und Column Mask
CREATE OR REFRESH STREAMING TABLE customers_silver (
  id int COMMENT 'This is the customer ID',
  name string,
  region string,
  ssn string MASK catalog.schema.ssn_mask_fn COMMENT 'SSN masked for privacy'
)
WITH ROW FILTER catalog.schema.us_filter_fn ON (region)
AS SELECT * FROM STREAM(customers_bronze)

-- Identity-Spalte
CREATE OR REFRESH STREAMING TABLE customers_with_id (
  customer_id BIGINT GENERATED ALWAYS AS IDENTITY,
  name string,
  region string
)
AS SELECT name, region FROM STREAM(customers_bronze)

-- Ohne inline-Flow, zum späteren Befüllen per CREATE FLOW
CREATE OR REFRESH STREAMING TABLE orders;

-- Mit inline Append-Flow
CREATE OR REFRESH STREAMING TABLE raw_data
FLOW INSERT BY NAME SELECT * FROM STREAM read_files('abfss://my_path');

-- Mit inline AUTO CDC Flow
CREATE OR REFRESH STREAMING TABLE target
FLOW AUTO CDC
FROM stream(cdc_data.users)
KEYS (userId)
SEQUENCE BY sequenceNum
STORED AS SCD TYPE 1;

-- Mit inline REPLACE USING Flow
CREATE OR REFRESH STREAMING TABLE payments_current
FLOW REPLACE USING (payment_id) SEQUENCE BY payment_date BY NAME
SELECT payment_id, booking_id, status, payment_date
FROM STREAM(samples.wanderbricks.payments);
```

### 5.1 Databricks-SQL-Variante (`sql-ref-syntax-ddl-create-streaming-table`)

Neben der Pipelines-Entwicklerreferenz existiert eine klassische SQL-Sprachreferenz aus Sicht von Databricks SQL, die in einigen Punkten abweicht: *"Streaming tables are only supported in Lakeflow pipelines and on Databricks SQL with Unity Catalog."*

**Abweichende Syntax:**

```
{ CREATE OR REFRESH STREAMING TABLE | CREATE STREAMING TABLE [ IF NOT EXISTS ] }
  table_name
  [ table_specification ]
  [ table_clauses ]
  [ {flow_clause | AS query} ]

table_clauses
  { PARTITIONED BY (col [, ...]) |
    CLUSTER BY clause |
    COMMENT table_comment |
    DEFAULT COLLATION UTF8_BINARY |
    TBLPROPERTIES clause |
    schedule |
    WITH { ROW FILTER clause } } [...]

schedule
  { SCHEDULE [ REFRESH ] schedule_clause |
    TRIGGER ON UPDATE [ AT MOST EVERY trigger_interval ] }

schedule_clause
  { EVERY number { HOUR | HOURS | DAY | DAYS | WEEK | WEEKS } |
    CRON cron_string [ AT TIME ZONE timezone_id ] }
```

**Unterschiede:** zusätzlich `CREATE STREAMING TABLE [IF NOT EXISTS]`; **kein** `PRIVATE`, **kein** `USING DELTA`, **kein** `LOCATION`; zusätzliche `DEFAULT COLLATION UTF8_BINARY` und `schedule`-Klausel inline. Die `schedule`-Klausel: zeitgesteuert (`SCHEDULE [REFRESH] EVERY n HOURS|DAYS|WEEKS` bzw. `CRON '<cron>' [AT TIME ZONE '<tz>']`) oder ereignisgesteuert (`TRIGGER ON UPDATE [AT MOST EVERY <interval>]`, Refresh bei Upstream-Änderungen, höchstens einmal je Intervall). `AT TIME ZONE LOCAL` wird nicht unterstützt.

```sql
-- Liquid Clustering
CREATE OR REFRESH STREAMING TABLE orders_with_cluster_by
  CLUSTER BY (order_date, customer_id)
  AS SELECT
    o_orderkey   AS order_id,
    o_custkey    AS customer_id,
    o_orderdate  AS order_date,
    o_totalprice AS total_price
  FROM STREAM(samples.tpch.orders);

-- Append-only aus Kafka
CREATE OR REFRESH STREAMING TABLE firehose_raw
  COMMENT 'Stores the raw data from Kafka'
  TBLPROPERTIES ('delta.appendOnly' = 'true')
  AS SELECT
    value raw_data, offset, timestamp, timestampType
  FROM STREAM read_kafka(bootstrapServers => 'ips', subscribe => 'topic_name');

-- Ereignisgesteuerter Refresh, höchstens 1x pro Stunde
CREATE STREAMING TABLE triggered_data
  TRIGGER ON UPDATE AT MOST EVERY INTERVAL 1 hour
  AS SELECT * FROM STREAM source_stream_data;

-- Zeitgesteuerter Refresh
CREATE STREAMING TABLE firehose_bronze
  SCHEDULE EVERY 1 HOUR
  AS SELECT from_json(raw_data, 'schema_string') data, * EXCEPT (raw_data)
  FROM STREAM firehose_raw;

-- Schema-Evolution mit Expectation, die bei Verletzung fehlschlägt
CREATE OR REFRESH STREAMING TABLE avro_data (
    CONSTRAINT date_parsing EXPECT (to_date(dt) >= '2000-01-01') ON VIOLATION FAIL UPDATE
  )
  AS SELECT * FROM STREAM read_files('gs://my-bucket/avroData');

-- Column- und Table-Constraint
CREATE OR REFRESH STREAMING TABLE csv_data (
    id int PRIMARY KEY, ts timestamp, event string
  )
  AS SELECT * FROM STREAM read_files('s3://bucket/path', format => 'csv', schema => 'id int, ts timestamp, event string');
```

## 6. `CREATE TABLE ... FLOW` (Managed Table, Beta)

Erstellt eine Managed Table in einer Pipeline, die von einem oder mehreren Flows geschrieben wird.

**Formale Syntax:**

```
CREATE TABLE
  table_name
  [ table_specification ]
  [ table_clauses ]
  [ flow_clause ]

table_specification
  ( { column_identifier column_type [column_properties] } [, ...]
    [ CONSTRAINT expectation_name EXPECT (expectation_expr)
        [ ON VIOLATION { FAIL UPDATE | DROP ROW } ] ] [, ...] )

table_clauses
  { PARTITIONED BY (col [, ...]) |
    CLUSTER BY clause |
    LOCATION path |
    COMMENT table_comment |
    TBLPROPERTIES clause |
    WITH { ROW FILTER clause } } [ ... ]

flow_clause
  FLOW INSERT [ONCE] BY NAME query
```

Für Fan-in (mehrere Quellen → dieselbe Managed Table) werden zusätzliche Flows per `CREATE FLOW` deklariert: `CREATE FLOW flow_name AS INSERT INTO table_name BY NAME query`.

```sql
CREATE TABLE main.sales.orders_managed (
  order_id BIGINT,
  customer_id BIGINT,
  order_date DATE,
  amount DOUBLE,
  CONSTRAINT positive_amount EXPECT (amount > 0) ON VIOLATION DROP ROW
)
CLUSTER BY (order_date, customer_id)
LOCATION '/mnt/managed/orders'
COMMENT 'Managed Table für Bestellungen, per Backfill befüllt'
TBLPROPERTIES ('quality' = 'silver')
WITH ROW FILTER main.sales.region_filter_fn ON (customer_id)
FLOW INSERT ONCE BY NAME
  SELECT order_id, customer_id, order_date, amount
  FROM main.sales.orders_backfill;
```

**Parameter:**
- `table_name` — darf nicht bereits einer Streaming Table gehören.
- `table_specification` — sonst aus Flow-Abfrage abgeleitet.
- `CONSTRAINT ... EXPECT`, `PARTITIONED BY`/`CLUSTER BY` (exklusiv), `LOCATION`, `COMMENT`, `TBLPROPERTIES`, `WITH ROW FILTER`.
- `FLOW INSERT [ONCE] BY NAME query` — Append-Flow, `ONCE` = einmalig/Backfill.

**Einschränkungen:**
- Kein CDC: `AUTO CDC INTO`/`apply_changes`/`apply_changes_from_snapshot` → Fehler `MANAGED_TABLE_DOES_NOT_SUPPORT_CDC` (für CDC: `CREATE STREAMING TABLE`).
- Nur `FLOW INSERT BY NAME`, kein `REPLACE WHERE`.
- Nur Unity-Catalog-Pipelines.
- Name einer bestehenden Streaming Table nicht wiederverwendbar → `CANNOT_SWITCH_STREAMING_TABLE_TO_MANAGED_TABLE`.

```sql
-- Managed Table aus einem inline Append-Flow einer Streaming Table
CREATE TABLE output
FLOW INSERT BY NAME SELECT * FROM STREAM(samples.tpch.orders);

-- Mit Liquid Clustering
CREATE TABLE orders_clustered
CLUSTER BY (order_date, customer_id)
FLOW INSERT BY NAME
  SELECT
    o_orderkey   AS order_id,
    o_custkey    AS customer_id,
    o_orderdate  AS order_date,
    o_totalprice AS total_price
  FROM STREAM(samples.tpch.orders);

-- Mit Expectation, die verletzende Zeilen verwirft
CREATE TABLE valid_events
  (CONSTRAINT positive_id EXPECT (id > 0) ON VIOLATION DROP ROW)
FLOW INSERT BY NAME
  SELECT id FROM STREAM read_files('s3://bucket/path', format => 'json');
```

## 7. `CREATE FLOW`

Erstellt Flows oder Backfills für Tabellen in einer Pipeline — getrennt vom Ziel definiert.

**Formale Syntax:**

```
CREATE FLOW flow_name [COMMENT comment] AS
{
  AUTO CDC [ONCE] INTO target_table create_auto_cdc_flow_spec |
  INSERT [ONCE] INTO target_table BY NAME [ replace_using_spec ] query
}

replace_using_spec
  REPLACE USING ( column_name [, ...] ) SEQUENCE BY sequence_column
```

`AUTO CDC ... INTO` und `INSERT ... INTO` schließen sich gegenseitig aus, ebenso `ONCE` und `REPLACE USING` (Letzteres erfordert eine Streaming-Quelle, `ONCE` schließt das aus):

```sql
CREATE FLOW payments_replace_flow COMMENT "Hält je payment_id nur die aktuellste Snapshot-Zeile" AS
INSERT INTO main.sales.payments_latest BY NAME
REPLACE USING (payment_id) SEQUENCE BY payment_date
SELECT payment_id, booking_id, status, payment_date
FROM STREAM(samples.wanderbricks.payments);
```

`ONCE` als Alternative zu `REPLACE USING` (einmaliger Backfill):

```sql
CREATE FLOW backfill_users AS
INSERT ONCE INTO users BY NAME
SELECT * FROM user_backfill_table;
```

**Parameter:**
- `flow_name`, `COMMENT`.
- `AUTO CDC ... INTO` — Change-Data-Semantik (volle Spezifikation: Abschnitt 8). `target_table` muss Streaming Table sein.
- `INSERT INTO` — ohne `ONCE` muss die Abfrage streamend sein (`STREAM`, Fehler bei Update/Delete der Quelle).
- `REPLACE USING (cols) SEQUENCE BY seq_col` (Beta, Runtime 18.2+) — ersetzt Zeilen je Schlüssel, höchster Sequenzwert gewinnt, Quelle muss Streaming sein, `BY NAME` Pflicht, nicht mit `ONCE`/`AUTO CDC` kombinierbar.
- `ONCE` — einmaliger Flow/Backfill, läuft bei Full Refresh erneut, nicht mit `REPLACE USING` kombinierbar.

```sql
-- Zwei Append-Flows in dieselbe Streaming Table
CREATE OR REFRESH STREAMING TABLE users;

CREATE FLOW users_flow AS
INSERT INTO users BY NAME
SELECT * FROM stream(raw_data.users);

CREATE FLOW backfill_users AS
INSERT ONCE INTO users BY NAME
SELECT * FROM user_backfill_table;

-- CDC-Flow
CREATE OR REFRESH STREAMING TABLE admins_cdc_target_table;

CREATE FLOW admin_cdc_flow AS
AUTO CDC INTO admins_cdc_target_table
FROM stream(cdc_data.admins)
KEYS (userId)
APPLY AS DELETE WHEN
  operation = "DELETE"
SEQUENCE BY sequenceNum
COLUMNS * EXCEPT (operation, sequenceNum)
STORED AS SCD TYPE 2;

-- REPLACE USING Flow
CREATE OR REFRESH STREAMING TABLE payments_latest;

CREATE FLOW payments_replace_flow AS
INSERT INTO payments_latest BY NAME
REPLACE USING (payment_id) SEQUENCE BY payment_date
SELECT payment_id, booking_id, status, payment_date
FROM STREAM(samples.wanderbricks.payments);
```

## 8. `AUTO CDC ... INTO`

Erstellt einen Flow, der CDC-Änderungen aus einer Quelle liest und auf eine Streaming-Ziel-Tabelle anwendet. Es muss vorab eine Ziel-Streaming-Tabelle deklariert werden. Für SCD-Typ-2-Tabellen müssen bei explizitem Zielschema zusätzlich die Spalten `__START_AT`/`__END_AT` mit demselben Datentyp wie das `SEQUENCE BY`-Feld enthalten sein.

**Formale Syntax:**

```
CREATE OR REFRESH STREAMING TABLE table_name;

CREATE FLOW flow_name AS AUTO CDC [ONCE] INTO table_name
FROM source
KEYS (keys)
[IGNORE NULL UPDATES [ON {columnList | * EXCEPT (exceptColumnList)}]]
[APPLY AS DELETE WHEN condition]
[APPLY AS TRUNCATE WHEN condition]
SEQUENCE BY orderByColumn
[SYSTEM SEQUENCE BY systemOrderByColumn]
[COLUMNS {columnList | * EXCEPT (exceptColumnList)}]
[STORED AS {SCD TYPE 1 | SCD TYPE 2 | BITEMPORAL}]
[TRACK HISTORY ON {columnList | * EXCEPT (exceptColumnList)}]
[COLUMNS TO UPDATE columnName]
```

Standardverhalten für `INSERT`/`UPDATE`: Upsert (aktualisieren bei Match, sonst Insert). `DELETE`-Verhalten über `APPLY AS DELETE WHEN`.

Beispiel mit vielen kombinierbaren Bausteinen (`COLUMNS TO UPDATE` schließt `IGNORE NULL UPDATES` aus; `APPLY AS TRUNCATE WHEN` nur für SCD Typ 1; `SYSTEM SEQUENCE BY`/`STORED AS BITEMPORAL` schließen SCD Typ 2 aus):

```sql
CREATE OR REFRESH STREAMING TABLE main.sales.users_cdc_target;

CREATE FLOW users_cdc_flow AS AUTO CDC INTO main.sales.users_cdc_target
FROM stream(cdc_data.users)
KEYS (userId)
IGNORE NULL UPDATES ON (email, phone)
APPLY AS DELETE WHEN operation = "DELETE"
SEQUENCE BY sequenceNum
COLUMNS * EXCEPT (operation, sequenceNum)
STORED AS SCD TYPE 2
TRACK HISTORY ON * EXCEPT (city);
```

**Weitere Varianten:**

```sql
-- ONCE für einmaligen Backfill (läuft bei Full Refresh erneut)
AUTO CDC ONCE INTO table_name ...

-- TRUNCATE nur für SCD Typ 1
APPLY AS TRUNCATE WHEN operation = "TRUNCATE"
STORED AS SCD TYPE 1

-- Bitemporal (Beta)
SEQUENCE BY sequenceNum
SYSTEM SEQUENCE BY _commit_timestamp
STORED AS BITEMPORAL

-- COLUMNS TO UPDATE für partielle Updates
COLUMNS TO UPDATE changedColumnsArray
```

**Parameter:**

- **`ONCE`** — einmaliger Insert/Backfill, läuft bei nicht-vollständigem Refresh nicht erneut.
- **`source`** — muss Streaming-Quelle sein; `STREAM`-Schlüsselwort für Streaming-Semantik.
- **`KEYS`** (erforderlich) — Spalte(n), die eine Zeile eindeutig identifiziert/identifizieren; kommagetrennt bei mehreren Spalten.
- **`IGNORE NULL UPDATES`** — erlaubt partielle Updates: `null`-Werte behalten den bestehenden Zielwert (auch bei geschachtelten Spalten). Mit `ON columnList` nur gelistete Spalten betroffen; mit `ON * EXCEPT (...)` alle außer den gelisteten. Standard: `null` überschreibt bestehenden Wert.
- **`APPLY AS DELETE WHEN`** — CDC-Ereignis als `DELETE` behandeln. Bei SCD Typ 2 wird die gelöschte Zeile zunächst als Tombstone in der Delta-Tabelle beibehalten (View im Metastore filtert sie heraus); Aufbewahrung konfigurierbar über `pipelines.cdc.tombstoneGCThresholdInSeconds`.
- **`APPLY AS TRUNCATE WHEN`** — CDC-Ereignis als vollständiges `TRUNCATE` behandeln; nur für SCD Typ 1 (SCD Typ 2 unterstützt Truncate nicht) — vorsichtig einsetzen, da vollständiges Truncate der Zieltabelle.
- **`SEQUENCE BY`** (erforderlich) — logische Reihenfolge der CDC-Ereignisse; bei mehreren Spalten `STRUCT`-Ausdruck (erstes Feld zuerst, bei Gleichstand nächstes Feld); Spalten müssen sortierbar sein.
- **`SYSTEM SEQUENCE BY`** (Beta, nur bitemporal) — Systemzeit, zu der ein CDC-Ereignis dem System bekannt wurde; zusammen mit `STORED AS BITEMPORAL`.
- **`COLUMNS`** — Teilmenge der Zielspalten, als Liste oder `* EXCEPT (...)`; Standard: alle Spalten.
- **`STORED AS`** — `SCD TYPE 1` (Standard), `SCD TYPE 2` oder `BITEMPORAL` (erfordert `SYSTEM SEQUENCE BY`, Beta).
- **`TRACK HISTORY ON`** — Teilmenge der Ausgabespalten, für die History-Einträge erzeugt werden; Standard: alle Spalten (`TRACK HISTORY ON *`).
- **`COLUMNS TO UPDATE`** — Quellspalte mit `array<string>` der je Change Record zu aktualisierenden Spalten (inkl. explizitem `null`); nicht gelistete Spalten bleiben unverändert; nicht kombinierbar mit `IGNORE NULL UPDATES`, nicht für bitemporale Tabellen.

```sql
CREATE OR REFRESH STREAMING TABLE target;

CREATE FLOW flow
AS AUTO CDC INTO
  target
FROM stream(cdc_data.users)
  KEYS (userId)
  APPLY AS DELETE WHEN operation = "DELETE"
  SEQUENCE BY sequenceNum
  COLUMNS * EXCEPT (operation, sequenceNum)
  STORED AS SCD TYPE 2
  TRACK HISTORY ON * EXCEPT (city);
```

## 9. `REFRESH` (MATERIALIZED VIEW oder STREAMING TABLE)

Aktualisiert die Daten einer Streaming Table oder Materialized View (Databricks SQL). Standardmäßig **synchron**; Status per `DESCRIBE EXTENDED` verfolgbar. Create-/Refresh-Operationen laufen auf **serverlosen Lakeflow-Pipelines** (Details im Catalog Explorer einsehbar). `REFRESH MATERIALIZED VIEW` gilt auch für materialisierte **Metric Views**.

**Syntax:**

```
REFRESH { MATERIALIZED VIEW | [ STREAMING ] TABLE } table_name
  [ FULL ] [ WHERE predicate ] [ SYNC | ASYNC ]
```

`FULL`, `WHERE` und `SYNC`/`ASYNC` lassen sich in beliebiger Teilmenge kombinieren.

**Parameter:**

- **`table_name`** — darf keine temporale Angabe/Options-Spezifikation enthalten; sonst `TABLE_OR_VIEW_NOT_FOUND`.
- **`FULL`** — bei Materialized Views: verarbeitet alle verfügbaren Quelldaten. Bei Streaming Tables: leert die Tabelle (Truncate) und verarbeitet alle Quelldaten mit der aktuellsten Tabellendefinition neu. Für Quellen ohne vollständige Historie/kurzer Retention (z. B. Kafka) nicht empfohlen — abgeschnittene Daten sind ggf. nicht wiederherstellbar.
- **`WHERE predicate`** — nur für Streaming Tables mit `FLOW REPLACE WHERE`-Klausel. Überschreibt das Prädikat für **diesen einen** Refresh (löscht nur passende Zeilen, berechnet sie aus der Quelle neu); die Flow-Definition bleibt unverändert — einmalige Operation für Backfills/Korrekturen. Auf anderen Objekten liefert `WHERE` einen Fehler.
- **`SYNC`** (Standard) — blockiert, bis Erstellung/initiale Ladung abgeschlossen ist.
- **`ASYNC`** — startet Hintergrund-Job, kehrt sofort zurück, liefert einen Link zur Pipeline zur Statusverfolgung.

```sql
-- Materialized View aktualisieren
REFRESH MATERIALIZED VIEW catalog.schema.view_name;

-- Streaming Table aktualisieren (aktueller Katalog/Schema qualifiziert)
REFRESH STREAMING TABLE st_name;

-- Vollständiger Refresh (Truncate + Neuverarbeitung)
REFRESH STREAMING TABLE cat.db.st_name FULL;

-- Einmaliger Predicate Override, asynchron
REFRESH STREAMING TABLE rep_st WHERE id = 3 ASYNC;
```

**Stand:** 2026-09-14.
