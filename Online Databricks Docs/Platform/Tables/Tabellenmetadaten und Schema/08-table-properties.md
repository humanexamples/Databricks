# Table Properties Referenz

Delta-Lake- und Apache-Iceberg-Tabellen nutzen Tabelleneigenschaften, um Verhalten zu konfigurieren. Dazu gehören Datenlayout, Dateigröße, Data Skipping, Isolation Level und Change Data Feed.

Alle Operationen, die Tabelleneigenschaften setzen oder ändern, stehen im Konflikt mit anderen gleichzeitigen Schreibvorgängen. Diese schlagen dann fehl.

## Tabelleneigenschaften ändern

Um bestehende Tabelleneigenschaften zu ändern, wird der SQL-Befehl `SET TBLPROPERTIES` verwendet.

### Präfix-Anforderungen

Delta-Lake-Tabellen benötigen das Präfix `delta.`. Iceberg-Tabellen benötigen das Präfix `iceberg.`.

```sql
%sql
-- Delta Lake
ALTER TABLE <table-name> SET TBLPROPERTIES ('delta.enableDeletionVectors' = true);

-- Iceberg table
ALTER TABLE <table-name> SET TBLPROPERTIES ('iceberg.enableDeletionVectors' = true);
```

### SparkSession-Eigenschaften versus Tabelleneigenschaften

Manche SparkSession-Konfigurationen überschreiben Tabelleneigenschaften. Databricks empfiehlt, für die meisten Workloads tabellenbezogene Konfigurationen zu verwenden.

Zuordnung:

- `delta.<conf>` → `spark.databricks.delta.properties.defaults.<conf>`
- `iceberg.<conf>` → `spark.databricks.iceberg.properties.defaults.<conf>`

```sql
%sql
-- Delta Lake
SET spark.databricks.delta.properties.defaults.appendOnly = true

-- Iceberg table
SET spark.databricks.iceberg.properties.defaults.appendOnly = true
```

## Vollständige Referenz der Tabelleneigenschaften

| Eigenschaft | Beschreibung | Datentyp | Standard |
|---|---|---|---|
| `autoOptimize.optimizeWrite` | Optimiert automatisch das Layout der Dateien dieser Tabelle beim Schreiben. | Boolean | (keiner) |
| `dataSkippingNumIndexedCols` | Anzahl der Spalten, für die Statistiken für Data Skipping gesammelt werden. Ein Wert von -1 bedeutet: Statistiken für alle Spalten sammeln. | Int | 32 |
| `dataSkippingStatsColumns` | Kommagetrennte Liste von Spaltennamen, für die Statistiken gesammelt werden, um Data Skipping zu verbessern. Hat Vorrang vor `dataSkippingNumIndexedCols`. | String | (keiner) |
| `deletedFileRetentionDuration` | Kürzeste Dauer, für die logisch gelöschte Datendateien vor der physischen Löschung aufbewahrt werden. Databricks empfiehlt mindestens 7 Tage. Ist die Aufbewahrungsdauer zu kurz, können bei lange laufenden Jobs unfertig committete Dateien gelöscht werden. | CalendarInterval | interval 1 week |
| `enableDeletionVectors` | Aktiviert Deletion Vectors und Predictive I/O für Updates. | Boolean | Abhängig von Workspace-Admin-Einstellungen und Runtime-Version |
| `logRetentionDuration` | Wie lange die Historie einer Tabelle aufbewahrt wird. VACUUM-Operationen überschreiben diese Schwelle. Ein großer Wert vergrößert die Historie, beeinflusst die Performance aber nicht, da Operationen auf dem Log konstante Zeit benötigen. | CalendarInterval | interval 30 days |
| `minReaderVersion` (nur Delta Lake) | Mindestens erforderliche Protokoll-Reader-Version zum Lesen dieser Tabelle. Databricks rät von manueller Konfiguration ab. | Int | 1 |
| `minWriterVersion` (nur Delta Lake) | Mindestens erforderliche Protokoll-Writer-Version zum Schreiben dieser Tabelle. Databricks rät von manueller Konfiguration ab. | Int | 2 |
| `format-version` (nur Iceberg managed Tabellen) | Die Iceberg-Tabellenformat-Version. Databricks rät von manueller Konfiguration ab. | Int | 2 |
| `randomizeFilePrefixes` | Erzeugt ein zufälliges Präfix für einen Dateipfad statt Partitionsinformationen zu verwenden. | Boolean | false |
| `targetFileSize` | Zielgröße einer Datei in Bytes oder größeren Einheiten, zum Beispiel 104857600 (Bytes) oder 100mb. | String | (keiner) |
| `parquet.compression.codec` | Kompressions-Codec einer Tabelle. Gültige Werte: ZSTD, SNAPPY, GZIP, LZ4, BROTLI. Verfügbar ab Runtime 16.0. Bestehende Dateien werden nicht automatisch neu geschrieben. Zum Neukomprimieren bestehender Daten: `OPTIMIZE table_name FULL`. | String | ZSTD |
| `parquet.format.version` (nur Delta Lake) | Der Wert 2.12.0 aktiviert fortgeschrittene Encodings, v2-Data-Page-Header und INT64-Zeitstempel. Das kann Abfrageleistung verbessern und Speicherbedarf senken. Gültige Werte: 1.0.0 und 2.12.0. Manche OSS-Iceberg-Reader unterstützen Parquet-v2-Encodings eventuell nicht. | String | 1.0.0 |
| `appendOnly` | Macht die Tabelle Append-Only. Append-Only-Tabellen erlauben kein Löschen bestehender Datensätze und kein Ändern bestehender Werte. | Boolean | false |
| `autoOptimize.autoCompact` | Fasst automatisch kleine Dateien innerhalb von Tabellenpartitionen zusammen, um das Problem vieler kleiner Dateien zu reduzieren. Werte: auto (empfohlen), true, legacy oder false. | String | (keiner) |
| `checkpoint.writeStatsAsJson` | Schreibt Dateistatistiken in Checkpoints im JSON-Format für die Spalte stats. | Boolean | false |
| `checkpoint.writeStatsAsStruct` | Schreibt Dateistatistiken in Checkpoints als Struct für die Spalte stats_parsed sowie Partitionswerte als Struct für partitionValues_parsed. | Boolean | true |
| `checkpointPolicy` | classic für klassische Checkpoints, v2 für v2-Checkpoints. | String | classic |
| `columnMapping.mode` | Aktiviert Column Mapping, damit Tabellenspalten und zugehörige Parquet-Spalten unterschiedliche Namen haben können. Gültige Werte: none, name und id. Das Aktivieren von columnMapping.mode aktiviert automatisch randomizeFilePrefixes. | DeltaColumnMappingMode | none |
| `compatibility.symlinkFormatManifest.enabled` (nur Delta Lake) | Konfiguriert die Delta-Lake-Tabelle so, dass alle Schreiboperationen die Manifeste automatisch aktualisieren. | Boolean | false |
| `enableChangeDataFeed` | Aktiviert den Change Data Feed. | Boolean | false |
| `enableTypeWidening` | Aktiviert Type Widening. | Boolean | false |
| `isolationLevel` | Grad, in dem eine Transaktion von Änderungen gleichzeitiger Transaktionen isoliert sein muss. Gültige Werte: Serializable und WriteSerializable. | String | WriteSerializable |
| `randomPrefixLength` | Anzahl der Zeichen für zufällige Präfixe, wenn randomizeFilePrefixes aktiv ist. | Int | 2 |
| `setTransactionRetentionDuration` | Kürzeste Dauer, innerhalb derer neue Snapshots Transaktions-IDs behalten. Neue Snapshots verwerfen und ignorieren Transaktions-IDs, die älter als diese Dauer sind. Wird genutzt, um Schreibvorgänge idempotent zu machen. | CalendarInterval | (keiner) |

## Wichtige Hinweise und Empfehlungen

- Gleichzeitige Schreibvorgänge schlagen fehl, wenn Tabelleneigenschaften geändert werden.
- Von einer manuellen Konfiguration der Protokollversionen (`minReaderVersion`, `minWriterVersion`) wird abgeraten.
- Lange Aufbewahrungsdauern vergrößern das Log, beeinflussen die Performance aber nicht.
- Bestehende Parquet-Dateien benötigen den Befehl `OPTIMIZE`, um mit einem neuen Codec neu komprimiert zu werden.
- Manche OSS-Iceberg-Reader haben Einschränkungen bei Parquet-v2-Encodings.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/table-properties  
**Stand:** 2026-08-06
