# Content-Briefing für alle Themenordner

Gemeinsame Vorlage: `C:\Temp\a - Kopie\Databricks-Dokumentation-DE\_build\template.py` (Funktion `render_pdf`).
Bereits fertiges Referenzbeispiel (Stil/Umfang/Ton als Vorbild ansehen, bevor du schreibst):
`C:\Temp\a - Kopie\Databricks-Dokumentation-DE\_build\build_01_01.py`

## Arbeitsweise pro PDF (für jeden Agenten verbindlich)

1. Quell-Notebook(s) im jeweiligen Kursordner per `find`/Glob suchen (Dateinamen können leicht von den Titeln unten abweichen, z.B. doppelte Leerzeichen — nicht raten, sondern nachsehen).
2. Notebook ist JSON (`nbformat`). Mit Python öffnen und `cells` durchgehen (siehe Beispielcode unten). Markdown-Zellen liefern die Erklärungen, Code-Zellen die SQL/Python-Beispiele.
3. **Eigenständigen deutschen Fließtext schreiben** — keine wörtliche Übersetzung. Erkläre das Konzept klar und verständlich, so wie ein gutes Doku-Portal es tun würde. Code-Beispiele **unverändert übernehmen** (nur ggf. kürzen/auswählen wenn zu lang), mit `html.escape()` in `<pre class="code sql">` bzw. `<pre class="code python">` einbetten.
4. **Eine gezielte Web-Recherche** (WebSearch, ggf. WebFetch auf docs.databricks.com) pro PDF durchführen, um aktuelle Begriffe/Deprecations/Ergänzungen zu prüfen, und das Ergebnis in eine `<div class="docbox">…</div>`-Box am Ende packen (mit Quelle als `<a href>`).
5. **0–2 illustrative Bilder** auswählen (Architektur-/Konzept-Diagramme oder ein aussagekräftiger Ergebnis-Screenshot — NICHT jeden Klick-für-Klick-UI-Screenshot). Bild von der Quelle nach `_build\assets\<Ordnernummer>\` kopieren, dann relativ referenzieren: `<figure class="img"><img src="assets/<Ordnernummer>/<datei>.png"><figcaption>…</figcaption></figure>`.
6. Ein Python-Skript `build_<Ordnernummer>_<PDFnummer>.py` in `_build\` anlegen (siehe `build_01_01.py` als Vorlage), das `render_pdf(...)` aufruft mit `out_pdf` = voller Pfad in den Zielordner. Skript ausführen (`python build_XX_YY.py`), prüfen dass PDF erzeugt wurde (Datei existiert, Größe > 20 KB).
7. Zwischen-HTML-Dateien bleiben in `_build\` liegen (kein Aufräumen nötig) — nur die PDFs müssen in den nummerierten Zielordnern landen.

Notebook-Lesecode:
```python
import json
nb = json.load(open(r"PFAD.ipynb", encoding="utf-8"))
for i, c in enumerate(nb["cells"]):
    print(i, c["cell_type"], "".join(c["source"])[:400])
```

Zielordner-Basis: `C:\Temp\a - Kopie\Databricks-Dokumentation-DE\`

---

## 00 Überblick (Zielordner: `00 Überblick`) — 1 PDF

**00-1 „Databricks Data-Engineering-Plattform & Lakeflow im Überblick“**
Quelle: die fast identischen Intro-Lectures „01 Lecture - Introduction to Data Engineering in Databricks“ aus Kurs 1, Kurs 2 und Kurs 3 (nur EINMAL verwenden, Dubletten ignorieren) — Pfade:
`1_Data Ingestion with Lakeflow Connect(DONE)\01 Lecture - Data Engineering in Databricks.ipynb`
`2_Deploy Workloads with Lakeflow Jobs(DONE)\01 Lecture - Introduction to Data Engineering in Databricks.ipynb`
Inhalt: Was ist die Databricks-Lakehouse-Plattform, Medallion-Architektur (Bronze/Silver/Gold), Unity-Catalog-Grundbegriffe (Metastore/Catalog/Schema/Table/Volume), und eine kurze Einordnung/Landkarte: was ist Lakeflow (Connect = Ingestion, Pipelines = Transformation, Jobs = Orchestrierung) und wie hängen die folgenden 8 Themenordner damit zusammen (kurzer Verweis je Ordner). Web-Recherche: "Databricks Lakeflow overview Connect Pipelines Jobs Designer" zur Bestätigung der aktuellen Begriffe.
Bild: `1_Data Ingestion with Lakeflow Connect(DONE)\images\` — such nach einem passenden Architektur-/Übersichtsbild.

---

## 01 Datenaufnahme mit Lakeflow Connect (Zielordner: `01 Datenaufnahme mit Lakeflow Connect`) — bereits PDF 1 fertig, PDFs 2–5 fehlen noch

Kursordner: `1_Data Ingestion with Lakeflow Connect(DONE)\`

**01-2 „Metadaten-Spalten & die Rescued-Data-Spalte“** — Quellen: `06 Lecture - Appending Metadata Columns on Ingest.ipynb`, `07 Demo - Adding Metadata Columns During Ingestion.ipynb`, `08 Lecture - Working with the Rescued Data Column.ipynb`, `09 Demo - Handling CSV Ingestion with the Rescued Data Column.ipynb`. Inhalt: warum Metadaten (Dateiname, Ingestion-Zeitstempel, `_metadata`-Spalte) beim Ingest sinnvoll sind, Beispielcode für `_metadata.file_name` etc.; was die `_rescued_data`-Spalte ist (fängt Schema-Abweichungen ab, z.B. zusätzliche/falsch typisierte Spalten bei CSV), Beispielcode. Web-Recherche: "Databricks rescued data column schema evolution".

**01-3 „Strukturierte & halbstrukturierte Daten laden (CSV, JSON)“** — Quellen: `11 Lecture - Ingesting Semi-Structured Data JSON.ipynb`, `12 Demo - Ingesting JSON files with Databricks.ipynb`, `13 Lab - Creating Bronze Tables from JSON Files.ipynb`, `10 Lab - Creating Bronze Tables from CSV Files.ipynb`. Inhalt: Besonderheiten beim Laden von CSV (Trennzeichen, Header, Encoding-Optionen von `read_files`) und JSON (verschachtelte Strukturen, `from_json`, Base64-dekodierte Felder), mit Codebeispielen. Web-Recherche: "Databricks read_files JSON CSV options documentation".

**01-4 „Enterprise-Datenintegration mit Lakeflow Connect“** — Quellen: `14 Lecture - Ingesting Enterprise Data Overview.ipynb`, `15 Demo - Enterprise Data Ingestion with Lakeflow Connect.ipynb`, `16 Lecture - Additional Features and Ingesting into Existing Delta Tables.ipynb`. Inhalt: Managed Connectors (SaaS-Anwendungen, Datenbanken) vs. Standard Connectors, warum das für Enterprise-Quellen (Salesforce, SQL Server, SharePoint etc.) einfacher ist als selbst geschriebene Ingestion-Skripte; kurzer Ausblick auf Databricks Marketplace. Web-Recherche: "Databricks Lakeflow Connect managed connectors list" (aktuelle Liste der unterstützten Quellen).

**01-5 „Daten in bestehende Delta-Tabellen einfügen (MERGE INTO & weitere Features)“** — Quelle: `17 Demo - BONUS - Data Ingestion with MERGE INTO.ipynb`. Inhalt: `MERGE INTO`-Syntax für Upsert-Logik (Insert/Update/Delete in einem Statement), typischer Anwendungsfall (neue Daten in bestehende Bronze/Silver-Tabelle einpflegen ohne Duplikate). Web-Recherche: "Databricks MERGE INTO delta syntax".

---

## 02 Orchestrierung mit Lakeflow Jobs (Zielordner: `02 Orchestrierung mit Lakeflow Jobs`) — 5 PDFs

Kursordner: `2_Deploy Workloads with Lakeflow Jobs(DONE)\`

**02-1 „Grundlagen: Jobs, Tasks und Komponenten“** — Quellen: `02 Lecture - Lakeflow Jobs Core Components.ipynb`, `03 Lecture - Course Project Overview.ipynb`, `04 Demo - Creating a Job Using the Lakeflow Jobs UI.ipynb`. Inhalt: Job/Task-Hierarchie, Task-Typen (Notebook, SQL, Pipeline, …), Abhängigkeiten zwischen Tasks.

**02-2 „Jobs erstellen, planen und automatisieren (Scheduling & Trigger)“** — Quellen: `06 Lecture - Creating and Scheduling Jobs.ipynb`, `07 Demo - Automating Workloads with Scheduling and Triggers.ipynb`. Inhalt: Cron-Scheduling, Trigger-Typen (Datei-Ankunft, kontinuierlich), Parameter-Übergabe an Tasks.

**02-3 „Bedingte und iterative Tasks (Run If, For Each)“** — Quellen: `08 Lecture - Conditional and Iterative Tasks.ipynb`, `09 Demo - Building Dynamic Workloads with Advanced Tasks.ipynb`, `10 Lab - Adding If-Else Task and Automating your Job.ipynb`. Inhalt: `Run If`-Bedingungen (abhängig vom Status vorheriger Tasks), `For Each`-Task für dynamische/parallele Verarbeitung von Listen.

**02-4 „Monitoring, Fehlerbehandlung und Repair“** — Quellen: `11 Lecture - Handling Task Failures and Monitoring Jobs Performance.ipynb`, `12 Demo - Monitoring and Repairing Task.ipynb`. Inhalt: Job-Run-Ansicht, Retry-Policies, „Repair and Rerun“ für fehlgeschlagene Tasks, Benachrichtigungen/Alerts.

**02-5 „Lakeflow Jobs in Produktion: Best Practices & modulare Orchestrierung“** — Quellen: `13 Lecture - Lakeflow Jobs in Production and Best Practices.ipynb`, `15 BONUS LAB - Modular Orchestration.ipynb`. Inhalt: Compute-Auswahl (Job-Cluster vs. All-Purpose vs. Serverless), Kostenaspekte, Best Practices für Produktionsumgebungen, Muster für modulare/wiederverwendbare Jobs (ein Job ruft andere Jobs/Pipelines auf).

Web-Recherche pro PDF (Beispiele): "Databricks Lakeflow Jobs conditional tasks for each task", "Databricks Jobs repair and rerun", "Databricks Jobs best practices serverless compute".
Bilder: `2_Deploy Workloads with Lakeflow Jobs(DONE)\Includes\images\` durchsuchen.

---

## 03 Deklarative Pipelines – Grundlagen (Zielordner: `03 Deklarative Pipelines - Grundlagen`) — 5 PDFs

Kursordner: `3_Build Data Pipelines with Lakeflow Spark Declarative Pipelines(DONE)\`

**03-1 „Konzepte: Flows, Streaming Tables & Materialized Views“** — Quellen: `01 Lecture...ipynb` (kurz, nur falls neue Punkte ggü. 00-Überblick), `02 Demo - Course Setup and Creating a Pipeline.ipynb`, `03 Lecture - Course Project and Dataset Types Overview.ipynb`. Inhalt: was ist eine Lakeflow Declarative Pipeline (ex Delta Live Tables/DLT — Namensänderung erwähnen!), Dataset-Typen: Streaming Table vs. Materialized View, deklarativer vs. prozeduraler Ansatz.

**03-2 „Pipelines entwickeln (Pipeline-Editor, Einstellungen)“** — Quellen: `04 Lecture - Simplified Pipeline Development and Common Pipeline Settings.ipynb`, `05 Demo - Developing a Simple Pipeline.ipynb`. Inhalt: Pipeline-Editor/Multi-File-Editor, typische Pipeline-Einstellungen (Zielschema, Katalog, Entwicklungs-/Produktionsmodus), Ordnerstruktur eines Pipeline-Projekts.

**03-3 „Datenqualität mit Expectations“** — Quellen: `06 Lecture - Ensure Data Quality with Expectations.ipynb`, `07 Demo - Adding Data Quality Expectations.ipynb`, `08 Lab - Create a Pipeline.ipynb`. Inhalt: `CONSTRAINT ... EXPECT (...)`-Syntax, die drei Verletzungsaktionen (WARN/DROP ROW/FAIL UPDATE), Beispielcode.

**03-4 „Streaming Joins & Produktivbetrieb“** — Quellen: `09 Lecture - Streaming Joins and Deploying Pipelines to Production.ipynb`, `10 Demo - Deploying a Pipeline to Production.ipynb`. Inhalt: Stream-Static-Joins-Muster, Unterschied Entwicklungs-/Produktionsmodus einer Pipeline, Deployment-Ablauf.

**03-5 „Change Data Capture Grundlagen (AUTO CDC, SCD Type 1)“** — Quellen: `11 Lecture - Change Data Capture (CDC) Overview.ipynb`, `12 Demo - Change Data Capture with AUTO CDC with SCD TYPE 1.ipynb`, `14 Bonus Lab - AUTO CDC INTO with SCD Type 1.ipynb`. Inhalt: was ist CDC, SCD Type 1 (Überschreiben) einfach erklärt, `AUTO CDC INTO`-Syntax mit `KEYS`/`SEQUENCE BY` (Hinweis: löst die ältere `APPLY CHANGES INTO`-API ab, gleiche Syntax nennen).

Web-Recherche: "Databricks Lakeflow Declarative Pipelines expectations", "Databricks AUTO CDC INTO SCD Type 1 syntax", "Delta Live Tables renamed Lakeflow Declarative Pipelines".
Bilder: `Includes\images\` und die `Demo 07/10/12 - pipeline`-Ordner (Screenshots eher spärlich einsetzen).

---

## 04 Deklarative Pipelines – Fortgeschritten (Zielordner: `04 Deklarative Pipelines - Fortgeschritten`) — 5 PDFs

Kursordner: `5_Advanced Techniques with Spark Declarative Pipelines\`

**04-1 „Multi-Flow-Pipelines & Liquid Clustering“** — Quellen: `1 Lecture - Multi Flows, Expectations, Liquid Clustering.ipynb`, `2 Demo - Multi Flow SDP with Liquid Clustering and Data Quality.ipynb` (+ Ordner `Demo2 - ingest_multiple_flows`). Inhalt: Flow = Query+Target-Konzept, Default- vs. explizite Flows, Multi-Flow-Muster vs. UNION, `CLUSTER BY AUTO`/explizites Liquid Clustering als Ersatz für Hive-Partitionierung/Z-Ordering (kurz — Details stehen in Ordner 06 Performance, hier nur Pipeline-Kontext).

**04-2 „Multiplex Streaming, Delta Sinks & Iceberg/UniForm“** — Quellen: `3 Lecture - Multiplex Streaming, Delta Sinks, Iceberg Reads.ipynb`, `4 Demo - Multiplex Streaming SDP with Delta Sinks and Iceberg Reads.ipynb` (+ `Demo4 - multiplex_pipeline`). Inhalt: Multiplex-Muster (einmal einlesen, nach Typ verzweigen), Delta Sinks (`dp.create_sink`, `append_flow`, Kafka/Event-Hub-Ziele), Delta UniForm für Iceberg-Kompatibilität (`enableIcebergCompatV2`, Einschränkung bei Deletion Vectors).

**04-3 „CDC vertieft: SCD Type 1 vs. Type 2 mit AUTO CDC INTO“** — Quellen: `5 Lecture - Change Data Capture (CDC) Review.ipynb`, `6 Demo - Automating SCD Type 2 with AUTO CDC.ipynb` (+ `Demo6 - my_pipeline`). Inhalt: SCD Type 1 vs. Type 2 (Historisierung), `AUTO CDC INTO`-Syntax mit `APPLY AS DELETE WHEN`, `SEQUENCE BY`, `STORED AS SCD TYPE 2`, `__START_AT`/`__END_AT`-Metadatenspalten.

**04-4 „Erweiterte Datenqualitätsprüfungen & Quarantäne-Muster“** — Quellen: `7 Lecture - Advanced Data Quality Checks and Expectations.ipynb`, `8 Demo - Advanced Data Quality Checks and Expectations.ipynb` (+ `Demo8 - dq_pipeline`). Inhalt: Grenzen einfacher NOT-NULL-Checks, Cross-Table-Expectations (Row-Count-Validierung, PK-Eindeutigkeit), robuste Bronze-Schicht-Strategie (STRING-Ingest + `TRY_CAST`), Quarantäne-Muster (`is_quarantined`-Flag statt `DROP ROW`) inkl. Codebeispiel.

**04-5 „Praxisbeispiel: Multi-Source E-Commerce-Pipeline“** — Quelle: `9 Lab - Building Multi-Source Ecommerce Pipeline with SDP.ipynb` (+ `Lab9 - ecommerce_pipeline`). Inhalt: Zusammenfassendes Praxisbeispiel, das Multi-Flow-Ingestion, Expectations, Stream-Static-Joins und Gold-Materialized-Views kombiniert — als abschließendes durchgängiges Codebeispiel darstellen.

Web-Recherche: "Databricks Delta Sinks append_flow documentation", "Databricks Delta UniForm Iceberg", "Databricks AUTO CDC INTO SCD Type 2".
Bilder: `Includes\images\` (Unterordner cdc_lecture, dq, multi_flow, multiplex).

---

## 05 Data Governance & Datenschutz (Zielordner: `05 Data Governance und Datenschutz`) — 5 PDFs

Kursordner: `6_Databricks Data Privacy\`

**05-1 „Unity-Catalog-Sicherheitsmodell (ACLs, Lineage, Discoverability)“** — Quelle: `DP 1.1 – Securing Data in Unity Catalog.ipynb` (erster Teil). Inhalt: UC-Objekthierarchie (Metastore → Catalog → Schema → Table/Volume), ACL-Modell (GRANT/REVOKE, wer/was/wie), Data Lineage, Tagging, System-Tables für Audit.

**05-2 „Row Filters, Column Masks & Dynamic Views“** — Quelle: `DP 1.1 – Securing Data in Unity Catalog.ipynb` (zweiter Teil, Row-Filter/Column-Mask-Abschnitt). Inhalt: `SET ROW FILTER`/`SET MASK`-Syntax mit Codebeispiel, Unterschied zu klassischen Dynamic Views, kurzer Hinweis auf ABAC-Policies (neuere, tag-basierte Alternative). Web-Recherche PFLICHT hier: "Databricks Unity Catalog row filters column masks ABAC 2026" — diese Doku hatten wir schon recherchiert, Ergebnis nutzen und im docbox referenzieren.

**05-3 „PII-Schutz: Pseudonymisierung & Anonymisierung“** — Quellen: `DP 1.2 – PII Data Security.ipynb`, `Pipeline\DP 1.2.1 - Pseudonymized PII Lookup Table.py`, `Pipeline\DP 1.2.2 - Anonymized Users Age.py`. Inhalt: Pseudonymisierung (Hashing mit Salt via Databricks Secrets, Tokenisierung) vs. Anonymisierung (Suppression, Generalisierung/Binning, IP-Kürzung, Rundung), mit echtem Codebeispiel aus den Pipeline-Dateien.

**05-4 „Change Data Feed: Änderungen nachverfolgen & propagieren“** — Quellen: `DP 1.3 – Processing Records from CDF and Propagating Changes.ipynb`, `DP 1.4L – Propagating Changes with CDF Lab.ipynb`. Inhalt: Change Data Feed aktivieren, `table_changes()`-Funktion, Löschungen aus einer Quelltabelle in nachgelagerte Tabellen propagieren (wichtig für DSGVO-Löschanfragen).

**05-5 „Compliance: DSGVO/CCPA & Datenlöschung“** — Quelle: `_MD\`-Notizen (Regulatory-Compliance-Abschnitt) + `Zusammenfassung.md` falls vorhanden. Inhalt: DSGVO/CCPA-Grundprinzipien im Databricks-Kontext, `VACUUM` und tatsächliches physisches Löschen, Einschränkungen bei DML auf Streaming Tables. Web-Recherche: "Databricks GDPR right to be forgotten delta lake vacuum".

Bilder: falls `_MD`-referenzierte Bilder unter `../assets/` fehlen (laut Survey teils nicht vorhanden), stattdessen `Includes\images\` des Kurses verwenden oder Bild weglassen — kein Blocker.

---

## 06 Performance-Optimierung (Zielordner: `06 Performance-Optimierung`) — 6 PDFs

Kursordner: `7_Databricks Performance Optimization\` — **beste Quelle ist `_MD\*.md`** (kondensierte Notizen), Bilder liegen im Top-Level-Ordner `assets\` (relativ referenziert) sowie `Includes\images\`.

**06-1 „Spark-Architektur & Adaptive Query Execution“** — Quelle: `_MD\1_Spark Architecture.md`. Inhalt: Jobs/Stages/Tasks, Driver/Executor/Cluster, Catalyst-Optimizer, Adaptive Query Execution (AQE), DataFrame vs. RDD.

**06-2 „Datenlayout: Data Skipping, Z-Ordering, Partitionierung“** — Quellen: `_MD\2_2_1 Data Skipping.md`, `_MD\2_2_2 Z-Ordering.md`, `_MD\2_2_3 Delta Lake Statistics.md`, `_MD\2_2_4 Partitioning.md`. Inhalt: Min/Max-Statistiken im Transaction Log, Z-Ordering (als Vorläufer, heute meist durch Liquid Clustering ersetzt), Partitionierungs-Use-Cases (GDPR-Löschungen, SCD2) und Risiken von Über-Partitionierung.

**06-3 „Liquid Clustering & Predictive Optimization“** — Quelle: `_MD\2_2_5 Liquid Clustering.md`. Inhalt: Vorteile (keine Kardinalitäts-Abstimmung, unempfindlich gegen Skew, inkrementelles OPTIMIZE), `CLUSTER BY`-Syntax, Predictive Optimization (automatisches OPTIMIZE/VACUUM, serverless).

**06-4 „Skew, Shuffle und Spill erkennen und beheben“** — Quellen: `_MD\3_1 Skew.md`, `_MD\3_2 Shuffles.md`, `_MD\3_3 Spill.md`. Inhalt: Ursachen von Data Skew und AQE-Skew-Handling, Shuffle-Mechanik (Wide vs. Narrow Transformations, Join-Strategien: Broadcast/Shuffle-Hash/Sort-Merge), Spill-Ursachen (RAM→Disk) und Gegenmaßnahmen.

**06-5 „Serialisierung & UDF-Performance“** — Quelle: `_MD\3_4 Serialization.md`. Inhalt: warum Python-UDFs teuer sind (Pickling pro Zeile, Catalyst-Optimierungsbarriere), Empfehlung Arrow-optimierte/vektorisierte UDFs zu nutzen.

**06-6 „Cluster-Auswahl: Photon, Spot-Instanzen & Serverless Compute“** — Quelle: `_MD\4 Fine-Tuning...md` (Cluster-Auswahl-Kapitel). Inhalt: Cluster-Typen (All-Purpose/Jobs/SQL-Warehouse), Photon-Engine, Spot-Instances mit On-Demand-Fallback, Autoscaling, Serverless Compute (heute GA für alle Compute-Typen).

Web-Recherche je PDF, z.B.: "Databricks liquid clustering documentation", "Databricks Photon engine", "Databricks Serverless compute GA 2026".

---

## 07 DevOps & CI-CD für Data Engineering (Zielordner: `07 DevOps und CI-CD`) — 5 PDFs

Kursordner: `4_DevOps Essentials for Data Engineering\Course Notebooks\M02 - CI\` und `...\M03 - CD\` (NICHT die `_Abschnitte`-Unterordner verwenden, das sind zerlegte Duplikate).

**07-1 „Software-Engineering-Best-Practices & Code-Modularisierung“** — Quellen: `01 Lecture - Intro to SWE Best Practices.ipynb`, `02 Lecture - Intro to Modularizing PySpark Code.ipynb`, `03 Demo - Modularizing PySpark Code (REQUIRED).ipynb`. Inhalt: warum monolithischer PySpark-Code schlecht wartbar ist, Refaktorierung in wiederverwendbare Funktionen (Beispielcode aus `src\helpers\project_functions.py` im Kursordner verwenden).

**07-2 „DevOps-, DataOps- und CI/CD-Grundlagen“** — Quellen: `05 Lecture - DevOps Fundamentals.ipynb`, `06 Lecture - The Role of CI and CD in DevOps.ipynb`, `07 Lecture - Planning the Project.ipynb`. Inhalt: DevOps-Lifecycle, Abgrenzung DevOps/DataOps/MLOps, Rolle von CI vs. CD, Umgebungsisolation (dev/stage/prod) mit Unity Catalog.

**07-3 „Unit Tests für PySpark (pytest, assertDataFrameEqual)“** — Quellen: `09 Lecture - Intro to Unit Tests for PySpark.ipynb`, `10 Demo - Creating and Executing Unit Tests.ipynb`, Datei `tests\unit_tests\test_spark_helper_functions.py` im Kursordner (echter Code!). Inhalt: `pyspark.testing.utils` (`assertDataFrameEqual`, `assertSchemaEqual`), pytest-Grundlagen, konkretes Testbeispiel aus der echten Testdatei.

**07-4 „Integrationstests mit Pipelines und Jobs“** — Quellen: `12 Lecture - Executing Integration Tests with SDP and Jobs.ipynb`, `13 Demo - Performing Integration Tests.ipynb`, Datei `tests\integration_test\integration_tests_sdp.py`. Inhalt: zwei Ansätze für Integrationstests (SDP-Expectations vs. Multi-Task-Jobs), Beispiel für Materialized-View-basierte Zeilenzahl-Validierung über dev/stage/prod.

**07-5 „Versionskontrolle mit Git & Databricks Git-Ordnern“** — Quellen: `14 Lecture - Version Control with Git Overview.ipynb`, `15 Lab - Version Control with Databricks Git Folders and GitHub.ipynb`, plus `M03 - CD\01 Lecture - Deploying Databricks Assets Overview.ipynb` als kurzer Ausblick auf Deployment (Brücke zu Ordner 08 Asset Bundles). Inhalt: Gitflow-Branching, Databricks Git-Folders, GitHub-PAT-Einrichtung, Repos-API für CI/CD.

Web-Recherche je PDF, z.B.: "Databricks pyspark testing assertDataFrameEqual documentation", "Databricks Git folders CI/CD".

---

## 08 Automatisiertes Deployment mit Asset Bundles (Zielordner: `08 Automatisiertes Deployment mit Asset Bundles`) — 4 PDFs

Kursordner: `8_Automated Deployment with Declarative Automation Bundles\` — jedes Modul hat einen eigenen Unterordner (`01`, `03`, `06`, `08_Using VSCode...`) mit Demo-Notebook UND echten Bundle-Dateien (`databricks.yml`, `resources\*.yml`) — diese echten YAML-Dateien unbedingt als Codebeispiele verwenden, nicht nur den Notebook-Text!

**08-1 „Grundlagen: databricks.yml & CLI-Lifecycle“** — Quelle: Modul `01` (Deploying a Simple DAB), dessen `databricks.yml`. Inhalt: was ist ein Declarative Automation Bundle (früher Databricks Asset Bundle/DAB), Grundstruktur von `databricks.yml`, CLI-Lifecycle: `databricks bundle validate/deploy/run/destroy` mit echten Befehlsbeispielen.

**08-2 „Multi-Environment-Deployments (Targets & Variablen)“** — Quelle: Modul `03` (Multiple Environments), dessen `databricks.yml`/`resources`. Inhalt: `targets`-Mapping (development/production), Bundle-Variablen, Lookup-Variablen, `include`-Mapping für modulare Resource-Dateien, echtes YAML-Beispiel mit zwei Targets.

**08-3 „CI/CD mit Asset Bundles (Tests + Pipelines kombiniert)“** — Quelle: Modul `06` (CI/CD with DABs), insbesondere der `Full Project`-Unterordner (`resources/job`, `resources/pipeline`, `src/dlt_pipelines`, `tests/unit_tests`, `tests/integration_test`). Inhalt: dreistufige Pipeline (dev/stage/prod), Kombination aus Unit-Tests, SDP-ETL-Pipeline und Integrationstests in einem Bundle, Verweis auf Ordner 07 (DevOps/Testing) als Grundlage.

**08-4 „Asset Bundles in VS Code“** — Quelle: Modul `08_Using VSCode...`. Inhalt: Databricks-VS-Code-Extension, PAT-Authentifizierung, YAML-Autovervollständigung/-Validierung, Deploy/Run direkt aus dem Editor.

Web-Recherche je PDF, z.B.: "Databricks Asset Bundles databricks.yml reference", "Databricks bundle targets variables lookup", "Databricks CLI bundle validate deploy".
