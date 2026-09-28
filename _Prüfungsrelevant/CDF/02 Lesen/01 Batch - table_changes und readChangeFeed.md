[← Übersicht](../00%20Uebersicht.md)

# CDF im Batch lesen: `table_changes()` und `readChangeFeed`

> Quellen: [Use change data feed on Databricks – Read changes in batch queries](https://docs.databricks.com/aws/en/tables/features/change-data-feed) · [table_changes table-valued function](https://docs.databricks.com/aws/en/sql/language-manual/functions/table_changes)

## Regeln für Batch-Reads

- Für Batch-Reads ist eine **Startversion Pflicht**. Eine Endversion ist optional.
- **Versionen** als Integer, **Zeitstempel** als String im Format `yyyy-MM-dd[ HH:mm:ss[.SSS]]`.
- Start und Ende sind **inklusive**.
- Nur Startversion angeben = von dort bis zur **neuesten** Version lesen.
- Eine Version **vor** Aktivierung des CDF → **Fehler**.

---

## SQL: `table_changes()`

### Syntax

```text
table_changes ( table_str, start [, end ] )
```

- `table_str`: Tabellenname als String. Ohne Qualifizierung wird `current_schema` verwendet. Enthält der Name Leerzeichen oder Punkte, die betroffenen Teile **innerhalb des Strings** mit Backticks quoten.
- `start` / `end`: Version (Integer) oder Zeitstempel (String).
- Rückgabe: alle Spalten der Tabelle **plus** `_change_type`, `_commit_version`, `_commit_timestamp` → [Schema](../01%20Grundlagen/02%20Schema%20und%20Metadatenspalten.md).

**Berechtigung (mindestens eine davon):** `SELECT`-Privileg auf der Tabelle · Owner der Tabelle · administrative Rechte.

### Beispiele

Version 0 bis 10:

```sql
SELECT * FROM table_changes('tableName', 0, 10)
```

Zwischen zwei Zeitstempeln (in der Doku auskommentiert):

```sql
--SELECT * FROM table_changes('tableName', '2021-04-21 05:45:46', '2021-05-21 12:00:00')
```

Ab Startversion bis zur neuesten:

```sql
SELECT * FROM table_changes('tableName', 0)
```

Tabellenname mit Sonderzeichen:

```sql
SELECT * FROM table_changes('`schema`.`dotted.tableName`', '2021-04-21 06:45:46', '2021-05-21 12:00:00')
```

---

## Python: `readChangeFeed`

Version 0 bis 10:

```python
spark.read \
  .option("readChangeFeed", "true") \
  .option("startingVersion", 0) \
  .option("endingVersion", 10) \
  .table("myDeltaTable")
```

Zwischen zwei Zeitstempeln:

```python
spark.read \
  .option("readChangeFeed", "true") \
  .option("startingTimestamp", '2021-04-21 05:45:46') \
  .option("endingTimestamp", '2021-05-21 12:00:00') \
  .table("myDeltaTable")
```

Ab Startversion bis zur neuesten:

```python
spark.read \
  .option("readChangeFeed", "true") \
  .option("startingVersion", 0) \
  .table("myDeltaTable")
```

## Scala

```scala
spark.read
  .option("readChangeFeed", "true")
  .option("startingVersion", 0)
  .option("endingVersion", 10)
  .table("myDeltaTable")
```

```scala
spark.read
  .option("readChangeFeed", "true")
  .option("startingTimestamp", "2021-04-21 05:45:46")
  .option("endingTimestamp", "2021-05-21 12:00:00")
  .table("myDeltaTable")
```

```scala
spark.read
  .option("readChangeFeed", "true")
  .option("startingVersion", 0)
  .table("myDeltaTable")
```

> Die ältere Schreibweise `readChangeData` ist ein Alias für `readChangeFeed` (siehe Optionsreferenz in [02 Streaming](02%20Streaming%20-%20readStream%20und%20Optionen.md)). Das Demo-Notebook in [03/01](../03%20Pipelines%20und%20Muster/01%20Demo%20-%20Silver%20nach%20Gold%20propagieren.md) verwendet sie noch.

---

## Versionen außerhalb des gültigen Bereichs

Standardmäßig liefert eine Version oder ein Zeitstempel **hinter dem letzten Commit** den Fehler `timestampGreaterThanLatestCommit`.

Ab **Databricks Runtime 11.3 LTS** lässt sich das tolerieren:

```sql
SET spark.databricks.delta.changeDataFeed.timestampOutOfRange.enabled = true;
```

Dann gilt:

| Angabe | Ergebnis |
|---|---|
| Start **nach** dem letzten Commit | leeres Ergebnis |
| Ende **nach** dem letzten Commit | alle Änderungen vom Start bis zum letzten Commit |

Zugehörige Fehler: `DELTA_CDC_START_VERSION_AFTER_LATEST`, `DELTA_CDC_READ_NULL_RANGE_BOUNDARY` (Start/Ende darf nicht `NULL` sein), `DELTA_MISSING_CHANGE_DATA` (für die Version wurde kein CDF aufgezeichnet) → [07](../07%20Einschraenkungen%20und%20Fehlermeldungen.md).

---

## Praxis-Tipp: nur den neuesten Stand pro Key

Batch-Reads liefern **alle** Zwischenstände. Für ein `MERGE` ins Ziel braucht man meist nur die letzte Änderung pro Schlüssel, ohne `update_preimage`. Genau so macht es das offizielle Demo-Notebook:

```sql
-- Collect only the latest version for each country
CREATE OR REPLACE TEMPORARY VIEW silverTable_latest_version as
SELECT *
    FROM
         (SELECT *, rank() over (partition by Country order by _commit_version desc) as rank
          FROM table_changes('silverTable', 2, 5)
          WHERE _change_type !='update_preimage')
    WHERE rank=1
```

Vollständiges Beispiel: [03/01 Demo – Silver nach Gold propagieren](../03%20Pipelines%20und%20Muster/01%20Demo%20-%20Silver%20nach%20Gold%20propagieren.md)

---
[← Übersicht](../00%20Uebersicht.md) · [Nächste Datei →](02%20Streaming%20-%20readStream%20und%20Optionen.md)
