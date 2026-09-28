# Real-Time Mode einrichten — Referenz

Dieses Dokument beschreibt die Voraussetzungen und Konfiguration, um Real-Time-Mode-Queries in Structured Streaming auszuführen — inklusive Compute-Anforderungen, Stream-to-Stream-Join-Konfiguration, Query-Konfiguration und Compute-Sizing. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/setup`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte.

## Abschnittsübersicht

1. [Voraussetzungen](#voraussetzungen)
2. [Stream-to-Stream-Joins](#stream-stream-joins)
3. [Query-Konfiguration](#query-konfiguration)
4. [Compute-Sizing](#compute-sizing)
5. [Quellen](#quellen)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

Für Real-Time Mode muss das Compute so konfiguriert sein, dass es folgende Anforderungen erfüllt:

- Klassisches Compute verwenden. Dedicated- und Standard-Access-Modes werden unterstützt. Standard Access Mode wird nur für Python unterstützt. Lakeflow-Pipelines und Serverless-Cluster werden nicht unterstützt.
- Databricks Runtime 16.4 LTS oder höher verwenden.
- Autoscaling deaktivieren.
- Photon deaktivieren.
- `spark.databricks.streaming.realTimeMode.enabled` auf `true` setzen.
- Spot-Instances deaktivieren, um Unterbrechungen zu vermeiden.

Für latenzsensitive Workloads mit UDFs empfiehlt Databricks, Dedicated Access Mode zu verwenden (siehe Abschnitt "Table functions" in der Datei `Referenz.md`).

Anleitungen zum Erstellen und Konfigurieren von klassischem Compute finden sich in der Doku-Seite "Compute configuration reference".

### <a id="stream-stream-joins">2. Stream-to-Stream-Joins</a>

Stream-to-Stream-Inner-Joins erfordern zusätzliche Konfiguration für Real-Time Mode. Outer Joins werden nicht unterstützt (siehe Abschnitt "Stream to stream join" in der Datei `Referenz.md`).

**Wichtig:** Um einen Stream-to-Stream-Join in Real-Time Mode mit mehreren anderen Streams auf demselben Cluster auszuführen, muss Databricks Runtime 18 LTS oder höher verwendet werden.

In Databricks Runtime 18.2 und darunter unterstützt Structured Streaming die folgenden Konfigurationen nicht für andere Verarbeitungsmodi, einschließlich `processingTime` und `availableNow`.

Um Stream-to-Stream-Joins für Real-Time Mode zu aktivieren, müssen folgende Spark-Konfigurationen gesetzt werden:

### Python

```python
spark.conf.set("spark.databricks.streaming.realTimeMode.streamStreamJoin.enabled", "true")
spark.conf.set("spark.sql.streaming.join.stateFormatVersion", "4")
spark.conf.set("spark.sql.streaming.join.stateFormatV4.enabled", "true")
spark.conf.set("spark.sql.streaming.stateStore.rocksdb.mergeOperatorVersion", "2")
spark.conf.set("spark.sql.streaming.realTimeMode.controlMessage.enabled", "true")
```

### SQL

```sql
SET spark.databricks.streaming.realTimeMode.streamStreamJoin.enabled = true;
SET spark.sql.streaming.join.stateFormatVersion = 4;
SET spark.sql.streaming.join.stateFormatV4.enabled = true;
SET spark.sql.streaming.stateStore.rocksdb.mergeOperatorVersion = 2;
SET spark.sql.streaming.realTimeMode.controlMessage.enabled = true;
```

## <a id="query-konfiguration">3. Query-Konfiguration</a>

Um eine Query in Real-Time Mode auszuführen, muss der Real-Time-Trigger aktiviert werden. Real-Time-Trigger werden nur im Update-Modus unterstützt.

### Python

```python
query = (
    spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", broker_address)
        .option("subscribe", input_topic)
        .load()
        .writeStream
        .format("kafka")
        .option("kafka.bootstrap.servers", broker_address)
        .option("topic", output_topic)
        .option("checkpointLocation", checkpoint_location)
        .outputMode("update")
        # In PySpark, the realTime trigger requires specifying the interval.
        .trigger(realTime="5 minutes")
        .start()
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.execution.streaming.RealTimeTrigger

val readStream = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("subscribe", inputTopic).load()
      .writeStream
      .format("kafka")
      .option("kafka.bootstrap.servers", brokerAddress)
      .option("topic", outputTopic)
      .option("checkpointLocation", checkpointLocation)
      .outputMode("update")
      .trigger(RealTimeTrigger.apply())
      // RealTimeTrigger can also accept an argument specifying the checkpoint interval.
      // For example, this code indicates a checkpoint interval of 5 minutes:
      // .trigger(RealTimeTrigger.apply("5 minutes"))
      .start()
```

## <a id="compute-sizing">4. Compute-Sizing</a>

Pro Compute-Ressource lässt sich ein Real-Time-Job ausführen, sofern das Compute genügend Task-Slots hat.

Um im Low-Latency-Modus zu laufen, muss die Gesamtzahl der verfügbaren Task-Slots gleich oder größer sein als die Anzahl der Tasks über alle Query-Stages hinweg.

### Beispiele zur Slot-Berechnung

| Pipeline-Typ | Konfiguration | Benötigte Slots |
| --- | --- | --- |
| Einstufig, zustandslos (Kafka-Quelle + Senke) | `maxPartitions` = 8 | 8 Slots |
| Zweistufig, zustandsbehaftet (Kafka-Quelle + Shuffle) | `maxPartitions` = 8, Shuffle-Partitionen = 20 | 28 Slots (8 + 20) |
| Dreistufig (Kafka-Quelle + Shuffle + Repartition) | `maxPartitions` = 8, zwei Shuffle-Stages zu je 20 | 48 Slots (8 + 20 + 20) |

Wird `maxPartitions` nicht gesetzt, wird die Anzahl der Partitionen im Kafka-Topic verwendet.

---

## <a id="quellen">5. Quellen</a>

- Set up real-time mode (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/real-time/setup
- Set up real-time mode (Mirror, Azure, verifiziert/vollständig abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/setup
- Set up real-time mode (AWS): https://docs.databricks.com/aws/en/structured-streaming/real-time/setup

**Stand:** 2026-08-22; Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
