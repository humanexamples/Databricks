# Structured-Streaming-Queries überwachen — Referenz

Dieses Dokument beschreibt das eingebaute Monitoring für Structured-Streaming-Anwendungen auf Databricks: die Spark-UI, das `StreamingQueryListener`-Interface zum Verschicken von Metriken an externe Systeme, Observable Metrics sowie die vollständige Feldreferenz aller über `StreamingQueryListener` verfügbaren Objekte (durationMs, eventTime, stateOperators, sources, sink) inklusive Beispiel-Events.

## Abschnittsübersicht

1. [Übersicht](#uebersicht)
2. [Structured-Streaming-Queries in der Spark-UI unterscheiden](#queryname)
3. [Structured-Streaming-Metriken an externe Dienste senden](#listener)
4. [Observable Metrics in Structured Streaming definieren](#observable-metrics)
5. [Unity-Catalog-, Delta-Lake- und Structured-Streaming-Metriken-Tabellenkennungen zuordnen](#uc-mapping)
6. [StreamingQueryListener-Objektmetriken](#listener-metrics)
7. [durationMs-Objekt](#durationms)
8. [eventTime-Objekt](#eventtime)
9. [stateOperators-Objekt](#stateoperators)
10. [StateOperatorProgress.customMetrics-Objekt](#custommetrics)
11. [sources-Objekt](#sources)
12. [sink-Objekt](#sink)
13. [Beispiele](#beispiele)

---

## <a id="uebersicht">1. Übersicht</a>

Databricks bietet eingebautes Monitoring für Structured-Streaming-Anwendungen über die Spark-UI, im Tab **Streaming**.

## <a id="queryname">2. Structured-Streaming-Queries in der Spark-UI unterscheiden</a>

Vergeben Sie für Ihre Streams einen eindeutigen Query-Namen, indem Sie `.queryName(<query-name>)` zu Ihrem `writeStream`-Code hinzufügen — so lässt sich in der Spark-UI leicht erkennen, welche Metriken zu welchem Stream gehören.

## <a id="listener">3. Structured-Streaming-Metriken an externe Dienste senden</a>

Streaming-Metriken können über das Streaming Query Listener Interface von Apache Spark an externe Dienste gesendet werden, um sie für Alerting oder Dashboarding zu nutzen. Ab Databricks Runtime 11.3 LTS ist `StreamingQueryListener` in Python und Scala verfügbar.

**Wichtig**

Für Workloads mit Unity-Catalog-fähigen Compute-Zugriffsmodi gelten folgende Einschränkungen:

- `StreamingQueryListener` benötigt Databricks Runtime 15.1 oder höher, um Credentials zu verwenden oder mit von Unity Catalog verwalteten Objekten auf Compute mit dediziertem Zugriffsmodus zu interagieren.
- `StreamingQueryListener` benötigt Databricks Runtime 16.1 oder höher für Scala-Workloads, die mit Standard-Zugriffsmodus (früher: Shared-Zugriffsmodus) konfiguriert sind.

**Hinweis**

Die Verarbeitungslatenz durch Listener kann die Query-Verarbeitungsgeschwindigkeit erheblich beeinträchtigen. Es wird empfohlen, die Verarbeitungslogik in diesen Listenern zu begrenzen und stattdessen in schnell antwortende Systeme wie Kafka zu schreiben.

Wenn für die Query an der Quelle keine Daten verfügbar sind und sie auf neue Daten wartet, wird dem Streaming Query Listener eine `onQueryIdle`-Nachricht zugestellt. Eine `onQueryProgress`-Nachricht wird nur am Ende des Streaming-Query-Batches zugestellt. Verarbeitet die Query bereits sehr lange Daten, kann es vorkommen, dass weder `onQueryIdle` noch `onQueryProgress` gesendet werden — die Query ist dennoch gesund und verarbeitet weiter Daten.

Der folgende Code zeigt einfache Beispiele für die Syntax einer Listener-Implementierung:

### Python

```python
class MyListener(StreamingQueryListener):
    def onQueryStarted(self, event):
        """
        Called when a query is started.

        Parameters
        ----------
        event: :class:`pyspark.sql.streaming.listener.QueryStartedEvent`
            The properties are available as the same as Scala API.

        Notes
        -----
        This is called synchronously with
        meth:`pyspark.sql.streaming.DataStreamWriter.start`,
        that is, ``onQueryStart`` will be called on all listeners before
        ``DataStreamWriter.start()`` returns the corresponding
        :class:`pyspark.sql.streaming.StreamingQuery`.
        Do not block in this method as it will block your query.
        """
        pass

    def onQueryProgress(self, event):
        """
        Called when there is some status update (ingestion rate updated, etc.)

        Parameters
        ----------
        event: :class:`pyspark.sql.streaming.listener.QueryProgressEvent`
            The properties are available as the same as Scala API.

        Notes
        -----
        This method is asynchronous. The status in
        :class:`pyspark.sql.streaming.StreamingQuery` returns the
        most recent status, regardless of when this method is called. The status
        of :class:`pyspark.sql.streaming.StreamingQuery`.
        may change before or when you process the event.
        For example, you may find :class:`StreamingQuery`
        terminates when processing `QueryProgressEvent`.
        """
        pass

    def onQueryIdle(self, event):
        """
        Called when the query is idle and waiting for new data to process.
        """
        pass

    def onQueryTerminated(self, event):
        """
        Called when a query is stopped, with or without error.

        Parameters
        ----------
        event: :class:`pyspark.sql.streaming.listener.QueryTerminatedEvent`
            The properties are available as the same as Scala API.
        """
        pass

my_listener = MyListener()
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.streaming.StreamingQueryListener
import org.apache.spark.sql.streaming.StreamingQueryListener._

val myListener = new StreamingQueryListener {

  /**
    * Called when a query is started.
    * @note This is called synchronously with
    *       [[org.apache.spark.sql.streaming.DataStreamWriter `DataStreamWriter.start()`]].
    *       `onQueryStart` calls on all listeners before
    *       `DataStreamWriter.start()` returns the corresponding [[StreamingQuery]].
    *        Do not block this method, as it blocks your query.
    */
  def onQueryStarted(event: QueryStartedEvent): Unit = {}

  /**
    * Called when there is some status update (ingestion rate updated, etc.)
    *
    * @note This method is asynchronous. The status in [[StreamingQuery]] returns the
    *       latest status, regardless of when this method is called. The status of [[StreamingQuery]]
    *       may change before or when you process the event. For example, you may find [[StreamingQuery]]
    *       terminates when processing `QueryProgressEvent`.
    */
  def onQueryProgress(event: QueryProgressEvent): Unit = {}

  /**
    * Called when the query is idle and waiting for new data to process.
    */
  def onQueryIdle(event: QueryProgressEvent): Unit = {}

  /**
    * Called when a query is stopped, with or without error.
    */
  def onQueryTerminated(event: QueryTerminatedEvent): Unit = {}
}
```

## <a id="observable-metrics">4. Observable Metrics in Structured Streaming definieren</a>

Observable Metrics sind benannte, beliebige Aggregatfunktionen, die auf einer Query (DataFrame) definiert werden können. Sobald die Ausführung eines DataFrames einen Abschlusspunkt erreicht (d. h. eine Batch-Query beendet oder eine Streaming-Epoche erreicht), wird ein benanntes Event emittiert, das die Metriken für die seit dem letzten Abschlusspunkt verarbeiteten Daten enthält.

Diese Metriken lassen sich beobachten, indem ein Listener an die Spark-Session angehängt wird. Der Listener hängt vom Ausführungsmodus ab:

- **Batch-Modus**: `QueryExecutionListener` verwenden.

  `QueryExecutionListener` wird aufgerufen, wenn die Query abgeschlossen ist. Zugriff auf die Metriken über die Map `QueryExecution.observedMetrics`.
- **Streaming bzw. Micro-Batch**: `StreamingQueryListener` verwenden.

  `StreamingQueryListener` wird aufgerufen, wenn die Streaming-Query eine Epoche abschließt. Zugriff auf die Metriken über die Map `StreamingQueryProgress.observedMetrics`. Databricks unterstützt den `continuous`-Trigger-Modus für Streaming nicht.

Beispiel:

### Python

```python
# Observe metric
observed_df = df.observe("metric", count(lit(1)).as("cnt"), count(col("error")).as("malformed"))
observed_df.writeStream.format("...").start()

# Define my listener.
class MyListener(StreamingQueryListener):
    def onQueryStarted(self, event):
        print(f"'{event.name}' [{event.id}] got started!")
    def onQueryProgress(self, event):
        row = event.progress.observedMetrics.get("metric")
        if row is not None:
            if row.malformed / row.cnt > 0.5:
                print("ALERT! Ouch! there are too many malformed "
                      f"records {row.malformed} out of {row.cnt}!")
            else:
                print(f"{row.cnt} rows processed!")
    def onQueryTerminated(self, event):
        print(f"{event.id} got terminated!")

# Add my listener.
spark.streams.addListener(MyListener())
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
// Observe row count (rc) and error row count (erc) in the streaming Dataset
val observed_ds = ds.observe("my_event", count(lit(1)).as("rc"), count($"error").as("erc"))
observed_ds.writeStream.format("...").start()

// Monitor the metrics using a listener
spark.streams.addListener(new StreamingQueryListener() {
  override def onQueryProgress(event: QueryProgressEvent): Unit = {
    event.progress.observedMetrics.get("my_event").foreach { row =>
      // Trigger if the number of errors exceeds 5 percent
      val num_rows = row.getAs[Long]("rc")
      val num_error_rows = row.getAs[Long]("erc")
      val ratio = num_error_rows.toDouble / num_rows
      if (ratio > 0.05) {
        // Trigger alert
      }
    }
  }
})
```

## <a id="uc-mapping">5. Unity-Catalog-, Delta-Lake- und Structured-Streaming-Metriken-Tabellenkennungen zuordnen</a>

Structured-Streaming-Metriken verwenden an mehreren Stellen das Feld `reservoirId` als eindeutige Identität einer Delta-Lake-Tabelle, die als Quelle einer Streaming-Query dient.

Das Feld `reservoirId` bildet die eindeutige Kennung ab, die von der Delta-Lake-Tabelle im Delta-Transaktionslog gespeichert wird. Diese ID entspricht **nicht** dem `tableId`-Wert, den Unity Catalog vergibt und im Catalog Explorer anzeigt.

Verwenden Sie die folgende Syntax, um die Tabellenkennung einer Delta-Lake-Tabelle einzusehen. Dies funktioniert für Unity-Catalog-verwaltete Tabellen, Unity-Catalog-externe Tabellen und alle Hive-Metastore-Delta-Lake-Tabellen:

```sql
DESCRIBE DETAIL <table-name>
```

Das in den Ergebnissen angezeigte Feld `id` ist die Kennung, die auf `reservoirId` in den Streaming-Metriken abgebildet wird.

## <a id="listener-metrics">6. StreamingQueryListener-Objektmetriken</a>

| Feld | Beschreibung |
| --- | --- |
| `id` | Eine eindeutige Query-ID, die über Neustarts hinweg bestehen bleibt. |
| `runId` | Eine Query-ID, die für jeden Start/Neustart eindeutig ist. Siehe [StreamingQuery.runId()](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.StreamingQuery.runId.html). |
| `name` | Der benutzerdefinierte Name der Query. `name` ist `null`, wenn kein Name angegeben wurde. |
| `timestamp` | Der Zeitstempel für die Ausführung des Micro-Batches. |
| `batchId` | Eine eindeutige ID für den aktuell verarbeiteten Batch von Daten. Bei Wiederholungen nach einem Fehler kann eine gegebene Batch-ID mehr als einmal ausgeführt werden. Ebenso wird die Batch-ID nicht erhöht, wenn keine Daten zu verarbeiten sind. |
| `batchDuration` | Die Verarbeitungsdauer eines Batch-Vorgangs in Millisekunden. |
| `numInputRows` | Die aggregierte (über alle Quellen) Anzahl der in einem Trigger verarbeiteten Datensätze. |
| `inputRowsPerSecond` | Die aggregierte (über alle Quellen) Rate der eintreffenden Daten. |
| `processedRowsPerSecond` | Die aggregierte (über alle Quellen) Rate, mit der Spark Daten verarbeitet. |

`StreamingQueryListener` definiert außerdem folgende Felder, die Objekte enthalten, welche sich für Custom-Metriken und Quellfortschrittsdetails untersuchen lassen:

| Feld | Beschreibung |
| --- | --- |
| `durationMs` | Typ: `ju.Map[String, JLong]`. Siehe durationMs-Objekt. |
| `eventTime` | Typ: `ju.Map[String, String]`. Siehe eventTime-Objekt. |
| `stateOperators` | Typ: `Array[StateOperatorProgress]`. Siehe stateOperators-Objekt. |
| `sources` | Typ: `Array[SourceProgress]`. Siehe sources-Objekt. |
| `sink` | Typ: `SinkProgress`. Siehe sink-Objekt. |
| `observedMetrics` | Typ: `ju.Map[String, Row]`. Benannte, beliebige Aggregatfunktionen, die auf einem DataFrame/einer Query definiert werden können (z. B. `df.observe`). |

## <a id="durationms">7. durationMs-Objekt</a>

**Objekttyp**: `ju.Map[String, JLong]`

Informationen darüber, wie lange verschiedene Phasen der Micro-Batch-Ausführung dauern.

| Feld | Beschreibung |
| --- | --- |
| `durationMs.addBatch` | Die Zeit, die zur Ausführung des Micro-Batches benötigt wird. Ausgenommen ist die Zeit, die Spark zur Planung des Micro-Batches benötigt. |
| `durationMs.getBatch` | Die Zeit, um die Metadaten zu den Offsets von der Quelle abzurufen. |
| `durationMs.latestOffset` | Der zuletzt konsumierte Offset für den Micro-Batch. Dieses Fortschrittsobjekt bezieht sich auf die Zeit, die zum Abrufen des neuesten Offsets aus den Quellen benötigt wird. |
| `durationMs.queryPlanning` | Die Zeit, die zur Erzeugung des Ausführungsplans benötigt wird. |
| `durationMs.triggerExecution` | Die Zeit, um den Micro-Batch zu planen und auszuführen. |
| `durationMs.walCommit` | Die Zeit, die zum Committen der neu verfügbaren Offsets benötigt wird. |
| `durationMs.commitBatch` | Die Zeit, die zum Committen der während `addBatch` in die Senke geschriebenen Daten benötigt wird. Nur vorhanden bei Senken, die Commit unterstützen. |
| `durationMs.commitOffsets` | Die Zeit, die zum Committen des Batches in das Commit-Log benötigt wird. |

## <a id="eventtime">8. eventTime-Objekt</a>

**Objekttyp**: `ju.Map[String, String]`

Informationen über den Event-Time-Wert, der in den im Micro-Batch verarbeiteten Daten gesehen wurde. Diese Daten werden vom Watermark genutzt, um zu bestimmen, wie der Zustand für die Verarbeitung zustandsbehafteter Aggregationen im Structured-Streaming-Job zu trimmen ist.

| Feld | Beschreibung |
| --- | --- |
| `eventTime.avg` | Die in diesem Trigger gesehene durchschnittliche Event-Time. |
| `eventTime.max` | Die in diesem Trigger gesehene maximale Event-Time. |
| `eventTime.min` | Die in diesem Trigger gesehene minimale Event-Time. |
| `eventTime.watermark` | Der in diesem Trigger verwendete Watermark-Wert. |

## <a id="stateoperators">9. stateOperators-Objekt</a>

**Objekttyp**: `Array[StateOperatorProgress]`. Das `stateOperators`-Objekt enthält Informationen über die im Structured-Streaming-Job definierten zustandsbehafteten Operationen und die daraus erzeugten Aggregationen.

| Feld | Beschreibung |
| --- | --- |
| `stateOperators.operatorName` | Der Name des zustandsbehafteten Operators, auf den sich die Metriken beziehen, z. B. `symmetricHashJoin`, `dedupe` oder `stateStoreSave`. |
| `stateOperators.numRowsTotal` | Die Gesamtzahl der Zeilen im Zustand als Ergebnis eines zustandsbehafteten Operators bzw. einer Aggregation. |
| `stateOperators.numRowsUpdated` | Die Gesamtzahl der im Zustand aktualisierten Zeilen als Ergebnis eines zustandsbehafteten Operators bzw. einer Aggregation. |
| `stateOperators.allUpdatesTimeMs` | Diese Metrik ist derzeit von Spark nicht messbar und soll in zukünftigen Updates entfernt werden. |
| `stateOperators.numRowsRemoved` | Die Gesamtzahl der aus dem Zustand entfernten Zeilen als Ergebnis eines zustandsbehafteten Operators bzw. einer Aggregation. |
| `stateOperators.allRemovalsTimeMs` | Diese Metrik ist derzeit von Spark nicht messbar und soll in zukünftigen Updates entfernt werden. |
| `stateOperators.commitTimeMs` | Die Zeit, die zum Committen aller Aktualisierungen (Puts und Removes) und Rückgabe einer neuen Version benötigt wird. |
| `stateOperators.memoryUsedBytes` | Vom State Store genutzter Speicher. |
| `stateOperators.numRowsDroppedByWatermark` | Die Anzahl der Zeilen, die als zu spät für die Einbeziehung in eine zustandsbehaftete Aggregation gelten. **Nur bei Streaming-Aggregationen**: die Anzahl der nach der Aggregation verworfenen Zeilen (nicht die rohen Eingabezeilen). Diese Zahl ist nicht exakt, gibt aber einen Hinweis darauf, dass verspätete Daten verworfen werden. |
| `stateOperators.numShufflePartitions` | Die Anzahl der Shuffle-Partitionen für diesen zustandsbehafteten Operator. |
| `stateOperators.numStateStoreInstances` | Die tatsächliche State-Store-Instanz, die der Operator initialisiert und pflegt. Bei vielen zustandsbehafteten Operatoren entspricht dies der Anzahl der Partitionen. Stream-Stream-Joins initialisieren jedoch vier State-Store-Instanzen pro Partition. |
| `stateOperators.customMetrics` | Siehe StateOperatorProgress.customMetrics für weitere Details. |

## <a id="custommetrics">10. StateOperatorProgress.customMetrics-Objekt</a>

**Objekttyp**: `ju.Map[String, JLong]`

`StateOperatorProgress` besitzt ein Feld `customMetrics`, das die Metriken enthält, die für das jeweils genutzte Feature spezifisch sind.

| Feature | Beschreibung |
| --- | --- |
| RocksDB State Store | Metriken für den RocksDB-State-Store. |
| HDFS State Store | Metriken für den HDFS-State-Store. |
| Stream-Deduplizierung | Metriken für die Zeilen-Deduplizierung. |
| Stream-Aggregation | Metriken für die Zeilen-Aggregation. |
| Stream-Join-Operator | Metriken für den Stream-Join-Operator. |
| `transformWithState` | Metriken für den `transformWithState`-Operator. |

### RocksDB-State-Store-Custom-Metriken

Von RocksDB gesammelte Informationen über Performance und Operationen bezüglich der für den Structured-Streaming-Job vorgehaltenen zustandsbehafteten Werte.

| Feld | Beschreibung |
| --- | --- |
| `customMetrics.rocksdbBytesCopied` | Die Anzahl der kopierten Bytes, wie vom RocksDB File Manager erfasst. |
| `customMetrics.rocksdbCommitCheckpointLatency` | Die Zeit in Millisekunden, um einen Snapshot des nativen RocksDB zu erstellen und in ein lokales Verzeichnis zu schreiben. |
| `customMetrics.rocksdbCompactLatency` | Die Zeit in Millisekunden für die (optionale) Kompaktierung während des Checkpoint-Commits. |
| `customMetrics.rocksdbCommitCompactLatency` | Die Kompaktierungszeit während des Commits, in Millisekunden. |
| `customMetrics.rocksdbCommitFileSyncLatencyMs` | Die Zeit in Millisekunden zum Synchronisieren des nativen RocksDB-Snapshots mit externem Speicher (dem Checkpoint-Speicherort). |
| `customMetrics.rocksdbCommitFlushLatency` | Die Zeit in Millisekunden, um die In-Memory-Änderungen von RocksDB auf die lokale Festplatte zu flushen. |
| `customMetrics.rocksdbCommitPauseLatency` | Die Zeit in Millisekunden, um die Hintergrund-Worker-Threads im Rahmen des Checkpoint-Commits anzuhalten, z. B. für Kompaktierung. |
| `customMetrics.rocksdbCommitWriteBatchLatency` | Die Zeit in Millisekunden, um die in der In-Memory-Struktur (`WriteBatch`) zwischengespeicherten Schreibvorgänge auf das native RocksDB anzuwenden. |
| `customMetrics.rocksdbFilesCopied` | Die Anzahl der kopierten Dateien, wie vom RocksDB File Manager erfasst. |
| `customMetrics.rocksdbFilesReused` | Die Anzahl der wiederverwendeten Dateien, wie vom RocksDB File Manager erfasst. |
| `customMetrics.rocksdbGetCount` | Die Anzahl der `get`-Aufrufe (ohne `gets` aus `WriteBatch` — der In-Memory-Batch zum Zwischenspeichern von Schreibvorgängen). |
| `customMetrics.rocksdbGetLatency` | Die durchschnittliche Zeit in Nanosekunden für den zugrunde liegenden nativen `RocksDB::Get`-Aufruf. |
| `customMetrics.rocksdbReadBlockCacheHitCount` | Die Anzahl der Cache-Treffer im Block-Cache von RocksDB. |
| `customMetrics.rocksdbReadBlockCacheMissCount` | Die Anzahl der Cache-Fehltreffer im Block-Cache von RocksDB. |
| `customMetrics.rocksdbSstFileSize` | Die Größe aller Static-Sorted-Table-(SST)-Dateien in der RocksDB-Instanz. |
| `customMetrics.rocksdbTotalBytesRead` | Die Anzahl der durch `get`-Operationen gelesenen unkomprimierten Bytes. |
| `customMetrics.rocksdbTotalBytesWritten` | Die Gesamtzahl der durch `put`-Operationen geschriebenen unkomprimierten Bytes. |
| `customMetrics.rocksdbTotalBytesReadThroughIterator` | Die Gesamtzahl der über einen Iterator gelesenen unkomprimierten Bytes. Manche zustandsbehafteten Operationen (z. B. Timeout-Verarbeitung in `FlatMapGroupsWithState` und Watermarking) erfordern das Lesen von Daten über einen Iterator. |
| `customMetrics.rocksdbTotalBytesReadByCompaction` | Die Anzahl der Bytes, die der Kompaktierungsprozess von der Festplatte liest. |
| `customMetrics.rocksdbTotalBytesWrittenByCompaction` | Die Gesamtzahl der Bytes, die der Kompaktierungsprozess auf die Festplatte schreibt. |
| `customMetrics.rocksdbTotalCompactionLatencyMs` | Die Zeit in Millisekunden für RocksDB-Kompaktierungen, einschließlich Hintergrund-Kompaktierungen und der optionalen, während des Commits ausgelösten Kompaktierung. |
| `customMetrics.rocksdbTotalFlushLatencyMs` | Die gesamte Flush-Zeit, einschließlich Hintergrund-Flushing. Flush-Operationen sind Prozesse, bei denen die `MemTable` auf Speicher geflusht wird, sobald sie voll ist. `MemTables` sind die erste Ebene, auf der Daten in RocksDB gespeichert werden. |
| `customMetrics.rocksdbZipFileBytesUncompressed` | Die Größe in Bytes der unkomprimierten Zip-Dateien, wie vom File Manager gemeldet. Der File Manager verwaltet die physische Festplattennutzung und Löschung von SST-Dateien. |
| `customMetrics.SnapshotLastUploaded.partition_<partition-id>_<state-store-name>` | Die zuletzt am Checkpoint-Speicherort gesicherte Version des RocksDB-Snapshots. Ein Wert von "-1" bedeutet, dass noch nie ein Snapshot gesichert wurde. Da Snapshots spezifisch für jede State-Store-Instanz sind, gilt diese Metrik für eine bestimmte Partitions-ID und einen State-Store-Namen. |
| `customMetrics.rocksdbPutLatency` | Die gesamte Put-Aufruf-Latenz. |
| `customMetrics.rocksdbPutCount` | Die Anzahl der Put-Aufrufe. |
| `customMetrics.rocksdbWriterStallLatencyMs` | Die Wartezeit des Writers, bis Kompaktierung oder Flush abgeschlossen sind. |
| `customMetrics.rocksdbTotalBytesWrittenByFlush` | Die durch Flush geschriebenen Gesamtbytes. |
| `customMetrics.rocksdbPinnedBlocksMemoryUsage` | Die Speichernutzung für gepinnte Blöcke. |
| `customMetrics.rocksdbNumInternalColFamiliesKeys` | Die Anzahl interner Schlüssel für interne Column-Families. |
| `customMetrics.rocksdbNumExternalColumnFamilies` | Die Anzahl externer Column-Families. |
| `customMetrics.rocksdbNumInternalColumnFamilies` | Die Anzahl interner Column-Families. |

### HDFS-State-Store-Custom-Metriken

Gesammelte Informationen über das Verhalten und die Operationen des HDFS-State-Store-Providers.

| Feld | Beschreibung |
| --- | --- |
| `customMetrics.stateOnCurrentVersionSizeBytes` | Die geschätzte Größe des Zustands nur für die aktuelle Version. |
| `customMetrics.loadedMapCacheHitCount` | Die Anzahl der Cache-Treffer bei im Provider zwischengespeicherten Zuständen. |
| `customMetrics.loadedMapCacheMissCount` | Die Anzahl der Cache-Fehltreffer bei im Provider zwischengespeicherten Zuständen. |
| `customMetrics.SnapshotLastUploaded.partition_<partition-id>_<state-store-name>` | Die zuletzt hochgeladene Version des Snapshots für eine bestimmte State-Store-Instanz. |

### Deduplizierungs-Custom-Metriken

Gesammelte Informationen über Deduplizierungsverhalten und -operationen.

| Feld | Beschreibung |
| --- | --- |
| `customMetrics.numDroppedDuplicateRows` | Die Anzahl der verworfenen Duplikatzeilen. |
| `customMetrics.numRowsReadDuringEviction` | Die Anzahl der während der Zustands-Eviction gelesenen Zustandszeilen. |

### Aggregations-Custom-Metriken

Gesammelte Informationen über Aggregationsverhalten und -operationen.

| Feld | Beschreibung |
| --- | --- |
| `customMetrics.numRowsReadDuringEviction` | Die Anzahl der während der Zustands-Eviction gelesenen Zustandszeilen. |

### Stream-Join-Custom-Metriken

Gesammelte Informationen über das Verhalten und die Operationen von Stream-Joins.

| Feld | Beschreibung |
| --- | --- |
| `customMetrics.skippedNullValueCount` | Die Anzahl übersprungener `null`-Werte, wenn `spark.sql.streaming.stateStore.skipNullsForStreamStreamJoins.enabled` auf `true` gesetzt ist. |

### transformWithState-Custom-Metriken

Gesammelte Informationen über das Verhalten und die Operationen von `transformWithState` (TWS).

| Feld | Beschreibung |
| --- | --- |
| `customMetrics.initialStateProcessingTimeMs` | Anzahl Millisekunden zur Verarbeitung des gesamten Initial-States. |
| `customMetrics.numValueStateVars` | Anzahl der Value-State-Variablen. Auch vorhanden bei `transformWithStateInPandas`. |
| `customMetrics.numListStateVars` | Anzahl der List-State-Variablen. Auch vorhanden bei `transformWithStateInPandas`. |
| `customMetrics.numMapStateVars` | Anzahl der Map-State-Variablen. Auch vorhanden bei `transformWithStateInPandas`. |
| `customMetrics.numDeletedStateVars` | Anzahl der gelöschten State-Variablen. Auch vorhanden bei `transformWithStateInPandas`. |
| `customMetrics.timerProcessingTimeMs` | Anzahl Millisekunden zur Verarbeitung aller Timer. |
| `customMetrics.numRegisteredTimers` | Anzahl der registrierten Timer. Auch vorhanden bei `transformWithStateInPandas`. |
| `customMetrics.numDeletedTimers` | Anzahl der gelöschten Timer. Auch vorhanden bei `transformWithStateInPandas`. |
| `customMetrics.numExpiredTimers` | Anzahl der abgelaufenen Timer. Auch vorhanden bei `transformWithStateInPandas`. |
| `customMetrics.numValueStateWithTTLVars` | Anzahl der Value-State-Variablen mit TTL. Auch vorhanden bei `transformWithStateInPandas`. |
| `customMetrics.numListStateWithTTLVars` | Anzahl der List-State-Variablen mit TTL. Auch vorhanden bei `transformWithStateInPandas`. |
| `customMetrics.numMapStateWithTTLVars` | Anzahl der Map-State-Variablen mit TTL. Auch vorhanden bei `transformWithStateInPandas`. |
| `customMetrics.numValuesRemovedDueToTTLExpiry` | Anzahl der wegen TTL-Ablauf entfernten Werte. Auch vorhanden bei `transformWithStateInPandas`. |
| `customMetrics.numValuesIncrementallyRemovedDueToTTLExpiry` | Anzahl der inkrementell wegen TTL-Ablauf entfernten Werte. |

## <a id="sources">11. sources-Objekt</a>

**Objekttyp**: `Array[SourceProgress]`

Das `sources`-Objekt enthält Informationen und Metriken für Streaming-Datenquellen.

| Feld | Beschreibung |
| --- | --- |
| `description` | Eine detaillierte Beschreibung der Streaming-Datenquellen-Tabelle. |
| `startOffset` | Die Start-Offset-Nummer innerhalb der Datenquellen-Tabelle, bei der der Streaming-Job gestartet wurde. |
| `endOffset` | Der zuletzt vom Micro-Batch verarbeitete Offset. |
| `latestOffset` | Der neueste vom Micro-Batch verarbeitete Offset. |
| `numInputRows` | Die Anzahl der aus dieser Quelle verarbeiteten Eingabezeilen. |
| `inputRowsPerSecond` | Die Rate, mit der Daten aus dieser Quelle zur Verarbeitung eintreffen (pro Sekunde). |
| `processedRowsPerSecond` | Die Rate, mit der Spark Daten aus dieser Quelle verarbeitet. |
| `metrics` | Typ: `ju.Map[String, String]`. Enthält Custom-Metriken für eine bestimmte Datenquelle. |

Databricks stellt folgende `sources`-Objekt-Implementierungen bereit:

- Apache-Kafka-Quellen
- Delta-Lake-Tabellenquellen
- Auto-Loader-Quellenobjekt
- PubSub-Quellenobjekt
- Pulsar-Quellenobjekt

**Hinweis**

Für Felder der Form `sources.<startOffset / endOffset / latestOffset>.*` (oder Varianten davon) ist eines der (bis zu) drei möglichen Felder gemeint, die jeweils das angegebene Unterfeld enthalten:

- `sources.startOffset.<child-field>`
- `sources.endOffset.<child-field>`
- `sources.latestOffset.<child-field>`

### Delta-Lake-sources-Objekt

Definitionen der Custom-Metriken für Delta-Lake-Tabellen als Streaming-Datenquelle.

| Feld | Beschreibung |
| --- | --- |
| `sources.description` | Die Beschreibung der Quelle, aus der die Streaming-Query liest. Beispiel: `"DeltaSource[table]"`. |
| `sources.<startOffset / endOffset>.sourceVersion` | Die Serialisierungsversion, mit der dieser Offset kodiert ist. |
| `sources.<startOffset / endOffset>.reservoirId` | Die ID der gelesenen Tabelle. Wird genutzt, um Fehlkonfigurationen beim Neustart einer Query zu erkennen. Siehe Abschnitt "Unity-Catalog-, Delta-Lake- und Structured-Streaming-Metriken-Tabellenkennungen zuordnen". |
| `sources.<startOffset / endOffset>.reservoirVersion` | Die Version der Tabelle, die aktuell verarbeitet wird. |
| `sources.<startOffset / endOffset>.index` | Der Index in der Sequenz der `AddFiles` dieser Version. Wird genutzt, um große Commits in mehrere Batches zu unterteilen. Dieser Index entsteht durch Sortierung nach `modificationTimestamp` und `path`. |
| `sources.<startOffset / endOffset>.isStartingVersion` | Gibt an, ob der aktuelle Offset den Start einer neuen Streaming-Query markiert, statt die Verarbeitung von Änderungen, die nach der initialen Datenverarbeitung eingetroffen sind. Beim Start einer neuen Query werden zunächst alle zu Beginn in der Tabelle vorhandenen Daten verarbeitet und danach alle neu eintreffenden Daten. |
| `sources.<startOffset / endOffset / latestOffset>.eventTimeMillis` | Für die Event-Time-Reihenfolge erfasste Event-Time. Die Event-Time der zur Verarbeitung anstehenden Daten des initialen Snapshots. Wird bei der Verarbeitung eines initialen Snapshots mit Event-Time-Reihenfolge genutzt. |
| `sources.latestOffset` | Der zuletzt von der Micro-Batch-Query verarbeitete Offset. |
| `sources.numInputRows` | Die Anzahl der aus dieser Quelle verarbeiteten Eingabezeilen. |
| `sources.inputRowsPerSecond` | Die Rate, mit der Daten aus dieser Quelle zur Verarbeitung eintreffen. |
| `sources.processedRowsPerSecond` | Die Rate, mit der Spark Daten aus dieser Quelle verarbeitet. |
| `sources.metrics.numBytesOutstanding` | Die kombinierte Größe der ausstehenden Dateien (von RocksDB nachverfolgte Dateien). Dies ist die Backlog-Metrik für Delta und Auto Loader als Streaming-Quelle. |
| `sources.metrics.numFilesOutstanding` | Die Anzahl der noch zu verarbeitenden ausstehenden Dateien. Dies ist die Backlog-Metrik für Delta und Auto Loader als Streaming-Quelle. |

### Apache-Kafka-sources-Objekt

Definitionen der Custom-Metriken für Apache-Kafka-Streaming-Datenquellen.

| Feld | Beschreibung |
| --- | --- |
| `sources.description` | Eine detaillierte Beschreibung der Kafka-Quelle mit Angabe des genauen gelesenen Kafka-Topics. Beispiel: `"KafkaV2[Subscribe[KAFKA_TOPIC_NAME_INPUT_A]]"`. |
| `sources.startOffset` | Die Start-Offset-Nummer innerhalb des Kafka-Topics, bei der der Streaming-Job gestartet wurde. |
| `sources.endOffset` | Der zuletzt vom Micro-Batch verarbeitete Offset. Dieser kann bei einer laufenden Micro-Batch-Ausführung gleich `latestOffset` sein. |
| `sources.latestOffset` | Der vom Micro-Batch ermittelte neueste Offset. Bei Drosselung verarbeitet der Micro-Batching-Prozess unter Umständen nicht alle Offsets, sodass sich `endOffset` und `latestOffset` unterscheiden. |
| `sources.numInputRows` | Die Anzahl der aus dieser Quelle verarbeiteten Eingabezeilen. |
| `sources.inputRowsPerSecond` | Die Rate, mit der Daten aus dieser Quelle zur Verarbeitung eintreffen. |
| `sources.processedRowsPerSecond` | Die Rate, mit der Spark Daten aus dieser Quelle verarbeitet. |
| `sources.metrics.avgOffsetsBehindLatest` | Die durchschnittliche Anzahl an Offsets, um die die Streaming-Query hinter dem neuesten verfügbaren Offset über alle abonnierten Topics zurückliegt. |
| `sources.metrics.estimatedTotalBytesBehindLatest` | Die geschätzte Anzahl an Bytes, die der Query-Prozess aus den abonnierten Topics noch nicht konsumiert hat. |
| `sources.metrics.maxOffsetsBehindLatest` | Die maximale Anzahl an Offsets, um die die Streaming-Query hinter dem neuesten verfügbaren Offset über alle abonnierten Topics zurückliegt. |
| `sources.metrics.minOffsetsBehindLatest` | Die minimale Anzahl an Offsets, um die die Streaming-Query hinter dem neuesten verfügbaren Offset über alle abonnierten Topics zurückliegt. |

Ab Databricks Runtime 17.1 werden die neuesten Kafka-Offsets nach Abschluss jedes Micro-Batches abgerufen. Bei Topics mit kontinuierlichem Dateneingang können die Backlog-Metriken kleine, dauerhaft von null verschiedene Werte zeigen. Dies ist erwartetes Verhalten und bedeutet nicht, dass der Stream in Rückstand gerät.

In Databricks Runtime 17.0 und darunter werden die neuesten Kafka-Offsets zum Startzeitpunkt des Micro-Batches abgerufen. Backlog-Metriken können `0` zurückgeben, wenn Streaming-Queries durchgängig alle zu Beginn des Micro-Batches verfügbaren Datensätze konsumieren.

### AWS-Kinesis-sources-Objekt (aus der AWS-Doku ergänzt)

Definitionen der Custom-Metriken für AWS-Kinesis-Streaming-Datenquellen.

| Feld | Beschreibung |
| --- | --- |
| `sources.description` | Beschreibung der Kinesis-Quelle mit Angabe des genauen gelesenen Kinesis-Streams. Beispiel: `"KinesisV2[stream]"`. |
| `sources.metrics.avgMsBehindLatest` | Durchschnittliche Anzahl Millisekunden, die ein Consumer hinter dem Anfang des Streams zurückliegt. |
| `sources.metrics.maxMsBehindLatest` | Maximale Anzahl Millisekunden, die ein Consumer hinter dem Anfang des Streams zurückliegt. |
| `sources.metrics.minMsBehindLatest` | Minimale Anzahl Millisekunden, die ein Consumer hinter dem Anfang des Streams zurückliegt. |
| `sources.metrics.totalPrefetchedBytes` | Anzahl der noch zu verarbeitenden Bytes. Das ist die **Backlog-Metrik** für Kinesis als Quelle. |
| `sources.<startOffset / endOffset / latestOffset>(index).shard.stream` | Name des Kinesis-Streams. |
| `sources.<startOffset / endOffset / latestOffset>(index).shard.shardId` | ID des Kinesis-Shards. |
| `sources.<startOffset / endOffset / latestOffset>(index).firstSeqNum` | Erste Sequenznummer der in einem Batch konsumierten Datensätze eines Shards. |
| `sources.<startOffset / endOffset / latestOffset>(index).lastSeqNum` | Letzte Sequenznummer der in einem Batch konsumierten Datensätze eines Shards. |
| `sources.<startOffset / endOffset / latestOffset>(index).closed` | Ob der Shard vom Kinesis-Stream geschlossen wurde. |
| `sources.<startOffset / endOffset / latestOffset>(index).msBehindLatest` | Ungefährer Rückstand der Streaming-Query gegenüber den neuesten Daten im Kinesis-Stream. |
| `sources.<startOffset / endOffset / latestOffset>(index).lastRecordSeqNum` | Sequenznummer des zuletzt konsumierten Datensatzes; dient der Prüfung auf Datenverlust. Kann bei EFO-Reads von `endSeqNum` abweichen. |
| `sources.metrics.mode` | Verwendeter Consumer-Modus: `Polling` oder `EFO`. |
| `sources.metrics.numStreams` | Anzahl der Kinesis-Streams. |
| `sources.metrics.numTotalShards` | Gesamtzahl aktiver und geschlossener Shards. |
| `sources.metrics.numClosedShards` | Anzahl geschlossener Shards. |
| `sources.metrics.numProcessedBytes` | Anzahl verarbeiteter Bytes. |
| `sources.metrics.numProcessedRecords` | Anzahl verarbeiteter Datensätze. |
| `sources.metrics.numAwsRateLimitErrors` | Bei Polling-Queries im Real-Time Mode: Anzahl der `GetRecords`-Anfragen, die AWS im abgeschlossenen Trigger per Rate Limit gedrosselt hat. |
| `sources.metrics.numRegisteredConsumers` | Anzahl registrierter Consumer im EFO-Modus. |

Mehr dazu: „Monitor Kinesis metrics“ in der Kinesis-Doku.

### Auto-Loader-Quellenmetriken

Definitionen der Custom-Metriken für Auto-Loader-Streaming-Datenquellen.

| Feld | Beschreibung |
| --- | --- |
| `sources.<startOffset / endOffset / latestOffset>.seqNum` | Die aktuelle Position in der Sequenz der verarbeiteten Dateien, in der Reihenfolge, in der die Dateien entdeckt wurden. |
| `sources.<startOffset / endOffset / latestOffset>.sourceVersion` | Die Implementierungsversion der cloudFiles-Quelle. |
| `sources.<startOffset / endOffset / latestOffset>.lastBackfillStartTimeMs` | Die Startzeit des letzten Backfill-Vorgangs. |
| `sources.<startOffset / endOffset / latestOffset>.lastBackfillFinishTimeMs` | Die Endzeit des letzten Backfill-Vorgangs. |
| `sources.<startOffset / endOffset / latestOffset>.lastInputPath` | Der zuletzt vom Benutzer angegebene Eingabepfad des Streams vor dessen Neustart. |
| `sources.metrics.numFilesOutstanding` | Die Anzahl der Dateien im Backlog. |
| `sources.metrics.numBytesOutstanding` | Die Größe (in Bytes) der Dateien im Backlog. |
| `sources.metrics.approximateQueueSize` | Die ungefähre Größe der Nachrichtenwarteschlange. Nur relevant, wenn die Option `cloudFiles.useNotifications` aktiviert ist. |
| `sources.numInputRows` | Die Anzahl der aus dieser Quelle verarbeiteten Eingabezeilen. Beim `binaryFile`-Quellformat entspricht `numInputRows` der Anzahl der Dateien. |

### PubSub-Quellenmetriken

Definitionen der Custom-Metriken für PubSub-Streaming-Datenquellen.

| Feld | Beschreibung |
| --- | --- |
| `sources.<startOffset / endOffset / latestOffset>.sourceVersion` | Die Implementierungsversion, mit der dieser Offset kodiert ist. |
| `sources.<startOffset / endOffset / latestOffset>.seqNum` | Die persistierte, aktuell verarbeitete Sequenznummer. |
| `sources.<startOffset / endOffset / latestOffset>.fetchEpoch` | Die größte gerade verarbeitete Fetch-Epoche. |
| `sources.metrics.numRecordsReadyToProcess` | Die Anzahl der zur Verarbeitung verfügbaren Datensätze im aktuellen Backlog. |
| `sources.metrics.sizeOfRecordsReadyToProcess` | Die Gesamtgröße in Bytes der unverarbeiteten Daten im aktuellen Backlog. |
| `sources.metrics.numDuplicatesSinceStreamStart` | Die Gesamtzahl der seit Streamstart verarbeiteten Duplikat-Datensätze. |

### Pulsar-Quellenmetriken

Definitionen der Custom-Metriken für Pulsar-Streaming-Datenquellen.

| Feld | Beschreibung |
| --- | --- |
| `sources.metrics.numInputRows` | Die Anzahl der im aktuellen Micro-Batch verarbeiteten Zeilen. |
| `sources.metrics.numInputBytes` | Die im aktuellen Micro-Batch insgesamt verarbeitete Anzahl an Bytes. |

## <a id="sink">12. sink-Objekt</a>

**Objekttyp**: `SinkProgress`

| Feld | Beschreibung |
| --- | --- |
| `sink.description` | Die Beschreibung der Senke, mit Details zur konkret verwendeten Senken-Implementierung. |
| `sink.numOutputRows` | Die Anzahl der Ausgabezeilen. Je nach Senkentyp können sich Verhalten oder Einschränkungen der Werte unterscheiden — siehe die konkret unterstützten Typen. |
| `sink.metrics` | `ju.Map[String, String]` mit Senken-Metriken. |

Databricks stellt aktuell zwei konkrete `sink`-Objekt-Implementierungen bereit:

| Senkentyp | Details |
| --- | --- |
| Delta-Lake-Tabelle | Siehe Delta-sink-Objekt. |
| Apache-Kafka-Topic | Siehe Kafka-sink-Objekt. |

Das Feld `sink.metrics` verhält sich bei beiden Varianten des `sink`-Objekts gleich.

### Delta-Lake-sink-Objekt

| Feld | Beschreibung |
| --- | --- |
| `sink.description` | Die Beschreibung der Delta-Senke, mit Details zur konkret verwendeten Delta-Senken-Implementierung. Beispiel: `"DeltaSink[table]"`. |
| `sink.numOutputRows` | Die Anzahl der Zeilen ist immer `-1`, da Spark für DSv1-Senken — die Klassifizierung der Delta-Lake-Senke — keine Ausgabezeilen ableiten kann. |

### Apache-Kafka-sink-Objekt

| Feld | Beschreibung |
| --- | --- |
| `sink.description` | Die Beschreibung der Kafka-Senke, in die die Streaming-Query schreibt, mit Details zur konkret verwendeten Kafka-Senken-Implementierung. Beispiel: `"org.apache.spark.sql.kafka010.KafkaSourceProvider$KafkaTable@e04b100"`. |
| `sink.numOutputRows` | Die Anzahl der Zeilen, die im Rahmen des Micro-Batches in die Ausgabetabelle bzw. Senke geschrieben wurden. In manchen Situationen kann dieser Wert "-1" sein, was allgemein als "unbekannt" zu interpretieren ist. |

## <a id="beispiele">13. Beispiele</a>

### Beispiel: Kafka-zu-Kafka-StreamingQueryListener-Event

```python
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
    "addBatch" : 18352,
    "getBatch" : 0,
    "latestOffset" : 31,
    "queryPlanning" : 977,
    "triggerExecution" : 20165,
    "walCommit" : 342
  },
  "eventTime" : {
    "avg" : "2022-10-31T20:09:18.070Z",
    "max" : "2022-10-31T20:09:30.125Z",
    "min" : "2022-10-31T20:09:09.793Z",
    "watermark" : "2022-10-31T20:08:46.355Z"
  },
  "stateOperators" : [ {
    "operatorName" : "stateStoreSave",
    "numRowsTotal" : 208,
    "numRowsUpdated" : 73,
    "allUpdatesTimeMs" : 434,
    "numRowsRemoved" : 76,
    "allRemovalsTimeMs" : 515,
    "commitTimeMs" : 0,
    "memoryUsedBytes" : 167069743,
    "numRowsDroppedByWatermark" : 0,
    "numShufflePartitions" : 20,
    "numStateStoreInstances" : 20,
    "customMetrics" : {
      "SnapshotLastUploaded.partition_0_default" : 1370,
      "SnapshotLastUploaded.partition_1_default" : 1370,
      "SnapshotLastUploaded.partition_2_default" : 1362,
      "SnapshotLastUploaded.partition_3_default" : 1370,
      "SnapshotLastUploaded.partition_4_default" : 1356,
      "rocksdbBytesCopied" : 0,
      "rocksdbCommitCheckpointLatency" : 0,
      "rocksdbCommitCompactLatency" : 0,
      "rocksdbCommitFileSyncLatencyMs" : 0,
      "rocksdbCommitFlushLatency" : 0,
      "rocksdbCommitPauseLatency" : 0,
      "rocksdbCommitWriteBatchLatency" : 0,
      "rocksdbFilesCopied" : 0,
      "rocksdbFilesReused" : 0,
      "rocksdbGetCount" : 222,
      "rocksdbGetLatency" : 0,
      "rocksdbPutCount" : 0,
      "rocksdbPutLatency" : 0,
      "rocksdbReadBlockCacheHitCount" : 165,
      "rocksdbReadBlockCacheMissCount" : 41,
      "rocksdbSstFileSize" : 232729,
      "rocksdbTotalBytesRead" : 12844,
      "rocksdbTotalBytesReadByCompaction" : 0,
      "rocksdbTotalBytesReadThroughIterator" : 161238,
      "rocksdbTotalBytesWritten" : 0,
      "rocksdbTotalBytesWrittenByCompaction" : 0,
      "rocksdbTotalCompactionLatencyMs" : 0,
      "rocksdbTotalFlushLatencyMs" : 0,
      "rocksdbWriterStallLatencyMs" : 0,
      "rocksdbZipFileBytesUncompressed" : 0
    }
  }, {
    "operatorName" : "dedupe",
    "numRowsTotal" : 2454744,
    "numRowsUpdated" : 73,
    "allUpdatesTimeMs" : 4155,
    "numRowsRemoved" : 0,
    "allRemovalsTimeMs" : 0,
    "commitTimeMs" : 0,
    "memoryUsedBytes" : 137765341,
    "numRowsDroppedByWatermark" : 34,
    "numShufflePartitions" : 20,
    "numStateStoreInstances" : 20,
    "customMetrics" : {
      "SnapshotLastUploaded.partition_0_default" : 1360,
      "SnapshotLastUploaded.partition_1_default" : 1360,
      "SnapshotLastUploaded.partition_2_default" : 1352,
      "SnapshotLastUploaded.partition_3_default" : 1360,
      "SnapshotLastUploaded.partition_4_default" : 1346,
      "numDroppedDuplicateRows" : 193,
      "rocksdbBytesCopied" : 0,
      "rocksdbCommitCheckpointLatency" : 0,
      "rocksdbCommitCompactLatency" : 0,
      "rocksdbCommitFileSyncLatencyMs" : 0,
      "rocksdbCommitFlushLatency" : 0,
      "rocksdbCommitPauseLatency" : 0,
      "rocksdbCommitWriteBatchLatency" : 0,
      "rocksdbFilesCopied" : 0,
      "rocksdbFilesReused" : 0,
      "rocksdbGetCount" : 146,
      "rocksdbGetLatency" : 0,
      "rocksdbPutCount" : 0,
      "rocksdbPutLatency" : 0,
      "rocksdbReadBlockCacheHitCount" : 3,
      "rocksdbReadBlockCacheMissCount" : 3,
      "rocksdbSstFileSize" : 78959140,
      "rocksdbTotalBytesRead" : 0,
      "rocksdbTotalBytesReadByCompaction" : 0,
      "rocksdbTotalBytesReadThroughIterator" : 0,
      "rocksdbTotalBytesWritten" : 0,
      "rocksdbTotalBytesWrittenByCompaction" : 0,
      "rocksdbTotalCompactionLatencyMs" : 0,
      "rocksdbTotalFlushLatencyMs" : 0,
      "rocksdbWriterStallLatencyMs" : 0,
      "rocksdbZipFileBytesUncompressed" : 0
    }
  }, {
    "operatorName" : "symmetricHashJoin",
    "numRowsTotal" : 2583,
    "numRowsUpdated" : 682,
    "allUpdatesTimeMs" : 9645,
    "numRowsRemoved" : 508,
    "allRemovalsTimeMs" : 46,
    "commitTimeMs" : 21,
    "memoryUsedBytes" : 668544484,
    "numRowsDroppedByWatermark" : 0,
    "numShufflePartitions" : 20,
    "numStateStoreInstances" : 80,
    "customMetrics" : {
      "SnapshotLastUploaded.partition_0_left-keyToNumValues" : 1310,
      "SnapshotLastUploaded.partition_1_left-keyWithIndexToValue" : 1318,
      "SnapshotLastUploaded.partition_2_left-keyToNumValues" : 1305,
      "SnapshotLastUploaded.partition_2_right-keyWithIndexToValue" : 1306,
      "SnapshotLastUploaded.partition_4_left-keyWithIndexToValue" : 1310,
      "rocksdbBytesCopied" : 0,
      "rocksdbCommitCheckpointLatency" : 0,
      "rocksdbCommitCompactLatency" : 0,
      "rocksdbCommitFileSyncLatencyMs" : 0,
      "rocksdbCommitFlushLatency" : 0,
      "rocksdbCommitPauseLatency" : 0,
      "rocksdbCommitWriteBatchLatency" : 0,
      "rocksdbFilesCopied" : 0,
      "rocksdbFilesReused" : 0,
      "rocksdbGetCount" : 4218,
      "rocksdbGetLatency" : 3,
      "rocksdbPutCount" : 0,
      "rocksdbPutLatency" : 0,
      "rocksdbReadBlockCacheHitCount" : 3425,
      "rocksdbReadBlockCacheMissCount" : 149,
      "rocksdbSstFileSize" : 742827,
      "rocksdbTotalBytesRead" : 866864,
      "rocksdbTotalBytesReadByCompaction" : 0,
      "rocksdbTotalBytesReadThroughIterator" : 0,
      "rocksdbTotalBytesWritten" : 0,
      "rocksdbTotalBytesWrittenByCompaction" : 0,
      "rocksdbTotalCompactionLatencyMs" : 0,
      "rocksdbTotalFlushLatencyMs" : 0,
      "rocksdbWriterStallLatencyMs" : 0,
      "rocksdbZipFileBytesUncompressed" : 0
    }
  } ],
  "sources" : [ {
    "description" : "KafkaV2[Subscribe[KAFKA_TOPIC_NAME_INPUT_A]]",
    "startOffset" : {
      "KAFKA_TOPIC_NAME_INPUT_A" : {
        "0" : 349706380
      }
    },
    "endOffset" : {
      "KAFKA_TOPIC_NAME_INPUT_A" : {
        "0" : 349706672
      }
    },
    "latestOffset" : {
      "KAFKA_TOPIC_NAME_INPUT_A" : {
        "0" : 349706672
      }
    },
    "numInputRows" : 292,
    "inputRowsPerSecond" : 13.65826278123392,
    "processedRowsPerSecond" : 14.479817514628582,
    "metrics" : {
      "avgOffsetsBehindLatest" : "0.0",
      "estimatedTotalBytesBehindLatest" : "0.0",
      "maxOffsetsBehindLatest" : "0",
      "minOffsetsBehindLatest" : "0"
    }
  }, {
    "description" : "KafkaV2[Subscribe[KAFKA_TOPIC_NAME_INPUT_B]]",
    "startOffset" : {
      KAFKA_TOPIC_NAME_INPUT_B" : {
        "2" : 143147812,
        "1" : 129288266,
        "0" : 138102966
      }
    },
    "endOffset" : {
      "KAFKA_TOPIC_NAME_INPUT_B" : {
        "2" : 143147812,
        "1" : 129288266,
        "0" : 138102966
      }
    },
    "latestOffset" : {
      "KAFKA_TOPIC_NAME_INPUT_B" : {
        "2" : 143147812,
        "1" : 129288266,
        "0" : 138102966
      }
    },
    "numInputRows" : 0,
    "inputRowsPerSecond" : 0.0,
    "processedRowsPerSecond" : 0.0,
    "metrics" : {
      "avgOffsetsBehindLatest" : "0.0",
      "maxOffsetsBehindLatest" : "0",
      "minOffsetsBehindLatest" : "0"
    }
  } ],
  "sink" : {
    "description" : "org.apache.spark.sql.kafka010.KafkaSourceProvider$KafkaTable@e04b100",
    "numOutputRows" : 76
  }
}
```

### Beispiel: Delta-Lake-zu-Delta-Lake-StreamingQueryListener-Event

```python
{
  "id" : "aeb6bc0f-3f7d-4928-a078-ba2b304e2eaf",
  "runId" : "35d751d9-2d7c-4338-b3de-6c6ae9ebcfc2",
  "name" : "silverTransformFromBronze",
  "timestamp" : "2022-11-01T18:21:29.500Z",
  "batchId" : 4,
  "numInputRows" : 0,
  "inputRowsPerSecond" : 0.0,
  "processedRowsPerSecond" : 0.0,
  "durationMs" : {
    "latestOffset" : 62,
    "triggerExecution" : 62
  },
  "stateOperators" : [ ],
  "sources" : [ {
    "description" : "DeltaSource[dbfs:/FileStore/<user>/stateful-trade-analysis-demo/table]",
    "startOffset" : {
      "sourceVersion" : 1,
      "reservoirId" : "84590dac-da51-4e0f-8eda-6620198651a9",
      "reservoirVersion" : 3216,
      "index" : 3214,
      "isStartingVersion" : true
    },
    "endOffset" : {
      "sourceVersion" : 1,
      "reservoirId" : "84590dac-da51-4e0f-8eda-6620198651a9",
      "reservoirVersion" : 3216,
      "index" : 3214,
      "isStartingVersion" : true
    },
    "latestOffset" : null,
    "numInputRows" : 0,
    "inputRowsPerSecond" : 0.0,
    "processedRowsPerSecond" : 0.0,
    "metrics" : {
      "numBytesOutstanding" : "0",
      "numFilesOutstanding" : "0"
    }
  } ],
  "sink" : {
    "description" : "DeltaSink[dbfs:/user/hive/warehouse/<user>.db/trade_history_silver_delta_demo2]",
    "numOutputRows" : -1
  }
}
```

### Beispiel: Kinesis-zu-Delta-Lake-StreamingQueryListener-Event

```python
{
  "id" : "3ce9bd93-da16-4cb3-a3b6-e97a592783b5",
  "runId" : "fe4a6bda-dda2-4067-805d-51260d93260b",
  "name" : null,
  "timestamp" : "2024-05-14T02:09:20.846Z",
  "batchId" : 0,
  "batchDuration" : 59322,
  "numInputRows" : 20,
  "inputRowsPerSecond" : 0.0,
  "processedRowsPerSecond" : 0.33714304979602844,
  "durationMs" : {
    "addBatch" : 5397,
    "commitBatch" : 4429,
    "commitOffsets" : 211,
    "getBatch" : 5,
    "latestOffset" : 21998,
    "queryPlanning" : 12128,
    "triggerExecution" : 59313,
    "walCommit" : 220
  },
  "stateOperators" : [ ],
  "sources" : [ {
    "description" : "KinesisV2[KinesisTestUtils-7199466178786508570-at-1715652545256]",
    "startOffset" : null,
    "endOffset" : [ {
      "shard" : {
        "stream" : "KinesisTestUtils-7199466178786508570-at-1715652545256",
        "shardId" : "shardId-000000000000"
      },
      "firstSeqNum" : "49652022592149344892294981243280420130985816456924495874",
      "lastSeqNum" : "49652022592149344892294981243290091537542733559041622018",
      "closed" : false,
      "msBehindLatest" : "0",
      "lastRecordSeqNum" : "49652022592149344892294981243290091537542733559041622018"
    }, {
      "shard" : {
        "stream" : "KinesisTestUtils-7199466178786508570-at-1715652545256",
        "shardId" : "shardId-000000000001"
      },
      "firstSeqNum" : "49652022592171645637493511866421955849258464818430476306",
      "lastSeqNum" : "49652022592171645637493511866434045107454611178897014802",
      "closed" : false,
      "msBehindLatest" : "0",
      "lastRecordSeqNum" : "49652022592171645637493511866434045107454611178897014802"
    } ],
    "latestOffset" : null,
    "numInputRows" : 20,
    "inputRowsPerSecond" : 0.0,
    "processedRowsPerSecond" : 0.33714304979602844,
    "metrics" : {
      "avgMsBehindLatest" : "0.0",
      "maxMsBehindLatest" : "0",
      "minMsBehindLatest" : "0",
      "mode" : "efo",
      "numClosedShards" : "0",
      "numProcessedBytes" : "30",
      "numProcessedRecords" : "18",
      "numRegisteredConsumers" : "1",
      "numStreams" : "1",
      "numTotalShards" : "2",
      "totalPrefetchedBytes" : "0"
    }
  } ],
  "sink" : {
    "description" : "DeltaSink[dbfs:/streaming/test/KinesisToDeltaServerlessLiteSuite/<run-id>/deltaTable]",
    "numOutputRows" : -1
  }
}
```

### Beispiel: Kafka+Delta-Lake-zu-Delta-Lake-StreamingQueryListener-Event

```python
{
 "id" : "210f4746-7caa-4a51-bd08-87cabb45bdbe",
 "runId" : "42a2f990-c463-4a9c-9aae-95d6990e63f4",
 "name" : null,
 "timestamp" : "2024-05-15T21:57:50.782Z",
 "batchId" : 0,
 "batchDuration" : 3601,
 "numInputRows" : 20,
 "inputRowsPerSecond" : 0.0,
 "processedRowsPerSecond" : 5.55401277422938,
 "durationMs" : {
  "addBatch" : 1544,
  "commitBatch" : 686,
  "commitOffsets" : 27,
  "getBatch" : 12,
  "latestOffset" : 577,
  "queryPlanning" : 105,
  "triggerExecution" : 3600,
  "walCommit" : 34
 },
 "stateOperators" : [ {
  "operatorName" : "symmetricHashJoin",
  "numRowsTotal" : 20,
  "numRowsUpdated" : 20,
  "allUpdatesTimeMs" : 473,
  "numRowsRemoved" : 0,
  "allRemovalsTimeMs" : 0,
  "commitTimeMs" : 277,
  "memoryUsedBytes" : 13120,
  "numRowsDroppedByWatermark" : 0,
  "numShufflePartitions" : 5,
  "numStateStoreInstances" : 20,
  "customMetrics" : {
   "loadedMapCacheHitCount" : 0,
   "loadedMapCacheMissCount" : 0,
   "stateOnCurrentVersionSizeBytes" : 5280
  }
 } ],
 "sources" : [ {
  "description" : "KafkaV2[Subscribe[topic-1]]",
  "startOffset" : null,
  "endOffset" : {
   "topic-1" : {
    "1" : 5,
    "0" : 5
   }
  },
  "latestOffset" : {
   "topic-1" : {
    "1" : 5,
    "0" : 5
   }
  },
  "numInputRows" : 10,
  "inputRowsPerSecond" : 0.0,
  "processedRowsPerSecond" : 2.77700638711469,
  "metrics" : {
   "avgOffsetsBehindLatest" : "0.0",
   "estimatedTotalBytesBehindLatest" : "0.0",
   "maxOffsetsBehindLatest" : "0",
   "minOffsetsBehindLatest" : "0"
  }
 }, {
  "description" : "DeltaSource[file:/tmp/spark-1b7cb042-bab8-4469-bb2f-733c15141081]",
  "startOffset" : null,
  "endOffset" : {
   "sourceVersion" : 1,
   "reservoirId" : "b207a1cd-0fbe-4652-9c8f-e5cc467ae84f",
   "reservoirVersion" : 1,
   "index" : -1,
   "isStartingVersion" : false
  },
  "latestOffset" : null,
  "numInputRows" : 10,
  "inputRowsPerSecond" : 0.0,
  "processedRowsPerSecond" : 2.77700638711469,
  "metrics" : {
   "numBytesOutstanding" : "0",
   "numFilesOutstanding" : "0"
  }
 } ],
 "sink" : {
  "description" : "DeltaSink[/tmp/spark-d445c92a-4640-4827-a9bd-47246a30bb04]",
  "numOutputRows" : -1
 }
}
```

### Beispiel: Rate-Source-zu-Delta-Lake-StreamingQueryListener-Event

```python
{
  "id" : "912ebdc1-edf2-48ec-b9fb-1a9b67dd2d9e",
  "runId" : "85de73a5-92cc-4b7f-9350-f8635b0cf66e",
  "name" : "dataGen",
  "timestamp" : "2022-11-01T18:28:20.332Z",
  "batchId" : 279,
  "numInputRows" : 300,
  "inputRowsPerSecond" : 114.15525114155251,
  "processedRowsPerSecond" : 158.9825119236884,
  "durationMs" : {
    "addBatch" : 1771,
    "commitOffsets" : 54,
    "getBatch" : 0,
    "latestOffset" : 0,
    "queryPlanning" : 4,
    "triggerExecution" : 1887,
    "walCommit" : 58
  },
  "stateOperators" : [ ],
  "sources" : [ {
    "description" : "RateStreamV2[rowsPerSecond=100, rampUpTimeSeconds=0, numPartitions=default",
    "startOffset" : 560,
    "endOffset" : 563,
    "latestOffset" : 563,
    "numInputRows" : 300,
    "inputRowsPerSecond" : 114.15525114155251,
    "processedRowsPerSecond" : 158.9825119236884
  } ],
  "sink" : {
    "description" : "DeltaSink[dbfs:/user/hive/warehouse/<user>.db/trade_history_bronze_delta_demo]",
    "numOutputRows" : -1
  }
}
```

**Stand:** Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
