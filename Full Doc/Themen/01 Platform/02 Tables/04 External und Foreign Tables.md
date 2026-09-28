# External, Foreign und Temporary Tables

Neben Managed Tables (siehe [Managed Tables.md](Managed%20Tables.md)) bietet Databricks drei weitere Tabellentypen für Szenarien, in denen Daten nicht vollständig von Unity Catalog verwaltet werden sollen oder können: External Tables für selbst verwalteten Cloud-Storage, Foreign Tables für externe Systeme über Lakehouse Federation, und Temporary Tables für sitzungsgebundene Zwischenergebnisse. Basierend auf offiziellen Databricks-Doku-Seiten (jeweils am Ende jedes Abschnitts referenziert).

## Abschnittsübersicht

1. [External Tables](#external)
2. [External Partition Discovery](#partition-discovery)
3. [Foreign Tables](#foreign)
4. [Foreign zu External konvertieren](#foreign-zu-external)
5. [Temporary Tables](#temporary)
6. [Zusammenfassung](#zusammenfassung)

---

## <a id="external">1. External Tables</a>

### 1.1 Was External Tables sind

External Tables speichern Datendateien im Cloud-Object-Storage, während Unity Catalog die Metadaten verwaltet und Governance durchsetzt. „Unity Catalog verwaltet weiterhin die Metadaten der Tabelle und stellt vollständige Datengovernance über alle Queries hinweg sicher." Das System verwaltet jedoch **nicht** Datenlebenszyklus, Optimierung, Speicherort oder Layout.

Wird eine External Table gelöscht, werden die Metadaten entfernt, die zugrunde liegenden Datendateien im Cloud-Storage bleiben jedoch bestehen.

### 1.2 Unterstützte Dateiformate

DELTA, CSV, JSON, AVRO, PARQUET, ORC, TEXT.

### 1.3 Wann External Tables sinnvoll sind

Databricks empfiehlt External Tables für zwei primäre Szenarien:

1. **Registrierung inkompatibler Daten:** „Eine Tabelle muss registriert werden, die auf bestehenden Daten basiert, die nicht mit Unity-Catalog-Managed-Tables kompatibel sind — etwa JSON oder Avro."
2. **Direkter externer Zugriff:** wenn Nicht-Databricks-Clients direkten Datenzugriff ohne Unity-Catalog-Berechtigungsdurchsetzung benötigen.

Für die meisten Anwendungsfälle empfiehlt Databricks stattdessen Managed Tables, die automatische Optimierung und bessere Performance bieten.

### 1.4 Berechtigungsanforderungen

Zum Erstellen von External Tables wird benötigt:

- `CREATE EXTERNAL TABLE`-Berechtigung auf dem External Location.
- `USE CATALOG`-Berechtigung auf dem übergeordneten Catalog.
- `USE SCHEMA`-Berechtigung auf dem übergeordneten Schema.
- `CREATE TABLE`-Berechtigung auf dem übergeordneten Schema.

### 1.5 Code-Beispiele

**SQL — mit definiertem Schema:**

```sql
CREATE TABLE <catalog>.<schema>.<table-name>(
  <column-name> <data-type>
)
LOCATION 's3://<bucket-path>/<table-directory>';
```

**SQL — aus Query-Ergebnissen:**

```sql
CREATE TABLE <catalog>.<schema>.<table-name>
LOCATION 's3://<bucket-path>/<table-directory>'
AS SELECT * FROM <source-table>;
```

**Python — mit definiertem Schema:**

```python
from pyspark.sql.types import StructType, StructField, StringType

schema = StructType([StructField("<column-name>", <data-type>())])
spark.createDataFrame([], schema).write \
  .option("path", "s3://<bucket-path>/<table-directory>") \
  .saveAsTable("<catalog>.<schema>.<table-name>")
```

**Python — aus DataFrame:**

```python
df.write \
  .option("path", "s3://<bucket-path>/<table-directory>") \
  .saveAsTable("<catalog>.<schema>.<table-name>")
```

**External Table löschen:**

```sql
DROP TABLE IF EXISTS catalog_name.schema_name.table_name;
```

```python
spark.sql("DROP TABLE IF EXISTS catalog_name.schema_name.table_name")

# Ab Databricks Runtime 18.2+
spark.catalog.dropTable("catalog_name.schema_name.table_name", ifExists=True)
```

### Quelle

- https://docs.databricks.com/aws/en/tables/external

---

## <a id="partition-discovery">2. External Partition Discovery</a>

External Partition Discovery erkennt automatisch Partitionen in Unity-Catalog-External-Tables. Standardmäßig „werden alle Verzeichnisse am Tabellen-Speicherort rekursiv aufgelistet, um Partitionen automatisch zu erkennen." Bei großen Tabellen kann dieser Ansatz jedoch zu Latenzproblemen führen.

### 2.1 Partition Metadata Logging als Alternative

Ab Databricks Runtime 13.3 LTS steht **Partition Metadata Logging** zur Verfügung — verbessert die Performance, indem explizite Partitions-Metadaten gepflegt werden, statt bei jedem Zugriff Verzeichnisse zu scannen.

**Wichtige Voraussetzung:** Tabellen mit aktiviertem Partition Metadata Logging können **nur** mit Databricks Runtime 13.3 LTS oder höher gelesen oder geschrieben werden.

### 2.2 Aktivierung

**Bei Tabellenerstellung:**

```sql
CREATE OR REPLACE TABLE <catalog>.<schema>.<table-name>
USING <format>
PARTITIONED BY (<partition-column-list>)
TBLPROPERTIES ('partitionMetadataEnabled' = 'true')
LOCATION 's3://<bucket-path>/<table-directory>';
```

**Spark-Konfiguration:**

```sql
SET spark.databricks.nonDelta.partitionLog.enabled = true;
```

### 2.3 Partitionen verwalten

**Registrierte Partitionen auflisten:**

```sql
SHOW PARTITIONS <table-name>;
```

**Partitions-Metadaten reparieren (Hive-Style-Partitionierung):**

```sql
MSCK REPAIR TABLE <table_name> SYNC PARTITIONS;
MSCK REPAIR TABLE <table_name> ADD PARTITIONS;
MSCK REPAIR TABLE <table_name> DROP PARTITIONS;
```

**Partitionen manuell hinzufügen:**

```sql
ALTER TABLE <table-name>
ADD PARTITION (<partition-column-name> = <partition-column-value>)
LOCATION 's3://<bucket-path>/<table-directory>/<partition-directory>';
```

### 2.4 Wichtige Einschränkungen

- Automatische Partitionserkennung wird deaktiviert, sobald Metadata Logging aktiviert ist.
- Pfadbasierte Lese-/Schreibvorgänge umgehen die Partitions-Metadaten-Registrierung.
- Fügen externe Systeme Daten am Tabellen-Speicherort hinzu, ist eine manuelle Metadaten-Reparatur nötig.

### Quelle

- https://docs.databricks.com/aws/en/tables/external-partition-discovery

---

## <a id="foreign">3. Foreign Tables</a>

### 3.1 Definition

Foreign Tables, auch Federated Tables genannt, sind „Tabellen, die über Unity Catalog als Teil eines Foreign Catalog registriert werden" — die Daten werden extern verwaltet, während Databricks Governance-Fähigkeiten hinzufügt.

### 3.2 Registrierungsmethoden

Databricks unterstützt zwei Ansätze:

1. **Query Federation:** nutzt „sichere JDBC-Verbindungen, um zu externen Datensystemen wie PostgreSQL und MySQL zu föderieren."
2. **Catalog Federation:** verbindet externe Catalogs wie Hive Metastore, AWS Glue oder Snowflake Horizon Catalog für direkten Dateispeicherzugriff.

### 3.3 Anwendungsfälle

Foreign Tables dienen als temporäre Lösung für den Zugriff auf externe Daten ohne Migration. Für häufig genutzte oder produktive Datensätze empfiehlt die Dokumentation den Übergang zu Unity-Catalog-Managed-Tables für bessere Performance.

### 3.4 Schreibfähigkeiten

Verfügt der Workspace über einen internen föderierten Hive Metastore mit entsprechenden Berechtigungen, lassen sich Foreign Tables erstellen oder beschreiben. Extern föderierte Metastores und Lakehouse-Federation-Tabellen bleiben jedoch **nur lesend**. Databricks verwaltet weder Metadaten noch Semantik für Schreibvorgänge, und die Transaktionsgarantien entsprechen nicht denen von Managed Tables.

### Quelle

- https://docs.databricks.com/aws/en/tables/foreign

---

## <a id="foreign-zu-external">4. Foreign zu External konvertieren</a>

Der Befehl `ALTER TABLE ... SET EXTERNAL` ermöglicht die Konvertierung von Foreign Tables in Unity-Catalog-External-Tables — unter Erhalt von Historie, Konfigurationen, Namen, Einstellungen, Berechtigungen und Views.

### Unterstützte Datenformate

Delta Lake, Parquet, ORC, Avro, JSON, CSV und TEXT — ab Databricks Runtime 17.3+.

### Voraussetzungen

- Die Foreign Table muss eine externe HMS-Tabelle sein (nicht managed).
- `OWNER`- oder `MANAGE`-Berechtigung auf der Tabelle wird benötigt.
- `CREATE`-Berechtigung auf dem `EXTERNAL LOCATION` wird benötigt.
- Runtime-Version 17.3 oder höher.

### Syntax

```sql
ALTER TABLE source_table SET EXTERNAL [DRY RUN]
```

Der optionale `DRY RUN`-Parameter validiert, ob die Konvertierung möglich ist, ohne sie auszuführen — bei Eignung wird `DRY_RUN_SUCCESS` zurückgegeben.

### Rückgängigmachen

```sql
DROP TABLE catalog.schema.my_external_table;
```

Die Tabelle wird beim nächsten Catalog-Sync wieder als Foreign Table föderiert.

### Verifikation

Über Catalog Explorer prüfbar: Vor der Konvertierung zeigt die Tabelle „Foreign" an, danach „External".

### Quelle

- https://docs.databricks.com/aws/en/tables/convert-foreign-external

---

## <a id="temporary">5. Temporary Tables</a>

### 5.1 Was Temporary Tables sind

Temporary Tables sind sitzungsgebundene Datenstrukturen, die nur während einer Databricks-Session bestehen. Sie „speichern Daten für die Dauer einer Databricks-Session" und erlauben es, „Zwischenergebnisse für explorative Analyse oder SQL-Datenpipelines zu materialisieren, ohne permanente Tabellen zu erstellen."

### 5.2 Wann sie sinnvoll sind

Empfohlen für:

- Speicherung kurzlebiger Zwischendaten während Analyse oder Entwicklung.
- Wiederverwendung von Query-Ergebnissen über mehrere Operationen innerhalb derselben Session.
- Nutzung einer tabellenartigen Schnittstelle, ohne den eigenen Catalog-Namensraum zu füllen.

Für Daten, die über die aktuelle Session hinaus bestehen oder zwischen Nutzern/Jobs geteilt werden müssen, sind permanente Unity-Catalog-Tabellen geeigneter.

### 5.3 Temporary Tables erstellen

**Leere Tabelle mit definiertem Schema:**

```sql
CREATE TEMPORARY TABLE temp_customers (
  id INT,
  name STRING
);
```

**Aus Query-Ergebnissen:**

```sql
CREATE OR REPLACE TEMP TABLE temp_recent_orders AS
SELECT order_id, customer_id, order_date, amount
FROM prod.sales.orders
WHERE order_date >= current_date() - INTERVAL 30 DAYS;
```

**Über VALUES-Klausel:**

```sql
CREATE TEMP TABLE temp_test_data AS
VALUES
  (9001, 101, 50.00),
  (9002, 204, 75.00),
  (9003, 101, 25.00)
AS t(order_id, customer_id, amount);
```

**Wichtige Einschränkung:** keine `USING`-Klausel angeben — Temporary Tables nutzen standardmäßig das Delta-Lake-Format.

### 5.4 Temporary Tables abfragen

Referenzierung nur über den Namen — keine Catalog- oder Schema-Angabe nötig:

```sql
SELECT * FROM temp_customers;
```

Bei unqualifizierten Namen sucht Databricks in dieser Reihenfolge:

1. Temporary Tables in der aktuellen Session.
2. Permanente Tabellen im aktuellen Schema.

Um eine durch eine gleichnamige Temporary Table überschattete permanente Tabelle explizit zu referenzieren, den vollständig qualifizierten Namen nutzen:

```sql
SELECT * FROM prod.sales.customers;
```

### 5.5 Temporary Tables modifizieren

Unterstützte DML-Operationen:

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

**Wichtige Einschränkung:** `DELETE FROM`-Operationen werden für Temporary Tables **nicht** unterstützt.

### 5.6 Temporary Tables löschen

```sql
DROP TEMP TABLE temp_customers;
DROP TEMP TABLE IF EXISTS temp_recent_orders;
```

Databricks löscht Temporary Tables automatisch, sobald die Session endet.

### 5.7 Lebenszyklus und Zeitlimits

Temporary Tables existieren ausschließlich innerhalb ihrer Erstellungs-Session, mit einer maximalen Lebensdauer von **sieben Tagen** ab Session-Erstellung. Sie werden unzugänglich, sobald die Session endet oder sieben Tage vergehen — je nachdem, was zuerst eintritt. Dies gilt über Notebooks, SQL Editor, Jobs und JDBC/ODBC-Sessions hinweg.

### 5.8 Storage-Verwaltung

Databricks verwaltet den Storage von Temporary Tables automatisch:

- **Serverless-Workspaces:** Daten im Default-Storage gespeichert, nutzt Customer-Managed-Keys, falls für Managed Services konfiguriert.
- **Classic Workspaces:** Daten im bei der Workspace-Erstellung konfigurierten Workspace-Storage-Bucket gespeichert.

Wird eine Tabelle unzugänglich, wird der Storage innerhalb weniger Tage automatisch zurückgewonnen.

### 5.9 Isolation und Berechtigungen

Keine `CREATE TABLE`-Berechtigung nötig — jeder Nutzer kann Temporary Tables erstellen. Session-Level-Isolation stellt sicher, dass nur der erstellende Nutzer auf seine Temporary Tables zugreifen kann. Mehrere Nutzer können sich den Zugriff auf Temporary Tables innerhalb derselben Session nicht teilen.

Temporary Tables und Temporary Views teilen sich einen Namensraum — beide lassen sich nicht mit identischem Namen in derselben Session erstellen.

### 5.10 Wichtige Einschränkungen

| Einschränkung | Details |
|---|---|
| Schema-Änderungen | `ALTER TABLE` nicht unterstützt — Tabellen stattdessen ersetzen |
| Cloning | Shallow und Deep Cloning nicht unterstützt |
| Time Travel | nicht verfügbar |
| Streaming | nicht in Streaming-Queries nutzbar (z. B. `foreachBatch`) |
| API-Unterstützung | nur SQL-APIs, keine DataFrame-APIs |
| Multi-User-Notebooks | nur ein Nutzer kann pro Session mit Temporary Tables interagieren |
| Dedicated Clusters | auf Single-User-Clustern nicht unterstützt |
| AWS GovCloud | nicht verfügbar in AWS GovCloud oder AWS GovCloud DoD |

Tabelleneigenschaften-Unterstützung umfasst nur `SET TBLPROPERTIES`- und `UNSET TBLPROPERTIES`-Klauseln (Serverless Compute, Databricks Runtime 18.2+ und Databricks SQL 2026.15+).

### Quelle

- https://docs.databricks.com/aws/en/tables/temporary-tables

---

## <a id="zusammenfassung">6. Zusammenfassung</a>

- **External Tables** speichern Daten im eigenen Cloud-Storage, während Unity Catalog nur Metadaten und Governance verwaltet — sinnvoll für inkompatible Formate (JSON, Avro) oder direkten externen Zugriff.
- **External Partition Discovery** erkennt Partitionen standardmäßig über rekursives Directory-Listing; **Partition Metadata Logging** (ab Runtime 13.3 LTS) ersetzt das durch explizite Metadaten für bessere Performance bei großen Tabellen.
- **Foreign Tables** bieten nur lesenden Zugriff auf extern verwaltete Systeme über Query Federation (JDBC) oder Catalog Federation (Hive Metastore, Glue, Snowflake) — als temporäre Brücke vor einer Migration zu Managed Tables gedacht.
- Foreign Tables lassen sich über `ALTER TABLE ... SET EXTERNAL` in External Tables konvertieren, mit vollständigem Erhalt von Historie und Berechtigungen.
- **Temporary Tables** sind sitzungsgebundene, automatisch verwaltete Delta-Tabellen mit maximal 7 Tagen Lebensdauer — ideal für Zwischenergebnisse, aber mit deutlichen Einschränkungen (kein `DELETE`, kein Time Travel, kein Cloning, nur SQL-APIs).

---

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### CREATE TABLE ... LOCATION (External Table)

```sql
CREATE TABLE sec_filings LOCATION 's3://depts/finance/sec_filings';

CREATE OR REPLACE TABLE sec_filings
  LOCATION 's3://depts/finance/sec_filings'
  AS (SELECT * FROM current_filings);
```

Die erste Variante registriert vorhandene Dateien am angegebenen Pfad als Tabelle, ohne explizites Schema anzugeben (Schema-Inferenz). Die zweite erstellt bzw. ersetzt die Tabelle aus einem Query-Ergebnis.

### Zugriff und Dateiverwaltung

```sql
GRANT SELECT ON TABLE sec_filings TO employee;

SELECT count(1) FROM sec_filings;

LIST 's3://depts/finance/sec_filings';
LIST 's3://depts/finance/sec_filings/_delta_log';
```

Governance (`GRANT`) erfolgt weiterhin über Unity Catalog auf Tabellenebene; `LIST` erlaubt den direkten Blick auf die zugrunde liegenden Dateien im Cloud-Storage-Pfad, ohne die Tabelle über SQL abzufragen.

### Quelle

- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-external-tables
