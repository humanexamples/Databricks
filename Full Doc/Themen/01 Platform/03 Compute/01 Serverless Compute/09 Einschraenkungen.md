# Serverless Compute — Einschränkungen

> Quelle: <https://docs.databricks.com/aws/en/compute/serverless/limitations>

## Sprachen und API-Support

- **R wird nicht unterstützt.**
- Nur **Spark-Connect-APIs**; **Spark-RDD-APIs werden nicht unterstützt.**
- *"Spark Connect … defers analysis and name resolution to execution time, which may change the behavior of your code."*
- **ANSI SQL** ist Default; Opt-out über `spark.sql.ansi.enabled = false`.
- Zeilengrößen aus `spark.createDataFrame` dürfen **128 MB** nicht überschreiten.

## Datenzugriff und Storage

- **Unity Catalog erforderlich** für die Verbindung zu externen Datenquellen.
- Cloud-Speicher über **Unity-Catalog-External-Locations** ansprechen.
- **DBFS-Zugriff eingeschränkt** — Volumes oder Workspace-Dateien verwenden.
- **Maven-Koordinaten** werden nicht unterstützt.
- **Global Temp Views** werden nicht unterstützt — Session-Temp-Views oder Tabellen verwenden.
- **DBFS-Mounts mit AWS Instance Profiles** werden nicht unterstützt.

## User-Defined Functions (UDFs)

- UDFs können **nicht auf das Internet** zugreifen; `CREATE FUNCTION (External)` wird nicht unterstützt.
- Benutzerdefinierter Custom-Code darf **1 GB** Memory nicht überschreiten.
- **Scala-UDFs** können nicht innerhalb von Higher-Order-Functions verwendet werden.

## UI und Logging

- **Spark UI nicht verfügbar** — Query Profile verwenden.
- **Spark-Logs nicht verfügbar** — nur client-seitige Application-Logs zugänglich.

## Networking und Workspace-Zugriff

- Cross-Workspace-Zugriff erfordert **dieselbe Region** und **keine IP-ACL / kein Front-End-PrivateLink**.
- **Databricks Container Services** wird nicht unterstützt.

## Streaming

- **Unterstützte Trigger:** `Trigger.AvailableNow()` (empfohlen), `Trigger.Once()` (deprecated, aber unterstützt).
- **Nicht unterstützt:** `Trigger.Continuous(interval)`, `Trigger.ProcessingTime(interval)`.
- Kontinuierliche Streaming-Workloads: Triggered Pipeline Mode oder `Trigger.AvailableNow()` in Continuous Jobs.

## Notebooks

- **Scala und R** werden nicht unterstützt.
- **JAR-Libraries** werden nicht unterstützt (JAR-Tasks in Jobs schon).
- **Notebook-scoped Libraries** werden **nicht** über Sitzungen hinweg gecacht.
- Das Teilen von **TEMP-Tabellen/-Views** zwischen Nutzern wird nicht unterstützt.
- **Autocomplete** und **Variable Explorer** für DataFrames werden nicht unterstützt.
- Neue Notebooks verwenden standardmäßig `.ipynb`; das Source-Format kann Probleme verursachen.
- **Notebook-Tags** werden nicht unterstützt — Serverless Usage Policies verwenden.

## Jobs

- Task-Logs sind **nicht pro Run isoliert**.
- **Task-Libraries** werden für Notebook-Tasks nicht unterstützt — Notebook-scoped Libraries verwenden.
- Standardmäßig **kein Query-Execution-Timeout** (konfigurierbar über `spark.databricks.execution.timeout`).
- *"Serverless compute has a maximum runtime of 7 days. Runs that exceed 7 days are terminated by the platform and are not retried."*

## Compute-spezifisch (nicht unterstützt)

- Compute-Policies
- Compute-scoped Init-Skripte
- Compute-scoped Libraries (inkl. Custom Data Sources)
- Instance Pools
- Compute Event Logs
- Die meisten Apache-Spark-Compute-Konfigurationen
- Compute-scoped Environment-Variablen (Job-Level-Environment-Variablen oder Widgets verwenden)

## Caching

- Metadata-Caching kann einen vollständigen Session-Kontext-Reset beim Katalogwechsel verhindern.
- **DataFrame- und SQL-Cache-APIs werden nicht unterstützt:**
  - `df.cache()`, `df.persist()`, `df.unpersist()`, `df.checkpoint()`
  - `spark.catalog.cacheTable()`, `spark.catalog.uncacheTable()`, `spark.catalog.clearCache()`
  - `CACHE TABLE`, `UNCACHE TABLE`, `REFRESH TABLE`, `CLEAR CACHE`

## Hive

- **Hive-SerDe-Tabellen** und der zugehörige `LOAD DATA`-Befehl werden nicht unterstützt.
- Unterstützte Datenquellen begrenzt auf: `AVRO`, `BINARYFILE`, `CSV`, `DELTA`, `JSON`, `KAFKA`, `ORC`, `PARQUET`, `TEXT`, `XML`.
- **Hive-Variablen** und Config-Variablen-Referenzen mit `${var}`-Syntax werden nicht unterstützt — stattdessen `DECLARE VARIABLE`, `SET VARIABLE`, SQL-Session-Variablen, Parameter-Marker oder die `IDENTIFIER`-Klausel.

## Unterstützte Datenquellen

- **DML (write/update/delete):** `CSV`, `JSON`, `AVRO`, `DELTA`, `KAFKA`, `PARQUET`, `ORC`, `TEXT`, `UNITY_CATALOG`, `BINARYFILE`, `XML`, `SIMPLESCAN`, `ICEBERG`
- **Read:** alle DML-Quellen plus `MYSQL`, `POSTGRESQL`, `SQLSERVER`, `REDSHIFT`, `SNOWFLAKE`, `SQLDW`, `DATABRICKS`, `BIGQUERY`, `ORACLE`, `SALESFORCE`, `SALESFORCE_DATA_CLOUD`, `TERADATA`, `WORKDAY_RAAS`, `MONGODB`
