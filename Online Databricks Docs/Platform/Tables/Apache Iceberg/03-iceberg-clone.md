# Eine Managed-Iceberg-Tabelle klonen

Mit `DEEP CLONE` erstellen Sie eine unabhängige Kopie einer Managed-Iceberg-Tabelle. Der Klon kopiert Daten und Metadaten in eine neue Managed-Iceberg-Tabelle in Unity Catalog.

## Klon-Methoden je nach Quelle und Ziel

Managed Iceberg-Tabellen unterstützen nur Deep Clone (kein Shallow Clone).

| Quelle | Ziel | Operation |
| --- | --- | --- |
| Managed Iceberg | Managed Iceberg | DEEP CLONE |
| Foreign Iceberg | Managed Iceberg | DEEP CLONE |
| Parquet oder Foreign Iceberg | Managed oder External Delta Lake | Inkrementeller Klon |

## Voraussetzungen

- Databricks Runtime 16.4 LTS oder höher
- `SELECT`-Rechte auf die Quelltabelle
- `CREATE TABLE`-Rechte auf das Zielschema (falls eine bestehende Tabelle ersetzt wird)
- Predictive Optimization muss auf Zielkatalog oder Zielschema aktiviert sein

## Syntax für Deep Clone

Grundlegende Syntax:

```sql
%sql
CREATE TABLE <catalog>.<schema>.<target-table>
DEEP CLONE <catalog>.<schema>.<source-table>;
```

Eine bestehende Zieltabelle ersetzen:

```sql
%sql
CREATE OR REPLACE TABLE <catalog>.<schema>.<target-table>
DEEP CLONE <catalog>.<schema>.<source-table>;
```

Nur erstellen, wenn die Tabelle noch nicht existiert:

```sql
%sql
CREATE TABLE IF NOT EXISTS <catalog>.<schema>.<target-table>
DEEP CLONE <catalog>.<schema>.<source-table>;
```

## Anwendungsfälle

Eine Produktionstabelle archivieren:

```sql
%sql
CREATE TABLE prod_catalog.archive.orders_snapshot_may2026
DEEP CLONE prod_catalog.main.orders;
```

Eine Tabelle in eine Entwicklungsumgebung kopieren:

```sql
%sql
CREATE OR REPLACE TABLE dev_catalog.test.orders
DEEP CLONE prod_catalog.main.orders;
```

## Eine Foreign-Iceberg-Tabelle klonen

```sql
%sql
CREATE TABLE <uc-catalog>.<schema>.<target-table>
DEEP CLONE <foreign-catalog>.<schema>.<source-table>;
```

## Tabelleneigenschaften nach dem Klonen setzen

Tabelleneigenschaften werden beim Klonen nicht übernommen. Sie müssen sie danach manuell mit `ALTER TABLE` setzen:

```sql
%sql
CREATE TABLE prod_catalog.archive.orders_snapshot
DEEP CLONE prod_catalog.main.orders;
ALTER TABLE prod_catalog.archive.orders_snapshot
SET TBLPROPERTIES (
  'archive.source' = 'prod_catalog.main.orders',
  'archive.created_date' = '2026-05-11');
```

## Wichtiges Verhalten

- Deep Clones sind vollständige, unabhängige Kopien. Änderungen an der Kopie wirken sich nicht auf die Quelle aus.
- Jeder Klon hat seine eigene, unabhängige Snapshot-Historie.
- Schema, Partitionierung und Tabelleneigenschaften werden kopiert. Unity-Catalog-Tags werden nicht kopiert.
- Unity Catalog verwaltet den Klon nach dem Erstellen unabhängig von der Quelle.

## Einschränkungen

- Shallow Clone wird für Managed-Iceberg-Tabellen nicht unterstützt.
- Eine Zero-Copy-Migration von Foreign-Tabellen wird nicht unterstützt.
- Deep Clones kopieren die Tabellenhistorie nicht. Time Travel bezieht sich nur auf die Historie des Klons, nicht auf die der Quelle.
- Das Tabellenformat kann beim Klonen nicht geändert werden.
- Tabelleneigenschaften müssen nach dem Klonen separat gesetzt werden.

---
**Quelle:** https://docs.databricks.com/aws/en/iceberg/clone  
**Stand:** 2026-08-06
