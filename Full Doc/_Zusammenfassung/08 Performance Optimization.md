# 09 Performance Optimization — Gesamtzusammenfassung

Konsolidierte Übersicht aller 13 Original-Markdown-Dateien im Ordner `09 Performance Optimization\` (3 Unterordner: Foundation Design, The Right Cluster, Code Optimization) mit **allen** enthaltenen Code-Beispielen und einer kurzen, einfachen Einführung pro Thema. Jede Originaldatei bleibt die primäre, ausführliche Quelle — dieses Dokument dient als kompakter Überblick plus vollständige Code-Referenz an einem Ort.

## Inhalt

1. [Spark-Ausführungsarchitektur](#1-spark-ausführungsarchitektur)
2. [Grundlagen der Query-Performance und das Small-File-Problem](#2-grundlagen-der-query-performance-und-das-small-file-problem)
3. [Partitioning](#3-partitioning)
4. [Data Skipping und Tabellenstatistiken](#4-data-skipping-und-tabellenstatistiken)
5. [Liquid Clustering](#5-liquid-clustering)
6. [Z-Ordering](#6-z-ordering)
7. [Disk Cache](#7-disk-cache)
8. [Cluster-Typen und Serverless Compute](#8-cluster-typen-und-serverless-compute)
9. [Instance-Auswahl und Cluster-Sizing](#9-instance-auswahl-und-cluster-sizing)
10. [Shuffles in Spark und Databricks](#10-shuffles-in-spark-und-databricks)
11. [Data Skew in Spark und Databricks](#11-data-skew-in-spark-und-databricks)
12. [Spill in Spark und Databricks](#12-spill-in-spark-und-databricks)
13. [Serialization in Spark und Databricks](#13-serialization-in-spark-und-databricks)
14. [Photon-Performance auf Azure Lasv3-Instanzen (AMD EPYC)](#14-photon-performance-auf-azure-lasv3-instanzen-amd-epyc)

---

## 1. Spark-Ausführungsarchitektur

**Einfach erklärt:** Bevor man Performance optimiert, muss man verstehen, wie eine Spark-/Databricks-Anwendung überhaupt ausgeführt wird. Der **Driver** koordiniert die Arbeit, verteilt sie über **Executors** auf **Worker-Knoten**, und teilt sie in **Jobs** (pro Action), **Stages** (getrennt durch Shuffles) und **Tasks** (kleinste Arbeitseinheit, je eine Datenpartition) ein.

**Grundbegriffe:** Ein **Job** entsteht pro Spark-Action (`save()`, `collect()`), ein **Job** besteht aus mehreren **Stages** (eine neue Stage entsteht meist dort, wo ein Shuffle nötig wird), und jede Stage besteht aus **Tasks** — der kleinsten Ausführungseinheit, gesendet an einen Executor, je einer Datenpartition zugewiesen.

**Cluster-Architektur:** Der **Driver** führt `main()` aus, erstellt den `SparkContext`, plant Tasks über die Executors ein — es gibt immer **genau einen Driver** pro Cluster. Der **Cluster Manager** verteilt Ressourcen. **Worker Nodes** führen Anwendungscode aus. **Executors** sind Prozesse auf einem Worker Node, die Tasks ausführen und Daten (Spark-Partitionen) vorhalten. **Databricks-Besonderheit:** anders als bei generischem Open-Source-Spark läuft bei Databricks immer genau **ein Executor pro Worker-Knoten** — "Worker" und "Executor" werden daher synonym verwendet. Interne Parallelität entsteht über die Anzahl der **Cores/Slots** dieses einen Executors (`spark.executor.cores`), nicht über mehrere Executor-Prozesse.

**Single-Node-Compute:** Der Driver agiert als Master **und** Worker (keine Worker-Knoten) und startet einen Executor-Thread pro logischem Kern minus 1 (reserviert für den Driver-Prozess selbst) — geeignet für Entwicklung/Tests, nicht für Produktion mit hohem Parallelitätsbedarf.

**Adaptive Query Execution (AQE):** Query-Re-Optimierung *während* der Ausführung, basierend auf exakten Laufzeitstatistiken (nach Shuffle-/Broadcast-Exchanges) statt nur Compile-Zeit-Schätzungen. Vier Kernfähigkeiten: (1) dynamischer Join-Strategie-Wechsel (Sort-Merge → Broadcast-Hash), (2) dynamisches Coalescing von Shuffle-Partitionen, (3) dynamische Skew-Join-Optimierung, (4) Empty-Relation-Erkennung/-Propagation. Eingeführt in Spark 3.0 (zunächst deaktiviert), seit **Spark 3.2 standardmäßig aktiviert**; in Databricks ebenfalls standardmäßig an.

**Ohne AQE** durchläuft eine DataFrame-Operation einen rein statischen Pfad: **Logical Plan** → **Catalyst-Optimierung** (Optimizer übersetzt in physischen Plan, unter Berücksichtigung von Regeln/Kostenmodellen) → **Physical Plan** (legt die konkrete Ausführung fest, übersetzt in RDD-Transformationen/-Actions) — bleibt während der gesamten Ausführung fix, ohne Laufzeitkorrekturen.

**Drei generelle Code-Optimierungsempfehlungen** (Grundlage für alle spezifischeren Techniken in diesem Dokument):
1. **DataFrame-/SQL-APIs statt RDD-APIs** — RDD-Operationen umgehen Catalyst und dessen Optimierungen (Prädikat-Pushdown, Spaltenbeschneidung, Join-Reordering).
2. **Unnötige Actions in Produktions-Jobs vermeiden** — `count()`, `display()`, `collect()` erzwingen jeweils volle Plan-Ausführung.
3. **Keine Driver-lastige Berechnung erzwingen** (z. B. single-threaded pandas) — stattdessen **Pandas API on Spark** (`import pyspark.pandas as ps`, seit Spark 3.2 / Databricks Runtime 10.0) für pandas-Syntax mit verteilter Ausführung.

Keine eigenständigen Code-Beispiele in dieser Datei.

---

## 2. Grundlagen der Query-Performance und das Small-File-Problem

**Einfach erklärt:** Vier Grundfaktoren bestimmen, wie schnell eine Query läuft: die **Anzahl gelesener Bytes**, die **Query-Komplexität**, die **Anzahl zugegriffener Dateien** (jeder Dateizugriff hat Overhead) und die verfügbare **Parallelität** (in MPP-Systemen wie Databricks entscheidend). Große Dateien sind effizienter für Scans, kleine Dateien besser für punktuelle Suchen.

**Drei häufige Performance-Engpässe:** (1) **Small-File-Problem** (zu viele winzige Dateien verlangsamen Queries und können Cloud-I/O-Throttling auslösen), (2) **Data Skew** (eine Partition ist deutlich größer, siehe Abschnitt 11), (3) **mehr Daten verarbeiten als nötig** (Data Skipping hilft hier, siehe Abschnitt 4).

**Small-File-Problem im Detail:** Zu viele kleine Dateien erhöhen Lese-Overhead, zu wenige große reduzieren Parallelität. **Über-Partitionierung** ist die häufigste Ursache. Offizieller Schwellenwert: zehntausende Dateien oder mehr, Dateien sollten **nicht kleiner als 8 MB** sein.

**Auto Optimize — zwei zusammenspielende Komponenten:**

**Optimize Write** passt Spark-Partitionsgrößen dynamisch innerhalb desselben Jobs an, Ziel: 128-MB-Dateien je Tabellenpartition. Standardmäßig aktiviert für `MERGE`, `UPDATE`/`DELETE` mit Subqueries; auf SQL-Warehouses/UC-Managed-Tables ab Runtime 13.3 LTS+ auch für `CTAS`/`INSERT`.

```sql
-- Über Tabelleneigenschaft aktivieren
ALTER TABLE table_name SET TBLPROPERTIES (delta.autoOptimize.optimizeWrite = true);
```

```python
# Über Session-Konfiguration aktivieren
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
```

**Auto Compact** läuft nach Job-Abschluss als eigener Job, kompaktiert kleine Dateien auf 128 MB.

```sql
-- Über Tabelleneigenschaft aktivieren
ALTER TABLE table_name SET TBLPROPERTIES (delta.autoOptimize.autoCompact = true);
```

```python
# Über Session-Konfiguration aktivieren
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "auto")
```

Weitere Parameter: `spark.databricks.delta.autoCompact.maxFileSize`/`minNumFiles` (Iceberg-Äquivalente mit `iceberg.`-Präfix). Akzeptierte Werte: `auto` (empfohlen), `legacy` (= `true`), `true` (fest 128 MB), `false`. In `DESCRIBE HISTORY` erscheint Auto Compaction als `OPTIMIZE`-Eintrag mit `operationParameters.auto = true`.

**Automatische Dateigröße nach Tabellengröße** (`delta.targetFileSize`):

| Tabellengröße | Ziel-Dateigröße |
|---|---|
| unter 2,56 TB | 256 MB |
| 2,56–10 TB | linear steigend von 256 MB auf 1 GB |
| über 10 TB | 1 GB |

```sql
-- Feste Ziel-Dateigröße explizit setzen (überschreibt Auto-Tuning; Iceberg: iceberg.targetFileSize)
ALTER TABLE table_name SET TBLPROPERTIES (delta.targetFileSize = '100mb');
```

Wächst die Zielgröße automatisch mit der Tabelle, werden bereits existierende kleinere Dateien **nicht** rückwirkend zusammengeführt — dafür `delta.targetFileSize` explizit setzen oder `OPTIMIZE` planen.

**Predictive File Sizing (KI-gestützt, für UC-Managed-Tables):** Drei Komponenten — Predictive Modeling (ideale Dateigröße aus Tausenden Produktions-Deployments gelernt), Write-Optimierung (6-fache Steigerung der durchschnittlichen Dateigröße), Background Compaction (asynchron, während ungenutzter Cluster-Zeit). Benchmark (1-TB-Data-Warehousing): bis zu **2,2x** Query-Performance-Verbesserung, ideale Dateigröße 64–100 MB. Voraussetzung: Databricks SQL oder Runtime 11.3+, UC Managed Tables.

**Small-File-Problem im Spark UI diagnostizieren:** Scan-/Write-Operatoren im SQL-DAG öffnen, Metrik „number of files read/written" prüfen (Schwellenwert: zehntausende Dateien). Abhilfen: `OPTIMIZE`, Predictive Optimization aktivieren, Datei-Layout überdenken, beim Schreiben zusätzlich Optimized Writes.

**Automatische Runtime-Optimierungen im Überblick** (Standard ab Runtime 10.4 LTS+): Disk Caching (Abschnitt 7), Dynamic File Pruning (Abschnitt 4), Low Shuffle Merge (Abschnitt 10), AQE (Abschnitt 1).

Disk Caching gezielt deaktivieren (nur für Benchmarking, nur Classic Compute):

```python
spark.conf.set('spark.databricks.io.cache.enabled', False)
```

**Weitere empfohlene, nicht standardmäßig aktive Optimierungen:** Table Cloning, Cost-Based Optimizer (Abschnitt 4), native JSON-String-Verarbeitung, Higher-Order-Functions statt UDFs (Abschnitt 13), Range-Join-Tuning (Abschnitt 4), Full-Text-Search-Indexes (Abschnitt 4). **Bewusst zu wählende Verhaltensweisen:** Isolation-Level-Anpassung (`Serializable` vs. `WriteSerializable`, siehe Abschnitt 5), Predictive I/O/Liquid Clustering statt veralteter Bloom-Filter-Indizes.

**Archivierung kalter Daten (Archival Support, Public Preview):** Adressiert Tabellen, deren Dateien über Cloud-Lifecycle-Policies in langsame Storage-Tiers (z. B. S3 Glacier) verschoben wurden — verhindert stille Fehlschläge/unvollständige Ergebnisse durch **frühes Fehlschlagen mit aussagekräftigen Fehlermeldungen**. Voraussetzung: Runtime 13.3 LTS+.

```sql
ALTER TABLE <table_name> SET TBLPROPERTIES(delta.timeUntilArchived = 'X days');
```

```sql
SHOW ARCHIVED FILES FOR table_name [ WHERE predicate ];
```

Wiederherstellung erfolgt **nicht** automatisch durch Databricks — dafür die Restore-APIs des Cloud-Anbieters nutzen (z. B. S3-Restore-Object-APIs); Archival Support erkennt wiederhergestellte Dateien danach automatisch.

---

## 3. Partitioning

**Einfach erklärt:** Partitionierung teilt eine Tabelle physisch nach Spaltenwerten in separate Verzeichnisse auf, damit Spark ganze Verzeichnisse überspringen kann — ist aber die am häufigsten **überstrapazierte** Optimierungstechnik und wird von Databricks für die meisten neuen Tabellen inzwischen **nicht mehr empfohlen** (Liquid Clustering ersetzt sie, siehe Abschnitt 5).

**Sinnvolle Anwendungsfälle:** Isolierung von Daten für getrennte Schemas, GDPR/CCPA-Löschanfragen (ganze Partition löschen), physische Datenisolierung (z. B. SCD Type 2 nach „aktuell"/„nicht aktuell").

**Best Practices, falls benötigt:** niedrigkardinale Spalte wählen, jede Partition **1 GB bis 1 TB** groß, meist nach Datum partitionieren.

| Tabellengröße | Empfehlung |
|---|---|
| unter 1 TB | **nicht** partitionieren |
| 1 TB bis 100 TB | Liquid Clustering statt Partitionierung |
| über 100 TB | Partitionierung kann helfen, Liquid Clustering aber zuerst prüfen |

**Über-Partitionierung (Kernproblem):** führt zu massenhaft kleinen Dateien (mehr Metadaten-Overhead) und Data Skew — ohne die Query-Performance tatsächlich zu verbessern.

**Code-Beispiel — Tabelle partitionieren:**

```python
(df
 .write
 .mode('overwrite')
 .option("overwriteSchema", "true")
 .partitionBy('id')   # nach id partitionieren
 .saveAsTable("iot_data_partitioned")
)
```

```sql
DESCRIBE HISTORY iot_data_partitioned;
```

**Partitionen inspizieren:**

```sql
SHOW PARTITIONS table_name [ PARTITION clause ]
```

```sql
-- Partitionierte Tabelle anlegen und Zeilen einfügen
USE salesdb;
CREATE TABLE customer(id INT, name STRING) PARTITIONED BY (state STRING, city STRING);
INSERT INTO customer PARTITION (state = 'CA', city = 'Fremont') VALUES (100, 'John');
INSERT INTO customer PARTITION (state = 'CA', city = 'San Jose') VALUES (200, 'Marry');
INSERT INTO customer PARTITION (state = 'AZ', city = 'Peoria') VALUES (300, 'Daniel');

-- Alle Partitionen auflisten
SHOW PARTITIONS customer;
SHOW PARTITIONS salesdb.customer;
SHOW PARTITIONS customer PARTITION (state = 'CA', city = 'Fremont');
SHOW PARTITIONS customer PARTITION (state = 'CA');
SHOW PARTITIONS customer PARTITION (city = 'San Jose');
```

```sql
SHOW PARTITIONS iot_data_partitioned;
```

```python
count = spark.sql("SHOW PARTITIONS iot_data_partitioned").count()
print(f"Partition count: {count}")  # Ausgabe: 2500
```

```sql
DESCRIBE HISTORY table_name
```

**Ingestion Time Clustering — die automatische Alternative:** Databricks clustert Daten in **unpartitionierten** Tabellen standardmäßig automatisch nach Ingestion-Zeit — 51 % der partitionierten Tabellen sind nach Datum/Zeit partitioniert, über zwei Drittel der Queries nutzen Datum-/Zeit-Prädikate. Kein Konfigurationsaufwand, bleibt über `DELETE`/`UPDATE`/`MERGE`/`OPTIMIZE` erhalten (via Low Shuffle Merge), kein Ingestion-Overhead. Benchmark: SELECT-Query-Performance im Schnitt **19x** schneller. Standardmäßig aktiv ab Runtime 11.2 / Databricks SQL 2022.35+. **Empfehlung:** Tabellen unter 1 TB nicht nach Datum/Timestamp partitionieren. Bei hochfrequenten `UPDATE`/`MERGE`-Statements zusätzlich Liquid Clustering auf einer der Ingestion-Reihenfolge entsprechenden Spalte einsetzen.

**Unterstützte Partitions-Datentypen:** `Date`, `Timestamp`, `TimestampNTZ`, `Interval`, `String`, `Binary`, `Boolean`, Integer-Varianten, `Float`/`Double`/`Decimal`. **Nicht unterstützt:** komplexe Typen (Structs, Maps, Arrays).

**Technische Rahmenbedingungen:** Transaktionsatomizität ist unabhängig von Partitionsgrenzen; Databricks-Cluster haben **keine** physische Datenlokalität zum Storage (Partitionierung wirkt nur über File-/Directory-Pruning); Hive-Style-Partitionierung ist **kein** Bestandteil des Delta-Lake-Protokolls (immer offizielle APIs nutzen, keine manuelle Verzeichnismanipulation); Column Mapping fügt Partitions-Verzeichnisnamen zufällige Präfixe hinzu.

**Delta-Lake-Best-Practices für partitionierte Tabellen:** UC-Managed-Tables nutzen, Predictive Optimization aktivieren, Liquid Clustering bevorzugen, `CREATE OR REPLACE TABLE` statt `DROP`+`CREATE`. Automatisch von Delta Lake gehandhabt (kein manueller Eingriff nötig): `REFRESH TABLE` überflüssig, automatisches Partitions-Tracking, `WHERE`-Klauseln statt manueller Partitionsangaben, Parquet-Dateien **niemals** manuell verändern.

**MERGE-Performance auf partitionierten Tabellen** — wichtigste Technik zuerst: Suchraum über Partitionsfilter einschränken:

```sql
MERGE INTO events USING updates
ON events.date = current_date() AND events.country = 'USA'
   AND events.id = updates.id
WHEN MATCHED THEN UPDATE SET events.data = updates.data
```

Weitere Techniken: Datei-Kompaktierung, `spark.sql.shuffle.partitions` anpassen, Optimized Writes, automatisches Dateigrößen-Tuning, Low Shuffle Merge.

**Spark-Caching-Warnung:** explizit abgeraten — zunichtemacht Data-Skipping-Vorteile zusätzlicher Filter, kann zu veralteten Daten führen.

**Vertiefung — Sprachreferenz-Syntax:**

```sql
-- Tabellendefinition mit mehreren Partitionsspalten
CREATE TABLE student(university STRING, major STRING, name STRING)
PARTITIONED BY (university, major);

-- Gezieltes Einfügen in eine bestimmte Partition
INSERT INTO student PARTITION(university = 'TU Kaiserslautern') (major, name)
SELECT major, name FROM freshmen;
```

`ALTER TABLE ... ADD/DROP/RENAME PARTITION` (nur Nicht-Delta-Tabellen — **für Delta-Lake-Tabellen nicht unterstützt**, dort automatisch gehandhabt):

```sql
-- Beispieltabelle (nicht Delta) mit Datumspartition
CREATE TABLE log(date DATE, id INT, event STRING) USING CSV PARTITIONED BY (date);

ALTER TABLE log ADD PARTITION(date = DATE'2021-09-10');
ALTER TABLE log DROP PARTITION(date = DATE'2021-09-10');
ALTER TABLE log PARTITION(date = DATE'2021-09-10') RENAME TO PARTITION(date = DATE'2021-09-11');
ALTER TABLE log RECOVER PARTITIONS;
```

```sql
SHOW PARTITIONS salesdb.customer;
SHOW PARTITIONS customer PARTITION (state = 'CA');
```

---

## 4. Data Skipping und Tabellenstatistiken

**Einfach erklärt:** Data Skipping vermeidet das Lesen von Dateien, die für eine Query offensichtlich irrelevant sind — basierend auf Statistiken (Min/Max, Null-Counts, Zeilenanzahl), die Databricks beim Schreiben automatisch je Datei sammelt, **ohne** die Datei jemals zu öffnen. Funktioniert am besten, wenn Daten natürlich nach den gefilterten Spalten geclustert sind (siehe Z-Ordering/Liquid Clustering).

**Wie es funktioniert:** Beim Schreiben sammelt Spark Statistiken pro Datei (standardmäßig für die ersten 32 Spalten), gespeichert im Transaktionslog, nicht in den Dateien selbst. Bei einem Filter (`WHERE date = '2026-07-01'`) prüft Spark zuerst die Statistiken — überlappt der Min/Max-Bereich einer Datei nicht, wird sie vollständig übersprungen.

```sql
SELECT
    input_file_name() AS "file_name",
    min(col) AS "col_min",
    max(col) AS "col_max"
FROM table
GROUP BY input_file_name()
```

```sql
-- Metadaten-only-Query, muss keine Dateien lesen, wenn col Statistiken hat
SELECT max(col) FROM table
```

**Einschränkung bei Timestamp-/String-Spalten:** wegen Präzisions-/Truncation-Problemen nicht immer exakt — Empfehlung: Statistiken für lange String-Spalten vermeiden.

**Spaltenanzahl-Grenze:** External Tables: standardmäßig erste 32 Spalten. UC Managed Tables: über Predictive Optimization intelligent gewählt, ohne 32-Spalten-Grenze.

| Eigenschaft | Standard | Zweck |
|---|---|---|
| `delta.dataSkippingNumIndexedCols` | 32 | Anzahl indizierter Spalten (`-1` = alle) |
| `delta.dataSkippingStatsColumns` (ab Runtime 13.3 LTS) | — | konkrete Spaltenliste, hat Vorrang |

```sql
SET spark.databricks.delta.properties.defaults.dataSkippingNumIndexedCols = 3;
ALTER TABLE table_name CHANGE COLUMN col AFTER col32;
ALTER TABLE table_name SET TBLPROPERTIES('delta.dataSkippingStatsColumns' = 'col1, col2, col3');
ALTER TABLE table_name SET TBLPROPERTIES('iceberg.dataSkippingStatsColumns' = 'col1, col2, col3');
```

Änderungen wirken **nicht rückwirkend** auf bereits geschriebene Daten.

**Filterreihenfolge:** Partition Filters → Data Filters (Data-Skipping-Statistiken) → Pushed Filters (Dateiformat-Ebene, z. B. Parquet-Row-Group-Filterung).

**Statistiken abfragen und neu berechnen:**

```sql
ANALYZE TABLE table_name [ PARTITION clause ]
    COMPUTE [ DELTA ] STATISTICS [ NOSCAN | FOR COLUMNS col1 [, ...] | FOR ALL COLUMNS ]

ANALYZE TABLES [ { FROM | IN } schema_name ] COMPUTE STATISTICS [ NOSCAN ]
```

```sql
ANALYZE TABLE students COMPUTE STATISTICS;
ANALYZE TABLE students COMPUTE STATISTICS NOSCAN;
ANALYZE TABLE mytable COMPUTE STATISTICS FOR ALL COLUMNS;
ANALYZE TABLE students COMPUTE STATISTICS FOR COLUMNS name;
ANALYZE TABLE some_delta_table COMPUTE DELTA STATISTICS;
ANALYZE TABLES IN school_schema COMPUTE STATISTICS NOSCAN;
ANALYZE TABLES COMPUTE STATISTICS;
```

```sql
SHOW STATISTICS [ { FROM | IN } ] table_name
    [ FOR COLUMNS column_name [, ...] | FOR ALL COLUMNS ]
    AS JSON
```

```sql
SHOW STATISTICS FROM customer AS JSON;
SHOW STATISTICS FROM customer FOR COLUMNS cust_id, name AS JSON;
SHOW STATISTICS FROM customer FOR ALL COLUMNS AS JSON;
```

**Drei Statistik-Quellen für Sparks Zeilenschätzungen:** Data Source (Parquet-Metadaten), Catalog (via `ANALYZE TABLE`), Runtime (AQE, zur Laufzeit). Inspektion über `DESCRIBE EXTENDED table_name [column_name]`, `EXPLAIN COST`/`DataFrame.explain(mode="cost")`, oder das SQL-Tab der Spark-UI (`Statistics(..., isRuntime=true)`).

**Predictive Optimization für Statistiken:** sammelt Statistiken beim Schreiben über Photon-fähiges Compute; löst `ANALYZE` automatisch im Hintergrund aus, sobald Statistiken veralten. Wählt intelligent relevante Spalten über die 32-Spalten-Grenze hinaus. **22 % durchschnittliche Performance-Steigerung.**

**Predictive I/O:** Beschleunigte Lesevorgänge (Deep-Learning-basierte Zugriffspfad-Optimierung, Voraussetzung: Photon, Serverless/Pro-SQL-Warehouses oder Photon-Cluster ab Runtime 11.3 LTS+) und beschleunigte Updates (nutzt Deletion Vectors statt vollständiger Datei-Neuschreibvorgänge, Voraussetzung: aktivierte Deletion Vectors, Runtime 14.0+ empfohlen).

**Bloom-Filter-Indizes (veraltet):** abgelöst durch Predictive I/O und Liquid Clustering.

```sql
DROP BLOOMFILTER INDEX ON TABLE table_name;
-- anschließend VACUUM ausführen
```

**Dynamic File Pruning (DFP):** erweitert statisches File Pruning um dynamische Filter, die von der Build-Seite eines Joins erzeugt und in die Scan-Operation gepusht werden — ermöglicht Star-Schema-Queries, von dateiweisem Skipping zu profitieren, ohne Join-Werte zur Kompilierzeit zu kennen.

**Voraussetzungen:** innere Tabelle im Delta-Format, Join-Typ `INNER`/`LEFT-SEMI`, Strategie `BROADCAST HASH JOIN`, Tabelle über Datei-Schwellenwert (Standard 1.000 Dateien).

| Parameter | Standard | Zweck |
|---|---|---|
| `spark.databricks.optimizer.dynamicFilePruning` | `true` | aktiviert/deaktiviert DFP |
| `spark.databricks.optimizer.deltaTableSizeThreshold` | 10 GB | Mindesttabellengröße |
| `spark.databricks.optimizer.deltaTableFilesThreshold` | 10 (aktuell) bzw. 1.000 (ursprünglich) | Mindestanzahl Dateien |

`MERGE`/`UPDATE`/`DELETE` erfordern Photon für DFP; `SELECT` profitiert mit Photon umfassender. Benchmark (TPC-DS 1 TB): bis zu **~8x** Speedup, 36/103 Queries mit 2x+, ein Beispiel von 8,6 Mrd. auf 66 Mio. gescannte Zeilen (>99 % Reduktion), 10s → <1s.

**Zusammenspiel mit Disk Cache:** Data Skipping reduziert die Anzahl zu lesender Dateien, der Disk Cache beschleunigt zusätzlich wiederholte Lesevorgänge der verbleibenden Dateien (siehe Abschnitt 7).

**Range Join Optimization:** beschleunigt „Point-in-Interval"- (`points.p BETWEEN ranges.start AND ranges.end`) und „Interval-Overlap"-Joins (`r1.start < r2.end AND r2.start < r1.end`). Automatische Bin-Größen-Ableitung per Sampling, oder manuell:

```sql
SELECT /*+ RANGE_JOIN(points, 10) */ *
FROM points JOIN ranges
ON points.p >= ranges.start AND points.p < ranges.end;
```

```sql
SET spark.databricks.optimizer.rangeJoin.binSize = 5
```

```sql
SET spark.databricks.optimizer.autoRangeJoin.enabled = false;
```

```python
events.hint("range_join", 60).join(minutes,
  on=[events.event_start < minutes.minute_end,
      minutes.minute_start < events.event_end]).show()
```

```sql
SELECT map_from_arrays(
  ARRAY(0.5, 0.9, 0.99, 0.999, 0.9999),
  APPROX_PERCENTILE(end::DOUBLE - start::DOUBLE,
    ARRAY(0.5, 0.9, 0.99, 0.999, 0.9999))
) AS bin_sizes
FROM ranges;
```

**Spatial Joins:** Databricks SQL Serverless + Runtime 17.3 kombinieren R-Tree-Indizierung, Photon-optimierte räumliche Joins und Range-Join-Optimierung automatisch — bis zu **17x** schnellere räumliche Joins gegenüber Apache Sedona auf Classic Clusters.

**Full-Text-Search-Indexes (Beta):** beschleunigt Lookups über Textspalten in Delta/Iceberg-Tabellen. Voraussetzungen: Runtime 18.2+, `MODIFY`+`CREATE TABLE`-Berechtigung, Row Tracking aktiviert, Spaltentyp `STRING`/`VARIANT`/`STRUCT`/`ARRAY`. Max. 4 Indizes/Tabelle.

```sql
CREATE SEARCH INDEX log_idx ON logs (message, error_detail);
```

```sql
CREATE SEARCH INDEX [IF NOT EXISTS] index_name
ON table_name (column_name [, column_name ...])
[OPTIONS (option_key = option_value [, ...])]
```

```sql
-- N-Gram-Tokenizer (Standard, Substring-Matching)
CREATE SEARCH INDEX log_ngram_idx
ON logs (message)
OPTIONS (tokenizer = 'ngram', ngram_size = 4);

-- Split-Tokenizer (Wort-Matching)
CREATE SEARCH INDEX log_word_idx
ON logs (message)
OPTIONS (tokenizer = 'split', min_token_length = 2);
```

```sql
-- Case-insensitive Substring-Suche
SELECT * FROM logs
WHERE isearch(message, 'connection refused');

-- Mehrspaltige Substring-Suche
SELECT * FROM logs
WHERE search(message, error_detail, '550e8400-e29b-41d4-a716-446655440000');

-- Wort-Suche (beliebige Reihenfolge)
SELECT * FROM audit_logs
WHERE search(message, 'user admin login', mode => 'word');
```

```sql
DESCRIBE INDEX log_idx;
REFRESH INDEX log_idx;
REFRESH INDEX log_idx FULL;
DROP INDEX log_idx;
DROP INDEX IF EXISTS log_idx;
```

Indizes aktualisieren sich **nicht automatisch** — regelmäßige `REFRESH INDEX`-Läufe nötig; Query-Korrektheit bleibt aber immer erhalten (Kombination aus Index + Tabellenscan für nicht indizierte Daten).

**Cost-Based Optimizer (CBO):** verbessert Query-Pläne bei Multi-Join-Queries, basiert auf denselben Tabellenstatistiken. `EXPLAIN` zeigt `rowCount`-Schätzungen; Spark-SQL-UI zeigt `"rows output: X est: Y"` zur Genauigkeitsprüfung. Standardmäßig aktiviert:

```python
spark.conf.set("spark.sql.cbo.enabled", "false")
```

**Vertiefung — weitere Statistik-Befehle:**

```sql
ANALYZE TABLE students COMPUTE STATISTICS FOR COLUMNS name;
```

```sql
-- Storage-Metriken für Unity-Catalog-Tabellen
ANALYZE TABLE main.my_schema.my_table COMPUTE STORAGE METRICS;

-- Für sehr große Tabellen (100.000+ Dateien): über Cloud-Storage-Inventory
ANALYZE TABLE main.my_schema.my_table COMPUTE STORAGE METRICS
USING INVENTORY LOCATION 's3://your-destination-bucket/your-prefix/'
CONF 'databricks-inventory-list-config';
```

```sql
-- Nur manuell erstellte Statistiken entfernen (Standard)
ANALYZE TABLE main.sales.orders DROP STATISTICS;
-- Nur automatisch erzeugte Statistiken entfernen
ANALYZE TABLE main.sales.orders DROP AUTO STATISTICS;
-- Beide Arten entfernen
ANALYZE TABLE main.sales.orders DROP ALL STATISTICS;
```

```sql
CREATE TABLE customer(cust_id INT, name STRING, state STRING) USING parquet;
INSERT INTO customer VALUES (100, 'Mike', 'AR'), (200, 'Jane', 'CA');
ANALYZE TABLE customer COMPUTE STATISTICS FOR ALL COLUMNS;

SHOW STATISTICS FROM customer AS JSON;
```

---

## 5. Liquid Clustering

**Einfach erklärt:** Liquid Clustering ist Databricks' moderner Ersatz für Hive-Style-Partitionierung und Z-Ordering. Statt starrer Partitionsgrenzen ist das Ziel eine bestimmte **Dateigröße** — Databricks entscheidet intelligent, welche Datenbereiche kombiniert werden, damit Dateigrößen ungefähr gleich bleiben. Das reduziert Data Skew drastisch, und Clustering-Keys lassen sich **jederzeit ändern, ohne bestehende Daten neu zu schreiben**. Unterstützt Delta Lake und Apache Iceberg, sowie Streaming Tables und Materialized Views.

**Partitioning vs. Clustering:** Partitionierung schreibt Daten physisch in separate Verzeichnisse (`/date=2026-01-01/`) — starr, riskiert Small-File-Problem bei falscher Spaltenwahl. Clustering kolokiert zusammengehörige Daten *innerhalb* und *über* Dateien hinweg, ohne Verzeichnisaufteilung — funktioniert bei jeder Kardinalität, auch hochkardinal.

| Aspekt | Partitioning | Clustering |
|---|---|---|
| Physisches Layout | separate Verzeichnisse je Wert | kolokiert, keine Verzeichnisaufteilung |
| Am besten für | niedrigkardinale Spalten | jede Kardinalität |
| Flexibilität | starr | Keys jederzeit neu definierbar |
| Small-File-Risiko | hoch bei Über-Partitionierung | niedrig, automatisch verwaltet |
| Databricks-Empfehlung | Legacy, nützlich bei sehr großen Tabellen | Standard für neue Tabellen |

**Vorteile:** beste Performance von Haus aus (Clustering beim Schreiben), konsistenteste Data-Skipping-Ergebnisse (immun gegen Skew), minimale Write-Amplification (echtes inkrementelles Optimieren), Row Level Concurrency, reduzierter kognitiver Overhead, inkrementell, flexibel, selbstoptimierend mit `CLUSTER BY AUTO`.

**Clustering-Keys wählen:** bis zu **4 Keys**, basierend auf häufig gefilterten Spalten; Spaltenreihenfolge irrelevant. Bei Tabellen unter 10 TB können mehr Keys Einzelspalten-Filter-Performance beeinträchtigen. Hochkardinale Spalten sind ausdrücklich geeignet. Korrelierte Spalten: nur eine als Key aufnehmen.

**Unterstützte Typen:** `Date`, `Timestamp`, `TimestampNTZ`, `String`, `Integer`, `Long`, `Short`, `Byte`, `Float`, `Double`, `Decimal`, Struct-Felder via Punktnotation. **Nicht unterstützt:** `StructType`, `MapType`, `ArrayType`.

**Tabellen erstellen und konfigurieren:**

```sql
-- Leere Tabelle
CREATE TABLE table1 (col0 INT, col1 STRING) CLUSTER BY (col0);
-- Aus bestehenden Daten
CREATE TABLE table2 CLUSTER BY (col0) AS SELECT * FROM table1;
-- Schema übernehmen (inkl. Clustering-Konfiguration)
CREATE TABLE table3 LIKE table1;
```

```python
# DeltaTable-API
(DeltaTable.create()
  .tableName("table1")
  .addColumn("col0", dataType="INT")
  .addColumn("col1", dataType="STRING")
  .clusterBy("col0")
  .execute())

# DataFrame-Write
df = spark.read.table("table1")
df.write.clusterBy("col0").saveAsTable("table2")

# writeTo-API (DataFrameWriterV2)
df.writeTo("table1").using("delta").clusterBy("col0").create()
```

```sql
ALTER TABLE <table_name> CLUSTER BY (<clustering_columns>);
```

`CLUSTER BY`-Klausel im Detail:

```sql
CLUSTER BY { ( column_name [, ...] ) | AUTO | NONE }
```

**Streaming-Unterstützung** (ab Runtime 16.4 LTS+):

```sql
CREATE TABLE table1 (col0 STRING, col1 DATE, col2 BIGINT) CLUSTER BY (col0, col1);
```

```python
(spark.readStream.table("source_table")
  .writeStream
  .clusterBy("column_name")
  .option("checkpointLocation", checkpointPath)
  .toTable("target_table"))
```

```python
# Mit Automatic Clustering
(spark.readStream.table("source_table")
  .writeStream
  .option("clusterByAuto", "true")
  .option("checkpointLocation", checkpointPath)
  .toTable("target_table"))
```

**Größenschwellenwerte beim Schreiben (Clustering on Write):**

| Anzahl Keys | Unity-Catalog-Schwellenwert | Andere Delta-Tabellen |
|---|---|---|
| 1 | 64 MB | 256 MB |
| 2 | 256 MB | 1 GB |
| 3 | 512 MB | 2 GB |
| 4 | 1 GB | 4 GB |

**Bestehende Tabellen konvertieren** (ab Runtime 18.1+):

```sql
ALTER TABLE <table_name> REPLACE PARTITIONED BY WITH CLUSTER BY [(columns) | AUTO]
```

```sql
ALTER TABLE t1 REPLACE PARTITIONED BY WITH CLUSTER BY (day, id);
OPTIMIZE t1;
```

```sql
ALTER TABLE t2 REPLACE PARTITIONED BY WITH CLUSTER BY AUTO;
```

Konvertiert bestehende Daten standardmäßig **nicht** rückwirkend (`OPTIMIZE FULL` nötig). Nicht unterstützt: Streaming Tables/Materialized Views in Lakeflow-Pipelines, Delta-Sharing-Tabellen mit Partition-Filterung.

**Nebenläufige Operationen während der Konvertierung:**

| Workload-Typ | Lesevorgänge | Schreibvorgänge |
|---|---|---|
| Batch | keine Downtime (alle Versionen) | keine Downtime ab Runtime 15.4+ |
| Streaming | Neustart erforderlich, kein Datenverlust | Stream-Neustart ohne Verlust committeter Daten |

**Konvertierung von Timestamp-partitionierten Tabellen:**

```sql
SET spark.databricks.delta.liquidConversion.statsGeneration.enabled = false;
ALTER TABLE t1 REPLACE PARTITIONED BY WITH CLUSTER BY (timestamp_col, id);
ANALYZE TABLE t1 COMPUTE DELTA STATISTICS;
```

**Rollback (offiziell nicht unterstützt):**

```sql
ALTER TABLE my_table UNSET TBLPROPERTIES ('delta.liquid.hierarchicalClusteringColumns');
ALTER TABLE my_table CLUSTER BY NONE;
CREATE OR REPLACE TABLE my_table PARTITIONED BY (<partition_columns>)
  AS SELECT * FROM my_table;
```

**Clustering triggern:**

```sql
OPTIMIZE table_name;
-- Erzwungenes Re-Clustering (ab Runtime 16.4 LTS+)
OPTIMIZE table_name FULL;
-- Partielles Re-Clustering (ab Runtime 18.1+)
OPTIMIZE events FULL WHERE event_date >= '2025-01-01';
```

```sql
DESCRIBE TABLE table_name;
DESCRIBE DETAIL table_name;
ALTER TABLE table_name CLUSTER BY (new_column1, new_column2);
ALTER TABLE table_name CLUSTER BY NONE;
```

**Diagnose:** `DESCRIBE DETAIL` liefert `clusteringColumns`; bei `AUTO` zusätzlich `clusterByAuto = true` (auch via `SHOW TBLPROPERTIES`). `DESCRIBE HISTORY` zeigt `REORG`/`UPGRADE PROTOCOL`/`REPLACE PARTITIONED BY WITH CLUSTER BY`-Einträge. Im Catalog-Explorer-History-Tab zeigt „Not applied" bei `AUTO LIQUID` den Skip-Grund. Query Profile zeigt gepruntes Prozent je Scan-Metrik. `system.storage.predictive_optimization_operations_history` liefert `AUTO_CLUSTERING_COLUMN_SELECTION`/`CLUSTERING`-Einträge mit DBU-Schätzung.

**Automatic Liquid Clustering (`CLUSTER BY AUTO`)** — Public Preview seit **5. März 2025**. Drei Schritte: Telemetrie-Analyse (Query-Scan-Statistiken), Workload-Modellierung (Predictive Optimization simuliert vergangene Queries), Kosten-Nutzen-Optimierung (nur Änderungen mit klarem Vorteil werden angewendet). Keine feste Re-Evaluierungs-Frequenz dokumentiert.

```sql
-- Bei Tabellenerstellung
CREATE OR REPLACE TABLE table1 (column01 INT, column02 STRING) CLUSTER BY AUTO;
-- Auf bestehender Tabelle aktivieren
ALTER TABLE table1 CLUSTER BY AUTO;
-- Hints setzen, bevor AUTO aktiviert wird
ALTER TABLE table1 CLUSTER BY (c1, c2);
ALTER TABLE table1 CLUSTER BY AUTO;
-- Deaktivieren
ALTER TABLE table1 CLUSTER BY NONE;
```

Beispielrechnung: ohne Clustering 5/10 Dateien gescannt (50 % Pruning), mit Clustering nur 1 Datei (90 % Pruning). **Kundenergebnisse:** Healthrise bis zu **10x** schnellere Queries auf allen Gold-Tabellen; CFC Underwriting sinkende Compute-Kosten trotz Datenwachstum.

**Nachteile:** nur UC-Managed-Tables (Delta ab Runtime 15.4 LTS, Iceberg erst ab Managed v3/Runtime 18.0+, **v2 nicht unterstützt**); setzt Predictive Optimization voraus (separate Serverless-Kosten); wählt evtl. keine Keys bei zu kleiner Tabelle; keine feste Re-Evaluierungs-Frequenz; DataFrame-API `clusterByAuto` nur im `overwrite`-Modus; `CREATE OR REPLACE` **ohne** `CLUSTER BY AUTO` schaltet Auto-Modus ab.

```sql
-- Von AUTO zu expliziten Spalten wechseln
ALTER TABLE table1 CLUSTER BY (column01, column02);
-- Von expliziten Spalten (oder ohne Clustering) zu AUTO wechseln
ALTER TABLE table1 CLUSTER BY AUTO;
```

**Isolation Levels:** `Serializable` (stärkstes Level, committete Schreiboperationen + alle Lesevorgänge serialisierbar) vs. `WriteSerializable` (Standard, nur Schreiboperationen serialisierbar — guter Kompromiss aus Konsistenz und Verfügbarkeit).

```sql
ALTER TABLE <table-name> SET TBLPROPERTIES ('delta.isolationLevel' = 'Serializable');
```

**Row-Level Concurrency:** reduziert Schreibkonflikte durch Erkennung auf Zeilenebene statt Dateiebene, via Deletion Vectors + Row Tracking. Automatisch aktiviert bei: Runtime 14.2 LTS+, unpartitionierte Quelltabelle, aktivierte Deletion Vectors. **Partitionierte Tabellen: nicht unterstützt.** Impact: 6.500+ Kunden, über 110 Mrd. Konflikte automatisch aufgelöst (>90 % Reduktion).

**Sechs Exception-Typen bei Schreibkonflikten:** `ConcurrentAppendException`, `ConcurrentDeleteReadException`, `ConcurrentDeleteDeleteException`, `MetadataChangedException`, `ConcurrentTransactionException`, `ProtocolChangedException`.

**Tabellenstatistiken für Query-Optimierung:**

```sql
ANALYZE TABLE mytable COMPUTE STATISTICS FOR ALL COLUMNS;
```

**Predictive Optimization:** automatisiert `OPTIMIZE` (inkl. inkrementelles Liquid Clustering, **kein** Z-Ordering), `VACUUM` (Retention via `delta.deletedFileRetentionDuration`, Standard 7 Tage), `ANALYZE`. Voraussetzungen: Premium-Plan+, SQL-Warehouses/Runtime 12.2 LTS+, nur UC-Managed-Tables. Standard für Konten nach dem 11.11.2024; Rollout für bestehende Konten bis **August 2026**.

```sql
ALTER CATALOG [catalog_name] { ENABLE | DISABLE | INHERIT } PREDICTIVE OPTIMIZATION;
ALTER { SCHEMA | DATABASE } schema_name { ENABLE | DISABLE | INHERIT } PREDICTIVE OPTIMIZATION;
ALTER TABLE table_name { ENABLE | DISABLE | INHERIT } PREDICTIVE OPTIMIZATION;
```

```sql
DESCRIBE (CATALOG | SCHEMA | TABLE) EXTENDED name;
```

```sql
-- Skip-Gründe (ab Runtime 18 LTS+)
DESCRIBE TABLE EXTENDED catalog_name.schema_name.table_name AS JSON;
```

**VACUUM im Detail:**

```sql
VACUUM table_name;
VACUUM table_name DRY RUN;
-- LITE-Modus (ab Runtime 16.4 LTS+)
VACUUM table_name LITE;
VACUUM table_name FULL;
REORG TABLE table_name APPLY (PURGE);
```

Standard-Retention: **7 Tage**. Predictive Optimization im Maßstab (2025/2026): Exabytes entfernt, hunderte PB kompaktiert, Millionen Tabellen mit Automatic Liquid Clustering. VACUUM bis zu **6x schneller**, **4x niedrigere Kosten**; Stats-on-Write **7–10x performanter** als nachträgliches `ANALYZE`.

**Praxisbeispiel Arctic Wolf** (Security-Operations, >1 Billion Events/Tag, 3,8+ PB): Dateianzahl 4 Mio. → 2 Mio.; Query-Zeit **~50 % schneller** (teils ~90 %); 90-Tage-Queries **51s → 6,6s** (~8,7x); Datenaktualität von Stunden auf Minuten.

**GA seit 22. Mai 2024** (ab Runtime 15.2). Adoption: 3.000+ aktive monatliche Kunden, 200+ PB/Monat geschrieben. Performance: **2–12x** schnellere Lesevorgänge, **7x schnellere Schreibzeiten** gegenüber Partitionierung+ZORDER. Delta-Lake-3.0-Benchmark: **2,5x schnelleres Clustering** relativ zu Z-Order.

**Kompatibilität:**

| Aspekt | Details |
|---|---|
| Delta-Lake-Tabellen | ab Runtime 15.4 LTS |
| Apache-Iceberg-Tabellen | Public Preview ab Runtime 16.4 LTS+ |
| Managed Iceberg v3 | unterstützt Automatic Liquid Clustering (ab Runtime 18.0+) |
| Protokoll | Writer Version 7, Reader Version 3 — **Downgrade nicht möglich** |

**Feature-Aktivierung überschreiben:**

```sql
-- Beispiel: Deletion Vectors deaktiviert lassen
ALTER TABLE table_name SET TBLPROPERTIES ('delta.enableDeletionVectors' = false);
ALTER TABLE table_name CLUSTER BY (clustering_columns);
```

**Streaming-Eager-Clustering:**

```sql
-- (als Spark-Konfiguration, nicht SQL-DDL)
spark.databricks.delta.liquid.eagerClustering.streaming.enabled = true
```

**Apache Iceberg über externe Engines:**

```sql
CREATE OR REPLACE TABLE main.schema.icebergTable PARTITIONED BY c1;
ALTER TABLE main.schema.icebergTable DROP PARTITION FIELD c2;
ALTER TABLE main.schema.icebergTable ADD PARTITION FIELD c2;
CREATE OR REPLACE TABLE main.schema.icebergTable PARTITIONED BY (bucket(c1, 10));
```

**Wichtige Limitierungen:** inkompatibel mit klassischer Partitionierung/ZORDER; max. 4 Keys; Runtime 15.1 und darunter: kein gefiltertes/gejointes/aggregiertes Clustering-on-Write; Iceberg v2: kein Row-Level Concurrency; DataFrame-APIs: Clustering nur bei Erstellung/`overwrite`.

**Zwei neuere Funktionen (Stand 2026):** Pipelines mit `CLUSTER BY AUTO` entfernen Clustering-Spalten automatisch, wenn diese aus dem Materialized-View-Schema entfernt werden. AUTO-CDC-Zieltabellen unterstützen jetzt Liquid Clustering, aktivierbar per Primary Key oder über die Ingestion-Spec. Das verbessert die Query-Performance auf CDC-Zieltabellen, ohne dass Clustering manuell gepflegt werden muss.

**Vertiefung — Sprachreferenz:**

```sql
CREATE TABLE t(a INT, b STRING) CLUSTER BY (a);
ALTER TABLE t CLUSTER BY (a, b);
OPTIMIZE t;
ALTER TABLE t CLUSTER BY NONE;
```

---

## 6. Z-Ordering

**Einfach erklärt:** Z-Ordering organisiert Tabellendaten physisch nach einer oder mehreren Spalten, sodass **ähnliche Werte in denselben Dateien landen** — das macht Data Skipping deutlich effektiver. Obwohl Databricks für neue Tabellen jetzt Liquid Clustering empfiehlt, ist Z-Ordering weiterhin relevant, u. a. für bestehende Tabellen.

**Wie es wirkt:** Schritt 1 — Daten werden physisch nach der gewählten Spalte organisiert. Schritt 2 — jede Datei zeichnet Min/Max-Werte in ihren Metadaten auf. Eine Query, die nach der Z-geordneten Spalte filtert, kann dann gezielt nur die relevante Datei öffnen, statt alle zu prüfen.

**Syntax:**

```sql
OPTIMIZE table_name [FULL] [WHERE predicate] [ZORDER BY (col_name1 [, ...])]
```

```sql
OPTIMIZE events
WHERE date >= current_timestamp() - INTERVAL 1 day
ZORDER BY (eventType);
```

**Eigenschaften:** max. **4 Spalten** empfohlen (Effektivität sinkt mit jeder weiteren); **nicht idempotent**, aber inkrementell (anders als reines Bin-Packing, das idempotent ist); balanciert nach **Tupel-Anzahl**, nicht Speichergröße; nicht auf Spalten ohne Statistiken anwenden; **inkompatibel mit Liquid Clustering**.

**Grenzen:** keine echte durchgängige Ordnung über die gesamte Tabelle (Werte können sich über viele Dateien verteilen). Muss periodisch neu ausgeführt werden. Jeder Lauf schreibt dabei große Mengen bereits geordneter Daten neu und schafft so eigene Performance-Probleme.

**Z-Ordering vs. Liquid Clustering:**

| Aspekt | Z-Ordering | Liquid Clustering |
|---|---|---|
| Ordnungsqualität | approximativ | konsistent |
| Ausführung | manueller, periodischer `OPTIMIZE` | inkrementell, auch beim Schreiben |
| Neuschreibaufwand | hoch | minimal |
| Änderbarkeit der Keys | vollständiger Neu-Lauf nötig | jederzeit ohne Rewrite |
| Kombinierbar mit Partitionierung | ja | nein |
| Databricks-Empfehlung | nicht mehr empfohlen | empfohlen |

---

## 7. Disk Cache

**Einfach erklärt:** Der Disk Cache beschleunigt wiederholte Lesevorgänge, indem Kopien remote gespeicherter Parquet-Dateien (inkl. Delta-Lake-Tabellen) lokal auf dem Compute-Knoten abgelegt werden — Standardbestandteil der automatischen Runtime-Optimierungen.

**Funktionsweise:** automatisches Caching beim ersten Remote-Lesen, nachfolgende Lesevorgänge lokal und schneller. `CACHE SELECT` wird in SQL-Warehouses und ab Runtime 14.2 ignoriert — der verbesserte Disk Cache übernimmt das automatisch.

**Namenshistorie:** früher „Delta Cache"/„DBIO Cache" — Umbenennung verdeutlicht: **kein** Bestandteil des Delta-Lake-Protokolls, sondern proprietäres Databricks-Feature (funktioniert auch für Nicht-Delta-Parquet).

**Disk Cache vs. Spark Cache:**

| Aspekt | Disk Cache | Spark Cache |
|---|---|---|
| Speicherort | lokale Dateien auf Worker | In-Memory-Blöcke |
| Gilt für | Parquet auf S3/ABFS/etc. | jedes DataFrame/RDD |
| Auslösung | automatisch | manuell (`.cache()`/`.persist()`) |
| Eviction | automatisch (LRU/Dateiänderung) | automatisch (LRU)/manuell (`unpersist`) |

Databricks empfiehlt automatisches Disk Caching gegenüber manuellem Spark Caching.

```python
spark.catalog.cacheTable("tableName")
dataFrame.cache()
spark.catalog.uncacheTable("tableName")
dataFrame.unpersist()
spark.catalog.listCachedTables()
```

| Parameter | Standard | Bedeutung |
|---|---|---|
| `spark.sql.inMemoryColumnarStorage.compressed` | `true` | automatische Kompression je Spalte |
| `spark.sql.inMemoryColumnarStorage.batchSize` | `10000` | Batch-Größe für spaltenbasiertes Caching |

**Cache-Konsistenz:** automatische Erkennung von Erstellung/Löschung/Änderung/Überschreibung der Quelldateien — **keine** manuelle Invalidierung nötig.

**Instance-Auswahl:** Worker mit lokalen SSD-Volumes wählen — Disk Caching ist dort automatisch optimal vorkonfiguriert. Standardmäßig **höchstens die Hälfte** des lokalen SSD-Speicherplatzes.

**Konfiguration:**

| Parameter | Bedeutung | Beispielwert |
|---|---|---|
| `spark.databricks.io.cache.maxDiskUsage` | reservierter Diskspeicher für gecachte Daten pro Knoten | `50g` |
| `spark.databricks.io.cache.maxMetaDataCache` | reservierter Diskspeicher für gecachte Metadaten | `1g` |
| `spark.databricks.io.cache.compression.enabled` | Kompression gecachter Daten | `false` |

**Autoscaling-Falle:** Werden Worker bei Autoscaling abgebaut, geht der dort gecachte Inhalt verloren.

**Aktivieren/Deaktivieren/Status prüfen:**

```python
spark.conf.get("spark.databricks.io.cache.enabled")
```

```python
spark.conf.set("spark.databricks.io.cache.enabled", "[true | false]")
```

Deaktivieren löscht bereits gecachte Daten **nicht** — verhindert nur neues Cachen/Lesen.

```python
# Benchmarking: gezielt deaktivieren, um andere Optimierungen isoliert zu sehen
spark.conf.set('spark.databricks.io.cache.enabled', False)
```

**Hinweis:** funktioniert **nicht** auf Serverless Compute (Fehler) — nur auf Classic Compute.

---

## 8. Cluster-Typen und Serverless Compute

**Einfach erklärt:** Die Wahl des richtigen Compute-Typs ist eine der wirkungsvollsten Performance-/Kostenentscheidungen — noch vor jeder Code-Optimierung. Databricks kennt drei klassische Compute-Typen (**All-Purpose**, **Jobs**, **SQL Warehouses**) sowie **Serverless Compute** als zunehmend zentralen, modernen Ansatz.

**Drei Compute-Typen:**

- **All-Purpose Compute:** interaktive Entwicklung/Tests, neustartbar, mehrbenutzerfähig, Auto-Scale sinnvoll.
- **Jobs Compute:** ephemer (entsteht/terminiert mit dem Job), Single-User, gut für Isolation/Debugging, geringere Kosten, **nicht neustartbar**.
- **SQL Warehouses:** Photon inklusive, für hohe Nebenläufigkeit/Ad-hoc-SQL/BI. Drei Typen: **Classic**, **Pro**, **Serverless**.

**Empfehlungen je Szenario:** Interaktive Notebooks/automatisierte Jobs/Pipelines → Serverless Compute generell bevorzugt; klassisches Compute nur bei RDD-APIs, R-Sprachunterstützung, nicht unterstützten Serverless-Features oder Legacy-Hive-Metastore.

**Berechtigungen für Compute-Ressourcen:** `CAN ATTACH TO` (anhängen), `CAN RESTART` (starten/neustarten/terminieren), `CAN MANAGE` (Details/Berechtigungen/Größe bearbeiten).

**SQL-Warehouse-Performance-Matrix:**

| Feature | Serverless | Pro | Classic |
|---|---|---|---|
| Photon | ✓ | ✓ | ✓ |
| Predictive I/O | ✓ | ✓ | ✗ |
| Intelligent Workload Management | ✓ | ✗ | ✗ |
| Startzeit | 2–6 Sek. | ~4 Min. | ~4 Min. |

**Spot Instances:** günstiger, aber vom Cloud-Anbieter zurückforderbar. **Niemals für den Driver!** Empfohlenes Muster: Driver On-Demand, Worker Spot (mit optionalem Fallback auf On-Demand bei strikten SLAs).

| SLA | Spot oder On-Demand |
|---|---|
| Nicht geschäftskritische Jobs | Driver On-Demand, Worker Spot |
| Strikte SLAs | Spot mit Fallback auf On-Demand |

Standard-Gebotspreis: 100 % des On-Demand-Preises. Konservativere Gebote (~50 %) maximieren Einsparungen, riskieren häufigere Terminierung; aggressivere (120–150 %) verbessern Stabilität.

**Autoscaling:** passt Cluster-Größe dynamisch an Nachfrage an, per Min/Max-Worker-Bereich.

**Optimized Autoscaling** (Premium+): skaliert von Min zu Max in max. 2 Ereignissen; kann herunterskalieren, selbst wenn nicht idle (berücksichtigt Shuffle-File-Zustand); Jobs-Compute skaliert nach 40s Unterauslastung herunter, All-Purpose nach 150s; `spark.databricks.aggressiveWindowDownS` steuert Häufigkeit (max. 600s).

**Standard Autoscaling:** startet mit 8 Knoten, skaliert exponentiell; skaliert herunter bei 90 % Unterauslastung für 10 Min. + mind. 30s idle.

**Photon:** vollständiger Neubau in C++ für SIMD-Hardware. TPC-DS-100TB-Weltrekord: **32.941.245 QphDS**, 2,2x schneller als Alibabas vorherigem Rekord, bei 10 % geringeren Systemkosten; unabhängig bestätigt durch Barcelona Supercomputing Center: 2,7x schneller, 12x besseres Preis-Leistungs-Verhältnis als Snowflake. Kunden sehen 40 % Compute-Reduktion bei ETL, 6x besseres Preis-Leistungs-Verhältnis, 2–3x schnellere Queries gegenüber Open-Source-Spark.

**Cluster-Optimierungsempfehlungen nach Workload:**
1. **DS & DE Development:** All-Purpose, Auto-Scale + Auto-Stop, auf Datenteilmenge entwickeln.
2. **Ingestion & ETL:** Jobs Compute, nach SLA dimensioniert.
3. **Ad-hoc SQL:** (Serverless) SQL Warehouse, Auto-Scale + Auto-Stop.
4. **BI Reporting:** isoliertes SQL Warehouse.
5. Best Practices: Spot auf Workern, neueste LTS-Runtime, Photon, neueste VM-Generation (erst General Purpose, dann Memory/Compute-optimiert testen).

**Serverless Compute** — drei Wertversprechen: **erhöhte Produktivität** (sofortiger Kaltstart, Autoscaling in Sekunden), **Zero Management** (Databricks übernimmt Pool-Management/Kapazität/Sicherheit), **niedrigeres TCO** (nur genutzte Ressourcen bezahlt). GA über All-Purpose, Jobs und SQL Warehouses.

**Kritischer Hinweis:** Serverless ändert **nichts** an der Optimierungslogik — Shuffles, Spill, Liquid Clustering, Photon bleiben relevant; Databricks liefert die beste Infrastruktur, Code/Datenlayout bleiben eigene Verantwortung. Startzeiten ~15–30s statt 5–12 Min. bei klassischem Compute.

**Technische Voraussetzungen (GA-Ankündigung):** UC-aktivierter Workspace, Shared-Access-Mode-Kompatibilität, Runtime 14.3+, PySpark (Scala zum Ankündigungszeitpunkt in Vorbereitung). Kundenbeispiele: Airbus (Ein-Klick-Aktivierung), Jet Linx Aviation (Bronze→Silver von ~16 auf ~7 Min.), AnyClip (vereinfachte Dev-zu-Prod-Migration).

---

## 9. Instance-Auswahl und Cluster-Sizing

**Einfach erklärt:** Nach der Wahl des Compute-Typs (Abschnitt 8) folgt die konkrete VM-Auswahl und Cluster-Dimensionierung — anhand von Faustregeln und einem systematischen „Wenn-dies-dann-das"-Entscheidungsprozess (IFTTT).

**Maschinentypen nach Cloud-Anbieter:** AWS — neben i3 auch **m7gd**/**r7gd** testen, **Graviton**-Instanzen erwägen. Azure — **Eav4**/**Dav4**/**F-Series** vor L-Series, **ACU-Metrik** prüfen. GCP — Standardwerte meist ausreichend. Netzwerkoptimierte Instanzen selten nötig, aber hilfreich bei Photon/bandbreitenintensiven Workloads.

**Grundregeln zur Dimensionierung:** Ein doppelt so großer Cluster, der den Job in halber Zeit fertigstellt, kostet ungefähr gleich viel — spart aber Zeit. Faustregeln für den ersten Durchlauf: `spark.sql.shuffle.partitions` = **2× Kernanzahl**; Speicher pro Maschine unter **128 GB**; **1 Kern pro 128 MB–200 GB** gelesener Daten.

**Kernfaktoren der Instance-Auswahl:** Core-to-RAM-Verhältnis, Prozessortyp, lokaler vs. entfernter Storage, Storage-Medium. Beispiel AWS C5-Familie: 1 Kern : 2 GB RAM, Intel, lokales NVMe.

**Driver-Sizing:** i. d. R. an Worker-Größe angleichen — **4–8 Kerne, 16–32 GB RAM** reicht meist. Ausnahmen: große Delta-Commits (100.000+ Dateien), viele nebenläufige Streams/Jobs, große Driver-Sammlungen (pandas/R). Der Driver ist eine **geteilte Ressource** (CPU, Speicher, DAG-/Task-Scheduler, treiberseitige UDFs) — für `VACUUM`-Jobs empfiehlt Databricks Autoscaling mit 1–4 Workern (je 8 Kerne) und Driver mit 8–32 Kernen; bei Engpässen Jobs auf mehrere Cluster aufteilen. Für erste Exploration: Single-Node-Compute mit großem Node-Typ.

**Spot-Markt:** unterschiedliche Einsparungs-/Unterbrechungsraten je Instanztyp — z. B. i3 ~70 % Einsparung/höhere Unterbrechung vs. r5d ~85 % Einsparung/niedrigere Unterbrechung.

**Flexible Node Types:** reduzieren Kapazitätsfehler (Stockout, z. B. `AWS_INSUFFICIENT_INSTANCE_CAPACITY_FAILURE`), indem automatisch eine Fallback-Liste kompatibler Instanzen genutzt wird. Workspace-Ebene: „Enable auto flexible node types". Individuelle Fallback-Listen nur über Clusters API (`worker_node_type_flexibility`/`driver_node_type_flexibility`, `alternate_node_type_ids`, max. 5 Typen). Kompatibilitätsanforderungen: vCPU/Speicher 100–110 %, gleiche lokale Disk, konsistente CPU-Architektur, gleiches OS-Image, Photon-Unterstützung — keine GPU/virtuellen Typen.

**AWS-Graviton (ARM64):** bestes Preis-Leistungs-Verhältnis unter den AWS-Instanztypen. Für Runtime 15.4 LTS ML+:

| Workload | Verbesserung mit Graviton |
|---|---|
| XGBoost/LightGBM | bis zu 11 % Speedup |
| Databricks AutoML | 63 % mehr Tuning-Durchläufe (Graviton3) |
| Spark MLlib | bis zu 1,7x Speedup |
| Feature Engineering (Point-in-Time-Joins) | bis zu 1,5x schneller |
| Kombiniert mit Photon | 3,1x Verbesserung |

Auswahl: „7g" (Graviton3) oder „6g" (Graviton2) im Namen, ab Runtime 15.4 LTS ML.

**Der IFTTT-Entscheidungsfluss:**

```
Photon nutzen?
├─ Ja  → Für Photon empfohlene VM-Typen als Ausgangspunkt wählen
└─ Nein → ETL-Workload mit Joins/Windows/Aggregationen?
          ├─ Ja  → Instanzempfehlungen für komplexe Datenoperationen
          └─ Nein → Instanzempfehlungen für leichtere Workloads
                     ↓
          Job ausführen → Spark UI: längste Query → Spill vorhanden?
          ├─ Nein → fertig
          └─ Ja  → spark.sql.shuffle.partitions auf Größe der größten
                    Shuffle-Read-Stage setzen (Referenz: 200 MB),
                    danach auf "auto" → Job erneut ausführen
                     ↓
                    weiterhin Spill? → wiederholen, bis kein Spill mehr auftritt
```

**Erinnerung: Shuffle-Partitionen** — im Zweifel `spark.sql.shuffle.partitions` auf `auto`; manuell: größte Shuffle-Read-Größe ÷ 200 (siehe Abschnitt 10, 12).

**Erinnerung: Event Log prüfen** — erste Anlaufstelle beim Troubleshooting, besonders bei Spot-Fehlschlägen. Drei Hauptursachen entfernter Executors: **Autoscaling** (erwartet, kein Fehler), **Spot-Verluste** (Decommissioning versucht Shuffle/RDD-Daten vor Terminierung zu migrieren), **Speichererschöpfung** (echter Fehler). Autoscaling-Events tragen den Typ `autoscale`, mit Status wie `CLUSTER_AT_DESIRED_SIZE`, `SCALE_UP_IN_PROGRESS_WAITING_FOR_EXECUTORS`, `BLOCKED_FROM_SCALING_DOWN_BY_CONFIGURATION`.

**Compute Creation Cheat Sheet (9 Best Practices):** Serverless zuerst prüfen; Standard Access Mode für Multi-User; mit General-Purpose-Instanzen beginnen; Graviton priorisieren; neueste EC2-Generation; On-Demand/Spot balancieren; Worker-Anzahl/-Größe an Operationstyp anpassen (wenige große Knoten bei Shuffle-lastig); VACUUM-Cluster wie oben konfigurieren; Photon für Batch-Workflows evaluieren.

---

## 10. Shuffles in Spark und Databricks

**Einfach erklärt:** Ein **Shuffle** verschiebt Daten vom Output einer Stage zum Input der nächsten — eine Nebenwirkung breiter (**wide**) Transformationen wie `join()`, `groupBy()`, `distinct()`, `orderBy()`. Er beinhaltet teures Netzwerk- und Disk-I/O und ist eine der teuersten Operationen in Spark. **Narrow** Transformationen (Filter, Map, Projektionen) brauchen dagegen nur eine Stage und keinen Shuffle.

**Ablauf (MapReduce-Analogie):** Map (Stage 1 liest/transformiert Daten) → Shuffle (Netzwerkbewegung zwischen Workern) → Reduce (Stage 2 aggregiert) → Schreiben.

**Shuffles erkennen (Spark UI):** längste Stage identifizieren → I/O-Metriken (Input, Output, Shuffle Read/Write) notieren → Task-Anzahl prüfen → Detailseite für Skew-/Spill-Analyse öffnen. Hohes I/O einschätzen: größte I/O-Spalte ÷ (Worker-Cores × Dauer in Sek.) — nähert sich 3 MB/s/Core, ist die Stage I/O-gebunden. Bei hohem Shuffle: `spark.sql.shuffle.partitions=auto`.

**Shuffle in der Query Profile (Databricks SQL):** eigener Operator-Typ im DAG, hohe „shuffle bytes written/read" signalisieren Optimierungsbedarf.

**AQE und Shuffles** (siehe auch Abschnitt 1): Drei der vier AQE-Kernfähigkeiten wirken direkt auf Shuffles.

**Dynamisches Coalescing:** fasst kleine Post-Shuffle-Partitionen zusammen. Beispiel: `SELECT max(i) FROM tbl GROUP BY j` erzeugt 5 Shuffle-Partitionen, 3 davon klein — AQE fasst sie zu einer zusammen (5→3 Tasks). `CustomShuffleReader` zeigt Flags `coalesced` und/oder `skewed`.

**Dynamische Join-Strategie-Umwandlung:** Sort-Merge-Join → Broadcast-Hash-Join, wenn eine Join-Seite laut Laufzeitstatistik unter `spark.sql.adaptive.autoBroadcastJoinThreshold` liegt — eliminiert Shuffle-Overhead komplett. Zusätzlich: Sort-Merge-Join → **Shuffled-Hash-Join**, wenn alle Post-Shuffle-Partitionen unter `spark.sql.adaptive.maxShuffledHashJoinLocalMapThreshold` liegen (Standard `0` = deaktiviert, seit Spark 3.2.0).

**Konfigurationsparameter:**

| Parameter | Standard | Bedeutung |
|---|---|---|
| `spark.sql.shuffle.partitions` | `200`, `"auto"` setzbar | Shuffle-Partitionsanzahl |
| `spark.sql.adaptive.coalescePartitions.enabled` | `true` | Coalescing an/aus |
| `spark.sql.adaptive.advisoryPartitionSizeInBytes` | `64MB` | Zielgröße zusammengefasster Partitionen |
| `spark.sql.adaptive.coalescePartitions.minPartitionSize` | `1MB` | Mindestgröße |
| `spark.databricks.adaptive.autoOptimizeShuffle.enabled` | — | Databricks: Auto-Optimized Shuffle |

**Query-Pläne auf AQE-Re-Optimierung analysieren:** Spark UI (`AdaptiveSparkPlan` mit `isFinalPlan`-Flag), `DataFrame.explain()` (initialer + finaler Plan, `isRuntime`-Flag), SQL `EXPLAIN` (zeigt **nicht** das Laufzeitverhalten).

**AQE in Structured Streaming** (ab Runtime 13.1, `foreachBatch`-Sink): Re-Optimierung pro Micro-Batch; wirkt nur auf zustandslose Operationen innerhalb der `foreachBatch`-Funktion. Benchmark: 1,2x–2x (bis 16x) bei zustandslosen Queries; Delta-MERGE median 1,38x (AQE) / 2,87x (mit Photon).

**SQL-Hints und -Klauseln:**

```sql
SELECT /*+ COALESCE(3) */ * FROM t;
SELECT /*+ REPARTITION(3) */ * FROM t;
SELECT /*+ REPARTITION(c) */ * FROM t;
SELECT /*+ REPARTITION(3, c) */ * FROM t;
SELECT /*+ REPARTITION */ * FROM t;
SELECT /*+ REPARTITION_BY_RANGE(c) */ * FROM t;
SELECT /*+ REPARTITION_BY_RANGE(3, c) */ * FROM t;
SELECT /*+ REBALANCE */ * FROM t;
SELECT /*+ REBALANCE(3) */ * FROM t;
SELECT /*+ REBALANCE(c) */ * FROM t;
SELECT /*+ REBALANCE(3, c) */ * FROM t;
```

**Join-Hints** (Priorisierung: `BROADCAST` > `MERGE` > `SHUFFLE_HASH` > `SHUFFLE_REPLICATE_NL`):

```sql
SELECT /*+ BROADCAST(t1) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;
SELECT /*+ MERGE(t1) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;
SELECT /*+ SHUFFLE_HASH(t1) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;
SELECT /*+ SHUFFLE_REPLICATE_NL(t1) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;
```

Automatisches Broadcasting ohne Hint: `spark.sql.autoBroadcastJoinThreshold` (Standard `10MB`), auf Databricks praktisch **30 MB** (`spark.databricks.adaptive.autoBroadcastJoinThreshold`, nur für dynamische AQE-Umwandlung).

**Query-Klauseln:**

```sql
-- Nur repartitionieren, keine Sortierung
SELECT age, name FROM person DISTRIBUTE BY age;
-- Repartitionieren UND innerhalb jeder Partition sortieren
SELECT age, name FROM person CLUSTER BY age;
```

`ORDER BY` sortiert **global**, `CLUSTER BY`/`SORT BY` nur innerhalb der Partition.

```sql
SELECT shuffle(array(1, 20, 3, 5));
-- [3,1,5,20]
SELECT shuffle(array(1, 20, NULL, 3));
-- [20,NULL,3,1]
```

**PySpark: `repartition()`, `coalesce()`, `shuffle()`:**

```python
repartition(numPartitions: Union[int, "ColumnOrName"], *cols: "ColumnOrName")
```

```python
from pyspark.sql import functions as sf

df = spark.range(0, 64, 1, 9).withColumn(
    "name", sf.concat(sf.lit("name_"), sf.col("id").cast("string"))
).withColumn("age", sf.col("id") - 32)

df.repartition(10).select(
    sf.spark_partition_id().alias("partition")
).distinct().sort("partition").show()

df.repartition(7, "age").select(
    sf.spark_partition_id().alias("partition")
).distinct().sort("partition").show()
```

```python
coalesce(numPartitions: int)
```

```python
spark.range(0, 10, 1, 3).coalesce(1).select(
    sf.spark_partition_id().alias("partition")
).distinct().sort("partition").show()
# Ergebnis: eine einzelne Partition (0)
```

```python
sf.shuffle(col, seed=None)
```

```python
import pyspark.sql.functions as sf
df = spark.sql("SELECT ARRAY(1, 20, 3, 5) AS data")
df.select("*", sf.shuffle(df.data, sf.lit(123))).show()
```

**Pandas Function APIs mit implizitem Shuffle:**

```python
df = spark.createDataFrame([(1, 1.0), (1, 2.0), (2, 3.0), (2, 5.0), (2, 10.0)], ("id", "v"))
def subtract_mean(pdf):
    v = pdf.v
    return pdf.assign(v=v - v.mean())
df.groupby("id").applyInPandas(subtract_mean, schema="id long, v double").show()
```

```python
df = spark.createDataFrame([(1, 21), (2, 30)], ("id", "age"))
def filter_func(iterator):
    for pdf in iterator:
        yield pdf[pdf.id == 1]
df.mapInPandas(filter_func, schema=df.schema).show()
```

```python
def asof_join(l, r):
    return pd.merge_asof(l, r, on="time", by="id")
df1.groupby("id").cogroup(df2.groupby("id")).applyInPandas(
    asof_join, schema="time int, id int, v1 double, v2 string"
).show()
```

**Join-Strategien:**

| Strategie | Shuffle? | Bemerkung |
|---|---|---|
| Broadcast Hash Join | nein | kleinere Tabelle verteilt statt geshuffelt |
| Shuffle Hash Join | ja | Standard für Photon |
| Sort-Merge Join | ja | Standard für Open-Source-Spark |
| Shuffle-Replicate-Nested-Loop-Join | ja | für Kreuzprodukte |

**Bucketing:** explizit **nicht empfohlen**. **Storage Partition Join (SPJ)** als moderne Verallgemeinerung, für V2-Datenquellen wie Apache Iceberg:

```sql
CREATE TABLE prod.db.target (id INT, salary INT, dep STRING)
USING iceberg PARTITIONED BY (dep, bucket(8, id));

CREATE TABLE prod.db.source (id INT, salary INT, dep STRING)
USING iceberg PARTITIONED BY (dep, bucket(8, id));

SET 'spark.sql.sources.v2.bucketing.enabled' 'true';
SET 'spark.sql.sources.v2.bucketing.pushPartValues.enabled' 'true';
SET 'spark.sql.requireAllClusterKeysForCoPartition' 'false';
SET 'spark.sql.sources.v2.bucketing.partiallyClusteredDistribution.enabled' 'true';

EXPLAIN SELECT * FROM target t INNER JOIN source s ON t.dep = s.dep AND t.id = s.id;
```

**Photon und Shuffles:** neu konzipiertes spaltenbasiertes Shuffle, ersetzt Sort-Merge- durch Hash-Joins. Benchmark: **1,5x höherer Durchsatz** bei CPU-gebundenen Workloads (+25 % zusätzlich zum bestehenden 5x-Gewinn).

**Low Shuffle Merge (LSM):** separiert unveränderte Zeilen in einen gestrafften Modus **ohne Shuffle** statt des traditionellen zweistufigen Join-Ansatzes (Inner Join zum Finden, Outer Join zum Schreiben). Automatisch aktiviert seit Runtime 10.4 LTS. Kombiniert mit Photon bis zu **4x** Performance-Steigerung. Benchmark: LSM allein 2–3x (bis 5x bei verteilten Updates); Healthcare-Kunde 10,6x; Fintech-Kunde 7x (11 Min. → 1,5 Min.).

**Delta Lake 1.1:** automatisches Repartitioning nach MERGE bei partitionierten Tabellen (`repartitionBeforeWrite`) — Beispiel: 19,66 Min. → 7,68 Min. (~60 % Reduktion).

**Shuffles in Structured Streaming:** Stateful Queries fixieren die Shuffle-Partitionsanzahl beim Checkpoint (Änderung von `spark.sql.shuffle.partitions` wirkungslos ohne neuen Checkpoint). **On-Demand State Repartitioning** (ab Runtime 18 LTS) erlaubt Größenänderung **unter Beibehaltung** des Checkpoint-Zustands:

```python
query.stop()
spark.conf.set("spark.sql.streaming.stateStore.partitions", "<numPartitions>")
query = df.writeStream.start()
```

**Real-Time Mode (RTM):** ersetzt festplattenbasierte Micro-Batch-Shuffles durch ein kontinuierliches **„Streaming Shuffle"** — Reducer starten, sobald Shuffle-Daten verfügbar sind, statt auf alle Mapper zu warten. Benchmark: bis 92 % schneller als Apache Flink (Kunden-Benchmark); Coinbase >80 % Latenzreduktion (Sub-100ms P99); MakeMyTrip Sub-50ms-P50.

**Shuffles in Lakeflow Declarative Pipelines:** Salting geskewter Keys, Liquid Clustering, Broadcast-Hints für Dimensionstabellen, Range-Join für zeitreihenbasierte Proximity-Joins, RocksDB-State-Management:

```json
{
  "configuration": {
    "spark.sql.streaming.stateStore.providerClass":
      "com.databricks.sql.streaming.state.RocksDBStateStoreProvider"
  }
}
```

**Cluster-Konfiguration zur Shuffle-Optimierung:** weniger, größere VMs reduzieren Netzwerk-I/O (Beispiel: 2×16-Core/128GB = 8×4-Core/32GB an Kapazität, aber weniger Netzwerk-Overhead); NVMe/SSD beschleunigt Shuffle-Read/Write; zusätzliche EBS-Shuffle-Volumes bei Bedarf (bis 5 TB/Instanz). **Optimized Autoscaling** entfernt Worker nur, wenn idle **und** keine benötigten Shuffle-Daten vorhanden — bis zu **30 % Kosteneinsparung**.

**Delta-Tabellenlayout und Shuffles:** `delta.targetFileSize` steuert Ausgabegröße über OPTIMIZE/Clustering/Compaction/Optimized Writes hinweg. MERGE-Shuffle-Tuning: Inner-Join-Bottleneck → Shuffle-Partitionen/Broadcast-Schwellenwert anpassen, kleine Dateien kompaktieren; Outer-Join-Bottleneck → Shuffle-Partitionen (Vorsicht: Small Files bei partitionierten Tabellen), Broadcast, Quelltabelle cachen.

**Query Watchdog:** schützt vor Queries, die unverhältnismäßig viel Output erzeugen (z. B. Cross-Join über leere Strings → 1 Billion Zeilen).

| Parameter | Zweck | Standard |
|---|---|---|
| `spark.databricks.queryWatchdog.enabled` | aktiviert Watchdog | — |
| `spark.databricks.queryWatchdog.outputRatioThreshold` | max. Output/Input-Verhältnis | 1000 |
| `spark.databricks.queryWatchdog.minTimeSecs` | Mindestlaufzeit vor Abbruch | — |
| `spark.databricks.queryWatchdog.minOutputRows` | Mindest-Output vor Abbruch | — |

Empfohlen für interaktive Analyse-Cluster, **nicht** für unbeaufsichtigte Produktions-ETL.

**Historische Entwicklung:** Spark 3.0 (AQE eingeführt), Spark 3.1 (Shuffle-Entfernung in bestimmten Szenarien, SHJ für alle Join-Typen), Spark 3.2 (AQE standardmäßig aktiviert, 61 % schnellere TPC-DS-Kompilierzeit), Spark 3.3 (Bloom-Filter-Joins, bis 10x Speedup). **60-TB-Facebook-Case-Study (2016):** Shuffle-Write-Latenz-Fix (+50 %), Index-Caching (Shuffle-Fetch-Zeit -50 %), insgesamt 4,5–6x CPU-Verbesserung, ~5x Latenzverbesserung ggü. Hive.

---

## 11. Data Skew in Spark und Databricks

**Einfach erklärt:** Data Skew entsteht, wenn eine Spark-Partition deutlich mehr Datensätze enthält als andere — meist nach Aggregationen/Joins über ungleichmäßig verteilte Schlüsselwerte. Eine Stage dauert immer so lange wie ihr **längster Task**: die geskewte Partition braucht doppelt so lange und doppelt so viel Speicher, während der Cluster wartet. Folge: Spill oder OOM-Fehler.

**Skew im Spark UI erkennen:** Jobs-Timeline (fehlgeschlagene Jobs, Ausführungslücken, dominierende lange Jobs) → längste Stage (I/O-Metriken, Task-Anzahl) → Summary Metrics: **„Ist die Max-Dauer 50 % größer als die 75.-Perzentil-Dauer, leidet die Stage wahrscheinlich unter Skew."** Bei niedrigem I/O: Small-File-Problem, langsame UDFs, kartesische Joins, explodierende Joins/`explode()`.

**Adaptive Query Execution (AQE):** zerlegt größere Partitionen automatisch in kleinere, ähnlich große. Skew-Erkennung: Partitionsgrößen vergleichen → Partitionen deutlich größer als Median werden aufgeteilt und mit der korrespondierenden Partition der anderen Seite gejoint. TPC-DS-Benchmark (Spark 3.0): bis zu **8x** Speedup, 32/103 Queries mit >1,1x.

**Konfigurationsparameter Skew-Join-Handling:**

| Parameter | Standard |
|---|---|
| `spark.sql.adaptive.skewJoin.enabled` | `true` |
| `spark.sql.adaptive.skewJoin.skewedPartitionFactor` | `5` |
| `spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes` | `256MB` |
| `spark.sql.adaptive.forceOptimizeSkewedJoin` | `false` (seit Spark 3.3.0) |

Eine Partition gilt als geskewt, wenn **beide** Bedingungen gelten: Größe > (`skewedPartitionFactor` × Median) **und** Größe > `skewedPartitionThresholdInBytes`. **Wichtige Einschränkung:** über 2.000 Shuffle-Partitionen kann Spark keine spezifischen Block-Größen mehr nachverfolgen — AQE erkennt Skew dann nicht mehr.

**Manuelle Steuerung (Legacy, retired):** Skew-Hints sind durch AQE obsolet, bleiben als historische Referenz:

```sql
SELECT /*+ SKEW('orders') */ *
FROM orders, customers
WHERE c_custId = o_custId
```

```sql
SELECT /*+ SKEW('orders', 'o_custId') */ *
FROM orders, customers
WHERE o_custId = c_custId

SELECT /*+ SKEW('orders', ('o_custId', 'o_storeRegionId')) */ *
FROM orders, customers
WHERE o_custId = c_custId AND o_storeRegionId = c_regionId
```

```sql
SELECT /*+ SKEW('orders', 'o_custId', 0) */ *
FROM orders, customers
WHERE o_custId = c_custId

SELECT /*+ SKEW('orders', 'o_custId', (0, 1, 2)) */ *
FROM orders, customers
WHERE o_custId = c_custId
```

**Join-Hints:**

```sql
SELECT /*+ COALESCE(3) */ * FROM t;
SELECT /*+ REPARTITION(3, c) */ * FROM t;
SELECT /*+ REBALANCE(c) */ * FROM t;
SELECT /*+ BROADCAST(t1) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;
SELECT /*+ MERGE(t1) */ * FROM t1 INNER JOIN t2 ON t1.key = t2.key;
```

**Range Joins und Skew** (siehe auch Abschnitt 4): Bin-Größe am 90./99./99,9. Perzentil der Intervalllängen ausrichten:

```sql
SELECT /*+ RANGE_JOIN(points, 10) */ *
FROM points JOIN ranges
ON points.p >= ranges.start AND points.p < ranges.end;
```

```sql
SET spark.databricks.optimizer.rangeJoin.binSize=5
```

```sql
SET spark.databricks.optimizer.autoRangeJoin.enabled = false;
```

```python
events.hint("range_join", 60).join(minutes,
  on=[events.event_start < minutes.minute_end,
      minutes.minute_start < events.event_end]).show()
```

```sql
SELECT map_from_arrays(
  ARRAY(0.5, 0.9, 0.99, 0.999, 0.9999),
  APPROX_PERCENTILE(end::DOUBLE - start::DOUBLE,
    ARRAY(0.5, 0.9, 0.99, 0.999, 0.9999))
) AS bin_sizes
FROM ranges;
```

**Vier Mitigationsstrategien** (aufsteigende Aufwandsreihenfolge): (1) **Skew-Werte filtern** (z. B. NULL-Werte, die typischerweise in einer Partition landen), (2) **Skew-Hints** (obsolet), (3) **AQE-Skew-Optimierung** (Standardweg), (4) **Salting** (letzte Option: zufällige Ganzzahlen als Suffix an geskewte Werte anhängen, zweistufige Aggregation).

```python
coalesce(numPartitions: int) -> DataFrame
```

```python
spark.range(0, 10, 1, 3).coalesce(1).select(
    sf.spark_partition_id().alias("partition")
).distinct().sort("partition").show()
```

**Datenlayout-Optimierung zur Skew-Vermeidung — Liquid Clustering:**

```sql
CREATE TABLE table1 (col0 INT, col1 STRING) CLUSTER BY (col0);
```

```python
df = spark.read.table("table1")
df.write.clusterBy("col0").saveAsTable("table2")
```

```sql
CREATE OR REPLACE TABLE table1 (column01 int, column02 string) CLUSTER BY AUTO;
```

```sql
ALTER TABLE <table_name> CLUSTER BY (<clustering_columns>);
ALTER TABLE table_name CLUSTER BY NONE;
OPTIMIZE table_name;
OPTIMIZE table_name FULL;
```

Reale Benchmarks: Arctic Wolf (3,8-PB-Tabelle) Query-Zeit 51s → 6,6s (7,7x); interne 1,1-PB-Tabelle 406s → 70s (5,9x), −86 % gelesene Bytes; Bolt (CDC) +138 % Schreibdurchsatz, −21 % (bis −63 %) Lesezeit; Co-Clustered Joins (Private Preview) 28min → 14min, Shuffle 1,2 TiB → 150 GiB.

**Data Skipping und Statistiken** (siehe Abschnitt 4):

```sql
ALTER TABLE table_name SET TBLPROPERTIES('delta.dataSkippingStatsColumns' = 'col1, col2, col3');
ANALYZE TABLE table_name COMPUTE DELTA STATISTICS;
```

**`OPTIMIZE`/`ZORDER`** (siehe Abschnitt 6):

```sql
OPTIMIZE events;
OPTIMIZE events FULL;
OPTIMIZE events WHERE date >= '2017-01-01';
OPTIMIZE events WHERE date >= current_timestamp() - INTERVAL 1 day ZORDER BY (eventType);
```

**Praxisbeispiel Star Schema:** große Dimensionstabellen nach Foreign Keys clustern, kleine Dimensionen broadcasten, Predictive Optimization für aktuelle Statistiken.

**Photon und Skew:** keine explizite Skew-Erkennung, aber schnellere Joins/Shuffles (Hash-Joins statt Sort-Merge, spaltenbasiertes Shuffle).

**Cluster-Konfiguration und Best Practices:** Standard Access Mode, Autoscaling, Photon evaluieren; Tabellen unter 1 TB **nicht** partitionieren, nur bei ≥1 GB/Partition partitionieren. Mehrschichtiges Monitoring: System-Tabellen (`system.compute`, `system.workflow`, `system.query`), Query-Profile, Spark-Event-Logs, Alerting, Drittanbieter-Integration.

**Query Watchdog** (siehe Abschnitt 10) als Schutz vor explodierenden Joins — Standard-Output-Ratio-Schwellenwert **1000x**.

**Skew in Structured Streaming:** langsamster Task begrenzt die Stream-Performance. Empfehlung: mehr Input-Partitionen, kleinere Batch-Size, `foreachBatch` + AQE (siehe Abschnitt 10).

---

## 12. Spill in Spark und Databricks

**Einfach erklärt:** Spill beschreibt, was passiert, wenn eine Partition zu groß ist, um vollständig in den verfügbaren RAM zu passen — ein Teil muss auf Festplatte ausgelagert und bei Bedarf zurückgeholt werden. Das ist der letzte Schutzmechanismus vor einem **Out-of-Memory-Fehler**, aber selbst teuer durch Serialisierung, Deserialisierung und Disk-I/O. Tritt am häufigsten während des Daten-Shufflings auf.

**Typische Ursachen:**

| Ursache | Parameter/Code |
|---|---|
| Zu hoch gesetzte maximale Partitionsgröße | `spark.sql.files.maxPartitionBytes` (Standard 128 MB) |
| Explodieren kleiner Arrays | `explode()` |
| Joins mit vielen neuen Zeilen | `join()`/`crossJoin()` |
| Joins auf geskewten Keys | siehe Abschnitt 11 |
| Group-by auf niedrigkardinalen Spalten | `groupBy()` |
| Zählen eindeutiger Werte | `countDistinct()`, `size(collect_set())` |
| Zu niedrige Shuffle-Partitionen | `spark.sql.shuffle.partitions` |

**Weitere Input-Partitioning-Parameter:**

| Parameter | Standard | Bedeutung |
|---|---|---|
| `spark.sql.files.maxPartitionBytes` | `128 MB` | max. Bytes pro Partition beim Dateilesen |
| `spark.sql.files.openCostInBytes` | `4 MB` | geschätzte Öffnungskosten, packt kleine Dateien zusammen |
| `spark.sql.files.minPartitionNum` | — | empfohlene Mindestanzahl Split-Partitionen |
| `spark.sql.files.maxPartitionNum` | kein Limit | empfohlene Höchstanzahl |

**Spill erkennen (Spark UI, Classic Compute):** erscheint **nur** auf der Stage-Detailseite und **nur wenn tatsächlich Spill vorliegt** — „Sehen Sie keine Statistiken für Spill, bedeutet das, dass die Stage keinen Spill hat." Zwei Werte: **Spill (Memory)** und **Spill (Disk)** (stets kleiner durch Kompression).

**Spill in der Query Profile (Databricks SQL):** Metriken „spill (bytes)"/„spill time". Mitigation: primär SQL-Warehouse-T-Shirt-Größe erhöhen, sekundär frühzeitig filtern, Skew reduzieren, Joins vereinfachen, Datei-Layout verbessern.

**Performance Insights:** dedizierte `DATA_SPILL`-Kategorie unter „Compute and resource insights" — Genie Code kann über „Optimize" Query umschreiben/Empfehlungen liefern.

**Spark-Speicherarchitektur:** JVM-Heap geteilt in **Storage Memory** (Caching) und **Execution Memory** (Shuffles/Sortierung/Joins/Aggregationen — führt bei Erschöpfung zu Spill). Speicherkonkurrenz wird dynamisch gehandhabt — Spill ist ein **eingebauter Mechanismus** des Unified-Memory-Modells, kein reiner Fehlerfall.

**Project Tungsten:** explizites Off-Heap-Memory-Management statt Garbage Collection (`sun.misc.Unsafe`) — Hash-Tabelle erreichte über 1 Mio. Aggregationsoperationen/Sekunde (2x `java.util.HashMap`-Durchsatz, kaum Degradation bei mehr Speicher). Cache-bewusster Sort: 3x Beschleunigung.

**Garbage-Collection-Tuning:** G1 GC überlegen für Sparks variable Speichermuster (vs. Parallel GC, CMS GC). Ausgangspunkt: **kein** Tuning (`-XX:+UseG1GC`).

```
-XX:+PrintFlagsFinal -XX:+PrintReferenceGC -verbose:gc
-XX:+PrintGCDetails -XX:+PrintGCTimeStamps
-XX:+PrintAdaptiveSizePolicy -XX:+UnlockDiagnosticVMOptions
-XX:+G1SummarizeConcMark
```

Full-GC vermeiden: `InitiatingHeapOccupancyPercent` senken (45→35), `ConcGCThreads` erhöhen. Humongous Objects: `G1HeapRegionSize` erhöhen (Max. 32 MB). Ergebnis nach Tuning: **1,7x** ggü. ungetuntem G1, **1,5x** ggü. Parallel GC.

**AQE und Spill-Vermeidung:** Partition-Coalescing und Skew-Join-Handling verhindern übergroße Partitionen (siehe Abschnitte 10–11).

```
spark.sql.adaptive.enabled = true
spark.sql.adaptive.coalescePartitions.enabled = true
spark.sql.adaptive.skewJoin.enabled = true
spark.sql.adaptive.autoBroadcastJoinThreshold = 30MB   -- Standard
```

Bei stark komprimierten Tabellen (20–40x):

```
spark.sql.adaptive.preshufflePartitionSizeInBytes = 16MB   -- statt Standard 128MB
```

**Shuffle-Partitionen dimensionieren:**

```
Anzahl Partitionen = Gesamte geshuffelte Datenmenge / 128 MB
```

```
spark.sql.shuffle.partitions = [berechneter_wert]
```

Zielbereich je Task: **128–200 MB**.

**Photon und Spill:** koordiniertes Off-Heap-Spilling zwischen Spark und Photon bei gemischten Plänen. TPC-DS Power Test: bis **2x** schneller als DBR 8.0.

**PySpark-Memory-Profiling (ab Runtime 12.0):**

```python
spark.conf.set("spark.python.profile.memory", "true")
```

```python
# Unoptimiert (~185 MiB)
def arith_op(pdf):
    result = []
    for x in pdf.v:
        result.append(x * 2)
    return pd.DataFrame({'v': result})

# Optimiert, vektorisiert (~61 MiB)
def optimized_arith_op(pdf):
    return pd.DataFrame({'v': pdf.v * 2})
```

```python
sc.show_profiles()
sc.dump_profiles(path)
```

**Performance Profiler:**

```python
# Unoptimiert
def plus_one(pdf):
    return pdf.apply(lambda x: x + 1)
# Optimiert
def plus_one(pdf):
    return pdf + 1
```

Ergebnis: 2.898.160 → 2.384 Funktionsaufrufe, 2,3s → 0,004s.

**Unified Profiling (ab Runtime 17.0):**

```python
spark.conf.set("spark.sql.pyspark.udf.profiler", "perf")
spark.conf.set("spark.sql.pyspark.udf.profiler", "memory")
```

**Instance-Storage-Autoscaling:** löst statische Provisionierungsprobleme (unvorhersehbarer Bedarf, Data Skew über Instanzen) über Linux LVM + dynamisches EBS-Attachment — Volumes werden automatisch angehängt, wenn Diskspeicher knapp wird, und wieder freigegeben.

**Disk Cache** (siehe Abschnitt 7) konkurriert implizit mit Spill um lokalen SSD-Speicherplatz (Standard: max. Hälfte).

**Spill in Structured Streaming:** großzügige Watermarks erhöhen State-Store-Speicherbedarf. **RocksDB** als State-Store-Provider lindert Speicherdruck (kein JVM-Heap). Verbesserte RocksDB-Speicherverwaltung (DBR 13.3 LTS): globales Speicherlimit, Changelog-Checkpointing statt vollständiger Snapshots.

| Operation | p95-Reduktion | p99-Reduktion |
|---|---|---|
| Streaming-Aggregation (Kafka) | bis 76 % | bis 87 % |
| Stream-Stream-Join | bis 78 % | bis 83 % |
| Drop Duplicates | bis 77 % | bis 93 % |
| `flatMapGroupsWithState` | bis 65 % | bis 66 % |

```python
# Delta Lake / Auto Loader: Standard 1000 Dateien pro Micro-Batch
.option("maxFilesPerTrigger", "1000")
# "Soft max" für Datenvolumen pro Micro-Batch
.option("maxBytesPerTrigger", "1g")
```

**Kinesis-spezifisch:** Puffer-Spill bei plötzlichem Datenanstieg — Lösung: Cluster-Kapazität erhöhen oder `fetchBufferSize` reduzieren.

**Cluster-/Warehouse-Sizing:** memory-optimierte Instanzen für ML/Shuffle/Spill-Workloads; „Storage optimized mit Disk-Cache" für wiederholte Lese-/Spill-Operationen. SQL-Warehouse: „Spillen Queries auf Disk, Cluster-Größe erhöhen."

**Spill-Mitigation im Überblick:** mehr RAM/Core; Data Skew adressieren; Partitionsgröße verwalten; `explode()` vermeiden; Datenmenge präventiv reduzieren; AQE aktiviert lassen; `preshufflePartitionSizeInBytes` bei komprimierten Tabellen reduzieren; Disk Cache bevorzugen; Instance-Storage-Autoscaling; SQL-Warehouse-Größe/Layout; RocksDB/Watermarks/Batch-Größe bei Streaming; G1-GC-Tuning; PySpark-UDFs profilen/vektorisieren.

**Praxisbeispiel Disney Streaming Services:** OOM-Fehler alle drei Tage bei `flatMapGroupsWithState`-Job — Root Cause: exzessive `HashMap$Node[16384]`-Instanzen aus nicht geschlossenen AWS-SDK-HTTP-Clients (Connection Leaks). Lehre: „Öffnest du eine Verbindung, schließe sie immer."

**60-TB-Facebook-Workload (2016):** Sorter-Bug (SPARK-13958, unbegrenztes Zeiger-Array) behoben — erzwingt Spill statt OOM, ermöglichte 24 statt 4 Tasks/Host; Memory-Leak-Fix (SPARK-14363) brachte 30 % Verbesserung; Puffergröße 4KB→64MB (~5 % schneller).

**Single-Node-Benchmark:** PySpark verarbeitete mit 10 GB RAM erfolgreich ~35 GB Daten (3,5x RAM) dank automatischem Spill — **Pandas stürzte bei >39 GB vollständig ab.**

---

## 13. Serialization in Spark und Databricks

**Einfach erklärt:** Serialisierung wird immer dann zum Performance-Problem, wenn Code (UDFs) oder Daten zwischen der JVM und einem externen Prozess (Python-Interpreter, Netzwerk, Disk) transportiert werden müssen. Jede UDF muss serialisiert und an alle Executors verteilt werden; Parameter/Rückgabewerte müssen pro Zeile konvertiert werden. **Python-UDFs trifft es am härtesten:** Code muss gepickelt werden, Spark startet pro Executor einen Python-Interpreter, jede Zeile wird einzeln konvertiert.

**UDF-Performance-Hierarchie** (schnellste zuerst): (1) **Built-in-Funktionen/SQL-UDFs** (keine zusätzliche Serialisierung), (2) **Scala-UDFs** (kein JVM-Serialisierungs-Overhead, aber Catalyst-Blackbox), (3) **Python-UDFs** (Serialisierung JVM↔Python), (4) **Pandas-UDFs** (bis zu 100x schneller dank Apache Arrow).

| UDF-Typ | Beschreibung |
|---|---|
| Scalar UDFs | eine Zeile → ein Ergebnis |
| Batch Scalar UDFs | mehrere Werte, 1:1-Verhältnis |
| Non-Scalar UDFs | flexibles Input/Output-Verhältnis |
| UDAFs | mehrere Zeilen → ein Aggregat |
| UDTFs | ein Input → mehrere Zeilen/Spalten |

**Standard-Python-UDFs (teuerster Weg):**

```python
def squared(s):
    return s * s
spark.udf.register("squaredWithPython", squared)
```

```python
from pyspark.sql.types import LongType
def squared_typed(s):
    return s * s
spark.udf.register("squaredWithPython", squared_typed, LongType())
```

```sql
SELECT id, squaredWithPython(id) AS id_squared FROM test
```

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import LongType
squared_udf = udf(squared, LongType())
df.select("id", squared_udf("id").alias("id_squared"))
```

```python
@udf("long")
def squared_udf(s):
    return s * s
```

```python
import pyspark.sql.functions as sf
@sf.udf
def function_name(col):
    pass
@sf.udf(returnType=<returnType>, useArrow=<useArrow>)
def function_name(col):
    pass
sf.udf(f=<function>, returnType=<returnType>, useArrow=<useArrow>)
```

**Pandas (Vectorized) UDFs über Apache Arrow — bis zu 100x schneller:**

```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf("returnType")
def function_name(args) -> ReturnType:
    ...
```

```python
# Series to Series
@pandas_udf(LongType())
def multiply_func(a: pd.Series, b: pd.Series) -> pd.Series:
    return a * b
df.select(multiply_func(col("x"), col("x"))).show()
```

```python
# Iterator of Series to Iterator of Series
from typing import Iterator
@pandas_udf("long")
def plus_one(batch_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
    for x in batch_iter:
        yield x + 1
df.select(plus_one(col("x"))).show()
```

```python
# Iterator of Multiple Series to Iterator of Series
from typing import Iterator, Tuple
@pandas_udf("long")
def multiply_two_cols(
    iterator: Iterator[Tuple[pd.Series, pd.Series]]
) -> Iterator[pd.Series]:
    for a, b in iterator:
        yield a * b
df.select(multiply_two_cols("x", "x")).show()
```

```python
# Series to Scalar
@pandas_udf("double")
def mean_udf(v: pd.Series) -> float:
    return v.mean()
df.select(mean_udf(df['v'])).show()
df.groupby("id").agg(mean_udf(df['v'])).show()
```

```python
spark.conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", "10000")  # Standard
```

```python
import pyspark.sql.functions as sf
@sf.pandas_udf(returnType=<returnType>, functionType=<functionType>)
def function_name(col):
    pass
sf.pandas_udf(f=<function>, returnType=<returnType>, functionType=<functionType>)
```

**Arrow-Optimized Python UDFs (Spark 3.5 / Runtime 14.0):** ~1,6x schneller bei Einzeltransformation, ~1,9x bei verketteten Operationen (32-GB-Datensätze) gegenüber gepickelten UDFs — optimiert den Serialisierungsweg **standardmäßiger** Python-UDFs, keine echte Vektorisierung.

```python
@udf(returnType=IntegerType(), useArrow=True)
def add_one(x):
    if x is not None:
        return x + 1
```

```python
spark.conf.set("spark.sql.execution.pythonUDF.arrow.enabled", "true")
```

**Arrow UDFs — nächste Generation (Runtime 18.0):** operieren direkt auf Arrow-Daten ohne Pandas-Zwischenkonvertierung. ~10 % schneller, ~40 % weniger Speicher als Pandas-UDFs.

```python
import pyarrow as pa
@arrow_udf("long")
def arrow_add_one(s: pa.Array) -> pa.Array:
    return s + 1
```

```sql
SELECT arrow_add_one(col) FROM table
```

```python
@arrow_udtf("id long, name string")
def explode_name(batch: pa.RecordBatch):
    return pa.table({...})
```

**Pandas Function APIs:**

```python
def subtract_mean(pdf):
    v = pdf.v
    return pdf.assign(v=v - v.mean())
df.groupby("id").applyInPandas(subtract_mean, schema="id long, v double").show()
```

```python
def filter_func(iterator):
    for pdf in iterator:
        yield pdf[pdf.id == 1]
df.mapInPandas(filter_func, schema=df.schema).show()
```

```python
def asof_join(l, r):
    return pd.merge_asof(l, r, on="time", by="id")
df1.groupby("id").cogroup(df2.groupby("id")).applyInPandas(
    asof_join, schema="time int, id int, v1 double, v2 string"
).show()
```

**Scala-UDFs:** Typed Transformations (auf Datasets mit Encodern) gegenüber gewöhnlichen Scala-UDFs bevorzugen — profitieren von Tungstens Binärformat.

**UDFs in Spark Connect vs. Classic:** Classic — UDFs „eager erstellt" (externe Werte bei Definition erfasst). Spark Connect — Python-UDFs **lazy**, Serialisierung/Registrierung bis Ausführungszeit verzögert. Databricks Connect erfordert **identische Python-Version** zwischen Client und Compute.

**Catalyst-Optimizer und die UDF-Blackbox:** Catalyst kann Code vor/nach einer UDF nicht verbinden — UDFs sind eine Analysebarriere. Empfehlung: UDFs generell vermeiden, native Higher-Order-Funktionen bevorzugen.

**Project Tungsten — codegenerierte Serialisierung:** über **2x schneller** als Kryo beim Shuffeln von 8 Mio. komplexen Zeilen (nutzt aus, dass alle Zeilen eines Shuffles dasselbe Schema haben).

**Datasets und Encoders:** Laufzeit-Codegenerierung für maßgeschneiderten Bytecode, Operationen direkt auf Tungsten-Binärformat. Benchmark: **4,5x weniger Speicher** beim Cachen von Strings, **bis zu 2x kleinere** serialisierte Daten als RDDs.

**Java- vs. Kryo-Serialisierung:** Java Serialization (Standard, langsamer, größerer Fußabdruck) vs. Kryo (schneller, kompakter, muss konfiguriert werden). Beide bleiben im klassischen JVM-Objektmodell — Tungsten/Encoder umgehen dieses Modell für deutlich höhere Performance.

**Avro als Serialisierungsformat** (zeilenbasiert, kompakt, dominant bei Kafka/Pub/Sub):

```sql
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/reviews_avro',
  format => 'avro')
```

```python
df = spark.read.format("avro").load("/Volumes/<catalog>/<schema>/<volume>/reviews_avro")
display(df)

df = spark.read.table("samples.wanderbricks.reviews")
df.write.format("avro").save("/Volumes/<catalog>/<schema>/<volume>/reviews_avro")
```

```python
avro_schema = '{"type": "record", "name": "Review", "fields": [...]}'
df = spark.read.format("avro").option("avroSchema", avro_schema).load("/path/")
```

```python
df_with_parts.write.format("avro").partitionBy("year", "month").save("/path/")
```

Parquet (spaltenbasiert) wird für analytische Workloads empfohlen, Avro für schreiblastige/Streaming-Szenarien. Native Integration seit Spark 2.4: Lese-Performance ~2x schneller, Schreib-Performance ~8–10 % besser als die externe Bibliothek.

**Avro mit Structured Streaming** (`from_avro`/`to_avro`), Schema Evolution (ab Runtime 14.2):

| Modus | Verhalten |
|---|---|
| `none` (Standard) | ignoriert Schema-Änderungen |
| `restart` | wirft `UnknownFieldException`, Neustart nötig |

```python
# Beispielhafte Nutzung mit Confluent Schema Registry
schema_registry_options = {
    "confluent.schema.registry.address": "https://schema-registry:8081/",
    "confluent.schema.registry.subject.name": "t-value"
}
```

**Protocol Buffers:**

```python
from_protobuf(
    data: 'ColumnOrName',
    messageName: Optional[str] = None,
    descFilePath: Optional[str] = None,
    options: Optional[Dict[str, str]] = None
)

to_protobuf(
    data: 'ColumnOrName',
    messageName: Optional[str] = None,
    descFilePath: Optional[str] = None,
    options: Optional[Dict[str, str]] = None
)
```

```python
from pyspark.sql.protobuf.functions import to_protobuf, from_protobuf
from pyspark.sql.functions import struct

schema_registry_options = {
    "schema.registry.subject": "app-events-value",
    "schema.registry.address": "https://schema-registry:8081/"
}

reviews_df = spark.read.table("samples.wanderbricks.reviews")
proto_bytes_df = reviews_df.select(
    to_protobuf(struct("review_id", "rating", "comment"),
                options=schema_registry_options).alias("proto_bytes"))

reviews_restored_df = proto_bytes_df.select(
    from_protobuf("proto_bytes",
                  options=schema_registry_options).alias("proto_event"))
```

```python
descriptor_file = "/path/to/proto_descriptor.desc"
proto_bytes_df = reviews_df.select(
    to_protobuf(struct("review_id", "rating", "comment"),
                "Review", descriptor_file).alias("proto_bytes"))
reviews_restored_df = proto_bytes_df.select(
    from_protobuf("proto_bytes", "Review",
                  descFilePath=descriptor_file).alias("review"))
```

**Kafka: binäre Serialisierung:**

```python
df.select(col("value").cast("string"))
```

```python
from pyspark.sql.functions import from_json
df.select(from_json(col("value"), schema).alias("parsed_value"))
```

```python
from pyspark.sql.functions import to_json, struct, col
df.select(
    col("userId").cast("string").alias("key"),
    to_json(struct("*")).alias("value")
).writeStream.format("kafka") \
 .option("kafka.bootstrap.servers", "localhost:9092") \
 .option("topic", "users") \
 .option("checkpointLocation", "/tmp/checkpoint") \
 .start()
```

**Isolation Levels (Transaktions-Serialisierbarkeit, nicht Datenserialisierung):**

```sql
ALTER TABLE <table-name> SET TBLPROPERTIES ('delta.isolationLevel' = 'Serializable');
```

**Mitigation im Überblick:** UDFs generell vermeiden; wo nötig Pandas-/Arrow-UDFs statt Standard-Python-UDFs; Typed Transformations statt Scala-UDFs; Business-Logik nach Spark portieren statt in UDFs zu wrappen; native Funktionen bevorzugen; Kryo statt Java-Serialisierung bei RDD-lastigen Workloads; passendes Datenformat wählen (Parquet/Avro); Schema Registry bei Avro/Protobuf-Kafka-Pipelines; Isolation Level bewusst wählen.

---

## 14. Photon-Performance auf Azure Lasv3-Instanzen (AMD EPYC)

**Einfach erklärt:** Ergänzend zum allgemeinen Photon-Überblick (Abschnitt 8) und der cloud-spezifischen Instance-Auswahl (Abschnitt 9, dort Azure Eav4/Dav4/F-Series vor L-Series) liefert ein Databricks-Benchmark konkrete Zahlen für Photon auf Azure **Lasv3**-Instanzen mit AMD 3rd-Gen-EPYC-7763v-Prozessoren — direkter Vergleich gegenüber der älteren Lsv2-Generation (AMD 1st Gen EPYC 7551).

**Testaufbau:** `Standard_L8s_v2` (ohne Photon, AMD 1st Gen EPYC 7551) vs. `Standard_L8as_v3` (mit Photon, AMD 3rd Gen EPYC 7763v) — beide mit 8 vCPUs/64 GB RAM, Lasv3 zusätzlich mit 128–160 Lanes PCIe Gen4 und bis zu 256 MB L3-Cache pro Socket. Photon-Aktivierung erfordert **keine Codeänderung** — nur die Option „Use Photon Acceleration".

**TPC-DS-Benchmark** (99 Queries, 1-TB- und 10-TB-Skalierungsfaktor, rein lesend):
- **5,3x** schnellere Ausführung (Photon+Lasv3 vs. ohne Photon+Lsv2)
- **2,5x** besseres Preis-Leistungs-Verhältnis

**ETL-Benchmark** (Lese-/Schreiboperationen, u. a. `MERGE`-DML und `CREATE TABLE AS` mit Delta, 1-TB-Skalierungsfaktor):
- **4,4x** schnellere Ausführung
- **3,6x** besseres Preis-Leistungs-Verhältnis (gemessen mit Premium-Jobs-Compute-Preisen)

**Einordnung:** Bestätigt und konkretisiert für Azure/AMD-EPYC die in Abschnitt 8 genannten generischen Photon-Zahlen (2–3x schnellere Queries, 6x besseres Preis-Leistungs-Verhältnis ggü. Open-Source-Spark) — mit einem direkten, reproduzierbaren Instance-zu-Instance-Vergleich statt eines Weltrekord-Benchmarks.






