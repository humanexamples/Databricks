## Table

Innerhalb eines [Schemas](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#schema) ist eine **Tabelle** das primäre sicherbare Objekt für strukturierte Daten in Unity Catalog. Databricks kennt folgende Tabellentypen:

- **Managed Tables** sind Tabellen, bei denen der Speicherort von Unity Catalog bestimmt wird. Wichtig: Die Daten selbst liegen weiterhin in deinem Cloud-Account. Databricks empfiehlt Managed Tables, um von den neuesten Tabellenfunktionen zu profitieren. Siehe [Unity Catalog Managed Tables für Delta Lake und Apache Iceberg](https://docs.databricks.com/aws/en/tables/managed).
- **External Tables** sind Tabellen, bei denen du den Speicherort selbst angibst. Unity Catalog verwaltet weiterhin die Metadaten der Tabelle, aber nicht den Lebenszyklus, die Optimierung, den Speicherort oder das Layout der Daten. Siehe [Mit External Tables arbeiten](https://docs.databricks.com/aws/en/tables/external).
- **Foreign Tables** sind Tabellen aus einem Foreign Catalog, die in Unity Catalog registriert sind. Siehe [Mit Foreign Tables arbeiten](https://docs.databricks.com/aws/en/tables/foreign).

Die folgende Tabelle fasst wichtige Details zu Tabellen zusammen:

| Detail | Beschreibung |
| :-------------------- | :----------------------------------------------------------- |
| Nutzungsprivilegien | Um auf eine Tabelle zuzugreifen, benötigt ein Nutzer `USE CATALOG` auf dem übergeordneten Katalog und `USE SCHEMA` auf dem übergeordneten Schema ([Nutzungsprivilegien](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges)), zusätzlich zum relevanten Tabellen-Level-Privileg wie `SELECT` oder `MODIFY`. |
| Vererbung | Tabellenprivilegien können vom übergeordneten Schema oder Katalog vererbt werden. `SELECT` auf einem Schema zu vergeben gewährt beispielsweise automatisch `SELECT` auf allen aktuellen und künftigen Tabellen in diesem Schema. Siehe [Privilegienvererbung](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#inheritance). |
| Lese- und Schreibzugriff | `SELECT` gewährt Lesezugriff, `MODIFY` gewährt Schreibzugriff (Insert, Update, Delete). Über [Lakehouse Federation](https://docs.databricks.com/aws/en/query-federation/) angebundene Foreign Tables sind schreibgeschützt und unterstützen das `MODIFY`-Privileg nicht. |

Weitere Informationen zu Tabellen siehe [Databricks-Tabellen](https://docs.databricks.com/aws/en/tables/).

```python
-- Mit der Anweisung DESCRIBE TABLE EXTENDED eine Tabelle beschreiben.
DESCRIBE TABLE EXTENDED mytable
```

```python
DROP TABLE IF EXISTS historical_users_bronze_ctas_rf;
```

```python
SELECT * FROM <catalog>.<schema>.<object> LIMIT 10;
```

```python
# Tabelle über die Apache-Spark-API lesen und anzeigen
mytable = spark.table(f"<catalog>.<schema>.<object>")
mytable.display()
```

```python
-- Historie einer Streaming Table
DESCRIBE HISTORY sql_csv_autoloader;
```

```python
SHOW TABLES;
```

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### ALTER TABLE

Ändert Schema oder Eigenschaften einer bestehenden Tabelle, z. B. Umbenennen, Properties setzen oder Speicherort ändern.

```sql
-- Tabelle umbenennen
ALTER TABLE student RENAME TO student_info;

-- Tabellen-Properties setzen bzw. entfernen
ALTER TABLE dbx.tab1 SET TBLPROPERTIES ('winner' = 'loser');
ALTER TABLE dbx.tab1 UNSET TBLPROPERTIES ('winner');
```

Quelle: [ALTER TABLE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-table)

### ALTER TABLE … ADD CONSTRAINT

Fügt Primary-Key-, Foreign-Key-, Unique- oder Check-Constraints hinzu.

```sql
CREATE TABLE persons(first_name STRING NOT NULL, last_name STRING NOT NULL, nickname STRING);
ALTER TABLE persons ADD CONSTRAINT persons_pk PRIMARY KEY(first_name, last_name);

-- Foreign Key, von Databricks nicht erzwungen, aber als gültig angenommen (RELY)
CREATE TABLE pets(name STRING, owner_first_name STRING, owner_last_name STRING);
ALTER TABLE pets ADD CONSTRAINT pets_persons_fk
    FOREIGN KEY(owner_first_name, owner_last_name) REFERENCES persons
    NOT ENFORCED RELY;

-- Check Constraint
ALTER TABLE pets ADD CONSTRAINT pets_name_not_cute_chk CHECK (length(name) < 20);
```

Quelle: [ALTER TABLE ADD CONSTRAINT](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-table-add-constraint)

### ALTER TABLE … DROP CONSTRAINT

Entfernt Primary-Key-, Foreign-Key- oder benannte Constraints wieder; `CASCADE` löscht auch abhängige Constraints.

```sql
-- Named Constraint löschen
ALTER TABLE pets DROP CONSTRAINT pets_name_not_cute_chk;

-- Foreign Key über die Spaltenliste löschen
ALTER TABLE pets DROP FOREIGN KEY IF EXISTS (owner_first_name, owner_last_name);

-- Primary Key inklusive abhängiger Foreign Keys löschen
ALTER TABLE persons DROP PRIMARY KEY CASCADE;
```

Quelle: [ALTER TABLE DROP CONSTRAINT](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-table-drop-constraint)

### ALTER TABLE … Spalten verwalten (ADD/ALTER/DROP/RENAME COLUMN)

Fügt Spalten hinzu, ändert deren Typ/Default/Nullability oder benennt bzw. entfernt sie.

```sql
-- Spalten hinzufügen
ALTER TABLE StudentInfo ADD COLUMNS (LastName STRING, DOB TIMESTAMP);

-- Default-Wert für eine Spalte setzen
ALTER TABLE StudentInfo ALTER COLUMN LastName SET DEFAULT 'unknown';

-- Spalte umbenennen bzw. entfernen
ALTER TABLE StudentInfo RENAME COLUMN LastName TO Surname;
ALTER TABLE StudentInfo DROP COLUMN IF EXISTS Surname;
```

Quelle: [ALTER TABLE — Spalten verwalten](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-table-manage-column)

### CREATE TABLE / CREATE TABLE USING

Legt eine neue Tabelle an — als Delta-, Iceberg- oder externe Tabelle, mit Kommentar, Properties, Partitionierung oder berechneten Spalten.

```sql
-- Delta-Tabelle mit Spaltendefinition
CREATE TABLE student (id INT, name STRING, age INT);

-- Tabelle aus dem Ergebnis einer Abfrage (CTAS)
CREATE TABLE student_copy AS SELECT * FROM student;

-- Partitionierte Tabelle mit Kommentar und Properties
CREATE TABLE student (id INT, name STRING, age INT)
    COMMENT 'this is a comment'
    TBLPROPERTIES ('foo'='bar')
    PARTITIONED BY (age);

-- Tabelle mit generierter (berechneter) Spalte
CREATE TABLE rectangles(a INT, b INT, area INT GENERATED ALWAYS AS (a * b));
```

Quelle: [CREATE TABLE USING](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-using) (Übersicht: [CREATE TABLE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table))

### CREATE TABLE … LIKE

Übernimmt die Struktur (Schema) einer bestehenden Tabelle, ohne deren Daten zu kopieren — optional mit neuem Speicherort oder Datenformat.

```sql
-- Struktur übernehmen, aber an einem neuen Speicherort
CREATE TABLE Student_Dupli LIKE Student LOCATION '/path/to/data_files';

-- Struktur übernehmen und als CSV-Datenquelle anlegen
CREATE TABLE Student_Dupli LIKE Student USING CSV LOCATION '/path/to/csv_files';
```

Quelle: [CREATE TABLE LIKE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-like)

### DROP TABLE

Löscht eine Tabelle. `FORCE` erlaubt das Löschen einer Basistabelle, auf die noch ein Shallow Clone verweist.

```sql
DROP TABLE IF EXISTS employeetable;

-- Basistabelle trotz existierendem Shallow Clone löschen
DROP TABLE employeetable FORCE;
```

Quelle: [DROP TABLE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-table)

### REPAIR TABLE

Aktualisiert die Partitionsinformationen einer Tabelle im Metastore, z. B. nachdem Partitionsverzeichnisse extern hinzugefügt wurden. In Unity Catalog synchronisiert `SYNC METADATA` die Metadaten.

```sql
-- Fehlende Partitionen anhand des Dateisystems nachtragen
MSCK REPAIR TABLE t1;

-- Metadaten mit dem Unity-Catalog-Service synchronisieren
MSCK REPAIR TABLE t1 SYNC METADATA;
```

Quelle: [REPAIR TABLE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-repair-table)

### TRUNCATE TABLE

Entfernt alle Zeilen einer Tabelle (oder einer bestimmten Partition), ohne die Tabelle selbst zu löschen.

```sql
-- Nur eine Partition leeren
TRUNCATE TABLE Student PARTITION (age = 10);

-- Alle Zeilen aus allen Partitionen entfernen
TRUNCATE TABLE Student;
```

Quelle: [TRUNCATE TABLE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-truncate-table)

### DESCRIBE TABLE

Zeigt Spalten und Metadaten einer Tabelle; `EXTENDED` liefert zusätzliche Details, `AS JSON` gibt das Ergebnis als JSON zurück.

```sql
DESCRIBE TABLE EXTENDED customer;

-- Nur eine bestimmte Spalte beschreiben
DESCRIBE customer salesdb.customer.name;

-- Ausgabe als JSON
DESCRIBE EXTENDED customer AS JSON;
```

Quelle: [DESCRIBE TABLE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-table)

### SHOW COLUMNS

Listet die Spaltennamen einer Tabelle auf.

```sql
SHOW COLUMNS IN customer;
SHOW COLUMNS IN salessc.customer;
```

Quelle: [SHOW COLUMNS](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-columns)

### SHOW CREATE TABLE

Gibt die `CREATE TABLE`-Anweisung zurück, mit der sich die Tabelle (inkl. aller Properties) rekonstruieren lässt.

```sql
CREATE TABLE test (c INT)
  TBLPROPERTIES ('prop1' = 'value1', 'prop2' = 'value2');

SHOW CREATE TABLE test;
```

Quelle: [SHOW CREATE TABLE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-create-table)

### SHOW TABLE EXTENDED

Zeigt erweiterte Informationen zu Tabellen, die einem Muster entsprechen — inklusive Partitionsdetails.

```sql
SHOW TABLE EXTENDED LIKE 'employee*';

-- Details zu einer bestimmten Partition
SHOW TABLE EXTENDED IN default LIKE 'employee' PARTITION (grade = 1);
```

Quelle: [SHOW TABLE EXTENDED](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-table)

### SHOW TABLES

Listet Tabellen eines Schemas auf, optional gefiltert per `LIKE`-Muster.

```sql
SHOW TABLES IN usersc;
SHOW TABLES FROM default LIKE 'sam*';
```

Quelle: [SHOW TABLES](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-tables)

### SHOW TABLES DROPPED

Listet kürzlich gelöschte Tabellen auf, die noch innerhalb der Wiederherstellungsfrist (`RETAIN DROPPED`) liegen und daher per `UNDROP TABLE` wiederhergestellt werden können.

```sql
USE CATALOG default;
USE SCHEMA my_schema;
DROP TABLE my_table_1;

SHOW TABLES DROPPED;
SHOW TABLES DROPPED IN default.my_schema;
```

Quelle: [SHOW TABLES DROPPED](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-tables-dropped)

### SHOW TBLPROPERTIES / TBLPROPERTIES-Klausel

`TBLPROPERTIES` setzt benutzerdefinierte Key-Value-Eigenschaften beim Anlegen einer Tabelle; `SHOW TBLPROPERTIES` liest sie aus.

```sql
CREATE TABLE customer(cust_code INT, name VARCHAR(100), cust_addr STRING)
    TBLPROPERTIES ('created.by.user' = 'John', 'created.date' = '01-01-2001');

SHOW TBLPROPERTIES customer;

-- Wert einer einzelnen Property abfragen
SHOW TBLPROPERTIES customer ('created.date');
```

Quellen: [SHOW TBLPROPERTIES](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-tblproperties), [TBLPROPERTIES-Klausel](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-tblproperties)

### UNDROP TABLE

Stellt eine kürzlich gelöschte Tabelle (oder Materialized View) innerhalb der Wiederherstellungsfrist wieder her — per Name oder über die per `SHOW TABLES DROPPED` ermittelte Tabellen-ID.

```sql
DROP TABLE my_catalog.my_schema.my_table;
UNDROP TABLE my_catalog.my_schema.my_table;

-- Wiederherstellung über die Tabellen-ID, falls der Name erneut vergeben wurde
UNDROP TABLE WITH ID '6ca7be55-8f58-47a7-85ee-7a59082fd17a';
```

Quelle: [UNDROP TABLE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-undrop-table)
