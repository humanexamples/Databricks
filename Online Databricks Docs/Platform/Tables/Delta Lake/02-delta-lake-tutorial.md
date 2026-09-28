# Tutorial: Delta-Lake-Tabellen erstellen und verwalten

Dieses Tutorial zeigt, wie man Delta-Lake-Tabellen auf Databricks anlegt und pflegt. Es nutzt Beispieldaten aus dem Datensatz "Synthetic Person Records".

## Voraussetzungen

- Zugriff auf eine Compute-Ressource
- Unity-Catalog-Berechtigungen: `USE CATALOG`, `USE SCHEMA`, `CREATE TABLE`
- Der Datensatz muss in ein Unity-Catalog-Volume hochgeladen sein

Alle Beispiele nutzen die Datei `person_10000.csv` und legen die Tabelle `workspace.default.people_10k` an. Alle Tabellen in Databricks sind Delta-Lake-Tabellen, sofern nichts anderes angegeben ist.

## 1. Eine Tabelle erstellen

### Python

```python
from pyspark.sql.types import StructType, StructField, IntegerType, StringType

schema = StructType([
  StructField("id", IntegerType(), True),
  StructField("firstName", StringType(), True),
  StructField("lastName", StringType(), True),
  StructField("gender", StringType(), True),
  StructField("age", IntegerType(), True)])

df = spark.read.format("csv").option("header", True).schema(schema).load("/Volumes/workspace/default/my-volume/person_10000.csv")

# Create the table if it does not exist. Otherwise, replace the existing table.
df.writeTo("workspace.default.people_10k").createOrReplace()

# If you know the table does not already exist, you can use this command instead.
# df.write.saveAsTable("workspace.default.people_10k")

# View the new table.
df = spark.read.table("workspace.default.people_10k")
display(df)
```

### SQL

```sql
%sql
-- Create the table with only the required columns and rename person_id to id.
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

-- View the new table.
SELECT * FROM workspace.default.people_10k;
```

## 2. Upsert in eine Tabelle

Ein Upsert kombiniert Insert und Update über `MERGE INTO`. Erst wird eine Quelltabelle mit neuen Daten angelegt, dann wird sie mit der Zieltabelle gemergt.

### Python

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from delta.tables import DeltaTable

schema = StructType([
  StructField("id", IntegerType(), True),
  StructField("firstName", StringType(), True),
  StructField("lastName", StringType(), True),
  StructField("gender", StringType(), True),
  StructField("age", IntegerType(), True)])

data = [
  (10001, 'Billy', 'Luppitt', 'M', 55),
  (10002, 'Mary', 'Smith', 'F', 98),
  (10003, 'Elias', 'Leadbetter', 'M', 48),
  (10004, 'Jane', 'Doe', 'F', 30),
  (10005, 'Joshua', '', 'M', 90),
  (10006, 'Ginger', '', 'F', 16),]

# Create the source table if it does not exist. Otherwise, replace the existing source table.
people_10k_updates = spark.createDataFrame(data, schema)
people_10k_updates.createOrReplaceTempView("people_10k_updates")

# Merge the source and target tables.
deltaTable = DeltaTable.forName(spark, 'workspace.default.people_10k')
(deltaTable.alias("people_10k")
  .merge(
    people_10k_updates.alias("people_10k_updates"),
    "people_10k.id = people_10k_updates.id")
  .whenMatchedUpdateAll()
  .whenNotMatchedInsertAll()
  .execute())

# View the additions to the table.
df = spark.read.table("workspace.default.people_10k")
df_filtered = df.filter(df["id"] >= 10001)
display(df_filtered)
```

### SQL

```sql
%sql
-- Create the source table if it does not exist. Otherwise, replace the existing source table.
CREATE OR REPLACE TABLE workspace.default.people_10k_updates(
  id INT,
  firstName STRING,
  lastName STRING,
  gender STRING,
  age INT);

-- Insert new data into the source table.
INSERT INTO workspace.default.people_10k_updates VALUES
  (10001, "Billy", "Luppitt", "M", 55),
  (10002, "Mary", "Smith", "F", 98),
  (10003, "Elias", "Leadbetter", "M", 48),
  (10004, "Jane", "Doe", "F", 30),
  (10005, "Joshua", "", "M", 90),
  (10006, "Ginger", "", "F", 16);

-- Merge the source and target tables.
MERGE INTO workspace.default.people_10k AS people_10k
USING workspace.default.people_10k_updates AS people_10k_updates
ON people_10k.id = people_10k_updates.id
WHEN MATCHED THEN
  UPDATE SET *
WHEN NOT MATCHED THEN
  INSERT *;

-- View the additions to the table.
SELECT * FROM workspace.default.people_10k WHERE id >= 10001
```

## 3. Eine Tabelle lesen

### Python

```python
people_df = spark.read.table("workspace.default.people_10k")
display(people_df)
```

### SQL

```sql
%sql
SELECT * FROM workspace.default.people_10k;
```

## 4. In eine Tabelle schreiben

Neue Daten lassen sich per Append hinzufügen oder eine Tabelle komplett überschreiben.

### Python (Append)

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import col

schema = StructType([
  StructField("id", IntegerType(), True),
  StructField("firstName", StringType(), True),
  StructField("lastName", StringType(), True),
  StructField("gender", StringType(), True),
  StructField("age", IntegerType(), True)])

data = [
  (10007, 'Miku', 'Hatsune', 'F', 25)]

# Create the new data.
df = spark.createDataFrame(data, schema)

# Append the new data to the target table.
df.write.mode("append").saveAsTable("workspace.default.people_10k")

# View the new addition.
df = spark.read.table("workspace.default.people_10k")
df_filtered = df.filter(df["id"] == 10007)
display(df_filtered)
```

### SQL (Append)

```sql
%sql
CREATE OR REPLACE TABLE workspace.default.people_10k_new (
  id INT,
  firstName STRING,
  lastName STRING,
  gender STRING,
  age INT);

-- Insert the new data.
INSERT INTO workspace.default.people_10k_new VALUES
  (10007, 'Miku', 'Hatsune', 'F', 25);

-- Append the new data to the target table.
INSERT INTO workspace.default.people_10k
SELECT * FROM workspace.default.people_10k_new;

-- View the new addition.
SELECT * FROM workspace.default.people_10k WHERE id = 10007;
```

### SQL (Overwrite)

```sql
%sql
INSERT OVERWRITE TABLE workspace.default.people_10k SELECT * FROM workspace.default.people_10k_2
```

## 5. Eine Tabelle aktualisieren

### Python

```python
from delta.tables import *
from pyspark.sql.functions import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")

# Declare the predicate and update rows using a SQL-formatted string.
deltaTable.update(
  condition = "gender = 'Female'",
  set = { "gender": "'F'" })

# Declare the predicate and update rows using Spark SQL functions.
deltaTable.update(
  condition = col('gender') == 'Male',
  set = { 'gender': lit('M') })

deltaTable.update(
  condition = col('gender') == 'Other',
  set = { 'gender': lit('O') })

# View the updated table.
df = spark.read.table("workspace.default.people_10k")
display(df)
```

### SQL

```sql
%sql
-- Declare the predicate and update rows.
UPDATE workspace.default.people_10k SET gender = 'F' WHERE gender = 'Female';
UPDATE workspace.default.people_10k SET gender = 'M' WHERE gender = 'Male';
UPDATE workspace.default.people_10k SET gender = 'O' WHERE gender = 'Other';

-- View the updated table.
SELECT * FROM workspace.default.people_10k;
```

## 6. Aus einer Tabelle löschen

### Python

```python
from delta.tables import *
from pyspark.sql.functions import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")

# Declare the predicate and delete rows using a SQL-formatted string.
deltaTable.delete("age < '18'")

# Declare the predicate and delete rows using Spark SQL functions.
deltaTable.delete(col('age') < '21')

# View the updated table.
df = spark.read.table("workspace.default.people_10k")
display(df)
```

### SQL

```sql
%sql
-- Delete rows using a predicate.
DELETE FROM workspace.default.people_10k WHERE age < '21';

-- View the updated table.
SELECT * FROM workspace.default.people_10k;
```

## 7. Tabellenhistorie anzeigen

### Python

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")
display(deltaTable.history())
```

### SQL

```sql
%sql
DESCRIBE HISTORY workspace.default.people_10k
```

## 8. Eine frühere Version abfragen (Time Travel)

### Python (über die Historie)

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")
deltaHistory = deltaTable.history()

# Query using the version number.
display(deltaHistory.where("version == 0"))

# Query using the timestamp.
display(deltaHistory.where("timestamp == '2026-01-05T23:09:47.000+00:00'"))
```

### Python (DataFrameReader)

```python
# Query using the version number.
df = spark.read.option('versionAsOf', 0).table("workspace.default.people_10k")

# Query using the timestamp.
df = spark.read.option('timestampAsOf', '2026-01-05T23:09:47.000+00:00').table("workspace.default.people_10k")
display(df)
```

### SQL

```sql
%sql
-- Query using the version number
SELECT * FROM workspace.default.people_10k VERSION AS OF 0;

-- Query using the timestamp
SELECT * FROM workspace.default.people_10k TIMESTAMP AS OF '2026-01-05T23:09:47.000+00:00';
```

### SQL (mit temporären Views)

```sql
%sql
-- Create a temporary view from version 0 of the table.
CREATE OR REPLACE TEMPORARY VIEW people_10k_v0 AS
SELECT * FROM workspace.default.people_10k VERSION AS OF 0;

-- Create a temporary view from a previous timestamp of the table.
CREATE OR REPLACE TEMPORARY VIEW people_10k_t0 AS
SELECT * FROM workspace.default.people_10k TIMESTAMP AS OF '2026-01-05T23:09:47.000+00:00';

SELECT * FROM people_10k_v0;
SELECT * FROM people_10k_t0;
```

## 9. Eine Tabelle optimieren

`OPTIMIZE` fasst kleine Dateien zusammen und verbessert dadurch die Abfrageleistung.

### Python

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")
deltaTable.optimize().executeCompaction()
```

### SQL

```sql
%sql
OPTIMIZE workspace.default.people_10k
```

## 10. Liquid Clustering nutzen

Liquid Clustering eignet sich besonders für Spalten mit hoher Kardinalität, zum Beispiel `firstName`.

### Python

```python
spark.sql("ALTER TABLE workspace.default.people_10k CLUSTER BY (firstName)")
spark.sql("OPTIMIZE FULL workspace.default.people_10k")
```

### SQL

```sql
%sql
ALTER TABLE workspace.default.people_10k CLUSTER BY (firstName);
OPTIMIZE FULL workspace.default.people_10k;
```

## 11. Vacuum – alte Snapshots aufräumen

`VACUUM` entfernt alte, nicht mehr benötigte Datendateien und reduziert so die Speicherkosten.

### Python

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")
deltaTable.vacuum()
```

### SQL

```sql
%sql
VACUUM workspace.default.people_10k
```
