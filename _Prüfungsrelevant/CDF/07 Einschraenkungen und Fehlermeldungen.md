[← Übersicht](00%20Uebersicht.md)

# Einschränkungen und Fehlermeldungen

> Quellen: [Use change data feed on Databricks – Limitations](https://docs.databricks.com/aws/en/tables/features/change-data-feed) · [Column mapping](https://docs.databricks.com/aws/en/tables/features/column-mapping) · [Type widening](https://docs.databricks.com/aws/en/tables/features/type-widening) · [Delta Lake streaming](https://docs.databricks.com/aws/en/structured-streaming/delta-lake) · [Iceberg reads](https://docs.databricks.com/aws/en/delta/iceberg-reads) · [Smartsheet limits](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/smartsheet-limits) · [Error classes](https://docs.databricks.com/aws/en/error-messages/error-classes) · [TRANSACTION_NOT_SUPPORTED](https://docs.databricks.com/aws/en/error-messages/transaction-not-supported-error-class) · [MULTI_STATEMENT_TRANSACTION_NOT_SUPPORTED](https://docs.databricks.com/aws/en/error-messages/multi-statement-transaction-not-supported-error-class) · [DELTA_CONCURRENT_APPEND](https://docs.databricks.com/aws/en/error-messages/delta-concurrent-append-error-class) · [DELTA_CONCURRENT_DELETE_READ](https://docs.databricks.com/aws/en/error-messages/delta-concurrent-delete-read-error-class) · [DELTA_CONCURRENT_DELETE_DELETE](https://docs.databricks.com/aws/en/error-messages/delta-concurrent-delete-delete-error-class) · [CONFIG_NOT_AVAILABLE](https://docs.databricks.com/aws/en/error-messages/config-not-available-error-class)

## Einschränkungen

### Schemaänderungen und Column Mapping

Mit **Column Mapping** lassen sich Spalten umbenennen oder löschen, ohne Datendateien neu zu schreiben. Danach ist der CDF aber eingeschränkt. **Nicht-additive Schemaänderungen** sind:

- Spalten **umbenennen oder löschen**
- **Datentyp** einer Spalte ändern
- **Nullability** ändern (z. B. `ALTER COLUMN ... SET NOT NULL`)

Regeln:

- Der CDF ist für eine Transaktion oder einen Bereich, **in dem** eine nicht-additive Schemaänderung passiert, **nicht lesbar**.
- Damit nicht-additive Änderungen **vor oder nach** dem Batch-Bereich nicht stören, nutzen Abfragen das Schema der **Endversion des Bereichs** statt der neuesten Version. Überspannt der Bereich die Änderung, schlägt die Abfrage trotzdem fehl.
- **Lösung:** Abfrage in Bereiche **vor** und **nach** der Schemaänderung aufteilen.
- **Streaming:** Bis einschließlich **DBR 12.2 LTS** kann man nicht aus dem CDF einer Tabelle mit Column Mapping streamen, die umbenannt oder gelöscht hat.
- Die Column-Mapping-Doku warnt ausdrücklich: Das Einschalten kann **nachgelagerte CDF-Operationen** und Streaming-Reads brechen.

### Type Widening

Den CDF **über eine Typänderung hinweg** zu lesen wird nicht unterstützt. Stattdessen zwei Reads: einer endet an der Version mit der Typänderung, der andere beginnt dort. Beim Lesen über Delta Sharing zusätzlich `responseFormat = delta` → [04/02](04%20Delta%20Sharing/02%20CDF%20lesen%20%28Empfaenger%29.md).

### Automatic CDF

- **Externe Iceberg-Clients** können den automatischen CDF nicht abfragen (CDF ist nicht Teil der Iceberg-Spezifikation). Bei Delta Lake können ebenfalls **nur Databricks-Reader** den automatischen CDF lesen.
- **Multi-Statement-Transaktionen:** nicht unterstützt, wenn die Quelltabelle während der Transaktion geändert wurde.
- **Row Filters und Column Masks:** Tabellen damit werden von Automatic CDF **nicht** unterstützt.

### Legacy CDF

- Schaltet man Legacy CDF aus und später wieder ein, ist der **Zeitraum dazwischen nicht abfragbar**.
- **Iceberg Reads (UniForm):** Legacy CDF funktioniert für Delta-Clients weiter, hat aber **keine Unterstützung in Iceberg**.

### Sonstiges

| Situation | Einschränkung |
|---|---|
| **Smartsheet**-Connector | nutzt Column Mapping → CDF **nicht** unterstützt; auch keine Streaming-Reads |
| **Managed Iceberg Tables** im Delta Sharing | CDF nicht unterstützt |
| Managed Iceberg Tables als Quelle für **Synced Tables** | kein inkrementelles Processing mit Automatic CDF |
| **Materialized Views** | CDF nur per Beta-Feature mit Voraussetzungen; kein Time Travel |
| **Time Travel** auf CDF-Queries | nicht möglich (`DELTA_UNSUPPORTED_TIME_TRAVEL_VIEWS`: „Cannot time travel views, subqueries, streams or change data feed queries.“) |
| **Views** | `table_changes` auf einer View nur, wenn die zugrunde liegende Delta-Tabelle **Row Tracking** hat |
| Row-Tracking-Metadaten | Row IDs und Row Commit Versions sind im CDF nicht lesbar |

---

## Transaktionen

In (Multi-Statement-)Transaktionen gelten eigene Regeln:

| Unterfehler | Bedeutung |
|---|---|
| `CDF_READ` | `table_changes()` wird in Transaktionen **nicht** unterstützt |
| `CDF_READ_WITH_UNCOMMITTED_CHANGES` | CDF nicht lesbar, weil der Bereich **nicht committete** Änderungen enthält (nur bei `TRANSACTION_NOT_SUPPORTED`) |
| `WRITE_TABLE_WITH_CDF` | Schreiben in Tabellen **mit aktiviertem CDF** wird in (Multi-Statement-)Transaktionen nicht unterstützt |
| `COLUMN_MAPPING_MODE_CHANGE_IN_CDF` | Änderung des Column-Mapping-Modus auf CDF-Tabellen in Transaktionen nicht unterstützt |

Zusätzlich: `TRANSACTION_CDF_SCHEMA_WITH_RESERVED_COLUMN_NAME` (CDF kann in einer Transaktion nicht eingeschaltet werden, wenn die Tabelle einen reservierten Spaltennamen hat) und `TRANSACTION_CDF_SETTING_HIGH_WATERMARK_NOT_ALLOWED`.

---

## Fehlermeldungen nach Ursache

### Versionen und Bereiche

| Fehler | SQLSTATE | Bedeutung / Lösung |
|---|---|---|
| `DELTA_MISSING_CHANGE_DATA` | KD002 | Für eine Version im Bereich wurde kein CDF aufgezeichnet. Mit `DESCRIBE HISTORY` prüfen, **wann CDF eingeschaltet wurde** |
| `DELTA_CDC_START_VERSION_AFTER_LATEST` | 22003 | Startversion liegt hinter der neuesten Tabellenversion |
| `DELTA_CDC_READ_NULL_RANGE_BOUNDARY` | 22004 | Start/Ende darf nicht `NULL` sein |
| `DELTA_CHANGELOG_UNBOUNDED_RANGE` | 0AKDE | Delta CDC unterstützt im Batch keine unbegrenzten Bereiche; Start **und** Ende angeben |
| `DELTA_CHANGELOG_SCHEMA_CHANGE_IN_RANGE` | 0AKDE | Bereich überspannt eine Schemaänderung → Bereich mit einheitlichem Schema wählen |
| `timestampGreaterThanLatestCommit` | – | Zeitstempel nach dem letzten Commit → [Out-of-Range-Toleranz](02%20Lesen/01%20Batch%20-%20table_changes%20und%20readChangeFeed.md) |

### Retention

| Fehler | Bedeutung |
|---|---|
| `DELTA_CHANGE_DATA_FILE_NOT_FOUND` | eine im Log referenzierte Datei fehlt; bei CDF-Abfragen oft, weil die Change-Data-Datei außerhalb der Retention liegt und per `VACUUM` gelöscht wurde |

### Reservierte Spaltennamen

| Fehler | Bedeutung |
|---|---|
| `DELTA_TABLE_ALREADY_CONTAINS_CDC_COLUMNS` | CDF kann nicht eingeschaltet werden, weil die Tabelle reservierte Spalten enthält → umbenennen oder löschen |
| `DELTA_TABLE_CONTAINS_RESERVED_CDC_COLUMNS` (SQLSTATE 42939) | CDF kann nicht berechnet werden, weil reservierte Spaltennamen existieren |
| `RESERVED_CDC_COLUMNS_ON_WRITE` | der Schreibvorgang enthält reservierte CDF-Spalten → umbenennen/löschen oder CDF ausschalten |
| `DELTA_CONCURRENT_APPEND` / `DELTA_CONCURRENT_DELETE_READ` / `DELTA_CONCURRENT_DELETE_DELETE` | Spalte `_change_type` kollidiert mit CDF-Metadaten und verhindert die Konflikterkennung auf Zeilenebene → Spalte umbenennen (bzw. CDC ausschalten) |

### Row Tracking und Automatic CDF

| Fehler | Bedeutung |
|---|---|
| `DELTA_CHANGELOG_REQUIRES_ROW_TRACKING` | CDC über `CHANGES` braucht Row Tracking: `TBLPROPERTIES ('delta.enableRowTracking' = 'true')` |
| `DELTA_CHANGELOG_ROW_TRACKING_DISABLED_IN_RANGE` | Row Tracking wurde im Bereich ausgeschaltet → Bereich mit aktivem Row Tracking wählen |
| `DELTA_CHANGELOG_REQUIRES_V2_TABLE` | Auto-CDF-Reads brauchen den **V2-Delta-Connector** |
| `DELTA_READ_TIME_CDC_NOT_SUPPORTED_FOR_TABLES_WITH_ACCESS_POLICIES` | Read-Time-CDF unterstützt keine Tabellen mit Zugriffsrichtlinien → laut Meldung die angegebene Tabelleneigenschaft für „Read-optimized CDF“ auf `true` setzen |
| `DELTA_TABLE_CHANGES_VIEW_REQUIRES_ROW_TRACKING` | `table_changes` auf einer View braucht Row Tracking auf der Basistabelle |
| `DELTA_TABLE_CHANGES_VIEW_UNSUPPORTED` | `table_changes` auf dieser View nicht unterstützt |

### Column Mapping und Konfiguration

| Fehler | Bedeutung |
|---|---|
| `DELTA_BLOCK_COLUMN_MAPPING_AND_CDC_OPERATION` | Operation nicht erlaubt, wenn die Tabelle CDF hat **und** per `DROP COLUMN` oder `RENAME COLUMN` geändert wurde |
| `DELTA_CDC_NOT_ALLOWED_IN_THIS_VERSION` | `delta.enableChangeDataFeed` kann in dieser Version nicht gesetzt werden |
| `DELTA_CHANGE_TABLE_FEED_DISABLED` | Schreiben in eine Tabelle mit gesetztem `delta.enableChangeDataFeed` nicht möglich, weil CDF nicht verfügbar ist |
| `CONFIG_NOT_AVAILABLE` | auf Serverless CDF nicht per Session-Konfiguration schalten, sondern per **Tabelleneigenschaft** oder Write-Option |

Fehler zu **Delta Sharing** (`DS_CDF_*`) → [04/02](04%20Delta%20Sharing/02%20CDF%20lesen%20%28Empfaenger%29.md) · Fehler zu **Datei-Change-Feeds** (`CF_*`) → [03/04](03%20Pipelines%20und%20Muster/04%20Change%20Feeds%20bei%20Datei-Ingestion.md)

---
[← Vorherige Datei](06%20Weitere%20Einsatzgebiete.md) · [Übersicht](00%20Uebersicht.md)
