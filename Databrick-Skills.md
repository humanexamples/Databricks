# Databricks Tech-Skills für den Lebenslauf

★ = in Kurs-Labs praktisch umgesetzt

---

## Langfassung

**Plattform & Architektur**
- Databricks Data Intelligence Platform (Lakehouse), Medallion-Architektur ★
- Delta Lake ★, Apache Iceberg, UniForm
- Serverless & Classic Compute (All-Purpose, Jobs, SQL Warehouses), Cluster Policies ★

**Sprachen**
- Python ★, PySpark (DataFrame API) ★, SQL / Databricks SQL ★, pandas ★

**Data Ingestion**
- Lakeflow Connect ★, Auto Loader ★, `COPY INTO` ★, `read_files`
  - Standard Connectors ★: Cloud-Objektspeicher, SFTP, Kafka, Kinesis, Pub/Sub (Batch, inkrementelles Batch, Streaming)
  - Managed Connectors: SaaS (Salesforce, Workday, SharePoint u. a.) und Datenbanken mit CDC (SQL Server, PostgreSQL, MySQL) über Ingestion Gateway und Serverless-Pipelines
  - Partner Connect / Third-Party-Tools: Fivetran, Informatica, Qlik u. a.
- Schema Inference & Evolution ★
- Dateiformate: CSV, JSON, Parquet ★
- Semi-strukturierte Daten: VARIANT-Datentyp, JSON-Pfadsyntax ★
- Metadaten: Datei-Metadatenspalte (`_metadata`) für Herkunft und Ladezeitpunkt ★
- Volumes, External Locations ★

**Pipelines & Transformation**
- Lakeflow Spark Declarative Pipelines (SDP, ehem. Delta Live Tables / DLT) ★: Streaming Tables, Materialized Views, Expectations
- UDFs (Python, Pandas, Unity Catalog) ★
- Lakeflow Designer (No-Code ETL) ★

**Inkrementelle Verarbeitung & Modellierung**
- Change Data Capture (CDC, AUTO CDC), Change Data Feed (CDF) ★
- SCD Type 1 & 2, dimensionale Modellierung ★

**Streaming**
- Spark Structured Streaming ★ (Trigger, Checkpoints, `foreachBatch`)
- Streaming Joins ★: Stream-Snapshot (Stream-Static), Stream-Stream in Materialized Views, Stream-Stream in Streaming Tables
- Stateful Streaming, Watermarks

**Orchestrierung**
- Lakeflow Jobs (Workflows) ★: Job-Trigger (Schedule, File Arrival, Table Update, Continuous), Task-Typen
- Monitoring, Repair Runs ★

**Governance & Security**
- Unity Catalog ★: Privilegien (`GRANT` / `REVOKE`), Row Filters, Column Masks, Dynamic Views
- Zugriffsmodelle: RBAC (Rechte über Gruppen) ★, ABAC mit Governed Tags
- PII: Pseudonymisierung, Anonymisierung ★
- Lineage, Auditing, System Tables ★
- Delta Sharing, Clean Rooms

**Performance-Optimierung**
- Liquid Clustering ★, Partitioning, Z-Ordering, Data Skipping ★
- `OPTIMIZE`, `VACUUM`, Predictive Optimization ★
- Shuffle, Skew, Spill, Broadcast Joins, AQE, Photon, Spark UI ★

**DevOps & Testing**
- Git / GitHub, Git Folders ★
- Databricks Asset Bundles: CI/CD, Multi-Environment (Dev/Stage/Prod) ★
- GitHub Actions, Azure DevOps, Terraform
- Databricks CLI ★, VS Code Extension ★, Databricks Connect
- pytest, PySpark Testing Utils, Integrationstests ★
- MLOps-Grundlagen ★

**Apps & AI/BI**
- Databricks Apps ★, AI/BI Dashboards, Genie ★, AI Functions ★

**Design Patterns**
- Datenfluss: Fan-in (Multi-Flow), Fan-out, Multiplex, Sinks ★
- Data Quality & Resilienz: Quarantine Pattern, Bronze als STRING, Rescued Data & Schema Hints ★
- Expectation-Muster: Zeilenzahl-Validierung, Erkennung fehlender Datensätze, Primärschlüssel-Eindeutigkeit, NULL-tolerante Constraints ★
- Schreibstrategien: Append, Overwrite, Selective Overwrite (`REPLACE WHERE` / `REPLACE USING`), Upsert (`MERGE INTO`), Deduplizierung ★
- Historische Daten: Backfill zusätzlich zum Stream ★
- Datei-Ingestion: Append-only, überschriebene und wachsende Dateien, periodische Voll-Snapshots, späte und unsortierte Dateien, Korrekturläufe, Schema-Drift, zeitgefilterte Ingestion, Aufräumen verarbeiteter Dateien ★
- Orchestrierung: Master-Child (modulare Jobs), Control-Tabelle mit For-Each, inkrementelles Kopieren per Watermark, If/Else-Verzweigung ★

---

## Kompaktversion

> **Plattform:** Databricks Lakehouse, Delta Lake, Apache Spark, Medallion-Architektur
> **Sprachen:** Python, PySpark, SQL, pandas
> **Data Engineering:** Lakeflow Connect (Standard, Managed & Partner Connectors), Auto Loader, Spark Declarative Pipelines (SDP / DLT), Structured Streaming (inkl. Streaming Joins), CDC / CDF, SCD Type 1 & 2
> **Daten & Formate:** CSV, JSON, Parquet, VARIANT (semi-strukturierte Daten), Datei-Metadaten
> **Orchestrierung:** Lakeflow Jobs (Workflows)
> **Governance:** Unity Catalog, RBAC / ABAC, Row Filters, Column Masks, PII-Pseudonymisierung, Lineage
> **Performance:** Liquid Clustering, Data Skipping, AQE, Join- und Shuffle-Optimierung
> **DevOps:** Git/GitHub, Databricks Asset Bundles, CI/CD, pytest, Databricks CLI
> **Patterns:** Fan-in / Fan-out / Multiplex, Quarantine, Upsert & Deduplizierung, Backfill, Master-Child-Orchestrierung
