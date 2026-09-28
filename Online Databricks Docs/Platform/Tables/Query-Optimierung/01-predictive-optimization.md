# Predictive Optimization für Unity Catalog Managed Tables

Predictive Optimization führt automatisch `OPTIMIZE`, `VACUUM` und `ANALYZE` auf Unity Catalog Managed Tables aus. Manuelle Wartung entfällt dadurch.

## Die drei Operationen

- **OPTIMIZE**: verbessert die Abfrageleistung durch Datei-Optimierung und inkrementelles Clustering.
- **VACUUM**: senkt Speicherkosten, indem nicht mehr referenzierte Datendateien entfernt werden.
- **ANALYZE**: sammelt Statistiken, um die Abfrageleistung zu verbessern.

Wichtiger Hinweis: `ZORDER` wird von Predictive Optimization nicht ausgeführt.

## Aktivierungsstatus

Predictive Optimization ist standardmäßig aktiv für Konten, die ab dem 11. November 2024 erstellt wurden. Der schrittweise Rollout für bestehende Konten soll bis August 2026 abgeschlossen sein.

## Voraussetzungen

- Premium-Plan oder höher in unterstützten Regionen
- SQL Warehouses oder Databricks Runtime 12.2 LTS oder höher
- Nur für Unity Catalog Managed Tables

## Abrechnung

Die Operationen laufen über Serverless Compute. Die Abrechnung erfolgt über die Serverless-Jobs-SKU.

## Predictive Optimization aktivieren oder deaktivieren

```sql
%sql
ALTER CATALOG [catalog_name] { ENABLE | DISABLE | INHERIT } PREDICTIVE OPTIMIZATION;
ALTER { SCHEMA | DATABASE } schema_name { ENABLE | DISABLE | INHERIT } PREDICTIVE OPTIMIZATION;
ALTER TABLE table_name { ENABLE | DISABLE | INHERIT } PREDICTIVE OPTIMIZATION;
```

## Status überprüfen

```sql
%sql
DESCRIBE (CATALOG | SCHEMA | TABLE) EXTENDED name
```

## Einschränkungen

Predictive Optimization läuft nicht für Open-Sharing-Empfänger und nicht für External Tables.

---
**Quelle:** https://docs.databricks.com/aws/en/optimizations/predictive-optimization  
**Stand:** 2026-08-06
