# 02 Tables — Gesamtzusammenfassung

Konsolidierte Übersicht aller 24 Inhaltsdateien dieses Ordners (inkl. Unterordner `07 Table Features/` und `10 Tabellenoperationen/`) mit **allen** enthaltenen Code-Beispielen. Dieses Dokument dient als kompakter Überblick plus vollständige Code-Referenz an einem Ort.

Zwei Abschnitte (11–12) behandeln Auto Loader Schema-Modi/JSON-Pfadsyntax sowie das Lesen von Unity-Catalog-Tabellen in Snowflake.

## Inhalt

1. [Tabellenkonzepte und Tabellentypen](#1-tabellenkonzepte-und-tabellentypen)
2. [Delta Lake Grundlagen](#2-delta-lake-grundlagen)
3. [Managed Tables](#3-managed-tables)
4. [External, Foreign und Temporary Tables](#4-external-foreign-und-temporary-tables)
5. [Apache Iceberg](#5-apache-iceberg)
6. [Schema und Tabellenhistorie](#6-schema-und-tabellenhistorie)
7. [Table Features](#7-table-features)
8. [Transactions](#8-transactions)
9. [Tabellenlayout und Performance](#9-tabellenlayout-und-performance)
10. [Tabellenoperationen](#10-tabellenoperationen)
11. [Auto Loader Schema-Modi und JSON-Pfadsyntax für semi-strukturierte Daten](#11-auto-loader-schema-modi-und-json-pfadsyntax-für-semi-strukturierte-daten)
12. [Unity Catalog Tables in Snowflake lesen (UniForm + Iceberg REST Catalog)](#12-unity-catalog-tables-in-snowflake-lesen-uniform--iceberg-rest-catalog)

---

## 1. Tabellenkonzepte und Tabellentypen

Databricks-Tabellen folgen der dreistufigen Namensraum-Hierarchie `catalog.schema.table`, verwaltet über Unity Catalog. Zwei Speicherformate: **Delta Lake** (Standard) und **Apache Iceberg**. Vier Haupttabellentypen — **Managed** (Unity Catalog verwaltet alles, empfohlener Standard), **External** (eigener Storage, nur Metadaten-Governance), **Foreign** (externes System verwaltet, nur lesend), **Temporary** (sitzungsgebunden) — plus spezialisierte Typen (Streaming Tables, Materialized Views).

**Vergleichsmatrix:**

| Feature | Managed | External | Foreign |
|---|---|---|---|
| Datenlebenszyklus | Unity Catalog verwaltet | selbst verwaltet | externes System verwaltet |
| Automatische Optimierungen | ja | eingeschränkt | nein |
| Formate | Delta Lake, Apache Iceberg | Delta Lake, CSV, JSON, AVRO, PARQUET, ORC, TEXT | abhängig vom externen System |
| Daten beim DROP gelöscht | ja | nein | nein |

Zugriff erfordert Berechtigungen: `SELECT`, `MODIFY`, `MANAGE`, `CREATE TABLE`, `USE CATALOG`, `USE SCHEMA`.

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick. (Enthält eine Vertiefung zu Delta Lake vs. Apache Iceberg; siehe Originaldatei für Details.)

---

## 2. Delta Lake Grundlagen

Delta Lake ist das **Standardformat** für praktisch alle Databricks-Tabellen: ACID-Transaktionen, skalierbares Metadaten-Handling, volle Spark-/Structured-Streaming-Kompatibilität, Time Travel, Schema Enforcement/Evolution. Das Transaktionslog folgt einem offenen Protokoll.

### Tabelle erstellen

```python
from pyspark.sql.types import StructType, StructField, IntegerType, StringType

schema = StructType([
  StructField("id", IntegerType(), True),
  StructField("firstName", StringType(), True),
  StructField("lastName", StringType(), True),
  StructField("gender", StringType(), True),
  StructField("age", IntegerType(), True)
])

df = spark.read.format("csv").option("header", True).schema(schema).load("/Volumes/workspace/default/my-volume/person_10000.csv")

df.writeTo("workspace.default.people_10k").createOrReplace()

df = spark.read.table("workspace.default.people_10k")
display(df)
```

```sql
CREATE OR REPLACE TABLE workspace.default.people_10k AS
SELECT
  person_id AS id,
  firstname,
  lastname,
  gender,
  age
FROM read_files(
  '/Volumes/workspace/default/my-volume/person_10000.csv',
  format => 'csv',
  header => true);

SELECT * FROM workspace.default.people_10k;
```

```sql
-- CREATE TABLE LIKE (Runtime 13.3 LTS+) — kopiert Schema/Eigenschaften ohne Daten
CREATE TABLE workspace.default.people_10k_prod LIKE workspace.default.people_10k;
```

```python
from delta.tables import DeltaTable

(DeltaTable.createIfNotExists(spark)
  .tableName("workspace.default.people_10k_2")
  .addColumn("id", "INT")
  .addColumn("firstName", "STRING")
  .addColumn("lastName", "STRING", comment="surname")
  .addColumn("gender", "STRING")
  .addColumn("age", "INT")
  .execute())

display(spark.read.table("workspace.default.people_10k_2"))
```

### MERGE / UPSERT

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from delta.tables import DeltaTable

schema = StructType([
  StructField("id", IntegerType(), True),
  StructField("firstName", StringType(), True),
  StructField("lastName", StringType(), True),
  StructField("gender", StringType(), True),
  StructField("age", IntegerType(), True)
])

data = [
  (10001, 'Billy', 'Luppitt', 'M', 55),
  (10002, 'Mary', 'Smith', 'F', 98),
  (10003, 'Elias', 'Leadbetter', 'M', 48),
  (10004, 'Jane', 'Doe', 'F', 30),
  (10005, 'Joshua', '', 'M', 90),
  (10006, 'Ginger', '', 'F', 16),
]

people_10k_updates = spark.createDataFrame(data, schema)
people_10k_updates.createOrReplaceTempView("people_10k_updates")

deltaTable = DeltaTable.forName(spark, 'workspace.default.people_10k')

(deltaTable.alias("people_10k")
  .merge(
    people_10k_updates.alias("people_10k_updates"),
    "people_10k.id = people_10k_updates.id")
  .whenMatchedUpdateAll()
  .whenNotMatchedInsertAll()
  .execute())

df = spark.read.table("workspace.default.people_10k")
df_filtered = df.filter(df["id"] >= 10001)
display(df_filtered)
```

```sql
CREATE OR REPLACE TABLE workspace.default.people_10k_updates(
  id INT,
  firstName STRING,
  lastName STRING,
  gender STRING,
  age INT
);

INSERT INTO workspace.default.people_10k_updates VALUES
  (10001, "Billy", "Luppitt", "M", 55),
  (10002, "Mary", "Smith", "F", 98),
  (10003, "Elias", "Leadbetter", "M", 48),
  (10004, "Jane", "Doe", "F", 30),
  (10005, "Joshua", "", "M", 90),
  (10006, "Ginger", "", "F", 16);

MERGE INTO workspace.default.people_10k AS people_10k
USING workspace.default.people_10k_updates AS people_10k_updates
ON people_10k.id = people_10k_updates.id
WHEN MATCHED THEN
  UPDATE SET *
WHEN NOT MATCHED THEN
  INSERT *;

SELECT * FROM workspace.default.people_10k WHERE id >= 10001;
```

### Lesen

```python
people_df = spark.read.table("workspace.default.people_10k")
display(people_df)
```

```sql
SELECT * FROM workspace.default.people_10k;
```

### Schreiben: Append und Overwrite

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
  StructField("id", IntegerType(), True),
  StructField("firstName", StringType(), True),
  StructField("lastName", StringType(), True),
  StructField("gender", StringType(), True),
  StructField("age", IntegerType(), True)
])

data = [(10007, 'Miku', 'Hatsune', 'F', 25)]
df = spark.createDataFrame(data, schema)

df.write.mode("append").saveAsTable("workspace.default.people_10k")

df = spark.read.table("workspace.default.people_10k")
df_filtered = df.filter(df["id"] == 10007)
display(df_filtered)
```

```sql
CREATE OR REPLACE TABLE workspace.default.people_10k_new (
  id INT, firstName STRING, lastName STRING, gender STRING, age INT
);

INSERT INTO workspace.default.people_10k_new VALUES
  (10007, 'Miku', 'Hatsune', 'F', 25);

INSERT INTO workspace.default.people_10k
SELECT * FROM workspace.default.people_10k_new;

SELECT * FROM workspace.default.people_10k WHERE id = 10007;
```

```python
df.write.mode("overwrite").saveAsTable("workspace.default.people_10k")
```

```sql
INSERT OVERWRITE TABLE workspace.default.people_10k
SELECT * FROM workspace.default.people_10k_2;
```

### UPDATE

```python
from delta.tables import *
from pyspark.sql.functions import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")

deltaTable.update(
  condition = "gender = 'Female'",
  set = { "gender": "'F'" }
)

deltaTable.update(
  condition = col('gender') == 'Male',
  set = { 'gender': lit('M') }
)

deltaTable.update(
  condition = col('gender') == 'Other',
  set = { 'gender': lit('O') }
)

df = spark.read.table("workspace.default.people_10k")
display(df)
```

```sql
UPDATE workspace.default.people_10k SET gender = 'F' WHERE gender = 'Female';
UPDATE workspace.default.people_10k SET gender = 'M' WHERE gender = 'Male';
UPDATE workspace.default.people_10k SET gender = 'O' WHERE gender = 'Other';

SELECT * FROM workspace.default.people_10k;
```

### DELETE

```python
from delta.tables import *
from pyspark.sql.functions import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")

deltaTable.delete("age < '18'")
deltaTable.delete(col('age') < '21')

df = spark.read.table("workspace.default.people_10k")
display(df)
```

```sql
DELETE FROM workspace.default.people_10k WHERE age < '21';

SELECT * FROM workspace.default.people_10k;
```

### DESCRIBE HISTORY

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")
display(deltaTable.history())
```

```sql
DESCRIBE HISTORY workspace.default.people_10k;
```

### Time Travel

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")
deltaHistory = deltaTable.history()

display(deltaHistory.where("version == 0"))
display(deltaHistory.where("timestamp == '2026-01-05T23:09:47.000+00:00'"))
```

```sql
SELECT * FROM workspace.default.people_10k VERSION AS OF 0;

SELECT * FROM workspace.default.people_10k TIMESTAMP AS OF '2026-01-05T23:09:47.000+00:00';
```

```python
df = spark.read.option('versionAsOf', 0).table("workspace.default.people_10k")

df = spark.read.option('timestampAsOf', '2026-01-05T23:09:47.000+00:00').table("workspace.default.people_10k")
display(df)
```

```sql
CREATE OR REPLACE TEMPORARY VIEW people_10k_v0 AS
SELECT * FROM workspace.default.people_10k VERSION AS OF 0;

CREATE OR REPLACE TEMPORARY VIEW people_10k_t0 AS
SELECT * FROM workspace.default.people_10k TIMESTAMP AS OF '2026-01-05T23:09:47.000+00:00';

SELECT * FROM people_10k_v0;
SELECT * FROM people_10k_t0;
```

### OPTIMIZE, Liquid Clustering und VACUUM

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")
# executeCompaction() ist der `OPTIMIZE`-Befehl in Python
deltaTable.optimize().executeCompaction()
```

```sql
OPTIMIZE workspace.default.people_10k;
```

```python
spark.sql("ALTER TABLE workspace.default.people_10k CLUSTER BY (firstName)")
spark.sql("OPTIMIZE workspace.default.people_10k FULL")
```

```sql
ALTER TABLE workspace.default.people_10k CLUSTER BY (firstName);
OPTIMIZE workspace.default.people_10k FULL;
```

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")
deltaTable.vacuum()
```

```sql
VACUUM workspace.default.people_10k;
```

### Einschränkungen auf S3

- **Bucket-Versionierung:** Konflikte mit Delta Lakes eigenem Versioning/Garbage Collection. Falls nötig: max. 3 Versionen per Lifecycle-Policy, Retention ≤ 7 Tage.
- **Multi-Cluster-Writes:** funktionieren nur innerhalb eines Workspace, nicht über Workspaces hinweg. `spark.databricks.delta.multiClusterWrites.enabled` deaktiviert Multi-Cluster-Writes (Risiko: Datenverlust/-korruption bei gleichzeitigem Zugriff mehrerer Cluster).
- **Nie `rm -rf`** zum Löschen von Delta-Tabellen nutzen — stattdessen `DROP TABLE`.

### CONVERT TO DELTA

```sql
-- Registrierte Parquet-Tabelle konvertieren
CONVERT TO DELTA database_name.table_name;

-- Partitioniertes Parquet-Verzeichnis konvertieren (Partitionsschema explizit angeben)
CONVERT TO DELTA parquet.`s3://my-bucket/path/to/table` PARTITIONED BY (date DATE);

-- Iceberg-Tabelle konvertieren (nutzt Iceberg-Manifest für Metadaten)
CONVERT TO DELTA iceberg.`s3://my-bucket/path/to/table`;
```

---

## 3. Managed Tables

Der empfohlene Standardtabellentyp — Unity Catalog übernimmt Storage, Optimierung und Lebenszyklus vollständig, für Delta Lake und Apache Iceberg. Gelöschte Managed Tables bleiben standardmäßig **7 Tage** über `UNDROP TABLE` wiederherstellbar (konfigurierbar 0 Std. bis 30 Tage auf Catalog-/Schema-Ebene).

```sql
-- Recovery-Frist auf Catalog-Ebene konfigurieren
ALTER CATALOG my_catalog RETAIN DROPPED TO 30 DAYS;

-- Recovery-Frist auf Schema-Ebene konfigurieren
ALTER SCHEMA my_catalog.my_schema RETAIN DROPPED TO 7 DAYS;
```

### Tabellen erstellen und löschen

```sql
CREATE TABLE <catalog-name>.<schema-name>.<table-name>(
  <column-specification>
);
```

```python
from pyspark.sql.types import StructType, StructField, StringType

schema = StructType([StructField("<column-name>", StringType())])
spark.createDataFrame([], schema).write \
  .saveAsTable("<catalog-name>.<schema-name>.<table-name>")
```

```python
from delta.tables import DeltaTable

DeltaTable.create(spark) \
  .tableName("<catalog-name>.<schema-name>.<table-name>") \
  .addColumn("<column-name>", "<data-type>") \
  .property("<key>", "<value>") \
  .execute()
```

```python
# Managed-Iceberg-Tabelle erstellen
from pyspark.sql.types import StructType, StructField, StringType

schema = StructType([StructField("<column-name>", StringType())])
spark.createDataFrame([], schema).write \
  .format("iceberg") \
  .saveAsTable("<catalog-name>.<schema-name>.<table-name>")
```

```sql
DROP TABLE IF EXISTS catalog_name.schema_name.table_name;
```

```python
spark.sql("DROP TABLE IF EXISTS catalog_name.schema_name.table_name")
```

### Automatische Upgrades

Beobachtungsfenster: **50 Tage** (Public Preview) bzw. **100 Tage** (GA-Features). Automatisch aktualisierte GA-Features: Automatic Liquid Clustering (15.4 LTS, ab 22. Mai 2026, nur neue Tabellen), Checkpoint V2 (13.3 LTS, ab 19. Mai 2026 für neue Tabellen in neuen Schemas / 13. Juli 2026 für bestehende Schemas), Row Tracking (14.0, ab 25. Juli 2026 für neue Tabellen in neuen Schemas / 13. Juli 2026 für bestehende Schemas), Catalog Commits (16.4 LTS, ab 13. Juli 2026, zunächst nur neue Tabellen in neuen Schemas), Parquet v2 (18.1, ab 25. Juni 2026, zunächst nur neue Tabellen in neuen Schemas). Jedes Feature rollt graduell aus und erreicht alle Kunden innerhalb von rund sechs Monaten nach Release-Datum.

```sql
-- Änderungen rückgängig machen
RESTORE TABLE <table_name> TO VERSION AS OF <version>;
```

```sql
-- Feature auf einzelner Tabelle deaktivieren
ALTER TABLE <table_name> DROP FEATURE <feature_name>;
```

### External Tables zu Managed Tables konvertieren

```sql
-- Standard-Konvertierung
ALTER TABLE catalog.schema.my_external_table SET MANAGED;

-- Bei aktiviertem Iceberg-Read (UniForm): TRUNCATE UNIFORM HISTORY kappt nur die
-- Iceberg-Historie von UniForm, nicht die Delta-Historie — nötig für saubere
-- Konvertierung mit minimaler Downtime; Iceberg-Time-Travel danach nicht mehr möglich.
ALTER TABLE catalog.schema.my_external_table SET MANAGED TRUNCATE UNIFORM HISTORY;
```

Voraussetzungen: Delta-Lake-Format, Databricks Runtime 17.3 LTS+ (oder Serverless), Tabellenbesitz-Berechtigungen, Reader/Writer auf Runtime 15.4 LTS+, keine nebenläufigen `OPTIMIZE`-Jobs, keine inkompatiblen Delta-Features (`minReaderVersion=2`, `minWriterVersion=7`, Column Mapping). Downtime typischerweise 1–5 Minuten, unabhängig von der Tabellengröße (100 GB: ~1–2 Min.; 1 TB: ~1–2 Min.; 10 TB: ~1–5 Min.).

```sql
-- Verifikation
DESCRIBE EXTENDED catalog_name.schema_name.table_name;
```

```sql
SELECT table_type FROM system.information_schema.tables
WHERE table_catalog = 'catalog_name'
AND table_schema = 'schema_name'
AND table_name = 'table_name';
```

```sql
-- Nachbereitung nach 14 Tagen
VACUUM my_converted_table;
```

### Predictive Optimization: ergänzende Details

```sql
DESCRIBE TABLE EXTENDED catalog_name.schema_name.table_name AS JSON;
```

liefert `predictive_optimization_evaluations` mit Bewertungsergebnissen (warum Operationen übersprungen wurden). Ergebnisse können bis zu 24 Std. verzögert erscheinen. Abrechnung über dedizierte Serverless-Jobs-Preisstufe.

---

## 4. External, Foreign und Temporary Tables

### External Tables

Speichern Daten im eigenen Cloud-Storage, Unity Catalog verwaltet nur Metadaten/Governance. Unterstützte Formate: DELTA, CSV, JSON, AVRO, PARQUET, ORC, TEXT. Beim `DROP` bleiben Dateien erhalten.

```sql
CREATE TABLE <catalog>.<schema>.<table-name>(
  <column-name> <data-type>
)
LOCATION 's3://<bucket-path>/<table-directory>';
```

```sql
CREATE TABLE <catalog>.<schema>.<table-name>
LOCATION 's3://<bucket-path>/<table-directory>'
AS SELECT * FROM <source-table>;
```

```python
from pyspark.sql.types import StructType, StructField, StringType

schema = StructType([StructField("<column-name>", <data-type>())])
spark.createDataFrame([], schema).write \
  .option("path", "s3://<bucket-path>/<table-directory>") \
  .saveAsTable("<catalog>.<schema>.<table-name>")
```

```python
df.write \
  .option("path", "s3://<bucket-path>/<table-directory>") \
  .saveAsTable("<catalog>.<schema>.<table-name>")
```

```sql
DROP TABLE IF EXISTS catalog_name.schema_name.table_name;
```

```python
spark.sql("DROP TABLE IF EXISTS catalog_name.schema_name.table_name")

# Ab Databricks Runtime 18.2+
spark.catalog.dropTable("catalog_name.schema_name.table_name", ifExists=True)
```

### External Partition Discovery

Standardmäßig rekursives Directory-Listing. Alternative ab Runtime 13.3 LTS: **Partition Metadata Logging** (Tabellen damit nur noch mit Runtime 13.3 LTS+ lesbar/schreibbar).

```sql
CREATE OR REPLACE TABLE <catalog>.<schema>.<table-name>
USING <format>
PARTITIONED BY (<partition-column-list>)
TBLPROPERTIES ('partitionMetadataEnabled' = 'true')
LOCATION 's3://<bucket-path>/<table-directory>';
```

```sql
SET spark.databricks.nonDelta.partitionLog.enabled = true;
```

```sql
SHOW PARTITIONS <table-name>;
```

```sql
MSCK REPAIR TABLE <table_name> SYNC PARTITIONS;
MSCK REPAIR TABLE <table_name> ADD PARTITIONS;
MSCK REPAIR TABLE <table_name> DROP PARTITIONS;
```

```sql
ALTER TABLE <table-name>
ADD PARTITION (<partition-column-name> = <partition-column-value>)
LOCATION 's3://<bucket-path>/<table-directory>/<partition-directory>';
```

### Foreign Tables

Nur lesender Zugriff (außer bei internem föderiertem Hive Metastore), verwaltet vom externen System, über Query Federation (JDBC) oder Catalog Federation (Hive Metastore, Glue, Snowflake Horizon Catalog).

### Foreign zu External konvertieren

```sql
ALTER TABLE source_table SET EXTERNAL [DRY RUN]
```

Voraussetzungen: externe HMS-Tabelle (nicht managed), `OWNER`/`MANAGE`-Berechtigung, `CREATE` auf `EXTERNAL LOCATION`, Runtime 17.3+.

```sql
-- Rückgängigmachen (wird beim nächsten Catalog-Sync wieder als Foreign Table föderiert)
DROP TABLE catalog.schema.my_external_table;
```

### Temporary Tables

Sitzungsgebunden, max. **7 Tage** Lebensdauer, standardmäßig Delta-Lake-Format.

```sql
CREATE TEMPORARY TABLE temp_customers (
  id INT,
  name STRING
);
```

```sql
CREATE OR REPLACE TEMP TABLE temp_recent_orders AS
SELECT order_id, customer_id, order_date, amount
FROM prod.sales.orders
WHERE order_date >= current_date() - INTERVAL 30 DAYS;
```

```sql
CREATE TEMP TABLE temp_test_data AS
VALUES
  (9001, 101, 50.00),
  (9002, 204, 75.00),
  (9003, 101, 25.00)
AS t(order_id, customer_id, amount);
```

```sql
SELECT * FROM temp_customers;
```

```sql
SELECT * FROM prod.sales.customers;
```

```sql
INSERT INTO temp_customers
VALUES (101, 'Jane Doe', 'jane@example.com');

UPDATE temp_recent_orders
SET amount = amount * 0.90
WHERE customer_id = 101;

MERGE INTO temp_customers target
USING prod.customer.new_signups source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

```sql
DROP TEMP TABLE temp_customers;
DROP TEMP TABLE IF EXISTS temp_recent_orders;
```

Wichtige Einschränkungen: kein `DELETE FROM`, kein `ALTER TABLE` (Schema), kein Cloning, kein Time Travel, keine Streaming-Queries, nur SQL-APIs, nur ein Nutzer pro Session, nicht auf Single-User-Clustern, nicht in AWS GovCloud.

### Vertiefung: CREATE TABLE ... LOCATION

```sql
CREATE TABLE sec_filings LOCATION 's3://depts/finance/sec_filings';

CREATE OR REPLACE TABLE sec_filings
  LOCATION 's3://depts/finance/sec_filings'
  AS (SELECT * FROM current_filings);
```

```sql
GRANT SELECT ON TABLE sec_filings TO employee;

SELECT count(1) FROM sec_filings;

LIST 's3://depts/finance/sec_filings';
LIST 's3://depts/finance/sec_filings/_delta_log';
```

---

## 5. Apache Iceberg

Zweites von Databricks vollständig unterstütztes offenes Tabellenformat (Spezifikationsversionen 1, 2, 3; nur Apache Parquet als Dateiformat). **Managed Iceberg Tables** (Unity Catalog) sind voll integriert und lese-/schreibfähig; **Foreign Iceberg Tables** (externe Catalogs: AWS Glue, Hive Metastore, Snowflake Horizon Catalog) sind nur lesend.

```sql
-- USING iceberg ist Pflicht, sonst entsteht eine Delta-Tabelle
CREATE TABLE <catalog-name>.<schema-name>.<table-name>(
  <column-specification>
)
USING iceberg;
```

```python
from pyspark.sql.types import StructType, StructField, StringType

schema = StructType([StructField("<column-name>", StringType())])
spark.createDataFrame([], schema).write \
  .format("iceberg") \
  .saveAsTable("<catalog-name>.<schema-name>.<table-name>")
```

```sql
CREATE FOREIGN CATALOG <catalog_name>
  USING CONNECTION <connection_name>
  OPTIONS (<system-spezifische Optionen>);
```

### Iceberg v3: neue Features (Runtime 18 LTS+)

Drei Kernfeatures: **Deletion Vectors** (kein vorheriges Deaktivieren nötig, anders als bei v2), **VARIANT-Datentyp**, **Row Lineage**.

```sql
-- Delta Lake mit Iceberg-Reads
CREATE OR REPLACE TABLE main.schema.table (c1 INT)
TBLPROPERTIES('delta.universalFormat.enabledFormats' = 'iceberg',
'delta.enableIcebergCompatV3' = 'true');
```

```sql
-- Natives Iceberg-Table
CREATE OR REPLACE TABLE main.schema.table (c1 INT)
USING iceberg
TBLPROPERTIES ('format-version' = 3);
```

### Iceberg-Tabellen klonen (nur Deep Clone)

```sql
CREATE TABLE <catalog>.<schema>.<target-table>
DEEP CLONE <catalog>.<schema>.<source-table>;
```

```sql
CREATE OR REPLACE TABLE <catalog>.<schema>.<target-table>
DEEP CLONE <catalog>.<schema>.<source-table>;
```

```sql
CREATE TABLE IF NOT EXISTS <catalog>.<schema>.<target-table>
DEEP CLONE <catalog>.<schema>.<source-table>;
```

```sql
-- Produktions-Archivierung
CREATE TABLE prod_catalog.archive.orders_snapshot_may2026
DEEP CLONE prod_catalog.main.orders;

-- Entwicklungs-Tests
CREATE OR REPLACE TABLE dev_catalog.test.orders
DEEP CLONE prod_catalog.main.orders;

-- Foreign-Iceberg-Tabelle in Unity Catalog übernehmen
CREATE TABLE <uc-catalog>.<schema>.<target-table>
DEEP CLONE <foreign-catalog>.<schema>.<source-table>;
```

### Delta-Tabellen als Iceberg lesen (UniForm)

Ab Runtime 14.3 LTS — siehe Abschnitt 7.14 unten für Details (Aktivierung, Verifikation, VACUUM-Verhalten).

---

## 6. Schema und Tabellenhistorie

### DESCRIBE HISTORY

```sql
DESCRIBE HISTORY table_name;          -- vollständige Historie
DESCRIBE HISTORY table_name LIMIT 1;  -- nur letzte Operation
```

Retention: `logRetentionDuration` (Standard 30 Tage), `deletedFileRetentionDuration` (Standard 7 Tage; Regel: `logRetentionDuration >= deletedFileRetentionDuration`).

```sql
ALTER TABLE table_name SET TBLPROPERTIES (
  delta.logRetentionDuration = "interval 60 days",
  delta.deletedFileRetentionDuration = "interval 30 days"
);

ALTER TABLE table_name SET TBLPROPERTIES (
  iceberg.logRetentionDuration = "interval 60 days",
  iceberg.deletedFileRetentionDuration = "interval 30 days"
);
```

**Historie-Schema** (14 Spalten): `version`, `timestamp`, `userId`, `userName`, `operation`, `operationParameters`, `job`, `notebook`, `clusterId`, `readVersion`, `isolationLevel`, `isBlindAppend`, `operationMetrics`, `userMetadata`. `operationMetrics` variiert je Operationstyp (WRITE, DELETE, MERGE, UPDATE, OPTIMIZE, CLONE, RESTORE, VACUUM, TRUNCATE, FSCK, CONVERT, STREAMING UPDATE).

### Schema Enforcement

Gilt nur für Delta-Lake-Tabellen. Regeln bei `INSERT`: Spalten müssen existieren, Typen werden sicher gecastet.

```sql
-- Fehler: UNRESOLVED_COLUMN.WITH_SUGGESTION
INSERT INTO catalog.schema.target_table (id, unknown_column) VALUES (1, 'value');
```

```sql
-- Erfolgreich: Integer 42 wird sicher zu BIGINT gecastet
INSERT INTO catalog.schema.target_table (id, bigint_column) VALUES (1, 42);
```

```sql
-- Fehler bei MERGE: DELTA_MERGE_UNRESOLVED_EXPRESSION
MERGE INTO catalog.schema.target_table AS t
USING catalog.schema.source_table AS s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.unknown_column = s.value
WHEN NOT MATCHED THEN INSERT (id, unknown_column) VALUES (s.id, s.value);
```

```sql
MERGE INTO catalog.schema.target_table AS t
USING catalog.schema.source_table AS s
ON t.id = s.id
WHEN NOT MATCHED THEN INSERT *;
```

```sql
ALTER TABLE catalog.schema.table_name ADD COLUMN new_column STRING;
```

```sql
SET spark.databricks.delta.schema.autoMerge.enabled = true;
INSERT INTO catalog.schema.table_name SELECT * FROM source_table;
```

```python
df.write.option("mergeSchema", "true").mode("append").saveAsTable("catalog.schema.table_name")
```

```sql
-- External Tables: Metadaten resynchronisieren
MSCK REPAIR TABLE <table-name> SYNC METADATA;
```

### Schema aktualisieren (Schema Evolution)

> Wichtig: Schema-Updates kollidieren mit **allen** nebenläufigen Schreiboperationen und **beenden jeden Stream**, der aus der Tabelle liest.

```sql
ALTER TABLE table_name ADD COLUMNS (col_name data_type [COMMENT col_comment] [FIRST|AFTER colA_name], ...);
```

```sql
-- Verschachtelte Structs
ALTER TABLE boxes ADD COLUMNS (colB.nested STRING AFTER field1);

-- Collections (ARRAY/MAP)
ALTER TABLE my_table ADD COLUMNS (points.element.z DOUBLE);
ALTER TABLE my_table ADD COLUMNS (points.key.z DOUBLE);
ALTER TABLE my_table ADD COLUMNS (points.value.z DOUBLE);
```

```sql
ALTER TABLE table_name ALTER [COLUMN] col_name (COMMENT col_comment | FIRST | AFTER colA_name);
```

```sql
-- Vollständige ALTER COLUMN-Klausel-Referenz
{ ALTER | CHANGE } [ COLUMN ] { column_identifier | field_name }
  { COMMENT comment |
    { FIRST | AFTER column_identifier } |
    { SET | DROP } NOT NULL |
    TYPE data_type |
    SET DEFAULT default_expression |
    DROP DEFAULT |
    SYNC IDENTITY |
    SET MASK mask_clause |
    DROP MASK |
    SET TAGS ('key' = 'value', ...) |
    UNSET TAGS ('key', ...) }
```

```sql
ALTER TABLE people10m ALTER COLUMN middleName DROP NOT NULL;
ALTER TABLE people10m ALTER COLUMN ssn SET NOT NULL;
```

```sql
ALTER TABLE table_name SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true');
ALTER TABLE table_name ALTER COLUMN col_name TYPE BIGINT;
```

```sql
CREATE FUNCTION ssn_mask(ssn STRING)
RETURN CASE WHEN is_account_group_member('HumanResourceDept') THEN ssn ELSE '***-**-****' END;

ALTER TABLE users ALTER COLUMN ssn SET MASK ssn_mask;
ALTER TABLE users ALTER COLUMN ssn DROP MASK;
```

```sql
ALTER TABLE schema.table ALTER COLUMN column_name SET TAGS ('pii' = 'true');
ALTER TABLE schema.table ALTER COLUMN column_name UNSET TAGS ('pii');
```

```sql
ALTER TABLE table_name ALTER COLUMN col_name SET DEFAULT default_expression;
ALTER TABLE table_name ALTER COLUMN col_name DROP DEFAULT;
```

**SYNC IDENTITY** (ab Runtime 10.4+) — kalibriert den internen High-Water-Mark-Zähler einer `GENERATED BY DEFAULT AS IDENTITY`-Spalte neu, wenn manuell größere ID-Werte eingefügt wurden als der Zähler kennt:

```sql
CREATE TABLE orders (
  id BIGINT GENERATED BY DEFAULT AS IDENTITY (START WITH 1 INCREMENT BY 1),
  customer STRING
);

INSERT INTO orders (customer) VALUES ('Anna');
INSERT INTO orders (customer) VALUES ('Ben');
INSERT INTO orders (customer) VALUES ('Clara');

INSERT INTO orders (id, customer) VALUES (1000, 'Alt-Kunde X');
INSERT INTO orders (id, customer) VALUES (1001, 'Alt-Kunde Y');

INSERT INTO orders (customer) VALUES ('Dennis');
```

```sql
ALTER TABLE orders ALTER COLUMN id SYNC IDENTITY;
```

```sql
ALTER TABLE table_name ALTER COLUMN identity_col_name SYNC IDENTITY;
```

```sql
ALTER TABLE table_name REPLACE COLUMNS (col_name1 col_type1 [COMMENT col_comment1], ...);
```

```sql
ALTER TABLE table_name RENAME COLUMN old_col_name TO new_col_name;
ALTER TABLE boxes RENAME COLUMN colB.field1 TO field001;
```

```sql
ALTER TABLE table_name DROP COLUMN col_name;
ALTER TABLE table_name DROP COLUMNS (col_name_1, col_name_2);

-- Physische Bereinigung
REORG TABLE table_name APPLY (PURGE);
VACUUM table_name;
```

```python
(spark.read.table(...)
  .withColumn("birthDate", col("birthDate").cast("date"))
  .write
  .mode("overwrite")
  .option("overwriteSchema", "true")
  .saveAsTable(...))

(spark.read.table(...)
  .withColumnRenamed("dateOfBirth", "birthDate")
  .write
  .mode("overwrite")
  .option("overwriteSchema", "true")
  .saveAsTable(...))
```

```sql
-- SQL (Runtime 18.1+)
INSERT WITH SCHEMA EVOLUTION INTO target_table
SELECT * FROM source_table;
```

```python
(spark.read
  .table("source_table")
  .write
  .option("mergeSchema", "true")
  .mode("append")
  .saveAsTable("target_table"))
```

```python
(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "<path-to-schema-location>")
  .load("<path-to-source-data>")
  .writeStream
  .option("mergeSchema", "true")
  .option("checkpointLocation", "<path-to-checkpoint>")
  .trigger(availableNow=True)
  .toTable("table_name"))
```

```sql
-- SQL (Runtime 15.4 LTS+)
MERGE WITH SCHEMA EVOLUTION INTO target
USING source
ON source.key = target.key
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE THEN DELETE;
```

```python
from delta.tables import *

(targetTable
  .merge(sourceDF, "source.key = target.key")
  .withSchemaEvolution()
  .whenMatchedUpdateAll()
  .whenNotMatchedInsertAll()
  .whenNotMatchedBySourceDelete()
  .execute())
```

```sql
-- EXCEPT-Klausel (ab Runtime 12.2 LTS+)
MERGE INTO target t
USING source s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET last_updated = current_date()
WHEN NOT MATCHED THEN INSERT * EXCEPT (last_updated, internal_count);
```

```python
# Legacy: Session-weite Aktivierung (nicht für Produktion empfohlen)
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", True)
```

```python
df.write.option("overwriteSchema", "true")
```

### Tabelleneigenschaften (TBLPROPERTIES)

```sql
ALTER TABLE <table-name> SET TBLPROPERTIES ('property.name' = value);
```

Präfix `delta.` bzw. `iceberg.`. Wichtige Eigenschaften (Auswahl): `appendOnly`, `autoOptimize.autoCompact`, `autoOptimize.optimizeWrite`, `checkpointPolicy` (`classic`/`v2`), `columnMapping.mode`, `dataSkippingNumIndexedCols` (Standard 32), `deletedFileRetentionDuration` (Standard 1 Woche), `enableChangeDataFeed`, `enableDeletionVectors`, `enableIcebergCompatV2`, `enableRowTracking`, `enableTypeWidening`, `format-version` (Iceberg, Standard 2), `isolationLevel` (Standard `WriteSerializable`), `logRetentionDuration` (Standard 30 Tage), `minReaderVersion`/`minWriterVersion`, `parquet.compression.codec` (Standard `ZSTD`), `parquet.format.version` (Standard `1.0.0`), `randomizeFilePrefixes`, `targetFileSize`, `universalFormat.enabledFormats`.

---

## 7. Table Features

### 7.1 Catalog Commits

Verlagert Transaktionskoordination von Tabellen- auf Catalog-Ebene. Voraussetzung: Runtime 16.4+ (Lesen/Schreiben/Erstellen), 18.0+ (Toggle auf bestehenden Tabellen), 17.3+ (Streaming Tables/Materialized Views). Iceberg-Unterstützung: Private Preview.

```sql
CREATE TABLE sales_data (
  sale_id BIGINT,
  amount DECIMAL(10,2),
  sale_date DATE)
TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported');
```

```sql
ALTER TABLE sales_data SET TBLPROPERTIES
  ('delta.feature.catalogManaged' = 'supported');
```

```sql
CREATE OR REFRESH STREAMING TABLE streaming_sales_data
TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported')
AS SELECT * FROM STREAM sales_data;
```

```sql
DESCRIBE DETAIL sales_data;
```

### 7.2 Change Data Feed (CDF)

Zwei Ansätze: **Automatic CDF** (Public Preview, Row-Lineage-basiert, Delta + Iceberg v3, Runtime 18 LTS+) vs. **Legacy CDF** (materialisiert beim Schreiben, nur Delta, individuelle Konfiguration). Nicht gleichzeitig auf derselben Tabelle nutzbar.

```sql
SELECT * FROM table_changes('tableName', 0, 10);
```

```python
spark.read.option("readChangeFeed", "true").option("startingVersion", 0).table("tableName")
```

```python
spark.read \
  .option("readChangeFeed", "true") \
  .option("startingVersion", 0) \
  .table("<table_name>")
```

```sql
SELECT * FROM table_changes('<table_name>', 0);
```

```python
(spark.readStream
  .option("readChangeFeed", "true")
  .table("<table_name>"))
```

Schema: `_change_type` (`insert`/`update_preimage`/`update_postimage`/`delete`), `_commit_version`, `_commit_timestamp`.

```sql
SELECT * FROM table_changes('tableName', 0, 10);

SELECT * FROM table_changes('tableName', '2021-04-21 05:45:46', '2021-05-21 12:00:00');
```

```python
spark.read \
  .option("readChangeFeed", "true") \
  .option("startingVersion", 0) \
  .table("myDeltaTable")

spark.read \
  .option("readChangeFeed", "true") \
  .option("startingVersion", 0) \
  .option("endingVersion", 10) \
  .table("myDeltaTable")
```

```sql
SET spark.databricks.delta.changeDataFeed.timestampOutOfRange.enabled = true;
```

```sql
CREATE TABLE myschema.t(c1 INT, c2 STRING)
  TBLPROPERTIES(delta.enableChangeDataFeed=true);

INSERT INTO myschema.t VALUES (1, 'Hello'), (2, 'World');
INSERT INTO myschema.t VALUES (3, '!');
UPDATE myschema.t SET c2 = upper(c2) WHERE c1 < 3;
DELETE FROM myschema.t WHERE c1 = 3;

SELECT * FROM table_changes('`myschema`.`t`', 2);
SELECT * FROM table_changes('`myschema`.`t`',
  '2022-09-01T18:32:27.000+0000') ORDER BY _commit_version;
```

```python
(spark.readStream
  .option("readChangeFeed", "true")
  .table("source_table")
  .writeStream
  .option("checkpointLocation", "<checkpoint-path>")
  .trigger(availableNow=True)
  .toTable("target_table"))
```

```sql
-- Migration von Legacy zu Automatic CDF
ALTER TABLE <table_name> UNSET TBLPROPERTIES ('delta.enableChangeDataFeed');
ALTER TABLE <table_name> SET TBLPROPERTIES (delta.enableRowTracking = true);
```

```sql
CREATE TABLE student (id INT, name STRING, age INT)
  TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

```sql
ALTER TABLE myDeltaTable
  SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

### 7.3 Checkpoint V2

Ermöglicht mehr nebenläufige Writer, reduziert Schreibkonflikte. Runtime 13.3 LTS+. Automatisch bei Liquid Clustering ab 14.1+.

```sql
ALTER TABLE table_name SET TBLPROPERTIES ('delta.checkpointPolicy' = 'v2');
```

```sql
CREATE TABLE table_name (...) TBLPROPERTIES ('delta.checkpointPolicy' = 'v2');
```

```sql
-- Downgrade
ALTER TABLE table_name DROP FEATURE v2Checkpoint;
```

### 7.4 Collation

Ab Runtime 16.4 LTS. Standard-Collation: `UTF8_BINARY`.

```sql
CREATE TABLE catalog.schema.my_table (
  id BIGINT,
  name STRING COLLATE UTF8_LCASE,
  metadata STRUCT<label: STRING COLLATE UNICODE>,
  tags ARRAY<STRING COLLATE UTF8_LCASE>,
  properties MAP<STRING, STRING COLLATE UTF8_LCASE>
) USING delta;
```

```sql
ALTER TABLE my_table ALTER COLUMN name TYPE STRING COLLATE UTF8_LCASE;

-- Auf Standard zurücksetzen
ALTER TABLE my_table ALTER COLUMN name TYPE STRING COLLATE UTF8_BINARY;
```

```sql
ANALYZE TABLE my_table COMPUTE DELTA STATISTICS;
OPTIMIZE FULL my_table;
SET spark.databricks.optimize.incremental = false;
OPTIMIZE my_table ZORDER BY zorder_column;
```

```sql
ALTER TABLE my_table ALTER COLUMN name TYPE STRING COLLATE UTF8_BINARY;
ALTER TABLE my_table DROP FEATURE collations;
```

### 7.5 Column Mapping

Reine Metadaten-Änderungen zum Umbenennen/Löschen von Spalten, ohne Dateien neu zu schreiben. Protokoll: Reader 2+, Writer 5+.

```sql
CREATE TABLE <table-name> (id INT, name STRING)
USING DELTA
TBLPROPERTIES ('delta.columnMapping.mode' = 'id');
```

```sql
ALTER TABLE <table-name> SET TBLPROPERTIES
('delta.columnMapping.mode' = 'name');
```

```sql
ALTER TABLE <table-name> RENAME COLUMN old_col_name TO new_col_name;

ALTER TABLE table_name DROP COLUMN col_name;
ALTER TABLE table_name DROP COLUMNS (col_name_1, col_name_2, ...);
```

```sql
ALTER TABLE <table-name> SET TBLPROPERTIES ('delta.columnMapping.mode' = 'none');
```

```python
checkpoint_path = "/path/to/checkpointLocation"
(spark.readStream
  .option("schemaTrackingLocation", checkpoint_path)
  .table("delta_source_table")
  .writeStream
  .option("checkpointLocation", checkpoint_path)
  .toTable("output_table"))
```

### 7.6 Deletion Vectors

Markieren Zeilen als modifiziert in Metadaten statt Dateien neu zu schreiben. Apache Iceberg v3: standardmäßig enthalten. Delta Lake: explizite Aktivierung.

```sql
CREATE TABLE <table-name> TBLPROPERTIES ('delta.enableDeletionVectors' = true);
ALTER TABLE <table-name> SET TBLPROPERTIES ('delta.enableDeletionVectors' = true);
```

```sql
CREATE TABLE <table-name> TBLPROPERTIES ('iceberg.enableDeletionVectors' = true);
ALTER TABLE <table-name> SET TBLPROPERTIES ('iceberg.enableDeletionVectors' = true);
```

Physische Bereinigung:

```sql
-- 1. OPTIMIZE, dann:
REORG TABLE table_name APPLY (PURGE);
-- 2. Danach VACUUM mit passender Retention-Schwelle
```

```sql
SET spark.databricks.delta.reorg.purgeMode = 'rows';
```

### 7.7 DROP FEATURE

```sql
ALTER TABLE <table-name> DROP FEATURE <feature-name>;
```

```sql
-- Vollständiges Protokoll-Downgrade mit Historien-Truncation
ALTER TABLE <table-name> DROP FEATURE <feature-name> TRUNCATE HISTORY;
```

Runtime 16.3+ (16.4 LTS empfohlen), `MODIFY`-Zugriff, nur ein Feature pro Befehl. Entfernbare Features: `catalogManaged`, `checkConstraints`, `collations-preview`, `columnMapping`, `deletionVectors`, `typeWidening`, `v2Checkpoint`, `checkpointProtection`.

**Zweistufiger Downgrade-Prozess:** Schritt 1 sofort (`DROP FEATURE ... TRUNCATE HISTORY`), Schritt 2 nach 24+ Stunden erneut ausführen — entfernt dabei alle Transaktionslog-Daten älter als 24 Stunden (Time-Travel-Verlust für diesen Zeitraum).

### 7.8 Feature Compatibility

`minReaderVersion` (1–3), `minWriterVersion` (2–7). Bei 3/7: Table Features (feingranulare Flags). Databricks empfiehlt ausdrücklich, diese Werte **niemals direkt zu verändern**.

**Mindest-Runtimes (Auswahl):** TimestampNTZ/Iceberg Reads/Liquid Clustering: 13.3 LTS; Row Tracking: 14.3 LTS; Type Widening/VARIANT: 15.4 LTS; Collations: 16.1; Protected Checkpoints: 16.3; Catalog Commits: 16.4 LTS.

### 7.9 Generated Columns

Werden physisch gespeichert, nicht zur Query-Zeit berechnet.

```sql
CREATE TABLE default.people10m (
  id INT,
  firstName STRING,
  birthDate TIMESTAMP,
  dateOfBirth DATE GENERATED ALWAYS AS (CAST(birthDate AS DATE))
);
```

```python
DeltaTable.create(spark) \
  .tableName("default.people10m") \
  .addColumn("id", "INT") \
  .addColumn("birthDate", "TIMESTAMP") \
  .addColumn("dateOfBirth", DateType(),
    generatedAlwaysAs="CAST(birthDate AS DATE)") \
  .execute()
```

```sql
CREATE TABLE events(
  eventId BIGINT,
  eventTime TIMESTAMP,
  eventDate DATE GENERATED ALWAYS AS (CAST(eventTime AS DATE))
)
PARTITIONED BY (eventDate);

SELECT * FROM events
WHERE eventTime >= "2020-10-01" AND eventTime <= "2020-10-01 12:00:00"
-- Filtert automatisch die Partition date=2020-10-01
```

**Identity Columns** (spezialisierte Generated Columns, nur `BIGINT`):

```sql
CREATE TABLE table_name (
  id_col1 BIGINT GENERATED ALWAYS AS IDENTITY,
  id_col2 BIGINT GENERATED ALWAYS AS IDENTITY (START WITH -1 INCREMENT BY 1),
  id_col3 BIGINT GENERATED BY DEFAULT AS IDENTITY
);
```

```python
from delta.tables import DeltaTable, IdentityGenerator
from pyspark.sql.types import LongType

DeltaTable.create() \
  .tableName("table_name") \
  .addColumn("id_col1", dataType=LongType(), generatedAlwaysAs=IdentityGenerator()) \
  .addColumn("id_col2", dataType=LongType(), generatedAlwaysAs=IdentityGenerator(start=-1, step=1)) \
  .addColumn("id_col3", dataType=LongType(), generatedByDefaultAs=IdentityGenerator()) \
  .execute()
```

```sql
CREATE OR REPLACE TABLE new_table (
  id BIGINT GENERATED BY DEFAULT AS IDENTITY (START WITH 5),
  event_date DATE,
  some_value BIGINT);

INSERT INTO new_table (id, event_date, some_value)
SELECT id, event_date, some_value FROM old_table;

INSERT INTO new_table (event_date, some_value)
SELECT event_date, some_value FROM new_records;
```

```sql
-- Inkompatibilität mit Column Masks
CREATE TABLE tbl (
  a INT MASK masking_function,
  generated_col INT GENERATED ALWAYS AS (a + 1)) USING DELTA;
```

```sql
CREATE TABLE tbl (
  a INT,
  generated_col INT GENERATED ALWAYS AS (a + 1)) USING DELTA;
ALTER TABLE tbl ALTER COLUMN a SET MASK masking_function;
```

### 7.10 Parquet v2

Ab Runtime 18.1. Fortgeschrittene Encodings, v2-Datenseiten-Header, INT64-Timestamps.

```sql
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.parquet.format.version' = '2.12.0');
ALTER TABLE <table_name> SET TBLPROPERTIES ('iceberg.parquet.format.version' = '2.12.0');
CREATE TABLE <table_name> (...) TBLPROPERTIES ('delta.parquet.format.version' = '2.12.0');
CREATE TABLE <table_name> (...) USING iceberg TBLPROPERTIES ('iceberg.parquet.format.version' = '2.12.0');
```

```sql
-- Bestehende Dateien neu schreiben (ab Runtime 18.2+)
REORG TABLE <table_name> APPLY (SET PARQUET (FORMAT_VERSION = '2.12.0'));

-- Rückgängigmachen
REORG TABLE <table_name> APPLY (SET PARQUET (FORMAT_VERSION = '1.0.0'));
```

### 7.11 Row Tracking

Ab Runtime 14.0. Stabile Row-IDs und Row-Commit-Versionen.

```sql
CREATE TABLE table_name TBLPROPERTIES (delta.enableRowTracking = true) AS SELECT * FROM source_table;
```

```sql
ALTER TABLE table_name SET TBLPROPERTIES (delta.enableRowTracking = true);
```

```sql
ALTER TABLE table_name SET TBLPROPERTIES (delta.enableRowTracking = false);
```

Metadaten-Felder: `_metadata.row_id`, `_metadata.row_commit_version`. Deaktivieren entfernt das Feature nicht vollständig — dafür `DROP FEATURE` nötig.

### 7.12 Constraints

**Durchgesetzt:** `NOT NULL`, `CHECK`. **Informativ (nicht durchgesetzt):** Primary Key, Foreign Key, Unique.

```sql
CREATE TABLE people10m (
  id INT NOT NULL,
  firstName STRING,
  middleName STRING NOT NULL
);

ALTER TABLE people10m ALTER COLUMN middleName DROP NOT NULL;
ALTER TABLE people10m ALTER COLUMN ssn SET NOT NULL;
```

```sql
ALTER TABLE people10m ADD CONSTRAINT dateWithinRange
  CHECK (birthDate > '1900-01-01');

ALTER TABLE people10m DROP CONSTRAINT dateWithinRange;
```

```sql
DESCRIBE DETAIL people10m;
SHOW TBLPROPERTIES people10m;
```

```sql
CREATE TABLE T(pk1 INTEGER NOT NULL, pk2 INTEGER NOT NULL,
  CONSTRAINT t_pk PRIMARY KEY(pk1, pk2));

CREATE TABLE S(pk INTEGER NOT NULL PRIMARY KEY,
  fk1 INTEGER, fk2 INTEGER,
  CONSTRAINT s_t_fk FOREIGN KEY(fk1, fk2) REFERENCES T);

CREATE TABLE U(id INTEGER NOT NULL, email STRING NOT NULL,
  CONSTRAINT u_uq_email UNIQUE(email));
```

```sql
ALTER TABLE T ADD CONSTRAINT t_pk PRIMARY KEY(pk1, pk2);
ALTER TABLE S ADD CONSTRAINT s_t_fk FOREIGN KEY(fk1, fk2) REFERENCES T;
ALTER TABLE U ADD CONSTRAINT u_uq_email UNIQUE(email);
```

```sql
CREATE TABLE persons(
  first_name STRING NOT NULL,
  last_name STRING NOT NULL,
  nickname STRING,
  CONSTRAINT persons_pk PRIMARY KEY(first_name, last_name));

CREATE TABLE customers(customerid STRING NOT NULL PRIMARY KEY, name STRING);
```

```sql
CREATE TABLE pets(
  name STRING, owner_first_name STRING, owner_last_name STRING,
  CONSTRAINT pets_persons_fk FOREIGN KEY (owner_first_name, owner_last_name)
    REFERENCES persons);

CREATE TABLE orders(
  orderid BIGINT NOT NULL CONSTRAINT orders_pk PRIMARY KEY,
  customerid STRING CONSTRAINT orders_customers_fk REFERENCES customers);
```

```sql
CREATE TABLE person_contacts(
  first_name STRING NOT NULL, last_name STRING NOT NULL,
  nickname STRING UNIQUE);

CREATE TABLE person_accounts(
  first_name STRING NOT NULL, last_name STRING NOT NULL, account_id STRING,
  CONSTRAINT person_accounts_uq UNIQUE(first_name, last_name));
```

Runtime-Verfügbarkeit: Primary-/Foreign-Key ab 13.3 LTS (GA ab 15.2+), Unique ab 18.2+ (Public Preview). `CTAS` unterstützt keine Constraint-Klauseln.

### 7.13 Type Widening

Ab Runtime 15.4 LTS. Typänderung in breiteren Typ ohne Datei-Neuschreibung.

| Ausgangstyp | Unterstützte breitere Typen |
|---|---|
| BYTE | SHORT, INT, BIGINT, DECIMAL, DOUBLE |
| SHORT | INT, BIGINT, DECIMAL, DOUBLE |
| INT | BIGINT, DECIMAL, DOUBLE |
| BIGINT | DECIMAL |
| FLOAT | DOUBLE |
| DECIMAL | DECIMAL mit größerer Präzision/Skala |
| DATE | TIMESTAMP_NTZ |
| VOID | jeder Typ |

```sql
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true');
CREATE TABLE T(c1 INT) TBLPROPERTIES('delta.enableTypeWidening' = 'true');
```

```sql
ALTER TABLE <table_name> ALTER COLUMN <col_name> TYPE <new_type>;
```

```sql
CREATE TABLE target_table (id INT, data STRING) TBLPROPERTIES ('delta.enableTypeWidening' = 'true');
CREATE TABLE source_table (id BIGINT, data STRING);
INSERT WITH SCHEMA EVOLUTION INTO target_table SELECT * FROM source_table;
```

```python
spark.table("source_table").write.mode("append").option("mergeSchema", "true").saveAsTable("target_table")
```

```python
from delta.tables import DeltaTable
source_df = spark.table("source_table")
target_table = DeltaTable.forName(spark, "target_table")
(target_table.alias("target")
  .merge(source_df.alias("source"), "target.id = source.id")
  .withSchemaEvolution()
  .whenMatchedUpdateAll()
  .whenNotMatchedInsertAll()
  .execute())
```

```sql
MERGE WITH SCHEMA EVOLUTION INTO target_table
USING source_table
ON target_table.id = source_table.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

```python
(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "<path-to-schema-location>")
  .load("<path-to-source-data>")
  .writeStream
  .option("mergeSchema", "true")
  .option("checkpointLocation", "<path-to-checkpoint>")
  .trigger(availableNow=True)
  .toTable("table_name"))
```

```python
(spark.readStream
  .table("delta_source_table")
  .writeStream
  .option("checkpointLocation", "/path/to/checkpointLocation")
  .option("mergeSchema", "true")
  .toTable("output_table"))
```

```python
checkpoint_path = "/path/to/checkpointLocation"
(spark.readStream
  .option("schemaTrackingLocation", checkpoint_path)
  .table("delta_source_table")
  .writeStream
  .option("checkpointLocation", checkpoint_path)
  .toTable("output_table"))
```

```python
checkpoint_path = "/path/to/checkpointLocation"
(spark.readStream
  .option("schemaTrackingLocation", checkpoint_path)
  .option("allowSourceColumnTypeChange", "<delta_source_table_version>")
  .table("delta_source_table")
  .writeStream
  .option("checkpointLocation", checkpoint_path)
  .toTable("output_table"))
```

```sql
SET spark.databricks.delta.streaming.allowSourceColumnTypeChange.ckpt_<checkpoint_id> = "<delta_source_table_version>";
SET spark.databricks.delta.streaming.allowSourceColumnTypeChange = "<delta_source_table_version>";
SET spark.databricks.delta.streaming.allowSourceColumnTypeChange = "always";
```

```json
{ "configuration": { "pipelines.enableTypeWidening": "true" } }
```

```yaml
configuration:
  pipelines.enableTypeWidening: 'true'
```

```python
import dlt
@dlt.table(
  table_properties={"delta.enableTypeWidening": "true"})
def my_table():
  return spark.readStream.table("source_table")
```

```sql
CREATE OR REFRESH STREAMING TABLE my_table
TBLPROPERTIES ('delta.enableTypeWidening' = 'true')
AS SELECT * FROM source_table;
```

```sql
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.enableTypeWidening' = 'false');
ALTER TABLE <table-name> DROP FEATURE 'typeWidening' [TRUNCATE HISTORY];
```

```python
spark.read.table("table_name") \
  .selectExpr("hash(CAST(column_name AS BIGINT))")
```

```sql
SELECT hash(CAST(column_name AS BIGINT)) FROM table_name;
```

### 7.14 Iceberg Reads (UniForm)

Ab Runtime 14.3 LTS. Erzeugt automatisch Iceberg-Metadaten neben Delta-Metadaten, ohne Parquet-Dateien neu zu schreiben.

```sql
CREATE TABLE T(c1 INT) TBLPROPERTIES(
  'delta.columnMapping.mode' = 'id',
  'delta.enableIcebergCompatV2' = 'true',
  'delta.universalFormat.enabledFormats' = 'iceberg');
```

```sql
ALTER TABLE table_name SET TBLPROPERTIES(
  'delta.columnMapping.mode' = 'name',
  'delta.enableIcebergCompatV2' = 'true',
  'delta.universalFormat.enabledFormats' = 'iceberg');
```

```sql
REORG TABLE table_name APPLY (UPGRADE UNIFORM(ICEBERG_COMPAT_VERSION=2));
```

```sql
DESCRIBE EXTENDED catalog_name.schema_name.table_name;
SHOW TBLPROPERTIES catalog_name.schema_name.table_name;
```

```sql
ALTER TABLE table_name UNSET TBLPROPERTIES ('delta.universalFormat.enabledFormats');
```

```sql
MSCK REPAIR TABLE <table-name> SYNC METADATA;
```

### 7.15 VARIANT-Datentyp

Ab Runtime 15.4 LTS. Speichert semi-strukturierte Daten in offenem Binär-Encoding.

```sql
CREATE TABLE table_name (variant_column VARIANT)
```

```sql
ALTER TABLE table_name SET TBLPROPERTIES('delta.feature.variantType' = 'supported')
```

Einschränkungen: nicht partitionierbar, kein Clustering-Key, nicht in `GROUP BY`/`ORDER BY`/`DISTINCT`/Set-Operatoren, keine Generated Column, keine `minValues`/`maxValues`-Statistiken, max. 128 MiB pro Wert (16 MiB bei Runtime ≤17.1).

### 7.16 Variant Shredding

Ab Runtime 17.3. Häufig genutzte Felder werden separat spaltenweise in Parquet gespeichert.

```sql
ALTER TABLE my_table SET TBLPROPERTIES ('delta.enableVariantShredding' = 'true');
ALTER TABLE my_table SET TBLPROPERTIES ('iceberg.enableVariantShredding' = 'true');
```

```sql
REORG TABLE my_table APPLY (SHRED VARIANT);
```

```sql
ALTER TABLE my_table SET TBLPROPERTIES ('delta.enableVariantShredding' = 'false');
ALTER TABLE my_table DROP FEATURE "variantShredding";
```

---

## 8. Transactions

Multi-Statement-, Multi-Table-Transaktionen mit vollen ACID-Garantien, aufbauend auf Catalog Commits. Zwei Modi: **Non-Interactive** (`BEGIN ATOMIC`, automatisches Commit/Rollback) und **Interactive** (`BEGIN TRANSACTION`, manuelles `COMMIT`/`ROLLBACK`, nur SQL Warehouses). Grenzen: max. 100 Tabellen (lesend/schreibend kombiniert) sowie zusätzlich max. 100 Views (nur lesend) pro Transaktion, je Tabelle max. 100 Zwischen-Commits, 10-Min-Idle-Timeout (Interactive), 48-Std-Maximaldauer, keine DDL, kein Time Travel.

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

```sql
BEGIN TRANSACTION;
INSERT INTO staging_customers SELECT * FROM external_customers WHERE load_date = current_date();
COMMIT;
```

```java
conn.setAutoCommit(false);
stmt.executeUpdate("INSERT INTO accounts (account_id, balance) VALUES (1001, 5000)");
stmt.executeUpdate("UPDATE accounts SET balance = balance - 100 WHERE account_id = 1001");
conn.commit();
```

### Tutorial: Transaktionen koordinieren

```sql
CREATE TABLE IF NOT EXISTS sample_accounts (
  id INT,
  account_name STRING,
  balance DECIMAL(10,2)) USING DELTA
TBLPROPERTIES (
  'delta.feature.catalogManaged' = 'supported');

CREATE TABLE IF NOT EXISTS sample_transactions (
  id INT,
  account_id INT,
  transaction_type STRING,
  amount DECIMAL(10,2)) USING DELTA
TBLPROPERTIES (
  'delta.feature.catalogManaged' = 'supported');
```

```sql
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported');
```

```sql
INSERT INTO sample_accounts VALUES
  (1, 'Alice', 1000.00),
  (2, 'Bob', 500.00);

INSERT INTO sample_transactions VALUES
  (1, 1, 'deposit', 100.00);
```

```sql
BEGIN ATOMIC
  UPDATE sample_accounts
  SET balance = balance + 100.00
  WHERE id = 1;

  INSERT INTO sample_transactions
  VALUES (2, 1, 'deposit', 100.00);
END;
```

```sql
BEGIN ATOMIC
  INSERT INTO sample_accounts VALUES (3, 'Charlie', -50.00);
  IF (SELECT balance FROM sample_accounts WHERE id = 3) < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Account balance cannot be negative';
  END IF;
END;
```

```sql
BEGIN ATOMIC
  INSERT INTO sample_accounts VALUES (4, 'David', 300.00);
  INSERT INTO non_existent_table VALUES (1, 2, 3);
END;
```

```sql
BEGIN TRANSACTION;

INSERT INTO sample_accounts VALUES (5, 'Eve', 850.00);
UPDATE sample_accounts SET balance = balance + 50.00 WHERE id = 2;

COMMIT;
```

```sql
BEGIN TRANSACTION;

INSERT INTO sample_accounts VALUES (6, 'Frank', 600.00);

SELECT * FROM sample_accounts WHERE id = 6;

ROLLBACK;
```

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
    INSERT INTO main.retail.orders (order_id, customer_id, amount)
    VALUES (p_order_id, p_customer_id, p_order_amount);

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

```sql
BEGIN ATOMIC
    DECLARE new_order_id STRING DEFAULT uuid();
    DECLARE v_batch_id STRING DEFAULT uuid();

    INSERT INTO main.retail.orders_staging (order_id, customer_id, amount, batch_id)
    VALUES (new_order_id, 'CUST_123', 249.99, v_batch_id);

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

    DELETE FROM main.retail.orders_staging
    WHERE batch_id = v_batch_id;
END;
```

```sql
DROP TABLE IF EXISTS sample_accounts;
DROP TABLE IF EXISTS sample_transactions;
DROP TABLE IF EXISTS main.retail.orders;
DROP TABLE IF EXISTS main.retail.orders_staging;
DROP TABLE IF EXISTS main.retail.total_sales;
```

### Vertiefung: BEGIN/COMMIT/ROLLBACK (Language Manual)

```sql
BEGIN TRANSACTION;
SELECT COUNT(*) FROM orders;
COMMIT;
```

```sql
BEGIN ATOMIC
  statement1;
  statement2;
  ...
END;
```

```sql
-- COMMIT macht vorherige Statements nach einem Fehler nicht ungeschehen
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
ROLLBACK;
```

```sql
BEGIN TRANSACTION;
SELECT 1/0;
SELECT 1;
ROLLBACK TRANSACTION;
```

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

---

## 9. Tabellenlayout und Performance

Liquid Clustering, Data Skipping, Dateigröße und Partitionierung sind ausführlich im Ordner `Performance Optimization/Foundation Design` behandelt (siehe dort). Dieses Dokument ergänzt die **Tabellengrößen-Überwachung**.

```sql
ANALYZE TABLE table_name COMPUTE STORAGE METRICS;
```

Ab Runtime 18.0, ausschließlich für Unity-Catalog-Managed-Tables. Liefert Total Storage Size, Active Data, Vacuumable Data, Time Travel Data.

**Wichtig:** die per UI/`DESCRIBE` gemeldete Tabellengröße entspricht **nicht** der tatsächlichen Cloud-Storage-Verzeichnisgröße (Time-Travel-Versionen belegen zusätzlichen Platz bis zum nächsten `VACUUM`).

### Vertiefung: Bloomfilter-Indizes (deprecated)

```sql
DROP BLOOMFILTER INDEX ON [TABLE] table_name [FOR COLUMNS(columnName1 [, ...])]
```

Bloom-Filter-Indizes sind deprecated — durch Predictive I/O, Data Skipping und Liquid Clustering abgelöst; Databricks empfiehlt, bestehende zu entfernen.

---

## 10. Tabellenoperationen

### 10.1 Clone, Details und Metadaten

**Deep Clone** (`CLONE`/`DEEP CLONE`): kopiert Daten und Metadaten vollständig. **Shallow Clone** (`SHALLOW CLONE`): kopiert nur Metadaten, referenziert Original-Dateien.

```sql
CREATE TABLE target_table CLONE source_table;
CREATE OR REPLACE TABLE target_table CLONE source_table;
CREATE TABLE IF NOT EXISTS target_table CLONE source_table;
```

```sql
CREATE TABLE target_table SHALLOW CLONE source_table;
CREATE TABLE target_table SHALLOW CLONE source_table VERSION AS OF version;
CREATE TABLE target_table SHALLOW CLONE source_table TIMESTAMP AS OF timestamp_expression;
```

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "source_table")
deltaTable.clone(target="target_table", isShallow=True, replace=False)
deltaTable.cloneAtVersion(version=1, target="target_table", isShallow=True, replace=False)
deltaTable.cloneAtTimestamp(timestamp="2019-01-01", target="target_table", isShallow=True, replace=False)
```

```sql
CREATE OR REPLACE TABLE archive_table CLONE my_prod_table;
```

```sql
CREATE TABLE model_dataset CLONE entire_dataset VERSION AS OF 15;
```

```sql
CREATE TABLE my_test SHALLOW CLONE my_prod_table;
UPDATE my_test WHERE user_id is null SET invalid=true;
MERGE INTO my_prod_table USING my_test ...;
DROP TABLE my_test;
```

```sql
CREATE OR REPLACE TABLE archive_table CLONE prod.my_table
TBLPROPERTIES (delta.logRetentionDuration = '3650 days',
               delta.deletedFileRetentionDuration = '3650 days');
```

```python
dt = DeltaTable.forName(spark, "prod.my_table")
tblProps = {"delta.logRetentionDuration": "3650 days",
            "delta.deletedFileRetentionDuration": "3650 days"}
dt.clone(target="archive_table", isShallow=False, replace=True, tblProps)
```

**Shallow Clone in Unity Catalog** (Public Preview) — unabhängige Zugriffskontrolle, Managed-zu-Managed bzw. External-zu-External:

```sql
CREATE TABLE <catalog-name>.<schema-name>.<target-table-name>
SHALLOW CLONE <catalog-name>.<schema-name>.<source-table-name>;
```

```sql
CREATE TABLE <catalog-name>.<schema-name>.<target-table-name>
SHALLOW CLONE <catalog-name>.<schema-name>.<source-table-name>
LOCATION 's3://<bucket-name>/<path-name>/<target-table-name>';
```

**DESCRIBE DETAIL:**

```sql
DESCRIBE DETAIL '/data/events/';
DESCRIBE DETAIL eventsTable;
```

**Benutzerdefinierte Metadaten (`userMetadata`):**

```sql
SET spark.databricks.delta.commitInfo.userMetadata=overwrite-comment;
INSERT OVERWRITE target_table SELECT * FROM data_source;
```

```sql
SET spark.databricks.iceberg.commitInfo.userMetadata=overwrite-comment;
INSERT OVERWRITE target_table SELECT * FROM data_source;
```

```python
df.write.mode("overwrite").option("userMetadata", "overwrite-comment").saveAsTable("target_table")
df.write.mode("append").option("userMetadata", "append-comment").saveAsTable("target_table")
```

**Vertiefung — CREATE TABLE ... CLONE (Language Manual):**

```sql
CREATE TABLE [IF NOT EXISTS] table_name
  [SHALLOW | DEEP] CLONE source_table_name [TBLPROPERTIES clause] [LOCATION path]

[CREATE OR] REPLACE TABLE table_name
  [SHALLOW | DEEP] CLONE source_table_name [TBLPROPERTIES clause] [LOCATION path]
```

```sql
CREATE TABLE target_catalog.target_schema.target_table
DEEP CLONE source_catalog.source_schema.source_table;

CREATE TABLE target_catalog.target_schema.target_table
SHALLOW CLONE source_catalog.source_schema.source_table;
```

```sql
DESCRIBE HISTORY table_name
```

```sql
RESTORE [ TABLE ] table_name [ TO ]
{ TIMESTAMP AS OF timestamp_expression | VERSION AS OF version }
```

```sql
RESTORE TABLE employee TO VERSION AS OF 1;

RESTORE TABLE employee TO TIMESTAMP AS OF '2022-08-02 00:00:00';

RESTORE TABLE employee TO TIMESTAMP AS OF current_timestamp() - INTERVAL '1' HOUR;
```

### 10.2 DROP, OPTIMIZE, VACUUM und Auto-TTL

**DROP TABLE:** Nur Managed Tables in Unity Catalog sind über `UNDROP` innerhalb des Recovery-Fensters (Standard 7 Tage) wiederherstellbar.

```sql
DROP TABLE table_name;
```

```sql
-- Anti-Pattern — NICHT EMPFOHLEN
DROP TABLE IF EXISTS table_name;
CREATE TABLE table_name AS SELECT ...
```

```sql
-- Empfohlene Alternative (atomar)
CREATE OR REPLACE TABLE table_name AS SELECT * FROM parquet.`/path/to/files`;
```

**OPTIMIZE:**

```sql
OPTIMIZE table_name;
OPTIMIZE table_name WHERE date >= '2022-11-18';
```

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "table_name")
deltaTable.optimize().executeCompaction()
```

```sql
OPTIMIZE events;
OPTIMIZE events FULL;
OPTIMIZE events WHERE date >= '2017-01-01';

OPTIMIZE events
WHERE date >= current_timestamp() - INTERVAL 1 day
ZORDER BY (eventType);
```

```sql
ALTER TABLE table_name SET TBLPROPERTIES ('delta.parquet.compression.codec' = 'ZSTD');
OPTIMIZE table_name FULL;
```

**VACUUM:**

```sql
SET spark.databricks.delta.retentionDurationCheck.enabled = false;   -- Delta
SET spark.databricks.iceberg.retentionDurationCheck.enabled = false; -- Iceberg
```

```sql
REORG TABLE table_name APPLY (PURGE);
```

```sql
SET spark.databricks.delta.vacuum.logging.enabled = true;
SET spark.databricks.iceberg.vacuum.logging.enabled = true;
```

```sql
VACUUM table_name;

ALTER TABLE table_name SET TBLPROPERTIES ('delta.deletedFileRetentionDuration' = '30 days');
```

**REORG TABLE (vollständige Syntax):**

```sql
REORG [ TABLE ] table_name { [ WHERE predicate ] APPLY ( PURGE ) |
                             APPLY ( UPGRADE UNIFORM ( ICEBERG_COMPAT_VERSION = version ) |
                                     CHECKPOINT |
                                     SET PARQUET ( FORMAT_VERSION = version ) ) }
```

```sql
REORG TABLE events WHERE date >= '2022-01-01' APPLY (PURGE);

REORG TABLE events APPLY (UPGRADE UNIFORM(ICEBERG_COMPAT_VERSION=2));

REORG TABLE events APPLY (CHECKPOINT);
```

**FSCK REPAIR TABLE:**

```sql
FSCK REPAIR TABLE t METADATA ONLY DRY RUN;
FSCK REPAIR TABLE t DRY RUN;
FSCK REPAIR TABLE t VERIFY ALL FILES DRY RUN;
```

**GENERATE (Manifest für Presto/Athena):**

```sql
GENERATE symlink_format_manifest FOR TABLE table_name;
```

### Auto-TTL (automatische zeitgesteuerte Zeilenlöschung)

Voraussetzungen: Predictive Optimization aktiviert, `MODIFY`-Berechtigung, Runtime 17.3+, Unity-Catalog-Managed-Delta/-Iceberg/Streaming Tables, Timestamp-Spalte vom Typ `DATE`/`TIMESTAMP`/`TIMESTAMP_NTZ`.

```sql
CREATE TABLE table_name DELETE ROWS <expiration_days> DAYS AFTER <time_column_name>;
```

```sql
ALTER TABLE my_catalog.my_schema.my_table DELETE ROWS 30 DAYS AFTER created_at;
```

```sql
CREATE STREAMING TABLE table_name
DELETE ROWS <expiration_days> DAYS AFTER <time_column_name>
AS SELECT * FROM STREAM(source);
```

```python
from pyspark import pipelines as dp

@dp.table(
  auto_ttl={"timestamp_column": <time_column_name>,
            "expire_in_days": <expiration_days>}
)
def function_name():
  return (query)
```

```python
spark.readStream.format("delta") \
  .option("skipChangeCommits", "true") \
  .table("source_table")
```

```sql
CREATE OR REFRESH STREAMING TABLE my_table AS
SELECT * FROM STREAM(source_table) OPTIONS (skipChangeCommits);
```

```sql
DESCRIBE TABLE EXTENDED table_name;
SHOW TBLPROPERTIES table_name;
```

```sql
ALTER TABLE table_name DROP ROW DELETION;
```

**Formel:** `Gesamtzeit = Expiration_Days + 6 (Buffer) + Retention_Days`. Ziel-Berechnung: `target_expiration_days = target_days - 6 - deletedFileRetentionDuration`.

```sql
WITH tables_with_deletes AS (
  SELECT DISTINCT catalog_name, schema_name, table_name
  FROM system.storage.predictive_optimization_operations_history
  WHERE operation_type = 'DELETE'
    AND timestampdiff(day, start_time, now()) < 7
)
SELECT hist.*
FROM system.storage.predictive_optimization_operations_history AS hist
INNER JOIN tables_with_deletes AS t
  ON hist.catalog_name = t.catalog_name
  AND hist.schema_name = t.schema_name
  AND hist.table_name = t.table_name
WHERE hist.operation_type IN ('DELETE', 'PURGE', 'VACUUM')
  AND timestampdiff(day, hist.start_time, now()) < 7
ORDER BY hist.start_time DESC;
```

```sql
WITH tables_with_deletes AS (
  SELECT DISTINCT table_name
  FROM system.storage.predictive_optimization_operations_history
  WHERE operation_type = 'DELETE'
    AND timestampdiff(day, start_time, now()) < 30
)
SELECT SUM(usage_quantity) AS total_estimated_dbu
FROM system.storage.predictive_optimization_operations_history AS hist
INNER JOIN tables_with_deletes AS t
  ON hist.table_name = t.table_name
WHERE hist.operation_type IN ('DELETE', 'PURGE', 'VACUUM')
  AND hist.usage_unit = 'ESTIMATED_DBU'
  AND timestampdiff(day, hist.start_time, now()) < 30;
```

```sql
DESCRIBE HISTORY table_name;
```

---

## 11. Auto Loader Schema-Modi und JSON-Pfadsyntax für semi-strukturierte Daten

**Einfach erklärt:** Ergänzt Abschnitt 6 (Schema Evolution) und 7.15 (VARIANT) um zwei praktische Werkzeuge für semi-strukturierte Daten, die in den bisherigen Abschnitten nicht vorkamen: die vier expliziten Schema-Evolution-Modi von Auto Loader (inkl. der `_rescued_data`-Spalte) und die Kurzsyntax zum direkten Navigieren in JSON-/VARIANT-Werten per Doppelpunkt, ohne vorher `from_json` mit explizitem Schema aufzurufen.

**Auto Loader Schema-Evolution-Modi** (Option `cloudFiles.schemaEvolutionMode`):

```python
(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "<path-to-schema-location>")
  .option("cloudFiles.schemaEvolutionMode", "addNewColumns")  # Standard: neue Spalten werden automatisch ergänzt, Stream stoppt einmalig zur Schema-Aktualisierung
  # Alternativen: "failOnNewColumns" (Stream schlägt fehl), "rescue" (neue/abweichende Felder landen in _rescued_data), "none" (neue Spalten werden ignoriert)
  .load("<path-to-source-data>"))
```

```python
# Schema-Hinweise für einzelne Spalten (ergänzt/korrigiert die automatische Inferenz)
(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.inferColumnTypes", "true")  # Standard: false (sonst werden alle Spalten als STRING inferiert)
  .option("cloudFiles.schemaHints", "column_name STRING")
  .load("<path-to-source-data>"))
```

Bei Modus `rescue` (bzw. wenn Daten nicht zum inferierten Schema passen) landen nicht parsbare oder unerwartete Felder in einer eigenen `_rescued_data`-Spalte statt Datenverlust zu verursachen.

**JSON-Pfadsyntax (Doppelpunkt-Notation)** — direkter Zugriff auf verschachtelte semi-strukturierte Werte in SQL-Ausdrücken, ohne explizites `from_json`-Schema:

```sql
-- Oberste Ebene eines JSON-/VARIANT-Werts
SELECT raw_column:fulfillment_days FROM my_table;

-- Verschachtelte Felder per Punktnotation
SELECT raw_column:fulfillment_days.shipping.days FROM my_table;

-- Typumwandlung direkt im Pfadausdruck
SELECT raw_column:fulfillment_days.packing::double FROM my_table;

-- Array-Werte per Index extrahieren
SELECT raw_column:clicked_items[0] FROM my_table;
```

---

## 12. Unity Catalog Tables in Snowflake lesen (UniForm + Iceberg REST Catalog)

**Einfach erklärt:** Konkreter Anwendungsfall von UniForm (siehe Abschnitt 7.14 „Iceberg Reads"), der dort noch nicht abgedeckt war: Wie eine per UniForm mit Iceberg-Metadaten versehene Delta-Tabelle direkt aus Snowflake gelesen wird — ohne Datenkopie, über die Unity-Catalog-Iceberg-REST-Catalog-API. Drei Schritte:

**Schritt 1 — UniForm auf der Delta-Tabelle aktivieren** (siehe Abschnitt 7.14 für die genaue `TBLPROPERTIES`-Syntax, z. B. `delta.universalFormat.enabledFormats = 'iceberg'`). Verifikation über die Metadaten-Location im Catalog Explorer.

**Schritt 2 — Unity Catalog als Catalog Integration in Snowflake registrieren:**

```sql
-- In Snowflake: Katalog-Integration gegen die Unity-Catalog-Iceberg-REST-API anlegen
CREATE CATALOG INTEGRATION unity_catalog_integration
  CATALOG_SOURCE = ICEBERG_REST
  TABLE_FORMAT = ICEBERG
  CATALOG_NAMESPACE = '<uc-catalog>.<uc-schema>'
  REST_CONFIG = (
    CATALOG_URI = '<unity-catalog-iceberg-rest-endpoint>',
    ACCESS_DELEGATION_MODE = VENDED_CREDENTIALS
  )
  REST_AUTHENTICATION = (
    TYPE = OAUTH,
    OAUTH_CLIENT_ID = '<service-principal-client-id>',
    OAUTH_CLIENT_SECRET = '<service-principal-client-secret>'
  )
  REFRESH_INTERVAL_SECONDS = 120
  ENABLED = TRUE;
```

Voraussetzung: ein Databricks-Service-Principal mit OAuth-Client-ID/-Secret für die Authentifizierung. `ACCESS_DELEGATION_MODE = VENDED_CREDENTIALS` lässt Unity Catalog temporäre, kurzlebige Storage-Credentials an Snowflake ausstellen (aktuell nur für AWS S3; für ADLS/GCS sind stattdessen External Volumes nötig).

**Schritt 3 — Iceberg-Tabelle in Snowflake referenzieren:**

```sql
CREATE ICEBERG TABLE my_uc_table
  CATALOG = 'unity_catalog_integration'
  CATALOG_TABLE_NAME = '<uc-catalog>.<uc-schema>.<uc-table>'
  AUTO_REFRESH = TRUE;
```

**Status:** Die REST-Catalog-Integration in Snowflake befindet sich in **Public Preview**; die zugrunde liegenden Unity-Catalog-Iceberg-REST-APIs sind bereits **GA**. `AUTO_REFRESH` und manuelles Refresh schließen sich gegenseitig aus (bei Auto-Refresh muss das konfigurierte Intervall abgewartet werden).
