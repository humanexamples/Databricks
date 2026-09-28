# Apache Iceberg in Databricks: Übersicht

Apache Iceberg ist ein offenes Tabellenformat für Analytics-Workloads. Databricks unterstützt Iceberg-Tabellen direkt. Dieser Artikel erklärt die Grundlagen.

## Was ist Apache Iceberg?

Apache Iceberg ist ein Open-Source-Tabellenformat. Es unterstützt Schema-Evolution, Time Travel und verstecktes Partitionieren (Hidden Partitioning). Databricks nutzt für Iceberg-Tabellen das Apache-Parquet-Dateiformat. Unterstützt werden die Iceberg-Spezifikationsversionen 1, 2 und 3.

Für jede Tabellenänderung schreibt Databricks eine neue Metadatendatei. Das sorgt für Atomarität. So bleiben ACID-Transaktionen auf Objektspeicher möglich.

## Der Iceberg-Katalog

Ein Iceberg-Katalog ist die oberste Architekturebene. Er liefert beim Laden einer Tabelle die aktuellen Metadaten. Er verwaltet auch Operationen wie Erstellen, Löschen und Umbenennen von Tabellen.

Databricks unterstützt zwei Arten von Katalogen:

- Kataloge, die von Unity Catalog verwaltet werden
- Fremde (foreign) Kataloge, zum Beispiel AWS Glue, Hive Metastore oder Snowflake Horizon Catalog

## Voraussetzungen

- Ein Workspace mit aktiviertem Unity Catalog
- Databricks Runtime 16.4 LTS oder höher
- Für Managed Tables: Serverless Compute muss aktiviert sein

## Managed Tables erstellen

Managed Iceberg-Tabellen lassen sich über Databricks Runtime, Databricks SQL oder externe Iceberg-kompatible Engines erstellen. Dazu zählen zum Beispiel Apache Spark, Flink, Trino und Kafka.

Managed Tables in Unity Catalog bieten zusätzliche Vorteile:

- Unity Catalog übernimmt Aufgaben zum Lebenszyklus der Tabelle
- Liquid Clustering verbessert die Performance
- Predictive Optimization senkt die Kosten
- Materialized Views unterstützen inkrementelles Refresh
- Streaming Tables laden Daten inkrementell

Das folgende Beispiel erstellt eine materialisierte View im Iceberg-Format:

```sql
%sql
CREATE MATERIALIZED VIEW <mv_name>
USING ICEBERG
AS
SELECT * FROM samples.nyctaxi.trips;
```

Mit `REPAIR TABLE` lassen sich Metadaten synchronisieren:

```sql
%sql
REPAIR TABLE <mv_name> SYNC METADATA;
```

## Partitionsfelder ändern

Bei managed Iceberg-Tabellen lassen sich Partitionsfelder nachträglich hinzufügen, entfernen oder ersetzen:

```sql
%sql
ALTER TABLE catalog.schema.table ADD PARTITION FIELD column_name;
```

```sql
%sql
ALTER TABLE catalog.schema.table DROP PARTITION FIELD column_name;
```

```sql
%sql
ALTER TABLE catalog.schema.table REPLACE PARTITION FIELD old_column WITH new_column;
```

## Foreign Tables

Foreign Iceberg-Tabellen werden von einem externen Katalog verwaltet. Sie sind nur lesbar (read-only). Sie bieten weniger Plattform-Funktionen als Managed Tables.

## Bekannte Einschränkungen

- Foreign Iceberg-Tabellen sind nur lesbar
- Nicht unterstützte Datentypen: UUID, Fixed(L), TIME und verschachtelte STRUCT-Felder mit Pflichtangabe (required)
- Position Deletes für Iceberg v2 werden nicht unterstützt
- Branching und Tagging werden nicht unterstützt
- Partitionierung nach dem Typ BINARY wird nicht unterstützt
- Ausdrucksbasierte Partition-Transformationen werden für Managed Tables über Databricks SQL nicht unterstützt

---
**Quelle:** https://docs.databricks.com/aws/en/iceberg/  
**Stand:** 2026-08-06
