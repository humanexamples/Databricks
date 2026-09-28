# Schema Enforcement

Databricks validiert die Datenqualität, indem es beim Schreiben ein Schema für Delta-Lake-Tabellen erzwingt. Das gilt nur für das Delta-Lake-Format, nicht für CSV- oder JSON-Dateien.

## Regeln bei INSERT-Operationen

Zwei Regeln gelten für INSERT-Befehle:

1. Alle eingefügten Spalten müssen in der Zieltabelle existieren.
2. Die Datentypen der Spalten müssen zu den Typen der Zieltabelle passen.

Databricks versucht dabei, Spaltendatentypen sicher auf den Zieltyp zu casten.

### Fehlschlagendes INSERT-Beispiel

Dieser Befehl schlägt fehl, weil `unknown_column` nicht in der Zieltabelle existiert.

```sql
%sql
INSERT INTO catalog.schema.target_table (id, unknown_column) VALUES (1, 'value');
```

### Erfolgreiches INSERT mit Typ-Casting

```sql
%sql
INSERT INTO catalog.schema.target_table (id, bigint_column) VALUES (1, 42);
```

## Regeln bei MERGE-Operationen

- Datentypen werden ebenfalls sicher gecastet, wo möglich.
- Zielspalten in UPDATE- oder INSERT-Aktionen müssen existieren.
- Bei `INSERT *` oder `UPDATE SET *` muss die Quelle alle Zielspalten enthalten. Zusätzliche Quellspalten werden ignoriert.

### Fehlschlagendes MERGE-Beispiel

```sql
%sql
MERGE INTO catalog.schema.target_table AS t
USING catalog.schema.source_table AS s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.unknown_column = s.value
WHEN NOT MATCHED THEN INSERT (id, unknown_column) VALUES (s.id, s.value);
```

### Erfolgreiches MERGE mit Platzhalter

```sql
%sql
MERGE INTO catalog.schema.target_table AS t
USING catalog.schema.source_table AS s
ON t.id = s.id
WHEN NOT MATCHED THEN INSERT *;
```

## Schema gezielt ändern

### Explizites ALTER TABLE

```sql
%sql
ALTER TABLE catalog.schema.table_name ADD COLUMN new_column STRING;
```

### Schema-Evolution aktivieren (SQL)

```sql
%sql
SET spark.databricks.delta.schema.autoMerge.enabled = true;
INSERT INTO catalog.schema.table_name SELECT * FROM source_table;
```

### Schema-Evolution aktivieren (Python)

```python
df.write.option("mergeSchema", "true").mode("append").saveAsTable("catalog.schema.table_name")
```

## Externe Tabellen

Bei externen Tabellen synchronisieren sich Metadatenänderungen, die außerhalb von Databricks passieren, nicht automatisch mit Unity Catalog. Das beeinflusst das Schema Enforcement. Folgender Befehl löst das Problem:

```sql
%sql
MSCK REPAIR TABLE <table-name> SYNC METADATA
```

---
**Quelle:** https://docs.databricks.com/aws/en/tables/schema-enforcement  
**Stand:** 2026-08-06
