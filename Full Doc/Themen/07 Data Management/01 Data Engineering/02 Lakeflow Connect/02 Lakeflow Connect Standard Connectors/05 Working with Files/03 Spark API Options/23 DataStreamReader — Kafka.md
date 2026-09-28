# DataStreamReader options — Kafka

Bereich: **DataStreamReader options › Kafka** — Optionen, die nur für **Streaming**-Lesen aus Kafka gelten (`spark.readStream.format("kafka")`).

Quelle: [Spark API options reference](https://learn.microsoft.com/en-us/azure/databricks/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `bytesEstimateWindowLength` | `300s` | Dauer-String (z. B. `10m`, `600s`) | „The time window used to estimate remaining bytes for the `estimatedTotalBytesBehindLatest` metric." |
| `maxOffsetsPerTrigger` | None | positive Ganzzahl | „The maximum number of offsets to process per trigger interval. Offsets are distributed proportionally across topic partitions." |
| `maxTriggerDelay` | `15m` | Dauer-String (z. B. `10m`, `600s`) | „The maximum time to wait for `minOffsetsPerTrigger` to accumulate before triggering." |
| `minOffsetsPerTrigger` | None | positive Ganzzahl | „The minimum number of offsets to accumulate before triggering a micro-batch. When `maxTriggerDelay` is reached, the micro-batch runs regardless." |

> Verbindungs- und gemeinsame Optionen (`kafka.bootstrap.servers`, `subscribe` / `assign` / `subscribePattern`, `startingOffsets`, `includeHeaders`, `failOnDataLoss`, `kafka.*` SSL/SASL) siehe [06 DataFrameReader — Kafka.md](06%20DataFrameReader%20%E2%80%94%20Kafka.md) bzw. die Structured-Streaming-Kafka-Doku.

## Beispiel

```python
df = (spark.readStream.format("kafka")
  .option("kafka.bootstrap.servers", "host:9092")
  .option("subscribe", "events")
  .option("startingOffsets", "latest")
  .option("maxOffsetsPerTrigger", 100000)
  .option("minOffsetsPerTrigger", 10000)
  .option("maxTriggerDelay", "5m")
  .load())
```
