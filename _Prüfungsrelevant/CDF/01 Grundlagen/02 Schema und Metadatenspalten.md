[← Übersicht](../00%20Uebersicht.md)

# CDF-Schema und Metadatenspalten

> Quellen: [Use change data feed on Databricks](https://docs.databricks.com/aws/en/tables/features/change-data-feed) · [table_changes](https://docs.databricks.com/aws/en/sql/language-manual/functions/table_changes) · [Databricks Runtime 15.4 LTS](https://docs.databricks.com/aws/en/release-notes/runtime/15.4lts) · [Row tracking](https://docs.databricks.com/aws/en/tables/features/row-tracking) · [Maintenance updates](https://docs.databricks.com/aws/en/release-notes/runtime/maintenance-updates)

## Welches Schema hat der Feed?

Beim Lesen des CDF verwendet die Abfrage das Schema der **neuesten Tabellenversion**. Die meisten Schemaänderungen werden unterstützt; bei Tabellen mit **Column Mapping** gibt es Einschränkungen (→ [07 Einschränkungen](../07%20Einschraenkungen%20und%20Fehlermeldungen.md)).

Zusätzlich zu den Datenspalten der Tabelle enthält der Feed **drei Metadatenspalten**:

| Spalte | Typ | Inhalt |
|---|---|---|
| `_change_type` | `STRING` | `insert`, `update_preimage`, `update_postimage`, `delete` |
| `_commit_version` | `LONG` (`BIGINT`) | Version des Delta-Logs bzw. der Tabelle, die die Änderung enthält |
| `_commit_timestamp` | `TIMESTAMP` | Zeitpunkt, zu dem der Commit erstellt wurde |

In der SQL-Referenz von `table_changes` sind alle drei Spalten `NOT NULL`.

### Die vier Änderungstypen

| `_change_type` | Bedeutung | Zeilen pro Änderung |
|---|---|---|
| `insert` | neue Zeile | 1 |
| `update_preimage` | Wert **vor** dem Update | 2 pro Update |
| `update_postimage` | Wert **nach** dem Update | (Pre + Post) |
| `delete` | gelöschte Zeile | 1 |

> **Merksatz:** Ein `UPDATE` erzeugt **zwei** Zeilen im Feed. Wer nur den neuen Stand braucht, filtert `update_preimage` heraus.

---

## Beispiel aus der SQL-Referenz

```sql
-- Create a Delta table with Change Data Feed;
> CREATE TABLE myschema.t(c1 INT, c2 STRING) TBLPROPERTIES(delta.enableChangeDataFeed=true);

-- Modify the table
> INSERT INTO myschema.t VALUES (1, 'Hello'), (2, 'World');
> INSERT INTO myschema.t VALUES (3, '!');
> UPDATE myschema.t SET c2 = upper(c2) WHERE c1 < 3;
> DELETE FROM myschema.t WHERE c1 = 3;

-- Show the history of table change events
> DESCRIBE HISTORY myschema.t;
 version timestamp                    userId           userName      operation    operationParameters                                            ...
       4 2022-09-01T18:32:35.000+0000 6167625779053302 alf@melmak.et DELETE       {"predicate":"[\"(spark_catalog.myschema.t.c1 = 3)\"]"}
       3 2022-09-01T18:32:32.000+0000 6167625779053302 alf@melmak.et UPDATE       {"predicate":"(c1#3195878 < 3)"}
       2 2022-09-01T18:32:28.000+0000 6167625779053302 alf@melmak.et WRITE        {"mode":"Append","partitionBy":"[]"}
       1 2022-09-01T18:32:26.000+0000 6167625779053302 alf@melmak.et WRITE        {"mode":"Append","partitionBy":"[]"}
       0 2022-09-01T18:32:23.000+0000 6167625779053302 alf@melmak.et CREATE TABLE {"isManaged":"true","description":null,"partitionBy":"[]","properties":"{\"delta.enableChangeDataFeed\":\"true\"}"}

-- Show the change table feed using a the commit timestamp retrieved from the history.
> SELECT * FROM table_changes('`myschema`.`t`', 2);
 c1 c2     _change_type    _commit_version _commit_timestamp
  3 !      insert                        2 2022-09-01T18:32:28.000+0000
  2 WORLD  update_postimage              3 2022-09-01T18:32:32.000+0000
  2 World  update_preimage               3 2022-09-01T18:32:32.000+0000
  1 Hello  update_preimage               3 2022-09-01T18:32:32.000+0000
  1 HELLO  update_postimage              3 2022-09-01T18:32:32.000+0000
  3 !      delete                        4 2022-09-01T18:32:35.000+0000

-- Show the ame change table feed using a point in time.
> SELECT * FROM table_changes('`myschema`.`t`', '2022-09-01T18:32:27.000+0000') ORDER BY _commit_version;
 c1 c2     _change_type    _commit_version _commit_timestamp
  3 !      insert                        2 2022-09-01T18:32:28.000+0000
  2 WORLD  update_postimage              3 2022-09-01T18:32:32.000+0000
  2 World  update_preimage               3 2022-09-01T18:32:32.000+0000
  1 Hello  update_preimage               3 2022-09-01T18:32:32.000+0000
  1 HELLO  update_postimage              3 2022-09-01T18:32:32.000+0000
  3 !      delete                        4 2022-09-01T18:32:35.000+0000
```

**Was man daran sieht:**

- Version 2 (zweites `INSERT`) → eine `insert`-Zeile.
- Version 3 (`UPDATE` auf 2 Zeilen) → **vier** Zeilen: je ein Pre- und Postimage.
- Version 4 (`DELETE`) → eine `delete`-Zeile.
- Die Abfrage ab Version 2 zeigt die Inserts aus Version 1 **nicht**.

---

## Reservierte Spaltennamen

Enthält das Tabellenschema bereits Spalten mit den Namen `_change_type`, `_commit_version` oder `_commit_timestamp`, **kann CDF auf der Tabelle nicht verwendet werden**. Diese Spalten müssen vor dem Einschalten umbenannt werden.

Zugehörige Fehlermeldungen (siehe [07](../07%20Einschraenkungen%20und%20Fehlermeldungen.md)): `DELTA_TABLE_ALREADY_CONTAINS_CDC_COLUMNS`, `DELTA_TABLE_CONTAINS_RESERVED_CDC_COLUMNS`, `RESERVED_CDC_COLUMNS_ON_WRITE`. Auch Konflikterkennung auf Zeilenebene bei parallelen Schreibvorgängen (`DELTA_CONCURRENT_APPEND`, `DELTA_CONCURRENT_DELETE_READ`, `DELTA_CONCURRENT_DELETE_DELETE`) scheitert, wenn eine Spalte `_change_type` heißt.

> Historischer Fix (DBR 9.1 LTS Maintenance Update): Hatte eine Tabelle eine eigene Spalte `_change_type` bei **ausgeschaltetem** CDF, wurde diese bei `MERGE` fälschlich mit `NULL` gefüllt.

---

## Zeitzone von `_commit_timestamp` (ab DBR 15.4 LTS)

Ab **Databricks Runtime 15.4 LTS** liefert `_commit_timestamp` die Commit-Zeit in der **Zeitzone der Spark-Session**. In älteren Runtimes gaben `update_preimage`, `update_postimage` und `delete` den Wert in **UTC** zurück, wenn die Session-Zeitzone nicht UTC war.

> Beim Upgrade von einer Runtime unter 15.4 LTS: nachgelagerte Vergleiche, Filter oder Schreibvorgänge prüfen, die `_commit_timestamp` verwenden.

---

## Row-Tracking-Spalten sind im Feed nicht lesbar

Die Row-Tracking-Metadatenfelder (**Row IDs** und **Row Commit Versions**) sind beim Lesen des Change Data Feed **nicht zugänglich**.

---
[← Vorherige Datei](01%20Was%20ist%20CDF%20-%20Automatic%20vs.%20Legacy.md) · [Übersicht](../00%20Uebersicht.md) · [Nächste Datei →](03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md)
