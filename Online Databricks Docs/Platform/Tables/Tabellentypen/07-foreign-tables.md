# Mit Foreign Tables arbeiten

Foreign Tables (auch Fremdtabellen genannt) werden über Unity Catalog als Teil eines Foreign Catalog registriert. Diese Seite erklärt, was Foreign Tables sind und wann man sie einsetzt.

## Definition

Foreign Tables enthalten Daten und Metadaten, die von externen Systemen verwaltet werden. Unity Catalog fügt Data Governance hinzu.

## Registrierungsmethoden

- **Query Federation**: nutzt sichere JDBC-Verbindungen, um Anfragen an externe Datensysteme wie PostgreSQL oder MySQL weiterzuleiten.
- **Catalog Federation**: verbindet externe Kataloge, etwa Hive Metastore, AWS Glue oder Snowflake Horizon Catalog.

## Wann Foreign Tables sinnvoll sind

Foreign Tables eignen sich als Übergangslösung, um auf externe Daten zuzugreifen, ohne sie zu migrieren. Für häufig abgefragte Datensätze empfiehlt Databricks den Wechsel zu Unity Catalog Managed Tables, da diese eine bessere Performance und Optimierung bieten.

## Erstellung und Schreibrechte

- Schreibbar sind Foreign Tables nur, wenn der Workspace einen internen, föderierten Hive Metastore nutzt.
- Externe föderierte Hive Metastores und Tabellen über Lakehouse Federation sind nur lesbar.
- Das Feld *Updated by* zeigt den Benutzer, der die letzte Metadaten-Aktualisierung ausgelöst hat.
- Schreibvorgänge haben nicht die gleichen Transaktionsgarantien wie Unity Catalog Managed Tables.

## Weiterführende Links

- Dokumentation zu Query Federation
- Dokumentation zu Catalog Federation
- Anleitung: Foreign Tables zu Managed Tables konvertieren
- Referenz zu Unity Catalog Managed Tables

---
**Quelle:** https://docs.databricks.com/aws/en/tables/foreign  
**Stand:** 2026-08-06
