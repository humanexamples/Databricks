# Transactions

Multi-Statement-, Multi-Table-Transaktionen erlauben es, mehrere SQL-Statements über mehrere Tabellen hinweg als atomare Einheit auszuführen — alle Änderungen gelingen gemeinsam oder scheitern gemeinsam. Dieses Feature baut direkt auf Catalog Commits auf (siehe [Table Features/01 Catalog Commits.md](Table%20Features/01%20Catalog%20Commits.md)).

## Abschnittsübersicht

1. [Was sind Transaktionen?](#was-sind)
2. [Zwei Transaktionsmodi](#modi)
3. [Voraussetzungen und Einschränkungen](#voraussetzungen)
4. [Tutorial: Transaktionen koordinieren](#tutorial)
5. [Zusammenfassung](#zusammenfassung)

---

## <a id="was-sind">1. Was sind Transaktionen?</a>

Transaktionen koordinieren Operationen über mehrere SQL-Statements und Tabellen hinweg und stellen sicher, dass alle Änderungen gemeinsam gelingen oder vollständig zurückgerollt werden. Sie bieten ACID-Garantien: Atomicity, Consistency, Isolation und Durability.

### Unterstützte Operationen

`SELECT`, `VALUES`-Klauseln, `INSERT` (alle Varianten), `UPDATE`, `COPY INTO`, `DELETE FROM`, `MERGE INTO`, `USE CATALOG`/`SCHEMA`, `EXECUTE IMMEDIATE`, `DESCRIBE TABLE`, `SHOW COLUMNS` und `GET DIAGNOSTICS`.

### Isolation und Nebenläufigkeit

Transaktionen erfassen konsistente Snapshots beim ersten Tabellenzugriff. Das System nutzt Optimistic Concurrency Control mit Konflikterkennung zur Commit-Zeit. **Non-Interactive Transactions** unterstützen Row-Level Concurrency (siehe [Liquid Clustering.md](../../Performance%20Optimization/Foundation%20Design/Liquid%20Clustering.md), Abschnitt 9.2); **Interactive Transactions** nutzen Table-Level Concurrency.

---

## <a id="modi">2. Zwei Transaktionsmodi</a>

### 2.1 Non-Interactive (`BEGIN ATOMIC`)

„Committet oder rollt automatisch zurück. Am besten geeignet für geplante Jobs und feste Statement-Sequenzen." Nutzt SQL-Scripting mit dem `ATOMIC`-Schlüsselwort, um alle Statements als eine einzige atomare Einheit auszuführen — entweder gelingen alle, oder alle scheitern gemeinsam.

**Unterstütztes Compute:** SQL Warehouses, Serverless Compute oder Cluster mit Databricks Runtime 18.0+.

**Unterstützte Syntax:** SQL, Scala-`spark.sql`-Blöcke, PySpark-`spark.sql`-Blöcke.

```sql
BEGIN ATOMIC
  DELETE FROM staging_sales WHERE load_date < current_date() - INTERVAL 7 DAYS;
  INSERT INTO staging_sales SELECT * FROM raw_sales WHERE load_date = current_date();
  MERGE INTO sales AS target USING staging_sales AS source
  ON target.sale_id = source.sale_id
  WHEN MATCHED THEN UPDATE SET *
  WHEN NOT MATCHED THEN INSERT *;
END;
```

```python
spark.sql("""BEGIN ATOMIC
  UPDATE inventory SET quantity = quantity - 10 WHERE product_id = 2001;
  UPDATE inventory SET quantity = quantity + 10 WHERE product_id = 2002;
  INSERT INTO inventory_moves (from_product, to_product, quantity, move_date)
  VALUES (2001, 2002, 10, current_date());
END;""")
```

### 2.2 Interactive (`BEGIN TRANSACTION`)

„Gibt manuelle Kontrolle über Commit und Rollback. Am besten geeignet für Validierung, Debugging und JDBC-Clients." Transaktionsgrenzen werden explizit über manuelle `COMMIT`- oder `ROLLBACK`-Befehle verwaltet.

**Unterstütztes Compute:** nur SQL Warehouses.

**Unterstützte Syntax:** nur SQL.

```sql
BEGIN TRANSACTION;
INSERT INTO staging_customers SELECT * FROM external_customers WHERE load_date = current_date();
-- Validierungslogik mit bedingtem COMMIT/ROLLBACK
COMMIT;
```

**Über JDBC:**

```java
conn.setAutoCommit(false);
stmt.executeUpdate("INSERT INTO accounts (account_id, balance) VALUES (1001, 5000)");
stmt.executeUpdate("UPDATE accounts SET balance = balance - 100 WHERE account_id = 1001");
conn.commit();
```

### 2.3 Direkter Vergleich

| Aspekt | Non-Interactive | Interactive |
|---|---|---|
| Commit/Rollback | automatisch | manuell |
| Am besten geeignet für | geplante ETL-Jobs, feste Sequenzen | Datenvalidierung, JDBC-Anwendungen |
| Compute-Unterstützung | breiter (SQL Warehouses, Serverless, Runtime 18.0+ Cluster) | nur SQL Warehouses |
| Sprachunterstützung | SQL + Scala + Python | nur SQL |

---

## <a id="voraussetzungen">3. Voraussetzungen und Einschränkungen</a>

### Voraussetzungen

Alle beschriebenen Tabellen müssen Unity-Catalog-Managed-Tables sein (Delta oder Iceberg) mit aktivierten Catalog Commits (siehe [Table Features/01 Catalog Commits.md](Table%20Features/01%20Catalog%20Commits.md)). Unterstütztes Compute: SQL Warehouses, Serverless Compute oder Cluster mit Databricks Runtime 18.0+.

### Wichtige Einschränkungen

- Maximal **100 Tabellen** (lesend/schreibend kombiniert) sowie zusätzlich maximal **100 Views** (nur lesend) pro Transaktion; je Tabelle zudem maximal **100 Zwischen-Commits** innerhalb der Transaktion.
- **10-Minuten-Idle-Timeout** für Interactive Transactions.
- **48-Stunden-Maximaldauer** insgesamt.
- DDL-Operationen innerhalb von Transaktionen nicht unterstützt.
- Time Travel innerhalb von Transaktionen nicht verfügbar.

---

## <a id="tutorial">4. Tutorial: Transaktionen koordinieren</a>

### 4.1 Setup: Beispieltabellen erstellen

```sql
-- Kontodaten
CREATE TABLE IF NOT EXISTS sample_accounts (
  id INT,
  account_name STRING,
  balance DECIMAL(10,2)) USING DELTA
TBLPROPERTIES (
  'delta.feature.catalogManaged' = 'supported');

-- Transaktionsdatensätze
CREATE TABLE IF NOT EXISTS sample_transactions (
  id INT,
  account_id INT,
  transaction_type STRING,
  amount DECIMAL(10,2)) USING DELTA
TBLPROPERTIES (
  'delta.feature.catalogManaged' = 'supported');
```

**Transaktionen auf bestehenden Tabellen aktivieren:**

```sql
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported');
```

**Beispieldaten einfügen:**

```sql
INSERT INTO sample_accounts VALUES
  (1, 'Alice', 1000.00),
  (2, 'Bob', 500.00);

INSERT INTO sample_transactions VALUES
  (1, 1, 'deposit', 100.00);
```

### 4.2 Non-Interactive Transactions (`BEGIN ATOMIC`)

**Erfolgreiche atomare Transaktion:**

```sql
BEGIN ATOMIC
  -- Alices Kontostand aktualisieren
  UPDATE sample_accounts
  SET balance = balance + 100.00
  WHERE id = 1;

  -- Einzahlungstransaktion protokollieren
  INSERT INTO sample_transactions
  VALUES (2, 1, 'deposit', 100.00);
END;
```

**Transaktionsfehlschlag mit `SIGNAL`:**

```sql
BEGIN ATOMIC
  INSERT INTO sample_accounts VALUES (3, 'Charlie', -50.00);
  IF (SELECT balance FROM sample_accounts WHERE id = 3) < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Account balance cannot be negative';
  END IF;
END;
```

**Automatischer Rollback bei Fehlschlag:**

```sql
BEGIN ATOMIC
  -- Gültig
  INSERT INTO sample_accounts VALUES (4, 'David', 300.00);
  -- Ungültig
  INSERT INTO non_existent_table VALUES (1, 2, 3);
END;
```

### 4.3 Interactive Transactions (`BEGIN TRANSACTION`)

**Änderungen committen:**

```sql
BEGIN TRANSACTION;

INSERT INTO sample_accounts VALUES (5, 'Eve', 850.00);
UPDATE sample_accounts SET balance = balance + 50.00 WHERE id = 2;

COMMIT;
```

**Änderungen zurückrollen:**

```sql
BEGIN TRANSACTION;

INSERT INTO sample_accounts VALUES (6, 'Frank', 600.00);

SELECT * FROM sample_accounts WHERE id = 6;

ROLLBACK;
```

### 4.4 Fortgeschritten: Stored Procedures und SQL Scripting

**Produktionstabellen erstellen:**

```sql
CREATE SCHEMA IF NOT EXISTS main.retail;

CREATE TABLE IF NOT EXISTS main.retail.orders (
  order_id STRING,
  customer_id STRING,
  amount DECIMAL(18,2))
TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported');

CREATE TABLE IF NOT EXISTS main.retail.orders_staging (
  order_id STRING,
  customer_id STRING,
  amount DECIMAL(18,2),
  batch_id STRING)
TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported');

CREATE TABLE IF NOT EXISTS main.retail.total_sales (
  customer_id STRING,
  total_amount DECIMAL(18,2))
TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported');
```

**Stored Procedure definieren:**

```sql
CREATE OR REPLACE PROCEDURE main.retail.apply_order(
    IN  p_order_id      STRING,
    IN  p_customer_id   STRING,
    IN  p_order_amount  DECIMAL(18,2))
LANGUAGE SQL
SQL SECURITY INVOKER
MODIFIES SQL DATA
AS
BEGIN
    -- Bestellung einfügen
    INSERT INTO main.retail.orders (order_id, customer_id, amount)
    VALUES (p_order_id, p_customer_id, p_order_amount);

    -- Gesamtumsatz je Kunde aktualisieren
    MERGE INTO main.retail.total_sales AS t
    USING (
        SELECT
          p_customer_id  AS customer_id,
          p_order_amount AS order_amount
    ) s
      ON t.customer_id = s.customer_id
    WHEN MATCHED THEN
      UPDATE SET t.total_amount = t.total_amount + s.order_amount
    WHEN NOT MATCHED THEN
      INSERT (customer_id, total_amount)
      VALUES (s.customer_id, s.order_amount);
END;
```

**Vollständige Transaktion mit Stored Procedure:**

```sql
BEGIN ATOMIC
    -- Staging-Batch-ID für diese Transaktion
    DECLARE new_order_id STRING DEFAULT uuid();
    DECLARE v_batch_id STRING DEFAULT uuid();

    -- 1) Eingehende Kunden- und Bestelldaten stagen
    INSERT INTO main.retail.orders_staging (order_id, customer_id, amount, batch_id)
    VALUES (new_order_id, 'CUST_123', 249.99, v_batch_id);

    -- 2) Finale Schreibvorgänge vom Staging zur Produktion über Stored Procedure treiben
    FOR o AS
      SELECT
        order_id,
        customer_id,
        amount
      FROM main.retail.orders_staging
      WHERE batch_id = v_batch_id
    DO
        CALL main.retail.apply_order(
          o.order_id,
          o.customer_id,
          o.amount
        );
    END FOR;

    -- 3) Verarbeitete Staging-Zeilen bereinigen
    DELETE FROM main.retail.orders_staging
    WHERE batch_id = v_batch_id;
END;
```

### 4.5 Aufräumen

```sql
DROP TABLE IF EXISTS sample_accounts;
DROP TABLE IF EXISTS sample_transactions;
DROP TABLE IF EXISTS main.retail.orders;
DROP TABLE IF EXISTS main.retail.orders_staging;
DROP TABLE IF EXISTS main.retail.total_sales;
```

---

## <a id="zusammenfassung">5. Zusammenfassung</a>

- **Transaktionen** ermöglichen atomare Multi-Statement-, Multi-Table-Operationen mit vollen ACID-Garantien — aufbauend auf Catalog Commits.
- **Non-Interactive (`BEGIN ATOMIC`)** committet/rollt automatisch zurück, ideal für geplante Jobs; unterstützt SQL, Scala und Python.
- **Interactive (`BEGIN TRANSACTION`)** gibt manuelle Kontrolle über `COMMIT`/`ROLLBACK`, ideal für Validierung und JDBC-Anwendungen; nur SQL, nur SQL Warehouses.
- Wichtige Grenzen: maximal 100 Tabellen/Views pro Transaktion, 10-Minuten-Idle-Timeout (Interactive), 48-Stunden-Maximaldauer, keine DDL-Operationen, kein Time Travel innerhalb einer Transaktion.
- SQL Scripting mit `DECLARE`, `IF`/`SIGNAL`, `FOR`-Schleifen und Stored Procedures lässt sich vollständig in `BEGIN ATOMIC`-Blöcken kombinieren, um komplexe, mehrstufige ETL-Logik atomar auszuführen.

---

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### BEGIN TRANSACTION

Syntax-Diagramm: `BEGIN { TRANSACTION | WORK }` — `WORK` ist ein reines Synonym für `TRANSACTION`.

**Konsistenter Snapshot bei Transaktionsbeginn:**

```sql
BEGIN TRANSACTION;
SELECT COUNT(*) FROM orders;
COMMIT;
```

Die Transaktion erfasst einen konsistenten Snapshot beim ersten Tabellenzugriff. Nebenläufige Änderungen anderer Sessions werden innerhalb der Transaktion nicht sichtbar, selbst wenn sie zwischenzeitlich committet werden.

### BEGIN ATOMIC

Syntax-Diagramm:

```sql
BEGIN ATOMIC
  statement1;
  statement2;
  ...
END;
```

Damit lassen sich mehrere Tabellen in einem atomaren Block aktualisieren und dabei per `SIGNAL` validieren, bevor committet wird — siehe Abschnitt 4.2 dieser Datei für ein ausführliches Beispiel.

### COMMIT

Syntax: `COMMIT [ TRANSACTION | WORK ]`

**Wichtige Falle — `COMMIT` allein macht Statements nach einem Fehler nicht ungeschehen:**

```sql
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
ROLLBACK;
```

Nach einem erfolgreichen `COMMIT` ist ein nachfolgendes `ROLLBACK` wirkungslos für bereits committete Änderungen. `COMMIT` und `ROLLBACK` beziehen sich stets auf die *aktuell offene* Transaktion, nicht auf die zuletzt geschlossene.

### ROLLBACK

Syntax: `ROLLBACK [ TRANSACTION | WORK ]`

**Nach einem fehlgeschlagenen Statement ist explizites `ROLLBACK` Pflicht, bevor weitergearbeitet werden kann:**

```sql
BEGIN TRANSACTION;
SELECT 1/0;
SELECT 1;
ROLLBACK TRANSACTION;
```

Dies gilt sowohl für Laufzeitfehler (z. B. Division durch Null) als auch für Parserfehler in einem Statement — die Transaktion bleibt bis zum expliziten `ROLLBACK` in einem Fehlerzustand hängen.

**Bedingtes Rollback über SQL Scripting:**

```sql
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
BEGIN
  DECLARE total_balance INT;
  SET total_balance = (SELECT SUM(balance) FROM accounts);
  IF total_balance < 0 THEN
    ROLLBACK;
  ELSE
    COMMIT;
  END IF;
END;
```
