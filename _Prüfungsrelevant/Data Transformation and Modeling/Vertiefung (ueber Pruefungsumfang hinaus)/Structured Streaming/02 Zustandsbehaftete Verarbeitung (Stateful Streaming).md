# Zustandsbehaftete Verarbeitung (Stateful Streaming)

## 1. Zustandslos vs. zustandsbehaftet

- **Zustandslos:** kein Zwischenzustand, keine zustandsbehafteten Operatoren. Beispiele: Stream-Static-Joins, `MERGE INTO` mit Delta, Operationen die nur tracken welche Zeilen Quelle→Senke schon verarbeitet wurden.
- **Zustandsbehaftet:** braucht inkrementelle Zwischenzustands-Updates. Beispiele: Streaming-Aggregation, `distinct`, `dropDuplicates`, Stream-Stream-Joins, eigene (custom) Stateful Apps.

### Optimierung zustandsloser Queries (DBR 18.0+)

```ini
# Adaptive Query Execution für zustandslose Streaming-Queries — standardmäßig aktiviert
spark.sql.adaptive.streaming.stateless.enabled true

# Auto Optimized Shuffle — erfordert zusätzlich aktiviertes AQE
spark.sql.shuffle.partitions auto
```

- Zustandslose Queries erlauben Ändern der **Anzahl Shuffle-Partitionen beim Neustart** (z. B. hohe Parallelität für Backfill, danach reduzieren):
```ini
spark.sql.shuffle.partitions <number>
```

## 2. Zustandsbehaftetes Streaming optimieren

- Compute-optimierte Instanztypen als Worker verwenden.
- Shuffle-Partitionen = 1x–2x Cluster-Cores.
- **Wichtig:** Shuffle-Partitionsanzahl wird bei **Checkpoint-Erstellung** fixiert. Spätere `spark.sql.shuffle.partitions`-Änderung wirkt sich auf bestehenden Checkpoint **nicht** aus → neuer Checkpoint-Pfad nötig (Ausnahmen: On-Demand State Repartitioning, Abschnitt 5; zustandslose Queries ab DBR 18.0, s. o.).

```ini
# verhindert Micro-Batches ohne Daten (sonst evtl. verzögerte Ausgabe bei Watermark/Processing-Time-Timeouts bis neue Daten eintreffen)
spark.sql.streaming.noDataMicroBatches.enabled false
```

- Empfohlen: **Changelog-Checkpointing mit RocksDB** (ab DBR 13.3 LTS) → senkt Checkpoint-Dauer und E2E-Latenz.
- **Hinweis:** State-Management-Schema (RocksDB vs. Standard) zwischen Neustarts nicht änderbar → neuer Checkpoint-Pfad nötig.

### Mehrere zustandsbehaftete Operatoren kombinieren (ab DBR 13.3 LTS)

- Ausgabe eines zustandsbehafteten Operators (z. B. gefensterte Aggregation) kann Eingabe eines weiteren sein (z. B. Join). Ab DBR 16.2 auch `transformWithState` einsetzbar.
- **Einschränkungen:** Legacy-Operatoren (`flatMapGroupsWithState`, `applyInPandasWithState`) nicht unterstützt; nur **Append**-Output-Modus erlaubt.

```python
# Verkettete Zeitfenster-Aggregation
windowedCounts = words.groupBy(
    window(words.timestamp, "10 minutes", "5 minutes"),
    words.word
).count()

anotherWindowedCounts = windowedCounts.groupBy(
    window(window_time(windowedCounts.window), "1 hour"),
    windowedCounts.word
).count()
```

```python
# Zeitfenster-Aggregation zweier Streams, dann Stream-Stream-Window-Join
clicksWindow = clicksWithWatermark.groupBy(
  clicksWithWatermark.clickAdId,
  window(clicksWithWatermark.clickTime, "1 hour")
).count()

impressionsWindow = impressionsWithWatermark.groupBy(
  impressionsWithWatermark.impressionAdId,
  window(impressionsWithWatermark.impressionTime, "1 hour")
).count()

clicksWindow.join(impressionsWindow, "window", "inner")
```

```python
# Stream-Stream-Zeitintervall-Join, dann Zeitfenster-Aggregation
joined = impressionsWithWatermark.join(
  clicksWithWatermark,
  expr("""
    clickAdId = impressionAdId AND
    clickTime >= impressionTime AND
    clickTime <= impressionTime + interval 1 hour
    """),
  "leftOuter"  # "inner", "leftOuter", "rightOuter", "fullOuter", "leftSemi"
)

joined.groupBy(
  joined.clickAdId,
  window(joined.clickTime, "1 hour")
).count()
```

### State Rebalancing

- Standardmäßig aktiviert in Lakeflow-Pipelines. Ab DBR 11.3 LTS via Cluster-Konfig aktivierbar:
```ini
spark.sql.streaming.statefulOperator.stateRebalancing.enabled true
```
- Nützt zustandsbehafteten Pipelines bei Cluster-Resizing (zustandslose profitieren nicht). Resizing löst Rebalancing aus; während Rebalancing kann Micro-Batch-Latenz steigen (Zustand wird vom Cloud-Speicher auf neue Executors geladen).
- **Hinweis:** Autoscaling hat Einschränkungen beim Herunterskalieren für Streaming — Databricks empfiehlt Lakeflow-Pipelines mit Enhanced Autoscaling.

## 3. Watermarks

- Entfernen automatisch alten Zustand → verhindern Speicherfehler/erhöhte Latenz. Steuern Schwellenwert, ab dem eine Zustandsentität (Fenster-Aggregat, Join-Key) nicht mehr verarbeitet wird.

```python
from pyspark.sql.functions import window

(df
  .withWatermark("event_time", "10 minutes")
  .groupBy(
    window("event_time", "5 minutes"),
    "id")
  .count()
)
# Ergebnis: Zustand für eine Zählung bleibt erhalten, bis Fensterende > 10 min älter als zuletzt beobachtete event_time
```

- **Wichtig:** Spalten in `groupBy()`/`window()` per Name referenzieren (`"<colName>"`/`col("<colName>")`, Scala auch `$colName`) — sonst geht der Event-Time-Marker verloren.
- Garantiert: Datensätze innerhalb des Schwellenwerts werden verarbeitet. Außerhalb: möglich, aber nicht garantiert.

### Latenz/Durchsatz-Abwägung

- **Kürzer:** geringere Latenz, weniger Zustand — aber geringe Toleranz für Verspätung.
- **Länger:** hohe Verspätungstoleranz — aber höhere Latenz, mehr Zustand.

### Watermarks × Output-Modus bei Windowed Aggregations

| Output-Modus | Verhalten |
|---|---|
| Append | Schreibt erst nach Watermark-Überschreitung (verzögert); alter Zustand danach verworfen. |
| Update | Schreibt sofort nach Berechnung, kann später überschreiben; alter Zustand nach Schwellenwert verworfen. |
| Complete | Zustand nie verworfen; jeder Trigger schreibt Zieltabelle vollständig neu. |

### Watermarks bei Stream-Stream-Joins

- Joins: nur Append-Modus, schreiben pro Batch die gematchten Zeilen.
- **Inner Join:** Watermark empfohlen (nicht zwingend) — ohne ihn versucht die Engine bei jedem Trigger jeden Key beidseitig zu joinen (Performance-Risiko).
- **Outer Join:** Watermark **verpflichtend**; ungematchte Zeilen werden mit `null` geschrieben, aber erst nach Überschreiten des Verspätungs-Schwellenwerts (Append-Modus).

### Multiple-Watermarks-Policy

```python
input_stream1 = ...      # delays up to 1 hour
input_stream2 = ...      # delays up to 2 hours

(input_stream1.withWatermark("eventTime1", "1 hour")
  .join(
    input_stream2.withWatermark("eventTime2", "2 hours"),
    joinCondition)
)
```

- Jeder Stream bekommt eigenen Watermark (aus jeweils max. Event-Zeit); global gilt standardmäßig das **Minimum** (`spark.sql.streaming.multipleWatermarkPolicy = min`) — verhindert fälschliches "zu spät", verzögert aber Ausgabe am Tempo des langsamsten Streams.
- `max`: schnellster Stream maßgeblich (geringere Latenz), aber Daten langsamerer Streams werden verworfen — Databricks rät zur Vorsicht.

### Watermarks bei `distinct`

```python
streamingDf = spark.readStream. ...  # columns: eventTime, id, value, ...

(streamingDf
  .withWatermark("eventTime", "1 hour")
  .distinct()
)
# Ergebnis: ohne Watermark wächst der Zustand unbegrenzt (jeder je gesehene Datensatz wird gehalten)
```

- **Wichtig:** Für Dedup nur bestimmter Spalten: `dropDuplicates()`/`dropDuplicatesWithinWatermark()` statt `distinct`.

### `dropDuplicatesWithinWatermark` (ab DBR 13.3 LTS)

- Exactly-once ≠ automatische Quell-Dedup. Entfernt Duplikate anhand eines beliebigen Schlüsselfelds, auch wenn andere Felder (z. B. Zeitstempel) zwischen Duplikaten abweichen.
- Garantiert dedupliziert: nur **innerhalb** des Watermark-Schwellenwerts. Watermark ist Pflicht; Schwellenwert > max. Zeitstempeldifferenz zwischen Duplikaten wählen.

```python
streamingDf = spark.readStream. ...

(streamingDf
  .withWatermark("eventTime", "10 hours")
  .dropDuplicatesWithinWatermark(["guid"])
)
```

- **Wichtig:** `dropDuplicates()`/`dropDuplicatesWithinWatermark()` können beim Neustart wegen State-Schema-Kompatibilitätsprüfung fehlschlagen, wenn der Compute-Access-Mode wechselt (siehe Kapitel "Grundlagen und Ausführungsmodell" → Checkpoints).

### Windowing-Beispiele

```python
# Tumbling Window: feste, nicht überlappende Größe — jede Zeile gehört zu genau 1 Fenster
hourly_sales = (orders
  .withWatermark("timestamp", "1 hour")
  .groupBy(window("timestamp", "1 hour"))
  .agg(sum("amount").alias("total_sales"))
)
# Ergebnis: eine Zeile je Stunde, z. B. [14:00,15:00): total_sales
```

```python
# Sliding Window: feste Größe, überlappende Intervalle — Zeile kann zu mehreren Fenstern gehören
rolling_sales = (orders
  .withWatermark("timestamp", "1 hour")
  .groupBy(window("timestamp", "6 hours", slideDuration="1 hour"))
  .agg(sum("amount").alias("total_sales"))
)
# Ergebnis: rollierender 6h-Umsatz, stündlich verschoben. slideDuration muss <= windowDuration sein
```

```python
# Session Window: keine feste Größe — öffnet bei erster Zeile, schließt nach Lückendauer ohne neue Zeile
sessionized_page_views = (activity
  .withWatermark("timestamp", "1 hour")
  .groupBy("user_id", session_window("timestamp", gapDuration="30 minutes"))
  .agg(sum("page_views").alias("total_page_views"))
)
# Ergebnis: eine Session je user_id-Aktivitätsausbruch (Lücke > 30 min beendet die Session)
```

- `timeColumn` von `window()`/`session_window()` muss `TimestampType`/`TimestampNTZType` sein; für Verarbeitungszeit statt Event-Zeit `current_timestamp()` nutzen.
- Fensterdauer: Mikrosekunden bis Tage — Monate+ nicht unterstützt.
- `complete`-Modus + gefensterte Aggregation → gesamter Fensterzustand unbegrenzt vorgehalten; `append` + passender Watermark begrenzt Zustandswachstum.

### SQL-Syntax: `WATERMARK`-Klausel (Lakeflow Streaming Tables)

- Funktional äquivalent zu `withWatermark(eventTime, delay)`: `WATERMARK [named_expression] DELAY OF [interval]`.

```sql
CREATE OR REFRESH STREAMING TABLE window_agg_1
AS SELECT window(ts, '10 seconds') as w, count(*) as CNT
FROM STREAM stream_source WATERMARK ts DELAY OF INTERVAL 10 SECONDS AS stream
GROUP BY window(ts, '10 seconds');
```

```sql
-- Watermark auf abgeleiteter Zeitstempelspalte
CREATE OR REFRESH STREAMING TABLE window_agg_2
AS SELECT window(ts, '10 seconds') as w, count(*) as CNT
FROM STREAM stream_source WATERMARK to_timestamp(ts_str) AS ts DELAY OF INTERVAL 10 SECONDS AS stream
GROUP BY window(ts, '10 seconds');
```

## 4. Structured-Streaming-Zustand lesen

- Braucht Leseberechtigung auf den Checkpoint-Pfad; Zugriff nur mit Batch-Read-Semantik.
- **Hinweis:** Zustand **nicht** lesbar für Lakeflow-Pipelines, Streaming-Tabellen, Materialized Views, Serverless Compute oder Standard-Access-Modus-Compute (Ausnahme s. Voraussetzungen).
- **Voraussetzungen:** DBR 16.3+ auf Standard-Access-Modus, oder DBR 14.3 LTS+ auf Dedicated-/No-Isolation-Modus, plus Leserecht auf Checkpoint-Pfad.

```python
df = spark.read.format("statestore").load("/checkpoint/path")
```
```sql
SELECT * FROM read_statestore('/checkpoint/path')
```

| Spalte | Typ | Beschreibung |
|---|---|---|
| `key` | Struct | Key eines Datensatzes des Operators |
| `value` | Struct | Wert eines Datensatzes des Operators |
| `partition_id` | Integer | Partition des State-Checkpoints |

Mit `readChangeFeed=true` (ab DBR 16.4 LTS) zusätzlich:

| Spalte | Typ | Beschreibung |
|---|---|---|
| `batch_id` | Long | Batch-ID der Zustandsänderung |
| `change_type` | String | `update` (Insert/Update) oder `delete` |
| `value` | Struct | `null` bei `change_type = delete` |

```python
# Zustandsänderungen über mehrere Batches lesen (ab DBR 16.4 LTS)
df = (spark.read
  .format("statestore")
  .option("readChangeFeed", True)
  .option("changeStartBatchId", 2)
  .load("<checkpointLocation>")
)
# optional zusätzlich: .option("changeEndBatchId", <id>)
```

```python
# Zustandsmetadaten lesen (ab DBR 14.3 LTS)
df = spark.read.format("state-metadata").load("<checkpointLocation>")
```
```sql
SELECT * FROM read_state_metadata('/checkpoint/path')
```

| Spalte | Typ | Beschreibung |
|---|---|---|
| `operatorId` | Integer | ID des zustandsbehafteten Operators |
| `operatorName` | String | Name des Operators |
| `stateStoreName` | String | Name des State Store |
| `numPartitions` | Integer | Anzahl Partitionen des State Store |
| `minBatchId` / `maxBatchId` | Long | Batch-ID-Bereich mit abfragbarem Zustand (nicht dauerhaft garantiert — alte Batches werden bereinigt) |

```python
# Eine Seite eines Stream-Stream-Joins abfragen
left_df = spark.read.format("statestore").option("joinSide", "left").load("/checkpoint/path")
```

```python
# Bei mehreren zustandsbehafteten Operatoren: erst Metadaten, dann gezielt per operatorId lesen
left_df = spark.read.format("statestore").option("operatorId", 1).load("/checkpoint/path")
```

## 5. On-Demand State Repartitioning (Public Preview)

- Ändert Partitionsanzahl einer zustandsbehafteten Query **ohne** Checkpoint-Verlust (sonst Standardverhalten: neuer Checkpoint nötig). Nützlich für Skalierung ohne Checkpoint-Neuaufbau.
- **Voraussetzungen:** DBR 18 LTS+; RocksDB-State-Store-Provider (ab DBR 17.3 Standard).

```python
query.stop()
spark.conf.set("spark.sql.streaming.stateStore.partitions", "<numPartitions>")
query = df.writeStream.start()
# Ergebnis: nach Neustart + Abschluss des zuletzt geplanten Micro-Batches führt die Query eine
# Repartitionierung durch, danach normale Verarbeitung. spark.sql.streaming.stateStore.partitions
# hat für zustandsbehaftete Queries Vorrang vor spark.sql.shuffle.partitions.
```

- **Monitoring:** `StreamingQueryProgress`-Ereignisse → `durationMs`-Metriken unter `controlBatch.REPARTITION` (Dauer der Repartitionierung in ms; größere Zustandsgröße = länger).

```python
# In Lakeflow-Pipelines: über spark_conf des @dp.table-/@dp.append_flow-Dekorators
from pyspark import pipelines as dp
from pyspark.sql import functions as F

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

## 6. Eigene Stateful Applications mit `transformWithState`

- Für beliebige (arbitrary) zustandsbehaftete Low-Latency-Anwendungen. Databricks empfiehlt `transformWithState` **statt** Legacy-Operatoren `flatMapGroupsWithState`/`mapGroupsWithState` (Abschnitt 9) — für Standard-Aggregation/Dedup/Joins weiterhin eingebaute Operatoren nutzen.

### Voraussetzungen

- `transformWithState`/`transformWithStateInPandas`: ab DBR 16.2. Real-Time-Modus: DBR 17.3 LTS+. Standard-Access-Modus: Python ab DBR 16.3+, Scala ab DBR 17.3+.
- RocksDB ist ab DBR 17.3 Standard-Provider; darunter manuell setzen:
```python
spark.conf.set("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")
```

### API-Varianten

- **PySpark:** zeilenbasiert `transformWithState` (einzig im **Real-Time-Modus** unterstützt, unterstützt Async via `asyncio`, s. Abschnitt 8 — Async nicht auf Serverless) und Pandas-basiert `transformWithStateInPandas`.
- **Scala:** nur zeilenbasierte API. Beide Sprachen: gleiche Fähigkeiten, andere Syntax.

### Design-Prinzip

- Eigene Klasse `StatefulProcessor` (bzw. `StatefulProcessorWithInitialState`) mit State-Variablen pro Gruppierungsschlüssel.
- Pro Micro-Batch: alle Zeilen eines Schlüssels als Iterator. `StatefulProcessorHandle`, Timer, eigene Bedingungen steuern die Ausgabe.
- State-Werte unterstützen individuelle TTL. State-Store unterstützt Schema-Evolution (Abschnitt 7) → Produktionscode iterierbar ohne Zustandsverlust.

### `StatefulProcessor` implementieren

- Spark übergibt `init` einen `StatefulProcessorHandle` (Python: Parameter `handle`; Scala: Methode `getHandle`) zum Erzeugen von State-Variablen/State-Store-Zugriff.

| Methode | Zweck |
|---|---|
| `handleInputRows` | Daten verarbeiten, Zustand aktualisieren, Zeilen je Micro-Batch ausgeben |
| `handleExpiredTimer` | Zeitbasierte Logik, unabhängig von neuen Zeilen |
| `handleInitialState` (optional) | Zustand vorbefüllen vor erster Eingabezeile |

| Verhalten | `handleInputRows` | `handleExpiredTimer` |
|---|---|---|
| State lesen/schreiben/aktualisieren/löschen | Ja | Ja |
| Timer erstellen/löschen | Ja | Ja |
| Zeilen ausgeben | Ja | Ja |
| Über Zeilen im Micro-Batch iterieren | Ja | Nein |
| Logik nach verstrichener Zeit auslösen | Nein | Ja |

- Kombinierbar (z. B. Timer bei jeder neuen Zeile neu setzen; bei Ablauf ohne neue Zeile aktuelle Werte ausgeben).

### State-Typen

- Pro Gruppierungsschlüssel isoliert — kein Zugriff auf/über andere Schlüssel hinweg möglich.

| Typ | Beschreibung |
|---|---|
| `ValueState` | Ein Wert pro Schlüssel (kann Struct/Tupel sein), muss vollständig ersetzt werden. TTL resettet bei Update, nicht beim Lesen. |
| `ListState` | Liste von Werten pro Schlüssel, je Wert eigene TTL. Anhängen einzeln/mehrfach; `put` überschreibt komplett (nur `put` resettet TTL aller Werte). |
| `MapState` | Map (Schlüssel→Wert) pro Gruppierungsschlüssel (≈ Python `dict`), je Paar eigene TTL. Update/Entfernen/Einzellesen/Auflisten/Iterieren möglich. |

- Erzeugung: `handle.getValueState`/`getListState`/`getMapState` — eindeutiger Name, Schema (Python explizit, Scala `Encoder`), optional TTL (ms). `MapState`: Schlüssel- und Wert-Schema getrennt angeben.

```python
# MapState-Beispiel: Sessions pro user_id, Schlüssel session_id
class SessionTracker(StatefulProcessor):
  def init(self, handle: StatefulProcessorHandle) -> None:
    self.sessions = handle.getMapState("sessions", StringType(), LongType())

  def handleInputRows(self, key, rows: Iterator[Row], timerValues) -> Iterator[Row]:
    for row in rows:
      session_id = row["session_id"]  # session_id is the MapState key
      count = self.sessions.getValue(session_id)[0] if self.sessions.containsKey(session_id) else 0
      new_count = count + 1
      self.sessions.updateValue(session_id, (new_count,))
    yield from []

  def close(self) -> None:
    pass

df.groupBy("user_id").transformWithState(SessionTracker(), ...)  # user_id is the grouping key
```

```python
# Python: State-Werte sind Tupel — put/update erwarten Tupel, get liefert Tupel
current_value_tuple = value_state.get()
current_value = current_value_tuple[0]
new_value = current_value + 1
value_state.update((new_value,))
```

### Zeitmodus (`timeMode`)

| Zeitmodus | Beschreibung |
|---|---|
| `ProcessingTime` | Timer/TTL basieren auf Wanduhrzeit zum Zeitpunkt der Micro-Batch-Verarbeitung |
| `EventTime` | Timer basieren auf Event-Time-Watermark; TTL **nicht** unterstützt; erfordert `eventTimeColumnName` |
| `NoTime` / `TimeMode.None()` | Weder Timer noch TTL unterstützt |

```python
# eventTimeColumnName benennt die Ausgabeschema-Spalte mit dem Event-Zeitstempel (korrekte Watermark-Weitergabe)
q = (
  df.groupBy("key")
    .transformWithState(
      statefulProcessor=MyProcessor(),
      outputStructType=output_schema,
      outputMode="Append",
      timeMode="EventTime",
      eventTimeColumnName="outputTimestamp",
    )
    .writeStream...)
```

### `TimerValues`

- Statt Systemuhr (unzuverlässig bei Retries):

| Methode | Beschreibung |
|---|---|
| `getCurrentProcessingTimeInMs` | Verarbeitungszeit des aktuellen Batches (ms seit Epoch) |
| `getCurrentWatermarkInMs` | Watermark des aktuellen Batches (ms seit Epoch) |

### Time-to-Live (TTL)

- Verhindert OOM durch veraltete Werte. Ablauf: Wert wird **still** entfernt (kein `handleExpiredTimer`-Aufruf) — für Logik bei Ablauf stattdessen Timer verwenden.
- TTL resettet bei Update. `ValueState`: gilt für den einen Wert. `ListState`: je Element unabhängig (nur `put` resettet alle). `MapState`: je Schlüssel-Wert-Paar unabhängig.
- **Wichtig:** Ohne TTL muss State-Eviction selbst implementiert werden (sonst OOM-Risiko).

### Beispiel: `SimpleCounterProcessor`

```python
class SimpleCounterProcessor(StatefulProcessor):
  def init(self, handle: StatefulProcessorHandle) -> None:
    value_state_schema = StructType([StructField("count", IntegerType(), True)])
    list_state_schema = StructType([StructField("count", IntegerType(), True)])
    self.value_state = handle.getValueState(stateName="valueState", schema=value_state_schema)
    self.list_state = handle.getListState(stateName="listState", schema=list_state_schema)
    # Schema can also be defined using strings and SQL DDL syntax
    self.map_state = handle.getMapState(stateName="mapState", userKeySchema="name string", valueSchema="count int")

  def handleInputRows(self, key, rows: Iterator[Row], timerValues) -> Iterator[Row]:
    count = 0
    for row in rows:
      list_state_rows = [(120,), (20,)]  # A list of tuples
      self.list_state.put(list_state_rows)
      self.list_state.appendValue((111,))
      self.list_state.appendList(list_state_rows)
      count += 1
    self.value_state.update((count,))
    iter_list = self.list_state.get()
    list_state_value = next(iter_list)[0]
    value = count
    user_key = ("user_key",)
    if self.map_state.exists():
      if self.map_state.containsKey(user_key):
        value += self.map_state.getValue(user_key)[0]
    self.map_state.updateValue(user_key, (value,))
    yield Row(id=key, countAsString=str(count))

q = (
  df.groupBy("key")
    .transformWithState(
      statefulProcessor=SimpleCounterProcessor(),
      outputStructType=output_schema,
      outputMode="Update",
      timeMode="None",
    )
    .writeStream...)
```

### Zeilen ausgeben (Emit rows)

- Keine Annahmen über Zustandsnutzung — pro Bedingung 0, 1 oder viele Zeilen ausgebbar (mehrere Bedingungen erlaubt, aber gleiches Schema für alle Zeilen).
- `transformWithStateInPandas`: gibt Pandas-DataFrames per `yield` aus (`outputStructType` definiert Schema).
- `transformWithState`: gibt `Row`-Objekte (Python) bzw. `Iterator` (Scala, Schema auto-abgeleitet) aus.
- `update`-Modus + leerer DataFrame/Iterator zurückgegeben → Werte für den Gruppierungsschlüssel werden auf `null` gesetzt.

### Initialen State angeben

- Nutzen: Migration bestehender Workflows, Schema-/Logikänderungen an Operator, manuelle Fehlerbehebung. DataFrame mit gleichem Gruppierungsschlüssel-Schema wie Eingabezeilen. Python: `handleInitialState` in `StatefulProcessor`. Scala: eigene Klasse `StatefulProcessorWithInitialState`.

```python
class CounterWithInitialState(StatefulProcessor):
  def init(self, handle: StatefulProcessorHandle) -> None:
    state_schema = StructType([StructField("count", IntegerType(), True)])
    self.count_state = handle.getValueState("countState", state_schema)

  def handleInitialState(self, key, initialState: Row, timerValues) -> None:
    self.count_state.update((initialState["count"],))

  def handleInputRows(self, key, rows: Iterator[Row], timerValues) -> Iterator[Row]:
    count = self.count_state.get()[0] if self.count_state.exists() else 0
    for _ in rows:
      count += 1
    self.count_state.update((count,))
    yield Row(id=key[0], count=count)

initial_state = spark.read.table("existing_counts").groupBy("id")

q = (
  df.groupBy("id")
    .transformWithState(
      statefulProcessor=CounterWithInitialState(),
      outputStructType=output_schema,
      outputMode="Update",
      timeMode="None",
      initialState=initial_state,
    )
    .writeStream...)
```

### `transformWithState` in Lakeflow-Pipelines

1. Ausgabeschema + Stateful-Processor-Logik definieren.
2. Pipeline-Flow erstellen, der `transformWithState` auf einem DataFrame aufruft.
3. Pipeline ausführen, Ergebnisse in Ziel-Senke validieren.

## 7. Schema-Evolution im State-Store

- Gilt für den RocksDB-State-Store bei `transformWithState`-Anwendungen — Datenmodell/Typen im State-Store anpassbar, ohne Zustand zu verlieren oder historische Daten neu zu verarbeiten.

### Voraussetzungen

```python
# State-Store-Encoding-Format muss Avro sein (nur für transformWithState/transformWithStateInPandas)
spark.conf.set("spark.sql.streaming.stateStore.encodingFormat", "avro")
```

- Gleiche Versionsvoraussetzungen wie Abschnitt 6.
- Schema-Evolution passiert **nicht automatisch** bei Quelldaten-Schemaänderung — nur beim Deploy einer neuen Anwendungsversion (Job muss neu gestartet werden, es läuft nur eine Version gleichzeitig).

### Unterstützte Muster

| Muster | Beschreibung |
|---|---|
| Type Widening | Restriktiverer → weniger restriktiver Datentyp |
| Felder hinzufügen | Neue Felder zum Schema bestehender State-Variablen |
| Felder entfernen | Bestehende Felder aus dem Schema entfernen |
| Felder neu anordnen | Matching per Name, nicht Position |
| State-Variable hinzufügen | Neu zur Anwendung (kein Avro-Encoder nötig) |
| State-Variable entfernen | z. B. via `handle.deleteIfExists("name")` (kein Avro-Encoder nötig) |

- **Type Widening — unterstützt:** `int`→`long`/`float`/`double`; `long`→`float`/`double`; `float`→`double`; `string`↔`bytes`.
```text
# Ergebnis: bestehende Werte werden automatisch hochgecastet, z. B. 12 → 12.00
```
- **Felder hinzufügen:** alte Daten gelesen im neuen Schema → Avro-Encoder liefert `null` für neue Felder. Python: immer `None`. Scala: Referenztypen → `null`, primitive Typen → Default (z. B. `0`/`false`) — Databricks empfiehlt `Option[<Type>]` in Scala, um Default-Imputation zu vermeiden.
- **Felder entfernen:** beim Lesen alter Daten werden im neuen Schema fehlende Felder ignoriert.
- **Felder neu anordnen:** möglich, auch kombiniert mit Hinzufügen/Entfernen (Name-Matching).

### Nicht unterstützte Muster

- **Felder umbenennen:** wird als Entfernen+Hinzufügen behandelt (kein Fehler, aber alte Werte gehen verloren — Matching läuft über den Namen).
- **Umbenennung/Typänderung von Map-Schlüsseln:** nicht möglich.
- **Type Narrowing (Downcasting):** nicht unterstützt (Datenverlustrisiko) — z. B. `double`→`float`/`long`/`int`, `float`→`long`/`int`, `long`→`int` alle verboten.

### Standardwerte für hinzugefügte Felder

- Keine eingebaute Kennzeichnung "durch Schema-Evolution hinzugefügt" — eigene Logik muss `null`/`None` behandeln. Python: `None` für alle Typen. Scala: `null` (Referenztypen) bzw. typspezifischer Default (primitive Typen), außer bei `Option[<Type>]`.

### Limitations

| Beschreibung | Standard-Grenzwert | Konfiguration zum Überschreiben |
|---|---|---|
| Schema-Evolutionen je State-Variable (mehrere Änderungen in einem Neustart = eine) | 16 | `spark.sql.streaming.stateStore.valueStateSchemaEvolutionThreshold` |
| Schema-Evolutionen je Streaming-Query | 128 | `spark.sql.streaming.stateStore.maxNumStateSchemaFiles` |

## 8. Asynchrone Verarbeitung mit `transformWithState` (Beta)

- Ab DBR 19, nur zeilenbasierte **Python**-`transformWithState`-API (nicht `transformWithStateInPandas`, nicht Scala, nicht Serverless). Baut auf `asyncio`: State-Operationen/eigene Logik laufen gruppierungsschlüsselübergreifend gleichzeitig, IPC wird gebatcht → höherer Durchsatz als synchron, ohne Drittanbieter-Bibliotheken.

### `AsyncStatefulProcessor` implementieren

- Alle API-Methoden (`init`, `close`, `handleInputRows`, `handleExpiredTimer`, `handleInitialState`) als `async def`.
- Lese-/Schreib-State-/Timer-Operationen (`valueState.get()`, `registerTimer` etc.) mit `await`. **Erstellen** von State-Objekten (`getValueState`, `getMapState`, `getListState`) bleibt **synchron**, ebenso `deleteIfExists`.
- Methoden laufen gleichzeitig über Schlüssel → eigener Code mit Member-Variablen/externen Systemen muss concurrency-safe sein.
- Fehler aus State-Operationen nicht abfangen/unterdrücken — Spark lässt Task fehlschlagen + wiederholt ihn; solche Fehler werden im `AsyncStatefulProcessor` nie an eigenen Code weitergereicht.

| Aufrufart | Klassen/Methoden |
|---|---|
| `await` (Einzelergebnis) | `AsyncValueState` (`exists`, `get`, `update`, `clear`); `AsyncMapState` (`exists`, `getValue`, `containsKey`, `updateValue`, `removeKey`, `clear`); `AsyncListState` (`exists`, `put`, `appendValue`, `appendList`, `clear`); `AsyncStatefulProcessorHandle` (`registerTimer`, `deleteTimer`) |
| `async for` (asynchroner Iterator) | `AsyncMapState` (`iterator`, `keys`, `values`); `AsyncListState` (`get`); `AsyncStatefulProcessorHandle` (`listTimers`) |

```python
class AsyncCountProcessor(AsyncStatefulProcessor):
  async def init(self, handle: AsyncStatefulProcessorHandle) -> None:
    self.count = handle.getValueState("count", value_schema)

  async def handleInputRows(self, key, rows, timerValues):
    total = (await self.count.get() or (0,))[0]
    for _ in rows:
      total += 1
    await self.count.update((total,))
    yield Row(action=key[0], count=total)

  async def close(self) -> None:
    pass
```

- Query-Start wie synchron über `transformWithState` — Async/synchron teilen sich dasselbe State-Format → Wechsel zwischen `AsyncStatefulProcessor` und `StatefulProcessor` ohne Checkpoint-Verlust möglich.
- **Optimierung:** besonders sinnvoll, wenn Logik auf externe Operationen wartet (z. B. HTTP) — `asyncio.gather` löst mehrere Anfragen gleichzeitig statt sequentiell:

```python
async def handleInputRows(self, key, rows, timerValues):
    user_id = key[0]
    scores = await asyncio.gather(*[self._fetch_score(row) for row in rows])
    max_score = max(scores)
    await self._score_state.update((max_score,))
    yield Row(user_id=user_id, score=max_score)
```

## 9. Legacy Arbitrary Stateful Operators (`mapGroupsWithState` / `flatMapGroupsWithState`)

- **Hinweis:** für neue Stateful-Apps empfiehlt Databricks `transformWithState` (Abschnitt 6) statt dieser Legacy-Operatoren.
- Eigener initialer State per Overload mit `initialState`-Parameter übergebbar (vermeidet erneute Verarbeitung bei fehlendem Checkpoint).

## 10. Beispiel-Stateful-Anwendungen

### Slowly Changing Dimension (SCD) Type 1

- Verfolgt nur den aktuellsten Wert eines Feldes. Alternative zu Streaming-Tabellen + `AUTO CDC ... INTO`, aber niedrigere Latenz für Near-Realtime (direkt im State-Store implementiert).

```python
class SCDType1StatefulProcessor(StatefulProcessor):
    def init(self, handle: StatefulProcessorHandle) -> None:
        value_state_schema = StructType([
            StructField("user", StringType(), True),
            StructField("time", LongType(), True),
            StructField("location", StringType(), True)
        ])
        self.latest_location = handle.getValueState("latestLocation", value_state_schema)

    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        max_row = None
        max_time = float('-inf')
        for pdf in rows:
            for _, pd_row in pdf.iterrows():
                if pd_row["time"] > max_time:
                    max_time = pd_row["time"]
                    max_row = tuple(pd_row)
        exists = self.latest_location.exists()
        if not exists or max_row[1] > self.latest_location.get()[1]:
            self.latest_location.update(max_row)
            yield pd.DataFrame({"user": (max_row[0],), "time": (max_row[1],), "location": (max_row[2],)})
        yield pd.DataFrame()

(df.groupBy("user")
  .transformWithStateInPandas(
      statefulProcessor=SCDType1StatefulProcessor(),
      outputStructType=output_schema,
      outputMode="Update",
      timeMode="None",
  )
  .writeStream...)
# Ergebnis: nur bei neuerem "time" pro user wird der State aktualisiert und die neue Zeile ausgegeben
```

- **SCD Type 2** (Historisierung mit Gültigkeitszeiträumen): gleiches Grundprinzip (eigener `StatefulProcessor` mit `ValueState`/`MapState`), dokumentiert in referenzierten Beispiel-Notebooks (Python/Scala).

### Downtime Detector

- Nutzt Timer, um auch ohne neue Zeilen zeitbasiert zu reagieren: bei jedem neuen Wert wird `lastSeen` aktualisiert, bestehende Timer gelöscht, neuer Timer gesetzt. Läuft ein Timer ab → verstrichene Zeit seit letztem Event ausgeben, neuer 10s-Timer.

```python
class DownTimeDetectorStatefulProcessor(StatefulProcessor):
    def init(self, handle: StatefulProcessorHandle) -> None:
        state_schema = StructType([StructField("value", TimestampType(), True)])
        self.handle = handle
        self.last_seen = handle.getValueState("last_seen", state_schema)

    def handleExpiredTimer(self, key, timerValues, expiredTimerInfo) -> Iterator[pd.DataFrame]:
        latest_from_existing = self.last_seen.get()
        downtime_duration = timerValues.getCurrentProcessingTimeInMs() - int(latest_from_existing[0].timestamp() * 1000)
        self.handle.registerTimer(timerValues.getCurrentProcessingTimeInMs() + 10000)
        yield pd.DataFrame({"id": key, "timeValues": str(downtime_duration)})
        # Ergebnis: downtime_duration in ms seit letztem Event für diesen key

    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        max_row = max((tuple(pdf.iloc[0]) for pdf in rows), key=lambda row: row[1])
        if self.last_seen.exists():
            latest_from_existing = self.last_seen.get()[0]
        else:
            latest_from_existing = datetime.datetime.fromtimestamp(0)
        if latest_from_existing < max_row[1]:
            for timer in self.handle.listTimers():
                self.handle.deleteTimer(timer)
            self.last_seen.update((max_row[1],))
        self.handle.registerTimer(timerValues.getCurrentProcessingTimeInMs() + 5000)
        yield pd.DataFrame({"id": key, "timeValues": str(timerValues.getCurrentProcessingTimeInMs())})
```

### Bestehende State-Informationen migrieren (initialer State aus Checkpoint)

- Initialer State ladbar direkt aus bestehendem Checkpoint-Pfad via `statestore`-Reader (Abschnitt 4) — z. B. für Migration von Legacy-Stateful-Apps zu `transformWithState`.

```python
initial_state = spark.read.format("statestore").option("path", "$checkpointsDir").load()

df.groupBy("id")
  .transformWithStateInPandas(
      statefulProcessor=AccumulatedCounterStatefulProcessorWithInitialState(),
      outputStructType=output_schema,
      outputMode="Update",
      timeMode="None",
      initialState=initial_state,
  )
  .writeStream...
```

- Initialer State nur bei **erster** Initialisierung der Anwendung setzbar (`handleInitialState`, s. Abschnitt 6). Analoge Beispiele (referenzierte Notebooks Python/Scala): Migration einer Delta-Tabelle in den State-Store, Session Tracking.

### Eigener Stream-Stream-Join mit `transformWithState`

- Sinnvoll wenn: `update`-Ausgabemodus benötigt (eingebaute Stream-Stream-Joins unterstützen ihn nicht, nützlich bei niedriger Latenz); weiterhin für spät eintreffende Zeilen (nach Watermark) gejoint werden muss; Many-to-many-Joins nötig sind. Volle Kontrolle über State-Ablauflogik, inkl. dynamischer Verlängerung der Aufbewahrung für Out-of-Order-Events.
- Grundmuster: mehrere `MapState`-Objekte (z. B. Profil-, Präferenz-, Aktivitätsdaten je `user_id`) werden in `handleInputRows` aktualisiert; ein Timer verzögert (z. B. 10s) die Join-Ausgabe, erzeugt in `handleExpiredTimer` durch Kombination der State-Werte.

```python
def handleInputRows(self, key, rows, timerValues):
    for _, row in df.iterrows():
        user_id = row["user_id"]
        if "event_type" in row:
            self.activity_state.updateValue(user_id, row.to_dict())
            self.handle.registerTimer(timerValues.get_current_processing_time_in_ms() + (10 * 1000))
        elif "name" in row:
            self.profile_state.updateValue(user_id, row.to_dict())
        elif "preferred_category" in row:
            self.preferences_state.updateValue(user_id, row.to_dict())
    return iter([])

def handleExpiredTimer(self, key, timerValues, expiredTimerInfo):
    user_activity = self.activity_state.getValue(key)
    user_profile = self.profile_state.getValue(key)
    user_preferences = self.preferences_state.getValue(key)
    if user_activity:
        output_row = {
            "user_id": key,
            "event_type": user_activity["event_type"],
            "timestamp": user_activity["timestamp"],
            "profile_name": user_profile.get("name") if user_profile else None,
            "email": user_profile.get("email") if user_profile else None,
            "preferred_category": user_preferences.get("preferred_category") if user_preferences else None
        }
        return iter([pd.DataFrame([output_row])])
    return iter([])
    # Ergebnis: eine gejointe Ausgabezeile je user_id, 10s nach dem Activity-Event, mit verfügbaren Profil-/Präferenzdaten
```

### Top-K-Berechnung

- Nutzt eine `ListState` mit einer Priority Queue, um die Top-K-Elemente eines Streams je Gruppierungsschlüssel nahezu in Echtzeit zu pflegen/aktualisieren. Dokumentiert in referenzierten Beispiel-Notebooks (Python/Scala).

**Stand:** 2026-09-14.
