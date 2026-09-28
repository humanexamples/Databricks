# Schema Evolution

Schema Evolution erlaubt es Systemen, sich an strukturelle Änderungen der Daten über die Zeit anzupassen. Typische Änderungen sind neue Spalten, umbenannte Felder, entfernte Spalten, Type Widening (z. B. INT zu DOUBLE) und andere Typumwandlungen.

## Vier unabhängige Kategorien

Schema Evolution betrifft vier unabhängige Bereiche:

1. **Connectors** (Auto Loader, Kafka, Kinesis, Lakeflow)
2. **Format-Parser** (`from_json`, `from_avro`, `from_xml`, `from_protobuf`)
3. **Engines** (Structured Streaming)
4. **Datasets** (Streaming-Tabellen, materialisierte Views, Delta-Tabellen, Views)

## Unterstützung durch Connectors

- **Auto Loader:** Unterstützt Spaltenänderungen und Type Widening über `cloudFiles.schemaEvolutionMode`. Neue Spalten und Umbenennungen erfordern einen manuellen Neustart. Ausführlich: [02 Lakeflow Connect/.../06 Auto Loader/01 Schema-Inferenz und -Evolution.md](../02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/01%20Schema-Inferenz%20und%20-Evolution.md).
- **Delta-Connector:** Neue Spalten werden mit `mergeSchema` automatisch übernommen. Umbenennen und Löschen von Spalten wird mit bestimmten Spark-Konfigurationen unterstützt.
- **SaaS-/CDC-Connectors:** Starten bei Schemaänderungen automatisch neu. Typänderungen erfordern einen vollständigen Refresh.
- **Kafka/Kinesis/Pub/Sub/Pulsar:** Keine native Unterstützung – Schema Evolution wird an die Format-Parser delegiert.

## Unterstützung durch Format-Parser

- **`from_json`:** Keine native Unterstützung; automatische Evolution ist in Lakeflow-Pipelines verfügbar. Ausführlich: [03 Lakeflow Pipelines/04 Ingestion und Laden von Daten/02 Schema Evolution aus JSON.md](../03%20Lakeflow%20Pipelines/04%20Ingestion%20und%20Laden%20von%20Daten/02%20Schema%20Evolution%20aus%20JSON.md).
- **`from_avro` / `from_protobuf`:** Unterstützt über die Confluent Schema Registry.
- **`from_csv` / `from_xml`:** Keine Unterstützung für Schema Evolution.

## Unterstützung auf Dataset-Ebene

- **Streaming-Tabellen:** Aktivieren Merge-Schema-Evolution standardmäßig; Type Widening muss explizit aktiviert werden.
- **Materialisierte Views:** Jede Schemaänderung löst eine vollständige Neuberechnung aus.
- **Delta-Tabellen:** Unterstützen Merge-Schema, Column Mapping und Type Widening; andere Typänderungen erfordern ein Neuschreiben der Tabelle mit `overwriteSchema`.
- **Views:** Unterstützen den Modus `SCHEMA EVOLUTION` für automatische Anpassung ohne explizite Spaltenliste.

## Relevante Konfigurationsoptionen

- `cloudFiles.schemaEvolutionMode`
- `rescuedDataColumn`
- `schemaHints`
- `addNewColumnsWithTypeWidening`
- `mergeSchema`
- `spark.databricks.delta.streaming.allowSourceColumnRename`
- `spark.databricks.delta.streaming.allowSourceColumnDrop`
- `delta.enableTypeWidening`
- `schemaLocationKey`
- `spark.databricks.delta.schema.autoMerge.enabled`
- `avroSchemaEvolutionMode`
- `overwriteSchema`
- `SCHEMA EVOLUTION`
- `SCHEMA TYPE EVOLUTION`

## Beispiel: Kafka-zu-Delta-Ingestion mit Avro-Schema-Evolution

Das folgende Beispiel liest einen Kafka-Stream mit Avro-Payload über die Confluent Schema Registry, dekodiert ihn mit `from_avro` (inkl. `avroSchemaEvolutionMode`) und schreibt ihn mit `mergeSchema` in eine Delta-Bronze-Tabelle:

```python
# ----- CONFIG: fill these in -----
CATALOG = "<catalog_name>"
SCHEMA = "<schema_name>"
SCHEMA_REG = "<schema registry endpoint>"
SR_USER = "<api key>"
SR_PASS = "<api secret>"
BOOTSTRAP = "<server:ip>"
TOPIC = "<topic>"

BRONZE_TABLE = f"{CATALOG}.{SCHEMA}.bronze_users"
CHECKPOINT = f"/Volumes/{CATALOG}/{SCHEMA}/checkpoints/bronze_users"

KAFKA_OPTS = {
  "kafka.security.protocol": "SASL_SSL",
  "kafka.sasl.mechanism": "PLAIN",
  "kafka.sasl.jaas.config": f"kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required username='{SR_USER}' password='{SR_PASS}';"
}

from pyspark.sql.functions import col
from pyspark.sql.avro.functions import from_avro

reader = (spark.readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", BOOTSTRAP)
  .option("subscribe", TOPIC)
  .option("startingOffsets", "earliest"))

for k, v in KAFKA_OPTS.items():
    reader = reader.option(k, v)

raw_df = reader.load()

decoded = from_avro(
    data=col("value"),
    jsonFormatSchema=None,
    subject=f"{TOPIC}-value",
    schemaRegistryAddress=SCHEMA_REG,
    options={
      "confluent.schema.registry.basic.auth.credentials.source": "USER_INFO",
      "confluent.schema.registry.basic.auth.user.info": f"{SR_USER}:{SR_PASS}",
      "avroSchemaEvolutionMode": "restart",
      "mode": "FAILFAST"
    }).alias("payload")

bronze_df = raw_df.select(decoded, "timestamp").select("payload.*", "timestamp")

(bronze_df.writeStream
  .format("delta")
  .option("checkpointLocation", CHECKPOINT)
  .option("ignoreChanges", "true")
  .outputMode("append")
  .option("mergeSchema", "true")
  .trigger(availableNow=True)
  .toTable(BRONZE_TABLE))
```

---
**Quelle:** https://docs.databricks.com/aws/en/data-engineering/schema-evolution  
**Stand:** 2026-08-07
