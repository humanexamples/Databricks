# Automatisches Löschen von Zeilen mit Auto-TTL

Auto Time-to-Live (Auto-TTL) entfernt automatisch Zeilen aus Unity-Catalog-Managed-Tables. Die Entfernung erfolgt nach einer festgelegten Zeitspanne, basierend auf den Werten einer Zeitstempel-Spalte.

## Wie funktioniert Auto-TTL?

Im Hintergrund führt Databricks automatisch `DELETE`-, `PURGE`- und `VACUUM`-Operationen aus. So werden abgelaufene Zeilen entfernt und endgültig aus dem Speicher gelöscht.

## Anwendungsfälle

- Daten entfernen, die älter als 1 Jahr sind, um Speicherkosten zu senken (365 Tage Ablaufzeit)
- Zum Löschen markierte Daten entfernen, mit 20 Tagen Ablaufzeit auf einer eigenen Zeitstempel-Spalte

## Voraussetzungen

- Predictive Optimization muss aktiviert sein
- `MODIFY`-Rechte auf der Tabelle
- Databricks Runtime 17.3 oder höher

## Auto-TTL aktivieren

### Delta Lake und Apache Iceberg Managed Tables

Für neue Tabellen:

```sql
%sql
CREATE TABLE table_name DELETE ROWS <expiration_days> DAYS AFTER <time_column_name>;
```

Für bestehende Tabellen:

```sql
%sql
ALTER TABLE table_name DELETE ROWS <expiration_days> DAYS AFTER <time_column_name>;
```

Beispiel:

```sql
%sql
ALTER TABLE my_catalog.my_schema.my_table DELETE ROWS 30 DAYS AFTER created_at;
```

### Streaming Tables mit Lakeflow-Pipelines

SQL-Syntax:

```sql
%sql
CREATE STREAMING TABLE table_name
DELETE ROWS <expiration_days> DAYS AFTER <time_column_name>
AS SELECT * FROM STREAM(source);
```

Python-Syntax:

```python
from pyspark import pipelines as dp

@dp.table(
    auto_ttl={"timestamp_column": <time_column_name>, "expire_in_days": <expiration_days>}
)
def function_name():
    return (query)
```

## Streaming-Reads konfigurieren

Für Structured Streaming, Lakeflow-Pipelines oder Streaming Tables, die von einer Auto-TTL-aktivierten Tabelle lesen, müssen Sie `skipChangeCommits` setzen.

Structured Streaming:

```python
spark.sql("ALTER TABLE source_table DELETE ROWS <expiration_days> DAYS AFTER <time_column_name>")
spark.readStream.format("delta").option("skipChangeCommits", "true").table("source_table")
```

Lakeflow-Pipelines:

```python
from pyspark import pipelines as dp

spark.sql("ALTER TABLE source_table DELETE ROWS <expiration_days> DAYS AFTER <time_column_name>")

@dp.table
def my_table():
    return spark.readStream.format("delta").option("skipChangeCommits", "true").table("source_table")
```

Streaming Tables:

```sql
%sql
ALTER TABLE source_table DELETE ROWS <expiration_days> DAYS AFTER <time_column_name>;
CREATE OR REFRESH STREAMING TABLE my_table AS
SELECT * FROM STREAM(source_table) OPTIONS (skipChangeCommits);
```

## Auto-TTL prüfen

Ob Auto-TTL aktiv ist, sehen Sie mit:

```sql
%sql
DESCRIBE TABLE EXTENDED table_name;
```

Oder mit den Tabelleneigenschaften:

```sql
%sql
SHOW TBLPROPERTIES table_name;
```

## Auto-TTL deaktivieren

Für Delta-Lake- und Iceberg-Tabellen:

```sql
%sql
ALTER TABLE table_name DROP ROW DELETION;
```

Für Streaming Tables in Python:

```python
from pyspark import pipelines as dp

@dp.table(
    auto_ttl=None
)
def function_name():
    return (query)
```

## Phasen des Daten-Lebenszyklus

| Phase | Dauer | Beschreibung |
| --- | --- | --- |
| Ablaufzeitraum | Benutzerdefiniert | Tage nach dem Zeitstempelwert, ab denen eine Zeile zum Löschen berechtigt ist |
| Pufferzeit | Bis zu 3 Tage pro Befehl | Verzögerung zwischen Ablauf und DELETE-/VACUUM-Operation (bis zu 6 Tage insgesamt) |
| Datenaufbewahrungsdauer | Benutzerdefiniert (Standard 7 Tage) | Zeitraum, in dem gelöschte Zeilen noch per Time Travel zugänglich sind |

## Ziel-Ablaufwert berechnen

```python
target_expiration_days = target_days - 6 - deletedFileRetentionDuration
```

Beispiel für eine Entfernung nach 30 Tagen bei 7 Tagen Standard-Aufbewahrung:

```python
target_expiration_days = 30 - 6 - 7  # = 17 days
```

Beispiel für eine Entfernung nach 90 Tagen bei 30 Tagen Aufbewahrung:

```python
target_expiration_days = 90 - 6 - 30  # = 54 days
```

## Auto-TTL überwachen

### Abfrage über eine Systemtabelle

```sql
%sql
WITH tables_with_deletes AS (
  SELECT DISTINCT catalog_name, schema_name, table_name
  FROM system.storage.predictive_optimization_operations_history
  WHERE
    operation_type = 'DELETE'
    AND timestampdiff(day, start_time, now()) < 7
)
SELECT hist.*
FROM system.storage.predictive_optimization_operations_history AS hist
INNER JOIN tables_with_deletes AS t
  ON hist.catalog_name = t.catalog_name
  AND hist.schema_name = t.schema_name
  AND hist.table_name = t.table_name
WHERE
  hist.operation_type IN ('DELETE', 'PURGE', 'VACUUM')
  AND timestampdiff(day, hist.start_time, now()) < 7
ORDER BY hist.start_time DESC;
```

### Abfrage zur Kostenschätzung

```sql
%sql
WITH tables_with_deletes AS (
  SELECT DISTINCT table_name
  FROM system.storage.predictive_optimization_operations_history
  WHERE
    operation_type = 'DELETE'
    AND timestampdiff(day, start_time, now()) < 30
)
SELECT SUM(usage_quantity) AS total_estimated_dbu
FROM system.storage.predictive_optimization_operations_history AS hist
INNER JOIN tables_with_deletes AS t
  ON hist.table_name = t.table_name
WHERE
  hist.operation_type IN ('DELETE', 'PURGE', 'VACUUM')
  AND hist.usage_unit = 'ESTIMATED_DBU'
  AND timestampdiff(day, hist.start_time, now()) < 30;
```

## Tabellenhistorie prüfen

```sql
%sql
DESCRIBE HISTORY table_name;
```

## Einschränkungen

- Wird nicht für materialisierte Views unterstützt.
- Die ALTER-Syntax steht für Änderungen an Auto-TTL bei Streaming Tables nicht zur Verfügung.
- Die Zeitspalte, die in der Auto-TTL-Regel definiert ist, kann nicht umbenannt werden.
- Seltene Transaktionskonflikte sind möglich. Liquid Clustering wird empfohlen.
- Probleme mit Private-Link-S3-Zugriff können zu Fehlern bei Serverless Compute führen.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/operations/auto-ttl  
**Stand:** 2026-08-06
