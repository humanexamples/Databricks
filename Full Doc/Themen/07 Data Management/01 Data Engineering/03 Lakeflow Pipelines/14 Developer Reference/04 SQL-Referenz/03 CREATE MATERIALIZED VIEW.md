# `CREATE MATERIALIZED VIEW` (Pipelines) — Referenz

## Abschnittsübersicht

1. [Grundzweck](#grundzweck)
2. [Formale Syntax](#syntax)
3. [Parameter](#parameter)
4. [Notwendige Berechtigungen](#berechtigungen)
5. [Einschränkungen](#einschraenkungen)
6. [Doku-eigene Beispiele](#doku-beispiele)
7. [Quellen](#quellen)

---

## <a id="grundzweck">1. Grundzweck</a>

Eine Materialized View ist eine View, bei der vorberechnete Ergebnisse für Abfragen verfügbar sind und aktualisiert werden können, um Änderungen an den Eingabedaten widerzuspiegeln. Materialized Views werden von einer Pipeline unterstützt. Bei jeder Aktualisierung einer Materialized View werden die Abfrageergebnisse neu berechnet, um Änderungen in vorgelagerten Datasets widerzuspiegeln. Materialized Views lassen sich manuell oder nach Zeitplan aktualisieren.

---

## <a id="syntax">2. Formale Syntax</a>

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

### Reales Beispiel mit möglichst vielen Bausteinen der formalen Syntax

`PARTITIONED BY` und `CLUSTER BY` schließen sich gegenseitig aus, ebenso `USING DELTA` und `USING ICEBERG` (siehe unten für Letzteres als separate Variante). Das folgende, aus den einzeln verifizierten Bausteinen dieses Dokuments zusammengesetzte Beispiel (kein wörtliches Einzelzitat einer Doku-Seite) kombiniert die größtmögliche gemeinsam nutzbare Untermenge — vollständige `column_list` mit Typ, `NOT NULL`, `COMMENT`, informationellem Primary-Key-`column_constraint`, `MASK`-Klausel, `CONSTRAINT ... EXPECT ... ON VIOLATION`, `table_constraint` als Foreign Key sowie die `view_clauses` `USING DELTA`, `CLUSTER BY`, `COMMENT`, `TBLPROPERTIES`, `REFRESH POLICY` und `WITH ROW FILTER`:

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

Hinweis: `LOCATION` ist nur beim Publizieren in den Hive Metastore verfügbar — in Unity Catalog wird der Speicherort automatisch verwaltet und die Klausel damit dort wirkungslos; sie ist hier der Vollständigkeit halber mit aufgeführt.

Separat zu betrachten, da mit `USING DELTA` im obigen Beispiel nicht kombinierbar:

- **`USING ICEBERG`** (Public Preview) — erzeugt eine Materialized View, die mit externen Iceberg-Readern kompatibel ist. Nach dem Erstellen muss `REPAIR TABLE <mv_name> SYNC METADATA` ausgeführt werden; die Materialized View ist für externe Iceberg-Reader dann nur lesbar. Zur Aktivierung muss das Databricks-Account-Team kontaktiert werden.
- **`PRIVATE`** — erzeugt eine private Materialized View, die nicht im Katalog registriert und nur innerhalb der definierenden Pipeline zugänglich ist; sie kann denselben Namen wie ein bereits im Katalog veröffentlichtes Objekt tragen und bleibt über die gesamte Lebensdauer der Pipeline bestehen (nicht nur ein einzelnes Update). Private Materialized Views wurden früher mit dem Parameter `TEMPORARY` erstellt.
- **`PARTITIONED BY`** als Alternative zu `CLUSTER BY` — Databricks empfiehlt für Pipelines jedoch, `CLUSTER BY` (Liquid Clustering) statt `PARTITIONED BY` zu verwenden. Mit `CLUSTER BY AUTO` wählt Databricks die Clustering-Spalten automatisch:

  ```sql
  CREATE OR REFRESH MATERIALIZED VIEW sample_trips
  CLUSTER BY AUTO
  AS SELECT pickup_zip, fare_amount FROM samples.nyctaxi.trips
  ```

---

## <a id="parameter">3. Parameter</a>

- **`REFRESH`** — erstellt bei Angabe die View oder aktualisiert eine bestehende View samt Inhalt.
- **`PRIVATE`** — erstellt eine private Materialized View. Nützlich als Zwischentabelle innerhalb einer Pipeline, die nicht im Katalog veröffentlicht werden soll. Private Materialized Views werden nicht dem Katalog hinzugefügt und sind nur innerhalb der definierenden Pipeline zugänglich; sie können denselben Namen wie ein bestehendes Katalogobjekt tragen — innerhalb der Pipeline lösen Referenzen auf den Namen dann zur privaten Materialized View auf; sie bestehen nur über die Lebensdauer der Pipeline fort, nicht nur ein einzelnes Update. Private Materialized Views wurden zuvor mit dem Parameter `TEMPORARY` erstellt.
- **`view_name`** — der Name der neu erstellten View. Der vollqualifizierte View-Name muss eindeutig sein. Private Materialized Views können denselben Namen wie ein im Katalog veröffentlichtes Objekt tragen.
- **`column_list`** — beschriftet optional die Spalten im Abfrageergebnis der View. Bei Angabe einer Spaltenliste muss die Anzahl der Spaltenaliase der Anzahl der Ausdrücke in der Abfrage entsprechen. Ohne Spaltenliste werden die Aliase aus dem View-Rumpf abgeleitet.
  - **`column_name`** — die Spaltennamen müssen eindeutig sein und den Ausgabespalten der Abfrage entsprechen.
  - **`column_type`** — legt den Datentyp der Spalte fest. Nicht alle von Databricks unterstützten Datentypen werden von Materialized Views unterstützt.
  - **`column_comment`** — ein optionales `STRING`-Literal zur Beschreibung der Spalte. Muss zusammen mit `column_type` angegeben werden; ist der Spaltentyp nicht angegeben, wird der Spaltenkommentar übersprungen.
  - **`column_constraint`** — fügt einer Spalte in einer Materialized View einen informationellen Primary-Key- oder Foreign-Key-Constraint hinzu.
  - **`MASK`-Klausel** — fügt eine Column-Mask-Funktion zur Anonymisierung sensibler Daten hinzu.
  - **`CONSTRAINT expectation_name EXPECT (expectation_expr) [ ON VIOLATION { FAIL UPDATE | DROP ROW } ]`** — fügt der Materialized View Datenqualitäts-Expectations hinzu, die über die Zeit nachverfolgt und über das Event-Log der Materialized View eingesehen werden können. Eine `FAIL UPDATE`-Expectation lässt die Verarbeitung sowohl beim Erstellen als auch beim Aktualisieren der Materialized View fehlschlagen. Eine `DROP ROW`-Expectation verwirft die gesamte Zeile, wenn die Expectation nicht erfüllt ist. `expectation_expr` darf aus Literalen, Spaltenbezeichnern innerhalb der Materialized View sowie deterministischen, eingebauten SQL-Funktionen oder Operatoren bestehen — mit Ausnahme von Aggregatfunktionen (einschließlich analytischer Window-Funktionen und Ranking-Window-Funktionen) sowie tabellenwertigen Generatorfunktionen; außerdem darf `expr` keine Subquery enthalten. Eine Materialized View, deren Definition Expectations enthält, wird bei jedem Update vollständig aktualisiert und unterstützt kein inkrementelles Refresh — um inkrementelles Refresh zu nutzen, müssen die Expectations entfernt oder außerhalb der Materialized-View-Definition angewendet werden.
- **`table_constraint`** — bei Angabe eines Schemas lassen sich Primary und Foreign Keys definieren; die Constraints sind informationell und werden nicht erzwungen. Um Table Constraints zu definieren, muss die Pipeline eine Unity-Catalog-fähige Pipeline sein.
- **`view_clauses`** — legt optional Partitionierung, Kommentare und benutzerdefinierte Eigenschaften der Materialized View fest. Jede Unterklausel darf nur einmal angegeben werden.
  - **`USING DELTA`** — legt das Datenformat fest. Standard ist DELTA. Optional.
  - **`USING ICEBERG`** (Public Preview) — erzeugt eine mit externen Iceberg-Readern kompatible Materialized View. Nach dem Erstellen muss `REPAIR TABLE <mv_name> SYNC METADATA` ausgeführt werden. Die Materialized View ist für externe Iceberg-Reader nur lesbar. Zur Aktivierung muss das Databricks-Account-Team kontaktiert werden.
  - **`PARTITIONED BY`** — optionale Liste von einer oder mehreren Spalten zur Partitionierung der Tabelle. Schließt `CLUSTER BY` gegenseitig aus. Liquid Clustering bietet eine flexible, optimierte Lösung für Clustering — Databricks empfiehlt, für Pipelines `CLUSTER BY` statt `PARTITIONED BY` zu verwenden.
  - **`CLUSTER BY`** — aktiviert Liquid Clustering auf der Tabelle und legt die als Clustering-Keys zu verwendenden Spalten fest. Mit `CLUSTER BY AUTO` wählt Databricks die Clustering-Keys intelligent zur Optimierung der Abfrageperformance. Schließt `PARTITIONED BY` gegenseitig aus.
  - **`LOCATION`** — optionaler Speicherort für Tabellendaten. Ist keiner gesetzt, verwendet das System standardmäßig den Pipeline-Speicherort. Diese Option ist nur beim Publizieren in den Hive Metastore verfügbar — in Unity Catalog wird der Speicherort automatisch verwaltet.
  - **`COMMENT`** — optionale Beschreibung für die Tabelle.
  - **`TBLPROPERTIES`** — optionale Liste von Tabelleneigenschaften für die Tabelle.
  - **`REFRESH POLICY`** (Beta) — legt optional eine Refresh Policy für die Materialized View fest. Siehe `CREATE MATERIALIZED VIEW Refresh Policy.md` in diesem Ordner.
  - **`WITH ROW FILTER`** — fügt der Tabelle eine Row-Filter-Funktion hinzu. Nachfolgende Abfragen für diese Tabelle erhalten nur die Teilmenge der Zeilen, für die die Funktion `TRUE` liefert — nützlich für feingranulare Zugriffskontrolle, da die Funktion Identität und Gruppenmitgliedschaften des aufrufenden Nutzers prüfen kann, um über das Filtern bestimmter Zeilen zu entscheiden.
- **`query`** — eine Abfrage, die das Dataset für die Tabelle definiert.

---

## <a id="berechtigungen">4. Notwendige Berechtigungen</a>

Der Run-as-Nutzer einer Pipeline benötigt folgende Berechtigungen:

- `SELECT`-Privileg auf die von der Materialized View referenzierten Basistabellen.
- `USE CATALOG`-Privileg auf den übergeordneten Katalog und `USE SCHEMA`-Privileg auf das übergeordnete Schema.
- `CREATE TABLE`- und `CREATE MATERIALIZED VIEW`-Privilegien auf das Schema, das die Materialized View enthält.

Um die Pipeline, in der die Materialized View definiert ist, aktualisieren zu können, sind zusätzlich erforderlich:

- `USE CATALOG`-Privileg auf den übergeordneten Katalog und `USE SCHEMA`-Privileg auf das übergeordnete Schema.
- Eigentümerschaft an der Materialized View oder `REFRESH`-Privileg auf die Materialized View.
- Der Eigentümer der Materialized View muss `SELECT`-Privileg auf die referenzierten Basistabellen besitzen.

Um die resultierende Materialized View abfragen zu können, sind erforderlich:

- `USE CATALOG`-Privileg auf den übergeordneten Katalog und `USE SCHEMA`-Privileg auf das übergeordnete Schema.
- `SELECT`-Privileg auf die Materialized View.

---

## <a id="einschraenkungen">5. Einschränkungen</a>

- Hat eine Materialized View mit einem `sum`-Aggregat über eine NULL-fähige Spalte den letzten Nicht-NULL-Wert dieser Spalte verloren — sodass nur noch `NULL`-Werte verbleiben —, liefert der resultierende Aggregatwert der Materialized View null statt `NULL`.
- Spaltenreferenzen benötigen keinen Alias. Ausdrücke, die keine reinen Spaltenreferenzen sind, benötigen einen Alias: erlaubt ist `SELECT col1, SUM(col2) AS sum_col2 FROM t GROUP BY col1`, nicht erlaubt ist `SELECT col1, SUM(col2) FROM t GROUP BY col1`.
- `NOT NULL` muss zusammen mit `PRIMARY KEY` manuell angegeben werden, damit es ein gültiges Statement ist.
- Materialized Views unterstützen keine Identity-Spalten oder Surrogatschlüssel.
- Materialized Views unterstützen die Befehle `OPTIMIZE` und `VACUUM` nicht — die Wartung erfolgt automatisch.
- Das Umbenennen der Tabelle oder das Ändern des Eigentümers wird nicht unterstützt.
- Generierte Spalten, Identity-Spalten und Default-Spalten werden nicht unterstützt.

---

## <a id="doku-beispiele">6. Doku-eigene Beispiele</a>

```sql
-- Create a materialized view by reading from an external data source, using the default schema:
CREATE OR REFRESH MATERIALIZED VIEW taxi_raw
AS SELECT * FROM read_files("/databricks-datasets/nyctaxi/sample/json/")

-- Create a materialized view by reading from a dataset defined in a pipeline:
CREATE OR REFRESH MATERIALIZED VIEW filtered_data
AS SELECT
  ...
FROM taxi_raw

-- Specify a schema and clustering columns for a table:
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

-- Use automatic liquid clustering to let Databricks choose the clustering columns:
CREATE OR REFRESH MATERIALIZED VIEW sample_trips
CLUSTER BY AUTO
AS SELECT pickup_zip, fare_amount FROM samples.nyctaxi.trips

-- Specify partition columns for a table:
CREATE OR REFRESH MATERIALIZED VIEW sales
(customer_id STRING,
  customer_name STRING,
  number_of_line_items STRING,
  order_datetime STRING,
  order_number LONG,
  order_day_of_week STRING GENERATED ALWAYS AS (dayofweek(order_datetime))
) PARTITIONED BY (order_day_of_week)
COMMENT "Raw data on sales"
AS SELECT * FROM ...

-- Specify a primary and foreign key constraint for a table:
CREATE OR REFRESH MATERIALIZED VIEW sales
(customer_id STRING NOT NULL PRIMARY KEY,
  customer_name STRING,
  number_of_line_items STRING,
  order_datetime STRING,
  order_number LONG,
  order_day_of_week STRING GENERATED ALWAYS AS (dayofweek(order_datetime)),
  CONSTRAINT fk_customer_id FOREIGN KEY (customer_id) REFERENCES main.default.customers(customer_id)
)
COMMENT "Raw data on sales"
AS SELECT * FROM ...

-- Specify a row filter and mask clause for a table:
CREATE OR REFRESH MATERIALIZED VIEW sales (
  customer_id STRING MASK catalog.schema.customer_id_mask_fn,
  customer_name STRING,
  number_of_line_items STRING COMMENT 'Number of items in the order',
  order_datetime STRING,
  order_number LONG,
  order_day_of_week STRING GENERATED ALWAYS AS (dayofweek(order_datetime))
)
COMMENT "Raw data on sales"
WITH ROW FILTER catalog.schema.order_number_filter_fn ON (order_number)
AS SELECT * FROM sales_bronze
```

---

## <a id="quellen">7. Quellen</a>

- CREATE MATERIALIZED VIEW (pipelines) — SQL-Sprachreferenz (formale Syntax, alle Parameter, notwendige Berechtigungen, Einschränkungen, sechs Doku-Beispiele): https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-materialized-view

**Stand:** 2026-08-19.
