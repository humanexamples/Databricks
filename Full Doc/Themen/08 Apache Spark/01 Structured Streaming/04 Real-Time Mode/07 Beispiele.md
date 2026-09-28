# Real-Time-Mode-Beispiele — Referenz

Dieses Dokument enthält lauffähige Code-Beispiele für Real-Time-Mode-Queries in Structured Streaming — von einfachen zustandslosen Transformationen bis zu komplexer zustandsbehafteter Verarbeitung mit benutzerdefiniertem State-Management. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/examples`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns inklusive korrekt formatierter Code-Blöcke lieferte (die GCP-Originalseite lieferte über WebFetch Code-Blöcke mit verlorenen Zeilenumbrüchen).

## Abschnittsübersicht

1. [Voraussetzungen](#voraussetzungen)
2. [Zustandslose Query-Beispiele](#zustandslose-beispiele)
3. [Zustandsbehaftete Query-Beispiele](#zustandsbehaftete-beispiele)
4. [Entwicklung und Testing](#entwicklung-testing)
5. [Beispiele für benutzerdefinierte Senken](#custom-sinks)
6. [Quellen](#quellen)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

Um die Beispiele auf dieser Seite auszuführen, wird Folgendes benötigt:

- Ein konfigurierter und laufender Real-Time-Mode-Cluster (siehe Datei `Setup.md` für Anforderungen und Konfiguration, oder Datei `Tutorial.md` für eine Schritt-für-Schritt-Anleitung).
- Grundlegende Vertrautheit mit Structured-Streaming-Konzepten (siehe die Doku-Seite "Structured Streaming concepts", falls neu im Thema Streaming).
- Zugriff auf unterstützte Streaming-Quellen und -Senken:
    - Für Kafka-Beispiele: ein Kafka-Broker mit konfigurierten Input-/Output-Topics.
    - Für Kinesis-Beispiele: AWS-Credentials und ein für Enhanced-Fan-Out-(EFO)-Modus konfigurierter Kinesis-Stream.
    - Für Lakebase-Beispiele: eine Lakebase-Datenbank (siehe Abschnitt "Requirements" der entsprechenden Doku für Anforderungen).
    - Für Beispiele mit benutzerdefinierten Senken: eine konfigurierte Ziel-Datenbank bzw. ein konfigurierter Zieldienst (im gegebenen Beispiel PostgreSQL).

**Hinweis:** Die Beispiele verwenden Platzhalterwerte wie `broker_address`, `input_topic` und `checkpoint_location`. Diese müssen vor dem Ausführen des Codes durch die tatsächlichen Konfigurationswerte ersetzt werden.

## <a id="zustandslose-beispiele">2. Zustandslose Query-Beispiele</a>

Zustandslose Queries verarbeiten jeden Datensatz unabhängig, ohne Zustand zwischen den Datensätzen zu halten. Diese Queries sind in der Regel einfacher und haben eine niedrigere Latenz als zustandsbehaftete Queries, da kein State-Storage verwaltet oder Lookups durchgeführt werden müssen. Zustandslose Queries eignen sich für Transformationen, Filterung, Joins mit statischen Daten und Routing-Operationen.

### Kafka-Quelle zu Kafka-Senke

In diesem Beispiel wird aus einer Kafka-Quelle gelesen und in eine Kafka-Senke geschrieben.

**Python:**

```python
query = (
    spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", broker_address)
        .option("startingOffsets", "earliest")
        .option("subscribe", input_topic)
        .load()
        .writeStream
        .format("kafka")
        .option("kafka.bootstrap.servers", broker_address)
        .option("topic", output_topic)
        .option("checkpointLocation", checkpoint_location)
        .trigger(realTime="5 minutes")
        .outputMode("update")
        .start()
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.streaming.OutputMode
import org.apache.spark.sql.execution.streaming.RealTimeTrigger

spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic)
      .load()
      .writeStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("topic", outputTopic)
      .option("checkpointLocation", checkpointLocation)
      .trigger(RealTimeTrigger.apply())
      .outputMode(OutputMode.Update())
      .start()
```

### Repartition

In diesem Beispiel wird aus einer Kafka-Quelle gelesen, die Daten werden auf 20 Partitionen repartitioniert und in eine Kafka-Senke geschrieben.

Aufgrund einer aktuellen Implementierungseinschränkung muss die Spark-Konfiguration `spark.sql.execution.sortBeforeRepartition` vor der Verwendung von `repartition` auf `false` gesetzt werden.

**Python:**

```python
# Sorting is not supported in repartition with real-time mode, so you must set this to false to achieve low latency.
spark.conf.set("spark.sql.execution.sortBeforeRepartition", "false")

query = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("subscribe", input_topic)
    .option("startingOffsets", "earliest")
    .load()
    .repartition(20)
    .writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("topic", output_topic)
    .option("checkpointLocation", checkpoint_location)
    .trigger(realTime="5 minutes")
    .outputMode("update")
    .start()
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.streaming.OutputMode
import org.apache.spark.sql.execution.streaming.RealTimeTrigger

// Sorting is not supported in repartition with real-time mode, so you must set this to false to achieve low latency.
spark.conf.set("spark.sql.execution.sortBeforeRepartition", "false")

spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic)
      .load()
      .repartition(20)
      .writeStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("topic", outputTopic)
      .option("checkpointLocation", checkpointLocation)
      .trigger(RealTimeTrigger.apply())
      .outputMode(OutputMode.Update())
      .start()
```

### Stream-Snapshot-Join (nur Broadcast)

In diesem Beispiel wird aus Kafka gelesen, die Daten werden mit einer statischen Tabelle gejoint und in eine Kafka-Senke geschrieben. Nur Stream-Static-Joins, die die statische Tabelle per Broadcast verteilen, werden unterstützt — das heißt, die statische Tabelle muss in den Speicher passen.

**Python:**

```python
from pyspark.sql.functions import broadcast, expr

# We assume the static table in the path `static_table_location` has a column 'lookupKey'.

query = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("subscribe", input_topic)
    .option("startingOffsets", "earliest")
    .load()
    .withColumn("joinKey", expr("CAST(value AS STRING)"))
    .join(
        broadcast(spark.read.format("parquet").load(static_table_location)),
        expr("joinKey = lookupKey")
    )
    .selectExpr("value AS key", "value")
    .writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("topic", output_topic)
    .option("checkpointLocation", checkpoint_location)
    .trigger(realTime="5 minutes")
    .outputMode("update")
    .start()
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.functions.{broadcast, expr}
import org.apache.spark.sql.streaming.OutputMode
import org.apache.spark.sql.execution.streaming.RealTimeTrigger

spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic)
      .load()
      .join(broadcast(spark.read.format("parquet").load(staticTableLocation)), expr("joinKey = lookupKey"))
      .writeStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("topic", outputTopic)
      .option("checkpointLocation", checkpointLocation)
      .trigger(RealTimeTrigger.apply())
      .outputMode(OutputMode.Update())
      .start()
```

### Kinesis-Quelle zu Kafka-Senke

In diesem Beispiel wird aus einer Kinesis-Quelle gelesen und in eine Kafka-Senke geschrieben.

**Python:**

Das folgende Beispiel liest aus Kinesis im **Polling-Modus** und schreibt nach Kafka (AWS-Fassung):

```python
query = (
    spark.readStream
        .format("kinesis")
        .option("streamName", stream_name)
        .option("region", region_name)
        .option("awsAccessKey", aws_access_key_id)
        .option("awsSecretKey", aws_secret_access_key)
        .option("consumerMode", "polling")
        .load()
        .selectExpr("partitionKey AS key", "CAST(data AS STRING) AS value")
        .writeStream
        .format("kafka")
        .option("kafka.bootstrap.servers", broker_address)
        .option("topic", output_topic)
        .option("checkpointLocation", checkpoint_location)
        .trigger(realTime="5 minutes")
        .outputMode("update")
        .start()
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.streaming.OutputMode
import org.apache.spark.sql.execution.streaming.RealTimeTrigger

spark.readStream
      .format("kinesis")
      .option("streamName", streamName)
      .option("region", regionName)
      .option("awsAccessKey", awsAccessKeyId)
      .option("awsSecretKey", awsSecretAccessKey)
      .option("consumerMode", "polling")
      .load()
      .select(
        col("partitionKey").alias("key"),
        col("data").cast("string").alias("value")
      )
      .writeStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("topic", outputTopic)
      .option("checkpointLocation", checkpointLocation)
      .trigger(RealTimeTrigger.apply())
      .outputMode(OutputMode.Update())
      .start()
```

Für den **Enhanced-Fan-Out-Modus (EFO)** statt Polling `consumerMode` auf `efo` setzen (dann zusätzlich `consumerName` angeben, siehe Kinesis-EFO-Doku).

### Union

In diesem Beispiel werden zwei Kafka-DataFrames aus zwei unterschiedlichen Topics per Union verbunden und in eine Kafka-Senke geschrieben.

**Python:**

```python
df1 = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("startingOffsets", "earliest")
    .option("subscribe", input_topic_1)
    .load()
)

df2 = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("startingOffsets", "earliest")
    .option("subscribe", input_topic_2)
    .load()
)

query = (
    df1.union(df2)
    .writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("topic", output_topic)
    .option("checkpointLocation", checkpoint_location)
    .trigger(realTime="5 minutes")
    .outputMode("update")
    .start()
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.streaming.OutputMode
import org.apache.spark.sql.execution.streaming.RealTimeTrigger

val df1 = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic1)
      .load()

val df2 = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic2)
      .load()

df1.union(df2)
      .writeStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("topic", outputTopic)
      .option("checkpointLocation", checkpointLocation)
      .trigger(RealTimeTrigger.apply())
      .outputMode(OutputMode.Update())
      .start()
```

### Kafka-Quelle zu Lakebase-Senke

In diesen Beispielen wird aus einer Kafka-Quelle gelesen und in eine Lakebase-Datenbank geschrieben. Für alle Verbindungsoptionen siehe die Doku-Seite "Connect to Lakebase".

#### Lakebase-Tabellen, die in Unity Catalog registriert sind

Das folgende Beispiel verwendet die Unity-Catalog-Verbindungsmethode, die Credentials automatisch verwaltet. Die Ziel-Lakebase-Datenbank muss in Unity Catalog registriert sein (siehe "Register a Lakebase database in Unity Catalog").

**Python:**

```python
query = (
    spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", broker_address)
        .option("subscribe", input_topic)
        .option("startingOffsets", "earliest")
        .load()
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
        .writeStream
        .outputMode("update")
        .option("checkpointLocation", checkpoint_location)
        .option("upsertkey", "<primary_key>")
        .trigger(realTime="5 minutes")
        .toTable("<catalog>.<schema>.<table>")
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.execution.streaming.RealTimeTrigger

spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic)
      .load()
      .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
      .writeStream
      .outputMode("update")
      .option("checkpointLocation", checkpointLocation)
      .option("upsertkey", "<primary_key>")
      .trigger(RealTimeTrigger.apply())
      .toTable("<catalog>.<schema>.<table>")
```

`<catalog>.<schema>.<table>` muss durch den vollqualifizierten Namen der Zieltabelle ersetzt werden, `<primary_key>` durch die Primärschlüsselspalte. Existiert die Tabelle nicht, erstellt der Connector sie unter Verwendung dieses Schlüssels.

#### Lakebase-Tabellen, die nicht in Unity Catalog registriert sind

Für Lakebase-Tabellen, die nicht in Unity Catalog registriert sind, werden die Optionen `endpoint` und `dbtable` verwendet:

**Python:**

```python
query = (
    spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", broker_address)
        .option("subscribe", input_topic)
        .option("startingOffsets", "earliest")
        .load()
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
        .writeStream
        .format("postgresql")
        .outputMode("update")
        .option("endpoint", "<project-id>.<branch-id>.<endpoint-id>")
        .option("dbtable", "<schema>.<table>")
        .option("upsertkey", "<primary_key>")
        .option("checkpointLocation", checkpoint_location)
        .trigger(realTime="5 minutes")
        .start()
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.execution.streaming.RealTimeTrigger

spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic)
      .load()
      .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
      .writeStream
      .format("postgresql")
      .outputMode("update")
      .option("endpoint", "<project-id>.<branch-id>.<endpoint-id>")
      .option("dbtable", "<schema>.<table>")
      .option("upsertkey", "<primary_key>")
      .option("checkpointLocation", checkpointLocation)
      .trigger(RealTimeTrigger.apply())
      .start()
```

`<catalog>.<schema>.<table>` muss durch den vollqualifizierten Namen der Zieltabelle ersetzt werden, `<primary_key>` durch die Primärschlüsselspalte.

Alle verfügbaren Optionen sind im Abschnitt "Lakebase tables not registered with Unity Catalog" der entsprechenden Doku beschrieben.

## <a id="zustandsbehaftete-beispiele">3. Zustandsbehaftete Query-Beispiele</a>

Zustandsbehaftete Queries halten Zustandsinformationen über Datensätze hinweg, was Operationen wie Deduplizierung, Aggregation und Windowing ermöglicht. Diese Queries sind essenziell für Anwendungsfälle, die Informationen über die Zeit oder über mehrere Ereignisse hinweg verfolgen müssen. Real-Time Mode unterstützt zustandsbehaftete Operationen mit derselben Semantik wie der Micro-Batch-Modus, verarbeitet Daten dabei jedoch kontinuierlich für niedrigere Latenz. Zustandsbehaftete Queries benötigen mehr Speicher und Rechenressourcen als zustandslose Queries, da sie Zustand pflegen und aktualisieren müssen.

### Deduplizierung

In diesem Beispiel werden Datensätze anhand der Spalten `timestamp` und `value` dedupliziert.

**Python:**

```python
query = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("startingOffsets", "earliest")
    .option("subscribe", input_topic)
    .load()
    .dropDuplicates(["timestamp", "value"])
    .writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("topic", output_topic)
    .option("checkpointLocation", checkpoint_location)
    .trigger(realTime="5 minutes")
    .outputMode("update")
    .start()
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.streaming.OutputMode
import org.apache.spark.sql.execution.streaming.RealTimeTrigger

spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic)
      .load()
      .dropDuplicates("timestamp", "value")
      .writeStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("topic", outputTopic)
      .option("checkpointLocation", checkpointLocation)
      .trigger(RealTimeTrigger.apply())
      .outputMode(OutputMode.Update())
      .start()
```

### Aggregation

In diesem Beispiel werden Datensätze nach `timestamp` und `value` gruppiert und die Vorkommen gezählt.

**Python:**

```python
from pyspark.sql.functions import col

query = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("startingOffsets", "earliest")
    .option("subscribe", input_topic)
    .load()
    .groupBy(col("timestamp"), col("value"))
    .count()
    .selectExpr("CAST(value AS STRING) AS key", "CAST(count AS STRING) AS value")
    .writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("topic", output_topic)
    .option("checkpointLocation", checkpoint_location)
    .trigger(realTime="5 minutes")
    .outputMode("update")
    .start()
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.functions.col
import org.apache.spark.sql.streaming.OutputMode
import org.apache.spark.sql.execution.streaming.RealTimeTrigger

spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic)
      .load()
      .groupBy(col("timestamp"), col("value"))
      .count()
      .writeStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("topic", outputTopic)
      .option("checkpointLocation", checkpointLocation)
      .trigger(RealTimeTrigger.apply())
      .outputMode(OutputMode.Update())
      .start()
```

### Union mit Aggregation

In diesem Beispiel werden zunächst zwei Kafka-DataFrames aus zwei unterschiedlichen Topics per Union verbunden und anschließend aggregiert. Am Ende wird in die Kafka-Senke geschrieben.

**Python:**

```python
from pyspark.sql.functions import col

df1 = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("startingOffsets", "earliest")
    .option("subscribe", input_topic_1)
    .load()
)

df2 = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("startingOffsets", "earliest")
    .option("subscribe", input_topic_2)
    .load()
)

query = (
    df1.union(df2)
    .groupBy(col("timestamp"), col("value"))
    .count()
    .selectExpr("CAST(value AS STRING) AS key", "CAST(count AS STRING) AS value")
    .writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("topic", output_topic)
    .option("checkpointLocation", checkpoint_location)
    .trigger(realTime="5 minutes")
    .outputMode("update")
    .start()
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.functions.col
import org.apache.spark.sql.execution.streaming.RealTimeTrigger

val df1 = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic1)
      .load()

val df2 = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic2)
      .load()

df1.union(df2)
      .groupBy(col("timestamp"), col("value"))
      .count()
      .writeStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("topic", outputTopic)
      .option("checkpointLocation", checkpointLocation)
      .trigger(RealTimeTrigger.apply())
      .outputMode(OutputMode.Update())
      .start()
```

### transformWithState

In diesem Beispiel wird `transformWithState` verwendet, um benutzerdefinierten Zustand mit TTL (Time-to-Live) zu pflegen. Der Prozessor zählt die Anzahl der pro Schlüssel gesehenen Datensätze.

**Python:**

```python
from typing import Iterator, Tuple

from pyspark.sql import Row
from pyspark.sql.streaming import StatefulProcessor, StatefulProcessorHandle
from pyspark.sql.types import LongType, StringType, TimestampType, StructField, StructType

class RTMStatefulProcessor(StatefulProcessor):
  """
  This processor counts the number of records it has seen for each key using state variables
  with TTLs. It redundantly maintains this count with a value, list, and map state to put load
  on the state variable cleanup mechanism. (In practice, only one value state is needed to maintain
  the count for a given grouping key.)

  The input schema it expects is (String, Long) which represents a (key, source-timestamp) tuple.
  The source-timestamp is passed through so that we can calculate end-to-end latency. The output
  schema is (String, Long, Long), which represents a (key, count, source-timestamp) 3-tuple.
  """

  def init(self, handle: StatefulProcessorHandle) -> None:
    state_schema = StructType([StructField("value", LongType(), True)])
    self.value_state = handle.getValueState("value", state_schema, 30000)
    map_key_schema = StructType([StructField("key", LongType(), True)])
    map_value_schema = StructType([StructField("value", StringType(), True)])
    self.map_state = handle.getMapState("map", map_key_schema, map_value_schema, 30000)
    list_schema = StructType([StructField("value", StringType(), True)])
    self.list_state = handle.getListState("list", list_schema, 30000)

  def handleInputRows(self, key, rows, timerValues) -> Iterator[Row]:
    for row in rows:
      # row is a tuple (key, source_timestamp)
      key_str = row[0]
      source_timestamp = row[1]
      old_value = value.get()
      if old_value is None:
        old_value = 0
      self.value_state.update((old_value + 1,))
      self.map_state.update((old_value,), (key_str,))
      self.list_state.appendValue((key_str,))
      yield Row(key=key_str, value=old_value + 1, timestamp=source_timestamp)

  def close(self) -> None:
    pass

output_schema = StructType(
  [
    StructField("key", StringType(), True),
    StructField("value", LongType(), True),
    StructField("timestamp", TimestampType(), True),
  ]
)

query = (
  spark.readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", broker_address)
  .option("subscribe", input_topic)
  .load()
  .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)", "timestamp")
  .groupBy("key")
  .transformWithState(
    statefulProcessor=RTMStatefulProcessor(),
    outputStructType=output_schema,
    outputMode="Update",
    timeMode="processingTime",
  )
  .writeStream
  .format("kafka")
  .option("kafka.bootstrap.servers", broker_address)
  .option("topic", output_topic)
  .option("checkpointLocation", checkpoint_location)
  .trigger(realTime="5 minutes")
  .outputMode("Update")
  .start()
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.Encoders
import org.apache.spark.sql.execution.streaming.RealTimeTrigger
import org.apache.spark.sql.streaming.{ListState, MapState, StatefulProcessor, OutputMode, TTLConfig, TimeMode, TimerValues, ValueState}

/**
 * This processor counts the number of records it has seen for each key using state variables
 * with TTLs. It redundantly maintains this count with a value, list, and map state to put load
 * on the state variable cleanup mechanism. (In practice, only one value state is needed to maintain
 * the count for a given grouping key.)
 *
 * The input schema it expects is (String, Long) which represents a (key, source-timestamp) tuple.
 * The source-timestamp is passed through so that we can calculate end-to-end latency. The output
 * schema is (String, Long, Long), which represents a (key, count, source-timestamp) 3-tuple.
 *
 */

class RTMStatefulProcessor(ttlConfig: TTLConfig)
  extends StatefulProcessor[String, (String, Long), (String, Long, Long)] {
  @transient private var _value: ValueState[Long] = _
  @transient private var _map: MapState[Long, String] = _
  @transient private var _list: ListState[String] = _

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    // Counts the number of records this key has seen
    _value = getHandle.getValueState("value", Encoders.scalaLong, ttlConfig)
    _map = getHandle.getMapState("map", Encoders.scalaLong, Encoders.STRING, ttlConfig)
    _list = getHandle.getListState("list", Encoders.STRING, ttlConfig)
  }

  override def handleInputRows(
      key: String,
      inputRows: Iterator[(String, Long)],
      timerValues: TimerValues): Iterator[(String, Long, Long)] = {
    inputRows.map { row =>
      val key = row._1
      val sourceTimestamp = row._2

      val oldValue = _value.get()
      _value.update(oldValue + 1)
      _map.updateValue(oldValue, key)
      _list.appendValue(key)

      (key, oldValue + 1, sourceTimestamp)
    }
  }
}

spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic)
      .load()
      .select(col("key").cast("STRING"), col("value").cast("STRING"), col("timestamp"))
      .as[(String, String, Timestamp)]
      .groupByKey(row => row._1)
      .transformWithState(new RTMStatefulProcessor(TTLConfig(Duration.ofSeconds(30))), TimeMode.ProcessingTime, OutputMode.Update)
      .as[(String, Long, Long)]
      .select(
            col("_1").as("key"),
            col("_2").as("value")
      )
      .writeStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("topic", outputTopic)
      .option("checkpointLocation", checkpointLocation)
      .trigger(RealTimeTrigger.apply())
      .outputMode(OutputMode.Update())
      .start()
```

**Hinweis:** Es gibt einen Unterschied darin, wie Real-Time Mode und andere Ausführungsmodi in Structured Streaming den `StatefulProcessor` in `transformWithState` ausführen (siehe Abschnitt "`transformWithState` in real-time mode" in der Datei `Referenz.md`).

## <a id="entwicklung-testing">4. Entwicklung und Testing</a>

Die `display`-Funktion lässt sich verwenden, um Real-Time-Streaming-Daten direkt in einem Notebook zu visualisieren und die Query-Logik sowie Datentransformationen zu überprüfen, bevor in Produktion mit Kafka oder benutzerdefinierten Senken deployt wird. Das ist nützlich für interaktive Entwicklung, Testing und Debugging von Real-Time-Mode-Queries, ohne externe Senken oder Produktionsinfrastruktur einzurichten.

Die `display`-Funktion mit `realTime`-Trigger ist ab Databricks Runtime 17.1 verfügbar. Ein vollständiges Beispiel mit der Rate-Quelle und `display` findet sich in der Datei `Tutorial.md`.

### Rate-Quelle anzeigen

In diesem Beispiel wird aus einer Rate-Quelle gelesen und das Streaming-DataFrame in einem Notebook angezeigt.

**Python:**

```python
inputDF = (
  spark
  .readStream
  .format("rate")
  .option("numPartitions", 2)
  .option("rowsPerSecond", 1)
  .load()
)
display(inputDF, realTime="5 minutes", outputMode="update")
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.streaming.Trigger
import org.apache.spark.sql.streaming.OutputMode

val inputDF = spark
  .readStream
  .format("rate")
  .option("numPartitions", 2)
  .option("rowsPerSecond", 1)
  .load()
display(inputDF, trigger=Trigger.RealTime(), outputMode=OutputMode.Update())
```

## <a id="custom-sinks">5. Beispiele für benutzerdefinierte Senken</a>

Wenn Streaming-Daten in Ziele geschrieben werden müssen, für die keine eingebaute Structured-Streaming-Unterstützung existiert, wird `foreachSink` verwendet, um benutzerdefinierte Schreiblogik zu implementieren. Benutzerdefinierte Senken geben volle Kontrolle darüber, wie Daten geschrieben werden, und ermöglichen die Integration mit beliebigen Datenbanken, APIs oder Speichersystemen.

### In PostgreSQL schreiben mit `foreachSink`

**Scala** (aus der AWS-Doku ergänzt):

```scala
import java.sql.{Connection, DriverManager, PreparedStatement}

import org.apache.spark.sql.{ForeachWriter, Row}

/**
 * Groups connection properties for
 * the JDBC writers.
 *
 * @param url JDBC url of the form jdbc:subprotocol:subname to connect to
 * @param dbtable database table that should be written into
 * @param username username for authentication
 * @param password password for authentication
 */
class JdbcWriterConfig(
    val url: String,
    val dbtable: String,
    val username: String,
    val password: String,
) extends Serializable

/**
 * Handles streaming data writes to a database sink via JDBC, by:
 *   - connecting to the database
 *   - buffering incoming data rows in batches to reduce write overhead
 *
 * @param config connection parameters and configuration knobs for the writer
 */
class JdbcStreamingDataWriter(config: JdbcWriterConfig)
  extends ForeachWriter[Row] with Serializable {
  // The writer currently only supports this hard-coded schema
  private val UPSERT_STATEMENT_SQL =
    s"""MERGE INTO "${config.dbtable}"
       |USING (
       |  SELECT
       |    CAST(? AS INTEGER) AS "id",
       |    CAST(? AS CHARACTER VARYING) AS "data"
       |) AS "source"
       |ON "test"."id" = "source"."id"
       |WHEN MATCHED THEN
       |  UPDATE SET "data" = "source"."data"
       |WHEN NOT MATCHED THEN
       |  INSERT ("id", "data") VALUES ("source"."id", "source"."data")
       |""".stripMargin

  private val MAX_BUFFER_SIZE = 3
  private val buffer = new Array[Row](MAX_BUFFER_SIZE)
  private var bufferSize = 0

  private var connection: Connection = _

  /**
   * Flushes the [[buffer]] by writing all rows in the buffer to the database.
   */
  private def flushBuffer(): Unit = {
    require(connection != null)

    if (bufferSize == 0) {
      return
    }

    var upsertStatement: PreparedStatement = null

    try {
      upsertStatement = connection.prepareStatement(UPSERT_STATEMENT_SQL)

      for (i <- 0 until bufferSize) {
        val row = buffer(i)
        upsertStatement.setInt(1, row.getAs[String]("key"))
        upsertStatement.setString(2, row.getAs[String]("value"))
        upsertStatement.addBatch()
      }

      upsertStatement.executeBatch()
      connection.commit()

      bufferSize = 0
    } catch { case e: Exception =>
      if (connection != null) {
        connection.rollback()
      }
      throw e
    } finally {
      if (upsertStatement != null) {
        upsertStatement.close()
      }
    }
  }

  override def open(partitionId: Long, epochId: Long): Boolean = {
    connection = DriverManager.getConnection(config.url, config.username, config.password)
    true
  }

  override def process(row: Row): Unit = {
    buffer(bufferSize) = row
    bufferSize += 1
    if (bufferSize >= MAX_BUFFER_SIZE) {
      flushBuffer()
    }
  }

  override def close(errorOrNull: Throwable): Unit = {
    flushBuffer()
    if (connection != null) {
      connection.close()
      connection = null
    }
  }
}

spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", testUtils.brokerAddress)
      .option("subscribe", inputTopic)
      .load()
      .writeStream
      .outputMode(OutputMode.Update())
      .trigger(defaultTrigger)
      .foreach(new JdbcStreamingDataWriter(new JdbcWriterConfig(jdbcUrl, tableName, jdbcUsername, jdbcPassword)))
      .start()
```

---

## <a id="quellen">6. Quellen</a>

- Real-time mode examples (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/real-time/examples
- Real-time mode examples (Mirror, Azure, verifiziert/vollständig abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/examples
- Real-time mode examples (AWS): https://docs.databricks.com/aws/en/structured-streaming/real-time/examples

**Stand:** 2026-08-22; Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
