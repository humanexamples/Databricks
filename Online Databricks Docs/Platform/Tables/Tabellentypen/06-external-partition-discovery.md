# Partitionserkennung für External Tables

Unity Catalog kann Partitionen von External Tables automatisch erkennen. Diese Seite erklärt die Strategien dafür und wie man sie optimiert.

## Empfehlung

Databricks empfiehlt Liquid Clustering statt klassischer Partitionierung. Das vereinfacht die Tabellenverwaltung und verbessert die Abfrageleistung. Unity Catalog erkennt Partitionen standardmäßig, indem es Verzeichnisse rekursiv auflistet. Bei großen Tabellen mit vielen Partitionsverzeichnissen empfiehlt sich zusätzlich das Partition Metadata Logging.

## Standard-Strategie zur Partitionserkennung

Standardmäßig durchsucht Unity Catalog rekursiv alle Verzeichnisse, um Partitionen zu finden. Bei großen Tabellen mit vielen Partitionsverzeichnissen kann das die Latenz erhöhen.

## Partition Metadata Logging aktivieren

SQL: Tabelle mit aktiviertem Logging erstellen

```sql
%sql
CREATE OR REPLACE TABLE <catalog>.<schema>.<table-name>
USING <format>
PARTITIONED BY (<partition-column-list>)
TBLPROPERTIES ('partitionMetadataEnabled' = 'true')
LOCATION 's3://<bucket-path>/<table-directory>';
```

Spark-Konfiguration

```sql
%sql
SET spark.databricks.nonDelta.partitionLog.enabled = true;
```

## Partitionen anzeigen

Alle Partitionen anzeigen

```sql
%sql
SHOW PARTITIONS <table-name>
```

Eine einzelne Partition prüfen

```sql
%sql
SHOW PARTITIONS <table-name>
PARTITION (<partition-column-name> = <partition-column-value>)
```

## Partitions-Metadaten reparieren

MSCK REPAIR-Varianten

```sql
%sql
MSCK REPAIR TABLE <table_name> SYNC PARTITIONS;
MSCK REPAIR TABLE <table_name> ADD PARTITIONS;
MSCK REPAIR TABLE <table_name> DROP PARTITIONS;
```

Partition manuell hinzufügen

```sql
%sql
ALTER TABLE <table-name>
ADD PARTITION (<partition-column-name> = <partition-column-value>)
LOCATION 's3://<bucket-path>/<table-directory>/<partition-directory>';
```

## Wichtige Einschränkungen

- Ein Lesezugriff über Verzeichnispfade liefert immer alle Partitionen, unabhängig vom Metadaten-Status.
- Pfadbasierte Insert- oder Overwrite-Operationen registrieren keine Partitions-Metadaten.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/external-partition-discovery  
**Stand:** 2026-08-06
