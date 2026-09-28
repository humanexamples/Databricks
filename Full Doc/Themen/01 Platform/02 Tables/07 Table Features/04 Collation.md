# Collation

Ab Databricks Runtime 16.4 LTS lässt sich die Collation auf String-Feldern in Delta-Lake-Tabellen festlegen — ermöglicht die Steuerung von „String-Vergleichen und Sortierverhalten auf Spaltenebene, etwa Case-Insensitive-Matching oder Locale-bewusste Sortierung." Die Standard-Collation für String-Felder ist `UTF8_BINARY`. Die Aktivierung fügt das Writer-Table-Feature `collations` hinzu. Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Tabellen mit Collation erstellen

Collation lässt sich auf Spaltenebene bei der Tabellenerstellung festlegen, anwendbar auf: Top-Level-String-Spalten, String-Felder in verschachtelten Typen (STRUCT, ARRAY), MAP-Values (nicht Keys).

```sql
CREATE TABLE catalog.schema.my_table (
  id BIGINT,
  name STRING COLLATE UTF8_LCASE,
  metadata STRUCT<label: STRING COLLATE UNICODE>,
  tags ARRAY<STRING COLLATE UTF8_LCASE>,
  properties MAP<STRING, STRING COLLATE UTF8_LCASE>
) USING delta;
```

## 2. Bestehende Spalten ändern

```sql
ALTER TABLE my_table ALTER COLUMN name TYPE STRING COLLATE UTF8_LCASE;

-- Auf Standard zurücksetzen
ALTER TABLE my_table ALTER COLUMN name TYPE STRING COLLATE UTF8_BINARY;
```

## 3. Wartung nach Collation-Änderung

```sql
ANALYZE TABLE my_table COMPUTE DELTA STATISTICS;
OPTIMIZE FULL my_table;
SET spark.databricks.optimize.incremental = false;
OPTIMIZE my_table ZORDER BY zorder_column;
```

Diese Schritte zu überspringen führt **nicht** zu falschen Ergebnissen, kann aber die Query-Performance reduzieren.

## 4. Verhalten bei Schema Evolution

- Bestehende Quellspalten behalten die Collation der Zieltabelle bei.
- Neue Quellspalten mit Collation übernehmen diese Collation in der Zieltabelle.
- Das `collations`-Feature aktiviert sich automatisch, sobald collatierte Spalten zu einer Tabelle hinzugefügt werden, die es noch nicht nutzt.

## 5. Deaktivierung

```sql
ALTER TABLE my_table ALTER COLUMN name TYPE STRING COLLATE UTF8_BINARY;
ALTER TABLE my_table DROP FEATURE collations;
```

## 6. Wichtige Einschränkungen

- Externe Reader, die Collations nicht erkennen, fallen standardmäßig auf `UTF8_BINARY` zurück.
- Iceberg-Reads für Tabellen mit Collation nicht unterstützt.
- Nicht nutzbar in `CHECK`-Constraints, Generated Columns oder Bloom-Filter-Indizes.
- Inkompatibel mit zustandsbehafteten Structured-Streaming-Queries.
- OSS-Delta-Lake-APIs (Scala/Python) unterstützen keine Collations.

## 7. Verwandte Themen

- Runtime-Anforderungen und Protokollversion im Gesamtüberblick: siehe [08 Feature Compatibility.md](08%20Feature%20Compatibility.md).

### Quelle

- https://docs.databricks.com/aws/en/tables/features/collation
