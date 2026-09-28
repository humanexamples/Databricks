# Data Transformation and Modeling — Uebersicht

Dieser Ordner deckt das Pruefungsthema **"Section 3: Data Transformation and Modeling" (22 %)** der Zertifizierung *Databricks Certified Data Engineer Associate* ab — das am hoechsten gewichtete Einzelthema der Pruefung.

**Quelle:** offizieller Exam Guide, direkt von Databricks bezogen (`databricks.com/sites/default/files/2026-05/databricks-certified-data-engineer-associate-exam-guide-may-2026-000.pdf`), Stand **4. Mai 2026** — die aktuell gueltige Pruefungsversion.

## Struktur: Kern vs. Vertiefung

Der Ordner ist bewusst in zwei Bereiche geteilt:

- **Kernordner (`01`–`07`)** — bildet die 7 offiziellen Objectives von Section 3 so direkt wie moeglich ab. Code-first, wenig Text, mit `Ergebnis:`-Kommentaren.
- **`Vertiefung (ueber Pruefungsumfang hinaus)/`** — technisch wertvolles, aber ueber den Associate-Pruefungsumfang hinausgehendes Material (volle Lakeflow-SQL/Python-DDL-Referenz, Structured-Streaming-Interna, UDF-Tiefe, PySpark-Reader/Writer-Referenz). Im offiziellen Exam Guide taucht z. B. "Structured Streaming" in Section 3 nicht auf, UDFs werden dort ebenfalls nicht erwaehnt — dieses Material bleibt zugaenglich, draengt sich aber nicht mehr in die Kernlektuere.

## Zuordnung: Objective → Datei

**1. "Implement data cleaning by reading bronze tables with PySpark/SQL, cleaning nulls, standardizing data types, and writing to new silver tables."**
- `01 SQL-Funktionen fuer Transformation/01 Cast und Typkonvertierung.md`, `03 NULL-Behandlung.md` — Bausteine (Cast-Funktionen, `isnull`/`coalesce`).
- `02 PySpark DataFrame-Transformationen/04 Bronze-zu-Silver Cleaning-Workflow.md` — der End-to-End-PySpark-Workflow selbst.

**2. "Combine DataFrames with operations such as Inner join, left join, broadcast join, multiple keys, cross join, union, and union all."**
- `02 PySpark DataFrame-Transformationen/01 Joins (Inner, Left, Broadcast, Cross, Multiple Keys, Union).md`

**3. "Manipulate columns, rows, and table structures by adding, dropping, splitting, renaming column names, applying filters, and exploding arrays."**
- `02 PySpark DataFrame-Transformationen/02 Spalten-, Zeilen- und Tabellenmanipulation.md`
- `01 SQL-Funktionen fuer Transformation/04 String-Funktionen.md`, `05 Array-Funktionen.md` — ergaenzende SQL-Funktionsreferenz (`split`, `slice`).

**4. "Perform data deduplication operations and aggregate operations on DataFrames, such as count, approximate count distinct, and mean, summary."**
- `02 PySpark DataFrame-Transformationen/03 Deduplizierung und Aggregation.md`

**5. "Understand the basic tuning parameters (spark.sql.shuffle.partitions, spark.default.parallelism, spark.executor/driver.memory, spark.sql.autoBroadcastJoinThreshold) and re-measure the performance."**
- `03 Spark Tuning-Parameter.md`

**6. "Understand the difference between, and how to build, Gold layer objects such as materialized views, views, streaming tables, and tables for BI and analytics teams in Unity Catalog."**
- `06 Lakeflow Declarative Pipelines - Grundlagen/01 Kernkonzepte (...).md` — Unterschiede MV/View/Streaming Table/Tabelle.
- `06 .../02`–`06` — Bau, Konfiguration, Unity-Catalog-Einbindung.
- `05 Datenmodellierung/` — Medaillon-Architektur und dimensionale Modellierung als Kontext fuer die Gold-Schicht.
- `04 DML und Kernkonzepte/01 MERGE INTO.md`, `02`, `03` — DML/Konzepte, die beim Bau von Gold-Objekten gebraucht werden.

**7. "Apply data quality checks and validation rules to ensure reliable Silver and Gold datasets."**
- `07 Data Quality Checks und Validierung.md`

## Zusatz: SQL-Funktionsreferenz

`01 SQL-Funktionen fuer Transformation/` deckt Cast/Typkonvertierung, Datum/Zeit, NULL-Behandlung, String-, Array- und JSON/CSV/VARIANT-Funktionen ab — direkt relevant fuer Objective 1 ("Datentypen standardisieren", "Nulls bereinigen") und als generelle SQL-Werkzeugkiste fuer Transformationen in Section 3.

## Inhalt von "Vertiefung (ueber Pruefungsumfang hinaus)/"

- **Lakeflow Declarative Pipelines – Referenz** — vollstaendige SQL-/Python-DDL-Syntax (`CREATE VIEW`/`MATERIALIZED VIEW`/`STREAMING TABLE`/`FLOW`/`AUTO CDC INTO`), SQL-vs-Python-Vergleich, Databricks-SQL-Standalone-Pipelines.
- **Lakeflow Declarative Pipelines – Transformation und CDC** — Flows (Fan-in/Fan-out), inkrementelles Refresh, CDC/SCD im Detail, Sinks, Observability, Best Practices.
- **Structured Streaming** — Ausfuehrungsmodell, zustandsbehaftete Verarbeitung, Real-Time Mode, Monitoring.
- **PySpark Reader-Writer-Referenz** — vollstaendige `DataFrameReader`/`DataFrameWriter`/`DataStreamReader`/`DataStreamWriter`-Optionsreferenz.
- **User-Defined Functions (UDFs)** — Unity-Catalog-UDFs, Session-scoped/Pandas-UDFs, UDTFs.
- **Semi-strukturierte Daten abfragen** — JSON-Pfad-Syntax an einem durchgerechneten Beispiel.

Dieses Material ist inhaltlich korrekt und gegen die Live-Dokumentation verifiziert, geht aber ueber das hinaus, was der Exam Guide fuer Section 3 explizit nennt — nuetzlich fuer tieferes Verstaendnis oder spaetere Prüfungen (z. B. Professional-Level), nicht Pflichtstoff fuer die Associate-Pruefung.

**Stand:** 2026-09-15.
