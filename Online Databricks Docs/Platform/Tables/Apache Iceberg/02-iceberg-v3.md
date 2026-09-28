# Apache Iceberg v3 in Databricks

Iceberg v3 bringt neue Funktionen für Managed Tables. Das gilt sowohl für native Iceberg-Tabellen als auch für Delta-Lake-Tabellen mit Iceberg-Lesezugriff über Unity Catalog.

## Drei neue Kernfunktionen

- **Deletion Vectors:** Ermöglichen effiziente zeilenweise Löschungen, ohne Dateien neu zu schreiben.
- **VARIANT-Datentyp:** Unterstützt die Speicherung und Verarbeitung von semi-strukturierten Daten.
- **Row Lineage:** Verfolgt inkrementelle Datenänderungen nach.

## Voraussetzungen

- Ein Workspace mit aktiviertem Unity Catalog
- Databricks Runtime 18 LTS oder höher

## Tabellen erstellen

Eine Delta-Lake-Tabelle mit Iceberg-v3-Kompatibilität legen Sie so an:

```sql
%sql
CREATE OR REPLACE TABLE main.schema.table (c1 INT) TBLPROPERTIES(
  'delta.universalFormat.enabledFormats' = 'iceberg',
  'delta.enableIcebergCompatV3' = 'true');
```

Eine native Iceberg-v3-Tabelle legen Sie so an:

```sql
%sql
CREATE OR REPLACE TABLE main.schema.table (c1 INT) USING iceberg
TBLPROPERTIES ('format-version' = 3);
```

## Bestehende Tabellen upgraden

Delta-Lake-Tabellen upgraden Sie mit:

```sql
%sql
ALTER TABLE catalog.schema.table SET TBLPROPERTIES(
  'delta.enableIcebergCompatV3' = 'true',
  'delta.enableIcebergCompatV2' = 'false');
```

Iceberg-Tabellen upgraden Sie mit:

```sql
%sql
ALTER TABLE catalog.schema.table SET TBLPROPERTIES (
  'format-version' = 3);
```

## Deletion Vectors

Deletion Vectors optimieren zeilenweise Änderungen. Bei neuen v3-Tabellen sind sie standardmäßig aktiviert.

Für Delta Lake:

```sql
%sql
CREATE TABLE catalog.schema.table (c1 INT) TBLPROPERTIES(
  'delta.enableDeletionVectors' = 'true',
  'delta.enableIcebergCompatV3' = 'true',
  'delta.universalFormat.enabledFormats' = 'iceberg');
```

Für Iceberg:

```sql
%sql
CREATE TABLE catalog.schema.table (c1 INT) USING ICEBERG
TBLPROPERTIES ('iceberg.enableDeletionVectors' = 'true');
```

## Der VARIANT-Datentyp

Für Delta Lake:

```sql
%sql
CREATE TABLE catalog.schema.deltaTable (col VARIANT) TBLPROPERTIES(
  'delta.enableIcebergCompatV3' = 'true',
  'delta.universalFormat.enabledFormats' = 'iceberg');
```

Für Iceberg:

```sql
%sql
CREATE TABLE catalog.schema.icebergTable (col VARIANT) USING iceberg;
```

Eine VARIANT-Spalte zu einer bestehenden Tabelle hinzufügen:

```sql
%sql
ALTER TABLE catalog.schema.table ADD COLUMN variant_col VARIANT;
```

## Tabellen zurückstufen (Downgrade)

Um zu einer früheren Version zurückzukehren, verwenden Sie `RESTORE TABLE`. Dafür muss ein Protokoll-Downgrade erlaubt sein:

```sql
%sql
set spark.databricks.delta.restore.protocolDowngradeAllowed = true;
RESTORE TABLE catalog.schema.table TO VERSION AS OF 1;
set spark.databricks.delta.restore.protocolDowngradeAllowed = false;
```

## Einschränkungen

Databricks unterstützt bei v3 aktuell nicht:

- Schreib-Standardwerte (write defaults)
- Initiale Standardwerte (initial defaults)
- Unbekannte Datentypen
- Zeitstempel mit Nanosekunden-Genauigkeit
- Transformationen mit mehreren Argumenten

---
**Quelle:** https://docs.databricks.com/aws/en/iceberg/iceberg-v3  
**Stand:** 2026-08-06
