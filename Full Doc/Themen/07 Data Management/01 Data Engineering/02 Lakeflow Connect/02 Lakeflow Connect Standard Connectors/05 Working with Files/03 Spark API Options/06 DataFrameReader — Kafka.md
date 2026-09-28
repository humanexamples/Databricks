# DataFrameReader options — Kafka

Bereich: **DataFrameReader options › Kafka** — Optionen für **Batch**-Lesen aus Kafka (`spark.read.format("kafka")`).

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `endingOffsets` | `latest` | enum / JSON-String | „Where to stop reading." |
| `endingOffsetsByTimestamp` | None | JSON-Timestamp-String | „Per-partition ending offsets specified as timestamps in milliseconds." |
| `endingTimestamp` | None | Ganzzahl | „Global ending timestamp in milliseconds applied to all partitions." |

> Die übrigen, gemeinsamen Kafka-Verbindungsoptionen (`kafka.bootstrap.servers`, `subscribe` / `assign` / `subscribePattern`, `startingOffsets`, `startingOffsetsByTimestamp`, `startingTimestamp`, `kafka.*` Sicherheits-/SSL-Properties, `includeHeaders`, `failOnDataLoss`) sind in der Structured-Streaming-Kafka-Doku beschrieben und gelten auch für Batch-Lesen.

Für **Streaming**-spezifische Kafka-Optionen siehe [23 DataStreamReader — Kafka.md](23%20DataStreamReader%20%E2%80%94%20Kafka.md).

## Beispiel

```python
df = (spark.read.format("kafka")
  .option("kafka.bootstrap.servers", "host:9092")
  .option("subscribe", "events")
  .option("startingOffsets", "earliest")
  .option("endingOffsets", "latest")
  .load())
```
