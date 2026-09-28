# Zuordnung: `_Zusammenfassung` → Prüfungsthemen (Data Engineer Associate)

Vollständige Zuordnung aller Markdown-Dateien im Ordner `_Zusammenfassung` (inkl. `_Ingestion`) zu den sieben offiziellen Prüfungsthemen aus [`databricksdataengineerassociate.md`](databricksdataengineerassociate.md). Die Zuordnung erfolgt pro Datei anhand ihres inhaltlichen Schwerpunkts; bei gemischten Ordnern (z. B. `05 SQL Language/03 Funktionen`, `10 Developers`, `12 Query Data`) wurde auf Datei- bzw. Unterordner-Ebene aufgeteilt statt den gesamten Ordner einem einzigen Thema zuzuschlagen.

**Gesamt:** 735 Dateien.

## Übersicht

| # | Prüfungsthema | Gewichtung | Anzahl Dateien |
|---|---|---|---|
| 1 | [Databricks Intelligence Platform](#platform) | 6 % | 66 |
| 2 | [Data Ingestion and Loading](#ingestion) | 21 % | 149 |
| 3 | [Data Transformation and Modeling](#transformation) | 22 % | 267 |
| 4 | [Working with Lakeflow Jobs](#jobs) | 16 % | 61 |
| 5 | [Implementing CI/CD](#cicd) | 10 % | 89 |
| 6 | [Troubleshooting, Monitoring, and Optimization](#troubleshooting) | 10 % | 16 |
| 7 | [Governance and Security](#governance) | 15 % | 86 |
| 8 | [Sonstiges (keinem Prüfungsthema direkt zugeordnet)](#sonstiges) | — | 1 |

---

## <a id="platform">1. Databricks Intelligence Platform</a>

**66 Dateien**

**`01 Platform/01 Architecture/`** (1 Datei)

- [01 Medallion Architecture](../_Zusammenfassung/01%20Platform/01%20Architecture/01%20Medallion%20Architecture.md)

**`01 Platform/01 Architecture/02 Production Planning/`** (11 Dateien)

- [00 Uebersicht](../_Zusammenfassung/01%20Platform/01%20Architecture/02%20Production%20Planning/00%20Uebersicht.md)
- [01 Account und Identitaet](../_Zusammenfassung/01%20Platform/01%20Architecture/02%20Production%20Planning/01%20Account%20und%20Identitaet.md)
- [02 Workspace-Strategie](../_Zusammenfassung/01%20Platform/01%20Architecture/02%20Production%20Planning/02%20Workspace-Strategie.md)
- [03 Unity Catalog Architektur](../_Zusammenfassung/01%20Platform/01%20Architecture/02%20Production%20Planning/03%20Unity%20Catalog%20Architektur.md)
- [04 Netzwerkarchitektur](../_Zusammenfassung/01%20Platform/01%20Architecture/02%20Production%20Planning/04%20Netzwerkarchitektur.md)
- [05 Storage-Architektur](../_Zusammenfassung/01%20Platform/01%20Architecture/02%20Production%20Planning/05%20Storage-Architektur.md)
- [06 Delta Lake Architektur](../_Zusammenfassung/01%20Platform/01%20Architecture/02%20Production%20Planning/06%20Delta%20Lake%20Architektur.md)
- [07 Infrastructure as Code](../_Zusammenfassung/01%20Platform/01%20Architecture/02%20Production%20Planning/07%20Infrastructure%20as%20Code.md)
- [08 Compute-Konfiguration](../_Zusammenfassung/01%20Platform/01%20Architecture/02%20Production%20Planning/08%20Compute-Konfiguration.md)
- [09 Observability-Strategie](../_Zusammenfassung/01%20Platform/01%20Architecture/02%20Production%20Planning/09%20Observability-Strategie.md)
- [10 High Availability und Disaster Recovery](../_Zusammenfassung/01%20Platform/01%20Architecture/02%20Production%20Planning/10%20High%20Availability%20und%20Disaster%20Recovery.md)

**`01 Platform/02 Tables/`** (8 Dateien)

- [01 Tabellenkonzepte und Tabellentypen](../_Zusammenfassung/01%20Platform/02%20Tables/01%20Tabellenkonzepte%20und%20Tabellentypen.md)
- [02 Delta Lake Grundlagen](../_Zusammenfassung/01%20Platform/02%20Tables/02%20Delta%20Lake%20Grundlagen.md)
- [03 Managed Tables](../_Zusammenfassung/01%20Platform/02%20Tables/03%20Managed%20Tables.md)
- [04 External und Foreign Tables](../_Zusammenfassung/01%20Platform/02%20Tables/04%20External%20und%20Foreign%20Tables.md)
- [05 Apache Iceberg](../_Zusammenfassung/01%20Platform/02%20Tables/05%20Apache%20Iceberg.md)
- [06 Schema und Tabellenhistorie](../_Zusammenfassung/01%20Platform/02%20Tables/06%20Schema%20und%20Tabellenhistorie.md)
- [08 Transactions](../_Zusammenfassung/01%20Platform/02%20Tables/08%20Transactions.md)
- [09 Tabellenlayout und Performance](../_Zusammenfassung/01%20Platform/02%20Tables/09%20Tabellenlayout%20und%20Performance.md)

**`01 Platform/02 Tables/07 Table Features/`** (16 Dateien)

- [01 Catalog Commits](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/01%20Catalog%20Commits.md)
- [02 Change Data Feed](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/02%20Change%20Data%20Feed.md)
- [03 Checkpoint V2](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/03%20Checkpoint%20V2.md)
- [04 Collation](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/04%20Collation.md)
- [05 Column Mapping](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/05%20Column%20Mapping.md)
- [06 Deletion Vectors](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/06%20Deletion%20Vectors.md)
- [07 Drop Feature](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/07%20Drop%20Feature.md)
- [08 Feature Compatibility](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/08%20Feature%20Compatibility.md)
- [09 Generated Columns](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/09%20Generated%20Columns.md)
- [10 Parquet v2](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/10%20Parquet%20v2.md)
- [11 Row Tracking](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/11%20Row%20Tracking.md)
- [12 Constraints](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/12%20Constraints.md)
- [13 Type Widening](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/13%20Type%20Widening.md)
- [14 Iceberg Reads (UniForm)](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/14%20Iceberg%20Reads%20%28UniForm%29.md)
- [15 Variant](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/15%20Variant.md)
- [16 Variant Shredding](../_Zusammenfassung/01%20Platform/02%20Tables/07%20Table%20Features/16%20Variant%20Shredding.md)

**`01 Platform/02 Tables/10 Tabellenoperationen/`** (2 Dateien)

- [01 Clone, Details und Metadaten](../_Zusammenfassung/01%20Platform/02%20Tables/10%20Tabellenoperationen/01%20Clone%2C%20Details%20und%20Metadaten.md)
- [02 DROP, OPTIMIZE, VACUUM und Auto-TTL](../_Zusammenfassung/01%20Platform/02%20Tables/10%20Tabellenoperationen/02%20DROP%2C%20OPTIMIZE%2C%20VACUUM%20und%20Auto-TTL.md)

**`01 Platform/03 Serverless Compute/`** (11 Dateien)

- [01 Uebersicht](../_Zusammenfassung/01%20Platform/03%20Serverless%20Compute/01%20Uebersicht.md)
- [02 Notebooks](../_Zusammenfassung/01%20Platform/03%20Serverless%20Compute/02%20Notebooks.md)
- [03 Git-Ordner (Git Folder Serverless)](../_Zusammenfassung/01%20Platform/03%20Serverless%20Compute/03%20Git-Ordner%20%28Git%20Folder%20Serverless%29.md)
- [04 Umgebung und Abhaengigkeiten](../_Zusammenfassung/01%20Platform/03%20Serverless%20Compute/04%20Umgebung%20und%20Abhaengigkeiten.md)
- [05 Best Practices](../_Zusammenfassung/01%20Platform/03%20Serverless%20Compute/05%20Best%20Practices.md)
- [06 Migration von Classic zu Serverless](../_Zusammenfassung/01%20Platform/03%20Serverless%20Compute/06%20Migration%20von%20Classic%20zu%20Serverless.md)
- [07 Streaming](../_Zusammenfassung/01%20Platform/03%20Serverless%20Compute/07%20Streaming.md)
- [08 Sandbox](../_Zusammenfassung/01%20Platform/03%20Serverless%20Compute/08%20Sandbox.md)
- [09 Einschraenkungen](../_Zusammenfassung/01%20Platform/03%20Serverless%20Compute/09%20Einschraenkungen.md)
- [10 Lakehouse Replay](../_Zusammenfassung/01%20Platform/03%20Serverless%20Compute/10%20Lakehouse%20Replay.md)
- [11 Serverless Compute verwalten](../_Zusammenfassung/01%20Platform/03%20Serverless%20Compute/11%20Serverless%20Compute%20verwalten.md)

**`04 Data guides/`** (1 Datei)

- [01 Magic Commands](../_Zusammenfassung/04%20Data%20guides/01%20Magic%20Commands.md)

**`04 Data guides/02 Work with files/`** (3 Dateien)

- [01 Datei-Speicheroptionen und Workspace Files](../_Zusammenfassung/04%20Data%20guides/02%20Work%20with%20files/01%20Datei-Speicheroptionen%20und%20Workspace%20Files.md)
- [02 Workspace Files als Code-Module](../_Zusammenfassung/04%20Data%20guides/02%20Work%20with%20files/02%20Workspace%20Files%20als%20Code-Module.md)
- [03 Unity Catalog Volumes](../_Zusammenfassung/04%20Data%20guides/02%20Work%20with%20files/03%20Unity%20Catalog%20Volumes.md)

**`04 Data guides/02 Work with files/04 DBFS/`** (3 Dateien)

- [01 DBFS Grundlagen](../_Zusammenfassung/04%20Data%20guides/02%20Work%20with%20files/04%20DBFS/01%20DBFS%20Grundlagen.md)
- [02 dbutils.fs — Befehlsreferenz](../_Zusammenfassung/04%20Data%20guides/02%20Work%20with%20files/04%20DBFS/02%20dbutils.fs%20%E2%80%94%20Befehlsreferenz.md)
- [03 Mounts und Migration](../_Zusammenfassung/04%20Data%20guides/02%20Work%20with%20files/04%20DBFS/03%20Mounts%20und%20Migration.md)

**`10 Developers/06 Databricks Utils/`** (9 Dateien)

- [00 Uebersicht](../_Zusammenfassung/10%20Developers/06%20Databricks%20Utils/00%20Uebersicht.md)
- [01 Credentials Utility (dbutils.credentials)](../_Zusammenfassung/10%20Developers/06%20Databricks%20Utils/01%20Credentials%20Utility%20%28dbutils.credentials%29.md)
- [02 Data Utility (dbutils.data)](../_Zusammenfassung/10%20Developers/06%20Databricks%20Utils/02%20Data%20Utility%20%28dbutils.data%29.md)
- [03 File System Utility (dbutils.fs)](../_Zusammenfassung/10%20Developers/06%20Databricks%20Utils/03%20File%20System%20Utility%20%28dbutils.fs%29.md)
- [04 Jobs Utility (dbutils.jobs)](../_Zusammenfassung/10%20Developers/06%20Databricks%20Utils/04%20Jobs%20Utility%20%28dbutils.jobs%29.md)
- [05 Library Utility (dbutils.library)](../_Zusammenfassung/10%20Developers/06%20Databricks%20Utils/05%20Library%20Utility%20%28dbutils.library%29.md)
- [06 Notebook Utility (dbutils.notebook)](../_Zusammenfassung/10%20Developers/06%20Databricks%20Utils/06%20Notebook%20Utility%20%28dbutils.notebook%29.md)
- [07 Secrets Utility (dbutils.secrets)](../_Zusammenfassung/10%20Developers/06%20Databricks%20Utils/07%20Secrets%20Utility%20%28dbutils.secrets%29.md)
- [08 Widgets Utility (dbutils.widgets)](../_Zusammenfassung/10%20Developers/06%20Databricks%20Utils/08%20Widgets%20Utility%20%28dbutils.widgets%29.md)

**`10 Developers/`** (1 Datei)

- [07 Databricks SDK fuer Python](../_Zusammenfassung/10%20Developers/07%20Databricks%20SDK%20fuer%20Python.md)

---

## <a id="ingestion">2. Data Ingestion and Loading</a>

**149 Dateien**

**`05 SQL Language/03 Funktionen/07 Datei-Funktionen/`** (2 Dateien)

- [copy_file](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/07%20Datei-Funktionen/copy_file.md)
- [read_files](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/07%20Datei-Funktionen/read_files/00%20%C3%9Cbersicht.md)

**`06 DML Statements/`** (1 Datei)

- [_copy_into](../_Zusammenfassung/06%20DML%20Statements/_copy_into.md)

**`07 Data Management/01 Data Engineering/02 Lakeflow Connect/01 Lakeflow Connect Managed Connectors/`** (1 Datei)

- [01 Managed Connectors Architektur](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/01%20Lakeflow%20Connect%20Managed%20Connectors/01%20Managed%20Connectors%20Architektur.md)

**`07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/`** (2 Dateien)

- [00 Standard Connector waehlen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/00%20Standard%20Connector%20waehlen.md)
- [01 Idempotenz_Databricks](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/01%20Idempotenz_Databricks.md)

**`07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/02 Batch Ingestion/`** (1 Datei)

- [01 Batch Ingestion](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/02%20Batch%20Ingestion/01%20Batch%20Ingestion.md)

**`07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/03 Incremental Batch Ingestion/`** (3 Dateien)

- [00 Overview](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/03%20Incremental%20Batch%20Ingestion/00%20Overview.md)
- [01 Auto_Loader](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/03%20Incremental%20Batch%20Ingestion/01%20Auto_Loader.md)
- [02 Incremental Batch Ingestion](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/03%20Incremental%20Batch%20Ingestion/02%20Incremental%20Batch%20Ingestion.md)

**`07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/04 Streaming Ingestion/`** (1 Datei)

- [01 Data Ingestion](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/04%20Streaming%20Ingestion/01%20Data%20Ingestion.md)

**`07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/05 Working with Files/`** (8 Dateien)

- [01 Read and Write Files](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/01%20Read%20and%20Write%20Files.md)
- [02 File_Tracking_Ingestion_Methoden](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/02%20File_Tracking_Ingestion_Methoden.md)
- [03 Vergleich_read_files_vs_spark_read](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Vergleich_read_files_vs_spark_read.md)
- [_Vergleich_read_files_vs_spark_read](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/_Vergleich_read_files_vs_spark_read.md)
- [_fileIngestionScenarios](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/_fileIngestionScenarios.md)
- [_read_files](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/_read_files.md)
- [_schema_Aspekte](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/_schema_Aspekte.md)
- [_spark_read](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/_spark_read.md)

**`07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/05 Working with Files/03 Spark API Options/`** (24 Dateien)

- [00 Überblick](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/00%20%C3%9Cberblick.md)
- [01 DataFrameReader — Common](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/01%20DataFrameReader%20%E2%80%94%20Common.md)
- [02 DataFrameReader — Avro](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/02%20DataFrameReader%20%E2%80%94%20Avro.md)
- [03 DataFrameReader — CSV](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/03%20DataFrameReader%20%E2%80%94%20CSV.md)
- [04 DataFrameReader — Excel](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/04%20DataFrameReader%20%E2%80%94%20Excel.md)
- [05 DataFrameReader — JSON](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/05%20DataFrameReader%20%E2%80%94%20JSON.md)
- [06 DataFrameReader — Kafka](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/06%20DataFrameReader%20%E2%80%94%20Kafka.md)
- [07 DataFrameReader — ORC](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/07%20DataFrameReader%20%E2%80%94%20ORC.md)
- [08 DataFrameReader — Parquet](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/08%20DataFrameReader%20%E2%80%94%20Parquet.md)
- [09 DataFrameReader — State store](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/09%20DataFrameReader%20%E2%80%94%20State%20store.md)
- [10 DataFrameReader — Text](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/10%20DataFrameReader%20%E2%80%94%20Text.md)
- [11 DataFrameReader — XML](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/11%20DataFrameReader%20%E2%80%94%20XML.md)
- [12 DataFrameWriter — Avro](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/12%20DataFrameWriter%20%E2%80%94%20Avro.md)
- [13 DataFrameWriter — Delta Lake und Apache Iceberg](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/13%20DataFrameWriter%20%E2%80%94%20Delta%20Lake%20und%20Apache%20Iceberg.md)
- [14 DataFrameWriter — CSV](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/14%20DataFrameWriter%20%E2%80%94%20CSV.md)
- [15 DataFrameWriter — Excel](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/15%20DataFrameWriter%20%E2%80%94%20Excel.md)
- [16 DataFrameWriter — JSON](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/16%20DataFrameWriter%20%E2%80%94%20JSON.md)
- [17 DataFrameWriter — ORC](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/17%20DataFrameWriter%20%E2%80%94%20ORC.md)
- [18 DataFrameWriter — Parquet](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/18%20DataFrameWriter%20%E2%80%94%20Parquet.md)
- [19 DataFrameWriter — Text](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/19%20DataFrameWriter%20%E2%80%94%20Text.md)
- [20 DataFrameWriter — XML](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/20%20DataFrameWriter%20%E2%80%94%20XML.md)
- [21 DataStreamReader — Common](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/21%20DataStreamReader%20%E2%80%94%20Common.md)
- [22 DataStreamReader — Auto Loader](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/22%20DataStreamReader%20%E2%80%94%20Auto%20Loader.md)
- [23 DataStreamReader — Kafka](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/23%20DataStreamReader%20%E2%80%94%20Kafka.md)

**`07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/05 Working with Files/04 Dateitypen/`** (9 Dateien)

- [01 Ingesting CSV](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/04%20Dateitypen/01%20Ingesting%20CSV.md)
- [02 Ingesting JSON](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/04%20Dateitypen/02%20Ingesting%20JSON.md)
- [03 Ingesting Text](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/04%20Dateitypen/03%20Ingesting%20Text.md)
- [04 Ingesting Excel](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/04%20Dateitypen/04%20Ingesting%20Excel.md)
- [05 Ingesting XML](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/04%20Dateitypen/05%20Ingesting%20XML.md)
- [06 Ingesting Parquet](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/04%20Dateitypen/06%20Ingesting%20Parquet.md)
- [07 Ingesting Avro](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/04%20Dateitypen/07%20Ingesting%20Avro.md)
- [08 Ingesting ORC](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/04%20Dateitypen/08%20Ingesting%20ORC.md)
- [09 State Store](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/04%20Dateitypen/09%20State%20Store.md)

**`07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/05 Working with Files/05 Diagnose- und Herkunftsspalten/`** (4 Dateien)

- [01 MetaData](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/05%20Diagnose-%20und%20Herkunftsspalten/01%20MetaData.md)
- [02 Rescuing Malformed Rows](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/05%20Diagnose-%20und%20Herkunftsspalten/02%20Rescuing%20Malformed%20Rows.md)
- [_metadata](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/05%20Diagnose-%20und%20Herkunftsspalten/_metadata.md)
- [_rescued_data](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/05%20Diagnose-%20und%20Herkunftsspalten/_rescued_data.md)

**`07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/05 Working with Files/06 Auto Loader/`** (18 Dateien)

- [00 Überblick](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/00%20%C3%9Cberblick.md)
- [01 Schema-Inferenz und -Evolution](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/01%20Schema-Inferenz%20und%20-Evolution.md)
- [02 Automatisches Type Widening](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/02%20Automatisches%20Type%20Widening.md)
- [03 Unity-Catalog-Integration](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/03%20Unity-Catalog-Integration.md)
- [04 Datei-Erkennungsmodi](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/04%20Datei-Erkennungsmodi.md)
- [05 Directory Listing Mode](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/05%20Directory%20Listing%20Mode.md)
- [06 File Notification Mode](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/06%20File%20Notification%20Mode.md)
- [07 Wie File Events funktionieren](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/07%20Wie%20File%20Events%20funktionieren.md)
- [08 Migration zu File Events](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/08%20Migration%20zu%20File%20Events.md)
- [09 Datei-Tracking und Checkpoints](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/09%20Datei-Tracking%20und%20Checkpoints.md)
- [10 Clean Source (Quelldateien aufräumen)](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/10%20Clean%20Source%20%28Quelldateien%20aufr%C3%A4umen%29.md)
- [11 Best Practices](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/11%20Best%20Practices.md)
- [12 Produktionsbetrieb](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/12%20Produktionsbetrieb.md)
- [13 Observability](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/13%20Observability.md)
- [14 Common Data Loading Patterns](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/14%20Common%20Data%20Loading%20Patterns.md)
- [15 FAQ](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/15%20FAQ.md)
- [16 Auto Loader vs read_files vs COPY INTO](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/16%20Auto%20Loader%20vs%20read_files%20vs%20COPY%20INTO.md)
- [17 Quellen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/17%20Quellen.md)

**`07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/05 Working with Files/06 Auto Loader/Options/`** (47 Dateien)

- [README](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/README.md)
- [cloudFiles.allowOverwrites](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.allowOverwrites.md)
- [cloudFiles.awsAccessKey](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.awsAccessKey.md)
- [cloudFiles.awsSecretKey](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.awsSecretKey.md)
- [cloudFiles.backfillInterval](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.backfillInterval.md)
- [cloudFiles.cleanSource](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.cleanSource.md)
- [cloudFiles.cleanSource.moveDestination](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.cleanSource.moveDestination.md)
- [cloudFiles.cleanSource.retentionDuration](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.cleanSource.retentionDuration.md)
- [cloudFiles.client](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.client.md)
- [cloudFiles.clientEmail](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.clientEmail.md)
- [cloudFiles.clientId](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.clientId.md)
- [cloudFiles.clientSecret](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.clientSecret.md)
- [cloudFiles.connectionString](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.connectionString.md)
- [cloudFiles.fetchParallelism](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.fetchParallelism.md)
- [cloudFiles.format](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.format.md)
- [cloudFiles.includeExistingFiles](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.includeExistingFiles.md)
- [cloudFiles.inferColumnTypes](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.inferColumnTypes.md)
- [cloudFiles.listOnStart](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.listOnStart.md)
- [cloudFiles.maxBytesPerTrigger](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.maxBytesPerTrigger.md)
- [cloudFiles.maxFileAge](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.maxFileAge.md)
- [cloudFiles.maxFilesPerTrigger](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.maxFilesPerTrigger.md)
- [cloudFiles.partitionColumns](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.partitionColumns.md)
- [cloudFiles.pathRewrites](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.pathRewrites.md)
- [cloudFiles.privateKey](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.privateKey.md)
- [cloudFiles.privateKeyId](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.privateKeyId.md)
- [cloudFiles.project](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.project.md)
- [cloudFiles.queueName](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.queueName.md)
- [cloudFiles.queueUrl](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.queueUrl.md)
- [cloudFiles.region](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.region.md)
- [cloudFiles.resourceGroup](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.resourceGroup.md)
- [cloudFiles.resourceTag](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.resourceTag.md)
- [cloudFiles.roleArn](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.roleArn.md)
- [cloudFiles.roleExternalId](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.roleExternalId.md)
- [cloudFiles.roleSessionName](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.roleSessionName.md)
- [cloudFiles.schemaEvolutionMode](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.schemaEvolutionMode.md)
- [cloudFiles.schemaHints](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.schemaHints.md)
- [cloudFiles.schemaLocation](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.schemaLocation.md)
- [cloudFiles.stsEndpoint](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.stsEndpoint.md)
- [cloudFiles.subscription](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.subscription.md)
- [cloudFiles.subscriptionId](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.subscriptionId.md)
- [cloudFiles.tenantId](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.tenantId.md)
- [cloudFiles.useIncrementalListing](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.useIncrementalListing.md)
- [cloudFiles.useManagedFileEvents](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.useManagedFileEvents.md)
- [cloudFiles.useNotifications](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.useNotifications.md)
- [cloudFiles.useStrictGlobber](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.useStrictGlobber.md)
- [cloudFiles.validateOptions](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/cloudFiles.validateOptions.md)
- [databricks.serviceCredential](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/Options/databricks.serviceCredential.md)

**`07 Data Management/01 Data Engineering/02 Lakeflow Connect/`** (1 Datei)

- [03 Other Ingestion Features](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/03%20Other%20Ingestion%20Features.md)

**`12 Query Data/`** (1 Datei)

- [00 Query data - Uebersicht](../_Zusammenfassung/12%20Query%20Data/00%20Query%20data%20-%20Uebersicht.md)

**`12 Query Data/01 Dateiformate/`** (3 Dateien)

- [01 CSV lesen und schreiben](../_Zusammenfassung/12%20Query%20Data/01%20Dateiformate/01%20CSV%20lesen%20und%20schreiben.md)
- [02 JSON lesen und schreiben](../_Zusammenfassung/12%20Query%20Data/01%20Dateiformate/02%20JSON%20lesen%20und%20schreiben.md)
- [03 Parquet lesen und schreiben](../_Zusammenfassung/12%20Query%20Data/01%20Dateiformate/03%20Parquet%20lesen%20und%20schreiben.md)

**`_Ingestion/Datei Ingestion Varianten/`** (16 Dateien)

- [00 Uebersicht](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/00%20Uebersicht.md)
- [01 Einmaliger, statischer Bestand](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/01%20Einmaliger%2C%20statischer%20Bestand.md)
- [02 Append-only](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/02%20Append-only.md)
- [03 Gleiche Datei wird ueberschrieben](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/03%20Gleiche%20Datei%20wird%20ueberschrieben.md)
- [04 Datei waechst](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/04%20Datei%20waechst.md)
- [05 Periodische Voll-Snapshots](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/05%20Periodische%20Voll-Snapshots.md)
- [06 Change-Events in Dateien](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/06%20Change-Events%20in%20Dateien.md)
- [07 Backfill zusaetzlich zum Stream](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/07%20Backfill%20zusaetzlich%20zum%20Stream.md)
- [08 Spaete, unsortierte Dateien](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/08%20Spaete%2C%20unsortierte%20Dateien.md)
- [09 Korrektur, Teilmenge neu laden](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/09%20Korrektur%2C%20Teilmenge%20neu%20laden.md)
- [10 Mehrere Quellordner (Multiplex)](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/10%20Mehrere%20Quellordner%20%28Multiplex%29.md)
- [11 Schema aendert sich ueber die Zeit](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/11%20Schema%20aendert%20sich%20ueber%20die%20Zeit.md)
- [12 Zeitfenster- und gefilterte Ingestion](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/12%20Zeitfenster-%20und%20gefilterte%20Ingestion.md)
- [13 Verarbeitete Dateien aufraeumen](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/13%20Verarbeitete%20Dateien%20aufraeumen.md)
- [98 Trigger und Zeitplanung](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/98%20Trigger%20und%20Zeitplanung.md)
- [99 Dedup und Upsert Muster](../_Zusammenfassung/_Ingestion/Datei%20Ingestion%20Varianten/99%20Dedup%20und%20Upsert%20Muster.md)

**`_Ingestion/`** (7 Dateien)

- [File Tracking](../_Zusammenfassung/_Ingestion/File%20Tracking.md)
- [Metadata (_metadata)](../_Zusammenfassung/_Ingestion/Metadata%20%28_metadata%29.md)
- [Rescued Data](../_Zusammenfassung/_Ingestion/Rescued%20Data.md)
- [Schema Definition (StructType)](../_Zusammenfassung/_Ingestion/Schema%20Definition%20%28StructType%29.md)
- [Schema Enforcement](../_Zusammenfassung/_Ingestion/Schema%20Enforcement.md)
- [Schema Evolution](../_Zusammenfassung/_Ingestion/Schema%20Evolution.md)
- [Schema Inference](../_Zusammenfassung/_Ingestion/Schema%20Inference.md)

---

## <a id="transformation">3. Data Transformation and Modeling</a>

**267 Dateien**

**`05 SQL Language/`** (1 Datei)

- [01 databricks_identifier](../_Zusammenfassung/05%20SQL%20Language/01%20databricks_identifier.md)

**`05 SQL Language/03 Funktionen/`** (1 Datei)

- [00 Uebersicht](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/00%20Uebersicht.md)

**`05 SQL Language/03 Funktionen/01 Cast und Typkonvertierung/`** (7 Dateien)

- [cast](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/01%20Cast%20und%20Typkonvertierung/cast.md)
- [coloncolonsign](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/01%20Cast%20und%20Typkonvertierung/coloncolonsign.md)
- [date](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/01%20Cast%20und%20Typkonvertierung/date.md)
- [questiondoublecolonsign](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/01%20Cast%20und%20Typkonvertierung/questiondoublecolonsign.md)
- [string](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/01%20Cast%20und%20Typkonvertierung/string.md)
- [timestamp](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/01%20Cast%20und%20Typkonvertierung/timestamp.md)
- [typeof](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/01%20Cast%20und%20Typkonvertierung/typeof.md)

**`05 SQL Language/03 Funktionen/02 Datum und Zeit/`** (5 Dateien)

- [to_char](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/02%20Datum%20und%20Zeit/to_char.md)
- [to_date](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/02%20Datum%20und%20Zeit/to_date.md)
- [to_timestamp](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/02%20Datum%20und%20Zeit/to_timestamp.md)
- [trunc](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/02%20Datum%20und%20Zeit/trunc.md)
- [unix_timestamp](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/02%20Datum%20und%20Zeit/unix_timestamp.md)

**`05 SQL Language/03 Funktionen/03 NULL-Behandlung/`** (3 Dateien)

- [coalesce](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/03%20NULL-Behandlung/coalesce.md)
- [isnotnull](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/03%20NULL-Behandlung/isnotnull.md)
- [isnull](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/03%20NULL-Behandlung/isnull.md)

**`05 SQL Language/03 Funktionen/04 String/`** (9 Dateien)

- [concat](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/04%20String/concat.md)
- [concat_ws](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/04%20String/concat_ws.md)
- [split](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/04%20String/split.md)
- [substr](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/04%20String/substr.md)
- [substring](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/04%20String/substring.md)
- [substring_index](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/04%20String/substring_index.md)
- [trim](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/04%20String/trim.md)
- [unbase64](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/04%20String/unbase64.md)
- [upper](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/04%20String/upper.md)

**`05 SQL Language/03 Funktionen/05 Array/`** (1 Datei)

- [slice](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/05%20Array/slice.md)

**`05 SQL Language/03 Funktionen/06 JSON, CSV und VARIANT/`** (9 Dateien)

- [colonsign](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/06%20JSON%2C%20CSV%20und%20VARIANT/colonsign.md)
- [from_csv](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/06%20JSON%2C%20CSV%20und%20VARIANT/from_csv.md)
- [from_json](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/06%20JSON%2C%20CSV%20und%20VARIANT/from_json.md)
- [parse_json](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/06%20JSON%2C%20CSV%20und%20VARIANT/parse_json.md)
- [schema_of_csv](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/06%20JSON%2C%20CSV%20und%20VARIANT/schema_of_csv.md)
- [schema_of_json](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/06%20JSON%2C%20CSV%20und%20VARIANT/schema_of_json.md)
- [schema_of_json_agg](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/06%20JSON%2C%20CSV%20und%20VARIANT/schema_of_json_agg.md)
- [schema_of_variant](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/06%20JSON%2C%20CSV%20und%20VARIANT/schema_of_variant.md)
- [schema_of_variant_agg](../_Zusammenfassung/05%20SQL%20Language/03%20Funktionen/06%20JSON%2C%20CSV%20und%20VARIANT/schema_of_variant_agg.md)

**`05 SQL Language/04 Datentypen/`** (1 Datei)

- [01 VARIANT](../_Zusammenfassung/05%20SQL%20Language/04%20Datentypen/01%20VARIANT.md)

**`06 DML Statements/`** (1 Datei)

- [_merge_into](../_Zusammenfassung/06%20DML%20Statements/_merge_into.md)

**`07 Data Management/01 Data Engineering/01 Concepts/`** (9 Dateien)

- [01-prozedural-vs-deklarativ](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/01%20Concepts/01-prozedural-vs-deklarativ.md)
- [02-batch-vs-streaming](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/01%20Concepts/02-batch-vs-streaming.md)
- [03-tabellen-vs-views](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/01%20Concepts/03-tabellen-vs-views.md)
- [04-schema-evolution](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/01%20Concepts/04-schema-evolution.md)
- [05-was-ist-cdc](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/01%20Concepts/05-was-ist-cdc.md)
- [06-join](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/01%20Concepts/06-join.md)
- [07-aggregation](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/01%20Concepts/07-aggregation.md)
- [08-merge](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/01%20Concepts/08-merge.md)
- [09-selective-overwrite](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/01%20Concepts/09-selective-overwrite.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/01 Concepts/`** (11 Dateien)

- [00 Uebersicht](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/01%20Concepts/00%20Uebersicht.md)
- [01 Was ist Spark Declarative Pipelines](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/01%20Concepts/01%20Was%20ist%20Spark%20Declarative%20Pipelines.md)
- [02 Wo ist DLT geblieben](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/01%20Concepts/02%20Wo%20ist%20DLT%20geblieben.md)
- [03 Pipelines](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/01%20Concepts/03%20Pipelines.md)
- [04 Standalone Pipelines](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/01%20Concepts/04%20Standalone%20Pipelines.md)
- [05 Views](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/01%20Concepts/05%20Views.md)
- [06 Materialized Views](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/01%20Concepts/06%20Materialized%20Views.md)
- [07 Streaming Tables](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/01%20Concepts/07%20Streaming%20Tables.md)
- [08 Refresh-Semantik](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/01%20Concepts/08%20Refresh-Semantik.md)
- [09 Pipeline-Modi (Triggered vs Continuous)](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/01%20Concepts/09%20Pipeline-Modi%20%28Triggered%20vs%20Continuous%29.md)
- [10 Serverless vs Classic Compute](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/01%20Concepts/10%20Serverless%20vs%20Classic%20Compute.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/02 Tutorials/`** (5 Dateien)

- [00 Tutorials-Uebersicht](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/02%20Tutorials/00%20Tutorials-Uebersicht.md)
- [01 Tutorial - Erste Pipeline](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/02%20Tutorials/01%20Tutorial%20-%20Erste%20Pipeline.md)
- [02 Tutorial - Pipelines mit mehreren Quellen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/02%20Tutorials/02%20Tutorial%20-%20Pipelines%20mit%20mehreren%20Quellen.md)
- [03 Tutorial - Datei-Pipelines](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/02%20Tutorials/03%20Tutorial%20-%20Datei-Pipelines.md)
- [04 Tutorial - Geodaten-Pipelines](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/02%20Tutorials/04%20Tutorial%20-%20Geodaten-Pipelines.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/03 Build und Entwicklung/`** (10 Dateien)

- [01 Pipelines erstellen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/03%20Build%20und%20Entwicklung/01%20Pipelines%20erstellen.md)
- [02 Notebook-Entwicklungserfahrung](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/03%20Build%20und%20Entwicklung/02%20Notebook-Entwicklungserfahrung.md)
- [03 Multi-File-Editor](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/03%20Build%20und%20Entwicklung/03%20Multi-File-Editor.md)
- [04 Workspace-Dateien importieren](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/03%20Build%20und%20Entwicklung/04%20Workspace-Dateien%20importieren.md)
- [05 Lokal entwickeln](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/03%20Build%20und%20Entwicklung/05%20Lokal%20entwickeln.md)
- [06 Source Control](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/03%20Build%20und%20Entwicklung/06%20Source%20Control.md)
- [07 Unit Testing](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/03%20Build%20und%20Entwicklung/07%20Unit%20Testing.md)
- [08 Berechtigungen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/03%20Build%20und%20Entwicklung/08%20Berechtigungen.md)
- [09 Konvertierung zu Databricks Asset Bundles](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/03%20Build%20und%20Entwicklung/09%20Konvertierung%20zu%20Databricks%20Asset%20Bundles.md)
- [10 Data Engineering Agent](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/03%20Build%20und%20Entwicklung/10%20Data%20Engineering%20Agent.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/04 Ingestion und Laden von Daten/`** (4 Dateien)

- [01 Daten laden](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/04%20Ingestion%20und%20Laden%20von%20Daten/01%20Daten%20laden.md)
- [02 Schema Evolution aus JSON](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/04%20Ingestion%20und%20Laden%20von%20Daten/02%20Schema%20Evolution%20aus%20JSON.md)
- [03 API-Ingestion](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/04%20Ingestion%20und%20Laden%20von%20Daten/03%20API-Ingestion.md)
- [04 Event Hubs](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/04%20Ingestion%20und%20Laden%20von%20Daten/04%20Event%20Hubs.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/05 CDC/`** (5 Dateien)

- [01 CDC-Grundlagen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/05%20CDC/01%20CDC-Grundlagen.md)
- [02 Change Data Feed](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/05%20CDC/02%20Change%20Data%20Feed.md)
- [03 SCD Type 1 vs Type 2](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/05%20CDC/03%20SCD%20Type%201%20vs%20Type%202.md)
- [04 Datenbank-Replikation](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/05%20CDC/04%20Datenbank-Replikation.md)
- [05 CDC fortgeschritten](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/05%20CDC/05%20CDC%20fortgeschritten.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/06 Flows/`** (7 Dateien)

- [01 Flows](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/06%20Flows/01%20Flows.md)
- [02 Flow-Beispiele](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/06%20Flows/02%20Flow-Beispiele.md)
- [03 Flow-Muster (Fan-in, Fan-out, Multiplex)](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/06%20Flows/03%20Flow-Muster%20%28Fan-in%2C%20Fan-out%2C%20Multiplex%29.md)
- [04 Backfill mit Flows](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/06%20Flows/04%20Backfill%20mit%20Flows.md)
- [05 Flows mit REPLACE WHERE](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/06%20Flows/05%20Flows%20mit%20REPLACE%20WHERE.md)
- [06 Flows mit REPLACE USING](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/06%20Flows/06%20Flows%20mit%20REPLACE%20USING.md)
- [07 foreachBatch](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/06%20Flows/07%20foreachBatch.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/07 Transformationen/`** (4 Dateien)

- [01 Transform-Grundlagen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/07%20Transformationen/01%20Transform-Grundlagen.md)
- [02 Inkrementelles Refresh](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/07%20Transformationen/02%20Inkrementelles%20Refresh.md)
- [03 Full Refresh von Streaming Tables](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/07%20Transformationen/03%20Full%20Refresh%20von%20Streaming%20Tables.md)
- [04 Zustandsbehaftete Verarbeitung](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/07%20Transformationen/04%20Zustandsbehaftete%20Verarbeitung.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/08 Data Quality (Expectations)/`** (2 Dateien)

- [01 Expectations-Grundlagen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/08%20Data%20Quality%20%28Expectations%29/01%20Expectations-Grundlagen.md)
- [02 Expectation-Patterns](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/08%20Data%20Quality%20%28Expectations%29/02%20Expectation-Patterns.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/09 Sinks/`** (2 Dateien)

- [01 Sinks](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/09%20Sinks/01%20Sinks.md)
- [02 Sinks in Lakeflow Pipelines](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/09%20Sinks/02%20Sinks%20in%20Lakeflow%20Pipelines.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/10 Governance und Zugriff/`** (2 Dateien)

- [01 Externer Zugriff](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/10%20Governance%20und%20Zugriff/01%20Externer%20Zugriff.md)
- [02 GDPR](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/10%20Governance%20und%20Zugriff/02%20GDPR.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/11 Konfiguration und Compute/`** (7 Dateien)

- [01 Pipeline konfigurieren](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/11%20Konfiguration%20und%20Compute/01%20Pipeline%20konfigurieren.md)
- [02 Ziel-Schema](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/11%20Konfiguration%20und%20Compute/02%20Ziel-Schema.md)
- [03 Compute konfigurieren](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/11%20Konfiguration%20und%20Compute/03%20Compute%20konfigurieren.md)
- [04 Serverless](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/11%20Konfiguration%20und%20Compute/04%20Serverless.md)
- [05 Autoscaling](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/11%20Konfiguration%20und%20Compute/05%20Autoscaling.md)
- [06 Echtzeit-Verarbeitung](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/11%20Konfiguration%20und%20Compute/06%20Echtzeit-Verarbeitung.md)
- [07 Workflows-Integration](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/11%20Konfiguration%20und%20Compute/07%20Workflows-Integration.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/12 Unity Catalog und Schema-Verwaltung/`** (10 Dateien)

- [01 Unity Catalog](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/12%20Unity%20Catalog%20und%20Schema-Verwaltung/01%20Unity%20Catalog.md)
- [02 Hive Metastore](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/12%20Unity%20Catalog%20und%20Schema-Verwaltung/02%20Hive%20Metastore.md)
- [03 HMS zu UC klonen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/12%20Unity%20Catalog%20und%20Schema-Verwaltung/03%20HMS%20zu%20UC%20klonen.md)
- [04 Migration zu DPM](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/12%20Unity%20Catalog%20und%20Schema-Verwaltung/04%20Migration%20zu%20DPM.md)
- [05 Live Schema](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/12%20Unity%20Catalog%20und%20Schema-Verwaltung/05%20Live%20Schema.md)
- [06 ALTER-SQL-Nutzung](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/12%20Unity%20Catalog%20und%20Schema-Verwaltung/06%20ALTER-SQL-Nutzung.md)
- [07 Updates](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/12%20Unity%20Catalog%20und%20Schema-Verwaltung/07%20Updates.md)
- [08 Properties](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/12%20Unity%20Catalog%20und%20Schema-Verwaltung/08%20Properties.md)
- [09 Parameter](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/12%20Unity%20Catalog%20und%20Schema-Verwaltung/09%20Parameter.md)
- [10 Tabellen verschieben](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/12%20Unity%20Catalog%20und%20Schema-Verwaltung/10%20Tabellen%20verschieben.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/13 Observability/`** (8 Dateien)

- [00 Observability-Uebersicht](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/13%20Observability/00%20Observability-Uebersicht.md)
- [01 Monitoring-UI](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/13%20Observability/01%20Monitoring-UI.md)
- [02 Event Logs ueberwachen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/13%20Observability/02%20Event%20Logs%20ueberwachen.md)
- [03 Event-Log-Schema](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/13%20Observability/03%20Event-Log-Schema.md)
- [04 Query History](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/13%20Observability/04%20Query%20History.md)
- [05 Event Hooks](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/13%20Observability/05%20Event%20Hooks.md)
- [06 Streaming wiederherstellen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/13%20Observability/06%20Streaming%20wiederherstellen.md)
- [07 Hohe Initialisierungszeit beheben](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/13%20Observability/07%20Hohe%20Initialisierungszeit%20beheben.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/14 Developer Reference/`** (12 Dateien)

- [00 Uebersicht](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/00%20Uebersicht.md)
- [01 SQL vs Python](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/01%20SQL%20vs%20Python.md)
- [02 SQL-Entwicklung](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/02%20SQL-Entwicklung.md)
- [03 SQL-Referenz-Uebersicht](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/03%20SQL-Referenz-Uebersicht.md)
- [05 Python-Entwicklung](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/05%20Python-Entwicklung.md)
- [06 Python-API-Referenz-Uebersicht](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/06%20Python-API-Referenz-Uebersicht.md)
- [08 Definition-Funktion](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/08%20Definition-Funktion.md)
- [09 Metaprogrammierung](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/09%20Metaprogrammierung.md)
- [10 Environment-Versionen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/10%20Environment-Versionen.md)
- [11 Environment-Versionskompatibilitaet](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/11%20Environment-Versionskompatibilitaet.md)
- [12 Externe Abhaengigkeiten](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/12%20Externe%20Abhaengigkeiten.md)
- [13 DLT-Meta](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/13%20DLT-Meta.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/14 Developer Reference/04 SQL-Referenz/`** (9 Dateien)

- [01 CREATE VIEW](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/04%20SQL-Referenz/01%20CREATE%20VIEW.md)
- [02 CREATE TEMPORARY VIEW](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/04%20SQL-Referenz/02%20CREATE%20TEMPORARY%20VIEW.md)
- [03 CREATE MATERIALIZED VIEW](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/04%20SQL-Referenz/03%20CREATE%20MATERIALIZED%20VIEW.md)
- [04 CREATE MATERIALIZED VIEW Refresh Policy](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/04%20SQL-Referenz/04%20CREATE%20MATERIALIZED%20VIEW%20Refresh%20Policy.md)
- [05 CREATE STREAMING TABLE](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/04%20SQL-Referenz/05%20CREATE%20STREAMING%20TABLE.md)
- [06 CREATE TABLE ... FLOW](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/04%20SQL-Referenz/06%20CREATE%20TABLE%20...%20FLOW.md)
- [07 CREATE FLOW](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/04%20SQL-Referenz/07%20CREATE%20FLOW.md)
- [08 AUTO CDC INTO](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/04%20SQL-Referenz/08%20AUTO%20CDC%20INTO.md)
- [09 REFRESH (MV oder ST)](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/04%20SQL-Referenz/09%20REFRESH%20%28MV%20oder%20ST%29.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/14 Developer Reference/07 Python-Referenz/`** (13 Dateien)

- [01 table](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/01%20table.md)
- [02 view](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/02%20view.md)
- [03 materialized_view](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/03%20materialized_view.md)
- [04 streaming_table](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/04%20streaming_table.md)
- [05 create_table](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/05%20create_table.md)
- [06 expectations](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/06%20expectations.md)
- [07 append_flow](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/07%20append_flow.md)
- [08 replace_flow](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/08%20replace_flow.md)
- [09 update_flow](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/09%20update_flow.md)
- [10 apply_changes](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/10%20apply_changes.md)
- [11 apply_changes_from_snapshot](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/11%20apply_changes_from_snapshot.md)
- [12 sink](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/12%20sink.md)
- [13 foreach_batch_sink](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/14%20Developer%20Reference/07%20Python-Referenz/13%20foreach_batch_sink.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/15 Databricks SQL fuer LDP/`** (9 Dateien)

- [00 Uebersicht](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/15%20Databricks%20SQL%20fuer%20LDP/00%20Uebersicht.md)
- [01 Materialized Views (DBSQL)](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/15%20Databricks%20SQL%20fuer%20LDP/01%20Materialized%20Views%20%28DBSQL%29.md)
- [02 Materialized Views konfigurieren](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/15%20Databricks%20SQL%20fuer%20LDP/02%20Materialized%20Views%20konfigurieren.md)
- [03 Materialized Views ueberwachen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/15%20Databricks%20SQL%20fuer%20LDP/03%20Materialized%20Views%20ueberwachen.md)
- [04 Refresh-Zeitplaene](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/15%20Databricks%20SQL%20fuer%20LDP/04%20Refresh-Zeitplaene.md)
- [05 Streaming](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/15%20Databricks%20SQL%20fuer%20LDP/05%20Streaming.md)
- [06 Flows mit REPLACE WHERE (DBSQL)](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/15%20Databricks%20SQL%20fuer%20LDP/06%20Flows%20mit%20REPLACE%20WHERE%20%28DBSQL%29.md)
- [07 Python nutzen (DBSQL)](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/15%20Databricks%20SQL%20fuer%20LDP/07%20Python%20nutzen%20%28DBSQL%29.md)
- [08 Compute](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/15%20Databricks%20SQL%20fuer%20LDP/08%20Compute.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/16 Best Practices/`** (5 Dateien)

- [00 Uebersicht](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/16%20Best%20Practices/00%20Uebersicht.md)
- [01 Datasets organisieren](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/16%20Best%20Practices/01%20Datasets%20organisieren.md)
- [02 Dimensionale Modellierung](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/16%20Best%20Practices/02%20Dimensionale%20Modellierung.md)
- [03 Verarbeitungsgarantien](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/16%20Best%20Practices/03%20Verarbeitungsgarantien.md)
- [04 Produktionsreife](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/16%20Best%20Practices/04%20Produktionsreife.md)

**`07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/`** (1 Datei)

- [17 Einschraenkungen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/03%20Lakeflow%20Pipelines/17%20Einschraenkungen.md)

**`08 Apache Spark/01 Structured Streaming/01 Grundlagen/`** (3 Dateien)

- [01 Konzepte](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/01%20Grundlagen/01%20Konzepte.md)
- [02 Tutorial](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/01%20Grundlagen/02%20Tutorial.md)
- [03 Beispiele](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/01%20Grundlagen/03%20Beispiele.md)

**`08 Apache Spark/01 Structured Streaming/02 Ausfuehrungsmodell/`** (4 Dateien)

- [01 Output-Modes](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/02%20Ausfuehrungsmodell/01%20Output-Modes.md)
- [02 Trigger](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/02%20Ausfuehrungsmodell/02%20Trigger.md)
- [03 Batch-Groesse](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/02%20Ausfuehrungsmodell/03%20Batch-Groesse.md)
- [04 Checkpoints](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/02%20Ausfuehrungsmodell/04%20Checkpoints.md)

**`08 Apache Spark/01 Structured Streaming/03 Zustandsbehaftete Verarbeitung/`** (5 Dateien)

- [01 Stateless Streaming](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/03%20Zustandsbehaftete%20Verarbeitung/01%20Stateless%20Streaming.md)
- [02 Stateful Streaming](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/03%20Zustandsbehaftete%20Verarbeitung/02%20Stateful%20Streaming.md)
- [03 Watermarks](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/03%20Zustandsbehaftete%20Verarbeitung/03%20Watermarks.md)
- [04 State lesen](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/03%20Zustandsbehaftete%20Verarbeitung/04%20State%20lesen.md)
- [05 State Repartitionierung](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/03%20Zustandsbehaftete%20Verarbeitung/05%20State%20Repartitionierung.md)

**`08 Apache Spark/01 Structured Streaming/04 Real-Time Mode/`** (8 Dateien)

- [00 Uebersicht](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/04%20Real-Time%20Mode/00%20Uebersicht.md)
- [01 Konzepte](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/04%20Real-Time%20Mode/01%20Konzepte.md)
- [02 Setup](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/04%20Real-Time%20Mode/02%20Setup.md)
- [03 Tutorial](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/04%20Real-Time%20Mode/03%20Tutorial.md)
- [04 Performance](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/04%20Real-Time%20Mode/04%20Performance.md)
- [05 Referenz](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/04%20Real-Time%20Mode/05%20Referenz.md)
- [06 Einschraenkungen](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/04%20Real-Time%20Mode/06%20Einschraenkungen.md)
- [07 Beispiele](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/04%20Real-Time%20Mode/07%20Beispiele.md)

**`08 Apache Spark/01 Structured Streaming/05 Stateful Applications/`** (5 Dateien)

- [00 Uebersicht](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/05%20Stateful%20Applications/00%20Uebersicht.md)
- [01 Schema-Evolution](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/05%20Stateful%20Applications/01%20Schema-Evolution.md)
- [02 Asynchrone Verarbeitung](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/05%20Stateful%20Applications/02%20Asynchrone%20Verarbeitung.md)
- [03 Legacy](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/05%20Stateful%20Applications/03%20Legacy.md)
- [04 Beispiele](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/05%20Stateful%20Applications/04%20Beispiele.md)

**`08 Apache Spark/01 Structured Streaming/06 Monitoring und Governance/`** (2 Dateien)

- [01 Stream-Monitoring](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/06%20Monitoring%20und%20Governance/01%20Stream-Monitoring.md)
- [02 Unity Catalog](../_Zusammenfassung/08%20Apache%20Spark/01%20Structured%20Streaming/06%20Monitoring%20und%20Governance/02%20Unity%20Catalog.md)

**`08 Apache Spark/02 PySpark/`** (2 Dateien)

- [01 Ueberblick und Basics](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/01%20Ueberblick%20und%20Basics.md)
- [02 Custom Data Sources](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/02%20Custom%20Data%20Sources.md)

**`08 Apache Spark/02 PySpark/03 DataFrameReader/`** (9 Dateien)

- [00 Uebersicht](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/03%20DataFrameReader/00%20Uebersicht.md)
- [01 format](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/03%20DataFrameReader/01%20format.md)
- [02 schema](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/03%20DataFrameReader/02%20schema.md)
- [03 option](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/03%20DataFrameReader/03%20option.md)
- [04 options](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/03%20DataFrameReader/04%20options.md)
- [05 load](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/03%20DataFrameReader/05%20load.md)
- [06 csv](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/03%20DataFrameReader/06%20csv.md)
- [07 json](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/03%20DataFrameReader/07%20json.md)
- [08 text](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/03%20DataFrameReader/08%20text.md)

**`08 Apache Spark/02 PySpark/04 DataFrameWriter/`** (14 Dateien)

- [00 Uebersicht](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/00%20Uebersicht.md)
- [01 format](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/01%20format.md)
- [02 mode](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/02%20mode.md)
- [03 option](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/03%20option.md)
- [04 options](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/04%20options.md)
- [05 save](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/05%20save.md)
- [06 csv](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/06%20csv.md)
- [07 json](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/07%20json.md)
- [08 text](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/08%20text.md)
- [09 saveAsTable](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/09%20saveAsTable.md)
- [10 insertInto](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/10%20insertInto.md)
- [11 partitionBy](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/11%20partitionBy.md)
- [12 sortBy](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/12%20sortBy.md)
- [13 clusterBy](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/04%20DataFrameWriter/13%20clusterBy.md)

**`08 Apache Spark/02 PySpark/05 DataStreamWriter/`** (14 Dateien)

- [00 Uebersicht](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/00%20Uebersicht.md)
- [01 format](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/01%20format.md)
- [02 option](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/02%20option.md)
- [03 options](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/03%20options.md)
- [04 outputMode](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/04%20outputMode.md)
- [05 partitionBy](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/05%20partitionBy.md)
- [06 clusterBy](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/06%20clusterBy.md)
- [07 trigger](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/07%20trigger.md)
- [08 queryName](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/08%20queryName.md)
- [09 foreach](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/09%20foreach.md)
- [10 foreachBatch](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/10%20foreachBatch.md)
- [11 start](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/11%20start.md)
- [12 toTable](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/12%20toTable.md)
- [13 table](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/05%20DataStreamWriter/13%20table.md)

**`08 Apache Spark/02 PySpark/06 DataStreamReader/`** (16 Dateien)

- [00 Uebersicht](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/00%20Uebersicht.md)
- [01 format](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/01%20format.md)
- [02 schema](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/02%20schema.md)
- [03 option](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/03%20option.md)
- [04 options](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/04%20options.md)
- [05 load](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/05%20load.md)
- [06 csv](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/06%20csv.md)
- [07 json](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/07%20json.md)
- [08 parquet](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/08%20parquet.md)
- [09 orc](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/09%20orc.md)
- [10 text](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/10%20text.md)
- [11 xml](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/11%20xml.md)
- [12 excel](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/12%20excel.md)
- [13 table](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/13%20table.md)
- [14 name](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/14%20name.md)
- [15 changes](../_Zusammenfassung/08%20Apache%20Spark/02%20PySpark/06%20DataStreamReader/15%20changes.md)

**`10 Developers/05 UDFs/`** (2 Dateien)

- [00 Overview](../_Zusammenfassung/10%20Developers/05%20UDFs/00%20Overview.md)
- [03 UDF Task Context](../_Zusammenfassung/10%20Developers/05%20UDFs/03%20UDF%20Task%20Context.md)

**`10 Developers/05 UDFs/01 Unity Catalog UDFs/`** (4 Dateien)

- [01 SQL und Python UDFs (Unity Catalog)](../_Zusammenfassung/10%20Developers/05%20UDFs/01%20Unity%20Catalog%20UDFs/01%20SQL%20und%20Python%20UDFs%20%28Unity%20Catalog%29.md)
- [02 Scala und Java UDFs (Unity Catalog)](../_Zusammenfassung/10%20Developers/05%20UDFs/01%20Unity%20Catalog%20UDFs/02%20Scala%20und%20Java%20UDFs%20%28Unity%20Catalog%29.md)
- [03 Batch Python UDFs (Unity Catalog)](../_Zusammenfassung/10%20Developers/05%20UDFs/01%20Unity%20Catalog%20UDFs/03%20Batch%20Python%20UDFs%20%28Unity%20Catalog%29.md)
- [04 Python UDTFs (Unity Catalog)](../_Zusammenfassung/10%20Developers/05%20UDFs/01%20Unity%20Catalog%20UDFs/04%20Python%20UDTFs%20%28Unity%20Catalog%29.md)

**`10 Developers/05 UDFs/02 Session-scoped UDFs/`** (5 Dateien)

- [01 Python Scalar UDFs](../_Zusammenfassung/10%20Developers/05%20UDFs/02%20Session-scoped%20UDFs/01%20Python%20Scalar%20UDFs.md)
- [02 Pandas UDFs](../_Zusammenfassung/10%20Developers/05%20UDFs/02%20Session-scoped%20UDFs/02%20Pandas%20UDFs.md)
- [03 Python UDTFs](../_Zusammenfassung/10%20Developers/05%20UDFs/02%20Session-scoped%20UDFs/03%20Python%20UDTFs.md)
- [04 Scala und Java UDFs](../_Zusammenfassung/10%20Developers/05%20UDFs/02%20Session-scoped%20UDFs/04%20Scala%20und%20Java%20UDFs.md)
- [05 Scala UDAFs](../_Zusammenfassung/10%20Developers/05%20UDFs/02%20Session-scoped%20UDFs/05%20Scala%20UDAFs.md)

**`12 Query Data/02 Semi-strukturierte Daten/`** (1 Datei)

- [01 JSON-Strings abfragen](../_Zusammenfassung/12%20Query%20Data/02%20Semi-strukturierte%20Daten/01%20JSON-Strings%20abfragen.md)

---

## <a id="jobs">4. Working with Lakeflow Jobs</a>

**61 Dateien**

**`07 Data Management/01 Data Engineering/04 Lakeflow Jobs/01 Uebersicht/`** (4 Dateien)

- [01 Was sind Jobs](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/01%20Uebersicht/01%20Was%20sind%20Jobs.md)
- [02 Schnellstart](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/01%20Uebersicht/02%20Schnellstart.md)
- [03 Jobs automatisieren](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/01%20Uebersicht/03%20Jobs%20automatisieren.md)
- [04 Best Practices fuer Produktion](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/01%20Uebersicht/04%20Best%20Practices%20fuer%20Produktion.md)

**`07 Data Management/01 Data Engineering/04 Lakeflow Jobs/02 Job erstellen und konfigurieren/`** (9 Dateien)

- [01 Job konfigurieren](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/02%20Job%20erstellen%20und%20konfigurieren/01%20Job%20konfigurieren.md)
- [02 Wiederkehrenden Job erstellen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/02%20Job%20erstellen%20und%20konfigurieren/02%20Wiederkehrenden%20Job%20erstellen.md)
- [03 Compute fuer Jobs](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/02%20Job%20erstellen%20und%20konfigurieren/03%20Compute%20fuer%20Jobs.md)
- [04 Classic Jobs](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/02%20Job%20erstellen%20und%20konfigurieren/04%20Classic%20Jobs.md)
- [05 Serverless Jobs](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/02%20Job%20erstellen%20und%20konfigurieren/05%20Serverless%20Jobs.md)
- [06 Umgebungsvariablen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/02%20Job%20erstellen%20und%20konfigurieren/06%20Umgebungsvariablen.md)
- [07 Git-Integration](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/02%20Job%20erstellen%20und%20konfigurieren/07%20Git-Integration.md)
- [08 Grosse Jobs](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/02%20Job%20erstellen%20und%20konfigurieren/08%20Grosse%20Jobs.md)
- [09 Backfill-Jobs](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/02%20Job%20erstellen%20und%20konfigurieren/09%20Backfill-Jobs.md)

**`07 Data Management/01 Data Engineering/04 Lakeflow Jobs/03 Trigger und Zeitplanung/`** (7 Dateien)

- [01 Trigger-Typen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/03%20Trigger%20und%20Zeitplanung/01%20Trigger-Typen.md)
- [02 Zeitgesteuert](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/03%20Trigger%20und%20Zeitplanung/02%20Zeitgesteuert.md)
- [03 Jetzt ausfuehren](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/03%20Trigger%20und%20Zeitplanung/03%20Jetzt%20ausfuehren.md)
- [04 Continuous Jobs](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/03%20Trigger%20und%20Zeitplanung/04%20Continuous%20Jobs.md)
- [05 Datei-Ankunfts-Trigger](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/03%20Trigger%20und%20Zeitplanung/05%20Datei-Ankunfts-Trigger.md)
- [06 Tabellen-Update-Trigger](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/03%20Trigger%20und%20Zeitplanung/06%20Tabellen-Update-Trigger.md)
- [07 Modell-Update-Trigger](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/03%20Trigger%20und%20Zeitplanung/07%20Modell-Update-Trigger.md)

**`07 Data Management/01 Data Engineering/04 Lakeflow Jobs/04 Tasks und Control Flow/`** (11 Dateien)

- [01 Task konfigurieren](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/04%20Tasks%20und%20Control%20Flow/01%20Task%20konfigurieren.md)
- [02 Control Flow](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/04%20Tasks%20und%20Control%20Flow/02%20Control%20Flow.md)
- [03 Bedingte Ausfuehrung (Run If)](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/04%20Tasks%20und%20Control%20Flow/03%20Bedingte%20Ausfuehrung%20%28Run%20If%29.md)
- [04 If-Else Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/04%20Tasks%20und%20Control%20Flow/04%20If-Else%20Task.md)
- [05 For-Each Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/04%20Tasks%20und%20Control%20Flow/05%20For-Each%20Task.md)
- [06 For-Each Lookup Beispiel](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/04%20Tasks%20und%20Control%20Flow/06%20For-Each%20Lookup%20Beispiel.md)
- [07 ForEach SQL-Lookup-Tutorial](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/04%20Tasks%20und%20Control%20Flow/07%20ForEach%20SQL-Lookup-Tutorial.md)
- [08 ForEach Watermark-Tutorial](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/04%20Tasks%20und%20Control%20Flow/08%20ForEach%20Watermark-Tutorial.md)
- [09 Run-Job-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/04%20Tasks%20und%20Control%20Flow/09%20Run-Job-Task.md)
- [10 Modulares Job-Design](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/04%20Tasks%20und%20Control%20Flow/10%20Modulares%20Job-Design.md)
- [11 Deaktivierte Tasks](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/04%20Tasks%20und%20Control%20Flow/11%20Deaktivierte%20Tasks.md)

**`07 Data Management/01 Data Engineering/04 Lakeflow Jobs/05 Task-Typen/`** (19 Dateien)

- [01 Notebook-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/01%20Notebook-Task.md)
- [02 Python-Script-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/02%20Python-Script-Task.md)
- [03 Python-Wheel-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/03%20Python-Wheel-Task.md)
- [04 Python-Wheels-in-Workflows](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/04%20Python-Wheels-in-Workflows.md)
- [05 SQL-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/05%20SQL-Task.md)
- [06 Pipeline-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/06%20Pipeline-Task.md)
- [07 Dashboard-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/07%20Dashboard-Task.md)
- [08 Alert-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/08%20Alert-Task.md)
- [09 dbt-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/09%20dbt-Task.md)
- [10 dbt-Platform-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/10%20dbt-Platform-Task.md)
- [11 dbt-in-Workflows](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/11%20dbt-in-Workflows.md)
- [12 JAR-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/12%20JAR-Task.md)
- [13 JAR erstellen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/13%20JAR%20erstellen.md)
- [14 JARs-in-Workflows](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/14%20JARs-in-Workflows.md)
- [15 Spark-Submit-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/15%20Spark-Submit-Task.md)
- [16 Spark-Submit-Legacy](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/16%20Spark-Submit-Legacy.md)
- [17 Power-BI-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/17%20Power-BI-Task.md)
- [18 Clean-Room-Notebook-Task](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/18%20Clean-Room-Notebook-Task.md)
- [19 Airflow-mit-Jobs](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/05%20Task-Typen/19%20Airflow-mit-Jobs.md)

**`07 Data Management/01 Data Engineering/04 Lakeflow Jobs/06 Berechtigungen und Monitoring/`** (5 Dateien)

- [01 Privilegien](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/06%20Berechtigungen%20und%20Monitoring/01%20Privilegien.md)
- [02 Monitoring](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/06%20Berechtigungen%20und%20Monitoring/02%20Monitoring.md)
- [03 Benachrichtigungen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/06%20Berechtigungen%20und%20Monitoring/03%20Benachrichtigungen.md)
- [04 Fehler beheben (Repair)](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/06%20Berechtigungen%20und%20Monitoring/04%20Fehler%20beheben%20%28Repair%29.md)
- [05 Performance diagnostizieren](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/06%20Berechtigungen%20und%20Monitoring/05%20Performance%20diagnostizieren.md)

**`07 Data Management/01 Data Engineering/04 Lakeflow Jobs/07 Parameter/`** (6 Dateien)

- [00 Parameter-Uebersicht](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/07%20Parameter/00%20Parameter-Uebersicht.md)
- [01 Job-Parameter](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/07%20Parameter/01%20Job-Parameter.md)
- [02 Task-Parameter](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/07%20Parameter/02%20Task-Parameter.md)
- [03 Parameter-Nutzung](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/07%20Parameter/03%20Parameter-Nutzung.md)
- [04 Dynamische Wertreferenzen](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/07%20Parameter/04%20Dynamische%20Wertreferenzen.md)
- [05 Task-Values](../_Zusammenfassung/07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/07%20Parameter/05%20Task-Values.md)

---

## <a id="cicd">5. Implementing CI/CD</a>

**89 Dateien**

**`10 Developers/01 Git Folders (Repos)/`** (7 Dateien)

- [00 Uebersicht](../_Zusammenfassung/10%20Developers/01%20Git%20Folders%20%28Repos%29/00%20Uebersicht.md)
- [01 Grundlagen](../_Zusammenfassung/10%20Developers/01%20Git%20Folders%20%28Repos%29/01%20Grundlagen.md)
- [02 Git-Integration konfigurieren](../_Zusammenfassung/10%20Developers/01%20Git%20Folders%20%28Repos%29/02%20Git-Integration%20konfigurieren.md)
- [03 Git-Operationen](../_Zusammenfassung/10%20Developers/01%20Git%20Folders%20%28Repos%29/03%20Git-Operationen.md)
- [04 CI-CD und Automatisierung](../_Zusammenfassung/10%20Developers/01%20Git%20Folders%20%28Repos%29/04%20CI-CD%20und%20Automatisierung.md)
- [05 Administration und private Netzwerke](../_Zusammenfassung/10%20Developers/01%20Git%20Folders%20%28Repos%29/05%20Administration%20und%20private%20Netzwerke.md)
- [06 Fehlerbehebung](../_Zusammenfassung/10%20Developers/01%20Git%20Folders%20%28Repos%29/06%20Fehlerbehebung.md)

**`10 Developers/02 CI-CD/`** (6 Dateien)

- [00 Uebersicht](../_Zusammenfassung/10%20Developers/02%20CI-CD/00%20Uebersicht.md)
- [01 Grundlagen und Empfehlungen](../_Zusammenfassung/10%20Developers/02%20CI-CD/01%20Grundlagen%20und%20Empfehlungen.md)
- [02 CI-CD-Workflows und Best Practices](../_Zusammenfassung/10%20Developers/02%20CI-CD/02%20CI-CD-Workflows%20und%20Best%20Practices.md)
- [03 Azure DevOps Integration](../_Zusammenfassung/10%20Developers/02%20CI-CD/03%20Azure%20DevOps%20Integration.md)
- [04 GitHub Actions Integration](../_Zusammenfassung/10%20Developers/02%20CI-CD/04%20GitHub%20Actions%20Integration.md)
- [05 Jenkins Integration](../_Zusammenfassung/10%20Developers/02%20CI-CD/05%20Jenkins%20Integration.md)

**`10 Developers/03 Databricks Asset Bundles (DAB)/`** (24 Dateien)

- [00 Uebersicht](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/00%20Uebersicht.md)
- [01 Grundlagen](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/01%20Grundlagen.md)
- [02 Tutorials - Jobs, Pipelines, Apps](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/02%20Tutorials%20-%20Jobs%2C%20Pipelines%2C%20Apps.md)
- [03 Python- und Scala-Artefakte](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/03%20Python-%20und%20Scala-Artefakte.md)
- [04 Templates](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/04%20Templates.md)
- [05 Konfiguration (databricks.yml)](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/05%20Konfiguration%20%28databricks.yml%29.md)
- [06 Bundles im Workspace (Web-UI)](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/06%20Bundles%20im%20Workspace%20%28Web-UI%29.md)
- [07 Deployment-Modi und Authentifizierung](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/07%20Deployment-Modi%20und%20Authentifizierung.md)
- [08 Zusammenarbeit und gemeinsame Dateien](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/08%20Zusammenarbeit%20und%20gemeinsame%20Dateien.md)
- [09 Manuelle Bundle-Erstellung und Ressourcen-Migration](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/09%20Manuelle%20Bundle-Erstellung%20und%20Ressourcen-Migration.md)
- [10 MLOps Stacks](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/10%20MLOps%20Stacks.md)
- [11 Direct Deployment Engine](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/11%20Direct%20Deployment%20Engine.md)
- [12 Air-Gapped-Umgebungen](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/12%20Air-Gapped-Umgebungen.md)
- [13 FAQ](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/13%20FAQ.md)
- [14 VS Code Extension](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/14%20VS%20Code%20Extension.md)
- [15 Ressourcentypen (Referenz)](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/15%20Ressourcentypen%20%28Referenz%29.md)
- [16 Job-Task-Typen](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/16%20Job-Task-Typen.md)
- [17 Job-Parameter](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/17%20Job-Parameter.md)
- [18 Run As](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/18%20Run%20As.md)
- [19 Berechtigungen (Permissions)](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/19%20Berechtigungen%20%28Permissions%29.md)
- [20 Overrides zwischen Targets](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/20%20Overrides%20zwischen%20Targets.md)
- [21 Private Artefakte](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/21%20Private%20Artefakte.md)
- [22 Bibliotheksabhaengigkeiten](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/22%20Bibliotheksabhaengigkeiten.md)
- [23 Beispiele (bundle-examples Repo)](../_Zusammenfassung/10%20Developers/03%20Databricks%20Asset%20Bundles%20%28DAB%29/23%20Beispiele%20%28bundle-examples%20Repo%29.md)

**`10 Developers/04 Terraform/`** (8 Dateien)

- [00 Uebersicht](../_Zusammenfassung/10%20Developers/04%20Terraform/00%20Uebersicht.md)
- [01 Grundlagen](../_Zusammenfassung/10%20Developers/04%20Terraform/01%20Grundlagen.md)
- [02 Workspace bereitstellen und verwalten](../_Zusammenfassung/10%20Developers/04%20Terraform/02%20Workspace%20bereitstellen%20und%20verwalten.md)
- [03 Cluster, Notebook und Job bereitstellen](../_Zusammenfassung/10%20Developers/04%20Terraform/03%20Cluster%2C%20Notebook%20und%20Job%20bereitstellen.md)
- [04 Unity Catalog automatisieren](../_Zusammenfassung/10%20Developers/04%20Terraform/04%20Unity%20Catalog%20automatisieren.md)
- [05 Service Principals bereitstellen](../_Zusammenfassung/10%20Developers/04%20Terraform/05%20Service%20Principals%20bereitstellen.md)
- [06 CDKTF](../_Zusammenfassung/10%20Developers/04%20Terraform/06%20CDKTF.md)
- [07 Fehlerbehebung](../_Zusammenfassung/10%20Developers/04%20Terraform/07%20Fehlerbehebung.md)

**`10 Developers/Authenticate developer tools/`** (16 Dateien)

- [00 Uebersicht](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/00%20Uebersicht.md)
- [01 Zugriff auf Databricks autorisieren](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/01%20Zugriff%20auf%20Databricks%20autorisieren.md)
- [02 OAuth Token Federation — Ueberblick](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/02%20OAuth%20Token%20Federation%20%E2%80%94%20Ueberblick.md)
- [03 Federation Policy konfigurieren](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/03%20Federation%20Policy%20konfigurieren.md)
- [04 Workload Identity Federation in CI-CD aktivieren](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/04%20Workload%20Identity%20Federation%20in%20CI-CD%20aktivieren.md)
- [05 Provider — GitHub Actions](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/05%20Provider%20%E2%80%94%20GitHub%20Actions.md)
- [06 Provider — Azure DevOps](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/06%20Provider%20%E2%80%94%20Azure%20DevOps.md)
- [07 Provider — AWS IAM](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/07%20Provider%20%E2%80%94%20AWS%20IAM.md)
- [08 Provider — Terraform Cloud, Bitbucket, Jenkins](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/08%20Provider%20%E2%80%94%20Terraform%20Cloud%2C%20Bitbucket%2C%20Jenkins.md)
- [09 Mit IdP-Token authentifizieren (Token Exchange)](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/09%20Mit%20IdP-Token%20authentifizieren%20%28Token%20Exchange%29.md)
- [10 OAuth U2M — Benutzerzugriff](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/10%20OAuth%20U2M%20%E2%80%94%20Benutzerzugriff.md)
- [11 Service Principals für CI-CD](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/11%20Service%20Principals%20f%C3%BCr%20CI-CD.md)
- [12 Unified Authentication](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/12%20Unified%20Authentication.md)
- [13 Umgebungsvariablen und Felder](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/13%20Umgebungsvariablen%20und%20Felder.md)
- [14 Konfigurationsprofile](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/14%20Konfigurationsprofile.md)
- [15 Personal Access Tokens (PAT)](../_Zusammenfassung/10%20Developers/Authenticate%20developer%20tools/15%20Personal%20Access%20Tokens%20%28PAT%29.md)

**`11 Testing/`** (1 Datei)

- [00 Uebersicht](../_Zusammenfassung/11%20Testing/00%20Uebersicht.md)

**`11 Testing/01 Unit Test/`** (12 Dateien)

- [01 Notebook-Testing Grundlagen](../_Zusammenfassung/11%20Testing/01%20Unit%20Test/01%20Notebook-Testing%20Grundlagen.md)
- [02 Python-Unit-Tests im Workspace (UI)](../_Zusammenfassung/11%20Testing/01%20Unit%20Test/02%20Python-Unit-Tests%20im%20Workspace%20%28UI%29.md)
- [03 Testing mit Databricks Connect](../_Zusammenfassung/11%20Testing/01%20Unit%20Test/03%20Testing%20mit%20Databricks%20Connect.md)
- [04 pytest in der VS-Code-Extension](../_Zusammenfassung/11%20Testing/01%20Unit%20Test/04%20pytest%20in%20der%20VS-Code-Extension.md)
- [05 Notebook Workflows als Testing-Orchestrierung (Legacy-Beispiel)](../_Zusammenfassung/11%20Testing/01%20Unit%20Test/05%20Notebook%20Workflows%20als%20Testing-Orchestrierung%20%28Legacy-Beispiel%29.md)
- [06 Notebook Best Practices (Software Engineering)](../_Zusammenfassung/11%20Testing/01%20Unit%20Test/06%20Notebook%20Best%20Practices%20%28Software%20Engineering%29.md)
- [07 PySpark-Testing-Utilities und Praxisbeispiel](../_Zusammenfassung/11%20Testing/01%20Unit%20Test/07%20PySpark-Testing-Utilities%20und%20Praxisbeispiel.md)
- [08 pytest — Grundlagen und Referenz](../_Zusammenfassung/11%20Testing/01%20Unit%20Test/08%20pytest%20%E2%80%94%20Grundlagen%20und%20Referenz.md)
- [09 chispa — PySpark-Testbibliothek](../_Zusammenfassung/11%20Testing/01%20Unit%20Test/09%20chispa%20%E2%80%94%20PySpark-Testbibliothek.md)
- [10 nutter — Databricks-Notebook-Testing](../_Zusammenfassung/11%20Testing/01%20Unit%20Test/10%20nutter%20%E2%80%94%20Databricks-Notebook-Testing.md)
- [11 unittest — Python-Standardbibliothek-Referenz](../_Zusammenfassung/11%20Testing/01%20Unit%20Test/11%20unittest%20%E2%80%94%20Python-Standardbibliothek-Referenz.md)
- [12 assertDataFrameEqual und assertSchemaEqual (API-Referenz)](../_Zusammenfassung/11%20Testing/01%20Unit%20Test/12%20assertDataFrameEqual%20und%20assertSchemaEqual%20%28API-Referenz%29.md)

**`11 Testing/02 Integrationstest/`** (3 Dateien)

- [01 Lakeflow Pipelines Unit Testing](../_Zusammenfassung/11%20Testing/02%20Integrationstest/01%20Lakeflow%20Pipelines%20Unit%20Testing.md)
- [02 Integrationstest-Konzepte auf Databricks](../_Zusammenfassung/11%20Testing/02%20Integrationstest/02%20Integrationstest-Konzepte%20auf%20Databricks.md)
- [03 SDP-Integrationstest-Patterns (Praxisbeispiel)](../_Zusammenfassung/11%20Testing/02%20Integrationstest/03%20SDP-Integrationstest-Patterns%20%28Praxisbeispiel%29.md)

**`11 Testing/03 CI-CD/`** (2 Dateien)

- [01 CI-CD Best Practices](../_Zusammenfassung/11%20Testing/03%20CI-CD/01%20CI-CD%20Best%20Practices.md)
- [02 Blog - CI-CD Praxisbeispiele und Software-Engineering-Kultur](../_Zusammenfassung/11%20Testing/03%20CI-CD/02%20Blog%20-%20CI-CD%20Praxisbeispiele%20und%20Software-Engineering-Kultur.md)

**`11 Testing/04 Git Workflow/`** (4 Dateien)

- [01 Jobs mit Git-Quellcode](../_Zusammenfassung/11%20Testing/04%20Git%20Workflow/01%20Jobs%20mit%20Git-Quellcode.md)
- [02 Blog - Repos-Historie und Features](../_Zusammenfassung/11%20Testing/04%20Git%20Workflow/02%20Blog%20-%20Repos-Historie%20und%20Features.md)
- [03 Blog - Asset Bundles und Git-Workflows (Ankuendigungen)](../_Zusammenfassung/11%20Testing/04%20Git%20Workflow/03%20Blog%20-%20Asset%20Bundles%20und%20Git-Workflows%20%28Ankuendigungen%29.md)
- [04 Blog - Lakebase Database Branching](../_Zusammenfassung/11%20Testing/04%20Git%20Workflow/04%20Blog%20-%20Lakebase%20Database%20Branching.md)

**`11 Testing/05 Andere Themen/`** (6 Dateien)

- [01 ML-Lifecycle](../_Zusammenfassung/11%20Testing/05%20Andere%20Themen/01%20ML-Lifecycle.md)
- [02 MLOps-Workflow](../_Zusammenfassung/11%20Testing/05%20Andere%20Themen/02%20MLOps-Workflow.md)
- [03 Python-Entwicklung auf Databricks](../_Zusammenfassung/11%20Testing/05%20Andere%20Themen/03%20Python-Entwicklung%20auf%20Databricks.md)
- [04 Allgemeine Developer Best Practices](../_Zusammenfassung/11%20Testing/05%20Andere%20Themen/04%20Allgemeine%20Developer%20Best%20Practices.md)
- [05 Blog - MLOps, DataOps und KI-gestuetzte Entwicklung](../_Zusammenfassung/11%20Testing/05%20Andere%20Themen/05%20Blog%20-%20MLOps%2C%20DataOps%20und%20KI-gestuetzte%20Entwicklung.md)
- [06 dbx (Legacy, archiviert)](../_Zusammenfassung/11%20Testing/05%20Andere%20Themen/06%20dbx%20%28Legacy%2C%20archiviert%29.md)

---

## <a id="troubleshooting">6. Troubleshooting, Monitoring, and Optimization</a>

**16 Dateien**

**`05 SQL Language/02 Aussagen und Metriken/01 Tabellen Analysieren/`** (3 Dateien)

- [01 ANALYZE TABLE COMPUTE STATISTICS](../_Zusammenfassung/05%20SQL%20Language/02%20Aussagen%20und%20Metriken/01%20Tabellen%20Analysieren/01%20ANALYZE%20TABLE%20COMPUTE%20STATISTICS.md)
- [02 ANALYZE TABLE COMPUTE STORAGE METRICS](../_Zusammenfassung/05%20SQL%20Language/02%20Aussagen%20und%20Metriken/01%20Tabellen%20Analysieren/02%20ANALYZE%20TABLE%20COMPUTE%20STORAGE%20METRICS.md)
- [03 ANALYZE TABLE DROP STATISTICS](../_Zusammenfassung/05%20SQL%20Language/02%20Aussagen%20und%20Metriken/01%20Tabellen%20Analysieren/03%20ANALYZE%20TABLE%20DROP%20STATISTICS.md)

**`09 Performance Optimization/01 Foundation Design/`** (7 Dateien)

- [01 Spark-Ausfuehrungsarchitektur](../_Zusammenfassung/09%20Performance%20Optimization/01%20Foundation%20Design/01%20Spark-Ausfuehrungsarchitektur.md)
- [02 Grundlagen der Query-Performance](../_Zusammenfassung/09%20Performance%20Optimization/01%20Foundation%20Design/02%20Grundlagen%20der%20Query-Performance.md)
- [03 Partitioning](../_Zusammenfassung/09%20Performance%20Optimization/01%20Foundation%20Design/03%20Partitioning.md)
- [04 Data Skipping und Tabellenstatistiken](../_Zusammenfassung/09%20Performance%20Optimization/01%20Foundation%20Design/04%20Data%20Skipping%20und%20Tabellenstatistiken.md)
- [05 Liquid Clustering](../_Zusammenfassung/09%20Performance%20Optimization/01%20Foundation%20Design/05%20Liquid%20Clustering.md)
- [06 Z-Ordering](../_Zusammenfassung/09%20Performance%20Optimization/01%20Foundation%20Design/06%20Z-Ordering.md)
- [07 Disk Cache](../_Zusammenfassung/09%20Performance%20Optimization/01%20Foundation%20Design/07%20Disk%20Cache.md)

**`09 Performance Optimization/02 The Right Cluster/`** (2 Dateien)

- [01 Cluster-Typen und Serverless Compute](../_Zusammenfassung/09%20Performance%20Optimization/02%20The%20Right%20Cluster/01%20Cluster-Typen%20und%20Serverless%20Compute.md)
- [02 Instance-Auswahl und Cluster-Sizing](../_Zusammenfassung/09%20Performance%20Optimization/02%20The%20Right%20Cluster/02%20Instance-Auswahl%20und%20Cluster-Sizing.md)

**`09 Performance Optimization/03 Code Optimization/`** (4 Dateien)

- [01 Shuffles](../_Zusammenfassung/09%20Performance%20Optimization/03%20Code%20Optimization/01%20Shuffles.md)
- [02 Data Skew](../_Zusammenfassung/09%20Performance%20Optimization/03%20Code%20Optimization/02%20Data%20Skew.md)
- [03 Spill](../_Zusammenfassung/09%20Performance%20Optimization/03%20Code%20Optimization/03%20Spill.md)
- [04 Serialization](../_Zusammenfassung/09%20Performance%20Optimization/03%20Code%20Optimization/04%20Serialization.md)

---

## <a id="governance">7. Governance and Security</a>

**86 Dateien**

**`02 Unity Catalog/`** (24 Dateien)

- [00 Overview](../_Zusammenfassung/02%20Unity%20Catalog/00%20Overview.md)
- [01 Meta Store](../_Zusammenfassung/02%20Unity%20Catalog/01%20Meta%20Store.md)
- [02 Catalog](../_Zusammenfassung/02%20Unity%20Catalog/02%20Catalog.md)
- [03 Schema](../_Zusammenfassung/02%20Unity%20Catalog/03%20Schema.md)
- [04 Table](../_Zusammenfassung/02%20Unity%20Catalog/04%20Table.md)
- [05 View](../_Zusammenfassung/02%20Unity%20Catalog/05%20View.md)
- [06 Materialized View](../_Zusammenfassung/02%20Unity%20Catalog/06%20Materialized%20View.md)
- [07 Metric View](../_Zusammenfassung/02%20Unity%20Catalog/07%20Metric%20View.md)
- [08 Volume](../_Zusammenfassung/02%20Unity%20Catalog/08%20Volume.md)
- [09 Function](../_Zusammenfassung/02%20Unity%20Catalog/09%20Function.md)
- [10 Model](../_Zusammenfassung/02%20Unity%20Catalog/10%20Model.md)
- [11 Service](../_Zusammenfassung/02%20Unity%20Catalog/11%20Service.md)
- [12 Secret](../_Zusammenfassung/02%20Unity%20Catalog/12%20Secret.md)
- [13 Feature](../_Zusammenfassung/02%20Unity%20Catalog/13%20Feature.md)
- [14 Storage credential](../_Zusammenfassung/02%20Unity%20Catalog/14%20Storage%20credential.md)
- [15 External location](../_Zusammenfassung/02%20Unity%20Catalog/15%20External%20location.md)
- [16 External metadata](../_Zusammenfassung/02%20Unity%20Catalog/16%20External%20metadata.md)
- [17 Service credential](../_Zusammenfassung/02%20Unity%20Catalog/17%20Service%20credential.md)
- [18 Connection](../_Zusammenfassung/02%20Unity%20Catalog/18%20Connection.md)
- [19 Share](../_Zusammenfassung/02%20Unity%20Catalog/19%20Share.md)
- [20 Provider](../_Zusammenfassung/02%20Unity%20Catalog/20%20Provider.md)
- [21 Recipient](../_Zusammenfassung/02%20Unity%20Catalog/21%20Recipient.md)
- [22 Clean room](../_Zusammenfassung/02%20Unity%20Catalog/22%20Clean%20room.md)
- [23 Tags](../_Zusammenfassung/02%20Unity%20Catalog/23%20Tags.md)

**`03 Governance/01 Data Governance/01 Uebersicht/`** (3 Dateien)

- [01 Was ist Data Governance](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/01%20Uebersicht/01%20Was%20ist%20Data%20Governance.md)
- [02 Identify Protect Manage](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/01%20Uebersicht/02%20Identify%20Protect%20Manage.md)
- [03 Was ist Unity Catalog](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/01%20Uebersicht/03%20Was%20ist%20Unity%20Catalog.md)

**`03 Governance/01 Data Governance/02 Objektmodell/`** (3 Dateien)

- [01 Securable Objects](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/02%20Objektmodell/01%20Securable%20Objects.md)
- [02 Managed vs External](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/02%20Objektmodell/02%20Managed%20vs%20External.md)
- [03 Object Storage Lifecycle](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/02%20Objektmodell/03%20Object%20Storage%20Lifecycle.md)

**`03 Governance/01 Data Governance/03 Setup/`** (4 Dateien)

- [01 Voraussetzungen](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/03%20Setup/01%20Voraussetzungen.md)
- [02 Erste Schritte](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/03%20Setup/02%20Erste%20Schritte.md)
- [03 Unity Catalog einrichten](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/03%20Setup/03%20Unity%20Catalog%20einrichten.md)
- [04 Metastore verwalten](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/03%20Setup/04%20Metastore%20verwalten.md)

**`03 Governance/01 Data Governance/04 Access Control/`** (5 Dateien)

- [01 Access Control Uebersicht](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/04%20Access%20Control/01%20Access%20Control%20Uebersicht.md)
- [02 Sicherheitsmodell und Verschluesselung](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/04%20Access%20Control/02%20Sicherheitsmodell%20und%20Verschluesselung.md)
- [03 Berechtigungskonzepte](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/04%20Access%20Control/03%20Berechtigungskonzepte.md)
- [04 Privilegien-Referenz](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/04%20Access%20Control/04%20Privilegien-Referenz.md)
- [05 Workspace-Catalog-Bindung](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/04%20Access%20Control/05%20Workspace-Catalog-Bindung.md)

**`03 Governance/01 Data Governance/05 Privilegien verwalten/`** (10 Dateien)

- [00 Uebersicht](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/05%20Privilegien%20verwalten/00%20Uebersicht.md)
- [01 Prinzipal-Typen](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/05%20Privilegien%20verwalten/01%20Prinzipal-Typen.md)
- [02 Schluesselprivilegien im Detail](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/05%20Privilegien%20verwalten/02%20Schluesselprivilegien%20im%20Detail.md)
- [03 Standardrechte ohne expliziten Grant](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/05%20Privilegien%20verwalten/03%20Standardrechte%20ohne%20expliziten%20Grant.md)
- [04 GRANT, REVOKE und SHOW GRANTS](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/05%20Privilegien%20verwalten/04%20GRANT%2C%20REVOKE%20und%20SHOW%20GRANTS.md)
- [05 Eigentuemerschaft (OWNER TO)](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/05%20Privilegien%20verwalten/05%20Eigentuemerschaft%20%28OWNER%20TO%29.md)
- [06 Admin-Privilegien](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/05%20Privilegien%20verwalten/06%20Admin-Privilegien.md)
- [07 Access Request Destinations](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/05%20Privilegien%20verwalten/07%20Access%20Request%20Destinations.md)
- [08 Grant-Rezepte fuer haeufige Szenarien](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/05%20Privilegien%20verwalten/08%20Grant-Rezepte%20fuer%20haeufige%20Szenarien.md)
- [09 Haeufige Stolpersteine](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/05%20Privilegien%20verwalten/09%20Haeufige%20Stolpersteine.md)

**`03 Governance/01 Data Governance/06 Table ACLs/`** (4 Dateien)

- [00 Uebersicht](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/06%20Table%20ACLs/00%20Uebersicht.md)
- [01 Table ACL](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/06%20Table%20ACLs/01%20Table%20ACL.md)
- [02 Object Privileges](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/06%20Table%20ACLs/02%20Object%20Privileges.md)
- [03 ANY FILE](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/06%20Table%20ACLs/03%20ANY%20FILE.md)

**`03 Governance/01 Data Governance/07 Filters und Masks/`** (2 Dateien)

- [00 Uebersicht](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/07%20Filters%20und%20Masks/00%20Uebersicht.md)
- [01 Manuell anwenden](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/07%20Filters%20und%20Masks/01%20Manuell%20anwenden.md)

**`03 Governance/01 Data Governance/08 ABAC/`** (16 Dateien)

- [00 Uebersicht](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/00%20Uebersicht.md)
- [01 Grundkonzepte](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/01%20Grundkonzepte.md)
- [02 Voraussetzungen](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/02%20Voraussetzungen.md)
- [03 ABAC vs RLS-CM](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/03%20ABAC%20vs%20RLS-CM.md)
- [04 Policies](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/04%20Policies.md)
- [05 Grant Policies](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/05%20Grant%20Policies.md)
- [06 Policy Evaluation](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/06%20Policy%20Evaluation.md)
- [07 Secure by Default](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/07%20Secure%20by%20Default.md)
- [08 Tutorial (UI)](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/08%20Tutorial%20%28UI%29.md)
- [09 Tutorial (SQL)](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/09%20Tutorial%20%28SQL%29.md)
- [10 Mapping-Tabellen](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/10%20Mapping-Tabellen.md)
- [11 Haeufige Muster](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/11%20Haeufige%20Muster.md)
- [12 Multi-Domain](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/12%20Multi-Domain.md)
- [13 Open Sharing](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/13%20Open%20Sharing.md)
- [14 Performance](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/14%20Performance.md)
- [15 Best Practices](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/08%20ABAC/15%20Best%20Practices.md)

**`03 Governance/01 Data Governance/09 Service Policies/`** (5 Dateien)

- [00 Uebersicht](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/09%20Service%20Policies/00%20Uebersicht.md)
- [01 Sensible Daten erkennen](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/09%20Service%20Policies/01%20Sensible%20Daten%20erkennen.md)
- [02 Policy erstellen](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/09%20Service%20Policies/02%20Policy%20erstellen.md)
- [03 Policy-Funktionsreferenz](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/09%20Service%20Policies/03%20Policy-Funktionsreferenz.md)
- [04 Policy-Beispiele](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/09%20Service%20Policies/04%20Policy-Beispiele.md)

**`03 Governance/01 Data Governance/10 Governed Tags/`** (6 Dateien)

- [00 Uebersicht](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/10%20Governed%20Tags/00%20Uebersicht.md)
- [01 Governed Tags verwalten](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/10%20Governed%20Tags/01%20Governed%20Tags%20verwalten.md)
- [02 Berechtigungen verwalten](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/10%20Governed%20Tags/02%20Berechtigungen%20verwalten.md)
- [03 Automatische Tag-Zuweisung](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/10%20Governed%20Tags/03%20Automatische%20Tag-Zuweisung.md)
- [04 KI-generierte Dokumentation](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/10%20Governed%20Tags/04%20KI-generierte%20Dokumentation.md)
- [05 Discoverability und Tag-Suche](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/10%20Governed%20Tags/05%20Discoverability%20und%20Tag-Suche.md)

**`03 Governance/01 Data Governance/11 Auditing und System Tables/`** (3 Dateien)

- [01 System Tables Uebersicht](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/11%20Auditing%20und%20System%20Tables/01%20System%20Tables%20Uebersicht.md)
- [02 Audit Logs, Billing und Lineage](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/11%20Auditing%20und%20System%20Tables/02%20Audit%20Logs%2C%20Billing%20und%20Lineage.md)
- [03 Insights-Tab (Catalog Explorer)](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/11%20Auditing%20und%20System%20Tables/03%20Insights-Tab%20%28Catalog%20Explorer%29.md)

**`03 Governance/01 Data Governance/12 PII und Pseudonymisierung/`** (1 Datei)

- [01 Pseudonymisierung und Anonymisierung](../_Zusammenfassung/03%20Governance/01%20Data%20Governance/12%20PII%20und%20Pseudonymisierung/01%20Pseudonymisierung%20und%20Anonymisierung.md)

---

## <a id="sonstiges">8. Sonstiges (keinem Prüfungsthema direkt zugeordnet)</a>

**1 Datei**

**`(Root)/`** (1 Datei)

- [databricks_tutorials](../_Zusammenfassung/databricks_tutorials.md)

---
