

# Apache Iceberg

Apache Iceberg ist neben Delta Lake das zweite von Databricks unterstützte offene Tabellenformat — mit vollständiger Integration für Managed Tables und Lesezugriff für Foreign Tables aus externen Catalogs. Dieses Dokument behandelt die Grundlagen, die neuen Iceberg-v3-Features, das Klonen von Iceberg-Tabellen und den Uniform-Mechanismus, der Delta-Tabellen für Iceberg-Clients lesbar macht. Basierend auf offiziellen Databricks-Doku-Seiten (jeweils am Ende jedes Abschnitts referenziert).

## Abschnittsübersicht

1. [Was ist Apache Iceberg?](#was-ist)
2. [Iceberg Catalog](#catalog)
3. [Voraussetzungen](#voraussetzungen)
4. [Managed vs. Foreign Iceberg Tables](#managed-vs-foreign)
5. [Weitere Kernfähigkeiten](#kernfaehigkeiten)
6. [Bekannte Einschränkungen](#einschraenkungen)
7. [Iceberg v3: neue Features](#iceberg-v3)
8. [Iceberg-Tabellen klonen](#klonen)
9. [Delta-Tabellen als Iceberg lesen (Universal Format)](#uniform)
10. [Zusammenfassung](#zusammenfassung)

---

## <a id="was-ist">1. Was ist Apache Iceberg?</a>

„Apache Iceberg ist ein Open-Source-Tabellenformat für Analytics-Workloads, das Features wie Schema Evolution, Time Travel und Hidden Partitioning unterstützt." Wie Delta Lake erzeugt es eine Abstraktionsschicht, die ACID-Transaktionen auf Object-Storage-Daten ermöglicht. Databricks unterstützt Iceberg-Tabellen im Apache-Parquet-Format sowie die Iceberg-Spezifikationsversionen 1, 2 und 3.

### Quelle

- https://docs.databricks.com/aws/en/iceberg/

---

## <a id="catalog">2. Iceberg Catalog</a>

Der **Iceberg Catalog** ist die oberste Architekturschicht — sie ruft aktuelle Metadaten beim Laden von Tabellen ab und handhabt Operationen wie das Erstellen, Löschen und Umbenennen von Tabellen.

Databricks unterstützt Iceberg-Tabellen, die verwaltet werden von:

- **Unity Catalog**
- **Foreign Catalogs** (AWS Glue, Hive Metastore, Snowflake Horizon Catalog)

### Quelle

- https://docs.databricks.com/aws/en/iceberg/

---

## <a id="voraussetzungen">3. Voraussetzungen</a>

**Allgemein:**

- Workspace mit aktiviertem Unity Catalog.
- Databricks Runtime 16.4 LTS oder höher.

**Für Managed Tables zusätzlich:**

- Serverless Compute muss aktiviert sein, mit Serverless-Netzwerkverbindung zum Cloud-Storage.
- Predictive Optimization aktiviert (für Tabellenwartung).
- Iceberg-Client-Version 1.9.2 oder höher.

### Quelle

- https://docs.databricks.com/aws/en/iceberg/

---

## <a id="managed-vs-foreign">4. Managed vs. Foreign Iceberg Tables</a>

### Managed Tables (Unity Catalog)

- Vollständig integriert mit Databricks-Features: Liquid Clustering, Predictive Optimization, Materialized Views und Streaming Tables.
- Lebenszyklusmanagement über Unity Catalog.
- Unterstützt Partition Evolution über externe Iceberg-Engines.
- Lese- und schreibfähig.

**Erstellen (SQL) — `USING iceberg` ist Pflicht, sonst entsteht eine Delta-Tabelle:**

```sql
CREATE TABLE <catalog-name>.<schema-name>.<table-name>(
  <column-specification>
)
USING iceberg;
```

**Gotcha:** ohne explizites `USING iceberg` erstellt Databricks standardmäßig eine Delta-Lake-Tabelle — die `USING`-Klausel entscheidet über das Format, nicht ein separater Iceberg-Schalter.

**Erstellen (Python):**

```python
from pyspark.sql.types import StructType, StructField, StringType

schema = StructType([StructField("<column-name>", StringType())])
spark.createDataFrame([], schema).write \
  .format("iceberg") \
  .saveAsTable("<catalog-name>.<schema-name>.<table-name>")
```

Kein `LOCATION` nötig — wie bei jeder Managed Table legt Unity Catalog den physischen Speicherort automatisch fest (siehe Abschnitt 7 unten und [`04 External und Foreign Tables.md`](04%20External%20und%20Foreign%20Tables.md) für den Vergleich mit External Tables).

### Foreign Tables (externe Catalogs)

- In Databricks **nur lesend**.
- Eingeschränkte Plattform-Unterstützung.
- Time Travel beschränkt auf bereits gelesene Snapshots.
- Keine Unterstützung für Partition Evolution.

**Entstehung — kein `CREATE TABLE` pro Tabelle:** Foreign Iceberg Tables werden nicht einzeln erstellt, sondern erscheinen automatisch, sobald ein externer Catalog (AWS Glue, Hive Metastore, Snowflake Horizon Catalog) als **Foreign Catalog** in Unity Catalog registriert ist. Das allgemeine `CREATE FOREIGN CATALOG`-Muster (verifiziert am Beispiel PostgreSQL in [`02 Catalog.md`](../../02%20Unity%20Catalog/02%20Catalog.md)):

```sql
CREATE FOREIGN CATALOG <catalog_name>
  USING CONNECTION <connection_name>
  OPTIONS (<system-spezifische Optionen>);
```

**Ungeklärt/bewusst nicht erraten:** Der konkrete `CONNECTION`-Typ und die passenden `OPTIONS`-Schlüssel für Glue/Hive-Metastore/Snowflake als Iceberg-Quelle konnten mit den hier verfügbaren Quellen nicht verifiziert werden (dafür ist laut Doku eine separate Lakehouse-Federation/Foreign-Catalogs-Seite maßgeblich, nicht die Iceberg-Übersichtsseite) — deshalb nur das generische, bereits verifizierte Grundmuster statt erfundener Glue-spezifischer Werte. Sobald die Foreign-Catalog-Verbindung mit den korrekten Werten steht, listet Unity Catalog dessen Iceberg-Tabellen automatisch als Foreign Tables — analog zum generellen Foreign-Table-Mechanismus in [`04 External und Foreign Tables.md`](04%20External%20und%20Foreign%20Tables.md), Abschnitt 3.

### Quelle

- https://docs.databricks.com/aws/en/iceberg/
- https://docs.databricks.com/aws/en/tables/managed (SQL-/Python-Beispiele zum Erstellen einer Managed-Iceberg-Tabelle, Gotcha zu `USING iceberg`)

---

## <a id="kernfaehigkeiten">5. Weitere Kernfähigkeiten</a>

- **Deep Cloning** von Managed Tables (siehe Abschnitt 7).
- **Partition Evolution** (Hinzufügen, Entfernen, Ersetzen von Feldern).
- **Materialized Views**, kompatibel mit externen Iceberg-Readern (Public Preview).
- **REST-Catalog-API** für externen Systemzugriff mit Credential Vending.

### Quelle

- https://docs.databricks.com/aws/en/iceberg/

---

## <a id="einschraenkungen">6. Bekannte Einschränkungen</a>

### Dateiformat und Datentypen

- Nur Apache Parquet als Dateiformat unterstützt.
- Nicht unterstützte Datentypen: `UUID`, `Fixed(L)`, `TIME` sowie verschachtelte `STRUCT`s mit Pflichtfeldern (`required`).

### Löschungen und Partitionierung

- Iceberg-v2-Löschungen über Position- und Equality-Deletes werden nicht unterstützt — stattdessen kommen bei v3 Deletion Vectors zum Einsatz (siehe Abschnitt 7).
- Partition Evolution steht für Foreign Tables nicht zur Verfügung.
- Partitionierung nach `Binary`-Typ wird nicht unterstützt.
- Ausdrucksbasierte Partition-Transforms (`years()`, `bucket()`, …) werden für Managed Tables nicht unterstützt.

### Zugriff und Integration

- Foreign Tables sind ausschließlich lesend.
- Branching und Tagging werden nicht unterstützt.
- Views sind von externen Engines aus nicht zugreifbar.
- AI Search steht nicht zur Verfügung.
- Credential Vending wird auf Workspaces mit Default-Storage nicht unterstützt.

### Besonderheiten Managed Tables

- Änderungen am Compression-Codec sind eingeschränkt (Standard: Zstd).
- Bestimmte Tabelleneigenschaften werden von Unity Catalog kontrolliert.
- Generated Columns und Constraints stehen nicht zur Verfügung.

### Besonderheiten Foreign Tables

- Time Travel ist auf bereits gelesene Snapshots beschränkt.
- Bucket-Transforms können die Performance verschlechtern.
- Keine Integration mit Cloud-Storage-Tiering.

### Quelle

- https://docs.databricks.com/aws/en/iceberg/

---

## <a id="iceberg-v3">7. Iceberg v3: neue Features</a>

„Apache Iceberg v3 verbessert die Query-Performance und führt neue Fähigkeiten für Managed Tables ein, die entweder natives Iceberg oder Delta Lake mit Iceberg-Reads in Unity Catalog nutzen."

### Drei Kernfeatures

1. **Deletion Vectors** — ermöglichen effizientes zeilenweises Löschen, ohne ganze Datendateien neu schreiben zu müssen (siehe auch [Liquid Clustering.md](../../Performance%20Optimization/Foundation%20Design/Liquid%20Clustering.md), Abschnitt 9.2, zu Deletion Vectors im Kontext von Row-Level Concurrency). Mit Iceberg v3 (Private Preview, Stand 21.01.2026) müssen Deletion Vectors dafür **nicht** deaktiviert werden — anders als bei Iceberg v2, wo dies für Iceberg Reads (UniForm) Voraussetzung ist (siehe [Table Features/14 Iceberg Reads (UniForm).md](Table%20Features/14%20Iceberg%20Reads%20%28UniForm%29.md), Abschnitt 2, und [Table Features/06 Deletion Vectors.md](Table%20Features/06%20Deletion%20Vectors.md), Abschnitt 7).
2. **VARIANT-Datentyp** — unterstützt Speicherung und Verarbeitung semi-strukturierter Daten.
3. **Row Lineage** — verfolgt inkrementelle Änderungen an Tabellendaten nach.

### Voraussetzungen

- Workspace mit aktiviertem Unity Catalog.
- Databricks Runtime 18 LTS oder neuer.

### Tabellen mit Iceberg v3 erstellen

Beide folgenden Beispiele geben bewusst **keine** `LOCATION`-Klausel an (so auch im Original der Doku) — es sind **Managed Tables**: Unity Catalog legt den physischen Speicherort automatisch innerhalb des Managed-Storage-Bereichs des Schemas/Catalogs fest. Für einen selbst gewählten Speicherort (External Table) siehe [`04 External und Foreign Tables.md`](04%20External%20und%20Foreign%20Tables.md), Abschnitt 1.

**Delta Lake mit Iceberg-Reads:**

```sql
CREATE OR REPLACE TABLE main.schema.table (c1 INT)
TBLPROPERTIES('delta.universalFormat.enabledFormats' = 'iceberg',
'delta.enableIcebergCompatV3' = 'true');
```

**Natives Iceberg-Table:**

```sql
CREATE OR REPLACE TABLE main.schema.table (c1 INT)
USING iceberg
TBLPROPERTIES ('format-version' = 3);
```

### Bestehende Tabellen upgraden

Upgrade über `ALTER TABLE`-Befehle oder durch Aktivieren eines beliebigen v3-Features. Ein Downgrade auf v2 ist über den `RESTORE`-Befehl möglich, sofern Protocol-Downgrade-Berechtigungen aktiviert sind.

### Bekannte Einschränkungen

Nicht unterstützt: Write-/Initial-Defaults, unbekannte Datentypen, Nanosekunden-präzise Timestamps, Multi-Argument-Transforms.

### Quelle

- https://docs.databricks.com/aws/en/iceberg/iceberg-v3

---

## <a id="klonen">8. Iceberg-Tabellen klonen</a>

### Nur Deep Clone

„Managed-Iceberg-Tabellen unterstützen nur Deep Cloning. Shallow Cloning und Formatkonvertierung während des Klonens werden nicht unterstützt." — Shallow Cloning steht bei Managed Iceberg Tables also anders als bei Delta-Lake-Tabellen nicht zur Verfügung.

### Syntax

**Grundlegender Deep Clone:**

```sql
CREATE TABLE <catalog>.<schema>.<target-table>
DEEP CLONE <catalog>.<schema>.<source-table>;
```

**Bestehende Tabelle ersetzen:**

```sql
CREATE OR REPLACE TABLE <catalog>.<schema>.<target-table>
DEEP CLONE <catalog>.<schema>.<source-table>;
```

**Bedingte Erstellung:**

```sql
CREATE TABLE IF NOT EXISTS <catalog>.<schema>.<target-table>
DEEP CLONE <catalog>.<schema>.<source-table>;
```

### Anwendungsfälle

**Produktions-Archivierung:**

```sql
CREATE TABLE prod_catalog.archive.orders_snapshot_may2026
DEEP CLONE prod_catalog.main.orders;
```

**Entwicklungs-Tests:**

```sql
CREATE OR REPLACE TABLE dev_catalog.test.orders
DEEP CLONE prod_catalog.main.orders;
```

**Foreign-Iceberg-Tabelle klonen** (Übernahme in Unity Catalog):

```sql
CREATE TABLE <uc-catalog>.<schema>.<target-table>
DEEP CLONE <foreign-catalog>.<schema>.<source-table>;
```

### Voraussetzungen

- Databricks Runtime 16.4 LTS oder später.
- `SELECT`-Berechtigung auf der Quelltabelle.
- `CREATE TABLE`- oder `MODIFY`-Berechtigung auf dem Ziel.
- Predictive Optimization auf Ziel-Catalog/-Schema aktiviert.

### Klon-Verhalten

- Vollständige Unabhängigkeit zwischen Quelle und Klon.
- Getrennte Snapshot-Historien für Time-Travel-Queries.
- Schema- und Partitionierungsinformationen bleiben erhalten.
- Unity-Catalog-Tags werden **nicht** kopiert.
- Unabhängiges Lebenszyklusmanagement nach der Erstellung.

### Wichtige Einschränkungen

- Zero-Copy-Konvertierung nicht unterstützt — alle Daten werden in Unity Catalog kopiert.
- Tabellenhistorie wird nicht übertragen, was Time Travel beeinträchtigt.
- Eigenschaften können nicht während des Klonens gesetzt werden (`ALTER TABLE` danach nutzen).
- Formatkonvertierung während des Klonens ist untersagt.

### Quelle

- https://docs.databricks.com/aws/en/iceberg/clone

---

## <a id="uniform">9. Delta-Tabellen als Iceberg lesen (Universal Format)</a>

Ab Databricks Runtime 14.3 LTS konfigurieren **Iceberg Reads** Delta-Lake-Tabellen so, dass sie automatisch Iceberg-Metadaten generieren — Iceberg-Clients können so Delta-Lake-Daten lesen, ohne Dateien neu schreiben zu müssen. Das **Universal Format (UniForm)** erzeugt dabei automatisch Iceberg-Metadaten neben den Delta-Lake-Metadaten, ohne die Parquet-Datendateien neu zu schreiben — „eine einzige Kopie der Datendateien unterstützt sowohl Delta- als auch Iceberg-Clients." Die Iceberg-Client-Unterstützung ist dabei **nur lesend**.

Ausführlich behandelt — inklusive Aktivierungssyntax, asynchroner Metadaten-Generierung, VACUUM-Verhalten, Verifikation und aller Einschränkungen — in [Table Features/14 Iceberg Reads (UniForm).md](Table%20Features/14%20Iceberg%20Reads%20%28UniForm%29.md).

### Quelle

- https://docs.databricks.com/aws/en/delta/iceberg-reads

---

## <a id="zusammenfassung">10. Zusammenfassung</a>

- **Apache Iceberg** ist ein offenes Tabellenformat, das Databricks als zweite Option neben Delta Lake vollständig unterstützt — inklusive Schema Evolution, Time Travel und Hidden Partitioning.
- **Managed Iceberg Tables** über Unity Catalog sind vollständig integriert (Liquid Clustering, Predictive Optimization) und lese-/schreibfähig; **Foreign Iceberg Tables** aus externen Catalogs sind nur lesend.
- Zahlreiche **Einschränkungen** betreffen Dateiformat/Datentypen, Löschungen/Partitionierung sowie Zugriff und Integration — jeweils unterschiedlich ausgeprägt für Managed und Foreign Tables (siehe Abschnitt 6).
- **Iceberg v3** bringt Deletion Vectors, den VARIANT-Datentyp und Row Lineage — erfordert Databricks Runtime 18 LTS.
- Iceberg-Tabellen unterstützen ausschließlich **Deep Cloning**, kein Shallow Cloning — auch das Übernehmen von Foreign-Tables in Unity Catalog erfolgt per Deep Clone.
- Für einen vertieften, quellenübergreifend geprüften Vergleich zu Delta Lake (Architektur, Governance, Engine-Unterstützung, Anwendungsfälle) siehe [Tabellenkonzepte und Tabellentypen.md](01%20Tabellenkonzepte%20und%20Tabellentypen.md), Abschnitt 3, „Vertiefung: Delta Lake vs. Apache Iceberg".
- Das **Universal Format (UniForm)** lässt Delta-Lake-Tabellen zusätzlich Iceberg-Metadaten generieren, sodass Iceberg-Clients dieselben Parquet-Dateien nutzen können, ohne dass Daten dupliziert werden müssen — allerdings nur lesend für Iceberg-Clients.
