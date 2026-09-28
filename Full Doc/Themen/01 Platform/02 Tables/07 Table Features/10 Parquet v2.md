# Parquet v2

Parquet v2 ist ab Databricks Runtime 18.1 verfügbar. Es verbessert Delta-Lake- und Apache-Iceberg-Tabellen durch „fortgeschrittene Encodings, v2-Datenseiten-Header und `INT64`-Timestamps." Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Wesentliche Verbesserungen

- **Fortgeschrittene Encodings:** Integer- und String-Spalten nutzen neuere Encoding-Methoden mit besserer Kompression und Dekodier-Performance gegenüber Parquet v1.
- **V2-Datenseiten-Header:** Seiten-Level-Statistiken und -Indizes verbessern Predicate Pushdown und Data-Skipping-Fähigkeiten (siehe [Data Skipping und Tabellenstatistiken.md](../../../09%20Performance%20Optimization/01%20Foundation%20Design/04%20Data%20Skipping%20und%20Tabellenstatistiken.md)), reduzieren die zur Query-Zeit gescannte Datenmenge.
- **INT64-Timestamps:** ersetzt das Legacy-`INT96`-Format, verbessert Spaltenstatistiken, Timestamp-Encoding und Kompressionseffizienz.

## 2. Aktivierung

Databricks upgradet kompatible Unity-Catalog-Managed-Tables automatisch (siehe [Managed Tables.md](../03%20Managed%20Tables.md), Abschnitt 6). Für manuelle Aktivierung die Tabelleneigenschaft `parquet.format.version` auf `2.12.0` setzen.

**Für bestehende Delta-Lake-Tabellen:**

```sql
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.parquet.format.version' = '2.12.0');
```

**Für bestehende Iceberg-Tabellen:**

```sql
ALTER TABLE <table_name> SET TBLPROPERTIES ('iceberg.parquet.format.version' = '2.12.0');
```

**Für neue Delta-Lake-Tabellen:**

```sql
CREATE TABLE <table_name> (...) TBLPROPERTIES ('delta.parquet.format.version' = '2.12.0');
```

**Für neue Iceberg-Tabellen:**

```sql
CREATE TABLE <table_name> (...) USING iceberg TBLPROPERTIES ('iceberg.parquet.format.version' = '2.12.0');
```

Nach der Konfiguration nutzen „alle nachfolgenden Schreibvorgänge v2-Encodings. Parquet-v1- und -v2-Dateien können in derselben Tabelle koexistieren."

## 3. Bestehende Dateien neu schreiben

Ab Databricks Runtime 18.2+ über `REORG TABLE`:

```sql
REORG TABLE <table_name> APPLY (SET PARQUET (FORMAT_VERSION = '2.12.0'));
```

## 4. Rückgängigmachen

```sql
REORG TABLE <table_name> APPLY (SET PARQUET (FORMAT_VERSION = '1.0.0'));
```

## 5. Einschränkungen

- Externe Iceberg-Reader unterstützen v2 möglicherweise nicht — Kompatibilität vorab prüfen.
- OpenSharing-Empfänger-Clients müssen v2-Encodings unterstützen.
- Materialized Views und Streaming Tables erfordern manuelle Aktivierung.

### Quelle

- https://docs.databricks.com/aws/en/tables/features/parquet-v2
