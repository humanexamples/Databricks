# Real-Time Mode in Structured Streaming

## 1. Was ist Real-Time Mode?

- Trigger-Typ von Structured Streaming, End-to-End-Latenz bis **5 ms**.
- Für operative Workloads mit Sofortreaktion: Fraud Detection, Echtzeit-Personalisierung.
- Nutzt dieselben Structured-Streaming-APIs wie Micro-Batch — Aktivierung nur über den Real-Time-Trigger. Auch in Lakeflow-Pipelines verfügbar.

**Wie niedrige Latenz erreicht wird:**
- Lang laufende Batches (Standard: 5 Minuten) — Daten werden verarbeitet, sobald sie eintreffen.
- Gleichzeitiges Scheduling aller Query-Stages → genügend Task-Slots über alle Stages eines Batches nötig.
- Sofortige Datenweitergabe zwischen Stages per Streaming-Shuffle statt Warten auf Stage-Abschluss.
- Checkpointing/Metriken zwischen Batches: längere Batches = selteneres Checkpointing, längere Replays im Fehlerfall, verzögerte Metriken; kürzere Batches = häufigeres Checkpointing, kann Latenz beeinflussen. → Trigger-Intervall gegen Ziel-Workload benchmarken.

**Real-Time Mode wählen, wenn:**
- Latenz < 1 s nötig (z. B. Kreditkartentransaktion in Echtzeit blocken bei Betrugs-Score-Überschreitung).
- Operative Entscheidungen sofort ausgelöst werden müssen (z. B. Werbenachricht bei Clickstream-Signal).
- Kontinuierliche statt periodische Verarbeitung nötig.

**Micro-Batch (Standard) wählen, wenn:**
- Analytische Verarbeitung (ETL, Medallion) mit Sekunden-/Minuten-Latenz reicht.
- Kostenoptimierung wichtiger als Sub-Sekunden-Latenz (Real-Time Mode braucht dedizierte Compute).
- Häufige Checkpoints für schnellere Recovery benötigt werden.

## 2. Einrichten (Setup)

**Compute-Voraussetzungen:**
- Klassisches Compute; Dedicated und Standard Access Mode unterstützt — Standard **nur Python**.
- Lakeflow-Pipelines (Classic/Serverless) **nicht** als Structured Streaming unterstützt (nur eigene Pipeline-Konfiguration); Serverless Compute generell **nicht** unterstützt.
- DBR **16.4 LTS+**.
- Autoscaling **deaktivieren**, Photon **deaktivieren**, Spot-Instances **deaktivieren**.
- `spark.databricks.streaming.realTimeMode.enabled = true`.
- Latenzsensitive UDF-Workloads → Dedicated Access Mode empfohlen.

**Stream-to-Stream-Joins:** Inner Joins brauchen Zusatzkonfig, **Outer Joins nicht unterstützt**. Joins mit mehreren anderen Streams auf demselben Cluster → DBR 18 LTS+.

```python
spark.conf.set("spark.databricks.streaming.realTimeMode.streamStreamJoin.enabled", "true")
spark.conf.set("spark.sql.streaming.join.stateFormatVersion", "4")
spark.conf.set("spark.sql.streaming.join.stateFormatV4.enabled", "true")
spark.conf.set("spark.sql.streaming.stateStore.rocksdb.mergeOperatorVersion", "2")
spark.conf.set("spark.sql.streaming.realTimeMode.controlMessage.enabled", "true")
```
- Analog in Scala (`spark.conf.set(...)`) und SQL (`SET ... = ...;`).
- DBR 18.2 und darunter: diese Settings werden für `processingTime`/`availableNow` nicht unterstützt.

**Query-Konfiguration** — nur **Update-Modus** unterstützt:

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
        # PySpark: Intervall bei realTime-Trigger ist Pflicht
        .trigger(realTime="5 minutes")
        .start()
)
```

**Compute-Sizing (Task-Slots):** ein Real-Time-Job pro Compute-Ressource, sofern genug Task-Slots vorhanden. Für Low-Latency: verfügbare Task-Slots **≥** Anzahl Tasks über alle Query-Stages.

| Pipeline-Typ | Konfiguration | Benötigte Slots |
|---|---|---|
| Einstufig, zustandslos (Kafka-Quelle + Senke) | `maxPartitions` = 8 | 8 |
| Zweistufig, zustandsbehaftet (Kafka-Quelle + Shuffle) | `maxPartitions` = 8, Shuffle-Partitionen = 20 | 28 (8+20) |
| Dreistufig (Kafka-Quelle + Shuffle + Repartition) | `maxPartitions` = 8, zwei Shuffle-Stages à 20 | 48 (8+20+20) |

- `maxPartitions` nicht gesetzt → Partitionsanzahl des Kafka-Topics wird verwendet.

## 3. Tutorial: Erste Real-Time-Query

1. Notebook mit Real-Time-Mode-Cluster erstellen, Python oder Scala wählen.
2. Query starten (`display` mit `realTime`-Trigger ab DBR 17.1):

```python
inputDF = (
  spark.readStream
  .format("rate")  # Testdaten ohne externe Abhängigkeiten
  .option("numPartitions", 2)
  .option("rowsPerSecond", 1)
  .load()
)
display(inputDF, realTime="5 minutes", outputMode="update")
# Ergebnis: Ausgabetabelle aktualisiert sich fortlaufend mit `timestamp` und
# monoton steigendem `value` pro neuer Zeile — sofortige Verarbeitung ohne
# Warten auf Batch-Grenzen.
```

- `numPartitions`/`rowsPerSecond` steuern Partitionierung/Rate.
- `realTime="5 minutes"` / `Trigger.RealTime()`: Intervall bestimmt Checkpointing-Häufigkeit (länger = seltener, aber potenziell längere Recovery).
- `outputMode="update"` / `OutputMode.Update()` ist Pflicht.

## 4. Performance optimieren und überwachen

**Compute-Tuning:**
- Anders als Micro-Batch: Real-Time-Tasks können im Leerlauf auf Daten warten — sorgfältiges Sizing essenziell.
- Zielauslastung (z. B. 50 %) über `maxPartitions` (Kafka) und `spark.sql.shuffle.partitions` (Shuffle-Stages) abstimmen.
- `maxPartitions` so setzen, dass jeder Task mehrere Kafka-Partitionen verarbeitet (Overhead ↓).
- Task-Slots pro Worker an einfache, einstufige Jobs anpassen.
- Bei Shuffle-intensiven Jobs experimentell minimale Shuffle-Partitionszahl ohne Backlog ermitteln — Compute plant den Job nicht ein, wenn zu wenig Slots vorhanden.
- Ab DBR 16.4 LTS: alle Real-Time-Pipelines nutzen Checkpoint v2 → nahtloser Wechsel Real-Time ↔ Micro-Batch.

**Latenzoptimierung (optional, standardmäßig deaktiviert):**
- **Asynchronous progress tracking:** Offset-/Commit-Log-Schreibvorgänge in asynchronen Thread verschoben → weniger Zeit zwischen Batches bei zustandslosen Queries.
- **Asynchronous state checkpointing:** nächster Micro-Batch startet sofort nach Berechnung, ohne auf State-Checkpointing-Abschluss zu warten → weniger Latenz bei zustandsbehafteten Queries.

**Monitoring: `StreamingQueryProgress`-Metriken**
- Traditionelle Batch-Dauer-Metriken spiegeln die tatsächliche E2E-Latenz in Real-Time Mode NICHT wider.
- Automatisch in Driver-Logs protokolliert; zugänglich via `onQueryProgress()` des `StreamingQueryListener`. `QueryProgressEvent.json()`/`toString()` enthalten `rtmMetrics`:

| Metrik | Beschreibung | Aggregationsebene |
|---|---|---|
| `processingLatencyMs` | Zeit zwischen Lesen eines Datensatzes und Schreiben in nächste Stage/Downstream. Bei einstufigen Queries = E2E-Latenz. | pro Task |
| `sourceQueuingLatencyMs` | Zeit zwischen Schreiben auf Message Bus (z. B. Kafka-Log-Append) und erstem Lesen durch die Query. | pro Task |
| `e2eLatencyMs` | Zeit zwischen Schreiben auf Message Bus und Downstream-Schreiben durch die Query. | pro Batch, über alle Tasks aggregiert |

```json
"rtmMetrics" : {
    "processingLatencyMs" : {"P0":0,"P50":0,"P90":0,"P95":0,"P99":0},
    "sourceQueuingLatencyMs" : {"P0":0,"P50":1,"P90":1,"P95":2,"P99":3},
    "e2eLatencyMs" : {"P0":0,"P50":1,"P90":1,"P95":2,"P99":4}
}
```

**Benutzerdefinierte Latenzmessung mit Observe API** — inline Messung ohne separaten Job; bei vorhandenem Quell-Zeitstempel Latenz pro Batch schätzen, indem vor der Senke ein Zeitstempel aufgezeichnet und die Differenz berechnet wird:

```python
from datetime import datetime
from pyspark.sql.functions import avg, col, lit, max, percentile_approx, udf, unix_millis
from pyspark.sql.types import TimestampType

@udf(returnType=TimestampType())
def current_timestamp():
  return datetime.now()

# Vor dem Schreiben in die Senke:
.withColumn("temp-timestamp", current_timestamp())
.withColumn("latency", unix_millis(col("temp-timestamp")).cast("long") - unix_millis(col("timestamp")).cast("long"))
.observe(
  "observedLatency",
  avg(col("latency")).alias("avg"),
  max(col("latency")).alias("max"),
  percentile_approx(col("latency"), lit(0.99), lit(150)).alias("p99"),
  percentile_approx(col("latency"), lit(0.5), lit(150)).alias("p50"))
.drop(col("latency"))
.drop(col("temp-timestamp"))
# .writeStream ...
```

- Ergebnisse erscheinen in Fortschrittsberichten, Listener-Zugriff via `observedMetrics`:
```json
"observedMetrics" : {
  "observedLatency" : {"avg": 63.84, "max": 219, "p99": 154, "p50": 49}
}
```

## 5. Referenz: Unterstützte Umgebungen, Quellen, Senken, Operatoren

**Sprachen und Compute** — unterstützte Sprachen: Scala, Java, Python.

| Compute-Typ | Unterstützt |
|---|---|
| Dedicated (früher Single User) | Ja |
| Standard (früher Shared) | Ja (nur Python) |
| Lakeflow Pipelines (Classic/Serverless) | Nicht als Structured Streaming; nur über eigene Pipeline-Konfiguration |
| Serverless | Nein |

- Latenzsensitive UDF-Workloads: Dedicated Access Mode empfohlen (Standard-Modus hat Sicherheitsisolations-Overhead).

**Ausführungsmodus:** nur **Update-Modus**; Append und Complete nicht unterstützt.

**Quellen und Senken**

| Quelle/Senke | Als Quelle | Als Senke |
|---|---|---|
| Apache Kafka | Ja | Ja |
| Event Hubs (via Kafka-Connector) | Ja | Ja |
| Kinesis | Ja (EFO-Modus empfohlen) | Nein |
| AWS MSK | Ja | Nein |
| Delta | Nein | Nein |
| Google Pub/Sub | Nein | Nein |
| Apache Pulsar | Nein | Nein |
| Beliebige Senken (`forEachWriter`) | — | Ja |

**Operatoren**

| Kategorie | Details |
|---|---|
| Zustandslos | Selection Ja, Projection Ja, `mapPartitions` Nein (siehe Einschränkungen), Union Ja (mit Einschränkungen) |
| UDFs | Scala UDF Ja (mit Einschränkungen), Python UDF Ja (mit Einschränkungen) |
| Aggregation | `sum`, `count`, `max`, `min`, `avg` und weitere Spark-Aggregationsfunktionen: Ja |
| Windowing | Tumbling Ja, Sliding Ja, Session Nein |
| Deduplizierung | `dropDuplicates` Ja, `dropDuplicatesWithinWatermark` Ja |
| Stream-to-Table-Join | Inner Ja, Outer Ja, Broadcast-Join (Tabelle ≤ 10 MB) Ja, Join ohne Broadcast Nein |
| Stream-to-Stream-Join | Inner Ja (DBR 18 LTS+, mit Konfiguration, siehe Abschnitt 2), Outer Nein |
| Beliebiger zustandsbehafteter Operator | `(flat)MapGroupsWithState` Nein, `transformWithState` Ja (mit Unterschieden, siehe unten) |
| Benutzerdefinierte Senken | `forEach` Ja, `forEachBatch` Nein |

**`transformWithState` — Unterschiede zum Micro-Batch-Modus:**
- `handleInputRows(key, inputRows: Iterator[T], timerValues)` wird **pro Zeile** aufgerufen — Iterator liefert nur **einen** Wert (Micro-Batch: alle Werte eines Schlüssels im Batch).
- **Event-Time-Timer nicht unterstützt.**
- `transformWithStateInPandas` nicht unterstützt → stattdessen zeilenbasierte `transformWithState`-API mit `Row`-Objekten.
- Timer-Auslösung verzögert sich nach Dateneingang: Timer für 10:00:00 löst nicht sofort ohne Daten; treffen Daten um 10:00:10 ein → 10 s Verzögerung; endet lang laufender Batch ohne neue Daten → Timer löst vor Batch-Ende aus.
- DBR 18.1 und darunter: `transformWithState` + Real-Time Mode + Python bei < 5 Datensätzen/s → Latenzen bis zu einigen 100 ms möglich; Upgrade auf DBR 18.2+ empfohlen.

**Python-UDFs in Real-Time Mode**

| Kategorie | UDF-Typ | Unterstützt |
|---|---|---|
| Zustandslos | Python-Scalar-UDF | Ja |
| Zustandslos | Arrow-Scalar-UDF | Ja |
| Zustandslos | Pandas-Scalar-UDF | Ja |
| Zustandslos | Arrow-Funktion (`mapInArrow`) | Ja |
| Zustandslos | Pandas-Funktion (Map) | Ja |
| Zustandsbehaftete Gruppierung (UDAF) | `transformWithState` (nur `Row`-Interface) | Ja |
| Zustandsbehaftete Gruppierung (UDAF) | `transformWithStateInPandas` | Nein |
| Zustandsbehaftete Gruppierung (UDAF) | `applyInPandasWithState` | Nein |
| Nicht-zustandsbehaftete Gruppierung (UDAF) | `apply`, `applyInArrow`, `applyInPandas` | Nein |
| Table Functions | UDTF, UC UDF | Nein |

- Minimale Latenz: `spark.sql.execution.arrow.maxRecordsPerBatch = 1` (Trade-off: Durchsatz ↓) — für die meisten Workloads empfohlen; nur bei höherem Durchsatzbedarf erhöhen (höhere Latenz).
- Pandas-UDFs/-Funktionen funktionieren mit Batch-Größe 1 schlecht — Batch-Größe erhöhen (z. B. ≥ 100) = höhere Latenz. Wo möglich Arrow-UDFs/-Funktionen bevorzugen.
- Latenzsensitive UDF-Workloads → Dedicated Access Mode.

## 6. Bekannte Einschränkungen

- **Quellen:** Kinesis — EFO-Modus für niedrigste Latenz empfohlen; häufige Repartitionierungen können Latenz negativ beeinflussen.
- **Union:**
  - Self-Union nicht unterstützt — Kafka: kein Union desselben Quell-DataFrames mit davon abgeleiteten DataFrames (Workaround: unterschiedliche DataFrames derselben Quelle); Kinesis: kein Union von DataFrames derselben Quelle/Konfiguration (Workaround: unterschiedliche `consumerName`-Option je DataFrame).
  - Zustandsbehaftete Operatoren (`aggregate`, `deduplicate`, `transformWithState`) dürfen nicht **vor** dem Union stehen.
  - Union mit Batch-Quellen nicht unterstützt.
- **`mapPartitions`:** (Scala) und ähnliche Python-APIs (`mapInPandas`, `mapInArrow`) verursachen Performance-Probleme — blockieren gesamte Ausgabe (höhere Latenz), unterstützen Watermark-Weitergabe schlecht. Stattdessen skalare UDFs (kombiniert mit "Transform complex data types" oder `filter`) verwenden.
- **`transformWithStateInPandas`:** nicht unterstützt — für benutzerdefinierte zustandsbehaftete Python-Verarbeitung zeilenbasierte `transformWithState`-API mit `Row`-Objekten verwenden.

## 7. Beispiele

**Voraussetzungen:** laufender Real-Time-Mode-Cluster; Kafka-Beispiele: Broker mit konfigurierten Topics; Kinesis: EFO-konfigurierter Stream + AWS-Credentials; Lakebase: konfigurierte Lakebase-Datenbank; benutzerdefinierte Senken: konfigurierter Zieldienst.

### Zustandslose Beispiele

- Jeder Datensatz wird unabhängig ohne Zustand verarbeitet — einfacher, niedrigere Latenz, kein State-Storage/Lookup.
- Geeignet für Transformationen, Filterung, Joins mit statischen Daten, Routing.

**Kafka → Kafka:**
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

**Repartition:** aktuelle Implementierungseinschränkung → `spark.sql.execution.sortBeforeRepartition` vor `repartition` auf `false` setzen (Sortierung bei Repartition in Real-Time Mode nicht unterstützt):
```python
spark.conf.set("spark.sql.execution.sortBeforeRepartition", "false")

query = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("subscribe", input_topic)
    .option("startingOffsets", "earliest")
    .load()
    .repartition(20)
    .writeStream.format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("topic", output_topic)
    .option("checkpointLocation", checkpoint_location)
    .trigger(realTime="5 minutes")
    .outputMode("update")
    .start()
)
```

**Stream-Snapshot-Join (nur Broadcast):** nur Stream-Static-Joins mit Broadcast der statischen Tabelle unterstützt — Tabelle muss in den Speicher passen:
```python
from pyspark.sql.functions import broadcast, expr

query = (
    spark.readStream.format("kafka")
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
    .writeStream.format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("topic", output_topic)
    .option("checkpointLocation", checkpoint_location)
    .trigger(realTime="5 minutes")
    .outputMode("update")
    .start()
)
```

**Kinesis → Kafka:**
```python
query = (
    spark.readStream.format("kinesis")
        .option("region", region_name)
        .option("awsAccessKey", aws_access_key_id)
        .option("awsSecretKey", aws_secret_access_key)
        .option("consumerMode", "efo")
        .option("consumerName", consumer_name)
        .load()
        .selectExpr("partitionKey AS key", "CAST(data AS STRING) AS value")
        .writeStream.format("kafka")
        .option("kafka.bootstrap.servers", broker_address)
        .option("topic", output_topic)
        .option("checkpointLocation", checkpoint_location)
        .trigger(realTime="5 minutes")
        .outputMode("update")
        .start()
)
```

**Union zweier Kafka-Topics:**
```python
df1 = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", broker_address) \
    .option("startingOffsets", "earliest") \
    .option("subscribe", input_topic_1).load()
df2 = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", broker_address) \
    .option("startingOffsets", "earliest") \
    .option("subscribe", input_topic_2).load()

query = (
    df1.union(df2)
    .writeStream.format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("topic", output_topic)
    .option("checkpointLocation", checkpoint_location)
    .trigger(realTime="5 minutes")
    .outputMode("update")
    .start()
)
```

**Kafka → Lakebase (in Unity Catalog registriert, Credentials automatisch verwaltet):**
```python
query = (
    spark.readStream.format("kafka")
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
# Existiert die Tabelle nicht, erstellt der Connector sie mit `upsertkey` als Primärschlüssel.
```

**Kafka → Lakebase (nicht in Unity Catalog registriert):** `format("postgresql")` + Optionen `endpoint` (`<project-id>.<branch-id>.<endpoint-id>`) und `dbtable` (`<schema>.<table>`):
```python
query = (
    spark.readStream.format("kafka")
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

### Zustandsbehaftete Beispiele

- Halten Zustand über Datensätze hinweg (Deduplizierung, Aggregation, Windowing) — mehr Speicher/Rechenressourcen nötig, aber dieselbe Semantik wie Micro-Batch, kontinuierlich für niedrigere Latenz.

**Deduplizierung:**
```python
query = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("startingOffsets", "earliest")
    .option("subscribe", input_topic)
    .load()
    .dropDuplicates(["timestamp", "value"])
    .writeStream.format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("topic", output_topic)
    .option("checkpointLocation", checkpoint_location)
    .trigger(realTime="5 minutes")
    .outputMode("update")
    .start()
)
```

**Aggregation:**
```python
from pyspark.sql.functions import col

query = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("startingOffsets", "earliest")
    .option("subscribe", input_topic)
    .load()
    .groupBy(col("timestamp"), col("value"))
    .count()
    .selectExpr("CAST(value AS STRING) AS key", "CAST(count AS STRING) AS value")
    .writeStream.format("kafka")
    .option("kafka.bootstrap.servers", broker_address)
    .option("topic", output_topic)
    .option("checkpointLocation", checkpoint_location)
    .trigger(realTime="5 minutes")
    .outputMode("update")
    .start()
)
```

**`transformWithState` mit TTL:** zählt Datensätze pro Schlüssel, pflegt Zähler redundant in `ValueState`, `ListState`, `MapState` (je TTL 30000 ms):

```python
class RTMStatefulProcessor(StatefulProcessor):
  def init(self, handle: StatefulProcessorHandle) -> None:
    state_schema = StructType([StructField("value", LongType(), True)])
    self.value_state = handle.getValueState("value", state_schema, 30000)
    map_key_schema = StructType([StructField("key", LongType(), True)])
    map_value_schema = StructType([StructField("value", StringType(), True)])
    self.map_state = handle.getMapState("map", map_key_schema, map_value_schema, 30000)
    list_schema = StructType([StructField("value", StringType(), True)])
    self.list_state = handle.getListState("list", list_schema, 30000)

  def handleInputRows(self, key, rows, timerValues) -> Iterator[Row]:
    for row in rows:  # Real-Time Mode: Iterator liefert genau eine Zeile
      key_str = row[0]
      source_timestamp = row[1]
      old_value = self.value_state.get()
      if old_value is None:
        old_value = 0
      self.value_state.update((old_value + 1,))
      self.map_state.update((old_value,), (key_str,))
      self.list_state.appendValue((key_str,))
      yield Row(key=key_str, value=old_value + 1, timestamp=source_timestamp)

query = (
  spark.readStream.format("kafka")
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
  .writeStream.format("kafka")
  .option("kafka.bootstrap.servers", broker_address)
  .option("topic", output_topic)
  .option("checkpointLocation", checkpoint_location)
  .trigger(realTime="5 minutes")
  .outputMode("Update")
  .start()
)
```

### Entwicklung und Testing

- `display`-Funktion (mit `realTime`-Trigger ab DBR 17.1) visualisiert Real-Time-Streaming-Daten direkt im Notebook — Query-Logik prüfen vor Deployment gegen Produktions-Senken (Kafka, benutzerdefinierte Senken), ohne externe Infrastruktur.

### Benutzerdefinierte Senken mit `foreach`

- Für Ziele ohne eingebaute Structured-Streaming-Unterstützung: `foreach`/`foreachSink` mit eigener `ForeachWriter`-Implementierung — volle Kontrolle über Schreiblogik, Integration mit beliebigen Datenbanken/APIs/Speichersystemen.

**Stand:** 2026-09-14.
