# 02 Unity Catalog — Gesamtzusammenfassung

Konsolidierte Übersicht aller 23 Objektreferenz-Dateien dieses Ordners (00–23) mit **allen** enthaltenen Code-Beispielen sowie einer kurzen, einfachen Einführung pro Thema. Jede Originaldatei bleibt die primäre, ausführliche Quelle — dieses Dokument dient als kompakter Überblick plus vollständige Code-Referenz an einem Ort.

## Inhalt

1. [Objektübersicht und Objektmodell](#1-objektübersicht-und-objektmodell)
2. [Metastore](#2-metastore)
3. [Catalog](#3-catalog)
4. [Schema](#4-schema)
5. [Table](#5-table)
6. [View](#6-view)
7. [Materialized View](#7-materialized-view)
8. [Metric View](#8-metric-view)
9. [Volume](#9-volume)
10. [Function](#10-function)
11. [Model](#11-model)
12. [Service](#12-service)
13. [Secret](#13-secret)
14. [Feature](#14-feature)
15. [Storage Credential](#15-storage-credential)
16. [External Location](#16-external-location)
17. [External Metadata](#17-external-metadata)
18. [Service Credential](#18-service-credential)
19. [Connection](#19-connection)
20. [Share](#20-share)
21. [Provider](#21-provider)
22. [Recipient](#22-recipient)
23. [Clean Room](#23-clean-room)
24. [Tags](#24-tags)
25. [Unity Catalog Compute: Zugriffsmodi, Fine-Grained Access Control und Lakeguard](#25-unity-catalog-compute-zugriffsmodi-fine-grained-access-control-und-lakeguard)
26. [Packaged Clean Rooms, Marketplace Apps und On-Behalf-Of-Authentifizierung](#26-packaged-clean-rooms-marketplace-apps-und-on-behalf-of-authentifizierung)
27. [Verifikationsprotokoll (Databricks-Blog-Abgleich)](#27-verifikationsprotokoll-databricks-blog-abgleich)

---

## 1. Objektübersicht und Objektmodell

**Einfach erklärt:** Unity Catalog ist die zentrale Governance-Schicht von Databricks. Alle Daten- und KI-Objekte werden in einem **dreistufigen Namespace** organisiert: `catalog.schema.objekt` — vergleichbar mit Ordner → Unterordner → Datei. Objekte sind entweder **Managed** (Unity Catalog verwaltet auch den Speicher) oder **External** (Unity Catalog verwaltet nur die Governance, der Speicher bleibt extern).

**Hierarchie:**

```
Metastore
 └── Catalog
      └── Schema
           ├── Table
           ├── View
           ├── Volume
           ├── Function
           ├── Model
           ├── Service
           └── Secret
```

Direkt unterhalb des Metastores (nicht im Catalog/Schema-Baum) liegen zwei weitere Objektgruppen:

- **Zugriff auf externe Systeme:** Storage Credential, External Location, External Metadata, Service Credential, Connection.
- **Daten-/KI-Sharing über Organisationsgrenzen:** Share, Provider, Recipient, Clean Room.

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick.

---

## 2. Metastore

**Einfach erklärt:** Der Metastore ist das oberste Objekt in Unity Catalog — ein Container pro Cloud-Region, der alle Kataloge sowie die Objekte zur Zugriffssteuerung und zum Daten-Sharing enthält. Ein Metastore kann mit mehreren Workspaces derselben Region verbunden sein; Rechte, die in einem Workspace vergeben werden, gelten dann in allen verbundenen Workspaces.

Wichtig: Metastore-Level-Privilegien (z. B. `CREATE CATALOG`) vererben sich **nicht** nach unten — anders als Katalog-/Schema-Grants, die automatisch für aktuelle und künftige Kindobjekte gelten. Der optionale **Metastore-Admin** kann u. a. den Metastore löschen, Workspace-Zuweisungen verwalten und die Eigentümerschaft jedes Objekts übernehmen.

Keine Code-Beispiele in dieser Datei.

---

## 3. Catalog

**Einfach erklärt:** Der Catalog ist die oberste Ebene innerhalb eines Metastores für eigene Daten-Assets — die erste Stufe des Drei-Ebenen-Namespace. Ein Catalog ist ein **Container-Objekt**: Rechte, die auf Catalog-Ebene vergeben werden, vererben sich automatisch an alle aktuellen und künftigen Schemas, Tabellen, Views, Volumes und Functions darin. `USE CATALOG` ist Voraussetzung, bevor überhaupt mit einem Objekt im Catalog interagiert werden kann. `BROWSE` erlaubt reines Entdecken der Metadaten ohne Datenzugriff. Per **Workspace-Bindung** lässt sich ein Catalog auf bestimmte Workspaces einschränken — das hat Vorrang vor jedem einzelnen Privileg.

```python
USE CATALOG dbacademy;
```

### ALTER CATALOG

```sql
-- Besitzer des Katalogs übertragen
ALTER CATALOG some_cat OWNER TO `alf@melmak.et`;

-- Tags setzen bzw. entfernen
ALTER CATALOG test SET TAGS ('tag1' = 'val1', 'tag2' = 'val2');
ALTER CATALOG test UNSET TAGS ('tag1', 'tag2');

-- Predictive Optimization aktivieren
ALTER CATALOG main ENABLE PREDICTIVE OPTIMIZATION;

-- 30-Tage-Wiederherstellungsfrist für gelöschte Managed Tables setzen
ALTER CATALOG my_catalog RETAIN DROPPED TO 30 DAYS;
```

### ALTER CATALOG … DROP CONNECTION

```sql
-- Konvertierung nur, wenn keine Foreign Tables/Views mehr existieren (Standard)
ALTER CATALOG hms_federated_catalog DROP CONNECTION;

-- Erzwungene Konvertierung inkl. Löschen verbleibender Foreign Tables
ALTER CATALOG hms_federated_catalog DROP CONNECTION FORCE;
```

### CREATE CATALOG

```sql
-- Katalog anlegen (nur falls nicht bereits vorhanden)
CREATE CATALOG IF NOT EXISTS customer_cat COMMENT 'This is customer catalog';

-- Katalog mit eigenem Managed-Storage-Ort
CREATE CATALOG customer_cat MANAGED LOCATION 's3://depts/finance';

-- Foreign Catalog über eine bestehende Connection (z. B. PostgreSQL)
CREATE FOREIGN CATALOG postgresql_catalog
  USING CONNECTION postgresql_connection
  OPTIONS (database = 'postgresdb');
```

### DROP CATALOG

```sql
-- Katalog inklusive aller Schemas löschen
DROP CATALOG vaccine CASCADE;

-- Katalog nur löschen, falls er existiert und leer ist
DROP CATALOG IF EXISTS vaccine RESTRICT;
```

### DESCRIBE CATALOG

```sql
DESCRIBE CATALOG main;
DESCRIBE CATALOG EXTENDED main;
```

### SHOW CATALOGS

```sql
SHOW CATALOGS;

-- Nur Kataloge, deren Name mit "pay" beginnt
SHOW CATALOGS LIKE 'pay*';
```

### USE CATALOG

```sql
USE CATALOG hive_metastore;

-- Katalog über eine String-Variable setzen
DECLARE mycat = 'main';
USE CATALOG IDENTIFIER(mycat);
```

---

## 4. Schema

**Einfach erklärt:** Ein Schema (auch "Datenbank" genannt) ist die zweite Ebene des Namespace, innerhalb eines Catalogs — vergleichbar mit einem Unterordner. Ein Schema kann ein einzelnes Projekt, einen Anwendungsfall oder eine Team-Sandbox repräsentieren und enthält Tabellen, Views, Volumes und Functions. Auch Schemas sind Container-Objekte mit Rechte-Vererbung; `USE SCHEMA` (zusätzlich zu `USE CATALOG` auf dem übergeordneten Catalog) ist Voraussetzung für jede Interaktion mit Objekten im Schema. `DATABASE` ist im Language Manual nur ein Alias für `SCHEMA` — Databricks bevorzugt `SCHEMA`.

```python
USE SCHEMA mySchema;
```

```python
-- Mit der Anweisung SHOW SCHEMAS IN die verfügbaren Schemas eines Katalogs anzeigen.
SHOW SCHEMAS IN mycatalog;
```

```python
-- Mit der Anweisung DESCRIBE SCHEMA EXTENDED Informationen zu einem Schema einsehen
DESCRIBE SCHEMA EXTENDED IDENTIFIER(DA.schema_name);
```

### ALTER SCHEMA

```sql
-- Schema-Eigenschaften setzen
ALTER SCHEMA inventory SET DBPROPERTIES ('Edited-by' = 'John', 'Edit-date' = '01/01/2001');

-- Besitzer übertragen
ALTER SCHEMA inventory OWNER TO `alf@melmak.et`;

-- Tags setzen
ALTER SCHEMA test SET TAGS ('tag1' = 'val1', 'tag2' = 'val2');

-- 7-Tage-Wiederherstellungsfrist für gelöschte Managed Tables (überschreibt Katalog-Einstellung)
ALTER SCHEMA my_catalog.my_schema SET RETAIN DROPPED TO 7 DAYS;
```

### ALTER SCHEMA … SET MANAGED LOCATION

```sql
ALTER SCHEMA my_catalog.my_schema SET MANAGED LOCATION 'abfss://container@account.dfs.core.windows.net/managed/';
```

### CREATE SCHEMA

```sql
CREATE SCHEMA IF NOT EXISTS customer_sc COMMENT 'This is customer schema';

-- Eigener Managed-Storage-Ort (nur in Unity Catalog unterstützt)
CREATE SCHEMA customer_sc MANAGED LOCATION 's3://depts/finance';

-- 14-Tage-Wiederherstellungsfrist für gelöschte Managed Tables
CREATE SCHEMA customer_sc RETAIN DROPPED FOR 14 DAYS;
```

### DROP SCHEMA

```sql
DROP SCHEMA inventory_schema CASCADE;
DROP SCHEMA IF EXISTS inventory_schema CASCADE;
```

### DESCRIBE SCHEMA

```sql
DESCRIBE SCHEMA employees;

ALTER SCHEMA employees SET DBPROPERTIES ('Create-by' = 'Kevin', 'Create-date' = '09/01/2019');
DESCRIBE SCHEMA EXTENDED employees;
```

### SHOW SCHEMAS

```sql
SHOW SCHEMAS;
SHOW SCHEMAS LIKE 'pay*';
SHOW SCHEMAS IN some_catalog;
```

### USE SCHEMA

```sql
USE SCHEMA userschema;

USE CATALOG main;
USE SCHEMA my_schema;
SELECT current_catalog(), current_schema();
```

---

## 5. Table

**Einfach erklärt:** Die Tabelle ist das zentrale Objekt für strukturierte Daten — Zeilen und Spalten, innerhalb eines Schemas. Drei Typen: **Managed** (Unity Catalog bestimmt den Speicherort, empfohlener Standard, profitiert von neuesten Features), **External** (eigener Speicherort, Unity Catalog verwaltet nur Metadaten, keine Löschung der Daten bei `DROP`) und **Foreign** (aus einem Foreign Catalog registriert, meist nur lesend). Zugriff braucht immer `USE CATALOG` + `USE SCHEMA` zusätzlich zum Tabellen-Privileg (`SELECT` = lesen, `MODIFY` = schreiben).

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

### ALTER TABLE

```sql
-- Tabelle umbenennen
ALTER TABLE student RENAME TO student_info;

-- Tabellen-Properties setzen bzw. entfernen
ALTER TABLE dbx.tab1 SET TBLPROPERTIES ('winner' = 'loser');
ALTER TABLE dbx.tab1 UNSET TBLPROPERTIES ('winner');
```

### ALTER TABLE … ADD CONSTRAINT

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

### ALTER TABLE … DROP CONSTRAINT

```sql
-- Named Constraint löschen
ALTER TABLE pets DROP CONSTRAINT pets_name_not_cute_chk;

-- Foreign Key über die Spaltenliste löschen
ALTER TABLE pets DROP FOREIGN KEY IF EXISTS (owner_first_name, owner_last_name);

-- Primary Key inklusive abhängiger Foreign Keys löschen
ALTER TABLE persons DROP PRIMARY KEY CASCADE;
```

### ALTER TABLE … Spalten verwalten (ADD/ALTER/DROP/RENAME COLUMN)

```sql
-- Spalten hinzufügen
ALTER TABLE StudentInfo ADD COLUMNS (LastName STRING, DOB TIMESTAMP);

-- Default-Wert für eine Spalte setzen
ALTER TABLE StudentInfo ALTER COLUMN LastName SET DEFAULT 'unknown';

-- Spalte umbenennen bzw. entfernen
ALTER TABLE StudentInfo RENAME COLUMN LastName TO Surname;
ALTER TABLE StudentInfo DROP COLUMN IF EXISTS Surname;
```

### CREATE TABLE / CREATE TABLE USING

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

### CREATE TABLE … LIKE

```sql
-- Struktur übernehmen, aber an einem neuen Speicherort
CREATE TABLE Student_Dupli LIKE Student LOCATION '/path/to/data_files';

-- Struktur übernehmen und als CSV-Datenquelle anlegen
CREATE TABLE Student_Dupli LIKE Student USING CSV LOCATION '/path/to/csv_files';
```

### DROP TABLE

```sql
DROP TABLE IF EXISTS employeetable;

-- Basistabelle trotz existierendem Shallow Clone löschen
DROP TABLE employeetable FORCE;
```

### REPAIR TABLE

```sql
-- Fehlende Partitionen anhand des Dateisystems nachtragen
MSCK REPAIR TABLE t1;

-- Metadaten mit dem Unity-Catalog-Service synchronisieren
MSCK REPAIR TABLE t1 SYNC METADATA;
```

### TRUNCATE TABLE

```sql
-- Nur eine Partition leeren
TRUNCATE TABLE Student PARTITION (age = 10);

-- Alle Zeilen aus allen Partitionen entfernen
TRUNCATE TABLE Student;
```

### DESCRIBE TABLE

```sql
DESCRIBE TABLE EXTENDED customer;

-- Nur eine bestimmte Spalte beschreiben
DESCRIBE customer salesdb.customer.name;

-- Ausgabe als JSON
DESCRIBE EXTENDED customer AS JSON;
```

### SHOW COLUMNS

```sql
SHOW COLUMNS IN customer;
SHOW COLUMNS IN salessc.customer;
```

### SHOW CREATE TABLE

```sql
CREATE TABLE test (c INT)
  TBLPROPERTIES ('prop1' = 'value1', 'prop2' = 'value2');

SHOW CREATE TABLE test;
```

### SHOW TABLE EXTENDED

```sql
SHOW TABLE EXTENDED LIKE 'employee*';

-- Details zu einer bestimmten Partition
SHOW TABLE EXTENDED IN default LIKE 'employee' PARTITION (grade = 1);
```

### SHOW TABLES

```sql
SHOW TABLES IN usersc;
SHOW TABLES FROM default LIKE 'sam*';
```

### SHOW TABLES DROPPED

```sql
USE CATALOG default;
USE SCHEMA my_schema;
DROP TABLE my_table_1;

SHOW TABLES DROPPED;
SHOW TABLES DROPPED IN default.my_schema;
```

### SHOW TBLPROPERTIES / TBLPROPERTIES-Klausel

```sql
CREATE TABLE customer(cust_code INT, name VARCHAR(100), cust_addr STRING)
    TBLPROPERTIES ('created.by.user' = 'John', 'created.date' = '01-01-2001');

SHOW TBLPROPERTIES customer;

-- Wert einer einzelnen Property abfragen
SHOW TBLPROPERTIES customer ('created.date');
```

### UNDROP TABLE

```sql
DROP TABLE my_catalog.my_schema.my_table;
UNDROP TABLE my_catalog.my_schema.my_table;

-- Wiederherstellung über die Tabellen-ID, falls der Name erneut vergeben wurde
UNDROP TABLE WITH ID '6ca7be55-8f58-47a7-85ee-7a59082fd17a';
```

---

## 6. View

**Einfach erklärt:** Eine View ist eine gespeicherte, schreibgeschützte SQL-Abfrage über eine oder mehrere Tabellen/Views — das Ergebnis wird bei jeder Abfrage neu berechnet, nicht gespeichert. Besonderheit: Nutzer brauchen keine Rechte auf den zugrunde liegenden Tabellen, nur `SELECT` auf der View selbst — zur Laufzeit gelten die Rechte des View-Eigentümers. Das macht Views nützlich, um nur bestimmte Zeilen/Spalten offenzulegen, ohne die Basistabelle direkt freizugeben.

### ALTER VIEW

```sql
-- View umbenennen
ALTER VIEW tempsc1.v1 RENAME TO tempsc1.v2;

-- View-Definition (Abfrage) ändern
ALTER VIEW tempsc1.v2 AS SELECT * FROM tempsc1.v1;

-- Besitzer übertragen
ALTER VIEW v1 OWNER TO `alf@melmak.et`;
```

### ALTER VIEW … SET MANAGED

```sql
ALTER VIEW hms_federated_catalog.my_schema.my_view SET MANAGED;
```

### CREATE VIEW

```sql
-- View mit Kommentaren und WHERE-Filter
CREATE OR REPLACE VIEW experienced_employee
    (id COMMENT 'Unique identification number', Name)
    COMMENT 'View for experienced employees'
    AS SELECT id, name
         FROM all_employee
        WHERE working_years > 5;

-- Temporäre View (nur für die aktuelle Session sichtbar)
CREATE TEMPORARY VIEW subscribed_movies
    AS SELECT mo.member_id, mb.full_name, mo.movie_title
         FROM movies AS mo
         INNER JOIN members AS mb
            ON mo.member_id = mb.id;

-- View mit SCHEMA EVOLUTION, damit sie Änderungen der Basistabelle automatisch übernimmt
CREATE VIEW emp_v WITH SCHEMA EVOLUTION AS SELECT * FROM emp;
```

### DROP VIEW

```sql
DROP VIEW IF EXISTS employeeView;
DROP VIEW usersc.employeeView;
```

### SHOW VIEWS

```sql
SHOW VIEWS FROM usersc;
SHOW VIEWS LIKE 'sam*';
```

---

## 7. Materialized View

**Einfach erklärt:** Eine Materialized View ist wie eine normale View, speichert ihr Ergebnis aber vorab — die Daten spiegeln den Stand der letzten Aktualisierung wider, statt bei jeder Abfrage neu berechnet zu werden. Zusätzlich zu `SELECT`/`MANAGE` gibt es das `REFRESH`-Privileg, um eine Aktualisierung auszulösen; reine `SELECT`-Nutzer können nur die gespeicherten Ergebnisse lesen.

### CREATE MATERIALIZED VIEW

```sql
-- Materialized View, die aktualisiert wird, sobald sich die Quelldaten ändern
CREATE MATERIALIZED VIEW IF NOT EXISTS subscribed_movies
  TRIGGER ON UPDATE
  AS SELECT mo.member_id, mb.full_name, mo.movie_title
       FROM movies AS mo INNER JOIN members AS mb ON mo.member_id = mb.id;

-- Täglich per Zeitplan aktualisierte Materialized View
CREATE MATERIALIZED VIEW daily_sales
  COMMENT 'Daily sales numbers'
  SCHEDULE EVERY 1 DAY
  AS SELECT date AS date, sum(sales) AS sumOfSales
       FROM table1
       GROUP BY date;

-- Materialized View mit Row Filter und Column Mask
CREATE MATERIALIZED VIEW masked_view (
    id int,
    name string,
    region string,
    ssn string MASK catalog.schema.ssn_mask_fn
  )
  WITH ROW FILTER catalog.schema.us_filter_fn ON (region)
  AS SELECT id, name, region, ssn
       FROM employees;
```

### ALTER MATERIALIZED VIEW

```sql
-- Aktualisierung auslösen, sobald sich die Quelldaten ändern
ALTER MATERIALIZED VIEW my_mv ADD TRIGGER ON UPDATE;

-- Zeitplan auf alle 2 Stunden ändern
ALTER MATERIALIZED VIEW my_mv ALTER SCHEDULE EVERY 2 HOURS;

-- Zeitplan per Cron-Ausdruck ändern (täglich um Mitternacht, Zeitzone Los Angeles)
ALTER MATERIALIZED VIEW my_mv ALTER SCHEDULE CRON '0 0 0 * * ? *' AT TIME ZONE 'America/Los_Angeles';
```

### EXPLAIN CREATE MATERIALIZED VIEW

```sql
EXPLAIN CREATE MATERIALIZED VIEW foo
AS
SELECT k, sum(v) FROM source.src_schema.table GROUP BY k;
```

---

## 8. Metric View

**Einfach erklärt:** Eine Metric View definiert wiederverwendbare Business-Metriken (z. B. Umsatz, Churn) einmal zentral, getrennt von den Dimensionen, nach denen gruppiert/gefiltert wird — und lässt sich danach wie eine normale View abfragen. Ziel: eine Kennzahl wird einmal definiert und überall konsistent berechnet, egal ob per SQL, BI-Tool oder Agent. Berechtigungsmodell wie bei Standard-Views (`SELECT` + Nutzungsprivilegien; Owner-Rechte lösen die Datenquellen zur Laufzeit auf).

Keine Code-Beispiele in dieser Datei.

---

## 9. Volume

**Einfach erklärt:** Ein Volume ist das sicherbare Objekt für **unstrukturierte** Daten (Dateien beliebigen Formats) im Cloud-Speicher — im Gegensatz zu Tabellen unterstützt es keine SQL-Abfragen, sondern dateibasierten Zugriff. Auch hier: **Managed** (Speicherort von Unity Catalog bestimmt) vs. **External** (eigener Pfad, z. B. für Zugriff von außerhalb Databricks). Zugriffspfad-Format: `/Volumes/catalog_name/schema_name/volume_name/`. Rechte: `READ VOLUME` zum Lesen, `WRITE VOLUME` zum Schreiben/Ändern/Löschen.

```python
-- Führen Sie den folgenden Befehl aus, um eine Liste der Volumes in einem bestimmten Schema anzuzeigen.
SHOW VOLUMES IN catalog_name.schema_name;
```

```python
-- Verwenden Sie die DESCRIBE VOLUME-Anweisung, um die Metadaten eines Volumes zurückzugeben.
DESCRIBE VOLUME myvolume;
```

```python
-- Verwenden Sie die LIST-Anweisung, um die verfügbaren Dateien in einem Verzeichnis aufzulisten.
LIST '/Volumes/catalog_name/schema_name/volume_name/'

-- ADLS 2
LIST 'abfss://container-name@storage-account-name.dfs.core.windows.net/path/to/data'

-- S3
LIST 's3://bucket-name/path/to/data'

-- GCS
LIST 'gs://bucket-name/path/to/data'
```

```python
spark.sql(f"LIST '{my_vol_path}/bright_home_orders'").display()
```

```python
CREATE VOLUME IF NOT EXISTS trigger_storage_location
```

### CREATE VOLUME

```sql
-- External Volume mit eigenem Speicherort
CREATE EXTERNAL VOLUME my_catalog.my_schema.my_external_volume
  LOCATION 's3://my-bucket/my-location/my-path'
  COMMENT 'This is my example external volume on S3';

-- Managed Volume mit vollqualifiziertem Namen
CREATE VOLUME my_catalog.my_schema.my_volume;
```

### ALTER VOLUME

```sql
ALTER VOLUME my_volume RENAME TO new_name_volume;
ALTER VOLUME my_volume SET TAGS ('tag1' = 'val1', 'tag2' = 'val2');
```

### DROP VOLUME

```sql
DROP VOLUME IF EXISTS my_catalog.my_schema.my_volume;
```

### DESCRIBE VOLUME

```sql
DESCRIBE VOLUME my_external_volume;
```

### SHOW VOLUMES

```sql
SHOW VOLUMES IN machine_learning;
SHOW VOLUMES LIKE 'a*';
```

### LIST

```sql
LIST 's3://us-east-1-dev/some_dir' WITH (CREDENTIAL aws_some_dir) LIMIT 2;
```

---

## 10. Function

**Einfach erklärt:** Eine Function ist wiederverwendbare, ausführbare Logik in einem Schema — umfasst benutzerdefinierte Funktionen (UDFs) in SQL/Python, Stored Procedures (SQL-Anweisungsfolgen mit Seiteneffekten) und registrierte MLflow-Modelle (technisch ebenfalls als Function implementiert). Zugriff braucht `EXECUTE` auf der Function zusätzlich zu den Nutzungsprivilegien; `EXECUTE` erlaubt Aufruf **und** Einsicht in Definition/Metadaten.

### CREATE FUNCTION (SQL User-Defined Function)

```sql
-- Einfache Skalarfunktion
CREATE FUNCTION area(x DOUBLE, y DOUBLE) RETURNS DOUBLE RETURN x * y;
SELECT area(3, 4);

-- Funktion mit DEFAULT-Parametern
CREATE FUNCTION roll_dice(num_dice INT DEFAULT 1, num_sides INT DEFAULT 6)
    RETURNS INT
    NOT DETERMINISTIC
    CONTAINS SQL
    COMMENT 'Roll a number of n-sided dice'
    RETURN (rand() * num_sides)::INT + 1;

-- Tabellenfunktion, die eine Ergebnismenge zurückgibt
CREATE FUNCTION weekdays(start DATE, end DATE)
    RETURNS TABLE(day_of_week STRING, day DATE)
    RETURN SELECT extract(DAYOFWEEK_ISO FROM day), day
             FROM (SELECT sequence(weekdays.start, weekdays.end)) AS T(days)
                  LATERAL VIEW explode(days) AS day
             WHERE extract(DAYOFWEEK_ISO FROM day) BETWEEN 1 AND 5;
```

### DROP FUNCTION

```sql
DROP FUNCTION hello;
DROP TEMPORARY FUNCTION IF EXISTS hello;
```

### DESCRIBE FUNCTION

```sql
DESCRIBE FUNCTION abs;
DESCRIBE FUNCTION EXTENDED abs;

-- Für eine selbst erstellte SQL-Funktion
CREATE FUNCTION dice(n INT) RETURNS INT
    NOT DETERMINISTIC
    COMMENT 'An n-sided dice'
    RETURN floor((rand() * n) + 1);
DESCRIBE FUNCTION EXTENDED dice;
```

### SHOW FUNCTIONS

```sql
SHOW SYSTEM FUNCTIONS IN salesdb max;
SHOW FUNCTIONS LIKE 't*';
```

---

## 11. Model

**Einfach erklärt:** Ein Model ist ein in Unity Catalog gespeichertes, versioniertes oder unversioniertes KI-Modell — ein Container für mehrere Trainingsläufe (Modellversionen), meist über MLflow befüllt. Zusätzliche Privilegien: `APPLY TAG` (Tags auf Model/Versionen), `CREATE MODEL VERSION` (neue Versionen registrieren, ohne Ausführungs-/Änderungsrecht). `CREATE MODEL` auf einem Catalog erlaubt Model-Erstellung in jedem Schema darin.

Keine Code-Beispiele in dieser Datei.

---

## 12. Service

**Einfach erklärt:** Ein Service ist ein governance-unterworfenes, aufrufbares KI-Asset (aktuell Beta) — entweder ein **Model Service** (LLM-Endpunkt) oder ein **MCP Service** (registrierter MCP-Server, steuert welche Tools Agenten nutzen dürfen). Damit lässt sich KI-Traffic mit denselben Privilegien regeln wie Daten: `CREATE SERVICE` zum Anlegen, `EXECUTE` zum Aufrufen (zusätzlich zu den Nutzungsprivilegien).

Keine Code-Beispiele in dieser Datei.

---

## 13. Secret

**Einfach erklärt:** Ein Secret speichert einen sensiblen Wert (Zugangsdaten, API-Token) im Drei-Ebenen-Namespace (`catalog.schema.secret`) — der Wert lässt sich in Code oder aus anderen Unity-Catalog-Objekten referenzieren, **ohne** ihn offenzulegen. Privilegien: `CREATE SECRET` (anlegen), `READ SECRET` (Wert abrufen), `WRITE SECRET` (aktualisieren), `REFERENCE SECRET` (Objekt darf referenzieren, ohne den Wert dem Nutzer zu zeigen).

Keine Code-Beispiele in dieser Datei.

---

## 14. Feature

**Public Preview.** **Einfach erklärt:** Ein Feature ist die gespeicherte Definition eines Machine-Learning-Merkmals — Quelldaten, Berechnungslogik, Zeitfenster — als einzige maßgebliche Quelle über Training, Materialisierung und Serving hinweg wiederverwendbar, mit Lineage-Tracking zu Quelldaten und nutzenden Modellen. Die Definition ist reine Metadatenoperation; berechnet wird erst bei der Materialisierung. Rechte: `CREATE FEATURE` zum Anlegen, `READ FEATURE` zum Lesen/Nutzen in Training und Inferenz.

Keine Code-Beispiele in dieser Datei.

---

## 15. Storage Credential

**Einfach erklärt:** Ein Storage Credential speichert die Authentifizierungsinformationen für einen Cloud-Speicherpfad — je Provider eine IAM-Rolle (AWS), ein Service Principal (Azure) oder ein Service Account (GCP). Meist Baustein für External Locations, kann aber auch direkt für External Tables genutzt werden. `CREATE STORAGE CREDENTIAL` wird auf Metastore-Ebene vergeben.

### ALTER STORAGE CREDENTIAL

```sql
-- Storage Credential umbenennen
ALTER STORAGE CREDENTIAL street_cred RENAME TO good_cred;

-- Eigentümer ändern
ALTER STORAGE CREDENTIAL street_cred OWNER TO `alf@melmak.et`;
```

### DROP STORAGE CREDENTIAL

```sql
-- Löschen erzwingen, auch wenn abhängige External Locations existieren
DROP STORAGE CREDENTIAL street_cred FORCE;

-- Ohne Fehler, falls das Credential nicht existiert
DROP STORAGE CREDENTIAL IF EXISTS street_cred;
```

### DESCRIBE STORAGE CREDENTIAL

```sql
DESCRIBE STORAGE CREDENTIAL good_cred;
```

### SHOW STORAGE CREDENTIALS

```sql
SHOW STORAGE CREDENTIALS;
```

---

## 16. External Location

**Einfach erklärt:** Eine External Location koppelt ein Storage Credential mit einem konkreten Cloud-Speicherpfad und regelt so den Zugriff auf diesen Pfad. `CREATE EXTERNAL LOCATION` wird auf Metastore-Ebene vergeben. Für Dateizugriff direkt auf dem Pfad braucht es `READ FILES`/`WRITE FILES` — Databricks empfiehlt aber, Cloud-Speicher stattdessen über **Volumes** (`READ VOLUME`/`WRITE VOLUME`) zu verwalten.

### CREATE EXTERNAL LOCATION

```sql
CREATE EXTERNAL LOCATION s3_remote URL 's3://us-east-1/location'
    WITH (STORAGE CREDENTIAL s3_remote_cred)
    COMMENT 'Default source for AWS exernal data';
```

### ALTER EXTERNAL LOCATION

```sql
-- Umbenennen
ALTER EXTERNAL LOCATION descend_loc RENAME TO decent_loc;

-- URL ändern (auch wenn die Location aktiv genutzt wird)
ALTER EXTERNAL LOCATION best_loc SET URL 's3://us-east-1-prod/best_location' FORCE;

-- Storage Credential wechseln
ALTER EXTERNAL LOCATION best_loc SET STORAGE CREDENTIAL street_cred;

-- Eigentümer ändern
ALTER EXTERNAL LOCATION best_loc OWNER TO `alf@melmak.et`;
```

### DROP EXTERNAL LOCATION

```sql
DROP EXTERNAL LOCATION IF EXISTS some_location;
```

### DESCRIBE EXTERNAL LOCATION / SHOW EXTERNAL LOCATIONS

```sql
DESCRIBE EXTERNAL LOCATION best_loco;

SHOW EXTERNAL LOCATIONS;
```

### REFRESH FOREIGN

```sql
REFRESH FOREIGN CATALOG some_catalog;
REFRESH FOREIGN SCHEMA some_catalog.some_schema;
REFRESH FOREIGN TABLE some_catalog.some_schema.some_table;

-- DBFS-Pfad einer föderierten Tabelle neu auflösen
REFRESH FOREIGN TABLE hms_fed_catalog.schema.table RESOLVE DBFS LOCATION;
```

### REFRESH FULL

```sql
-- Streaming Table vollständig neu verarbeiten (Truncate + Neuaufbau)
REFRESH STREAMING TABLE cat.db.st_name FULL;
```

---

## 17. External Metadata

**Einfach erklärt:** Ein External-Metadata-Objekt definiert benutzerdefinierte Data-Lineage-Beziehungen für Systeme, die außerhalb der nativen Lineage-Nachverfolgung von Unity Catalog laufen — nützlich, um Lineage auch für externe Tools/Pipelines sichtbar zu machen. `CREATE EXTERNAL METADATA` wird auf Metastore-Ebene vergeben; `MODIFY` auf dem Objekt (plus Rechte auf allen referenzierten UC-Objekten) wird benötigt, um Lineage-Beziehungen zu ändern.

Keine Code-Beispiele in dieser Datei.

---

## 18. Service Credential

**Einfach erklärt:** Ein Service Credential speichert Authentifizierungsinformationen für den Zugriff auf externe **Cloud-Dienste** — im Unterschied zum Storage Credential, das Cloud-**Speicher** regelt. `ACCESS` erlaubt die Nutzung des Credentials für einen externen Dienst; `CREATE CONNECTION` (kombiniert mit `CREATE CONNECTION` auf dem Metastore) erlaubt, mit diesem Credential eine Connection zu einer externen Datenbank anzulegen.

### ALTER SERVICE CREDENTIAL

```sql
-- Service Credential umbenennen
ALTER SERVICE CREDENTIAL street_cred RENAME TO good_cred;

-- Eigentümer ändern
ALTER SERVICE CREDENTIAL street_cred OWNER TO `alf@melmak.et`;
```

### DROP SERVICE CREDENTIAL

```sql
DROP SERVICE CREDENTIAL secrets;

-- Ohne Fehler, falls das Credential nicht existiert
DROP SERVICE CREDENTIAL IF EXISTS secrets;
```

### DESCRIBE SERVICE CREDENTIAL

```sql
DESCRIBE SERVICE CREDENTIAL secrets;
```

### SHOW SERVICE CREDENTIALS

```sql
SHOW SERVICE CREDENTIALS;
```

---

## 19. Connection

**Einfach erklärt:** Eine Connection speichert Endpunkt und Zugangsdaten für ein externes System und unterstützt Query Federation, Catalog Federation, Managed Ingestion, JDBC-Zugriff und HTTP-Dienste. `CREATE CONNECTION` wird auf Metastore-Ebene vergeben (zusätzlich auf dem Service Credential, falls genutzt); `USE CONNECTION` erlaubt Einsicht und Nutzung.

### CREATE CONNECTION

```sql
-- PostgreSQL-Connection mit Secrets statt Klartext-Zugangsdaten
CREATE CONNECTION postgresql_connection
TYPE POSTGRESQL
OPTIONS (
  host '<hostname>',
  port '5432',
  user secret('secrets.r.us', 'postgresUser'),
  password secret('secrets.r.us', 'postgresPassword')
);

-- HTTP-Connection (z. B. für einen externen REST-Dienst)
CREATE CONNECTION slack_conn
TYPE HTTP
OPTIONS (
  host 'https://slack.com',
  port '443',
  base_path '/api/',
  bearer_token secret('secrets.r.us', 'slackBearerToken')
);
```

Unterstützte `TYPE`-Werte u. a. `DATABRICKS`, `HTTP`, `MYSQL`, `POSTGRESQL`, `REDSHIFT`, `SNOWFLAKE`, `SQLDW`, `SQLSERVER`. Sensible Optionswerte sollten stets über die `secret()`-Funktion statt im Klartext referenziert werden.

### ALTER CONNECTION

```sql
ALTER CONNECTION mysql_connection SET OWNER TO `alf@melmak.et`;
ALTER CONNECTION mysql_connection RENAME TO `other_mysql_connection`;
ALTER CONNECTION mysql_connection OPTIONS (host 'newmysqlhost.us-west-2.amazonaws.com', port '3306');
```

### DROP CONNECTION

```sql
DROP CONNECTION IF EXISTS mysql_connection;
```

### DESCRIBE CONNECTION / SHOW CONNECTIONS

```sql
DESCRIBE CONNECTION postgresql_connection;

SHOW CONNECTIONS;
```

---

## 20. Share

**Einfach erklärt:** Ein Share ist eine logische Gruppierung von Daten-Assets (Tabellen, Views, Volumes) im Rahmen von **OpenSharing** (der aktuelle Name für Databricks' Delta-Sharing-basiertes Sharing-Modell), die ein Provider externen Recipients zur Verfügung stellt. `SELECT` auf einem Share wird an einen **Recipient** vergeben (nicht an einzelne Nutzer). `CREATE SHARE` wird auf Metastore-Ebene vergeben.

### CREATE SHARE

```sql
CREATE SHARE IF NOT EXISTS customer_share COMMENT 'This is customer share';
```

### ALTER SHARE

```sql
ALTER SHARE some_share
  ADD TABLE my_schema.my_tab
    COMMENT 'some comment'
    PARTITION(c1_int = 5, c2_date LIKE '2021%')
    AS shared_schema.shared_tab;

ALTER SHARE share ADD TABLE table1 WITH HISTORY;
ALTER SHARE share ADD TABLE table2 WITHOUT HISTORY;

ALTER SHARE some_share RENAME TO new_share;
ALTER SHARE some_share OWNER TO `alf@melmak.et`;
```

### DROP SHARE

```sql
DROP SHARE IF EXISTS vaccine;
```

### SHOW SHARES / SHOW SHARES IN PROVIDER

```sql
SHOW SHARES;
SHOW SHARES LIKE 'vaccine';
SHOW SHARES IN PROVIDER some_provider;
```

### SHOW ALL IN SHARE

```sql
CREATE SHARE IF NOT EXISTS customer_share COMMENT 'This is customer share';
ALTER SHARE customer_share ADD TABLE my_schema.tab1 AS their_schema.tab1;
ALTER SHARE customer_share ADD TABLE other_schema.tab2 PARTITION (c1 = 5), (c1 = 7);
SHOW ALL IN SHARE customer_share;
```

### GRANT / REVOKE / SHOW GRANTS ON SHARE

```sql
GRANT SELECT ON SHARE vaccines TO RECIPIENT jab_me_now_corp;
REVOKE SELECT ON SHARE vaccines FROM RECIPIENT jab_me_now_corp;
SHOW GRANTS ON SHARE shared_date;
```

### Gesamtablauf (OpenSharing)

```sql
ALTER PROVIDER `Center for Disease Control` RENAME TO cdc;
SHOW SHARES IN PROVIDER cdc;
CREATE CATALOG cdcdata USING SHARE cdc.vaccinedata;
```

---

## 21. Provider

**Einfach erklärt:** Ein Provider repräsentiert eine externe Organisation, die Daten mit der eigenen Organisation teilt — angelegt im Metastore des **Recipients**. `USE PROVIDER` erlaubt, alle Provider und ihre Shares einzusehen und (kombiniert mit `CREATE CATALOG`) einen geteilten Katalog einzubinden, ohne Metastore-Admin zu sein. `CREATE PROVIDER` wird auf Metastore-Ebene vergeben.

### ALTER PROVIDER

```sql
ALTER PROVIDER `Center for Disease Control` RENAME TO cdc;
ALTER PROVIDER cdc OWNER TO `alf@melmak.et`;
```

### DROP PROVIDER

```sql
DROP PROVIDER IF EXISTS other_corp;
```

### DESCRIBE PROVIDER

```sql
DESCRIBE PROVIDER other_org;
```

### SHOW PROVIDERS

```sql
SHOW PROVIDERS;
SHOW PROVIDERS LIKE 'other_org';
```

---

## 22. Recipient

**Einfach erklärt:** Ein Recipient repräsentiert eine externe Organisation/Nutzergruppe, mit der ein Provider Daten teilt — angelegt im Metastore des **Providers**. Auf dem Recipient-Objekt selbst lassen sich keine Rechte vergeben; der Zugriff läuft über `SELECT` auf einem Share, das dem Recipient gewährt wird. `CREATE RECIPIENT` wird auf Metastore-Ebene vergeben.

### CREATE RECIPIENT

```sql
CREATE RECIPIENT other_databricks_org
USING ID 'azure:westus:f12dcb34-5678-9d4c-1234-c5ac67f8b90a';

CREATE RECIPIENT recipient_name
COMMENT 'description'
PROPERTIES (property_key = 'property_value');
```

### ALTER RECIPIENT

```sql
ALTER RECIPIENT `Center for Disease Control` RENAME TO cdc;
ALTER RECIPIENT cdc OWNER TO `alf@melmak.et`;
ALTER RECIPIENT cdc SET PROPERTIES ( 'country' = 'US' );
```

### DROP RECIPIENT

```sql
CREATE RECIPIENT other_corp COMMENT 'OtherCorp.com';
DESCRIBE RECIPIENT other_corp;
DROP RECIPIENT other_corp;
```

### DESCRIBE RECIPIENT / SHOW RECIPIENTS

```sql
CREATE RECIPIENT other_org;
DESCRIBE RECIPIENT other_org;

SHOW RECIPIENTS;
SHOW RECIPIENTS LIKE 'other_org';
```

### SET RECIPIENT

```sql
CREATE RECIPIENT nasdaq PROPERTIES ('country' = 'US');
CREATE VIEW my_view AS
  SELECT * FROM my_table
  WHERE country = CURRENT_RECIPIENT('country');
SET RECIPIENT nasdaq;
SELECT * FROM my_view;
```

### SHOW GRANTS TO RECIPIENT

```sql
SHOW GRANTS TO RECIPIENT a_corp;
```

---

## 23. Clean Room

**Einfach erklärt:** Ein Clean Room bietet eine sichere Umgebung, um mit anderen Organisationen an gemeinsamen Daten zu arbeiten, **ohne** dass eine Partei ihre zugrunde liegenden Rohdaten offenlegt (z. B. für gemeinsame Analysen, ohne Kundendaten auszutauschen). `CREATE CLEAN ROOM` wird auf Metastore-Ebene vergeben. `EXECUTE CLEAN ROOM TASK` erlaubt Notebook-Ausführung und Detaileinsicht; `MODIFY CLEAN ROOM` erlaubt Aktualisierung (Daten-Assets, Notebooks, Kommentare hinzufügen/entfernen).

Keine Code-Beispiele in dieser Datei.

---

## 24. Tags

**Einfach erklärt:** Tags sind Schlüssel-Wert-Paare (oder reine Schlüssel), die auf Unity-Catalog-Objekten angebracht werden, um sie zu klassifizieren, auffindbar zu machen und in Policies (v. a. ABAC) zu referenzieren. Unterstützte Objekte: Catalogs, Schemas, Tabellen, Tabellenspalten, Volumes, Views, Functions, registrierte Modelle/-versionen, External-Metadata-Objekte (Preview), plus Dashboards, Genie-Agenten, Apps, Notebooks.

**Wichtige Regeln:** Groß-/Kleinschreibung wird unterschieden; max. 256 Zeichen je Schlüssel/Wert; verbotene Zeichen im Schlüssel: `. , - = / :`; keine führenden/nachgestellten Leerzeichen; max. 50 Tags pro Objekt, max. 1.000 Spalten-Tags pro Tabelle; Spalten-Tagging erfordert einen `ALTER TABLE`-Befehl **je Spalte** (kein Batch).

**Governed Tags vs. System Tags:** Governed Tags werden account-weit über Regeln durchgesetzt (Schloss-Symbol in der UI, `ASSIGN`-Berechtigung nötig, nur erlaubte Policy-Werte). System Tags sind eine von Databricks vordefinierte Unterkategorie davon (Schraubenschlüssel-Symbol, unveränderliche Definition). In ABAC-Policies kaskadieren Tags implizit an Kindobjekte — **außer** auf Spaltenebene.

**Sicherheitshinweis:** Tag-Daten liegen als Klartext vor und können global repliziert werden — **keine** PII/sensiblen Werte in Tag-Namen, -Werten oder -Beschreibungen speichern.

### SET TAG / UNSET TAG (Runtime 16.1+, bevorzugter Ansatz)

```sql
SET TAG ON CATALOG catalog `cost_center` = `hr`;
UNSET TAG ON CATALOG catalog cost_center;
```

### Spalten-Tags (Runtime 13.3+, Alternative)

```sql
ALTER TABLE schema.table ALTER COLUMN column_name SET TAGS ('key' = 'value');
```

### Tags über Information-Schema abfragen

```sql
SELECT catalog_name, schema_name, table_name, tag_name, tag_value
FROM information_schema.column_tags
WHERE tag_name = 'pii' AND schema_name = 'default';
```

---

## 25. Unity Catalog Compute: Zugriffsmodi, Fine-Grained Access Control und Lakeguard

**Einfach erklärt:** Unity Catalog regelt nicht nur Daten-Objekte, sondern auch, **wie Compute (Cluster) auf diese Objekte zugreifen darf**. Kernbaustein ist **Unity Catalog Lakeguard** — die von Databricks als „industry-first and only data governance multi-user Apache Spark" beschriebene Technologie, die Governance und Isolation sowohl auf Standard- als auch auf Dedicated Clusters durchsetzt (nicht nur auf Serverless-Compute).

**Cluster-Zugriffsmodus — Auto Mode (GA).** Beim Anlegen eines Clusters muss nicht mehr manuell zwischen Zugriffsmodi wie *Standard* (Shared) und *Dedicated* (Single User) gewählt werden: **Auto Mode** wählt den empfohlenen Zugriffsmodus automatisch anhand der Cluster-Konfiguration und vereinfacht so die UI um Best-Practice-Vorgaben. Verfügbar auf AWS, Azure und GCP.

**Fine-Grained Access Control (FGAC) auf Dedicated Clusters (GA ab Databricks Runtime 15.4).** Dedicated Clusters sind „Single-Identity"-Cluster (fest einem Nutzer oder einer Gruppe zugeordnet). Vorher konnten dort Row Filter/Column Masks und andere fein-granulare Schutzmechanismen nicht durchgesetzt werden — seit DBR 15.4 unterstützen Dedicated Clusters lesend:

- Row-Level-Security (Row Filter) und Column Masking
- Views, Dynamic Views, Materialized Views, Streaming Tables

`MERGE INTO` (Schreibzugriff auf FGAC-geschützte Daten) befindet sich in **Private Preview**. Technischer Hintergrund: Da Spark beim Verarbeiten von FGAC-geschützten Abfragen mehr Daten liest als nötig („overfetching"), werden solche Abfragen transparent auf **serverlosem Hintergrund-Compute** verarbeitet und nach der Serverless-Jobs-Rate abgerechnet — auch wenn der Cluster selbst kein Serverless-Cluster ist. Gruppen-Sharing von Dedicated Clusters ist ebenfalls GA (ab DBR 15.4); Audit-Logs erfassen dabei `identity_metadata` mit `run_as`/`run_by`-Feldern.

**Unity Catalog Service Credentials (GA auf AWS, Azure, GCP).** Ergänzt die Beschreibung in Abschnitt 18: Service Credentials lassen sich über UI, API oder Terraform verwalten (Catalog Explorer → External Data → Credentials) und werden von Standard- und Dedicated-Clustern, SQL-Warehouses, Delta Live Tables sowie Serverless-Compute unterstützt. Databricks nennt als Ziel, dass Service Credentials **Instance-Profile pro Compute-Ressource überflüssig machen** — Authentifizierung gegenüber externen Cloud-Diensten wird stattdessen zentral über Unity Catalog vergeben und verwaltet.

**Roadmap (zum Zeitpunkt des Blogposts angekündigt, noch nicht GA):** Single-Node-Konfiguration für Standard Clusters, SparkML auf Standard Clusters (Private Preview), UC-Python-UDFs mit Custom Dependencies und Vectorized Processing, Cluster-Log-Delivery zu UC Volumes (Public Preview), unbegrenzter Datei-Upload/Download für UC Volumes über das Python SDK (Private Preview).

Keine Code-Beispiele in dieser Datei.

---

## 26. Packaged Clean Rooms, Marketplace Apps und On-Behalf-Of-Authentifizierung

**Einfach erklärt:** Ergänzt die knappe Beschreibung in Abschnitt 23 (Clean Room) um ein konkretes Produktionsbeispiel (Stagwell), das zeigt, wie **Databricks Packaged Clean Rooms** zusammen mit **Marketplace Apps** und **Delta Sharing** ein Self-Service-Identity-Matching-Produkt ermöglichen, ohne dass Rohdaten zwischen den Parteien ausgetauscht werden.

**Databricks Packaged Clean Rooms.** Ein vorkonfiguriertes Clean-Room-Muster, das den sonst nötigen manuellen Freigabeschritt für Marketplace-Distributionen eliminiert: Eine Marke („Brand") kann das Matching-Notebook **sofort ausführen**, statt auf eine manuelle Genehmigung zu warten. Beide Parteien sehen die Ergebnisse anschließend über **Delta Sharing**; die zugrunde liegenden Rohdaten bleiben durch Plattform-Enforcement gegenseitig verborgen. Im Matching-Workflow selbst laufen Joins zwischen Marken-Daten und einer ID-Spine, Identity Resolution über mehrere Identifikatoren sowie die Berechnung von Match-Raten, Coverage-Metriken und Household-/Consumer-IDs.

**Marketplace Apps.** Werden direkt im Workspace des Kunden installiert; Databricks provisioniert dafür automatisch einen **Service Principal** samt Umgebungsvariablen. Der App-Code selbst bleibt für Konsumenten undurchsichtig (Schutz der Anbieter-IP), die Authentifizierung läuft über einen OAuth-Flow. Laut Artikel verkürzt sich die Deployment-Zeit für ein solches Produkt dadurch von Monaten auf Minuten.

**On-Behalf-Of-Authentifizierung (OBO) — vier Identitäts-Layer.** Ein Clean-Room-/Marketplace-App-Produkt wie das von Stagwell kombiniert vier unterschiedliche Identitäten:

1. **OBO User Token** — per `x-forwarded-access-token`-Header für den eigentlichen Datenzugriff im Namen des einloggten Nutzers.
2. **App Service Principal** — für App-Level-Operationen und Telemetrie.
3. **Backend Service Principal** — Machine-to-Machine-OAuth für den Lifecycle des Clean Rooms (Anlegen, Verwalten).
4. **Brand User PAT** — ein gescopter Personal Access Token mit Clean-Room-/SQL-/Unity-Catalog-Rechten.

Unity-Catalog-ACLs werden dabei automatisch anhand der jeweiligen Nutzeridentität angewendet; Zeilenfilter und Spaltenmasken werden im Clean Room ebenfalls automatisch durchgesetzt, Governance und Zugriffskontrolle erfolgen konsequent auf Nutzerebene statt nur auf App-Ebene.

Keine Code-Beispiele in dieser Datei.

---

## 27. Verifikationsprotokoll (Databricks-Blog-Abgleich)

Abgleich der in diesem Ordner dokumentierten Themen gegen aktuelle **Databricks-Blog-Artikel** (`databricks.com/blog`, teils ergänzt durch `community.databricks.com`), durchgeführt am 2026-09-24:

| Thema (Abschnitt) | Blog-Quelle | Ergebnis |
|---|---|---|
| Metric View (8) | [What's new with Unity Catalog at Data + AI Summit 2026](https://www.databricks.com/blog/whats-new-unity-catalog-data-ai-summit-2026) | ✅ Bestätigt und ergänzt: Metric Views sind laut Blog **GA seit April 2026**, werden nach Apache Spark **open-sourced**, und wurden am DAIS 2026 um Multi-Fact-Relationships, Level-of-Detail-Berechnungen, parametrisierte Metriken, eine **Materialization**-Funktion (Public Preview, für schnellere Dashboard-/Agent-Queries) sowie Power-BI-/Tableau-Import (Beta) erweitert — Details, die die Originaldatei (reiner Konzeptüberblick ohne Versionsangaben) nicht enthält. Ergänzungswürdig in [07 Metric View.md](../02%20Unity%20Catalog/07%20Metric%20View.md). |
| Service / MCP Service (12) | [Announcing managed MCP servers with Unity Catalog and Databricks Integration](https://www.databricks.com/blog/announcing-managed-mcp-servers-unity-catalog-and-mosaic-ai-integration); [Unity Gateway: How to connect agents to external MCPs securely](https://www.databricks.com/blog/ai-gateway-how-connect-agents-external-mcps-securely); [Stop rogue AI: How Unity Catalog secures your agent actions](https://www.databricks.com/blog/stop-rogue-ai-how-unity-catalog-secures-your-agent-actions) | ✅ Bestätigt: MCP Services werden über **Unity Gateway** (Control Plane für KI-Traffic) aufgerufen, sind als `catalog.schema.mcp_service` adressierbar und governt mit Grants, Tool-Auswahl, Service-Policies sowie Audit-/Usage-Logging — deckt sich mit der knappen Beschreibung in der Originaldatei. Ergänzend laut DAIS-2026-Blog: **Unity Gateway erweitert Governance jetzt auch auf Modelle, Agenten und Skills** mit kontextuellen Service-Policies (Beta) — in der Originaldatei noch nicht enthalten. |
| Governed Tags (24) | [Enforce consistent, secure tagging across data and AI assets with Governed Tags in Unity Catalog](https://www.databricks.com/blog/enforce-consistent-secure-tagging-across-data-and-ai-assets-governed-tags-unity-catalog-public); [ABAC row filtering and column masking policies, governed tags, and data classification are now generally available](https://www.databricks.com/blog/abac-row-filtering-and-column-masking-policies-governed-tags-and-data-classification-are-now) | ✅ Bestätigt: Governed Tags, ABAC-Policies und automatisierte Data Classification sind inzwischen **GA** (ursprünglicher Blogpost vom 23.09.2025 kündigte Public Preview an). Neu laut DAIS-2026-Blog: **Tag-Propagation** (Private Preview) trägt Governed Tags automatisch von Quelltabellen/-spalten an nachgelagerte Tabellen/Views weiter — Ergänzung zum in der Originaldatei beschriebenen Vererbungsverhalten (dort nur Catalog→Schema→Tabelle, nicht spaltenübergreifend zwischen Tabellen). |
| Clean Room (23) | [Databricks Clean Rooms: Now Generally Available on AWS and Azure](https://www.databricks.com/blog/databricks-clean-rooms-now-generally-available-aws-and-azure); [What's New with Data Sharing and Collaboration – Summer 2025](https://www.databricks.com/blog/whats-new-data-sharing-and-collaboration-summer-2025) | ✅ Bestätigt und ergänzt: Clean Rooms sind seit Februar 2025 **GA** (AWS/Azure), inkl. Federated Sharing über Clouds, HIPAA-Support, Management-APIs und Self-Collaboration innerhalb eines Metastores. Seit Sommer 2025 zusätzlich: **Secure Self-Runs** (Mitwirkende können eigene Notebooks mit expliziter Freigabe anderer Teilnehmer hochladen/ausführen), privacy-zentrierte Identity Resolution, Multi-Party-Kollaboration. Die Originaldatei nennt keine dieser Fähigkeiten oder den GA-Status. |
| Share / Provider / Recipient (20–22) | [Introducing OpenSharing: the Next Evolution of Delta Sharing for the Agentic Era](https://www.databricks.com/blog/introducing-opensharing-next-evolution-delta-sharing-agentic-era) | ✅ Bestätigt: Die Terminologie „OpenSharing", die die Originaldateien bereits durchgängig verwenden, stammt aus der Ankündigung vom 10.06.2026 — OpenSharing ist die Weiterentwicklung von Delta Sharing, seither ein **Linux-Foundation-Projekt**, erstes offenes Protokoll für Agent-Skills, KI-Modelle und unstrukturierte Daten, mit Iceberg-REST-Client-Unterstützung und neuen On-Premises-Speicherpartnern (MinIO GA; Everpure, Qumulo, VAST Data in Preview). Diese Hintergrundinformation (warum „OpenSharing" statt „Delta Sharing") fehlt in den Originaldateien komplett. |
| Catalog / Schema / Table (3–5) | [What's new with Unity Catalog at Data + AI Summit 2026](https://www.databricks.com/blog/whats-new-unity-catalog-data-ai-summit-2026) | ⚠️ **Ergänzung nötig:** Laut DAIS-2026-Blog gibt es inzwischen einen **vierstufigen Namespace** (`metastore.catalog.schema.table`) für Cross-Cloud-/Cross-Region-Governance über mehrere Accounts hinweg — die Originaldateien beschreiben durchgängig nur den (weiterhin gültigen) **dreistufigen** Namespace `catalog.schema.table`. Kein Fehler, aber eine relevante Erweiterung, die in [02 Catalog.md](../02%20Unity%20Catalog/02%20Catalog.md) ergänzt werden sollte. Zusätzlich: External-Engine-Zugriff (Spark, Flink) auf Managed-Delta-Tabellen ist jetzt Public Preview. |
| Volume (9) | [What's new with Unity Catalog at Data + AI Summit 2026](https://www.databricks.com/blog/whats-new-unity-catalog-data-ai-summit-2026) | ⚠️ **Ergänzung:** Ein neuer **FILE-Volume-Typ** (Beta) governt unstrukturierte Daten (PDFs, Bilder, Audio, Video) direkt innerhalb von Managed-Delta-/Iceberg-Tabellen — über die klassischen Managed/External-Volumes aus der Originaldatei hinaus. |

**Gesamtfazit:** Alle in den Originaldateien beschriebenen Kernkonzepte (Objekthierarchie, Privilegienmodell, DDL-Syntax) sind weiterhin aktuell und wurden durch keinen Blog-Artikel widerlegt. Die Blog-Recherche deckt jedoch durchgängig auf, dass die Referenzdateien den **funktionalen Ist-Zustand zum Erstellungszeitpunkt** abbilden, während mehrere Bereiche (Metric Views, MCP/Unity Gateway, Governed Tags, Clean Rooms, OpenSharing, Catalog-Namespace, Volumes) seit den jüngsten Data + AI Summit 2026- und 2025-Ankündigungen um GA-Status, neue Preview-Features oder Hintergrundkontext erweitert wurden. Empfehlung: die oben markierten ⚠️-Punkte bei nächster Gelegenheit in die jeweiligen Originaldateien einpflegen.
