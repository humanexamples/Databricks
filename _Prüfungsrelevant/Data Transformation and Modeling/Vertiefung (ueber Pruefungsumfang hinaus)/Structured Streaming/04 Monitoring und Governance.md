# Structured Streaming: Monitoring und Governance

## 1. Überblick

- Eingebautes Monitoring über die Spark-UI (Tab **Streaming**).
- Jedem Stream über `.queryName(<query-name>)` im `writeStream`-Code einen eindeutigen Namen geben, um Streams in der UI zu unterscheiden.

## 2. Metriken an externe Dienste senden: `StreamingQueryListener`

- Streaming Query Listener Interface von Apache Spark → Metriken an externe Dienste senden (Alerting, Dashboarding).
- `StreamingQueryListener` in Python und Scala ab DBR 11.3 LTS.

**Einschränkungen bei Unity-Catalog-fähigen Compute-Zugriffsmodi:**
- Credentials/UC-verwaltete Objekte auf **dediziertem** Zugriffsmodus → DBR 15.1+ nötig.
- Scala-Workloads mit **Standard**-Zugriffsmodus (früher Shared) → DBR 16.1+ nötig.

**Gotchas:**
- Verarbeitungslogik in Listenern begrenzt halten — Latenz dort kann die Query-Geschwindigkeit erheblich beeinträchtigen; stattdessen in schnell antwortende Systeme wie Kafka schreiben.
- `onQueryIdle` wird zugestellt, wenn an der Quelle keine Daten verfügbar sind; `onQueryProgress` nur am Ende eines Batches.
- Bei sehr lange laufender Batch-Verarbeitung können beide Nachrichten ausbleiben, ohne dass die Query ungesund ist.

```python
class MyListener(StreamingQueryListener):
    def onQueryStarted(self, event):
        # Synchron mit DataStreamWriter.start() aufgerufen — hier nicht blockieren.
        pass
    def onQueryProgress(self, event):
        # Asynchron; enthält den neuesten Fortschritt der Query.
        pass
    def onQueryIdle(self, event):
        # Wird aufgerufen, wenn die Query auf neue Daten wartet.
        pass
    def onQueryTerminated(self, event):
        # Wird beim Stoppen der Query aufgerufen (mit oder ohne Fehler).
        pass

my_listener = MyListener()
spark.streams.addListener(my_listener)
```

- Scala analog: `StreamingQueryListener`-Subklasse mit `onQueryStarted(event: QueryStartedEvent)`, `onQueryProgress(event: QueryProgressEvent)`, `onQueryIdle(event: QueryProgressEvent)`, `onQueryTerminated(event: QueryTerminatedEvent)`.

## 3. Observable Metrics

- Benannte, beliebige Aggregatfunktionen auf einem DataFrame/einer Query via `df.observe(name, aggExpr, ...)`.
- Bei jedem Abschlusspunkt (Batch-Ende bzw. Streaming-Epoche) wird ein benanntes Event mit den Metriken seit dem letzten Abschlusspunkt emittiert — beobachtet über einen an die Spark-Session angehängten Listener.
- **Batch-Modus:** `QueryExecutionListener` — bei Query-Abschluss aufgerufen; Zugriff über `QueryExecution.observedMetrics`.
- **Streaming/Micro-Batch:** `StreamingQueryListener` — bei Abschluss jeder Epoche aufgerufen; Zugriff über `StreamingQueryProgress.observedMetrics`. `continuous`-Trigger-Modus wird für Streaming **nicht** unterstützt.

```python
observed_df = df.observe("metric", count(lit(1)).as("cnt"), count(col("error")).as("malformed"))
observed_df.writeStream.format("...").start()

class MyListener(StreamingQueryListener):
    def onQueryStarted(self, event):
        print(f"'{event.name}' [{event.id}] got started!")
    def onQueryProgress(self, event):
        row = event.progress.observedMetrics.get("metric")
        if row is not None:
            if row.malformed / row.cnt > 0.5:
                print(f"ALERT! Too many malformed records {row.malformed} out of {row.cnt}!")
            else:
                print(f"{row.cnt} rows processed!")
    def onQueryTerminated(self, event):
        print(f"{event.id} got terminated!")

spark.streams.addListener(MyListener())
```

## 4. Tabellenkennungen zuordnen: Unity Catalog, Delta Lake und Streaming-Metriken

- Streaming-Metriken nutzen `reservoirId` als eindeutige Identität einer Delta-Lake-Tabelle als Streaming-Quelle.
- `reservoirId` = die im Delta-Transaktionslog gespeicherte ID — **nicht** die von Unity Catalog vergebene `tableId`.

```sql
DESCRIBE DETAIL <table-name>
-- Ergebnis: Feld `id` der Tabelle == `reservoirId` in den Streaming-Metriken.
-- Funktioniert für UC-verwaltete, UC-externe und Hive-Metastore-Delta-Tabellen.
```

## 5. `StreamingQueryListener`-Objektmetriken (Top-Level)

| Feld | Beschreibung |
|---|---|
| `id` | Eindeutige Query-ID, bleibt über Neustarts hinweg bestehen. |
| `runId` | Eindeutige ID je Start/Neustart. |
| `name` | Benutzerdefinierter Query-Name (`null`, falls keiner gesetzt). |
| `timestamp` | Zeitstempel der Micro-Batch-Ausführung. |
| `batchId` | ID des aktuell verarbeiteten Batches (kann bei Retries mehrfach vorkommen; erhöht sich nicht ohne neue Daten). |
| `batchDuration` | Verarbeitungsdauer des Batches in ms. |
| `numInputRows` | Aggregierte (über alle Quellen) Anzahl verarbeiteter Datensätze im Trigger. |
| `inputRowsPerSecond` | Aggregierte Eingaberate. |
| `processedRowsPerSecond` | Aggregierte Verarbeitungsrate. |
| `durationMs` | Map mit Phasendauern — siehe Abschnitt 6. |
| `eventTime` | Map mit Event-Time-Statistik — siehe Abschnitt 7. |
| `stateOperators` | Array mit Metriken je zustandsbehaftetem Operator — siehe Abschnitt 8. |
| `sources` | Array mit Metriken je Quelle — siehe Abschnitt 10. |
| `sink` | Objekt mit Senken-Metriken — siehe Abschnitt 11. |
| `observedMetrics` | Map mit benannten Observable-Metrics-Ergebnissen (siehe Abschnitt 3). |

## 6. `durationMs`-Objekt

Dauer der einzelnen Phasen der Micro-Batch-Ausführung:

| Feld | Beschreibung |
|---|---|
| `addBatch` | Zeit für die Ausführung des Micro-Batches (ohne Planungszeit). |
| `getBatch` | Zeit zum Abrufen der Offset-Metadaten von der Quelle. |
| `latestOffset` | Zeit zum Abrufen des neuesten Offsets aus den Quellen. |
| `queryPlanning` | Zeit zur Erzeugung des Ausführungsplans. |
| `triggerExecution` | Gesamtzeit zum Planen und Ausführen des Micro-Batches. |
| `walCommit` | Zeit zum Committen der neu verfügbaren Offsets. |
| `commitBatch` | Zeit zum Committen der während `addBatch` in die Senke geschriebenen Daten (nur bei commit-fähigen Senken). |
| `commitOffsets` | Zeit zum Committen des Batches in das Commit-Log. |

## 7. `eventTime`-Objekt

Event-Time-Info im Micro-Batch, genutzt vom Watermark zum Trimmen des Zustands:

| Feld | Beschreibung |
|---|---|
| `avg` / `max` / `min` | Durchschnittliche / maximale / minimale Event-Time im Trigger. |
| `watermark` | Der im Trigger verwendete Watermark-Wert. |

## 8. `stateOperators`-Objekt (`Array[StateOperatorProgress]`)

Info über jede zustandsbehaftete Operation und die daraus erzeugten Aggregationen:

| Feld | Beschreibung |
|---|---|
| `operatorName` | Name des Operators, z. B. `symmetricHashJoin`, `dedupe`, `stateStoreSave`. |
| `numRowsTotal` | Gesamtzahl Zeilen im Zustand. |
| `numRowsUpdated` | Anzahl im Zustand aktualisierter Zeilen. |
| `numRowsRemoved` | Anzahl aus dem Zustand entfernter Zeilen. |
| `allUpdatesTimeMs` / `allRemovalsTimeMs` | Derzeit von Spark nicht messbar (sollen künftig entfernt werden). |
| `commitTimeMs` | Zeit zum Committen aller Updates/Removes und Rückgabe einer neuen Version. |
| `memoryUsedBytes` | Vom State Store genutzter Speicher. |
| `numRowsDroppedByWatermark` | Anzahl als zu spät verworfener Zeilen (bei Streaming-Aggregationen: nach der Aggregation verworfene Zeilen, nicht rohe Eingabezeilen). Näherungswert. |
| `numShufflePartitions` | Anzahl Shuffle-Partitionen dieses Operators. |
| `numStateStoreInstances` | Anzahl initialisierter State-Store-Instanzen (meist = Partitionsanzahl; Stream-Stream-Joins initialisieren 4 pro Partition). |
| `customMetrics` | Feature-spezifische Metriken — siehe Abschnitt 9. |

## 9. `StateOperatorProgress.customMetrics`

Feature-spezifische Metriken, je genutztem State-Store/Operator-Typ.

### RocksDB-State-Store (Auswahl wichtiger Felder)

| Feld | Beschreibung |
|---|---|
| `rocksdbCommitCheckpointLatency` / `rocksdbCommitCompactLatency` / `rocksdbCommitFileSyncLatencyMs` / `rocksdbCommitFlushLatency` / `rocksdbCommitPauseLatency` / `rocksdbCommitWriteBatchLatency` | Latenzen (ms) der jeweiligen Phase beim Checkpoint-Commit. |
| `rocksdbFilesCopied` / `rocksdbFilesReused` / `rocksdbBytesCopied` | Kopierte/wiederverwendete Dateien bzw. Bytes (RocksDB File Manager). |
| `rocksdbGetCount` / `rocksdbGetLatency` / `rocksdbPutCount` / `rocksdbPutLatency` | Anzahl/Latenz der `get`-/`put`-Aufrufe (ohne `WriteBatch`-Gets). |
| `rocksdbReadBlockCacheHitCount` / `rocksdbReadBlockCacheMissCount` | Cache-Treffer/-Fehltreffer im Block-Cache. |
| `rocksdbSstFileSize` | Größe aller SST-Dateien der Instanz. |
| `rocksdbTotalBytesRead` / `rocksdbTotalBytesWritten` | Unkomprimierte gelesene/geschriebene Bytes via `get`/`put`. |
| `rocksdbTotalBytesReadThroughIterator` | Über einen Iterator gelesene Bytes (z. B. bei Timeout-Verarbeitung, Watermarking). |
| `rocksdbTotal*ByCompaction`, `rocksdbTotalCompactionLatencyMs`, `rocksdbTotalFlushLatencyMs` | Kompaktierungs-/Flush-Metriken. |
| `SnapshotLastUploaded.partition_<id>_<state-store-name>` | Zuletzt gesicherte Snapshot-Version je Partition/State-Store (`-1` = noch nie gesichert). |
| `rocksdbWriterStallLatencyMs` | Wartezeit des Writers bis Kompaktierung/Flush abgeschlossen sind. |
| `rocksdbNumInternalColFamiliesKeys`, `rocksdbNumExternalColumnFamilies`, `rocksdbNumInternalColumnFamilies` | Column-Family-Zähler. |

### HDFS-State-Store

| Feld | Beschreibung |
|---|---|
| `stateOnCurrentVersionSizeBytes` | Geschätzte Zustandsgröße der aktuellen Version. |
| `loadedMapCacheHitCount` / `loadedMapCacheMissCount` | Cache-Treffer/-Fehltreffer im Provider. |
| `SnapshotLastUploaded.partition_<id>_<state-store-name>` | Zuletzt hochgeladene Snapshot-Version. |

### Deduplizierung / Aggregation / Stream-Join

| Feld | Beschreibung |
|---|---|
| `numDroppedDuplicateRows` | Anzahl verworfener Duplikate (Deduplizierung). |
| `numRowsReadDuringEviction` | Während der Zustands-Eviction gelesene Zustandszeilen (Deduplizierung und Aggregation). |
| `skippedNullValueCount` | Übersprungene `null`-Werte bei aktiviertem `spark.sql.streaming.stateStore.skipNullsForStreamStreamJoins.enabled` (Stream-Join). |

### `transformWithState` (TWS)

| Feld | Beschreibung |
|---|---|
| `initialStateProcessingTimeMs` | Verarbeitungszeit des gesamten Initial-States. |
| `numValueStateVars` / `numListStateVars` / `numMapStateVars` | Anzahl der jeweiligen State-Variablentypen. |
| `numDeletedStateVars` | Anzahl gelöschter State-Variablen. |
| `timerProcessingTimeMs` | Verarbeitungszeit aller Timer. |
| `numRegisteredTimers` / `numDeletedTimers` / `numExpiredTimers` | Timer-Zähler. |
| `numValueStateWithTTLVars` / `numListStateWithTTLVars` / `numMapStateWithTTLVars` | Anzahl State-Variablen mit TTL je Typ. |
| `numValuesRemovedDueToTTLExpiry` / `numValuesIncrementallyRemovedDueToTTLExpiry` | Wegen TTL-Ablauf entfernte Werte (gesamt / inkrementell). |

- Die meisten dieser Felder sind auch bei `transformWithStateInPandas` vorhanden.

## 10. `sources`-Objekt (`Array[SourceProgress]`)

| Feld | Beschreibung |
|---|---|
| `description` | Beschreibung der Quelle. |
| `startOffset` / `endOffset` / `latestOffset` | Start-Offset des Jobs / zuletzt verarbeiteter Offset / neuester bekannter Offset. |
| `numInputRows` / `inputRowsPerSecond` / `processedRowsPerSecond` | Verarbeitete Zeilen bzw. Raten dieser Quelle. |
| `metrics` | Quellenspezifische Custom-Metriken. |

- Databricks stellt `sources`-Implementierungen für Kafka, Delta Lake, Auto Loader, PubSub und Pulsar bereit.

**Delta-Lake-Quelle:** `description` (z. B. `"DeltaSource[table]"`), `<startOffset/endOffset>.sourceVersion`, `.reservoirId` (siehe Abschnitt 4), `.reservoirVersion`, `.index` (Position in der `AddFiles`-Sequenz der Version, sortiert nach `modificationTimestamp`+`path`), `.isStartingVersion` (initialer Snapshot vs. nachfolgende Änderungen), `<start/end/latestOffset>.eventTimeMillis` (bei Event-Time-Reihenfolge). `metrics.numBytesOutstanding`/`numFilesOutstanding` = Backlog-Metriken.

**Kafka-Quelle:** `description` (z. B. `"KafkaV2[Subscribe[TOPIC]]"`), `startOffset`/`endOffset`/`latestOffset` je Topic/Partition. `metrics.avgOffsetsBehindLatest`/`maxOffsetsBehindLatest`/`minOffsetsBehindLatest` (Rückstand über alle Topics), `metrics.estimatedTotalBytesBehindLatest`.
- Ab DBR 17.1: neueste Kafka-Offsets werden nach **jedem** Micro-Batch abgerufen → bei kontinuierlichem Dateneingang können Backlog-Metriken dauerhaft kleine, von Null verschiedene Werte zeigen (kein Rückstandsindiz).
- DBR 17.0 und darunter: Abruf zu **Batch-Beginn**; Backlog kann `0` sein, wenn die Query durchgängig alle zu Batch-Beginn verfügbaren Daten konsumiert.

**Auto-Loader-Quelle:** `<start/end/latestOffset>.seqNum` (Position in der Dateisequenz), `.sourceVersion`, `.lastBackfillStartTimeMs`/`.lastBackfillFinishTimeMs`, `.lastInputPath`. `metrics.numFilesOutstanding`/`numBytesOutstanding` (Backlog), `metrics.approximateQueueSize` (nur bei `cloudFiles.useNotifications`). `numInputRows` entspricht bei `binaryFile`-Quellformat der Dateianzahl.

**PubSub-Quelle:** `.sourceVersion`, `.seqNum`, `.fetchEpoch`. `metrics.numRecordsReadyToProcess`, `.sizeOfRecordsReadyToProcess`, `.numDuplicatesSinceStreamStart`.

**Pulsar-Quelle:** `metrics.numInputRows`, `metrics.numInputBytes` (je aktueller Micro-Batch).

## 11. `sink`-Objekt (`SinkProgress`)

| Feld | Beschreibung |
|---|---|
| `description` | Beschreibung der Senken-Implementierung. |
| `numOutputRows` | Anzahl Ausgabezeilen (Verhalten variiert je Senkentyp). |
| `metrics` | Senkenspezifische Custom-Metriken. |

**Delta-Lake-Senke:** `description` z. B. `"DeltaSink[table]"`; `numOutputRows` ist **immer `-1`**, da Spark für DSv1-Senken (Klassifizierung von Delta Lake) keine Ausgabezeilen ableiten kann.

**Kafka-Senke:** `description` z. B. `"org.apache.spark.sql.kafka010.KafkaSourceProvider$KafkaTable@..."`; `numOutputRows` = Anzahl im Micro-Batch geschriebener Zeilen (`-1` = unbekannt).

## 12. Beispiel-Event: Kafka-zu-Kafka mit mehreren zustandsbehafteten Operatoren

```json
{
  "id" : "3574feba-646d-4735-83c4-66f657e52517",
  "runId" : "38a78903-9e55-4440-ad81-50b591e4746c",
  "name" : "STREAMING_QUERY_NAME_UNIQUE",
  "timestamp" : "2022-10-31T20:09:30.455Z",
  "batchId" : 1377,
  "numInputRows" : 687,
  "inputRowsPerSecond" : 32.13433743393049,
  "processedRowsPerSecond" : 34.067241892293964,
  "durationMs" : {
    "addBatch" : 18352, "getBatch" : 0, "latestOffset" : 31,
    "queryPlanning" : 977, "triggerExecution" : 20165, "walCommit" : 342
  },
  "eventTime" : {
    "avg" : "2022-10-31T20:09:18.070Z", "max" : "2022-10-31T20:09:30.125Z",
    "min" : "2022-10-31T20:09:09.793Z", "watermark" : "2022-10-31T20:08:46.355Z"
  },
  "stateOperators" : [
    { "operatorName" : "stateStoreSave", "numRowsTotal" : 208, "numRowsUpdated" : 73,
      "numRowsRemoved" : 76, "commitTimeMs" : 0, "memoryUsedBytes" : 167069743,
      "numRowsDroppedByWatermark" : 0, "numShufflePartitions" : 20, "numStateStoreInstances" : 20,
      "customMetrics" : { "rocksdbGetCount" : 222, "rocksdbReadBlockCacheHitCount" : 165, "...": "..." } },
    { "operatorName" : "dedupe", "numRowsTotal" : 2454744, "numRowsUpdated" : 73,
      "numRowsRemoved" : 0, "numRowsDroppedByWatermark" : 34, "numShufflePartitions" : 20,
      "numStateStoreInstances" : 20, "customMetrics" : { "numDroppedDuplicateRows" : 193, "...": "..." } },
    { "operatorName" : "symmetricHashJoin", "numRowsTotal" : 2583, "numRowsUpdated" : 682,
      "numRowsRemoved" : 508, "commitTimeMs" : 21, "memoryUsedBytes" : 668544484,
      "numShufflePartitions" : 20, "numStateStoreInstances" : 80, "customMetrics" : { "...": "..." } }
  ],
  "sources" : [
    { "description" : "KafkaV2[Subscribe[KAFKA_TOPIC_NAME_INPUT_A]]",
      "startOffset" : { "KAFKA_TOPIC_NAME_INPUT_A" : { "0" : 349706380 } },
      "endOffset" : { "KAFKA_TOPIC_NAME_INPUT_A" : { "0" : 349706672 } },
      "latestOffset" : { "KAFKA_TOPIC_NAME_INPUT_A" : { "0" : 349706672 } },
      "numInputRows" : 292, "inputRowsPerSecond" : 13.658, "processedRowsPerSecond" : 14.480,
      "metrics" : { "avgOffsetsBehindLatest" : "0.0", "estimatedTotalBytesBehindLatest" : "0.0",
                     "maxOffsetsBehindLatest" : "0", "minOffsetsBehindLatest" : "0" } }
  ],
  "sink" : {
    "description" : "org.apache.spark.sql.kafka010.KafkaSourceProvider$KafkaTable@e04b100",
    "numOutputRows" : 76
  }
}
```

Weitere dokumentierte Beispiel-Events (analoges Schema, andere Quellen-/Senken-Kombination):
- **Delta-Lake-zu-Delta-Lake:** `stateOperators: []`, `sink.numOutputRows: -1`.
- **Kinesis-zu-Delta-Lake:** Kinesis-`sources`-Metriken wie `mode: "efo"`, `numClosedShards`, `numTotalShards`, `avgMsBehindLatest`.
- **Kafka+Delta-Lake-zu-Delta-Lake:** Stream-Static-artiger Join mit `symmetricHashJoin`-Operator über zwei Quellen.
- **Rate-Source-zu-Delta-Lake:** einfachste Quelle, `RateStreamV2[rowsPerSecond=..., numPartitions=...]`.

## 13. Unity Catalog mit Structured Streaming

- Unity Catalog fügt den verfügbaren Structured-Streaming-Quellen/-Senken keine expliziten Beschränkungen hinzu.
- Möglich: Streamen aus verwalteten (managed) und externen Tabellen; Nutzung von UC-verwalteten externen Speicherorten für Object-Storage-URI-Zugriff; Schreiben in externe Tabellen über Tabellennamen oder Dateipfade (verwaltete Tabellen erfordern den Tabellennamen).
- **Checkpoints müssen in von Unity Catalog verwalteten externen Speicherorten liegen.**

### Eine Unity-Catalog-View als Stream lesen (ab DBR 14.3 LTS)

- Zugrunde liegende Tabellen müssen Delta-Lake-Format verwenden.

```python
df = spark.readStream.table("demoView")
```

- Erforderlich: `SELECT`-Recht auf die View.
- **Gotcha:** Wird die View-Definition geändert (referenzierte Tabellen hinzugefügt/geändert), kann derselbe Streaming-Checkpoint **nicht mehr** verwendet werden.

### Unterstützte Streaming-Optionen für Views

- Der Streaming-Reader wendet Optionen auf die Dateien/Metadaten der zugrunde liegenden Delta-Lake-Tabellen an.
- Unterstützt: `maxFilesPerTrigger`, `maxBytesPerTrigger`, `ignoreDeletes`, `skipChangeCommits`, `withEventTimeOrder`, `startingTimestamp`, `startingVersion`.
- Views mit `UNION ALL` unterstützen `withEventTimeOrder` und `startingVersion` **nicht**.
- Nicht unterstützte Optionen (z. B. `readChangeFeed`) lösen aus:
```
AnalysisException: [UNSUPPORTED_STREAMING_OPTIONS_FOR_VIEW.UNSUPPORTED_OPTION] Unsupported for streaming a view. Reason: option <option> is not supported.
```

### Unterstützte Streaming-Operationen in View-Definitionen

| Operation | Zweck | Operator | Beispiel |
|---|---|---|---|
| Project | Spaltenebenen-Berechtigungen | `SELECT ... FROM ...` | `CREATE VIEW project_view AS SELECT id, value FROM source_table` |
| Filter | Zeilenebenen-Berechtigungen | `WHERE ...` | `CREATE VIEW filter_view AS SELECT * FROM source_table WHERE value > 100` |
| Union all | Ergebnisse mehrerer Tabellen | `UNION ALL` | `CREATE VIEW union_view AS SELECT id, value FROM source_table1 UNION ALL SELECT * FROM source_table2` |

**Nicht unterstützt:** Aggregationen, Sortierungen, Table-Valued Functions (z. B. `table_changes()`). Bei nicht unterstützten Operationen:
```
UnsupportedOperationException: [UNEXPECTED_OPERATOR_IN_STREAMING_VIEW] Unexpected operator <operator> in the CREATE VIEW statement as a streaming source. A streaming view query must consist only of SELECT, WHERE, and UNION ALL operations.
```

### Limitierungen

- Continuous-Processing-Modus von Apache Spark wird nicht unterstützt.
- Je nach Compute-Zugriffsmodus (Standard vs. dediziert) gelten unterschiedliche, separat dokumentierte Streaming-Funktionseinschränkungen.
- **Views als Streaming-Quelle — zusätzliche Einschränkungen:**
  - Nur Views, die Delta-Lake-Tabellen abfragen, können gestreamt werden; andere Datenquellen werden nicht unterstützt.
  - Views müssen bei Unity Catalog registriert sein.
  - Nicht alle Operationen/Optionen werden unterstützt (siehe oben).
  - Wird der View eine neue Spalte hinzugefügt, bevor der Stream das Schema der zugrunde liegenden Tabelle aktualisiert hat, schlägt der Stream mit einem Fehler wegen fehlender Spalte fehl — die Spalte muss zunächst zur zugrunde liegenden Tabelle hinzugefügt werden; erst nachdem der Stream diese Tabellenversion verarbeitet hat, darf sie auch zur View hinzugefügt werden.

**Stand:** 2026-09-14.
