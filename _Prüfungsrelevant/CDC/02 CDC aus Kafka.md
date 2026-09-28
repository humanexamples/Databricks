[← Übersicht](00%20Uebersicht.md)

# CDC aus Kafka

**Kombination:** Kafka (Structured Streaming) · `from_json` · Secrets · AUTO CDC · Fan-in mehrerer Topics per Append-Flow

Log-basierte CDC-Werkzeuge (Debezium, Oracle GoldenGate, AWS DMS …) schreiben ihre Events häufig nicht in Dateien, sondern direkt in Kafka-Topics. Der Unterschied zu [01](01%20Debezium-Dateien%20mit%20Auto%20Loader%20und%20AUTO%20CDC.md): Die Quelle ist ein Stream statt eines Ordners, und die Payload steckt als Bytes in der Spalte `value`.

---

## A – Ein Topic → AUTO CDC (Python-Pipeline)

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col, from_json, expr

event_schema = """
  op STRING,
  ts_ms BIGINT,
  before STRUCT<order_id: BIGINT, status: STRING, amount: DECIMAL(10,2)>,
  after  STRUCT<order_id: BIGINT, status: STRING, amount: DECIMAL(10,2)>
"""

# ---------- Bronze: Kafka-Rohdaten ----------
@dp.table(comment="Roh-CDC-Events aus Kafka")
def bronze_orders_cdc():
    return (spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", "broker1:9092")
            .option("subscribe", "erp.public.orders")
            .option("startingOffsets", "earliest")
            .option("kafka.security.protocol", "SASL_SSL")
            .option("kafka.sasl.mechanism", "PLAIN")
            .option("kafka.sasl.jaas.config",
                    dbutils.secrets.get("kafka", "jaas_config"))   # Zugangsdaten nie im Code
            .load()
            .select(col("key").cast("string").alias("kafka_key"),
                    from_json(col("value").cast("string"), event_schema).alias("event"),
                    col("topic"), col("partition"), col("offset"),
                    col("timestamp").alias("kafka_ts")))

# ---------- Aufbereitung ----------
@dp.temporary_view
@dp.expect_or_drop("valid_key", "order_id IS NOT NULL")
def orders_cdc_clean():
    return (spark.readStream.table("bronze_orders_cdc")
            .select(expr("coalesce(event.after.order_id, event.before.order_id)").alias("order_id"),
                    col("event.after.status").alias("status"),
                    col("event.after.amount").alias("amount"),
                    col("event.op").alias("op"),
                    col("event.ts_ms").alias("ts_ms")))

# ---------- Silver: aktueller Stand ----------
dp.create_streaming_table("silver_orders")

dp.create_auto_cdc_flow(
    target             = "silver_orders",
    source             = "orders_cdc_clean",
    keys               = ["order_id"],
    sequence_by        = col("ts_ms"),
    apply_as_deletes   = expr("op = 'd'"),
    except_column_list = ["op", "ts_ms"],
    stored_as_scd_type = 1)
```

**Warum Bronze die Kafka-Metadaten (`topic`, `partition`, `offset`) behält:** Damit lässt sich jedes Silver-Ergebnis bis zur exakten Kafka-Nachricht zurückverfolgen. Kafka selbst hält Nachrichten nur begrenzt vor (Retention), Bronze dagegen dauerhaft.

---

## B – Mehrere Topics / Regionen → ein Ziel (Fan-in)

Gleiches Schema, mehrere Quellen, z. B. je Region ein Topic. Jede Quelle bekommt einen **eigenen Append-Flow mit eigenem Checkpoint** in dieselbe Bronze-Tabelle. Eine neue Region = ein neuer Flow, ohne Full Refresh.

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col, from_json, lit

# event_schema wie in A
dp.create_streaming_table("bronze_orders_cdc_all")

def kafka_flow(region: str, topic: str):
    @dp.append_flow(target="bronze_orders_cdc_all", name=f"orders_cdc_{region}")
    def _flow():
        return (spark.readStream.format("kafka")
                .option("kafka.bootstrap.servers", "broker1:9092")
                .option("subscribe", topic)
                .load()
                .select(from_json(col("value").cast("string"), event_schema).alias("event"),
                        lit(region).alias("region")))

for region, topic in [("de", "erp.de.orders"), ("fr", "erp.fr.orders"), ("it", "erp.it.orders")]:
    kafka_flow(region, topic)
```

Danach wie in A: Aufbereitungs-View → AUTO CDC. **Achtung:** Wenn dieselbe `order_id` in mehreren Regionen vorkommen kann, muss `region` Teil der Keys sein: `keys = ["region", "order_id"]`.

---

## C – Alternative: Kafka mit Auto CDC in SQL

```sql
CREATE OR REFRESH STREAMING TABLE bronze_orders_cdc AS
SELECT from_json(CAST(value AS STRING),
                 'op STRING, ts_ms BIGINT,
                  before STRUCT<order_id: BIGINT, status: STRING, amount: DECIMAL(10,2)>,
                  after  STRUCT<order_id: BIGINT, status: STRING, amount: DECIMAL(10,2)>') AS event,
       topic, partition, offset
FROM STREAM read_kafka(
  bootstrapServers => 'broker1:9092',
  subscribe        => 'erp.public.orders',
  startingOffsets  => 'earliest');

CREATE TEMPORARY VIEW orders_cdc_clean AS
SELECT coalesce(event.after.order_id, event.before.order_id) AS order_id,
       event.after.status AS status,
       event.after.amount AS amount,
       event.op AS op,
       event.ts_ms AS ts_ms
FROM STREAM bronze_orders_cdc;

CREATE OR REFRESH STREAMING TABLE silver_orders;

CREATE FLOW orders_cdc AS AUTO CDC INTO silver_orders
FROM STREAM orders_cdc_clean
KEYS (order_id)
APPLY AS DELETE WHEN op = 'd'
SEQUENCE BY ts_ms
COLUMNS * EXCEPT (op, ts_ms)
STORED AS SCD TYPE 1;
```

---

## Kafka-spezifische Hinweise

| Thema | Hinweis |
|---|---|
| Reihenfolge | Kafka garantiert Reihenfolge nur **innerhalb einer Partition**. AUTO CDC ordnet über `SEQUENCE BY` ohnehin selbst → Reihenfolge der Ankunft ist egal. |
| Tombstones | Debezium sendet nach einem Delete oft eine Nachricht mit `value = NULL` (für Log Compaction). `from_json(NULL)` ergibt `NULL` → per Expectation `valid_key` verwerfen. |
| Schema-Änderungen | Neue Spalten in der Quelle erfordern ein angepasstes `event_schema`. Alternative: Payload als `VARIANT` speichern (`parse_json`) und erst in der Aufbereitung typisieren. |
| Secrets | Zugangsdaten über `dbutils.secrets.get()` bzw. `secret()` in SQL, nie im Klartext. |

---
[← Vorherige Datei](01%20Debezium-Dateien%20mit%20Auto%20Loader%20und%20AUTO%20CDC.md) · [Übersicht](00%20Uebersicht.md) · [Nächste Datei →](03%20CDC%20prozedural%20mit%20foreachBatch%20und%20MERGE.md)

## Quellen

- [Stream processing with Apache Kafka and Databricks](https://docs.databricks.com/aws/en/connect/streaming/kafka)
- [read_kafka table-valued function](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_kafka)
- [The AUTO CDC APIs](https://docs.databricks.com/aws/en/ldp/cdc)
