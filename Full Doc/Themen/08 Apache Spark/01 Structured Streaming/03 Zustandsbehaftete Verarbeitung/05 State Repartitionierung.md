# State Repartitionierung — Referenz

Dieses Dokument beschreibt das On-Demand State Repartitioning für zustandsbehaftete ("stateful") Structured-Streaming-Queries: das Ändern der Partitionsanzahl ohne Verlust des Checkpoint-Zustands. Verifiziert per `WebFetch` gegen die GCP-Original-URL sowie ergänzend gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/state-repartitioning`), die eine vollständige, wörtliche Wiedergabe des Roh-Inhalts lieferte.

## Abschnittsübersicht
1. [Überblick](#ueberblick)
2. [Voraussetzungen](#voraussetzungen)
3. [Die Anzahl der Partitionen ändern](#partitionen-aendern)
4. [Repartitionierungsstatus überwachen](#monitoring)
5. [Structured-Streaming-Beispiel](#beispiel-structured-streaming)
6. [Lakeflow-Pipelines-Beispiel](#beispiel-lakeflow)
7. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick</a>

**Wichtig:** Diese Funktion befindet sich in der Public Preview.

On-Demand State Repartitioning ermöglicht es, die Anzahl der Partitionen einer zustandsbehafteten Structured-Streaming-Query anzupassen, ohne den Checkpoint-Zustand zu verlieren.

Ohne On-Demand State Repartitioning wird die Anzahl der Shuffle-Partitionen bei der Checkpoint-Erstellung festgelegt. Wird `spark.sql.shuffle.partitions` geändert, ignorieren Queries mit bestehenden Checkpoints den neuen Wert. Um eine neue Partitionsanzahl anzuwenden, musste die Query bislang mit einem neuen Checkpoint neu gestartet werden.

On-Demand State Repartitioning bietet folgende Vorteile:

- Queries lassen sich durch Anpassung der Partitionsanzahl optimieren, ohne den Checkpoint neu aufzubauen.
- Queries lassen sich hoch- oder herunterskalieren, um sich an veränderte Workloads anzupassen.

## <a id="voraussetzungen">2. Voraussetzungen</a>

- Databricks Runtime 18 LTS und höher.
- Die Query muss den RocksDB-State-Store-Provider verwenden. Ab DBR 17.3 ist RocksDB der Standard-State-Store-Provider (siehe die Dokumentation zur Konfiguration des RocksDB-State-Stores).

## <a id="partitionen-aendern">3. Die Anzahl der Partitionen ändern</a>

Über die Spark-Konfiguration `spark.sql.streaming.stateStore.partitions` lässt sich nach einem Neustart der Query die Anzahl der Shuffle- und Streaming-State-Partitionen ändern:

### Python

```python
query.stop()
spark.conf.set("spark.sql.streaming.stateStore.partitions", "<numPartitions>")
query = df.writeStream.start()
```

Für zustandsbehaftete Queries hat `spark.sql.streaming.stateStore.partitions` Vorrang vor `spark.sql.shuffle.partitions`. Nach dem Neustart der Query und dem Abschluss des zuletzt geplanten Micro-Batches führt die Query eine Repartitionierungsoperation aus, um die Zustandsdaten auf die neue Partitionsanzahl umzuverteilen. Nach Abschluss der Repartitionierungsoperation setzt die Query die Verarbeitung fort.

## <a id="monitoring">4. Repartitionierungsstatus überwachen</a>

Nach Abschluss des nächsten Micro-Batches enthalten die `StreamingQueryProgress`-Ereignisse die Dauer der Repartitionierungsoperation. In den `durationMs`-Metriken eines Ereignisses zeigt `controlBatch.REPARTITION` den Dauerwert in Millisekunden an. Größere Zustandsgrößen können die Repartitionierungsdauer erhöhen (siehe die Dokumentation zum Monitoring von Structured-Streaming-Queries).

## <a id="beispiel-structured-streaming">5. Structured-Streaming-Beispiel</a>

Das folgende Beispiel skaliert eine Query vom Standardwert 200 auf 100 Shuffle-Partitionen herunter. Dazu wird die Query gestoppt, die neue Partitionsanzahl gesetzt und die Query neu gestartet:

### Python

```python
# Start the query with the default partition count (200)
query = (df
  .withWatermark("event_time", "10 minutes")
  .groupBy(
    window("event_time", "5 minutes"),
    "id")
  .count()
  .writeStream
  .format("delta")
  .option("checkpointLocation", "/checkpoint/path")
  .outputMode("append")
  .start()
)

# Stop the query and scale down to 100 partitions
query.stop()

spark.conf.set("spark.sql.streaming.stateStore.partitions", "100")

# Restart the query with the same options
query = (df
  .withWatermark("event_time", "10 minutes")
  .groupBy(
    window("event_time", "5 minutes"),
    "id")
  .count()
  .writeStream
  .format("delta")
  .option("checkpointLocation", "/checkpoint/path")
  .outputMode("append")
  .start()
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
// Start the query with the default partition count (200)
val query = df
  .withWatermark("event_time", "10 minutes")
  .groupBy(
    window($"event_time", "5 minutes"),
    $"id")
  .count()
  .writeStream
  .format("delta")
  .option("checkpointLocation", "/checkpoint/path")
  .outputMode("append")
  .start()

// Stop the query and scale down to 100 partitions
query.stop()

spark.conf.set("spark.sql.streaming.stateStore.partitions", "100")

// Restart the query with the same options
val query2 = df
  .withWatermark("event_time", "10 minutes")
  .groupBy(
    window($"event_time", "5 minutes"),
    $"id")
  .count()
  .writeStream
  .format("delta")
  .option("checkpointLocation", "/checkpoint/path")
  .outputMode("append")
  .start()
```

## <a id="beispiel-lakeflow">6. Lakeflow-Pipelines-Beispiel</a>

In Lakeflow-Pipelines wird `spark.sql.streaming.stateStore.partitions` über den Parameter `spark_conf` des `@dp.table`- oder `@dp.append_flow`-Dekorators gesetzt.

Partitionen für einen Flow setzen:

```python
from pyspark import pipelines as dp
from pyspark.sql import functions as F

source_path = "/databricks-datasets/iot-stream/data-device/"

dp.create_streaming_table("target_table")

@dp.append_flow(
  target="target_table",
  name="my_flow_1",
  spark_conf={"spark.sql.streaming.stateStore.partitions": "100"}
)
def my_flow_1():
  return (spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "json")
    .load(source_path)
    .withColumn("timestamp", F.to_timestamp("timestamp"))
    .withWatermark("timestamp", "10 minutes")
    .groupBy(F.window("timestamp", "5 minutes"), "id")
    .count())
```

Partitionen auf Tabellenebene für den Default-Flow setzen:

```python
from pyspark import pipelines as dp
from pyspark.sql import functions as F

source_path = "/databricks-datasets/iot-stream/data-device/"

@dp.table(
  name="table_1",
  spark_conf={"spark.sql.streaming.stateStore.partitions": "100"}
)
def table_1():
  return (spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "json")
    .load(source_path)
    .withColumn("timestamp", F.to_timestamp("timestamp"))
    .withWatermark("timestamp", "10 minutes")
    .groupBy(F.window("timestamp", "5 minutes"), "id")
    .count())
```

---

## <a id="quellen">7. Quellen</a>
- On-demand state repartitioning for stateful streaming queries (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/state-repartitioning
- On-demand state repartitioning for stateful streaming queries (Mirror, verifiziert/vollständig abgerufen, Azure): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/state-repartitioning

**Stand:** 2026-08-22; Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
