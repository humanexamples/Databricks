# `DataStreamReader.changes()`

Gibt Zeilen-Änderungen (Change Data Capture) einer Tabelle als Streaming-DataFrame zurück.

## Signatur

```python
changes(tableName)
```

## Beschreibung

*"Returns the row-level changes (Change Data Capture) from the specified table as a streaming DataFrame."*

Funktioniert mit Data-Source-V2-Tabellen, deren Katalog `TableCatalog.loadChangelog()` implementiert. Über `option()` lassen sich Startversion bzw. -zeitstempel sowie Verarbeitungsoptionen konfigurieren (`startingVersion`, `startingTimestamp`).

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `tableName` | `str` | Name der Tabelle, aus der gelesen wird. |

## Rückgabewert

`DataFrame`

## Beispiel

```python
spark.readStream.option("startingVersion", "10").changes("my_table")
```

## Quellen

- DataStreamReader.changes: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/changes

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
