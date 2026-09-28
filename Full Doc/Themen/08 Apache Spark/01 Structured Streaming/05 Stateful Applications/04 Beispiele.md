# Beispiel-Stateful-Anwendungen — Referenz

Dieses Dokument sammelt Code-Beispiele für eigene (custom) Stateful-Streaming-Anwendungen mit dem Operator `transformWithState`. Der Original-Inhalt bei `https://docs.databricks.com/gcp/en/stateful-applications/examples` wurde von WebFetch nur stark verkürzt (zusammengefasst) zurückgegeben; als vollständige, wortgetreue Quelle wurde daher die inhaltsgleiche Azure-Mirror-Seite `https://learn.microsoft.com/en-us/azure/databricks/stateful-applications/examples` per WebFetch abgerufen und verifiziert.

## Abschnittsübersicht
1. [Einleitung](#einleitung)
2. [Voraussetzungen](#voraussetzungen)
3. [Slowly Changing Dimension (SCD) Type 1](#scd1)
4. [Slowly Changing Dimension (SCD) Type 2](#scd2)
5. [Downtime Detector](#downtime)
6. [Bestehende State-Informationen migrieren](#migrate-state)
7. [Delta-Tabelle in State-Store migrieren (Initialisierung)](#migrate-delta)
8. [Session Tracking](#session-tracking)
9. [Eigener Stream-Stream-Join mit transformWithState](#stream-join)
10. [Top-K-Berechnung](#topk)
11. [Quellen](#quellen)

---

## <a id="einleitung">1. Einleitung</a>

Diese Seite enthält Code-Beispiele für eigene Stateful-Streaming-Anwendungen mit dem Operator `transformWithState`. Databricks empfiehlt, für gängige Operationen wie Aggregationen und Joins die eingebauten Stateful-Methoden zu verwenden.

Siehe [Uebersicht.md](00%20Uebersicht.md) (Original: "Build a custom stateful application with transformWithState").

> **Hinweis:** Python unterstützt sowohl die zeilenbasierte `transformWithState`-API (verfügbar im Micro-Batch- und im Real-Time-Modus) als auch den Pandas-basierten Operator `transformWithStateInPandas`. Die folgenden Beispiele verwenden `transformWithStateInPandas` in Python und `transformWithState` in Scala.

---

## <a id="voraussetzungen">2. Voraussetzungen</a>

Der Operator `transformWithState` und die zugehörigen APIs und Klassen haben folgende Voraussetzungen:

- Verfügbar ab Databricks Runtime 16.2 und höher.
- Der Standard-Access-Modus wird für Python (`transformWithStateInPandas` und zeilenbasiertes `transformWithState`) ab Databricks Runtime 16.3 und höher unterstützt, für Scala (`transformWithState`) ab Databricks Runtime 17.3 und höher.
- RocksDB ist ab Databricks Runtime 17.3 der Standard-State-Store-Provider. Für Databricks-Runtime-Versionen unter 17.3 muss der RocksDB-State-Store-Provider konfiguriert werden. Databricks empfiehlt, RocksDB als Teil der Compute-Konfiguration zu aktivieren.

> **Hinweis:** Auf Databricks-Runtime-Versionen unter 17.3 wird der RocksDB-State-Store-Provider für die aktuelle Session wie folgt aktiviert:

```python
spark.conf.set("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")
```

---

## <a id="scd1">3. Slowly Changing Dimension (SCD) Type 1</a>

Der folgende Code ist ein Beispiel für die Implementierung von SCD Type 1 mit `transformWithState`. SCD Type 1 verfolgt nur den jeweils aktuellsten Wert für ein gegebenes Feld.

> **Hinweis:** Streaming-Tabellen und `AUTO CDC ... INTO` können verwendet werden, um SCD Type 1 oder Type 2 mit Delta-Lake-gestützten Tabellen zu implementieren. Dieses Beispiel implementiert SCD Type 1 im State-Store, was für nahezu Echtzeit-Anwendungen niedrigere Latenz bietet.

### Python

```python
# Import the necessary libraries
import pandas as pd
from pyspark.sql.streaming import StatefulProcessor, StatefulProcessorHandle
from pyspark.sql.types import StructType, StructField, LongType, StringType
from typing import Iterator

# Set the state store provider to RocksDB
spark.conf.set("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")

# Define the output schema for the streaming query
output_schema = StructType([
    StructField("user", StringType(), True),
    StructField("time", LongType(), True),
    StructField("location", StringType(), True)
])

# Define a custom StatefulProcessor for slowly changing dimension type 1 (SCD1) operations
class SCDType1StatefulProcessor(StatefulProcessor):
    def init(self, handle: StatefulProcessorHandle) -> None:
        self.handle = handle
        # Define the schema for the state value
        value_state_schema = StructType([
            StructField("user", StringType(), True),
            StructField("time", LongType(), True),
            StructField("location", StringType(), True)
        ])
        # Initialize the state to store the latest location for each user
        self.latest_location = handle.getValueState("latestLocation", value_state_schema)

    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        # Find the row with the maximum time value
        max_row = None
        max_time = float('-inf')
        for pdf in rows:
            for _, pd_row in pdf.iterrows():
                time_value = pd_row["time"]
                if time_value > max_time:
                    max_time = time_value
                    max_row = tuple(pd_row)

        # Check whether state exists and update if necessary
        exists = self.latest_location.exists()
        if not exists or max_row[1] > self.latest_location.get()[1]:
            # Update the state with the new max row
            self.latest_location.update(max_row)
            # Yield the updated row
            yield pd.DataFrame(
                {"user": (max_row[0],), "time": (max_row[1],), "location": (max_row[2],)}
            )
        # Yield an empty DataFrame if no update is needed
        yield pd.DataFrame()

    def close(self) -> None:
        # No cleanup needed
        pass

# Apply the stateful transformation to the input DataFrame
(df.groupBy("user")
  .transformWithStateInPandas(
      statefulProcessor=SCDType1StatefulProcessor(),
      outputStructType=output_schema,
      outputMode="Update",
      timeMode="None",
  )
  .writeStream...  # Continue with stream writing configuration
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.streaming._

// Define a case class to represent user location data
case class UserLocation(
    user: String,
    time: Long,
    location: String)

// Define a stateful processor for slowly changing dimension type 1 (SCD1) operations
class SCDType1StatefulProcessor extends StatefulProcessor[String, UserLocation, UserLocation] {
  import org.apache.spark.sql.{Encoders}

  // Transient value state to store the latest location for each user
  @transient private var _latestLocation: ValueState[UserLocation] = _

  private val userLocationEncoder = Encoders.product[UserLocation]

  // Initialize the state store
  override def init(
      outputMode: OutputMode,
      timeMode: TimeMode): Unit = {
    // Create a value state named "locationState" using UserLocation encoder
    // TTLConfig.NONE means the state has no expiration
    _latestLocation = getHandle.getValueState[UserLocation]("locationState",
      userLocationEncoder, TTLConfig.NONE)
  }

  // Process input rows and update state
  override def handleInputRows(
      key: String,
      inputRows: Iterator[UserLocation],
      timerValues: TimerValues): Iterator[UserLocation] = {
    // Find the location with the maximum timestamp from input rows
    val maxNewLocation = inputRows.maxBy(_.time)

    // Update state and emit output if:
    // 1. No previous state exists, or
    // 2. New location has a more recent timestamp than the stored one
    if (_latestLocation.getOption().isEmpty || maxNewLocation.time > _latestLocation.get().time) {
      _latestLocation.update(maxNewLocation)
      Iterator.single(maxNewLocation)  // Emit the updated location
    } else {
      Iterator.empty  // No update needed, emit nothing
    }
  }
}

import spark.implicits._
import java.util.UUID

// Create a dedicated schema for the example tables
spark.sql("CREATE SCHEMA IF NOT EXISTS main.stateful_examples")

// Seed a small Delta table to use as the streaming source
spark.sql("DROP TABLE IF EXISTS main.stateful_examples.scd1_source_scala")
Seq(
  UserLocation("u1", 1L, "NYC"),
  UserLocation("u1", 3L, "SF"),
  UserLocation("u1", 2L, "LA"),
  UserLocation("u2", 5L, "London")
).toDF().write.saveAsTable("main.stateful_examples.scd1_source_scala")

val q = spark.readStream
  .table("main.stateful_examples.scd1_source_scala")
  .as[UserLocation]
  .groupByKey(_.user)
  .transformWithState(
    new SCDType1StatefulProcessor(),
    TimeMode.None(),
    OutputMode.Update()
  )
  .writeStream
  .format("memory")
  .queryName("scd1_output_scala")
  .option("checkpointLocation", s"/tmp/checkpoint_${UUID.randomUUID()}")
  .trigger(Trigger.AvailableNow())
  .start()

q.awaitTermination()

// Each user keeps only its latest location by time: u1 -> SF (time 3), u2 -> London (time 5)
spark.sql("SELECT user, time, location FROM scd1_output_scala ORDER BY user").show()
```

---

## <a id="scd2">4. Slowly Changing Dimension (SCD) Type 2</a>

Die folgenden Notebooks enthalten ein Beispiel für die Implementierung von SCD Type 2 mit `transformWithState` in Python bzw. Scala.

- SCD Type 2 Python: [Notebook abrufen](https://docs.databricks.com/notebooks/source/streaming/tws-scd2-python.html)
- SCD Type 2 Scala: [Notebook abrufen](https://docs.databricks.com/notebooks/source/streaming/tws-scd2-scala.html)

---

## <a id="downtime">5. Downtime Detector</a>

`transformWithState` implementiert Timer, mit denen basierend auf verstrichener Zeit reagiert werden kann, selbst wenn in einem Micro-Batch keine Datensätze für einen gegebenen Schlüssel verarbeitet werden.

Das folgende Beispiel implementiert ein Muster für einen Downtime-Detector (Ausfallzeit-Erkennung). Jedes Mal, wenn ein neuer Wert für einen gegebenen Schlüssel gesehen wird, aktualisiert es den `lastSeen`-State-Wert, löscht bestehende Timer und setzt einen Timer für die Zukunft neu.

Läuft ein Timer ab, gibt die Anwendung die seit dem letzten beobachteten Event für den Schlüssel verstrichene Zeit aus. Anschließend wird ein neuer Timer gesetzt, der 10 Sekunden später ein Update ausgibt.

### Python

Um das Beispiel komplett auszuführen, wird ein einzelner Sensorwert als Streaming-Quelle angelegt. Weil die Timer Processing Time nutzen, verwendet der Treiber einen `processingTime`-Trigger und wartet vor dem Stoppen, damit die Timer auslösen.

```python
import datetime
import time
import uuid
import pandas as pd
from pyspark.sql.streaming import StatefulProcessor, StatefulProcessorHandle
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from typing import Iterator

spark.conf.set("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")

class DownTimeDetectorStatefulProcessor(StatefulProcessor):
    def init(self, handle: StatefulProcessorHandle) -> None:
        # Define the schema for the state value (timestamp)
        state_schema = StructType([StructField("value", TimestampType(), True)])
        self.handle = handle
        # Initialize state to store the last seen timestamp for each key
        self.last_seen = handle.getValueState("last_seen", state_schema)

    def handleExpiredTimer(self, key, timerValues, expiredTimerInfo) -> Iterator[pd.DataFrame]:
        latest_from_existing = self.last_seen.get()
        # Calculate downtime as the elapsed time between the last observed event and now
        downtime_duration = timerValues.getCurrentProcessingTimeInMs() - int(latest_from_existing[0].timestamp() * 1000)
        # Register a new timer for 10 seconds in the future
        self.handle.registerTimer(timerValues.getCurrentProcessingTimeInMs() + 10000)
        # Yield a DataFrame with the key and downtime duration
        yield pd.DataFrame(
            {
                "id": key,
                "timeValues": str(downtime_duration),
            }
        )

    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        # Find the row with the maximum timestamp
        max_row = max((tuple(pdf.iloc[0]) for pdf in rows), key=lambda row: row[1])

        # Get the latest timestamp from the existing state or use epoch start if a timestamp doesn't exist
        if self.last_seen.exists():
            latest_from_existing = self.last_seen.get()[0]
        else:
            latest_from_existing = datetime.datetime.fromtimestamp(0)

        # If the new data is more recent than the existing state
        if latest_from_existing < max_row[1]:
            # Delete all existing timers
            for timer in self.handle.listTimers():
                self.handle.deleteTimer(timer)
            # Update the last seen timestamp
            self.last_seen.update((max_row[1],))

        # Register a new timer for 5 seconds in the future
        self.handle.registerTimer(timerValues.getCurrentProcessingTimeInMs() + 5000)

        # Get current processing time in milliseconds
        timestamp_in_millis = str(timerValues.getCurrentProcessingTimeInMs())

        # Yield a DataFrame with the key and current timestamp
        yield pd.DataFrame({"id": key, "timeValues": timestamp_in_millis})

    def close(self) -> None:
        # No cleanup needed
        pass

# Create a dedicated schema for the example tables
spark.sql("CREATE SCHEMA IF NOT EXISTS main.stateful_examples")

# Seed a small Delta table with a sensor reading to use as the streaming source
spark.sql("DROP TABLE IF EXISTS main.stateful_examples.sensor_events")
spark.createDataFrame(
    [("sensor1", datetime.datetime(2024, 1, 1, 12, 0, 0))],
    "id string, timestamp timestamp",
).write.saveAsTable("main.stateful_examples.sensor_events")

df = spark.readStream.table("main.stateful_examples.sensor_events")

# Output schema: the key and a time value (processing time or elapsed downtime)
output_schema = StructType([
    StructField("id", StringType(), True),
    StructField("timeValues", StringType(), True),
])

# ProcessingTime mode enables the timers that detect downtime
q = (
    df.groupBy("id")
    .transformWithStateInPandas(
        statefulProcessor=DownTimeDetectorStatefulProcessor(),
        outputStructType=output_schema,
        outputMode="Update",
        timeMode="ProcessingTime",
    )
    .writeStream.format("memory")
    .queryName("downtime_output")
    .option("checkpointLocation", f"/tmp/checkpoint_{uuid.uuid4()}")
    .trigger(processingTime="5 seconds")
    .start()
)

# Wait past the timers so they fire, then stop the query
time.sleep(30)
q.stop()

# When a timer fires, it emits the elapsed time in milliseconds since the last observed event
display(spark.sql("SELECT * FROM downtime_output"))
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import java.sql.Timestamp
import org.apache.spark.sql.Encoders
import org.apache.spark.sql.streaming._
import spark.implicits._
import java.util.UUID

// The (String, Timestamp) schema represents an (id, time). We want to do downtime
// detection on every single unique sensor, where each sensor has a sensor ID.
// downtimeThresholdMs is the timer duration in milliseconds.
class DowntimeDetector(downtimeThresholdMs: Long) extends
  StatefulProcessor[String, (String, Timestamp), (String, Long)] {

  @transient private var _lastSeen: ValueState[Timestamp] = _

  private val timestampEncoder = Encoders.TIMESTAMP

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    _lastSeen = getHandle.getValueState[Timestamp]("lastSeen", timestampEncoder, TTLConfig.NONE)
  }

  // The logic here is as follows: find the largest timestamp seen so far. Set a timer for
  // the duration later.
  override def handleInputRows(
      key: String,
      inputRows: Iterator[(String, Timestamp)],
      timerValues: TimerValues): Iterator[(String, Long)] = {
    val latestRecordFromNewRows = inputRows.maxBy(_._2.getTime)

    // Use getOrElse to initiate state variable if it doesn't exist
    val latestTimestampFromExistingRows = Option(_lastSeen.get()).getOrElse(new Timestamp(0))
    val latestTimestampFromNewRows = latestRecordFromNewRows._2

    if (latestTimestampFromNewRows.after(latestTimestampFromExistingRows)) {
      // Cancel the one existing timer, since we have a new latest timestamp.
      // We call "listTimers()" because we don't know ahead of time what
      // the timestamp of the existing timer will be.
      getHandle.listTimers().foreach(timer => getHandle.deleteTimer(timer))

      _lastSeen.update(latestTimestampFromNewRows)
      // Use timerValues to schedule a timer using processing time.
      getHandle.registerTimer(timerValues.getCurrentProcessingTimeInMs() + downtimeThresholdMs)
    } else {
      // No new latest timestamp, so there is no need to update the state or set a timer.
    }

    Iterator.empty
  }

  override def handleExpiredTimer(
    key: String,
    timerValues: TimerValues,
    expiredTimerInfo: ExpiredTimerInfo): Iterator[(String, Long)] = {
      val latestTimestamp = _lastSeen.get()
      // Downtime is the elapsed time in milliseconds between the last observed event and now
      val downtimeDurationMs =
        timerValues.getCurrentProcessingTimeInMs() - latestTimestamp.getTime

      // Register another timer that will fire in 10 seconds.
      // Timers can be registered anywhere but init()
      getHandle.registerTimer(timerValues.getCurrentProcessingTimeInMs() + 10000)

      Iterator((key, downtimeDurationMs))
  }
}

// Create a dedicated schema for the example tables
spark.sql("CREATE SCHEMA IF NOT EXISTS main.stateful_examples")

// Seed a small Delta table with a sensor reading to use as the streaming source
spark.sql("DROP TABLE IF EXISTS main.stateful_examples.sensor_events_scala")
Seq(
  ("sensor1", Timestamp.valueOf("2024-01-01 12:00:00"))
).toDF("id", "timestamp").write.saveAsTable("main.stateful_examples.sensor_events_scala")

// ProcessingTime mode enables the timers that detect downtime
val q = spark.readStream
  .table("main.stateful_examples.sensor_events_scala")
  .as[(String, Timestamp)]
  .groupByKey(_._1)
  .transformWithState(
    new DowntimeDetector(5000L),
    TimeMode.ProcessingTime(),
    OutputMode.Update()
  )
  .writeStream
  .format("memory")
  .queryName("downtime_output_scala")
  .option("checkpointLocation", s"/tmp/checkpoint_${UUID.randomUUID()}")
  .trigger(Trigger.ProcessingTime("5 seconds"))
  .start()

// Wait past the timers so they fire, then stop the query
Thread.sleep(30000)
q.stop()

// When a timer fires, it emits the elapsed time in milliseconds since the last observed event
spark.sql("SELECT * FROM downtime_output_scala").show(false)
```

---

## <a id="migrate-state">6. Bestehende State-Informationen migrieren</a>

Das folgende Beispiel zeigt, wie eine Stateful-Anwendung implementiert wird, die einen initialen State akzeptiert. Man kann jeder Stateful-Anwendung eine Behandlung für initialen State hinzufügen, aber der initiale State kann nur beim ersten Initialisieren der Anwendung gesetzt werden.

Dieses Beispiel verwendet den `statestore`-Reader, um bestehende State-Informationen aus einem Checkpoint-Pfad zu laden. Ein Beispielanwendungsfall für dieses Muster ist die Migration von Legacy-Stateful-Anwendungen zu `transformWithState`.

### Python

```python
# Import the necessary libraries
import pandas as pd
from pyspark.sql.streaming import StatefulProcessor, StatefulProcessorHandle
from pyspark.sql.types import StructType, StructField, LongType, StringType, IntegerType
from typing import Iterator

# Set RocksDB as the state store provider for better performance
spark.conf.set("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")

"""
Input schema is as below

input_schema = StructType(
    [StructField("id", StringType(), True)],
    [StructField("value", StringType(), True)]
)
"""

# Define the output schema for the streaming query
output_schema = StructType([
    StructField("id", StringType(), True),
    StructField("accumulated", StringType(), True)
])

class AccumulatedCounterStatefulProcessorWithInitialState(StatefulProcessor):

    def init(self, handle: StatefulProcessorHandle) -> None:
        # Define the schema for the state value (integer)
        state_schema = StructType([StructField("value", IntegerType(), True)])
        # Initialize state to store the accumulated counter for each id
        self.counter_state = handle.getValueState("counter_state", state_schema)
        self.handle = handle

    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        # Check if state exists for the current key
        exists = self.counter_state.exists()
        if exists:
            value_row = self.counter_state.get()
            existing_value = value_row[0]
        else:
            existing_value = 0

        accumulated_value = existing_value

        # Process input rows and accumulate values
        for pdf in rows:
            value = pdf["value"].astype(int).sum()
            accumulated_value += value

        # Update the state with the new accumulated value
        self.counter_state.update((accumulated_value,))

        # Yield a DataFrame with the key and accumulated value
        yield pd.DataFrame({"id": key, "accumulated": str(accumulated_value)})

    def handleInitialState(self, key, initialState, timerValues) -> None:
        # Initialize the state with the provided initial value
        init_val = initialState.at[0, "initVal"]
        self.counter_state.update((init_val,))

    def close(self) -> None:
        # No cleanup needed
        pass

# Load initial state from a checkpoint directory
initial_state = spark.read.format("statestore")
  .option("path", "$checkpointsDir")
  .load()

# Apply the stateful transformation to the input DataFrame
df.groupBy("id")
  .transformWithStateInPandas(
      statefulProcessor=AccumulatedCounterStatefulProcessorWithInitialState(),
      outputStructType=output_schema,
      outputMode="Update",
      timeMode="None",
      initialState=initial_state,
  )
  .writeStream...  # Continue with stream writing configuration
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
// Import the necessary libraries
import org.apache.spark.sql.streaming._
import org.apache.spark.sql.{Dataset, Encoder, Encoders, DataFrame}
import org.apache.spark.sql.types._

// Define a stateful processor that can handle the initial state
class InitialStateStatefulProcessor extends StatefulProcessorWithInitialState[String, (String, String, String), (String, String), (String, Int)] {
  // Transient value state to store the accumulated value
  @transient protected var valueState: ValueState[Int] = _

  private val intEncoder = Encoders.scalaInt

  // Initialize the state store
  override def init(
      outputMode: OutputMode,
      timeMode: TimeMode): Unit = {
    // Create a value state named "valueState" using Int encoder
    // TTLConfig.NONE means the state has no automatic expiration
    valueState = getHandle.getValueState[Int]("valueState",
      intEncoder, TTLConfig.NONE)
  }

  // Process input rows and update state
  override def handleInputRows(
      key: String,
      inputRows: Iterator[(String, String, String)],
      timerValues: TimerValues): Iterator[(String, String)] = {
    var existingValue = 0
    // Retrieve existing value from state if it exists
    if (valueState.exists()) {
      existingValue += valueState.get()
    }
    var accumulatedValue = existingValue
    // Accumulate values from input rows
    for (row <- inputRows) {
      accumulatedValue += row._2.toInt
    }
    // Update the state with the new accumulated value
    valueState.update(accumulatedValue)
    // Return the key and accumulated value as a string
    Iterator((key, accumulatedValue.toString))
  }

  // Handle initial state when provided
  override def handleInitialState(
      key: String, initialState: (String, Int), timerValues: TimerValues): Unit = {
    // Update the state with the initial value
    valueState.update(initialState._2)
  }
}
```

---

## <a id="migrate-delta">7. Delta-Tabelle in State-Store migrieren (Initialisierung)</a>

Die folgenden Notebooks enthalten ein Beispiel zum Initialisieren von State-Store-Werten aus einer Delta-Tabelle mit `transformWithState` in Python bzw. Scala.

- Initialize state from Delta Python: [Notebook abrufen](https://docs.databricks.com/notebooks/source/streaming/tws-init-python.html)
- Initialize state from Delta Scala: [Notebook abrufen](https://docs.databricks.com/notebooks/source/streaming/tws-init-scala.html)

---

## <a id="session-tracking">8. Session Tracking</a>

Die folgenden Notebooks enthalten ein Beispiel für Session Tracking mit `transformWithState` in Python bzw. Scala.

- Session tracking Python: [Notebook abrufen](https://docs.databricks.com/notebooks/source/streaming/tws-session-python.html)
- Session tracking Scala: [Notebook abrufen](https://docs.databricks.com/notebooks/source/streaming/tws-session-scala.html)

---

## <a id="stream-join">9. Eigener Stream-Stream-Join mit transformWithState</a>

Der folgende Code demonstriert einen eigenen Stream-Stream-Join über mehrere Streams hinweg mit `transformWithState`. Dieser Ansatz kann anstelle eines eingebauten Join-Operators aus folgenden Gründen verwendet werden:

- Es wird der Update-Ausgabemodus benötigt, der Stream-Stream-Joins nicht unterstützt. Dies ist besonders nützlich für Anwendungen mit niedrigerer Latenz.
- Joins müssen weiterhin für spät eintreffende Zeilen (nach Ablauf des Watermarks) durchgeführt werden.
- Es müssen Many-to-many-Stream-Stream-Joins durchgeführt werden.

Dieses Beispiel gibt dem Nutzer volle Kontrolle über die State-Ablauflogik und ermöglicht so eine dynamische Verlängerung der Aufbewahrungsdauer (retention period), um auch nach dem Watermark noch mit außer-der-Reihe eintreffenden (out-of-order) Events umzugehen.

### Python

Im folgenden Beispiel kommen Profil-, Präferenz- und Aktivitäts-Events auf **einem** Stream an, jeweils mit einem `record_type` markiert. Der Prozessor puffert jeden Datensatztyp als eigene **`ValueState`**-Variable. Ein Processing-Time-Timer gibt den angereicherten Join kurz nach Eintreffen eines Aktivitäts-Events aus. Profil- und Präferenz-State laufen nach einer Stunde Inaktivität per **TTL** ab; jede Aktivität wird nach dem Join aus dem State gelöscht.

> **Hinweis:** Das Beispiel hält pro Nutzer nur **eine** Aktivität und löscht sie nach dem Join. Treffen vor dem Timer mehrere Aktivitäten desselben Nutzers ein, ersetzt die spätere die frühere, und jeder Timer liest die zuletzt gepufferte Aktivität. Um jede Aktivität zu erhalten, Aktivitäten in einem List- oder Map-State nach Event-Zeit puffern.

> Aktualisiert auf die AWS-Fassung: Die frühere Version nutzte drei `MapState`-Variablen; die aktuelle nutzt `ValueState` mit TTL.

```python
# Import the necessary libraries
import pandas as pd
import time
import uuid
from datetime import datetime
from pyspark.sql.streaming import StatefulProcessor, StatefulProcessorHandle
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from typing import Iterator

spark.conf.set("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")

# Define output schema for the joined data
output_schema = StructType([
    StructField("user_id", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("profile_name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("preferred_category", StringType(), True)
])

class CustomStreamJoinProcessor(StatefulProcessor):
    # Buffer each user's profile, preference, and activity records in state.
    def init(self, handle: StatefulProcessorHandle) -> None:
        self.handle = handle

        profile_schema = StructType([
            StructField("name", StringType(), True),
            StructField("email", StringType(), True)
        ])
        preferences_schema = StructType([
            StructField("preferred_category", StringType(), True)
        ])
        activity_schema = StructType([
            StructField("event_type", StringType(), True),
            StructField("timestamp", TimestampType(), True)
        ])

        # One value state per record type. The grouping key is user_id, so each
        # state holds the latest record of that type for the user.
        # Profile and preference state expire after an hour of inactivity via TTL
        self.profile_state = handle.getValueState("userProfile", profile_schema, ttlDurationMs=3600000)
        self.preferences_state = handle.getValueState("userPreferences", preferences_schema, ttlDurationMs=3600000)
        self.activity_state = handle.getValueState("userActivity", activity_schema)

    # Route each incoming record by its type and buffer it in state. When an
    # activity event arrives, set a timer to emit the enriched join after a delay.
    def handleInputRows(self, key, rows: Iterator[pd.DataFrame], timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            for _, row in pdf.iterrows():
                record_type = row["record_type"]
                if record_type == "activity":
                    self.activity_state.update((row["event_type"], row["timestamp"]))
                    # Set a timer to process this event after a 10-second delay
                    self.handle.registerTimer(timerValues.getCurrentProcessingTimeInMs() + 10000)
                elif record_type == "profile":
                    self.profile_state.update((row["name"], row["email"]))
                elif record_type == "preference":
                    self.preferences_state.update((row["preferred_category"],))

        # No immediate output; the enriched row is emitted when the timer expires
        return iter([])

    # Perform the lookup after the delay, handling out-of-order and late-arriving records.
    def handleExpiredTimer(self, key, timerValues, expiredTimerInfo) -> Iterator[pd.DataFrame]:
        if not self.activity_state.exists():
            return iter([])

        activity = self.activity_state.get()
        profile = self.profile_state.get() if self.profile_state.exists() else None
        preferences = self.preferences_state.get() if self.preferences_state.exists() else None

        # Combine data from the different states into a single output row
        output_row = {
            "user_id": key[0],
            "event_type": activity[0],
            "timestamp": activity[1],
            "profile_name": profile[0] if profile else None,
            "email": profile[1] if profile else None,
            "preferred_category": preferences[0] if preferences else None
        }
        # The activity has been consumed by this join, so clear it from state
        self.activity_state.clear()
        return iter([pd.DataFrame([output_row])])

    def close(self) -> None:
        pass

# Create a dedicated schema for the example tables
spark.sql("CREATE SCHEMA IF NOT EXISTS main.stateful_examples")

# Seed a small Delta table with profile, preference, and activity records for one user
spark.sql("DROP TABLE IF EXISTS main.stateful_examples.user_events")
input_schema = StructType([
    StructField("user_id", StringType()),
    StructField("record_type", StringType()),
    StructField("event_type", StringType()),
    StructField("timestamp", TimestampType()),
    StructField("name", StringType()),
    StructField("email", StringType()),
    StructField("preferred_category", StringType())
])
spark.createDataFrame(
    [
        ("u1", "profile", None, None, "Alice", "alice@example.com", None),
        ("u1", "preference", None, None, None, None, "electronics"),
        ("u1", "activity", "purchase", datetime(2024, 1, 1, 12, 0, 0), None, None, None),
    ],
    input_schema,
).write.saveAsTable("main.stateful_examples.user_events")

df = spark.readStream.table("main.stateful_examples.user_events")

# Apply transformWithState. ProcessingTime mode enables the timer that fires the join.
q = (
    df.groupBy("user_id")
    .transformWithStateInPandas(
        statefulProcessor=CustomStreamJoinProcessor(),
        outputStructType=output_schema,
        outputMode="Append",
        timeMode="ProcessingTime",
    )
    .writeStream.format("memory")
    .queryName("enriched_events")
    .option("checkpointLocation", f"/tmp/checkpoint_{uuid.uuid4()}")
    .trigger(processingTime="5 seconds")
    .start()
)

# Wait past the 10-second timer so it fires, then stop the query
time.sleep(30)
q.stop()

# The enriched row joins the activity with the buffered profile and preference
display(spark.sql("SELECT * FROM enriched_events"))
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
// Import the necessary libraries
import org.apache.spark.sql.streaming._
import org.apache.spark.sql.Encoders
import spark.implicits._
import java.sql.Timestamp
import java.util.UUID
import java.time.Duration

// Unified input record: every event arrives on one stream, tagged by record_type
case class UserRecord(
    user_id: String,
    record_type: String,
    event_type: Option[String],
    timestamp: Option[Timestamp],
    name: Option[String],
    email: Option[String],
    preferred_category: Option[String]
)

case class UserActivity(event_type: String, timestamp: Timestamp)
case class UserProfile(name: String, email: String)
case class UserPreferences(preferred_category: String)

// Enriched user event combining activity with profile and preference data
case class EnrichedUserEvent(
    user_id: String,
    event_type: String,
    timestamp: Timestamp,
    profile_name: Option[String],
    email: Option[String],
    preferred_category: Option[String]
)

// Custom stateful processor for the stream-stream join
class CustomStreamJoinProcessor extends StatefulProcessor[String, UserRecord, EnrichedUserEvent] {
  // One value state per record type. The grouping key is user_id, so each state
  // holds the latest record of that type for the user.
  @transient private var _profileState: ValueState[UserProfile] = _
  @transient private var _preferencesState: ValueState[UserPreferences] = _
  @transient private var _activityState: ValueState[UserActivity] = _

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    // Profile and preference state expire after an hour of inactivity via TTL
    _profileState = getHandle.getValueState[UserProfile]("profileState", Encoders.product[UserProfile], TTLConfig(Duration.ofHours(1)))
    _preferencesState = getHandle.getValueState[UserPreferences]("preferencesState", Encoders.product[UserPreferences], TTLConfig(Duration.ofHours(1)))
    _activityState = getHandle.getValueState[UserActivity]("activityState", Encoders.product[UserActivity], TTLConfig.NONE)
  }

  // Route each incoming record by its type and buffer it in state. When an
  // activity event arrives, set a timer to emit the enriched join after a delay.
  override def handleInputRows(
      key: String,
      inputRows: Iterator[UserRecord],
      timerValues: TimerValues): Iterator[EnrichedUserEvent] = {
    inputRows.foreach { rec =>
      rec.record_type match {
        case "activity" =>
          _activityState.update(UserActivity(rec.event_type.getOrElse(""), rec.timestamp.orNull))
          getHandle.registerTimer(timerValues.getCurrentProcessingTimeInMs() + 10000)
        case "profile" =>
          _profileState.update(UserProfile(rec.name.getOrElse(""), rec.email.getOrElse("")))
        case "preference" =>
          _preferencesState.update(UserPreferences(rec.preferred_category.getOrElse("")))
        case _ =>
      }
    }
    Iterator.empty
  }

  // When the timer expires, join the buffered activity with the latest profile and preference
  override def handleExpiredTimer(
      key: String,
      timerValues: TimerValues,
      expiredTimerInfo: ExpiredTimerInfo): Iterator[EnrichedUserEvent] = {
    if (!_activityState.exists()) {
      Iterator.empty
    } else {
      val activity = _activityState.get()
      val profile = if (_profileState.exists()) Some(_profileState.get()) else None
      val preferences = if (_preferencesState.exists()) Some(_preferencesState.get()) else None
      // The activity has been consumed by this join, so clear it from state
      _activityState.clear()
      Iterator.single(EnrichedUserEvent(
        user_id = key,
        event_type = activity.event_type,
        timestamp = activity.timestamp,
        profile_name = profile.map(_.name),
        email = profile.map(_.email),
        preferred_category = preferences.map(_.preferred_category)
      ))
    }
  }
}

// Create a dedicated schema for the example tables
spark.sql("CREATE SCHEMA IF NOT EXISTS main.stateful_examples")

// Seed a small Delta table with profile, preference, and activity records for one user
spark.sql("DROP TABLE IF EXISTS main.stateful_examples.user_events_scala")
Seq(
  UserRecord("u1", "profile", None, None, Some("Alice"), Some("alice@example.com"), None),
  UserRecord("u1", "preference", None, None, None, None, Some("electronics")),
  UserRecord("u1", "activity", Some("purchase"), Some(Timestamp.valueOf("2024-01-01 12:00:00")), None, None, None)
).toDF().write.saveAsTable("main.stateful_examples.user_events_scala")

// Apply the custom stateful processor. ProcessingTime mode enables the join timer.
val enrichedStream = spark.readStream
  .table("main.stateful_examples.user_events_scala")
  .as[UserRecord]
  .groupByKey(_.user_id)
  .transformWithState(
    new CustomStreamJoinProcessor(),
    TimeMode.ProcessingTime(),
    OutputMode.Append()
  )

val q = enrichedStream.writeStream
  .format("memory")
  .queryName("enriched_events_scala")
  .option("checkpointLocation", s"/tmp/checkpoint_${UUID.randomUUID()}")
  .trigger(Trigger.ProcessingTime("5 seconds"))
  .start()

// Wait past the 10-second timer so it fires, then stop the query
Thread.sleep(30000)
q.stop()

// The enriched row joins the activity with the buffered profile and preference
spark.sql("SELECT * FROM enriched_events_scala").show(false)
```

---

## <a id="topk">10. Top-K-Berechnung</a>

Das folgende Beispiel verwendet eine `ListState` mit einer Priority Queue, um die Top-K-Elemente eines Streams für jeden Gruppierungsschlüssel nahezu in Echtzeit zu pflegen und zu aktualisieren.

- Top-K Python: [Notebook abrufen](https://docs.databricks.com/notebooks/source/streaming/tws-topk-python.html)
- Top-K Scala: [Notebook abrufen](https://docs.databricks.com/notebooks/source/streaming/tws-topk-scala.html)

---

## <a id="quellen">11. Quellen</a>

- Example stateful applications (Original, GCP): https://docs.databricks.com/gcp/en/stateful-applications/examples
- Example stateful applications (Mirror, verifiziert/vollständig abgerufen, Azure): https://learn.microsoft.com/en-us/azure/databricks/stateful-applications/examples

**Stand:** 2026-08-22; Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
