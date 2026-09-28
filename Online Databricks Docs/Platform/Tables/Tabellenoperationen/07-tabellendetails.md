# Tabellendetails mit DESCRIBE DETAIL prüfen

Mit `DESCRIBE DETAIL` rufen Sie detaillierte Metadaten zu einer Delta-Lake- oder Apache-Iceberg-Tabelle ab. Dazu zählen Dateianzahl, Datengröße, Partitionsspalten und aktivierte Tabellenfunktionen.

## Beispiele

Details über einen Pfad abfragen:

```sql
%sql
DESCRIBE DETAIL '/data/events/'
```

Details über einen Tabellennamen abfragen:

```sql
%sql
DESCRIBE DETAIL eventsTable
```

## Schema der Ausgabe

Die Ausgabe von `DESCRIBE DETAIL` besteht aus genau einer Zeile mit folgendem Schema:

| Spalte | Typ | Beschreibung |
| --- | --- | --- |
| `format` | string | Format der Tabelle (zum Beispiel `delta` oder `iceberg`) |
| `id` | string | Eindeutige ID der Tabelle |
| `name` | string | Name der Tabelle, wie im Metastore definiert |
| `description` | string | Beschreibung der Tabelle |
| `location` | string | Speicherort der Tabelle |
| `createdAt` | timestamp | Zeitpunkt der Erstellung |
| `lastModified` | timestamp | Zeitpunkt der letzten Änderung |
| `partitionColumns` | Array aus Strings | Namen der Partitionsspalten, falls die Tabelle partitioniert ist |
| `numFiles` | long | Anzahl der Dateien in der aktuellsten Version der Tabelle |
| `sizeInBytes` | int | Größe des aktuellsten Snapshots in Bytes |
| `properties` | String-String-Map | Alle gesetzten Eigenschaften dieser Tabelle |
| `minReaderVersion` | int | Minimale Reader-Version (laut Log-Protokoll), die die Tabelle lesen kann |
| `minWriterVersion` | int | Minimale Writer-Version (laut Log-Protokoll), die in die Tabelle schreiben kann |
| `statistics` | Map mit String-Keys | Zusätzliche Statistiken auf Tabellenebene |
| `tableFeatures` | Array aus Strings | Liste der von der Tabelle unterstützten Tabellenfunktionen |
| `clusteringColumns` | Array aus Strings | Die für Liquid Clustering verwendeten Spalten |

## Beispielausgabe

```
+------+--------------------+------------------+-----------+--------------------+---------------------+-------------------+----------------+--------+-----------+----------+----------------+----------------+
|format|                  id|              name|description|             location|            createdAt|       lastModified|partitionColumns|numFiles|sizeInBytes|properties|minReaderVersion|minWriterVersion|
+------+--------------------+------------------+-----------+--------------------+---------------------+-------------------+----------------+--------+-----------+----------+----------------+----------------+
| delta|d31f82d2-a69f-42e...|default.deltatable|       null|file:/Users/tuor/...|2020-06-05 12:20:...|2020-06-05 12:20:20|              []|      10|      12345|        []|               1|               2|
+------+--------------------+------------------+-----------+--------------------+---------------------+-------------------+----------------+--------+-----------+----------+----------------+----------------+
```

---
**Quelle:** https://docs.databricks.com/aws/en/tables/operations/table-details  
**Stand:** 2026-08-06
