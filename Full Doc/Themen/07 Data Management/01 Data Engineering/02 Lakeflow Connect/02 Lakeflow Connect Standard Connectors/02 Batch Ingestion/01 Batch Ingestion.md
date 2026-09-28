# CTAS
- Daten als **Batches von Zeilen in Databricks laden**, oft nach einem Zeitplan
- Klassische Batch Ingestion **verarbeitet bei jeder Ausführung alle Datensätze**
- Batch Ingestion eignet sich gut für große Mengen historischer Daten, bei denen Echtzeitverarbeitung nicht erforderlich ist.
- Sie ist in der Regel einfacher zu implementieren und zu verwalten und daher eine gängige Wahl für geplante Datenpipelines.
- Gängige Techniken:
  - Die SQL-Anweisung: `CREATE TABLE AS (CTAS)` unter Verwendung von [`read_files()`](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files):
    - Daten: | JSON | CSV | XML | TEXT | BINARYFILE | PARQUET | AVRO | ORC
    - Kann das Dateiformat automatisch erkennen und ein einheitliches Schema über alle Dateien hinweg ableiten.
    - Kann in **Streaming Tables** verwendet werden, um Dateien **inkrementell mithilfe von Auto Loader** in Delta Lake zu laden.
  - Die Python-Methode: `spark.read.load()`


```sql
-- Batch Ingestion mit CTAS
CREATE TABLE new_table AS
  SELECT *
  FROM read_files(
     <path_to_file(s)>,
     format => '<file_type>',
     <other_format_specific_options>
  );
```

`CREATE TABLE AS (CTAS)` creates a **Delta table by default** -- from files in cloud object storage. 

**Delta Lake – Key Features**

1. **ACID Transactions** — Atomicity, Consistency, Isolation, Durability for all operations, allowing multiple users to read and write data concurrently without conflicts.
2. **Data Manipulation Language (DML)** — Supports DML operations such as INSERT, UPDATE, DELETE, and MERGE, enabling flexible data management.
3. **Time Travel** — Allows users to query and revert to previous versions of data, facilitating auditing and recovery.
4. **Schema Evolution and Enforcement** — Enforces a defined schema for data integrity while allowing schema evolution, enabling structural changes without breaking existing workflows.
5. **Many More!** — Provides additional features including **unified batch** and **streaming processing**, **performance optimization**, and **scalability**.
