# Echtzeit-Verarbeitung (Real-Time Mode)

## Abschnittsübersicht

1. [Überblick und Status](#ueberblick)
2. [Wie Real-Time Mode niedrige Latenz erreicht](#latenz-mechanismen)
3. [Verhältnis zu Continuous-Pipelines](#continuous-verhaeltnis)
4. [Voraussetzungen](#voraussetzungen)
5. [Konfiguration in drei Schritten](#konfiguration)
6. [Code-Beispiele](#code-beispiele)
7. [Unterstützte Quellen und Senken](#quellen-senken)
8. [Compute-Sizing](#compute-sizing)
9. [Operator-Unterstützung](#operatoren)
10. [Monitoring der Performance](#monitoring)
11. [Limitierungen](#limitierungen)

---

## <a id="ueberblick">1. Überblick und Status</a>

**Wichtig:** Real-Time Mode in Lakeflow-Pipelines befindet sich im **Public Preview** auf Databricks Runtime 18.1.3 im Preview-Channel.

Real-Time Mode ermöglicht Datenverarbeitung mit extrem niedriger Latenz — End-to-End-Latenz von **bis zu 5 Millisekunden**. Real-Time Mode eignet sich für operative Workloads, die eine unmittelbare Reaktion auf Streaming-Daten erfordern, etwa Betrugserkennung und Echtzeit-Personalisierung.

Real-Time Mode ist auch direkt in Structured Streaming außerhalb von Pipelines verfügbar.

## <a id="latenz-mechanismen">2. Wie Real-Time Mode niedrige Latenz erreicht</a>

Real-Time Mode unterscheidet sich in drei zentralen Punkten von der Standard-Continuous-Verarbeitung:

- **Long-running Batches**: Das System verarbeitet Daten, sobald sie in der Quelle verfügbar sind, innerhalb lang laufender Batches (Standard: fünf Minuten).
- **Simultaneous Stage Scheduling**: Alle Query-Stages werden gleichzeitig eingeplant. Die Compute-Ressource muss genügend verfügbare Task-Slots besitzen, um alle Stages gleichzeitig abzudecken (siehe Abschnitt 8, Compute-Sizing).
- **Streaming Shuffle**: Daten werden zwischen Stages weitergegeben, sobald sie produziert wurden, statt darauf zu warten, dass eine vorgelagerte Stage abgeschlossen ist, bevor die nachgelagerte Stage startet.

Das über `pipelines.trigger.interval` konfigurierte Checkpoint-Intervall steuert, wie häufig State und Source-Offsets dauerhaft gespeichert werden. Längere Intervalle reduzieren den Checkpointing-Overhead, erhöhen aber die Recovery-Zeit nach einem Fehler und verzögern die Metrik-Meldung. Kürzere Intervalle verbessern die Durability, fügen aber Overhead hinzu.

## <a id="continuous-verhaeltnis">3. Verhältnis zu Continuous-Pipelines</a>

Real-Time Mode ist ein spezialisierter Typ eines Continuous-Triggers. Continuous-Modus ist weiterhin erforderlich; Real-Time Mode fügt zusätzliche Flow-Level-Latenzoptimierungen hinzu. Um Real-Time Mode zu nutzen, muss die Pipeline zunächst im Continuous-Modus laufen. Real-Time Mode wendet dann zusätzliche Optimierungen auf Flow-Ebene an, um Sub-Sekunden-Latenz über das hinaus zu erreichen, was Standard-Continuous-Verarbeitung liefert.

Das Aktivieren von Real-Time Mode erfordert drei Konfigurationsschritte:

1. Pipeline auf Continuous-Modus setzen.
2. Real-Time Mode auf Pipeline-Ebene aktivieren.
3. Einen Real-Time-Update-Flow definieren.

## <a id="voraussetzungen">4. Voraussetzungen</a>

| Anforderung | Wert |
|---|---|
| Databricks Runtime | 18.1.3 auf dem Lakeflow-Pipelines-Preview-Channel |
| Compute-Typ | Classic Compute oder Serverless |

## <a id="konfiguration">5. Konfiguration in drei Schritten</a>

### Schritt 1: Pipeline auf Continuous-Modus setzen

In den Pipeline-Einstellungen **Pipeline mode** auf **Continuous** setzen, oder im Pipeline-JSON:

```json
{
  "continuous": true
}
```

### Schritt 2: Real-Time Mode auf Pipeline-Ebene aktivieren

In den Pipeline-Einstellungen unter **Advanced > Spark config** folgenden Key hinzufügen:

```ini
spark.databricks.streaming.realTimeMode.enabled = true
```

Alternativ im Pipeline-JSON:

```json
{
  "continuous": true,
  "spark_conf": {
    "spark.databricks.streaming.realTimeMode.enabled": "true"
  }
}
```

### Schritt 3: Real-Time-Update-Flow definieren

Real-Time Mode erfordert einen Update Flow. `dp.create_sink()` definiert das Ausgabeziel, anschließend wird der `@dp.update_flow`-Decorator mit `pipelines.trigger` auf `"RealTime"` gesetzt und `target` zeigt auf den Sink:

```python
from pyspark import pipelines as dp

# Define the output sink
dp.create_sink(
    "my_kafka_sink",
    "kafka",
    {
        "kafka.bootstrap.servers": "<bootstrap-servers>",
        "topic": "<output-topic>",
    }
)

# Define the real-time update flow targeting the sink
@dp.update_flow(
    name="my_rtm_flow",
    target="my_kafka_sink",
    spark_conf={
        "pipelines.trigger": "RealTime",
        "pipelines.trigger.interval": "5 minutes",  # optional; defaults to 5 minutes
    }
)
def my_real_time_flow():
    return (
        spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "<bootstrap-servers>")
            .option("subscribe", "<input-topic>")
            .load()
    )
```

Flow-Level-Konfigurationsparameter:

| Parameter | Erforderlich | Standard | Beschreibung |
|---|---|---|---|
| `pipelines.trigger` | Ja | — | Auf `"RealTime"` setzen, um Real-Time Mode für diesen Flow zu aktivieren. |
| `pipelines.trigger.interval` | Nein | `"5 minutes"` | Checkpoint-Intervall. Steuert, wie oft State und Offsets committet werden. Kürzere Werte verbessern die Recoverability; längere Werte reduzieren den Overhead. |

## <a id="code-beispiele">6. Code-Beispiele</a>

### Kafka zu Kafka

```python
from pyspark import pipelines as dp

dp.create_sink("kafka_output_sink", "kafka", {
    "kafka.bootstrap.servers": broker_address,
    "topic": output_topic,
})

@dp.update_flow(
    name="kafka_rtm_flow",
    target="kafka_output_sink",
    spark_conf={
        "pipelines.trigger": "RealTime",
        "pipelines.trigger.interval": "5 minutes",
    }
)
def kafka_rtm_flow():
    return (
        spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", broker_address)
            .option("subscribe", input_topic)
            .option("startingOffsets", "latest")
            .load()
            .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)", "timestamp")
    )
```

### Anreicherung mit Broadcast Join

Ein Kafka-Stream wird gegen eine statische Lookup-Tabelle gejoint. Es werden nur Broadcast- (Stream-zu-Static-) Joins unterstützt; Stream-zu-Stream-Joins werden in Real-Time Mode **nicht** unterstützt.

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import broadcast, expr

dp.create_sink("enriched_output_sink", "kafka", {
    "kafka.bootstrap.servers": broker_address,
    "topic": enriched_output_topic,
})

@dp.update_flow(
    name="enriched_events_flow",
    target="enriched_output_sink",
    spark_conf={
        "pipelines.trigger": "RealTime",
        "pipelines.trigger.interval": "5 minutes",
    }
)
def enriched_events():
    lookup = spark.read.table("catalog.schema.lookup_table")
    return (
        spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", broker_address)
            .option("subscribe", input_topic)
            .load()
            .withColumn("event_key", expr("CAST(value AS STRING)"))
            .join(broadcast(lookup), expr("event_key = lookup_key"))
            .select("event_key", "lookup_value", "timestamp")
    )
```

### Aggregation

Zählt Events nach Schlüssel mittels eines zustandsbehafteten `groupBy`. `spark.sql.shuffle.partitions` sollte auf die Anzahl der Input-Partitionen abgestimmt werden, für zustandsbehaftete Operationen:

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col

dp.create_sink("event_counts_sink", "kafka", {
    "kafka.bootstrap.servers": broker_address,
    "topic": output_topic,
})

@dp.update_flow(
    name="event_counts_flow",
    target="event_counts_sink",
    spark_conf={
        "pipelines.trigger": "RealTime",
        "pipelines.trigger.interval": "5 minutes",
        "spark.sql.shuffle.partitions": "8",
    }
)
def event_counts():
    return (
        spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", broker_address)
            .option("subscribe", input_topic)
            .load()
            .selectExpr("CAST(key AS STRING) AS event_type", "timestamp")
            .groupBy(col("event_type"))
            .count()
    )
```

## <a id="quellen-senken">7. Unterstützte Quellen und Senken</a>

| Connector | Als Quelle | Als Senke | Hinweise |
|---|---|---|---|
| Apache Kafka | Ja | Ja | — |
| AWS MSK | Ja | Ja | Nutzt das Kafka-kompatible Interface. |
| Azure Event Hubs (Kafka-Connector) | Ja | Ja | Nutzt das Kafka-kompatible Interface. |
| Amazon Kinesis | Ja | Nicht unterstützt | Nur für EFO-Modus (Enhanced Fan-Out) verwenden. |
| Delta | Nicht unterstützt | Nicht unterstützt | — |

## <a id="compute-sizing">8. Compute-Sizing</a>

Pro Compute-Ressource lässt sich eine Real-Time-Pipeline betreiben, sofern die Compute-Ressource genügend Task-Slots besitzt. Die verfügbaren Task-Slots müssen alle Tasks über alle Query-Stages hinweg abdecken.

| Pipeline-Typ | Konfiguration | Benötigte Task-Slots |
|---|---|---|
| Single-Stage stateless (Kafka-Quelle + Senke) | `maxPartitions` = 8 | 8 |
| Two-Stage stateful (Kafka-Quelle + Shuffle) | `maxPartitions` = 8, Shuffle-Partitionen = 20 | 28 (8 + 20) |
| Three-Stage (Kafka-Quelle + zwei Shuffles) | `maxPartitions` = 8, zwei Shuffle-Stages à 20 | 48 (8 + 20 + 20) |

Wird `maxPartitions` nicht gesetzt, wird die Anzahl der Partitionen im Kafka-Topic verwendet.

## <a id="operatoren">9. Operator-Unterstützung</a>

| Kategorie | Operator | Unterstützt |
|---|---|---|
| Stateless | Selection, Projection | Ja |
| UDFs | Scala UDF | Ja (mit Einschränkungen) |
| UDFs | Python UDF | Ja (mit Einschränkungen) |
| Aggregation | sum, count, max, min, avg | Ja |
| Windowing | Tumbling, Sliding | Ja |
| Windowing | Session | Nicht unterstützt |
| Deduplication | `dropDuplicates` | Ja (unbounded state) |
| Deduplication | `dropDuplicatesWithinWatermark` | Nicht unterstützt |
| Joins | Broadcast Table Join | Ja |
| Joins | Stream-to-Stream Join | Nicht unterstützt |
| Custom | `transformWithState` | Ja (mit Verhaltensunterschieden) |
| Custom | `union` | Ja (mit Einschränkungen) |
| Custom | `forEach` | Nicht unterstützt |
| Custom | `flatMapGroupsWithState` | Nicht unterstützt |
| Custom | `mapPartitions` | Nicht unterstützt |
| Custom | `forEachBatch` | Nicht unterstützt |

### `transformWithState` in Real-Time Mode

`transformWithState` wird in Real-Time Mode unterstützt, mit folgenden Unterschieden gegenüber Micro-Batch-Verarbeitung:

- `handleInputRows` wird einmal pro Zeile aufgerufen statt einmal pro Schlüssel und Batch. Der `inputRows`-Iterator liefert pro Aufruf einen einzelnen Wert.
- Event-Time-Timer werden nicht unterstützt. Processing-Time-Timer feuern, wenn ein Long-running-Batch endet und keine Daten eingetroffen sind.
- `transformWithStateInPandas` wird nicht unterstützt.

### Pandas UDFs in Real-Time Mode

Um die Latenz mit Pandas-UDFs zu minimieren, sollte `spark.sql.execution.arrow.maxRecordsPerBatch` auf `1` gesetzt werden. Das optimiert auf Kosten des Durchsatzes für Latenz. Ist auch der Durchsatz wichtig, sollte der Wert auf `100` oder höher gesetzt werden.

## <a id="monitoring">10. Monitoring der Performance</a>

Real-Time Mode stellt Latenz-Metriken in `StreamingQueryProgress` unter dem Feld `latencies` bereit. Zugriff über einen `StreamingQueryListener` oder durch Inspektion der `lastProgress`-Eigenschaft der Streaming-Query.

| Metrik | Beschreibung |
|---|---|
| `processingLatencyMs` | Zeit zwischen dem Einlesen eines Datensatzes durch den Flow und dessen vollständiger Verarbeitung durch den Flow |
| `sourceQueuingLatencyMs` | Zeit zwischen dem erfolgreichen Schreiben eines Datensatzes in den Message Bus (z. B. Log-Append-Zeit in Kafka) und dessen erstem Einlesen durch den Flow |
| `e2eLatencyMs` | Gesamte End-to-End-Latenz von der Produktion des Datensatzes an der Quelle bis zu dessen vollständiger Verarbeitung durch den Flow |

Jede Metrik wird als p50-, p90-, p95- und p99-Perzentil gemeldet.

## <a id="limitierungen">11. Limitierungen</a>

Es wird empfohlen, pro Pipeline einen Real-Time-Flow zu verwenden. Mehrere Flows sind zulässig, aber Task-Slot-Konkurrenz zwischen Flows erhöht die Latenz.
