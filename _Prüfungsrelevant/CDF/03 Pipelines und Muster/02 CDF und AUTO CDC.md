[← Übersicht](../00%20Uebersicht.md)

# CDF und AUTO CDC

> Quellen: [Change data capture and snapshots](https://docs.databricks.com/aws/en/data-engineering/what-is-cdc) · [The AUTO CDC APIs](https://docs.databricks.com/aws/en/ldp/cdc) · [create_auto_cdc_flow](https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-apply-changes) · [ETL in Databricks SQL (Tutorial)](https://docs.databricks.com/aws/en/sql/get-started/sql-etl-tutorial) · [Tutorial: Build an ETL pipeline using CDC](https://docs.databricks.com/aws/en/ldp/tutorial-pipelines) · [Pipeline best practices](https://docs.databricks.com/aws/en/ldp/best-practices/) · [Replicate an external RDBMS table](https://docs.databricks.com/aws/en/ldp/database-replication) · [Backfill with flows](https://docs.databricks.com/aws/en/ldp/flows-backfill) · [REPLACE USING flows](https://docs.databricks.com/aws/en/ldp/flows-replace-using) · [Error classes](https://docs.databricks.com/aws/en/error-messages/error-classes) · [Release Notes Juni 2025](https://docs.databricks.com/aws/en/release-notes/product/2025/june)

## Zusammenhang

- `AUTO CDC` ist für Änderungen aus einem **CDC-Feed** gedacht, laut Doku ausdrücklich auch aus **Delta-Tabellen mit aktiviertem CDF**.
- `create_auto_cdc_flow()` „creates a flow that uses Lakeflow pipelines change data capture (CDC) functionality to process source data from a **change data feed (CDF)**“.
- Die `AUTO CDC`-APIs ersetzen seit Juni 2025 die `APPLY CHANGES`-APIs (gleiche Syntax); `apply_changes()` heißt jetzt `create_auto_cdc_flow()`.
- AUTO CDC wird **nicht** von Apache Spark Declarative Pipelines (Open Source) unterstützt.

**Laut Doku `AUTO CDC` verwenden, wenn:**

- das Quellsystem einen Change Data Feed erzeugt,
- aus einer **Delta-Tabelle mit aktiviertem CDF** gelesen wird,
- ein CDC-Feed einer relationalen Datenbank vorliegt (z. B. über Debezium oder Oracle GoldenGate).

> **Rollen im Lakehouse:** CDF **liefert** die Änderungen einer Delta-Tabelle, AUTO CDC **wendet** Änderungen auf eine Zieltabelle an (SCD 1 oder 2). Kombiniert: Der CDF einer Tabelle wird zur Quelle eines AUTO-CDC-Flows.

Grundlagen zu AUTO CDC, SCD und Sequenzierung: [../../SCD/02 SCD Type 2 mit AUTO CDC](../../SCD/02%20SCD%20Type%202%20mit%20AUTO%20CDC.md) · [Vollständige AUTO-CDC-Referenz](../../Data%20Transformation%20and%20Modeling/Vertiefung%20%28ueber%20Pruefungsumfang%20hinaus%29/Lakeflow%20Declarative%20Pipelines%20-%20Transformation%20und%20CDC/03%20Change%20Data%20Capture%20%28CDC%29.md)

---

## Tutorial: ETL in Databricks SQL mit CDF → AUTO CDC → Materialized View

Das offizielle Tutorial baut eine dreistufige Pipeline **nur mit SQL**: Quelltabelle mit CDF → SCD-2-Dimension mit `AUTO CDC` → aggregierende Materialized View.

### Schritt 2: Quelltabelle mit CDF anlegen und befüllen

```sql
CREATE OR REPLACE TABLE products (
  product_id INT,
  product_name STRING,
  category STRING,
  warehouse STRING
)
TBLPROPERTIES (delta.enableChangeDataFeed = true);

INSERT INTO products VALUES
  (1, 'Spoon', 'Cutlery', 'Seattle'),
  (2, 'Fork', 'Cutlery', 'Portland'),
  (3, 'Knife', 'Cutlery', 'Denver'),
  (4, 'Chair', 'Furniture', 'Austin'),
  (5, 'Table', 'Furniture', 'Chicago'),
  (6, 'Lamp', 'Lighting', 'Boston'),
  (7, 'Mug', 'Kitchenware', 'Seattle'),
  (8, 'Plate', 'Kitchenware', 'Atlanta'),
  (9, 'Bowl', 'Kitchenware', 'Dallas'),
  (10, 'Glass', 'Kitchenware', 'Phoenix');
```

Änderungen simulieren (neue Produkte, Lagerwechsel, Kategoriewechsel):

```sql
INSERT INTO products VALUES
  (11, 'Napkin', 'Dining', 'San Francisco'),
  (12, 'Coaster', 'Dining', 'New York');

UPDATE products SET warehouse = 'Los Angeles' WHERE product_id = 1;
UPDATE products SET category = 'Dining' WHERE product_id = 2;
```

### Schritt 3: Den Change Data Feed ansehen

```sql
SELECT
  product_id, product_name, warehouse,
  _change_type, _commit_version
FROM table_changes('products', 1)
ORDER BY _commit_version, product_id;
```

Der Löffel (Spoon) hat drei Events: `insert` (Seattle), `update_preimage` (Seattle) und `update_postimage` (Los Angeles). Eine einzige fachliche Änderung erzeugt also mehrere Events. Genau diese Komplexität nimmt `AUTO CDC` ab.

### Schritt 4: SCD-2-Dimension mit `AUTO CDC`

> **Beta** in diesem Kontext; erfordert **Databricks Runtime 17.3** oder höher.

```sql
CREATE OR REFRESH STREAMING TABLE products_history
SCHEDULE REFRESH EVERY 1 DAY
FLOW AUTO CDC
FROM STREAM products WITH (readChangeFeed = true)
KEYS (product_id)
APPLY AS DELETE WHEN _change_type = 'delete'
SEQUENCE BY _commit_timestamp
COLUMNS * EXCEPT (_change_type, _commit_version, _commit_timestamp)
STORED AS SCD TYPE 2;
```

| Klausel | Bedeutung |
|---|---|
| `FROM STREAM products WITH (readChangeFeed = true)` | liest den **CDF** der Quelltabelle als Stream |
| `APPLY AS DELETE WHEN _change_type = 'delete'` | CDF-Deletes schließen die aktuelle Version |
| `SEQUENCE BY _commit_timestamp` | CDF-Metadatenspalte als Reihenfolge |
| `COLUMNS * EXCEPT (_change_type, _commit_version, _commit_timestamp)` | CDF-Metadatenspalten landen nicht im Ziel |
| `SCHEDULE REFRESH EVERY 1 DAY` | tägliche Aktualisierung |

```sql
SELECT product_id, product_name, warehouse, __START_AT, __END_AT
FROM products_history
ORDER BY product_id, __START_AT;
```

Ergebnis: Spoon und Fork haben je zwei Versionen, alle anderen eine; `__END_AT = NULL` markiert die aktuelle Version.

### Schritt 5: Deletes durch die Pipeline schicken

```sql
DELETE FROM products WHERE product_id = 9;
DELETE FROM products WHERE product_id = 10;
```

Die Deletes stehen jetzt im CDF, die Streaming Table hat sie aber noch nicht gesehen:

```sql
REFRESH STREAMING TABLE products_history;
```

```sql
SELECT product_id, product_name, warehouse, __START_AT, __END_AT
FROM products_history
ORDER BY product_id, __START_AT;
```

Bowl und Glass sind jetzt mit `__END_AT` geschlossen. Die Streaming Table hat **nur die neuen Delete-Events** verarbeitet, nicht noch einmal die alten Inserts und Updates.

### Schritt 6: Aggregierende Materialized View

```sql
CREATE OR REPLACE MATERIALIZED VIEW products_by_category
SCHEDULE REFRESH EVERY 1 DAY
AS
SELECT
  category,
  COUNT(*) AS active_products
FROM products_history
WHERE __END_AT IS NULL
GROUP BY category;
```

```sql
SELECT * FROM products_by_category ORDER BY active_products DESC;
```

### Schritt 7: Die Kaskade prüfen

```sql
UPDATE products SET warehouse = 'Seattle' WHERE product_id = 3;
```

1. `products` zeichnet die Änderung im **CDF** auf.
2. `products_history` verarbeitet das Event und legt eine neue Version für das Messer (Knife) an.
3. `products_by_category` berechnet nur die betroffene Zeile (Cutlery) neu.

```sql
SELECT product_id, product_name, warehouse, __START_AT, __END_AT
FROM products_history
WHERE product_id = 3
ORDER BY __START_AT;

SELECT * FROM products_by_category ORDER BY active_products DESC;
```

> **Beobachtung:** Das Tutorial filtert `update_preimage` nicht ausdrücklich heraus. Die Doku sagt nicht explizit, wie AUTO CDC Preimages behandelt. Ein vorgeschalteter Filter `_change_type != 'update_preimage'` (wie in Python-Varianten üblich) entfernt nur die alten Werte und ändert das Ergebnis des Postimages nicht.

---

## Workaround aus der Fehlerreferenz: Expectations bei `AUTO CDC FROM SNAPSHOT`

`AUTO CDC FROM SNAPSHOT` unterstützt **keine Expectations** (Fehler `APPLY_CHANGES_FROM_SNAPSHOT_EXPECTATIONS_NOT_SUPPORTED`). Die Fehlerreferenz empfiehlt eine Zwei-Stufen-Lösung **über CDF**:

1. Snapshot mit **SCD Typ 1** in eine **Zwischentabelle ohne Expectations** laden.
2. Änderungen der Zwischentabelle lesen mit `spark.readStream.option("readChangeFeed", "true").table`.
3. Mit `apply_changes` (heute `create_auto_cdc_flow`) ins Endziel schreiben, zusätzlich mit:
   - `apply_as_deletes = "_change_type == 'delete'"`
   - `except_column_list = ["_change_type", "_commit_version", "_commit_timestamp"]`
   - den Expectations auf der finalen Zieltabelle.

Hintergrund: Laut Doku kann das Ziel von `AUTO CDC FROM SNAPSHOT` selbst einen CDF (SCD 1 oder 2) für nachgelagerte Abfragen liefern → [03 CDF von AUTO-CDC-Zielen](03%20CDF%20von%20AUTO-CDC-Zielen%20und%20Materialized%20Views.md).

---

## Tutorial „ETL pipeline using CDC“: SCD2 statt eigener CDF-Historie

Das Pipeline-Tutorial ordnet ein: Delta unterstützt CDF, und `table_changes` kann Änderungen abfragen. **Der Hauptzweck von CDF ist aber, Änderungen in einer Pipeline zu erfassen, nicht, eine vollständige Sicht aller Änderungen seit Beginn aufzubauen.** Besonders bei Events außerhalb der Reihenfolge wird das komplex. Dafür gibt es SCD 2:

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import *

# create the table
dp.create_streaming_table(
    name="customers_history", comment="Slowly Changing Dimension Type 2 for customers"
)

# store all changes as SCD2
dp.create_auto_cdc_flow(
    target="customers_history",
    source="customers_cdc_clean",
    keys=["id"],
    sequence_by=col("operation_date"),
    ignore_null_updates=False,
    apply_as_deletes=expr("operation = 'DELETE'"),
    except_column_list=["operation", "operation_date", "_rescued_data"],
    stored_as_scd_type="2",
)  # Enable SCD2 and store individual updates
```

```sql
CREATE OR REFRESH STREAMING TABLE customers_history;

CREATE FLOW customers_history_cdc
AS AUTO CDC INTO
  customers_history
FROM stream(customers_cdc_clean)
KEYS (id)
APPLY AS DELETE WHEN
operation = "DELETE"
SEQUENCE BY operation_date
COLUMNS * EXCEPT (operation, operation_date, _rescued_data)
STORED AS SCD TYPE 2;
```

Optional lassen sich die verfolgten Spalten einschränken: `TRACK HISTORY ON {columnList | EXCEPT(exceptColumnList)}`.

---

## Best Practice: deklaratives CDC statt imperativem `MERGE`

Die Pipeline-Best-Practices empfehlen, CDC **nicht** mit eigenen `MERGE`-Anweisungen umzusetzen: Reihenfolge, Deduplizierung, partielle Updates und Schemaentwicklung müssten sonst einzeln gelöst werden. `AUTO CDC ... INTO` (SQL) bzw. `create_auto_cdc_flow()` (Python) erledigen das deklarativ.

Verwandte Muster aus den Quellen:

- **Initiale Befüllung + laufender Change Feed** (`once`-Flow, dann Change Flow): siehe [Vollständige AUTO-CDC-Referenz, Abschnitt 9](../../Data%20Transformation%20and%20Modeling/Vertiefung%20%28ueber%20Pruefungsumfang%20hinaus%29/Lakeflow%20Declarative%20Pipelines%20-%20Transformation%20und%20CDC/03%20Change%20Data%20Capture%20%28CDC%29.md).
- **Legacy-SCD-Tabelle migrieren**, deren ursprünglicher Change Feed nicht mehr existiert: Historie einmalig per `AUTO CDC ONCE` einspielen, danach den neuen Feed anhängen:

```sql
CREATE OR REFRESH STREAMING TABLE customers_history;

-- One-time seed: replay the legacy history as change events
CREATE FLOW customers_history_seed
AS AUTO CDC ONCE INTO customers_history
FROM stream(legacy.customers_scd2)
KEYS (customer_id)
SEQUENCE BY valid_from
STORED AS SCD TYPE 2;

-- Ongoing live CDC into the same target
CREATE FLOW customers_history_cdc
AS AUTO CDC INTO customers_history
FROM stream(customers_cdc_bronze)
KEYS (customer_id)
SEQUENCE BY change_timestamp
STORED AS SCD TYPE 2;
```

  Beide Flows müssen Keys, SCD-Typ und den Datentyp der Sequenzspalte teilen. Der Cutover muss **pro Key** gelten: Die erste Live-Änderung jedes Keys muss nach seiner letzten eingespielten Änderung sequenziert sein.

- **Kein echter Change Feed, nur „neuester Datensatz pro Key“:** `REPLACE USING`-Flow. Die Doku empfiehlt ausdrücklich, stattdessen AUTO CDC zu verwenden, wenn die Quelle ein Change Feed mit expliziten Insert/Update/Delete-Operationen ist.

```sql
CREATE OR REFRESH STREAMING TABLE bookings_current
FLOW REPLACE USING (booking_id) SEQUENCE BY booking_update_id BY NAME
SELECT booking_id, status, total_amount, booking_update_id
FROM STREAM(samples.wanderbricks.booking_updates);
```

---
[← Vorherige Datei](01%20Demo%20-%20Silver%20nach%20Gold%20propagieren.md) · [Übersicht](../00%20Uebersicht.md) · [Nächste Datei →](03%20CDF%20von%20AUTO-CDC-Zielen%20und%20Materialized%20Views.md)
