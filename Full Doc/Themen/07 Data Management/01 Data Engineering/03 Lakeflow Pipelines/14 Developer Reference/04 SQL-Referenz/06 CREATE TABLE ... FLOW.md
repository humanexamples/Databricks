# `CREATE TABLE ... FLOW` (Pipelines) — Referenz

## Abschnittsübersicht

1. [Grundzweck](#grundzweck)
2. [Formale Syntax](#syntax)
3. [Parameter](#parameter)
4. [Einschränkungen](#einschraenkungen)
5. [Doku-eigene Beispiele](#doku-beispiele)
6. [Quellen](#quellen)

---

## <a id="grundzweck">1. Grundzweck</a>

**Beta.** Das Statement `CREATE TABLE ... FLOW` erstellt eine Managed Table in einer Pipeline, die von einem oder mehreren Flows geschrieben wird.

---

## <a id="syntax">2. Formale Syntax</a>

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

Um mehrere Quellen in eine Managed Table zusammenzuführen (Fan-in), werden mehrere Flows deklariert, die per `CREATE FLOW` auf dieselbe Tabelle zeigen:

```
CREATE FLOW flow_name AS INSERT INTO table_name BY NAME query
```

### Reales Beispiel mit möglichst vielen Bausteinen der formalen Syntax

`PARTITIONED BY` und `CLUSTER BY` schließen sich gegenseitig aus. Das folgende, aus den einzeln verifizierten Bausteinen dieses Dokuments zusammengesetzte Beispiel (kein wörtliches Einzelzitat einer Doku-Seite) kombiniert die größtmögliche gemeinsam nutzbare Untermenge — vollständige `table_specification` mit `CONSTRAINT ... EXPECT ... ON VIOLATION`, die `table_clauses` `CLUSTER BY`, `LOCATION`, `COMMENT`, `TBLPROPERTIES`, `WITH ROW FILTER`, sowie eine `FLOW INSERT ONCE BY NAME`-Klausel:

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

Zwei Bausteine sind mit obigem Beispiel nicht kombinierbar bzw. gehören separat betrachtet:

- **`PARTITIONED BY`** als Alternative zu `CLUSTER BY`.
- **`FLOW INSERT BY NAME`** (ohne `ONCE`) für laufende Streaming-Befüllung statt einmaligem Backfill; mehrere solche Flows lassen sich per separatem `CREATE FLOW ... AS INSERT INTO table_name BY NAME query` auf dieselbe Tabelle richten (Fan-in), siehe Doku-Beispiele unten und `CREATE FLOW.md` in diesem Ordner.

---

## <a id="parameter">3. Parameter</a>

- **`table_name`** — der Name der zu erstellenden Managed Table. Ist der Name nicht qualifiziert, wird die Tabelle im Ziel-Schema der Pipeline erstellt. Der Name darf noch nicht zu einer Streaming Table gehören.
- **`table_specification`** — definiert optional die Spalten, ihre Typen, Eigenschaften und Beschreibungen. Fehlt sie, wird das Schema aus der Flow-Abfrage abgeleitet.
- **`CONSTRAINT expectation_name EXPECT (expectation_expr) [ ON VIOLATION { FAIL UPDATE | DROP ROW } ]`** — fügt der Managed Table Datenqualitäts-Expectations hinzu, die über die Zeit nachverfolgt und über das Event-Log der Pipeline eingesehen werden können. Eine `FAIL UPDATE`-Expectation lässt die Verarbeitung sowohl beim Erstellen als auch beim Aktualisieren der Tabelle fehlschlagen. Eine `DROP ROW`-Expectation verwirft die gesamte Zeile, wenn die Expectation nicht erfüllt ist. `expectation_expr` darf aus Literalen, Spaltenbezeichnern innerhalb der Tabelle sowie deterministischen, eingebauten SQL-Funktionen oder Operatoren bestehen — mit Ausnahme von Aggregatfunktionen (einschließlich analytischer Window-Funktionen und Ranking-Window-Funktionen) sowie tabellenwertigen Generatorfunktionen; außerdem darf `expectation_expr` keine Subquery enthalten.
- **`PARTITIONED BY (col [, ...])`** — partitioniert die Tabelle optional nach einer Teilmenge von Spalten.
- **`CLUSTER BY clause`** — aktiviert optional Liquid Clustering auf der Tabelle. `PARTITIONED BY` und `CLUSTER BY` lassen sich nicht kombinieren.
- **`LOCATION path`** — optionaler Speicherort für die Tabellendaten.
- **`COMMENT table_comment`** — ein `STRING`-Literal zur Beschreibung der Tabelle.
- **`TBLPROPERTIES clause`** — legt optional eine oder mehrere benutzerdefinierte Tabelleneigenschaften fest.
- **`WITH ROW FILTER clause`** — fügt der Tabelle eine Row-Filter-Funktion hinzu. Nachfolgende Abfragen für diese Tabelle erhalten nur die Teilmenge der Zeilen, für die die Funktion `TRUE` liefert.
- **`FLOW INSERT [ONCE] BY NAME query`** — definiert einen Append-Flow, der das Ergebnis von `query` per Namensabgleich (*by name*) in die Tabelle einfügt. `query` kann Batch- oder Streaming-Quellen referenzieren. `ONCE` führt den Flow einmalig aus (z. B. für einen Backfill) statt bei jedem Update. Jeder benannte Flow verarbeitet seine Eingabe genau einmal pro Pipeline-Update — identisch zu `FLOW INSERT BY NAME` auf einer Streaming Table.

---

## <a id="einschraenkungen">4. Einschränkungen</a>

- Managed Tables unterstützen keine CDC-Change-Flows. `AUTO CDC INTO` (SQL) bzw. `apply_changes`/`apply_changes_from_snapshot` (Python) gegen eine Managed Table schlägt mit `MANAGED_TABLE_DOES_NOT_SUPPORT_CDC` fehl. Für CDC-Ziele ist stattdessen `CREATE STREAMING TABLE` zu verwenden (siehe `CREATE STREAMING TABLE.md` in diesem Ordner).
- Managed Tables unterstützen kein `FLOW ... REPLACE WHERE`. Nur `FLOW INSERT BY NAME` wird unterstützt.
- Managed Tables werden nur in Pipelines mit Unity Catalog unterstützt. Der Hive Metastore wird nicht unterstützt.
- Der Name einer bestehenden Streaming Table lässt sich nicht für eine Managed Table wiederverwenden. Die Streaming Table muss zuerst gelöscht werden, sonst schlägt das Statement mit `CANNOT_SWITCH_STREAMING_TABLE_TO_MANAGED_TABLE` fehl.

---

## <a id="doku-beispiele">5. Doku-eigene Beispiele</a>

```sql
-- Create a managed table populated by an inline append flow from a streaming table
CREATE TABLE output
FLOW INSERT BY NAME SELECT * FROM STREAM(samples.tpch.orders);

-- Create a managed table that ingests files with schema inference and evolution
CREATE TABLE raw_data
FLOW INSERT BY NAME
  SELECT * FROM STREAM read_files('abfss://<container-name>@<storage-account-name>.dfs.core.windows.net/base/path');

-- Create a partitioned managed table from a streaming source
CREATE TABLE events
PARTITIONED BY (bucket)
FLOW INSERT BY NAME
  SELECT id, bucket FROM STREAM read_files('abfss://my_path', format => 'json');

-- Create a managed table with liquid clustering
CREATE TABLE orders_clustered
CLUSTER BY (order_date, customer_id)
FLOW INSERT BY NAME
  SELECT
    o_orderkey   AS order_id,
    o_custkey    AS customer_id,
    o_orderdate  AS order_date,
    o_totalprice AS total_price
  FROM STREAM(samples.tpch.orders);

-- Create a managed table with a data quality expectation that drops violating rows
CREATE TABLE valid_events
  (CONSTRAINT positive_id EXPECT (id > 0) ON VIOLATION DROP ROW)
FLOW INSERT BY NAME
  SELECT id FROM STREAM read_files('s3://bucket/path', format => 'json');
```

---

## <a id="quellen">6. Quellen</a>

- CREATE TABLE ... FLOW (pipelines) — SQL-Sprachreferenz (Beta-Status, formale Syntax, alle Parameter, Einschränkungen, fünf Doku-Beispiele, Fan-in-Muster über separates `CREATE FLOW`): https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-table-flow

**Stand:** 2026-08-19.
