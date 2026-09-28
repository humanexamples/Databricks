# Stateful Streaming — Referenz

Dieses Dokument erklärt zustandsbehaftete ("stateful") Structured-Streaming-Queries, einschließlich zustandsbehafteter Operationen, Optimierungsempfehlungen, dem Verketten mehrerer zustandsbehafteter Operatoren und State Rebalancing. Verifiziert per `WebFetch` gegen die GCP-Original-URL sowie ergänzend gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/stateful-streaming`), die eine vollständige, wörtliche Wiedergabe des Roh-Inhalts lieferte.

## Abschnittsübersicht
1. [Definition](#definition)
2. [Zustandsbehaftete Operationen](#stateful-operations)
3. [Zustandsbehaftete Structured-Streaming-Queries optimieren](#optimierung)
4. [Mehrere zustandsbehaftete Operatoren in Structured Streaming kombinieren](#mehrere-operatoren)
5. [State Rebalancing für Structured Streaming](#state-rebalancing)
6. [Quellen](#quellen)

---

## <a id="definition">1. Definition</a>

Eine *zustandsbehaftete* ("stateful") Structured-Streaming-Query benötigt inkrementelle Aktualisierungen von Zwischenzustandsinformationen, während eine *zustandslose* ("stateless") Structured-Streaming-Query lediglich nachverfolgt, welche Zeilen von der Quelle bis zur Senke bereits verarbeitet wurden. Für Optimierungsfunktionen zustandsloser Queries siehe das Dokument "Stateless Streaming".

## <a id="stateful-operations">2. Zustandsbehaftete Operationen</a>

Zu den zustandsbehafteten Operationen zählen Streaming-Aggregation, `distinct`, `dropDuplicates`, Stream-Stream-Joins sowie benutzerdefinierte zustandsbehaftete Anwendungen.

Die für zustandsbehaftete Structured-Streaming-Queries erforderlichen Zwischenzustandsinformationen können bei fehlerhafter Konfiguration zu unerwarteter Latenz und Produktionsproblemen führen.

In Databricks Runtime 13.3 LTS oder höher kann Changelog-Checkpointing mit RocksDB aktiviert werden, um die Checkpoint-Dauer und die End-to-End-Latenz für Structured-Streaming-Workloads zu senken. Databricks empfiehlt, Changelog-Checkpointing für alle zustandsbehafteten Structured-Streaming-Queries zu aktivieren (siehe die Dokumentation zum Aktivieren von Changelog-Checkpointing im RocksDB-State-Store).

## <a id="optimierung">3. Zustandsbehaftete Structured-Streaming-Queries optimieren</a>

Databricks empfiehlt für zustandsbehaftete Structured-Streaming-Queries Folgendes:

- Compute-optimierte Instanztypen als Worker verwenden.
- Die Anzahl der Shuffle-Partitionen auf das 1- bis 2-Fache der Anzahl der Cluster-Cores setzen.

**Wichtig:** Die Anzahl der Shuffle-Partitionen wird zum Zeitpunkt der Checkpoint-Erstellung festgelegt. Eine Änderung von `spark.sql.shuffle.partitions` hat keine Auswirkung auf eine Streaming-Query, die bereits über einen Checkpoint verfügt — die Query verwendet weiterhin die ursprüngliche Partitionsanzahl. Um eine neue Partitionsanzahl anzuwenden, muss die Query mit einem neuen Checkpoint-Pfad gestartet werden.

In Databricks Runtime 18.0 und höher unterstützen zustandslose Streaming-Queries dynamische Änderungen der Shuffle-Partitionen, ohne dass ein neuer Checkpoint erforderlich ist.

In Databricks Runtime 18 LTS und höher kann die Partitionsanzahl für zustandsbehaftete Queries geändert werden, ohne den Checkpoint-Zustand zu verlieren (siehe das Dokument "State Repartitionierung").

- Die Konfiguration `spark.sql.streaming.noDataMicroBatches.enabled` in der SparkSession auf `false` setzen. Dies verhindert, dass die Streaming-Micro-Batch-Engine Micro-Batches verarbeitet, die keine Daten enthalten. Wird diese Konfiguration auf `false` gesetzt, kann dies auch dazu führen, dass zustandsbehaftete Operationen, die Watermarks oder Verarbeitungszeit-Timeouts verwenden, erst dann eine Ausgabe erzeugen, wenn neue Daten eintreffen, statt sofort.

Databricks empfiehlt, RocksDB mit Changelog-Checkpointing zu verwenden, um den Zustand für zustandsbehaftete Streams zu verwalten (siehe die Dokumentation zur Konfiguration des RocksDB-State-Stores).

**Hinweis:** Das State-Management-Schema kann zwischen Query-Neustarts nicht geändert werden. Wurde eine Query mit dem Standard-Management gestartet, muss sie von Grund auf mit einem neuen Checkpoint-Pfad neu gestartet werden, um den State Store zu ändern.

## <a id="mehrere-operatoren">4. Mehrere zustandsbehaftete Operatoren in Structured Streaming kombinieren</a>

In Databricks Runtime 13.3 LTS oder höher bietet Databricks erweiterte Unterstützung für zustandsbehaftete Operatoren in Structured-Streaming-Workloads. Mehrere zustandsbehaftete Operatoren können verkettet werden, das heißt, die Ausgabe einer Operation — etwa einer gefensterten Aggregation — kann als Eingabe einer weiteren zustandsbehafteten Operation dienen, etwa eines Joins.

In Databricks Runtime 16.2 oder höher kann `transformWithState` in Workloads mit mehreren zustandsbehafteten Operatoren verwendet werden (siehe die Dokumentation zum Erstellen einer benutzerdefinierten zustandsbehafteten Anwendung mit `transformWithState`).

Die folgenden Beispiele zeigen mehrere unterstützte Muster.

**Wichtig — Einschränkungen bei mehreren zustandsbehafteten Operatoren:**

- Legacy-benutzerdefinierte zustandsbehaftete Operatoren (`FlatMapGroupWithState` und `applyInPandasWithState`) werden nicht unterstützt.
- Nur der Append-Output-Modus wird unterstützt.

### Verkettete Zeitfenster-Aggregation

#### Python

```python
words = ...  # streaming DataFrame of schema { timestamp: Timestamp, word: String }

# Group the data by window and word and compute the count of each group
windowedCounts = words.groupBy(
    window(words.timestamp, "10 minutes", "5 minutes"),
    words.word
).count()

# Group the windowed data by another window and word and compute the count of each group
anotherWindowedCounts = windowedCounts.groupBy(
    window(window_time(windowedCounts.window), "1 hour"),
    windowedCounts.word
).count()
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import spark.implicits._

val words = ... // streaming DataFrame of schema { timestamp: Timestamp, word: String }

// Group the data by window and word and compute the count of each group
val windowedCounts = words.groupBy(
  window($"timestamp", "10 minutes", "5 minutes"),
  $"word"
).count()

// Group the windowed data by another window and word and compute the count of each group
val anotherWindowedCounts = windowedCounts.groupBy(
  window($"window", "1 hour"),
  $"word"
).count()
```

### Zeitfenster-Aggregation in zwei unterschiedlichen Streams, gefolgt von einem Stream-Stream-Window-Join

#### Python

```python
clicksWindow = clicksWithWatermark.groupBy(
  clicksWithWatermark.clickAdId,
  window(clicksWithWatermark.clickTime, "1 hour")
).count()

impressionsWindow = impressionsWithWatermark.groupBy(
  impressionsWithWatermark.impressionAdId,
  window(impressionsWithWatermark.impressionTime, "1 hour")
).count()

clicksWindow.join(impressionsWindow, "window", "inner")
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
val clicksWindow = clicksWithWatermark
  .groupBy(window("clickTime", "1 hour"))
  .count()

val impressionsWindow = impressionsWithWatermark
  .groupBy(window("impressionTime", "1 hour"))
  .count()

clicksWindow.join(impressionsWindow, "window", "inner")
```

### Stream-Stream-Zeitintervall-Join, gefolgt von einer Zeitfenster-Aggregation

#### Python

```python
joined = impressionsWithWatermark.join(
  clicksWithWatermark,
  expr("""
    clickAdId = impressionAdId AND
    clickTime >= impressionTime AND
    clickTime <= impressionTime + interval 1 hour
    """),
  "leftOuter"                 # can be "inner", "leftOuter", "rightOuter", "fullOuter", "leftSemi"
)

joined.groupBy(
  joined.clickAdId,
  window(joined.clickTime, "1 hour")
).count()
```

## <a id="state-rebalancing">5. State Rebalancing für Structured Streaming</a>

State Rebalancing ist standardmäßig für alle Streaming-Workloads in Lakeflow-Pipelines aktiviert. In Databricks Runtime 11.3 LTS oder höher kann folgende Konfigurationsoption in der Spark-Cluster-Konfiguration gesetzt werden, um State Rebalancing zu aktivieren:

```ini
spark.sql.streaming.statefulOperator.stateRebalancing.enabled true
```

State Rebalancing kommt zustandsbehafteten Structured-Streaming-Pipelines zugute, die Cluster-Resizing-Ereignisse durchlaufen. Zustandslose Streaming-Operationen profitieren davon nicht, unabhängig von Änderungen der Cluster-Größe.

**Hinweis:** Compute-Autoscaling hat Einschränkungen beim Herunterskalieren der Cluster-Größe für Structured-Streaming-Workloads. Databricks empfiehlt, für Streaming-Workloads Spark Declarative Pipelines auf Lakeflow mit Enhanced Autoscaling zu verwenden (siehe die Dokumentation zur Optimierung der Lakeflow-Pipeline-Cluster-Auslastung mit Autoscaling).

Cluster-Resizing-Ereignisse lösen State Rebalancing aus. Micro-Batches können während Rebalancing-Ereignissen eine höhere Latenz aufweisen, da der Zustand vom Cloud-Speicher auf die neuen Executor geladen wird.

---

## <a id="quellen">6. Quellen</a>
- What is stateful streaming? (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/stateful-streaming
- What is stateful streaming? (Mirror, verifiziert/vollständig abgerufen, Azure): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/stateful-streaming

**Stand:** 2026-08-22; Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
