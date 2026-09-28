# Temporäre Tabellen in Databricks SQL und Databricks Runtime

Temporäre Tabellen speichern Daten nur für die Dauer einer Databricks-Sitzung. Sie eignen sich für Zwischenergebnisse bei explorativer Analyse oder in SQL-Datenpipelines, ohne dauerhafte Tabellen im Katalog anzulegen.

Gültig ab Databricks Runtime 18.1 und in Databricks SQL.

## Wann temporäre Tabellen sinnvoll sind

- Kurzlebige Zwischenergebnisse während explorativer Analyse oder Entwicklung speichern
- Abfrageergebnisse mehrfach in derselben Sitzung wiederverwenden
- Eine tabellenähnliche Schnittstelle nutzen, ohne den Katalog-Namensraum zu belegen

**Wichtig:** Müssen Daten über die aktuelle Sitzung hinaus bestehen bleiben oder mit anderen Nutzern oder Jobs geteilt werden, sollte stattdessen eine dauerhafte Unity-Catalog-Tabelle verwendet werden.

## Temporäre Tabelle erstellen oder ersetzen

Zum Erstellen dient `CREATE TEMPORARY TABLE` oder `CREATE TEMP TABLE`. Zum Ersetzen dient `[CREATE OR] REPLACE TEMPORARY TABLE` oder `[CREATE OR] REPLACE TEMP TABLE`.

```sql
%sql
-- Create an empty temporary table with a defined schema
CREATE TEMPORARY TABLE temp_customers (
  id INT,
  name STRING
);

-- Replace the temporary table with a new defined schema
REPLACE TEMP TABLE temp_customers (
  id INT,
  name STRING,
  email STRING
);
```

```sql
%sql
-- Create or replace a temporary table from query results
CREATE OR REPLACE TEMP TABLE temp_recent_orders AS
SELECT order_id, customer_id, order_date, amount
FROM prod.sales.orders
WHERE order_date >= current_date() - INTERVAL 30 DAYS;

-- Create a temporary table using VALUES clause
CREATE TEMP TABLE temp_test_data AS
VALUES
  (9001, 101, 50.00),
  (9002, 204, 75.00),
  (9003, 101, 25.00)
AS t(order_id, customer_id, amount);
```

### Wichtige Hinweise zur Erstellung

- Die `USING`-Klausel darf beim Erstellen von temporären Tabellen nicht angegeben werden.
- Temporäre Tabellen nutzen standardmäßig das Delta-Lake-Format.
- Zum Ersetzen (`REPLACE`) einer temporären Tabelle muss das Schlüsselwort `TEMPORARY` oder `TEMP` angegeben werden.

## Temporäre Tabellen abfragen

Der Zugriff erfolgt nur über den Tabellennamen, ohne Angabe von Katalog oder Schema.

```sql
%sql
-- Query a temporary table
SELECT * FROM temp_customers;

-- Join temporary tables with permanent tables
SELECT
  c.name,
  o.order_id,
  o.amount
FROM temp_customers c
INNER JOIN temp_recent_orders o
  ON c.id = o.customer_id;
```

## Reihenfolge der Namensauflösung

Databricks sucht in folgender Reihenfolge:

1. Temporäre Tabellen in der aktuellen Sitzung
2. Dauerhafte Tabellen im aktuellen Schema

### Namenskonflikte

Trägt eine temporäre Tabelle denselben Namen wie eine dauerhafte Tabelle, hat die temporäre Tabelle in dieser Sitzung Vorrang.

```sql
%sql
-- References temporary table (if it exists)
SELECT * FROM customers;

-- Explicitly references permanent table
SELECT * FROM prod.sales.customers;
```

## Temporäre Tabellen ändern

Unterstützt werden Insert-, Update- und Merge-Operationen über die üblichen DML-Befehle.

```sql
%sql
-- Insert data into a temporary table
INSERT INTO temp_customers VALUES (101, 'Jane Doe', 'jane@example.com');

-- Insert from a query
INSERT INTO temp_customers
SELECT id, name, email
FROM prod.customer.active_customers
WHERE region = 'US-WEST';

-- Update rows in a temporary table
UPDATE temp_recent_orders
SET amount = amount * 0.90
WHERE customer_id = 101;

-- Merge data into a temporary table
MERGE INTO temp_customers target
USING prod.customer.new_signups source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

**Einschränkung:** `DELETE FROM`-Operationen werden für temporäre Tabellen nicht unterstützt. Stattdessen sollte `MERGE INTO` mit einer Filterbedingung genutzt werden, oder die Tabelle wird mit gefilterten Daten neu erstellt.

## Temporäre Tabellen löschen

Databricks löscht temporäre Tabellen automatisch, sobald die Sitzung endet.

```sql
%sql
-- Drop a temporary table
DROP TEMP TABLE temp_customers;

-- Drop only if it exists
DROP TEMP TABLE IF EXISTS temp_recent_orders;
```

## Lebensdauer und zeitliche Grenzen

- Temporäre Tabellen existieren nur innerhalb der Databricks-Sitzung, in der sie erstellt wurden.
- Die maximale Lebensdauer beträgt sieben Tage ab Sitzungsbeginn.
- Sie werden unzugänglich, sobald die Sitzung endet oder nach sieben Tagen – je nachdem, was zuerst eintritt.
- Die Grenzen gelten für Notebooks, den SQL-Editor, Jobs und JDBC/ODBC-Sitzungen.

## Speicherung und Bereinigung

Databricks verwaltet den Speicherort für temporäre Tabellen automatisch. Er hängt vom Workspace-Typ ab:

- **Serverless-Workspaces:** Die Daten liegen im Standardspeicher. Ist ein Customer-Managed Key für Managed Services konfiguriert, wird dieser Schlüssel auch für temporäre Tabellen verwendet.
- **Classic Workspaces:** Die Daten liegen im Workspace-Storage-Bucket, der bei der Workspace-Erstellung konfiguriert wurde. Die Verschlüsselung lässt sich auf Bucket-Ebene konfigurieren.

Die Bereinigung ist in der Regel wenige Tage nach dem Ende der Zugänglichkeit abgeschlossen.

## Isolation und Berechtigungen

- Jeder Benutzer kann temporäre Tabellen erstellen.
- Es sind keine `CREATE TABLE`-Berechtigungen auf Katalog oder Schema nötig.
- Jede temporäre Tabelle existiert nur innerhalb der Sitzung, die sie erstellt hat.
- Andere Benutzer können temporäre Tabellen weder lesen, ändern noch überhaupt bemerken.
- Temporäre Tabellen teilen sich einen Namensraum mit temporären Views.

## Einschränkungen

- **Schema-Änderungen:** `ALTER TABLE`-Operationen werden nicht unterstützt.
- **Tabelleneigenschaften:** Nur die Klauseln `SET TBLPROPERTIES` und `UNSET TBLPROPERTIES` werden unterstützt.
- **Klonen:** Shallow und Deep Clone werden nicht unterstützt.
- **Time Travel:** Time-Travel-Abfragen werden nicht unterstützt.
- **Streaming:** Temporäre Tabellen können nicht in Streaming-Abfragen verwendet werden.
- **API-Unterstützung:** Nur SQL-APIs werden unterstützt. DataFrame-APIs werden nicht unterstützt.
- **Mehrbenutzer-Notebooks:** Nur ein Benutzer kann mit temporären Tabellen interagieren.
- **Dedicated Cluster:** Temporäre Tabellen werden auf Dedicated-(Single-User-)Clustern nicht unterstützt.
- **AWS GovCloud:** Temporäre Tabellen werden in AWS GovCloud und AWS GovCloud DoD nicht unterstützt.

## Weiterführende Ressourcen

- Unity Catalog Managed Tables für Delta Lake und Apache Iceberg
- Mit External Tables arbeiten
- SQL-Referenz: CREATE VIEW
- SQL-Referenz: CREATE TABLE
- SQL-Referenz: DROP TABLE
- SQL-Referenz: INSERT
- SQL-Referenz: MERGE INTO
- Dokumentation zur Namensauflösung

---
**Quelle:** https://docs.databricks.com/aws/en/tables/temporary-tables  
**Stand:** 2026-08-06
