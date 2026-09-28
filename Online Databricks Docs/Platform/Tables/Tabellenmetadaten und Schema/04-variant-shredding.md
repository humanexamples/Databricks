# Variant Shredding

Variant Shredding verbessert die Abfrageleistung auf `VARIANT`-Spalten. Häufig vorkommende Felder werden dabei als eigene Spalten in den zugrunde liegenden Parquet-Dateien gespeichert.

## Vorteile

- Weniger I/O beim Lesen einzelner Felder.
- Bessere Kompression durch das spaltenorientierte Format statt einer binären Speicherung.

## Voraussetzungen

Zum Lesen und Schreiben von geshredderten VARIANT-Tabellen ist Databricks Runtime 17.3 oder höher nötig. Für optimale Leistung bei Statistiken und Data Skipping wird Runtime 18.1 oder höher empfohlen.

## Shredding aktivieren

### Automatisch

Neue Tabellen, die mit `CREATE TABLE` und einer VARIANT-Spalte angelegt werden, haben Shredding automatisch aktiviert.

### Manuell für bestehende Tabellen

Für Delta-Lake-Tabellen:

```sql
%sql
ALTER TABLE my_table SET TBLPROPERTIES ('delta.enableVariantShredding' = 'true');
```

Für Iceberg-Tabellen:

```sql
%sql
ALTER TABLE my_table SET TBLPROPERTIES ('iceberg.enableVariantShredding' = 'true');
```

## Shredding deaktivieren

```sql
%sql
ALTER TABLE my_table SET TBLPROPERTIES ('delta.enableVariantShredding' = 'false');
```

## Shredding vollständig entfernen

```sql
%sql
ALTER TABLE my_table DROP FEATURE "variantShredding";
```

Dieser Befehl schreibt die Daten in ein ungeshreddertes Format zurück und deaktiviert das Feature.

## Einschränkungen

- Schreibvorgänge haben zusätzlichen Overhead.
- Bestehende Daten müssen manuell über `REORG TABLE` neu geschrieben werden.
- Gilt nur für Top-Level-VARIANT-Spalten oder VARIANT-Felder in Structs.
- VARIANT-Daten innerhalb von Arrays oder Maps sind ausgeschlossen.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/features/variant-shredding  
**Stand:** 2026-08-06
