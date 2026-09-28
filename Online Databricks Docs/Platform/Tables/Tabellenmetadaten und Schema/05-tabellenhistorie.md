# Tabellenhistorie

Bei Apache-Iceberg- und Delta-Lake-Tabellen erzeugt jede Operation, die eine Tabelle ändert, eine neue Tabellenversion. Das ermöglicht Auditing, Rollbacks und Time-Travel-Abfragen.

Databricks empfiehlt nicht, die Tabellenhistorie als langfristige Backup-Lösung für die Datenarchivierung zu verwenden.

## Tabellenhistorie abrufen

Der Befehl `DESCRIBE HISTORY` liefert Details zu den Operationen. Die Aufbewahrungsdauer der Historie wird über die Tabelleneigenschaft `logRetentionDuration` gesteuert. Sie beträgt standardmäßig 30 Tage.

```sql
%sql
DESCRIBE HISTORY table_name
```

```sql
%sql
DESCRIBE HISTORY table_name LIMIT 1
```

## Spalten des Historie-Schemas

| Spalte | Beschreibung |
|---|---|
| `version` | Tabellenversion, die durch die Operation erzeugt wurde |
| `timestamp` | Zeitpunkt, zu dem die Version committet wurde |
| `userId` / `userName` | Identifikation des Nutzers |
| `operation` | Name der Operation |
| `operationParameters` | Details der Operation, zum Beispiel Prädikate |
| `isBlindAppend` | Ob die Operation nur angehängt hat |
| `operationMetrics` | Statistiken zur Operation, etwa geänderte Zeilen oder Dateien |

## Operationsmetriken nach Typ

Je nach Operation werden unterschiedliche Metriken erfasst.

- **WRITE / CREATE / REPLACE / COPY:** `numFiles`, `numOutputBytes`, `numOutputRows`
- **DELETE:** `numAddedFiles`, `numRemovedFiles`, `numDeletedRows`, `numCopiedRows`, Zeitmetriken
- **MERGE:** Zeilenanzahl von Quelle und Ziel, Dateimetriken, Zeitmetriken
- **OPTIMIZE:** Dateianzahl, Byte-Metriken, Perzentile der Dateigröße

## OPTIMIZE-Operationen klassifizieren

Um den Optimierungstyp zu bestimmen, wird das Feld `operationParameters` geprüft.

- **Auto Compaction:** `auto = 'true'`
- **Liquid Clustering:** `clusterBy` ist gesetzt
- **Z-Ordering:** `zOrderBy` ist gesetzt

Diese Abfrage klassifiziert alle OPTIMIZE-Operationen einer Tabelle:

```sql
%sql
SELECT version, timestamp,
  CASE
    WHEN operationParameters.clusterBy IS NOT NULL AND operationParameters.clusterBy <> '[]' THEN 'Liquid clustering'
    WHEN operationParameters.zOrderBy IS NOT NULL AND operationParameters.zOrderBy <> '[]' THEN 'Z-ordering'
    WHEN operationParameters.auto = 'true' THEN 'Auto compaction'
    ELSE 'Manual OPTIMIZE'
  END AS optimize_type
FROM (DESCRIBE HISTORY table_name)
WHERE operation = 'OPTIMIZE'
```

## Time Travel

Historische Tabellenversionen lassen sich über Zeitstempel oder Versionsnummer abfragen.

SQL:

```sql
%sql
SELECT * FROM people10m TIMESTAMP AS OF '2018-10-18T22:15:12.013Z';
SELECT * FROM people10m VERSION AS OF 123;
```

Python:

```python
df1 = spark.read.option("timestampAsOf", "2019-01-01").table("people10m")
df2 = spark.read.option("versionAsOf", 123).table("people10m")
```

Alternative @-Syntax:

```sql
%sql
SELECT * FROM people10m@20190101000000000
SELECT * FROM people10m@v123
```

Ab Databricks Runtime 18.0 werden Time-Travel-Abfragen blockiert, wenn sie eine Version anfragen, die älter ist als die Tabelleneigenschaft `deletedFileRetentionDuration` (Standard: 7 Tage).

## Aufbewahrungsdauer konfigurieren

Für erweiterten Time Travel lassen sich diese Tabelleneigenschaften anpassen:

- `delta.logRetentionDuration = "interval <interval>"` (Standard: 30 Tage)
- `delta.deletedFileRetentionDuration = "interval <interval>"` (Standard: 7 Tage)

Eine höhere Aufbewahrungsschwelle kann die Speicherkosten erhöhen.

## Tabelle wiederherstellen (RESTORE)

```sql
%sql
RESTORE TABLE target_table TO VERSION AS OF <version>;
RESTORE TABLE target_table TO TIMESTAMP AS OF <timestamp>;
```

Voraussetzungen: Die Berechtigung `MODIFY` ist nötig. Zeitstempel-Formate sind `yyyy-MM-dd HH:mm:ss` oder `yyyy-MM-dd`.

`RESTORE` markiert Dateien mit `dataChange = true`. Nachgelagerte Streaming-Jobs verarbeiten wiederhergestellte Datensätze dadurch als neue Daten. Das kann zu doppelten Datensätzen führen.

## Letzte Commit-Version

Die zuletzt committete Version der aktuellen Sitzung lässt sich so abrufen.

```sql
%sql
SET spark.databricks.delta.lastCommitVersionInSession
```

```python
spark.conf.get("spark.databricks.delta.lastCommitVersionInSession")
```

---
**Quelle:** https://docs.databricks.com/aws/en/tables/history  
**Stand:** 2026-08-06
