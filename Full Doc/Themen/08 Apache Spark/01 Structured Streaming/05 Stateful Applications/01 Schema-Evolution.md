# Schema-Evolution im State-Store — Referenz

Dieses Dokument gibt einen Überblick über Schema-Evolution im State-Store und Beispiele für unterstützte Arten von Schemaänderungen bei `transformWithState`.

## Abschnittsübersicht
1. [Was ist Schema-Evolution im State-Store?](#was-ist-schema-evolution)
2. [Voraussetzungen](#voraussetzungen)
3. [Unterstützte Schema-Evolution-Muster im State-Store](#unterstuetzte-muster)
4. [Wann tritt Schema-Evolution auf?](#wann)
5. [Nicht unterstützte Schema-Evolution-Muster](#nicht-unterstuetzt)
6. [Type Widening im State-Store](#type-widening)
7. [Felder zu State-Store-Werten hinzufügen](#add-fields)
8. [Felder aus State-Store-Werten entfernen](#remove-fields)
9. [Felder in einer State-Variable neu anordnen](#reorder-fields)
10. [Eine State-Variable zu einer Stateful-Anwendung hinzufügen](#add-variable)
11. [Eine State-Variable aus einer Stateful-Anwendung entfernen](#remove-variable)
12. [Standardwerte für hinzugefügte Felder einer State-Variable](#default-values)
13. [Einschränkungen (Limitations)](#limitations)

---

## <a id="was-ist-schema-evolution">1. Was ist Schema-Evolution im State-Store?</a>

Schema-Evolution bezeichnet die Fähigkeit einer Anwendung, mit Änderungen am Schema von Daten umzugehen.

Databricks unterstützt Schema-Evolution im RocksDB-State-Store für Structured-Streaming-Anwendungen, die `transformWithState` verwenden.

Schema-Evolution bietet Flexibilität für die Entwicklung und erleichtert die Wartung. Mit Schema-Evolution kann das Datenmodell oder die Datentypen im State-Store angepasst werden, ohne State-Informationen zu verlieren oder eine vollständige Neuverarbeitung historischer Daten zu erfordern.

---

## <a id="voraussetzungen">2. Voraussetzungen</a>

Um Schema-Evolution zu nutzen, muss das State-Store-Encoding-Format auf Avro gesetzt werden. Für die aktuelle Session wird dies wie folgt gesetzt:

Python:

```python
spark.conf.set("spark.sql.streaming.stateStore.encodingFormat", "avro")
```

Schema-Evolution wird nur für Stateful-Operationen unterstützt, die `transformWithState` oder `transformWithStateInPandas` verwenden. Diese Operatoren und die zugehörigen APIs und Klassen haben folgende Voraussetzungen:

- Verfügbar ab Databricks Runtime 16.2 und höher.
- Der Standard-Access-Modus wird für Python (`transformWithStateInPandas` und zeilenbasiertes `transformWithState`) ab Databricks Runtime 16.3 und höher unterstützt, und für Scala (`transformWithState`) ab Databricks Runtime 17.3 und höher.
- RocksDB ist ab Databricks Runtime 17.3 der Standard-State-Store-Provider. Für Databricks-Runtime-Versionen unter 17.3 muss der RocksDB-State-Store-Provider konfiguriert werden. Databricks empfiehlt, RocksDB als Teil der Compute-Konfiguration zu aktivieren.

Auf Databricks-Runtime-Versionen unter 17.3 wird der RocksDB-State-Store-Provider für die aktuelle Session wie folgt aktiviert:

Python:

```python
spark.conf.set("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")
```

---

## <a id="unterstuetzte-muster">3. Unterstützte Schema-Evolution-Muster im State-Store</a>

Databricks unterstützt folgende Schema-Evolution-Muster für Stateful-Structured-Streaming-Operationen:

| Muster | Beschreibung |
|---------|-------------|
| [Type Widening](#type-widening) | Datentypen von restriktiveren zu weniger restriktiven Typen ändern. |
| [Felder hinzufügen](#add-fields) | Neue Felder zum Schema bestehender State-Store-Variablen hinzufügen. |
| [Felder entfernen](#remove-fields) | Bestehende Felder aus dem Schema einer State-Store-Variable entfernen. |
| [Felder neu anordnen](#reorder-fields) | Felder in einer Variable neu anordnen. |
| [State-Variablen hinzufügen](#add-variable) | Eine neue State-Variable zu einer Anwendung hinzufügen. |
| [State-Variablen entfernen](#remove-variable) | Eine bestehende State-Variable aus einer Anwendung entfernen. |

---

## <a id="wann">4. Wann tritt Schema-Evolution auf?</a>

Schema-Evolution im State-Store resultiert aus der Aktualisierung des Codes, der die Stateful-Anwendung definiert. Daraus ergibt sich Folgendes:

- Schema-Evolution tritt nicht automatisch als Folge von Schemaänderungen in den Quelldaten der Query auf.
- Schema-Evolution tritt nur auf, wenn eine neue Version der Anwendung deployt wird. Da immer nur eine Version einer Streaming-Query gleichzeitig laufen kann, muss der Streaming-Job neu gestartet werden, um das Schema für State-Variablen weiterzuentwickeln.
- Der eigene Code definiert explizit alle State-Variablen und setzt das Schema für alle State-Variablen.
  - In Scala wird ein `Encoder` verwendet, um das Schema für jede Variable anzugeben.
  - In Python wird das Schema explizit als `StructType` konstruiert.

### <a id="nicht-unterstuetzt">4.1 Nicht unterstützte Schema-Evolution-Muster</a>

Folgende Schema-Evolution-Muster werden nicht unterstützt:

- **Felder umbenennen (Field renaming):** Das Umbenennen von Feldern wird nicht unterstützt, da Felder anhand des Namens abgeglichen werden. Der Versuch, ein Feld umzubenennen, wird so behandelt, dass das Feld entfernt und ein neues Feld hinzugefügt wird. Diese Operation führt nicht zu einem Fehler, da das Entfernen und Hinzufügen von Feldern erlaubt ist, aber die Werte des ursprünglichen Felds werden nicht in das neue Feld übernommen.

- **Umbenennung oder Typänderung von Map-Schlüsseln:** Der Name oder Typ von Schlüsseln in Map-State-Variablen kann nicht geändert werden.

- **Type Narrowing:** Type-Narrowing-Operationen, auch bekannt als _Downcasting_, werden nicht unterstützt. Diese Operationen können zu Datenverlust führen. Folgende Beispiele sind nicht unterstützte Type-Narrowing-Operationen:
  - `double` kann nicht zu `float`, `long` oder `int` verengt werden
  - `float` kann nicht zu `long` oder `int` verengt werden
  - `long` kann nicht zu `int` verengt werden

---

## <a id="type-widening">5. Type Widening im State-Store</a>

Primitive Datentypen können zu entgegenkommenderen (weniger restriktiven) Typen erweitert werden. Folgende Type-Widening-Änderungen werden unterstützt:

- `int` kann zu `long`, `float` oder `double` erhoben werden
- `long` kann zu `float` oder `double` erhoben werden
- `float` kann zu `double` erhoben werden
- `string` kann zu `bytes` erhoben werden
- `bytes` kann zu `string` erhoben werden

Bestehende Werte werden auf den neuen Typ hochgecastet (upcast). Zum Beispiel wird `12` zu `12.00`.

### 5.1 Beispiel für Type Widening mit transformWithState

Python:

```python
class IntStateProcessor(StatefulProcessor):
    def init(self, handle):
        # Initial schema with Integer field
        state_schema = StructType([
            StructField("value1", IntegerType(), True)
        ])
        self.state = handle.getValueState("testState", state_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            # Convert input value to integer and update state
            value = pdf["value"].iloc[0]
            self.state.update((int(value),))
        # Read current state
        current_state = self.state.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "stateValue": [current_state[0]]
        })

class LongStateProcessor(StatefulProcessor):
    def init(self, handle):
        # Later schema with Long field (type widening)
        state_schema = StructType([
            StructField("value1", LongType(), True)
        ])
        self.state = handle.getValueState("testState", state_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            # Convert input value to long and update state
            value = pdf["value"].iloc[0]
            # When reading state written with IntStateProcessor,
            # it will be automatically converted to Long
            self.state.update((int(value),))
        # Read current state
        current_state = self.state.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "stateValue": [current_state[0]]
        })
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
// Initial run with Integer field
case class StateV1(value1: Integer)

class ProcessorV1 extends StatefulProcessor[String, String, String] {
  @transient var state: ValueState[StateV1] = _

  private val stateV1Encoder = Encoders.product[StateV1]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state = getHandle.getValueState[StateV1](
      "testState",
      stateV1Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      state.update(StateV1(value.toInt))
      value
    }
  }
}

// Later run with Long field (type widening)
case class StateV2(value1: Long)

class ProcessorV2 extends StatefulProcessor[String, String, String] {
  @transient var state: ValueState[StateV2] = _

  private val stateV2Encoder = Encoders.product[StateV2]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state = getHandle.getValueState[StateV2](
      "testState",
      stateV2Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      state.update(StateV2(value.toLong))
      value
    }
  }
}
```

---

## <a id="add-fields">6. Felder zu State-Store-Werten hinzufügen</a>

Neue Felder können zum Schema bestehender State-Store-Werte hinzugefügt werden.

Beim Lesen von Daten, die mit dem alten Schema geschrieben wurden, gibt der Avro-Encoder für hinzugefügte Felder nativ als `null` kodierte Daten zurück.

Python interpretiert diese Werte immer als `None`. Scala hat je nach Typ des Felds unterschiedliches Standardverhalten. Databricks empfiehlt, Logik zu implementieren, die sicherstellt, dass Scala für fehlende Daten keine Werte imputiert. Siehe [Standardwerte für hinzugefügte Felder einer State-Variable](#default-values).

### 6.1 Beispiele für das Hinzufügen neuer Felder mit transformWithState

Python:

```python
class StateV1Processor(StatefulProcessor):
    def init(self, handle):
        # Initial schema with a single field
        state_schema = StructType([
            StructField("value1", IntegerType(), True)
        ])
        self.state = handle.getValueState("testState", state_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            value = pdf["value"].iloc[0]
            self.state.update((int(value),))
        current_state = self.state.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "stateValue": [current_state[0]]
        })

class StateV2Processor(StatefulProcessor):
    def init(self, handle):
        # Later schema with additional fields
        state_schema = StructType([
            StructField("value1", IntegerType(), True),
            StructField("value2", StringType(), True)
        ])
        self.state = handle.getValueState("testState", state_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            value = pdf["value"].iloc[0]
            # Read current state
            current_state = self.state.get()
            # When reading state written with StateV1(1),
            # it will be automatically converted to StateV2(1, None)
            value1 = current_state[0]
            value2 = current_state[1]
            # Now update with both fields populated
            self.state.update((int(value), f"metadata-{value}"))
        current_state = self.state.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "value1": [current_state[0]],
            "value2": [current_state[1]]
        })
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
// Initial run with single field
case class StateV1(value1: Integer)

class ProcessorV1 extends StatefulProcessor[String, String, String] {
  @transient var state: ValueState[StateV1] = _

  private val stateV1Encoder = Encoders.product[StateV1]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state = getHandle.getValueState[StateV1](
      "testState",
      stateV1Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      state.update(StateV1(value.toInt))
      value
    }
  }
}

// Later run with additional field
case class StateV2(value1: Integer, value2: String)

class ProcessorV2 extends StatefulProcessor[String, String, String] {
  @transient var state: ValueState[StateV2] = _

  private val stateV2Encoder = Encoders.product[StateV2]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state = getHandle.getValueState[StateV2](
      "testState",
      stateV2Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      // When reading state written with StateV1(1),
      // it will be automatically converted to StateV2(1, null)
      val currentState = state.get()
      // Now update with both fields populated
      state.update(StateV2(value.toInt, s"metadata-${value}"))
      value
    }
  }
}
```

---

## <a id="remove-fields">7. Felder aus State-Store-Werten entfernen</a>

Felder können aus dem Schema einer bestehenden Variable entfernt werden. Beim Lesen von Daten mit dem alten Schema werden Felder, die in den alten Daten vorhanden waren, aber nicht im neuen Schema, ignoriert.

### 7.1 Beispiele für das Entfernen von Feldern aus State-Variablen

Python:

```python
class RemoveFieldsOriginalProcessor(StatefulProcessor):
    def init(self, handle):
        # Initial schema with multiple fields
        state_schema = StructType([
            StructField("value1", IntegerType(), True),
            StructField("value2", StringType(), True)
        ])
        self.state = handle.getValueState("testState", state_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            value = pdf["value"].iloc[0]
            self.state.update((int(value), f"metadata-{value}"))
        current_state = self.state.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "value1": [current_state[0]],
            "value2": [current_state[1]]
        })

class RemoveFieldsReducedProcessor(StatefulProcessor):
    def init(self, handle):
        # Later schema with field removed
        state_schema = StructType([
            StructField("value1", IntegerType(), True)
        ])
        self.state = handle.getValueState("testState", state_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            value = pdf["value"].iloc[0]
            # When reading state written with RemoveFieldsOriginalProcessor(1, "metadata-1"),
            # it will be automatically converted to just (1,)
            current_state = self.state.get()
            value1 = current_state[0]
            self.state.update((int(value),))
        current_state = self.state.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "value1": [current_state[0]]
        })
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
// Initial run with multiple fields
case class StateV1(value1: Integer, value2: String)

class ProcessorV1 extends StatefulProcessor[String, String, String] {
  @transient var state: ValueState[StateV1] = _

  private val stateV1Encoder = Encoders.product[StateV1]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state = getHandle.getValueState[StateV1](
      "testState",
      stateV1Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      state.update(StateV1(value.toInt, s"metadata-${value}"))
      value
    }
  }
}

// Later run with field removed
case class StateV2(value1: Integer)

class ProcessorV2 extends StatefulProcessor[String, String, String] {
  @transient var state: ValueState[StateV2] = _

  private val stateV2Encoder = Encoders.product[StateV2]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state = getHandle.getValueState[StateV2](
      "testState",
      stateV2Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      // When reading state written with StateV1(1, "metadata-1"),
      // it will be automatically converted to StateV2(1)
      val currentState = state.get()
      state.update(StateV2(value.toInt))
      value
    }
  }
}
```

---

## <a id="reorder-fields">8. Felder in einer State-Variable neu anordnen</a>

Felder in einer State-Variable können neu angeordnet werden, auch wenn gleichzeitig bestehende Felder hinzugefügt oder entfernt werden. Felder in State-Variablen werden anhand des Namens abgeglichen, nicht anhand der Position.

### 8.1 Beispiele für das Neuanordnen von Feldern in einer State-Variable

Python:

```python
class OrderedFieldsProcessor(StatefulProcessor):
    def init(self, handle):
        # Initial schema with fields in original order
        state_schema = StructType([
            StructField("value1", IntegerType(), True),
            StructField("value2", StringType(), True)
        ])
        self.state = handle.getValueState("testState", state_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            value = pdf["value"].iloc[0]
            self.state.update((int(value), f"metadata-{value}"))
        current_state = self.state.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "value1": [current_state[0]],
            "value2": [current_state[1]]
        })

class ReorderedFieldsProcessor(StatefulProcessor):
    def init(self, handle):
        # Later schema with reordered fields
        state_schema = StructType([
            StructField("value2", StringType(), True),
            StructField("value1", IntegerType(), True)
        ])
        self.state = handle.getValueState("testState", state_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            value = pdf["value"].iloc[0]
            # When reading state written with OrderedFieldsProcessor(1, "metadata-1"),
            # it will be automatically converted to ("metadata-1", 1)
            current_state = self.state.get()
            value2 = current_state[0]
            value1 = current_state[1]
            self.state.update((f"new-metadata-{value}", int(value)))
        current_state = self.state.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "value2": [current_state[0]],
            "value1": [current_state[1]]
        })
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
// Initial run with fields in original order
case class StateV1(value1: Integer, value2: String)

class ProcessorV1 extends StatefulProcessor[String, String, String] {
  @transient var state: ValueState[StateV1] = _

  private val stateV1Encoder = Encoders.product[StateV1]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state = getHandle.getValueState[StateV1](
      "testState",
      stateV1Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      state.update(StateV1(value.toInt, s"metadata-${value}"))
      value
    }
  }
}

// Later run with reordered fields
case class StateV2(value2: String, value1: Integer)

class ProcessorV2 extends StatefulProcessor[String, String, String] {
  @transient var state: ValueState[StateV2] = _

  private val stateV2Encoder = Encoders.product[StateV2]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state = getHandle.getValueState[StateV2](
      "testState",
      stateV2Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      // When reading state written with StateV1(1, "metadata-1"),
      // it will be automatically converted to StateV2("metadata-1", 1)
      val currentState = state.get()
      state.update(StateV2(s"new-metadata-${value}", value.toInt))
      value
    }
  }
}
```

---

## <a id="add-variable">9. Eine State-Variable zu einer Stateful-Anwendung hinzufügen</a>

State-Variablen können auch zwischen Query-Läufen hinzugefügt werden.

> **Hinweis:** Dieses Muster erfordert keinen Avro-Encoder und wird von allen `transformWithState`-Anwendungen unterstützt.

### 9.1 Beispiel für das Hinzufügen einer State-Variable zu einer Stateful-Anwendung

Python:

```python
class MultiStateV1Processor(StatefulProcessor):
    def init(self, handle):
        # Initial schema with a single state variable
        state_schema = StructType([
            StructField("value1", IntegerType(), True),
            StructField("value2", StringType(), True)
        ])
        self.state1 = handle.getValueState("testState1", state_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            value = pdf["value"].iloc[0]
            self.state1.update((int(value), f"metadata-{value}"))
        current_state = self.state1.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "value1": [current_state[0]],
            "value2": [current_state[1]]
        })

class MultiStateV2Processor(StatefulProcessor):
    def init(self, handle):
        # Add a second state variable
        state1_schema = StructType([
            StructField("value1", IntegerType(), True),
            StructField("value2", StringType(), True)
        ])
        state2_schema = StructType([
            StructField("value1", StringType(), True),
            StructField("value2", IntegerType(), True)
        ])
        self.state1 = handle.getValueState("testState1", state1_schema)
        self.state2 = handle.getValueState("testState2", state2_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            value = pdf["value"].iloc[0]
            self.state1.update((int(value), f"metadata-{value}"))
            # Access and update the new state variable
            current_state2 = self.state2.get()  # Will be None on first run
            self.state2.update((f"new-metadata-{value}", int(value)))
        current_state1 = self.state1.get()
        current_state2 = self.state2.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "state1_value1": [current_state1[0]],
            "state1_value2": [current_state1[1]],
            "state2_value1": [current_state2[0]],
            "state2_value2": [current_state2[1]]
        })
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
// Initial run with fields in original order
case class StateV1(value1: Integer, value2: String)

class ProcessorV1 extends StatefulProcessor[String, String, String] {
  @transient var state1: ValueState[StateV1] = _

  private val stateV1Encoder = Encoders.product[StateV1]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state1 = getHandle.getValueState[StateV1](
      "testState1",
      stateV1Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      state1.update(StateV1(value.toInt, s"metadata-${value}"))
      value
    }
  }
}

case class StateV2(value1: String, value2: Integer)

class ProcessorV2 extends StatefulProcessor[String, String, String] {
  @transient var state1: ValueState[StateV1] = _
  @transient var state2: ValueState[StateV2] = _

  private val stateV1Encoder = Encoders.product[StateV1]
  private val stateV2Encoder = Encoders.product[StateV2]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state1 = getHandle.getValueState[StateV1](
      "testState1",
      stateV1Encoder,
      TTLConfig.NONE)
    state2 = getHandle.getValueState[StateV2](
      "testState2",
      stateV2Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      state1.update(StateV1(value.toInt, s"metadata-${value}"))
      val currentState2 = state2.get()
      state2.update(StateV2(s"new-metadata-${value}", value.toInt))
      value
    }
  }
}
```

---

## <a id="remove-variable">10. Eine State-Variable aus einer Stateful-Anwendung entfernen</a>

Zusätzlich zum Entfernen von Feldern können auch State-Variablen zwischen Query-Läufen entfernt werden.

> **Hinweis:** Dieses Muster erfordert keinen Avro-Encoder und wird von allen `transformWithState`-Anwendungen unterstützt.

### 10.1 Beispiel für das Entfernen einer State-Variable aus einer Stateful-Anwendung

Python:

```python
class MultiStateV2Processor(StatefulProcessor):
    def init(self, handle):
        # Add a second state variable
        state1_schema = StructType([
            StructField("value1", IntegerType(), True),
            StructField("value2", StringType(), True)
        ])
        state2_schema = StructType([
            StructField("value1", StringType(), True),
            StructField("value2", IntegerType(), True)
        ])
        self.state1 = handle.getValueState("testState1", state1_schema)
        self.state2 = handle.getValueState("testState2", state2_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            value = pdf["value"].iloc[0]
            self.state1.update((int(value), f"metadata-{value}"))
            # Access and update the new state variable
            current_state2 = self.state2.get()  # Will be None on first run
            self.state2.update((f"new-metadata-{value}", int(value)))
        current_state1 = self.state1.get()
        current_state2 = self.state2.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "state1_value1": [current_state1[0]],
            "state1_value2": [current_state1[1]],
            "state2_value1": [current_state2[0]],
            "state2_value2": [current_state2[1]]
        })

class RemoveStateVarProcessor(StatefulProcessor):
    def init(self, handle):
        # Only use one state variable and delete the other
        state_schema = StructType([
            StructField("value1", IntegerType(), True),
            StructField("value2", StringType(), True)
        ])
        self.state1 = handle.getValueState("testState1", state_schema)
        # Delete old state variable that we no longer need
        handle.deleteIfExists("testState2")
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            value = pdf["value"].iloc[0]
            self.state1.update((int(value), f"metadata-{value}"))
        current_state = self.state1.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "value1": [current_state[0]],
            "value2": [current_state[1]]
        })
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
case class StateV1(value1: Integer, value2: String)
case class StateV2(value1: Integer, value2: String)

class ProcessorV1 extends StatefulProcessor[String, String, String] {
  @transient var state1: ValueState[StateV1] = _
  @transient var state2: ValueState[StateV2] = _

  private val stateV1Encoder = Encoders.product[StateV1]
  private val stateV2Encoder = Encoders.product[StateV2]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state1 = getHandle.getValueState[StateV1](
      "testState1",
      stateV1Encoder,
      TTLConfig.NONE)
    state2 = getHandle.getValueState[StateV2](
      "testState2",
      stateV2Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      state1.update(StateV1(value.toInt, s"metadata-${value}"))
      val currentState2 = state2.get()
      state2.update(StateV2(value.toInt, s"new-metadata-${value}"))
      value
    }
  }
}

class ProcessorV2 extends StatefulProcessor[String, String, String] {
  @transient var state1: ValueState[StateV1] = _

  private val stateV1Encoder = Encoders.product[StateV1]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state1 = getHandle.getValueState[StateV1](
      "testState1",
      stateV1Encoder,
      TTLConfig.NONE)
    // delete old state variable that we no longer need
    getHandle.deleteIfExists("testState2")
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      state1.update(StateV1(value.toInt, s"metadata-${value}"))
      value
    }
  }
}
```

---

## <a id="default-values">11. Standardwerte für hinzugefügte Felder einer State-Variable</a>

Werden neue Felder zu einer bestehenden State-Variable hinzugefügt, verhalten sich mit dem alten Schema geschriebene State-Variablen wie folgt:

- Der Avro-Encoder gibt für hinzugefügte Felder einen `null`-Wert zurück.
- Python konvertiert diese Werte für alle Datentypen zu `None`.
- Das Scala-Standardverhalten unterscheidet sich je nach Datentyp:
  - Referenztypen geben `null` zurück.
  - Primitive Typen geben einen Standardwert zurück, der je nach primitivem Typ unterschiedlich ist. Beispiele sind `0` für `int`-Typen oder `false` für `bool`-Typen.

Es gibt keine eingebaute Funktionalität oder Metadaten, die das Feld als durch Schema-Evolution hinzugefügt markieren. Es muss eigene Logik implementiert werden, um mit Null-Werten umzugehen, die für Felder zurückgegeben werden, die im vorherigen Schema nicht existierten.

Für Scala können Standardwert-Imputationen vermieden werden, indem `Option[<Type>]` verwendet wird, das fehlende Werte als `None` statt mit dem Typ-Standardwert zurückgibt.

Es muss eigene Logik implementiert werden, um korrekt mit Situationen umzugehen, in denen `None`-Werte aufgrund von Schema-Evolution zurückgegeben werden.

### 11.1 Beispiel für Standardwerte bei hinzugefügten Feldern einer State-Variable

Python:

```python
class NullDefaultsProcessor(StatefulProcessor):
    def init(self, handle):
        # Initial schema
        state_schema = StructType([
            StructField("value1", IntegerType(), True),
            StructField("value2", StringType(), True)
        ])
        self.state = handle.getValueState("testState", state_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            value = pdf["value"].iloc[0]
            self.state.update((int(value), f"metadata-{value}"))
        current_state = self.state.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "value1": [current_state[0]],
            "value2": [current_state[1]]
        })

class ExpandedNullDefaultsProcessor(StatefulProcessor):
    def init(self, handle):
        # Evolution: Adding new fields with null/default values
        state_schema = StructType([
            StructField("value1", IntegerType(), True),
            StructField("value2", StringType(), True),
            StructField("value3", LongType(), True),
            StructField("value4", IntegerType(), True),
            StructField("value5", BooleanType(), True)
        ])
        self.state = handle.getValueState("testState", state_schema)
    def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
        for pdf in rows:
            value = pdf["value"].iloc[0]
            # Reading from state
            current_state = self.state.get()
            # Showing how null defaults work in Python
            # When reading state written with NullDefaultsProcessor state = (1, "metadata-1"),
            # it will be automatically converted to (1, "metadata-1", None, None, None)
            # In Python, both primitive and reference types will be None
            value1 = current_state[0]
            value2 = current_state[1]
            value3 = current_state[2]  # Will be None when evolved from older schema
            value4 = current_state[3]  # Will be None when evolved from older schema
            value5 = current_state[4]  # Will be None when evolved from older schema
            # Check if value3 is None
            if value3 is None:
                print("The value3 field is None (default value for evolution)")
                value3 = 100  # Set a real value now
            # Now update with all fields populated
            self.state.update((
                value1,
                value2,
                value3,
                value4 if value4 is not None else 42,
                value5 if value5 is not None else True
            ))
        current_state = self.state.get()
        yield pd.DataFrame({
            "id": [key[0]],
            "value1": [current_state[0]],
            "value2": [current_state[1]],
            "value3": [current_state[2]],
            "value4": [current_state[3]],
            "value5": [current_state[4]]
        })
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
// Example demonstrating how null defaults work in schema evolution

import org.apache.spark.sql.streaming._
import org.apache.spark.sql.Encoders

// Initial schema that will be evolved
case class StateV1(value1: Integer, value2: String)

class ProcessorV1 extends StatefulProcessor[String, String, String] {
  @transient var state: ValueState[StateV1] = _

  private val stateV1Encoder = Encoders.product[StateV1]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state = getHandle.getValueState[StateV1](
      "testState",
      stateV1Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      state.update(StateV1(value.toInt, s"metadata-${value}"))
      value
    }
  }
}

// Evolution: Adding a new field with null/default values
case class StateV2(value1: Integer, value2: String, value3: Long, value4: Option[Long])

class ProcessorV2 extends StatefulProcessor[String, String, String] {
  @transient var state: ValueState[StateV2] = _

  private val stateV2Encoder = Encoders.product[StateV2]

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    state = getHandle.getValueState[StateV2](
      "testState",
      stateV2Encoder,
      TTLConfig.NONE)
  }

  override def handleInputRows(
    key: String,
    inputRows: Iterator[String],
    timerValues: TimerValues): Iterator[String] = {
    rows.map { value =>
      // Reading from state
      val currentState = state.get()

      // Showing how null defaults work for different types
      // When reading state written with StateV1(1, "metadata-1"),
      // it will be automatically converted to StateV2(1, "metadata-1", 0L, None)
      println(s"Current state: $currentState")

      // For primitive types like Long, the UnsafeRow default for null is 0
      val longValue = if (currentState.value3 == 0L) {
        println("The value3 field is the default value (0)")
        100L // Set a real value now
      } else {
        currentState.value3
      }

      // Now update with all fields populated
      state.update(StateV2(value.toInt, s"metadata-${value}", longValue))
      value
    }
  }
}
```

---

## <a id="limitations">12. Einschränkungen (Limitations)</a>

Die folgende Tabelle beschreibt die Standard-Grenzwerte für Schema-Evolution-Änderungen:

| Beschreibung | Standard-Grenzwert | Spark-Konfiguration zum Überschreiben |
|-------------|---------------|----------------------------------|
| Schema-Evolutionen für eine State-Variable. Das Anwenden mehrerer Schemaänderungen in einem Query-Neustart zählt als eine einzelne Schema-Evolution. | 16 | `spark.sql.streaming.stateStore.valueStateSchemaEvolutionThreshold` |
| Schema-Evolutionen für die Streaming-Query. Das Anwenden mehrerer Schemaänderungen in einem Query-Neustart zählt als eine einzelne Schema-Evolution. | 128 | `spark.sql.streaming.stateStore.maxNumStateSchemaFiles` |

Folgende Punkte sollten bei der Fehlersuche zur Schema-Evolution von State-Variablen sorgfältig beachtet werden:

- Manche Muster werden für Schema-Evolution nicht unterstützt. Siehe [Nicht unterstützte Schema-Evolution-Muster](#nicht-unterstuetzt).
- Schema-Evolution hat alle Voraussetzungen von `transformWithState` und erfordert das Avro-Encoding-Format. Siehe [Voraussetzungen](#voraussetzungen).
- Eine Streaming-Query muss neu gestartet werden, um Code-Änderungen zu deployen, die zu Schema-Evolution führen.

**Stand:** Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
