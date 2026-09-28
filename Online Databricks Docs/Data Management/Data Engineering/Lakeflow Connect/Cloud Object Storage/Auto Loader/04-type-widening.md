# Automatisches Type Widening in Auto Loader

Auto Loader unterstützt automatisches Type Widening, um kompatible Datentypänderungen ohne manuelles Eingreifen zu verarbeiten. Das reduziert den Wartungsaufwand für Pipelines durch automatische Schema-Evolution.

## Unterstützte Typänderungen

| Quelltyp | Erweiterbar auf |
| --- | --- |
| `byte` | `short`, `int`, `long`, `decimal`, `double` |
| `short` | `int`, `long`, `decimal`, `double` |
| `int` | `long`, `decimal`, `double` |
| `long` | `decimal` |
| `float` | `double` |
| `decimal` | `decimal` mit größerer Präzision/Skalierung |
| `date` | `timestampNTZ` (nur Parquet) |

Beim Erweitern numerischer Typen auf `decimal` passt sich die Präzision je nach Ausgangstyp an (byte/short/int: 10; long: 20).

## Voraussetzungen

- Databricks Runtime 16.4 oder höher
- Type Widening muss auf der Delta-Lake-Tabelle aktiviert sein:

```sql
%sql
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true')
```

```sql
%sql
CREATE TABLE T(c1 INT) TBLPROPERTIES('delta.enableTypeWidening' = 'true')
```

## Type Widening aktivieren

In den Schema-Evolution-Einstellungen `addNewColumnsWithTypeWidening` angeben:

```python
query = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.inferColumnTypes", True)
  .option("cloudFiles.schemaLocation", <schemaPath>)
  .option("cloudFiles.schemaEvolutionMode", "addNewColumnsWithTypeWidening")
  .load(<inputPath>)
  .writeStream
  .option("mergeSchema", "true")
  .option("checkpointLocation", <checkpointPath>)
  .trigger(availableNow=True)
  .toTable("table_name"))
```

## Verhalten bei Schema-Evolution

Bei `addNewColumnsWithTypeWidening` schlägt der Stream fehl: Neue Spalten werden zum Schema hinzugefügt und unterstützte Typänderungen erweitert, während nicht unterstützte Konvertierungen in die Rescued-Data-Spalte wandern.

## Einschränkungen

- `prefersDecimal` darf bei diesem Modus nicht auf `false` gesetzt werden (Standard: `true`).
- Die Erweiterung von `date` auf `timestampNTZ` gilt nur für Parquet-Dateien.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/type-widening  
**Stand:** 2026-08-07
