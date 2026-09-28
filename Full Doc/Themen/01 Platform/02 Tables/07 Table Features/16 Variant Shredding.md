# Variant Shredding

„Variant Shredding verbessert die Query-Performance auf `VARIANT`-Spalten, indem häufig vorkommende Felder als separate Spalten in den zugrunde liegenden Parquet-Dateien gespeichert werden." Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Performance-Vorteile

Die Technik reduziert den I/O-Bedarf beim Zugriff auf Felder und verbessert die Datenkompression durch spaltenbasierte statt Binary-Blob-Speicherung.

## 2. Voraussetzungen

Databricks Runtime 17.3 oder später zum Lesen/Schreiben geshreddeter VARIANT-Tabellen. Für optimale Performance bei Variant-Statistiken und Data Skipping wird Runtime 18.1+ empfohlen.

## 3. Aktivierung

Neue Tabellen mit VARIANT-Spalten haben Shredding ab Runtime 17.3 nur über `CREATE TABLE` automatisch aktiviert — **nicht** über `CREATE OR REPLACE TABLE` oder `ALTER TABLE`. In diesen Fällen sowie bei bestehenden Tabellen ist manuelle Aktivierung nötig:

```sql
-- Delta Lake
ALTER TABLE my_table SET TBLPROPERTIES ('delta.enableVariantShredding' = 'true');

-- Iceberg
ALTER TABLE my_table SET TBLPROPERTIES ('iceberg.enableVariantShredding' = 'true');
```

**Bestehende Daten nachträglich shredden:**

```sql
REORG TABLE my_table APPLY (SHRED VARIANT);
```

## 4. Deaktivierung und Entfernung

```sql
-- Für zukünftige Schreibvorgänge deaktivieren
ALTER TABLE my_table SET TBLPROPERTIES ('delta.enableVariantShredding' = 'false');

-- Bestehende geshredderte Daten entfernen und Feature deaktivieren
ALTER TABLE my_table DROP FEATURE "variantShredding";
```

## 5. Wichtige Einschränkungen

- Schreibvorgänge verursachen zusätzlichen Overhead.
- Die Aktivierung konvertiert keine bestehenden Daten — betrifft nur neue Schreibvorgänge.
- Gilt nur für Top-Level-VARIANT-Spalten und Struct-Felder (VARIANT-Daten innerhalb von Arrays oder Maps ausgeschlossen).

## 6. Verwandte Themen

- Grundlagen des VARIANT-Datentyps: siehe [15 Variant.md](15%20Variant.md).
- Allgemeines Vorgehen beim Entfernen von Features: siehe [07 Drop Feature.md](07%20Drop%20Feature.md).

### Quelle

- https://docs.databricks.com/aws/en/tables/features/variant-shredding
