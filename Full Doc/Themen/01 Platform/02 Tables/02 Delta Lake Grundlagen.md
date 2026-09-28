# Delta Lake Grundlagen

Delta Lake ist die optimierte Speicherschicht, die das Fundament für Tabellen im Lakehouse auf Databricks bildet — Standardformat für praktisch alle Tabellen. Dieses Dokument behandelt die Grundkonzepte, ein vollständiges praktisches Tutorial mit allen Kernoperationen, und bekannte Einschränkungen bei S3. Basierend auf offiziellen Databricks-Doku-Seiten (jeweils am Ende jedes Abschnitts referenziert).

## Abschnittsübersicht

1. [Was ist Delta Lake?](#was-ist)
2. [Setup: Tabelle erstellen](#setup)
3. [MERGE / UPSERT](#merge)
4. [Lesen](#lesen)
5. [Schreiben: Append und Overwrite](#schreiben)
6. [UPDATE](#update)
7. [DELETE](#delete)
8. [DESCRIBE HISTORY](#history)
9. [Time Travel](#time-travel)
10. [OPTIMIZE, Liquid Clustering und VACUUM](#wartung)
11. [Einschränkungen auf S3](#s3-limitations)
12. [Zusammenfassung](#zusammenfassung)

---

## <a id="was-ist">1. Was ist Delta Lake?</a>

Delta Lake ist „die optimierte Speicherschicht, die das Fundament für Tabellen in einem Lakehouse auf Databricks bildet." Es handelt sich um Open-Source-Software, die auf Parquet-Datendateien aufbaut und ein dateibasiertes Transaktionslog hinzufügt.

**Kernfunktionen:**

- **ACID-Transaktionen und skalierbares Metadaten-Handling** — erweitert Parquet-Dateien um Fähigkeiten für zuverlässige Datenoperationen im großen Maßstab, inkl. nebenläufigem Lesen/Schreiben durch mehrere Nutzer ohne Konflikte.
- **Spark-Kompatibilität und Streaming:** volle Kompatibilität mit Apache-Spark-APIs, enge Integration mit Structured Streaming — „eine einzige Kopie der Daten für sowohl Batch- als auch Streaming-Operationen."
- **Standardformat:** „Delta Lake ist das Standardformat für alle Operationen auf Databricks. Sofern nicht anders angegeben, sind alle Tabellen auf Databricks Delta-Lake-Tabellen."
- **Offenes Protokoll:** das Transaktionslog folgt „einem klar definierten, offenen Protokoll, das von jedem System zum Lesen des Logs genutzt werden kann."
- **DML-Operationen:** unterstützt `INSERT`, `UPDATE`, `DELETE` und `MERGE` für flexible Datenverwaltung (siehe Abschnitte 3, 6 und 7).
- **Time Travel:** erlaubt das Abfragen und Zurücksetzen auf frühere Datenversionen — für Auditing und Wiederherstellung (siehe Abschnitt 9).
- **Schema Evolution und Enforcement:** setzt ein definiertes Schema zur Sicherung der Datenintegrität durch, erlaubt aber gleichzeitig kontrollierte Schema-Evolution für strukturelle Änderungen, ohne bestehende Workflows zu brechen (siehe [Table Features/13 Type Widening.md](Table%20Features/13%20Type%20Widening.md) und [Table Features/05 Column Mapping.md](Table%20Features/05%20Column%20Mapping.md)).
- **Performance-Optimierung und Skalierbarkeit:** siehe den gesamten Ordner [Performance Optimization](../../Performance%20Optimization/) für Data Skipping, Liquid Clustering, Z-Ordering und weitere Optimierungstechniken.

Databricks hat das Delta-Lake-Protokoll ursprünglich entwickelt und trägt weiterhin zum Open-Source-Projekt bei — die Garantien von Delta Lake bilden die Grundlage für Optimierungen im gesamten Databricks-Ökosystem.

### Quelle

- https://docs.databricks.com/aws/en/delta/

---

## <a id="setup">2. Setup: Tabelle erstellen</a>

Die folgenden Abschnitte demonstrieren die zentralen Delta-Lake-Operationen anhand eines Beispieldatensatzes mit Personendatensätzen — jeweils in Python und SQL.

**Aus CSV-Datei erstellen (Python):**

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

**SQL (über `read_files`):**

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

**`CREATE TABLE LIKE`** (Databricks Runtime 13.3 LTS+) — kopiert Schema und Eigenschaften ohne Daten:

```sql
CREATE TABLE workspace.default.people_10k_prod LIKE workspace.default.people_10k;
```

**Über `DeltaTableBuilder`-API (Python):**

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

### Quelle

- https://docs.databricks.com/aws/en/delta/tutorial

---

## <a id="merge">3. MERGE / UPSERT</a>

**Python:**

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

**SQL:**

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

Zur internen Funktionsweise von `MERGE` (zweistufiger Join-Ansatz) und Performance-Tuning siehe [Partitioning.md](../../Performance%20Optimization/Foundation%20Design/Partitioning.md), Abschnitt 10.3, sowie [Shuffles.md](../../Performance%20Optimization/Code%20Optimization/Shuffles.md), Abschnitt 10 (Low Shuffle Merge).

### Quelle

- https://docs.databricks.com/aws/en/delta/tutorial

---

## <a id="lesen">4. Lesen</a>

```python
people_df = spark.read.table("workspace.default.people_10k")
display(people_df)
```

```sql
SELECT * FROM workspace.default.people_10k;
```

### Quelle

- https://docs.databricks.com/aws/en/delta/tutorial

---

## <a id="schreiben">5. Schreiben: Append und Overwrite</a>

**Append (Python):**

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

**Append (SQL, über Zwischentabelle):**

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

**Overwrite:**

```python
df.write.mode("overwrite").saveAsTable("workspace.default.people_10k")
```

```sql
INSERT OVERWRITE TABLE workspace.default.people_10k
SELECT * FROM workspace.default.people_10k_2;
```

### Quelle

- https://docs.databricks.com/aws/en/delta/tutorial

---

## <a id="update">6. UPDATE</a>

**Python:**

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

**SQL:**

```sql
UPDATE workspace.default.people_10k SET gender = 'F' WHERE gender = 'Female';
UPDATE workspace.default.people_10k SET gender = 'M' WHERE gender = 'Male';
UPDATE workspace.default.people_10k SET gender = 'O' WHERE gender = 'Other';

SELECT * FROM workspace.default.people_10k;
```

### Quelle

- https://docs.databricks.com/aws/en/delta/tutorial

---

## <a id="delete">7. DELETE</a>

**Python:**

```python
from delta.tables import *
from pyspark.sql.functions import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")

deltaTable.delete("age < '18'")
deltaTable.delete(col('age') < '21')

df = spark.read.table("workspace.default.people_10k")
display(df)
```

**SQL:**

```sql
DELETE FROM workspace.default.people_10k WHERE age < '21';

SELECT * FROM workspace.default.people_10k;
```

### Quelle

- https://docs.databricks.com/aws/en/delta/tutorial

---

## <a id="history">8. DESCRIBE HISTORY</a>

**Python:**

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")
display(deltaTable.history())
```

**SQL:**

```sql
DESCRIBE HISTORY workspace.default.people_10k;
```

Ausführliche Behandlung der Historie-Struktur in [Schema und Tabellenhistorie.md](Schema%20und%20Tabellenhistorie.md).

### Quelle

- https://docs.databricks.com/aws/en/delta/tutorial

---

## <a id="time-travel">9. Time Travel</a>

**Über Historie filtern (Python):**

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")
deltaHistory = deltaTable.history()

display(deltaHistory.where("version == 0"))
display(deltaHistory.where("timestamp == '2026-01-05T23:09:47.000+00:00'"))
```

**Direkt per Version/Timestamp (SQL):**

```sql
SELECT * FROM workspace.default.people_10k VERSION AS OF 0;

SELECT * FROM workspace.default.people_10k TIMESTAMP AS OF '2026-01-05T23:09:47.000+00:00';
```

**Über DataFrame-Reader-Optionen (Python):**

```python
df = spark.read.option('versionAsOf', 0).table("workspace.default.people_10k")

df = spark.read.option('timestampAsOf', '2026-01-05T23:09:47.000+00:00').table("workspace.default.people_10k")
display(df)
```

**Als temporäre View (SQL):**

```sql
CREATE OR REPLACE TEMPORARY VIEW people_10k_v0 AS
SELECT * FROM workspace.default.people_10k VERSION AS OF 0;

CREATE OR REPLACE TEMPORARY VIEW people_10k_t0 AS
SELECT * FROM workspace.default.people_10k TIMESTAMP AS OF '2026-01-05T23:09:47.000+00:00';

SELECT * FROM people_10k_v0;
SELECT * FROM people_10k_t0;
```

### Quelle

- https://docs.databricks.com/aws/en/delta/tutorial

---

## <a id="wartung">10. OPTIMIZE, Liquid Clustering und VACUUM</a>

**OPTIMIZE — kleine Dateien zusammenfassen (Bin-Packing/Compaction):** Häufige Schreibvorgänge (viele kleine Appends/Merges) erzeugen viele kleine Dateien, die Lesezugriffe verlangsamen (mehr Dateien = mehr Overhead). `OPTIMIZE` schreibt sie zu größeren, effizienteren Dateien um — die Zeilen selbst ändern sich nicht, nur ihr physisches Layout:

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")
# executeCompaction() ist der `OPTIMIZE` Befehl in Python
deltaTable.optimize().executeCompaction()
```

```sql
OPTIMIZE workspace.default.people_10k;
```

**Liquid Clustering aktivieren:** `CLUSTER BY` legt eine oder mehrere Spalten als Clustering-Keys fest — Delta Lake sortiert/layoutet die Daten dann automatisch nach diesen Spalten, um Data Skipping bei Filtern auf diese Spalten zu beschleunigen (moderner Ersatz für starres `PARTITIONED BY`, ohne dessen Nachteile wie Small-File-Probleme bei niedrig-kardinalen Partitionswerten). `OPTIMIZE FULL` ist danach einmalig nötig: normales `OPTIMIZE` clustert nur neu hinzugekommene Daten inkrementell, `OPTIMIZE FULL` sortiert zusätzlich auch die bereits vorhandenen (alten) Daten nach dem neuen Clustering-Key um:

```python
spark.sql("ALTER TABLE workspace.default.people_10k CLUSTER BY (firstName)")
spark.sql("OPTIMIZE workspace.default.people_10k FULL")
```

```sql
ALTER TABLE workspace.default.people_10k CLUSTER BY (firstName);
OPTIMIZE workspace.default.people_10k FULL;
```

**VACUUM — alte Dateien endgültig löschen:** Delta Lake überschreibt/löscht Zeilen nie sofort physisch — Updates/Deletes/`OPTIMIZE` erzeugen neue Dateien, während die alten Dateien für Time Travel und nebenläufige Leser zunächst erhalten bleiben. `VACUUM` räumt diese nicht mehr referenzierten alten Dateien dauerhaft weg, die älter sind als der Retention-Schwellenwert (Standard: 7 Tage, Tabelleneigenschaft `delta.deletedFileRetentionDuration`). Danach ist Time Travel/Rollback auf Versionen, die diese Dateien brauchten, nicht mehr möglich — der Speicherplatz ist aber freigegeben:

```python
from delta.tables import *

deltaTable = DeltaTable.forName(spark, "workspace.default.people_10k")
deltaTable.vacuum()
```

```sql
VACUUM workspace.default.people_10k;
```

Ausführliche Behandlung dieser drei Operationen (Konfigurationsparameter, Predictive Optimization, Benchmarks) in [Liquid Clustering.md](../../Performance%20Optimization/Foundation%20Design/Liquid%20Clustering.md).

### Quelle

- https://docs.databricks.com/aws/en/delta/tutorial

---

## <a id="s3-limitations">11. Einschränkungen auf S3</a>

### 11.1 Bucket-Versionierung

Delta Lake implementiert eigenes Versioning und eigene Garbage Collection. Aktivierte S3-Bucket-Versionierung führt zu Konflikten, da S3 Dateikopien behält, die Delta Lake als gelöscht betrachtet — einschließlich solcher, die durch `VACUUM` entfernt wurden. Muss Versionierung aktiviert bleiben, empfiehlt Databricks, nur drei Versionen über eine Lifecycle-Policy zu behalten, mit einer Aufbewahrungsdauer von 7 Tagen oder weniger.

### 11.2 Multi-Cluster-Write-Einschränkungen

Delta Lake unterstützt Multi-Cluster-Writes innerhalb eines einzelnen Workspace — diese Garantie gilt jedoch **nicht** über Workspaces hinweg. „Das eventually-consistent-Modell von Amazon S3 kann zu Problemen führen, wenn mehrere Systeme oder Cluster gleichzeitig Daten in derselben Tabelle modifizieren."

**Nicht unterstützt in diesem Modus:**

- Server-Side Encryption mit Customer-Provided Encryption Keys.
- S3-Pfade mit Credentials auf Clustern ohne AWS-Security-Token-Service-Zugriff.

Die Einstellung `spark.databricks.delta.multiClusterWrites.enabled` lässt sich nutzen, um Multi-Cluster-Writes zu deaktivieren — dies „kann jedoch zu Datenverlust oder Datenkorruption führen", falls mehrere Cluster gleichzeitig auf dieselbe Tabelle zugreifen.

### 11.3 Direkte Dateilöschung vermeiden

`rm -rf` zum Löschen von Delta-Lake-Tabellen vermeiden — das erzeugt veraltete Datenprobleme. Stattdessen die vorgesehenen Tabellenlöschverfahren nutzen (`DROP TABLE`, siehe [Tabellenoperationen/DROP, OPTIMIZE, VACUUM und Auto-TTL.md](Tabellenoperationen/DROP%2C%20OPTIMIZE%2C%20VACUUM%20und%20Auto-TTL.md)).

### Quelle

- https://docs.databricks.com/aws/en/delta/s3-limitations

---

## <a id="zusammenfassung">12. Zusammenfassung</a>

- **Delta Lake** ist die Standard-Speicherschicht für praktisch alle Databricks-Tabellen — mit ACID-Transaktionen, skalierbarem Metadaten-Handling und vollständiger Spark-/Structured-Streaming-Kompatibilität.
- Das grundlegende Operations-Set umfasst Tabellenerstellung, Lesen, Append/Overwrite-Schreiben, `UPDATE`, `DELETE`, `MERGE`, `DESCRIBE HISTORY`, Time Travel sowie Wartung über `OPTIMIZE`, Liquid Clustering und `VACUUM` — jeweils konsistent in Python und SQL verfügbar.
- Time Travel erlaubt den Zugriff auf historische Tabellenzustände über `VERSION AS OF`/`TIMESTAMP AS OF` sowie entsprechende DataFrame-Reader-Optionen.
- Auf S3 sind Bucket-Versionierung und Multi-Workspace-Multi-Cluster-Writes mit Vorsicht zu behandeln — direktes Löschen von Dateien über `rm -rf` sollte grundsätzlich vermieden werden.
- Für einen vertieften, quellenübergreifend geprüften Vergleich zu Apache Iceberg (Architektur, Engine-Unterstützung, Anwendungsfälle) siehe [Tabellenkonzepte und Tabellentypen.md](01%20Tabellenkonzepte%20und%20Tabellentypen.md), Abschnitt 3, „Vertiefung: Delta Lake vs. Apache Iceberg".

---

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### CONVERT TO DELTA

Wandelt bestehende Parquet- (oder Iceberg-)Tabellen in Delta-Lake-Tabellen um, ohne die Daten neu zu schreiben — ergänzt Abschnitt 2 (Tabelle erstellen) um den Migrationspfad für bereits vorhandene Daten. Syntax: `CONVERT TO DELTA table_name [NO STATISTICS] [PARTITIONED BY clause]`.

**Registrierte Parquet-Tabelle konvertieren:**

```sql
CONVERT TO DELTA database_name.table_name;
```

**Partitioniertes Parquet-Verzeichnis konvertieren** (Partitionsschema muss explizit angegeben werden):

```sql
CONVERT TO DELTA parquet.`s3://my-bucket/path/to/table` PARTITIONED BY (date DATE);
```

**Iceberg-Tabelle konvertieren** (nutzt die Iceberg-Manifest-Datei für Metadaten):

```sql
CONVERT TO DELTA iceberg.`s3://my-bucket/path/to/table`;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/delta-convert-to-delta

