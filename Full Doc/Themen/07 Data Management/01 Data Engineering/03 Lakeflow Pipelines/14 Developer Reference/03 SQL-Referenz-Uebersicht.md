# SQL-Referenz-Übersicht für Lakeflow Declarative Pipelines

## Grundzweck

Die SQL-Programmierschnittstelle von Lakeflow Declarative Pipelines definiert Pipelines mit `CREATE`-Statements, `CREATE FLOW` und `AUTO CDC INTO`.

Für konzeptionelle Informationen und einen Überblick über die Verwendung von Lakeflow-Pipelines-SQL siehe die Datei `SQL-Entwicklung.md` in diesem Ordner. Für Informationen zur Python-API siehe die Python-Sprachreferenz für Lakeflow-Pipelines im Nachbarordner `Python-Referenz/`.

Python-User-Defined-Functions (UDFs) lassen sich in SQL-Abfragen verwenden — diese UDFs müssen jedoch vor dem Aufruf in SQL-Quelldateien in Python-Dateien definiert werden.

## SQL-Statements

Die folgenden Statements dienen dazu, mit Pipelines in SQL zu arbeiten — jedes ist in einer eigenen Datei im Unterordner `SQL-Referenz/` dieses Ordners dokumentiert:

- `AUTO CDC INTO` — siehe `SQL-Referenz/AUTO CDC INTO.md`
- `CREATE FLOW` — siehe `SQL-Referenz/CREATE FLOW.md`
- `CREATE MATERIALIZED VIEW` — siehe `SQL-Referenz/CREATE MATERIALIZED VIEW.md`
- `CREATE STREAMING TABLE` — siehe `SQL-Referenz/CREATE STREAMING TABLE.md`
- `CREATE TABLE ... FLOW` — siehe `SQL-Referenz/CREATE TABLE ... FLOW.md`
- `CREATE TEMPORARY VIEW` — siehe `SQL-Referenz/CREATE TEMPORARY VIEW.md`
- `CREATE VIEW` — siehe `SQL-Referenz/CREATE VIEW.md`

Zusätzlich lassen sich die folgenden Statements verwenden, um mit Pipelines zu arbeiten — diese müssen jedoch aus Databricks SQL heraus ausgeführt werden, nicht aus einer Pipeline selbst (nicht Teil dieses Dokumentationsblocks, da sie außerhalb der eigentlichen Pipeline-SQL-Sprache liegen):

- `ALTER STREAMING TABLE` (allgemeine SQL-Sprachreferenz)
- `ALTER MATERIALIZED VIEW` (allgemeine SQL-Sprachreferenz)
- `EXPLAIN CREATE MATERIALIZED VIEW` (allgemeine SQL-Sprachreferenz)

## Quellen

- Pipeline SQL language reference (Übersicht über die SQL-Statements für Lakeflow-Pipelines, Abgrenzung zu den nur aus Databricks SQL nutzbaren `ALTER`-/`EXPLAIN`-Statements, UDF-Hinweis): https://docs.databricks.com/aws/en/ldp/developer/sql-ref

**Stand:** 2026-08-19.
