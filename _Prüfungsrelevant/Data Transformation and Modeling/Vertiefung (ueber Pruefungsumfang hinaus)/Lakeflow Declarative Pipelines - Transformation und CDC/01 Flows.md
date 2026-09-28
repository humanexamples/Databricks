# Flows in Lakeflow Declarative Pipelines

## 1. Was ist ein Flow?

Ein Flow ist die kleinste Verarbeitungseinheit einer Pipeline: eine **Query**, die ihr Ergebnis in ein **Target** (Tabelle/Sink) schreibt — batch oder inkrementell als Stream. Am einfachsten sichtbar am Standardfall, der beim Anlegen einer Streaming Table automatisch entsteht:

```sql
CREATE OR REFRESH STREAMING TABLE customers_silver
AS SELECT * FROM STREAM(customers_bronze);
-- Die Query "SELECT * FROM STREAM(customers_bronze)" IST hier bereits der Flow —
-- er heißt automatisch genauso wie die Tabelle: "customers_silver".
```

## 2. Flow-Typen im Überblick

Es gibt sechs Flow-Typen — sie unterscheiden sich darin, *wie* die Query verarbeitet wird (Batch oder Streaming) und *wohin* sie schreiben darf. Ausführliche Beispiele zu den meisten davon folgen weiter unten in dieser Datei; hier nur die Kernsyntax zur Einordnung:

- **Append** (Streaming, Ziel: Streaming Table oder Sink) — der häufigste Typ, hängt neue Zeilen einfach an. Vollständige Beispiele: Abschnitt 7 (mehrere Kafka-Topics) und 8 (mehrere Quellen statt `UNION`).
  ```python
  @dp.append_flow(target = "customers_silver")
  def my_flow():
    return spark.readStream.table("customers_bronze")
  ```
- **Materialized View** (Batch, Ziel: nur MV) — entsteht implizit, sobald man eine MV definiert; verarbeitet wo möglich nur neue/geänderte Daten (siehe `REFRESH POLICY` in der SQL-Referenz-Datei).
  ```sql
  CREATE MATERIALIZED VIEW daily_revenue AS 
  SELECT order_date, SUM(amount) 
  FROM orders 
  GROUP BY order_date;
  ```
- **Auto CDC** (Streaming, Ziel: nur Streaming Table) — verarbeitet Insert/Update/Delete-Events, inkl. SCD Typ 1/2. Nur `keys`/`KEYS` und `sequence_by`/`SEQUENCE BY` sind Pflicht, der Rest ist optional:
  ```sql
  CREATE FLOW apply_cdc AS 
  AUTO CDC INTO customers_history 
  FROM stream(customers_cdc) 
  KEYS (customer_id) SEQUENCE BY change_timestamp
  STORED AS SCD TYPE 2;
  ```
  ```python
  @dp.table
  def customers_cdc_source():
    return spark.readStream.table("customers_cdc")

  dp.create_streaming_table("customers_history")
  dp.create_auto_cdc_flow(
    target = "customers_history",
    source = "customers_cdc_source",
    keys = ["customer_id"],
    sequence_by = "change_timestamp",
    stored_as_scd_type = "2")
  ```
  Weitere optionale Parameter (`IGNORE NULL UPDATES`, `COLUMNS`/`TRACK HISTORY ON` als Ein-/Ausschlussliste, `COLUMNS TO UPDATE`, `APPLY AS DELETE/TRUNCATE WHEN`, zusammengesetzte Keys, eigener Flow-Name über `name`/`flow_name`, Bitemporal) — jeweils mit eigenem Codebeispiel: [`03 Change Data Capture (CDC).md`](03%20Change%20Data%20Capture%20%28CDC%29.md), Abschnitt 4 und 10. Vollständiges Backfill-Beispiel mit `AUTO CDC`: Abschnitt 11.2 dieser Datei.
- **REPLACE WHERE** (Batch, Ziel: Streaming Table) — ersetzt nur ein per Prädikat definiertes Zeilenfenster, statt die ganze Tabelle neu zu schreiben (z. B. nur die letzten 7 Tage neu berechnen):
  ```sql
  CREATE FLOW orders_enriched AS 
  INSERT INTO orders_enriched BY NAME
  REPLACE WHERE date >= date_add(current_date(), -7)
  SELECT * FROM orders_fct;
  ```
  ```python
  @dp.table(replace_where = "date >= date_add(current_date(), -7)")
  def orders_enriched():
    return spark.read.table("orders_fct")
  ```
  
  **`BY NAME`** ordnet die Spalten der `SELECT`-Liste anhand ihres **Namens** der Zieltabelle zu, statt anhand ihrer Position. Es gibt dafür genau drei Alternativen direkt nach dem Zieltabellennamen:
  
  ```sql
  -- a) Explizite Spaltenliste — positional, aber nur für die genannten Spalten
  INSERT INTO orders_enriched (order_id, date, amount) SELECT order_id, date, amount FROM orders_fct;
  
  -- b) BY NAME — Zuordnung nach Spaltenname (siehe oben)
  INSERT INTO orders_enriched BY NAME SELECT * FROM orders_fct;
  
  -- c) Default: gar nichts angeben
  INSERT INTO orders_enriched SELECT * FROM orders_fct;
  ```
  
  **Default-Verhalten (Fall c):** Ohne Spaltenliste und ohne `BY NAME` gilt dasselbe wie bei einer expliziten Liste aller Spalten in Definitionsreihenfolge der Tabelle. Es wird also wieder **positional** zugeordnet, diesmal gegen alle Spalten der Zieltabelle in ihrer Definitionsreihenfolge:
  
  ```sql
  -- Zieltabelle: orders_enriched(order_id, date, region)
  INSERT INTO orders_enriched SELECT region, order_id, date FROM staging;
  -- FALSCH, aber kein Fehler: 1. SELECT-Spalte (region) -> 1. Zielspalte (order_id), usw.
  ```
  
  Bei `SELECT * FROM orders_fct` (wie im Flow-Beispiel oben) hängt die Spaltenreihenfolge von der Quelltabelle ab — stimmt sie nicht exakt mit der Zieltabelle überein, landen bei Fall c Werte unbemerkt in falschen Spalten. Deshalb steht im Flow-Beispiel bewusst `BY NAME`.
- **REPLACE USING** *(Beta, Databricks Runtime 18.2+, Streaming, Ziel: Streaming Table)* — ersetzt in der Zieltabelle alle Zeilen, die zu den angegebenen Schlüsselspalten passen, restliche Zeilen bleiben unverändert. Gedacht für eine Quelle aus **partiellen, wiederholten Snapshots** (z. B. nur die zuletzt geänderten Zahlungen), nicht für einen einzelnen Vollbestand. `SEQUENCE BY` sorgt dafür, dass je Schlüssel der **höchste** Sequenzwert gewinnt, auch bei unsortiert eintreffenden Updates. `BY NAME` ist Pflicht, die Quelle muss eine Streaming-Abfrage sein, und `REPLACE USING` lässt sich nicht mit `ONCE` oder `AUTO CDC ... INTO` kombinieren:
  ```sql
  CREATE OR REFRESH STREAMING TABLE payments_latest;

  CREATE FLOW payments_replace_flow AS
  INSERT INTO payments_latest BY NAME
  REPLACE USING (payment_id) SEQUENCE BY payment_date
  SELECT payment_id, booking_id, status, payment_date
  FROM STREAM(samples.wanderbricks.payments);
  -- Ergebnis: pro payment_id bleibt nur die Zeile mit dem größten payment_date übrig,
  -- Zahlungen mit anderer payment_id in der Tabelle bleiben unangetastet.
  ```
  ```python
  from pyspark import pipelines as dp

  dp.create_streaming_table("payments_latest")

  @dp.replace_flow(
    target = "payments_latest",
    replace_using = ["payment_id"],
    sequence_by = "payment_date")
  def payments_replace_flow():
    return spark.readStream.table("samples.wanderbricks.payments")
  ```
  Mehrere Schlüsselspalten sind möglich (`replace_using = ["region", "account_id"]` in Python bzw. `REPLACE USING (region, account_id)` in SQL) — dann muss die Schlüssel-**Kombination** übereinstimmen, damit eine Zeile ersetzt wird.
- **Update** *(Public Preview, Streaming, Ziel: nur Sink, kein Delta)* — für globale, nicht-watermarked Aggregate, bei denen nur geänderte Zeilen geschrieben werden. Vollständiges Beispiel: Abschnitt 6.

**Nebenbei:** Alle Typen außer `Update` gibt es in SQL **und** Python; `Update` nur in Python. `Append`/`Update` entsprechen den gleichnamigen Structured-Streaming-Output-Modes; `Auto CDC` ist eine Lakeflow-exklusive Erweiterung ohne Structured-Streaming-Äquivalent; der *Complete*-Output-Mode ist als Flow-Typ nicht freigeschaltet.

## 3. Standard-Flow vs. explizit definierter Flow

Beim Anlegen einer Tabelle entsteht meist automatisch ein **Standard-Flow** (bei Streaming Table: Append-Flow, gleicher Name wie Tabelle):

```sql
CREATE OR REFRESH STREAMING TABLE customers_silver
AS SELECT * FROM STREAM(customers_bronze)
```

```python
from pyspark import pipelines as dp

@dp.table()
def customers_silver():
  return spark.readStream.table("customers_bronze")
```

Getrennt vom Ziel definiert (identisches Ergebnis/Name):

```python
dp.create_streaming_table("customers_silver")

@dp.append_flow(target = "customers_silver")
def customer_silver():
  return spark.readStream.table("customers_bronze")
```

```sql
CREATE OR REFRESH STREAMING TABLE customers_silver;

CREATE FLOW customers_silver
AS INSERT INTO customers_silver BY NAME
SELECT * FROM STREAM(customers_bronze);
```

- Einsatzzweck getrennter Definition: mehrere Flows an ein Ziel anhängen (neue Regionen ohne Full Refresh, Backfill, mehrere Quellen ohne `UNION`).
- **Gotcha:** Expectations müssen auf der **Zieltabelle** definiert werden — nicht innerhalb `@append_flow`.

## 4. Verarbeitungsmodi

**Inkrementell (Standard):** Ein Flow merkt sich per Checkpoint, was er schon verarbeitet hat, und liest bei jedem Lauf nur die **neuen** Datensätze seit dem letzten Mal — effizient bei Kafka/Auto Loader. Passiert automatisch bei jedem normalen Pipeline-Update, kein spezieller Befehl nötig.

**Full Refresh:** Verwirft den Checkpoint und verarbeitet die komplette Quelle neu — nötig z. B. nach einer geänderten Transformationslogik. Muss explizit ausgelöst werden:

```sql
REFRESH STREAMING TABLE customers_silver FULL;
-- Truncated die Tabelle und verarbeitet alle Quelldaten neu mit der aktuellen Flow-Definition.
```

## 5. Checkpoints und Flow-Namen

Jeder Flow verwaltet seinen eigenen Checkpoint (Fortschritts-Merker) unter seinem **Flow-Namen** — der Name *ist* also die Identität des Checkpoints, nicht nur eine Beschriftung:

```sql
-- Flow "customers_silver" hat einen eigenen Checkpoint unter diesem Namen.
CREATE FLOW customers_silver AS INSERT INTO customers_silver BY NAME
SELECT * FROM STREAM(customers_bronze);

-- Wird der Flow umbenannt, gibt es keinen passenden alten Checkpoint mehr dafür ->
-- der neue Name startet bei Null und verarbeitet ALLE Quelldaten erneut:
CREATE FLOW customers_silver_v2 AS INSERT INTO customers_silver BY NAME
SELECT * FROM STREAM(customers_bronze);
```

Daraus folgen drei praktische Konsequenzen:
- **Umbenennen = ungewolltes Full Reprocessing**, wie im Beispiel oben — nicht einfach zum Aufräumen umbenennen.
- **Fehler-Isolation:** Läuft ein Flow langsam oder schlägt fehl, hat das keinen Einfluss auf andere Flows derselben Pipeline — jeder hat seinen eigenen, unabhängigen Fortschritt.
- **Namen sind pro Pipeline einmalig:** Derselbe Flow-Name kann nicht für eine andere Query wiederverwendet werden — der alte Checkpoint würde nicht mehr zur neuen Query passen.

## 6. Update-Flows (Public Preview)

- Schreibt mit `update`-Output-Mode in einen **Sink**, nur pro Batch geänderte Zeilen.
- Unterstützt zustandsbehaftete Aggregationen **ohne Watermark** (globale Kennzahlen statt Anhängen).
- Delta-Tabellen **nicht** als Ziel unterstützt — nur Sink (z. B. Kafka). Nur Python.

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
)
def event_counts():
    return (
        spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", broker_address)
            .option("subscribe", input_topic)
            .load()
            .selectExpr("CAST(key AS STRING) AS event_type")
            .groupBy(col("event_type"))
            .count()
    )
```

- Über `spark_conf` zusätzlich für *Real-Time Mode* konfigurierbar (`pipelines.trigger: "RealTime"`, Public Preview).

## 7. Mehrere Kafka-Topics kombinieren (Fan-in)

Append-Flows kombinieren mehrere Quellen in ein Ziel, ohne `UNION` und ohne Full Refresh bei neuen Quellen:

```python
from pyspark import pipelines as dp

dp.create_streaming_table("kafka_target")

@dp.append_flow(target = "kafka_target")
def topic1():
  return (
    spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", "host1:port1,...")
      .option("subscribe", "topic1")
      .load()
  )

@dp.append_flow(target = "kafka_target")
def topic2():
  return (
    spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", "host1:port1,...")
      .option("subscribe", "topic2")
      .load()
  )
```

```sql
CREATE OR REFRESH STREAMING TABLE kafka_target;

CREATE FLOW topic1
AS INSERT INTO kafka_target BY NAME
SELECT * FROM read_kafka(bootstrapServers => 'host1:port1,...', subscribe => 'topic1');

CREATE FLOW topic2
AS INSERT INTO kafka_target BY NAME
SELECT * FROM read_kafka(bootstrapServers => 'host1:port1,...', subscribe => 'topic2');
```

Programmatisch aus einer Liste (**Gotcha:** Default-Parameter nötig, sonst Late-Binding-Fehler):

```python
from pyspark import pipelines as dp

dp.create_streaming_table("kafka_target")

topic_list = ["topic1", "topic2", "topic3"]

for topic_name in topic_list:

  @dp.append_flow(target = "kafka_target", name=f"{topic_name}_flow")
  def topic_flow(topic=topic_name):
    return (
      spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "host1:port1,...")
        .option("subscribe", topic)
        .load()
    )
```

## 8. Append-Flow-Verarbeitung statt `UNION`

Mehrere Quellen in eine Streaming Table, ohne Full Refresh bei neuer Quelle:

```python
dp.create_streaming_table("raw_orders")

@dp.append_flow(target="raw_orders")
def raw_orders_us():
  return spark.readStream \
    .format("cloudFiles") \
    .option("cloudFiles.format", "csv") \
    .load("/path/to/orders/us")

@dp.append_flow(target="raw_orders")
def raw_orders_eu():
  return spark.readStream \
    .format("cloudFiles") \
    .option("cloudFiles.format", "csv") \
    .load("/path/to/orders/eu")

# Weitere Flows ohne den bei UNION nötigen Full Refresh ergänzbar:
@dp.append_flow(target="raw_orders")
def raw_orders_apac():
  return spark.readStream \
    .format("cloudFiles") \
    .option("cloudFiles.format", "csv") \
    .load("/path/to/orders/apac")
```

```sql
CREATE OR REFRESH STREAMING TABLE raw_orders;

CREATE FLOW raw_orders_us
AS INSERT INTO raw_orders BY NAME
SELECT * FROM STREAM read_files("/path/to/orders/us", format => "csv");

CREATE FLOW raw_orders_eu
AS INSERT INTO raw_orders BY NAME
SELECT * FROM STREAM read_files("/path/to/orders/eu", format => "csv");

-- Weitere Flows ohne Full Refresh ergänzbar:
CREATE FLOW raw_orders_apac
AS INSERT INTO raw_orders BY NAME
SELECT * FROM STREAM read_files("/path/to/orders/apac", format => "csv");
```

## 9. `transformWithStateInPandas` in einem Flow

Beispiel: Sensor-Heartbeat-Überwachung — kein Heartbeat in 5 Min → Alarm-Eintrag.

- **Gotcha:** RocksDB ist ab DBR 17.3 Standard-State-Provider. Bei Provider-Exception: Config ergänzen, Full Refresh/Checkpoint-Reset, neu starten:

```json
"configuration": {
    "spark.sql.streaming.stateStore.providerClass": "com.databricks.sql.streaming.state.RocksDBStateStoreProvider",
    "spark.sql.streaming.stateStore.rocksdb.changelogCheckpointing.enabled": "true"
}
```

Gerüst (`StatefulProcessor` mit `init`, `handleInputRows`, `handleExpiredTimer`, `close`; Timer über `handle.registerTimer`/`deleteTimer`, Zustand über `handle.getValueState`):

```python
from typing import Iterator
import pandas as pd
from pyspark import pipelines as dp
from pyspark.sql.functions import col, from_json
from pyspark.sql.streaming import StatefulProcessor, StatefulProcessorHandle
from pyspark.sql.types import StructType, StructField, LongType, StringType, TimestampType

class SensorHeartbeatProcessor(StatefulProcessor):
    def init(self, handle: StatefulProcessorHandle) -> None:
        state_schema = StructType([
            StructField("sensor_type", StringType(), False),
            StructField("last_heartbeat_time", TimestampType(), False)])
        self.sensor_state = handle.getValueState("sensorState", state_schema)
        timer_schema = StructType([StructField("timer_ts", LongType(), False)])
        self.timer_state = handle.getValueState("timerState", timer_schema)
        self.handle = handle

    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        pdf = next(rows)
        row = pdf.iloc[0]
        current_time = pd.Timestamp(timerValues.getCurrentProcessingTimeInMs(), unit='ms')
        self.sensor_state.update((row["sensor_type"], current_time))
        if self.timer_state.exists():
            old_timer = self.timer_state.get()[0]
            self.handle.deleteTimer(old_timer)
        expiry_time = timerValues.getCurrentProcessingTimeInMs() + (5 * 60 * 1000)
        self.handle.registerTimer(expiry_time)
        self.timer_state.update((expiry_time,))
        return iter([])  # keine Ausgabe bei Input, nur bei Timer-Ablauf

    def handleExpiredTimer(self, key, timerValues, expiredTimerInfo) -> Iterator[pd.DataFrame]:
        if self.sensor_state.exists():
            state = self.sensor_state.get()
            output = pd.DataFrame({
                "sensor_id": [key[0]],
                "sensor_type": [state[0]],
                "last_heartbeat_time": [state[1]]})
            self.sensor_state.clear()
            self.timer_state.clear()
            yield output

    def close(self) -> None:
        pass

dp.create_streaming_table("sensorAlerts")

@dp.append_flow(target = "sensorAlerts")
def kafka_delta_flow():
    return (
      spark.readStream
        .format("kafka")
        .option("subscribe", "<your-kafka-topic>")
        .option("startingOffsets", "earliest")
        .load()
        .select(from_json(col("value").cast("string"), sensor_schema).alias("data"), col("timestamp"))
        .select("data.*", "timestamp")
        .withWatermark('timestamp', '1 hour')
        .groupBy(col("sensor_id"))
        .transformWithStateInPandas(
          statefulProcessor = SensorHeartbeatProcessor(),
          outputStructType = output_schema,
          outputMode = 'update',
          timeMode = 'ProcessingTime'))
```

## 10. Fan-in, Fan-out und Multiplexing

### 10.1 Fan-in: viele Quellen, ein Ziel

Konsolidiert mehrere Quellen (Streams, Cloud-Speicher, DBs, IoT) für konsistente Transformation/Dedup/Anreicherung. Append-Flows: kein `UNION`, kein manuelles Checkpointing — jede Quelle eigener Flow/Checkpoint, schreibt in dieselbe Streaming Table (siehe Abschnitte 7/8).

### 10.2 Fan-out: eine Quelle, viele Ziele

**a) `for`-Schleifen** für identische Logik pro Ziel:

```python
regions = ["US", "EU", "APAC"]

for region in regions:
    @dp.materialized_view(name=f"orders_{region.lower()}_filtered")
    def filtered_orders(region_filter=region):
        return spark.read.table("combined_orders").filter(f"region = '{region_filter}'")
```

- **Gotcha:** jede erzeugte Tabelle liest die komplette Quelle unabhängig — bei Kafka o. ä. Performance-Risiko.

**b) Unabhängige Flows/Views** bei deutlich unterschiedlicher Transformation je Ziel (je eigenes `@dp.materialized_view`).

**c) ForEachBatch** für individuelles Routing (Ziele ohne natives Streaming, z. B. JDBC; Beispiele in Abschnitt 12). Je nach Fall passt eine andere Flow-zu-Sink-Kombination: **ein Flow → ein Sink mit mehreren Ausgabezielen** eignet sich für einfache Multi-Output-Fälle mit gemeinsamer Logik (Beispiel: Abschnitt 12.4, "Zwei Ziele"). **Mehrere Flows → ein gemeinsamer Sink** passt, wenn Transformation/Fehlerbehandlung/Checkpoint zentral laufen sollen, z. B. bei vielen Topics/APIs (Beispiel: Abschnitt 12.4, "Basissyntax", erweiterbar um weitere `@dp.append_flow`). **Ein Flow → ein dedizierter Sink** eignet sich für viele unabhängige Streams mit isolierter Fehlerbehandlung.

### 10.3 Fan-in und Fan-out kombiniert

Typisch: Nutzeraktivität aus mehreren Apps (Fan-in) → Bronze-Tabelle + parallel Echtzeit-Alerting (Fan-out). Muster: `for`-Schleifen für Fan-in, `foreach_batch_sink` für Fan-out-Routing.

### 10.4 Multiplex-Pattern (Praxisbeispiel, kein offizieller Produktbegriff)

Aus Databricks-Blogpost (Fintech Uplift, 100+ Merchants, 100+ Kafka-/S3-Topics mit eigenem Schema). Klassisches `foreachBatch` scheiterte an: seriellen Writes (Laufzeit wächst je Zieltabelle), hartkodierter Komplexität (neues Topic = Code-Release), Starrheit (unterschiedliche Refresh-Raten), schlechter Cluster-Auslastung.

Lösung — Multiplexing + CDC + Meta-Programming, fünf Stufen:
1. **Bronze Stage 1:** ein `readStream` liest alle Kafka-Topics in eine gemeinsame Bronze-Tabelle (ein Checkpoint, ein Scan).
2. **Dynamische Topic-Erkennung:** View über Bronze Stage 1 ermittelt aktuell beobachtete Topics.
3. **Bronze Stage 2 — Fan-out per Meta-Programming:** je erkanntem Topic programmatisch eine Tabelle, neue Topics automatisch ohne Code-Änderung.
4. **Silver — CDC via `AUTO CDC ... INTO`:** SCD-Typ-1-Updates, separate JSON-Konfiguration für Expectations/Typ-Erzwingung.
5. **Gold — Aggregation** fürs Reporting.

Skelett Bronze-Stage-2-Fan-out:

```python
from pyspark import pipelines as dp

@dp.table(name="events_bronze")
def events_bronze():
    return spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "host1:port1,...") \
        .option("subscribe", "all-events") \
        .load()

event_types = ["order", "payment", "shipment"]

for event_type in event_types:
    @dp.table(name=f"events_{event_type}")
    def events_by_type(t=event_type):
        return spark.readStream.table("events_bronze").where(f"event_type = '{t}'")
```

- **Kernprinzip:** alle Aspekte jeder Tabelle über Konfiguration steuerbar (Schema, Expectations, Typ-Mappings, Refresh-Raten, Partitionierung) ohne Code-Änderung.
- **Ergebnis:** 100+ Notebooks → wenige Pipeline-Tasks (~98 % weniger Artefakte); parallele statt serielle Tabellengenerierung (Auto-Scaling); zentrales Data-Quality-Management via UI.
- **Warnung:** komplexes Streaming-Design-Pattern mit eigenen Trade-offs — erst Basis-Production-Practices etablieren.

### 10.5 Best Practices und Limitierungen

**Best Practices:** Schema muss bei Append-Flows zwischen Quelle/Ziel übereinstimmen (Expectations helfen bei Abweichung); `for`-Schleifen einfach halten, eindeutige Benennung, Ressourcen beobachten; bei Message Queues gemeinsamen `foreach_batch_sink` + konsolidierenden Append-Flow nutzen.

**Limitierungen:**
- Lineage-UI zeigt für neue Append-Flow-Quellen ggf. keine vollständigen Metriken.
- **Gotcha:** Werte aus `for`-Schleifen-Liste nur ergänzen, nie entfernen — ein weggelassener Eintrag lässt die Tabelle automatisch aus dem Ziel-Schema fallen → Datenverlust.
- `foreach_batch_sink` (Public Preview) schreibt Batches unabhängig — kein Rollback bereits erfolgreicher Writes bei Fehlschlag eines Ziels.

## 11. Backfill historischer Daten

Backfill = historische Daten nachträglich durch eine für aktuelle/streamende Daten konzipierte Pipeline verarbeiten (ML-Training, Datenqualitätskorrektur, geänderte Anforderungen).

Umsetzung über Append-Flow mit `ONCE` (SQL: `INSERT INTO ONCE`):

```python
from pyspark import pipelines as dp

@dp.table()
def csv_target():
  return spark.readStream \
    .format("cloudFiles") \
    .option("cloudFiles.format","csv") \
    .load("path/to/sourceDir")

@dp.append_flow(
  target = "csv_target",
  once = True)
def backfill():
  return spark.read \
    .format("cloudFiles") \
    .option("cloudFiles.format","csv") \
    .load("path/to/backfill/data/dir")
```

```sql
CREATE OR REFRESH STREAMING TABLE csv_target
AS SELECT * FROM read_files("path/to/sourceDir", "csv");

CREATE FLOW backfill
AS INSERT INTO ONCE csv_target BY NAME
SELECT * FROM read_files("path/to/backfill/data/dir", "csv");
```

**Überlegungen:**
- Historische Daten typischerweise an Bronze-Streaming-Table anhängen — Silver/Gold übernehmen automatisch.
- Pipeline muss Duplikate robust handhaben.
- Historisches und aktuelles Schema müssen kompatibel sein.
- Datenvolumen/SLA bei Cluster-/Batch-Dimensionierung berücksichtigen.

### 11.1 Ausführliches Beispiel: Backfill zu bestehender Pipeline

Ausgangslage: Pipeline liest Events ab 01.01.2025 (`modifiedAfter` begrenzt Inkrementell-Verarbeitung). Backfill der drei Vorjahre, partitioniert nach Jahr/Monat/Tag, JSON.

- **Muster:** `append once`-Flow läuft einmalig, bleibt danach idle (Code bleibt in Pipeline; bei Full Refresh läuft Backfill erneut). Pro Jahr eigener Flow — Python: Meta-Programming (Funktion + `for`-Schleife); SQL: Code je Flow wiederholt.

```python
from pyspark import pipelines as dp

source_root_path = spark.conf.get("registration_events_source_root_path")
begin_year = spark.conf.get("begin_year")
backfill_years = spark.conf.get("backfill_years")  # z. B. "2024,2023,2022"
incremental_load_path = f"{source_root_path}/*/*/*"

def setup_backfill_flow(year):
    backfill_path = f"{source_root_path}/year={year}/*/*"
    @dp.append_flow(
        target="registration_events_raw",
        once=True,
        name=f"flow_registration_events_raw_backfill_{year}",
        comment=f"Backfill {year} Raw registration events")
    def backfill():
        return spark.read.format("json").option("inferSchema", "true").load(backfill_path)

dp.create_streaming_table(name="registration_events_raw", comment="Raw registration events")

@dp.append_flow(
        target="registration_events_raw",
        name="flow_registration_events_raw_incremental",
        comment="Raw registration events")
def ingest():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.maxFilesPerTrigger", 100)
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .option("modifiedAfter", "2024-12-31T23:59:59.999+00:00")
        .load(incremental_load_path)
        .where(f"year(timestamp) >= {begin_year}")
    )

for year in backfill_years.split(","):
    setup_backfill_flow(year)
```

```sql
CREATE OR REFRESH STREAMING TABLE registration_events_raw;

CREATE FLOW registration_events_raw_incremental
AS INSERT INTO registration_events_raw BY NAME
SELECT * FROM STREAM read_files(
  "/Volumes/gc/demo/apps_raw/event_registration/*/*/*",
  format => "json", inferColumnTypes => true, maxFilesPerTrigger => 100,
  schemaEvolutionMode => "addNewColumns", modifiedAfter => "2024-12-31T23:59:59.999+00:00"
)
WHERE year(timestamp) >= '2025';

CREATE FLOW registration_events_raw_backfill_2024
AS INSERT INTO ONCE registration_events_raw BY NAME
SELECT * FROM read_files("/Volumes/gc/demo/apps_raw/event_registration/year=2024/*/*", format => "json", inferColumnTypes => true);

-- analog für 2023 und 2022
```

**Wichtige Muster:** Trennung der Zuständigkeiten (inkrementell unabhängig vom Backfill, eigene Konfiguration je Flow); `ONCE` garantiert genau einen Lauf (klare Audit-Spur); großer Backfill in Teil-Backfills aufteilbar (Enhanced Autoscaling); Schema-Evolution über `schemaEvolutionMode="addNewColumns"`.

### 11.2 SCD-Ziel während einer Migration befüllen

Szenario: SCD-Tabelle mit jahrelanger Historie aus Legacy-System, ursprünglicher Change Feed nicht mehr verfügbar → einmalige Einspielung in neues `AUTO CDC`-Ziel, danach frischer CDC-Feed.

- **Gotcha:** Ein `AUTO CDC`-Ziel akzeptiert nur `AUTO CDC`-Flows — einfacher `INSERT INTO ONCE`-Append-Flow schlägt bei Validierung fehl.

Ablauf: (1) Ziel-Streaming-Table anlegen; (2) Legacy-Historie via `AUTO CDC ONCE`-Flow einspielen, sequenziert nach Legacy-Gültigkeits-Startspalte (`AUTO CDC` baut `__START_AT`/`__END_AT` selbst — nicht direkt schreiben); (3) laufenden `AUTO CDC`-Flow für frischen Change Feed anhängen — erste Live-Änderung je Key muss zeitlich nach letzter geseedeter Änderung desselben Keys liegen.

```sql
CREATE OR REFRESH STREAMING TABLE customers_history;

-- Einmaliger Seed: Legacy-Historie als Change-Events wiederabspielen
CREATE FLOW customers_history_seed
AS AUTO CDC ONCE INTO customers_history
FROM stream(legacy.customers_scd2)
KEYS (customer_id)
SEQUENCE BY valid_from
STORED AS SCD TYPE 2;

-- Laufender Live-CDC-Flow in dasselbe Ziel
CREATE FLOW customers_history_cdc
AS AUTO CDC INTO customers_history
FROM stream(customers_cdc_bronze)
KEYS (customer_id)
SEQUENCE BY change_timestamp
STORED AS SCD TYPE 2;
```

- Beide Flows müssen bei Keys, SCD-Typ, Datentyp der Sequenzspalte übereinstimmen (sonst casten).
- Gleiches Muster für SCD Typ 1 (`STORED AS SCD TYPE 1` in beiden Flows).
- Vor Produktivbetrieb: an Key-Stichprobe validieren, dass erste Live-Änderung genau eine neue Version erzeugt und vorherige korrekt schließt.

## 12. ForEachBatch-Sink

Transformieren/Mergen/Schreiben in Ziele ohne native Streaming-Writes (Merge/Upsert in Delta, mehrere/nicht unterstützte Ziele, benutzerdefinierte Python-Transformationen). Konzipiert für Streaming-Queries wie `append_flow` — nicht für Batch-Pipelines oder `AUTO CDC`-Semantik.

### 12.1 Full Refresh

- ForEachBatch nutzt Streaming Query → Pipeline verfolgt Checkpoint je Flow. Bei Full Refresh: Checkpoint zurückgesetzt, Sink-Funktion sieht `batch_id` ab 0.
- **Gotcha:** Zieldaten werden dabei **nicht** automatisch bereinigt (Pipeline kennt Schreibziel nicht) — manuelles Leeren externer Tabellen/Speicherorte nötig.

### 12.2 Event-Log und Databricks Connect

- Sink-Erstellung erzeugt `SinkDefinition`-Event (`"format": "foreachBatch"`) im Event-Log.
- **Gotcha:** Nicht serialisierbare Funktion (Voraussetzung für Databricks Connect) → `WARN`-Eintrag. Parameter (z. B. via `dbutils`) **vor** dem UDF abrufen, als Wert übergeben.

### 12.3 Best Practices und Limitierungen

- Funktion knapp halten (kein Threading, keine schweren Abhängigkeiten, keine großen In-Memory-Manipulationen).
- Checkpoints pro Flow, nicht pro Sink.
- Externe Abhängigkeiten auf allen Cluster-Knoten validieren.
- Kein automatisches Housekeeping für ForEachBatch-Ziele.
- Für eine Quelle → mehrere Ziele: `df.persist()`/`df.cache()` in der Funktion (sonst mehrfache Reads).
- Databricks Connect: UDF muss serialisierbar sein, kein `dbutils`.

### 12.4 Beispiele

Basissyntax:

```python
from pyspark import pipelines as dp

@dp.foreach_batch_sink(name = "my_foreachbatch_sink")
def feb_sink(df, batch_id):
  # Merge, Schreiben an mehrere Ziele etc.
  return

@dp.table()
def example_source_data():
  return spark.range(5)

@dp.append_flow(target="my_foreachbatch_sink")
def my_flow():
  return spark.readStream.format("delta").table("example_source_data")
```

Zwei Ziele, idempotente Delta-Writes via `txnVersion`/`txnAppId` (fehlgeschlagener Write an eine Tabelle verhindert Doppel-Write an die bereits erfolgreiche):

```python
from pyspark import pipelines as dp

app_id = "my-app-name"  # unterschiedliche Anwendungen in dieselbe Tabelle -> eindeutige txnAppId

@dp.foreach_batch_sink(name="user_events_feb")
def user_events_handler(df, batch_id):
    df.write.format("delta").mode("append") \
     .option("txnVersion", batch_id).option("txnAppId", app_id) \
     .saveAsTable("my_catalog.my_schema.example_table_1")

    df.write.format("json").mode("append") \
      .option("txnVersion", batch_id).option("txnAppId", app_id) \
      .save("/tmp/json_target")
    return

@dp.table()
def example_source():
  return spark.range(5)

@dp.append_flow(target="user_events_feb", name="user_events_flow")
def read_user_events():
    return spark.readStream.format("delta").table("example_source")
```

Merge mit externer Delta-Tabelle (`DeltaTable.merge`):

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col
from delta.tables import DeltaTable

@dp.foreach_batch_sink(name = "external_merge_feb")
def foreachBatchFunc(df, batchId):
  out = DeltaTable.forName(df.sparkSession, $table)
  out.alias("target") \
    .merge(df.alias("source"), "source.value = target.value") \
    .whenMatchedUpdateAll() \
    .whenNotMatchedInsertAll() \
    .whenNotMatchedBySourceDelete() \
    .execute()

@dp.update_flow(target="external_merge_feb", name="merge_flow")
def read_data():
    return spark.readStream.format("delta").load("/tmp/source_delta_table").filter(col("value").isNotNull())
```

- **FAQ:** mehrere Flows (`@dp.append_flow`) können denselben ForEachBatch-Sink ansteuern, je eigener Checkpoint. Keine Datenretention/-bereinigung durch die Pipeline. Serialisierungsfehler: Cluster-Driver-Logs oder Event-Log.

**Stand:** 2026-09-14.
