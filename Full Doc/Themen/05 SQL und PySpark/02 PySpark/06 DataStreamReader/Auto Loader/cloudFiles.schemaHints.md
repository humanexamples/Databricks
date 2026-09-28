# `cloudFiles.schemaHints`

Erzwingt einzelne Spaltentypen während der Schema-Inferenz.

## Beschreibung

> *"Schema information that you specify to Auto Loader during schema inference."*

Gibt bekannte Typen für einzelne — auch verschachtelte — Felder vor, während der Rest des Schemas weiterhin ganz normal inferiert wird. Wird nur verwendet, wenn **kein** explizites `schema` angegeben ist, und funktioniert unabhängig davon, ob `cloudFiles.inferColumnTypes` an oder aus ist. Auch noch gar nicht vorhandene Spalten lassen sich damit vorab deklarieren; historische Zeilen erhalten dafür dann `NULL`. Für Struct-Felder wird Punktnotation verwendet, `.element` adressiert Array-Elemente, `.key`/`.value` Einträge in einer Map. Array-/Map-Hints sind ab Databricks Runtime 9.1 LTS unterstützt.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.schemaHints", "tags map<string,string>, version int, user_info.dob DATE")
      .load("/Volumes/analytics/bronze/events"))
```

```sql
CREATE OR REFRESH STREAMING TABLE events
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaLocation => '/Volumes/analytics/bronze/_schema',
  schemaHints => 'loyalty_tier STRING, region_code STRING'
);
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
