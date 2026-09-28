# Custom Stateful Applications mit transformWithState — Referenz

Dieses Dokument beschreibt, wie man mit `transformWithState` eigene (arbitrary) zustandsbehaftete Streaming-Anwendungen in Structured Streaming baut. Der Inhalt wurde per WebFetch gegen die Original-URL `https://docs.databricks.com/gcp/en/stateful-applications/` verifiziert und vollständig abgerufen.

## Abschnittsübersicht
1. [Einleitung](#einleitung)
2. [Voraussetzungen](#voraussetzungen)
3. [Was ist transformWithState?](#was-ist-tws)
4. [Definition eines StatefulProcessor](#statefulprocessor-def)
5. [StatefulProcessorHandle](#handle)
6. [Eigene State-Typen](#state-typen)
7. [Verwendung der State-Variablen in Methoden mit eigener Logik](#state-variablen-verwenden)
8. [Verarbeitung eingehender Zeilen (handleInputRows)](#handle-input)
9. [Behandlung abgelaufener Timer (handleExpiredTimer)](#timers)
10. [Beispiel-Anwendung](#beispiel)
11. [Zeilen ausgeben (Emit rows)](#emit-rows)
12. [Initialen State behandeln](#initial-state)
13. [Asynchrone Verarbeitung (Beta)](#async)
14. [transformWithState in Lakeflow-Pipelines verwenden](#lakeflow)
15. [Quellen](#quellen)

---

## <a id="einleitung">1. Einleitung</a>

Mit `transformWithState` können zustandsbehaftete (stateful) Streaming-Anwendungen gebaut und Lösungen mit niedriger Latenz sowie nahezu Echtzeit implementiert werden. Mit benutzerdefinierten (custom) Stateful-Operatoren lässt sich beliebige zustandsbehaftete Logik erstellen, mit der neue operative Anwendungsfälle möglich werden, die mit der traditionellen Structured-Streaming-Verarbeitung nicht umsetzbar sind.

> **Hinweis:** Für Stateful-Operationen wie Aggregationen, Deduplizierung und Streaming-Joins empfiehlt Databricks, die eingebauten Structured-Streaming-Operatoren anstelle eigener Logik zu verwenden. Siehe [Was ist Stateful Streaming?](../../04%20Stateful%20Streaming/) (Original: "What is stateful streaming?").

Databricks empfiehlt, `transformWithState` anstelle der Legacy-Operatoren wie `flatMapGroupsWithState` und `mapGroupsWithState` für beliebige (arbitrary) State-Transformationen zu verwenden. Siehe [Legacy.md](03%20Legacy.md) (Original: "Legacy arbitrary stateful operators").

---

## <a id="voraussetzungen">2. Voraussetzungen</a>

Die Operatoren `transformWithState` und `transformWithStateInPandas` haben folgende Voraussetzungen:

- Verfügbar ab Databricks Runtime 16.2 und höher.
  - Für den Real-Time-Modus wird Databricks Runtime 17.3 LTS oder höher benötigt. Siehe "Real-time mode concepts".
  - Für den Standard-Access-Modus ist Python ab Databricks Runtime 16.3 und höher verfügbar, Scala ab Databricks Runtime 17.3 und höher.
- RocksDB ist ab Databricks Runtime 17.3 der Standard-State-Store-Provider.
  - Für Databricks Runtime 17.2 und niedriger muss der RocksDB-State-Store-Provider konfiguriert werden. Databricks empfiehlt, RocksDB in der Spark-Konfiguration zu aktivieren.

Python:

```python
spark.conf.set("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")
```

---

## <a id="was-ist-tws">3. Was ist transformWithState?</a>

Der Operator `transformWithState` wendet einen benutzerdefinierten Stateful-Processor auf eine Structured-Streaming-Query an. Man muss einen eigenen Stateful-Processor implementieren, um `transformWithState` zu verwenden. Structured Streaming enthält APIs, um diesen Stateful-Processor in Python, Scala oder Java zu bauen.

`transformWithState` wird verwendet, um eigene Logik auf einen Gruppierungsschlüssel (grouping key) anzuwenden. Das grundlegende Design sieht so aus:

- Man definiert eine oder mehrere State-Variablen.
- State-Informationen bleiben für jeden Gruppierungsschlüssel erhalten. Jede State-Variable kann im benutzerdefinierten Code angesprochen werden.
- Für jeden verarbeiteten Micro-Batch stehen alle Zeilen für den Schlüssel als Iterator zur Verfügung.
- Mit dem `StatefulProcessorHandle` sowie Timern und benutzerdefinierten Bedingungen wird gesteuert, wie Zeilen ausgegeben werden.
- Um State-Ablauf und State-Größe zu steuern, unterstützen State-Werte individuelle Time-to-Live-Definitionen (TTL).

Da `transformWithState` Schema-Evolution im State-Store unterstützt, können Produktivanwendungen iteriert und aktualisiert werden, ohne historische State-Informationen zu verlieren. Nach einer Aktualisierung des State-Schemas müssen Zeilen nicht erneut verarbeitet werden, was Code-Deployments und Wartung vereinfacht. Siehe [Schema-Evolution.md](01%20Schema-Evolution.md) (Original: "Schema evolution in the state store").

> **Wichtig:** Die Databricks-Dokumentation verwendet `transformWithState`, um sowohl Python- als auch Scala-Implementierungen zu beschreiben:
> - PySpark unterstützt sowohl die zeilenbasierte `transformWithState`-API als auch den Pandas-basierten Operator `transformWithStateInPandas`.
>   - `transformWithStateInPandas` wird im Real-Time-Modus nicht unterstützt. Stattdessen wird `transformWithState` verwendet. Details siehe "transformWithState in real-time mode".
>   - Die zeilenbasierte `transformWithState`-API unterstützt asynchrone Verarbeitung mit `asyncio` für höheren Durchsatz. Asynchrone Verarbeitung wird auf Serverless Compute nicht unterstützt. Siehe [Asynchrone Verarbeitung (Beta)](#async).
> - Scala unterstützt nur die zeilenbasierte `transformWithState`-API.
>
> Die Scala- und Python-Implementierungen von `transformWithState` haben dieselben Fähigkeiten, unterscheiden sich aber in der Syntax.

---

## <a id="statefulprocessor-def">4. Definition eines StatefulProcessor</a>

Ein eigener Stateful-Processor wird definiert, indem die Klasse `StatefulProcessor` erweitert und ihre Methoden implementiert werden.

Spark übergibt an die `init`-Methode des `StatefulProcessor` einen `StatefulProcessorHandle`. Mit diesem Handle werden State-Variablen erzeugt und mit dem State-Store interagiert.

`transformWithState` unterstützt drei State-Typen: `ValueState`, `ListState` und `MapState`. Jeder Typ speichert den State für jeden Gruppierungsschlüssel mit einer unterschiedlichen zugrunde liegenden Datenstruktur.

Folgende Methoden werden implementiert, um eigene Logik zu definieren:

- `handleInputRows` implementieren, um zu steuern, wie die Anwendung Daten verarbeitet, den State aktualisiert und für jeden Micro-Batch Zeilen ausgibt. Siehe [Verarbeitung eingehender Zeilen](#handle-input).
- `handleExpiredTimer` implementieren, um zeitbasierte Logik auszuführen, unabhängig davon, ob der Gruppierungsschlüssel in einem Micro-Batch neue Zeilen erhält. Siehe [Behandlung abgelaufener Timer](#timers).
- Optional `handleInitialState` implementieren, um State vorzubefüllen, bevor die Anwendung Eingabezeilen verarbeitet. Siehe [Initialen State behandeln](#initial-state).

Die folgende Tabelle vergleicht das funktionale Verhalten dieser Methoden:

| Verhalten | `handleInputRows` | `handleExpiredTimer` |
|----------|-------------------|----------------------|
| State-Werte lesen, schreiben, aktualisieren oder löschen | Ja | Ja |
| Timer erstellen oder löschen | Ja | Ja |
| Zeilen ausgeben | Ja | Ja |
| Über Zeilen im aktuellen Micro-Batch iterieren | Ja | Nein |
| Logik basierend auf verstrichener Zeit auslösen | Nein | Ja |

`handleInputRows` und `handleExpiredTimer` können kombiniert werden, um bei Bedarf komplexe Logik zu implementieren.

Beispiel: Eine Anwendung könnte `handleInputRows` verwenden, um für jeden Micro-Batch State-Werte zu aktualisieren und einen Timer 10 Sekunden in der Zukunft zu setzen. Werden keine weiteren Zeilen verarbeitet, kann `handleExpiredTimer` verwendet werden, um die aktuellen Werte im State-Store auszugeben. Werden neue Zeilen für den Gruppierungsschlüssel verarbeitet, kann der bestehende Timer gelöscht und ein neuer Timer gesetzt werden.

### <a id="handle">4.1 StatefulProcessorHandle</a>

In PySpark ermöglicht die Klasse `StatefulProcessorHandle` den Zugriff auf Funktionen, die steuern, wie der eigene Code State-Informationen nutzt.

Beim Initialisieren eines `StatefulProcessor` muss immer der `StatefulProcessorHandle` importiert und der Variable `handle` übergeben werden. Die `handle`-Variable verknüpft die lokale Variable in der Python-Klasse mit der State-Variable.

> **Hinweis:** Scala verwendet die Methode `getHandle`.

### <a id="state-typen">4.2 Eigene State-Typen</a>

In einem einzigen Stateful-Operator können mehrere State-Objekte implementiert werden.

Der State-Typ wird anhand der vollständigen Anwendungslogik gewählt. Zum Beispiel könnten Sessions mit einer `ValueState`, gruppiert nach `user_id` und `session_id`, verfolgt werden. Oder, um Bedingungen über mehrere Sessions hinweg auszuwerten, eine `MapState`, gruppiert nach `user_id`, mit `session_id` als Map-Schlüssel.

Verwendet das State-Objekt einen `StructType`, müssen für jedes Feld im Struct eindeutige Namen für das Schema definiert werden. Diese Namen sind sichtbar, wenn der State-Store gelesen wird. Siehe "Read Structured Streaming state information".

Die folgenden Abschnitte beschreiben die von `transformWithState` unterstützten State-Typen:

#### `ValueState`

`ValueState` speichert für jeden Gruppierungsschlüssel einen einzelnen Wert.

Ein Value-State kann komplexe Typen enthalten, z. B. ein Struct oder Tupel. Für `ValueState` muss Logik implementiert werden, die den gesamten Wert ersetzt.

Die Time-to-Live für einen Value-State wird zurückgesetzt, wenn der Wert aktualisiert wird. Wird ein Quellschlüssel für `ValueState` verarbeitet, ohne den gespeicherten `ValueState` zu aktualisieren, wird die Time-to-Live nicht zurückgesetzt.

#### `ListState`

`ListState` speichert für jeden Gruppierungsschlüssel eine Liste.

Ein List-State ist eine Sammlung von Werten, die jeweils komplexe Typen enthalten können. Jeder Wert in einer Liste hat seine eigene Time-to-Live.

Elemente können zu einer Liste hinzugefügt werden, indem einzelne Elemente angehängt werden, eine Liste von Elementen angehängt wird, oder die gesamte Liste mit `put` überschrieben wird. Um die Time-to-Live zurückzusetzen, muss eine `put`-Operation verwendet werden.

#### `MapState`

`MapState` speichert für jeden Gruppierungsschlüssel eine Map. Maps sind das Apache-Spark-Äquivalent zu einem Python-Dictionary (`dict`).

Ein Map-State ist eine Sammlung eindeutiger Schlüssel, die jeweils auf einen Wert abbilden, der komplexe Typen enthalten kann. Jedes Schlüssel-Wert-Paar in einer Map hat seine eigene Time-to-Live.

Der Wert eines bestimmten Schlüssels kann aktualisiert werden, oder ein Schlüssel samt Wert kann entfernt werden. Ein einzelner Wert kann über seinen Schlüssel zurückgegeben werden, alle Schlüssel oder alle Werte können aufgelistet werden, oder ein Iterator kann zurückgegeben werden, um mit der vollständigen Menge der Schlüssel-Wert-Paare in der Map zu arbeiten.

> **Wichtig:** Gruppierungsschlüssel beschreiben die Felder, die in der `GROUP BY`-Klausel einer Structured-Streaming-Query angegeben sind. Map-States können für einen Gruppierungsschlüssel eine beliebige Anzahl von Schlüssel-Wert-Paaren enthalten.
>
> Wenn die Query z. B. `GROUP BY user_id` verwendet und für jede `session_id` eine Map definiert werden soll, ist der Gruppierungsschlüssel `user_id` und der `MapState`-Schlüssel `session_id`:

Python:

```python
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

df.groupBy("user_id").transformWithState(SessionTracker(), ...) # user_id is the grouping key
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
case class Event(userId: String, sessionId: String)

class SessionTracker extends StatefulProcessor[String, Event, (String, Long)] {
  @transient private var sessions: MapState[String, Long] = _

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    sessions = getHandle.getMapState[String, Long]("sessions", Encoders.STRING, Encoders.scalaLong, TTLConfig.NONE)
  }

  override def handleInputRows(
      key: String,
      rows: Iterator[Event],
      timerValues: TimerValues): Iterator[(String, Long)] = {
    rows.foreach { event =>
      val count = if (sessions.containsKey(event.sessionId)) sessions.getValue(event.sessionId) else 0L
      sessions.updateValue(event.sessionId, count + 1) // sessionId is the MapState key
    }
    Iterator.empty
  }
}

df.as[Event]
  .groupByKey(_.userId) // userId is the grouping key
  .transformWithState(new SessionTracker(), TimeMode.None(), OutputMode.Update())
```

#### Erstellen einer eigenen State-Variable im StatefulProcessor

Beim Initialisieren des `StatefulProcessor` wird für jedes State-Objekt eine lokale Variable erstellt, mit der in der eigenen Logik mit State-Objekten interagiert werden kann. State-Variablen werden definiert und initialisiert, indem die eingebaute `init`-Methode der Klasse `StatefulProcessor` überschrieben wird.

Mit den Methoden `getValueState`, `getListState` und `getMapState` können im `StatefulProcessor` beliebig viele State-Objekte definiert werden.

Jedes State-Objekt muss Folgendes haben:

- Einen eindeutigen Namen
- Ein Schema
  - In Python muss das Schema angegeben werden.
  - In Scala kann ein `Encoder` übergeben werden, um das State-Schema anzugeben.

Optional kann außerdem eine Time-to-Live (TTL)-Dauer in Millisekunden angegeben werden. Bei der Implementierung eines Map-States muss eine separate Schemadefinition für die Map-Schlüssel und die Werte angegeben werden.

> **Hinweis:** Der `StatefulProcessor` behandelt die Logik für Abfrage, Aktualisierung und Ausgabe von State-Informationen getrennt. Siehe [Verwendung der State-Variablen in Methoden mit eigener Logik](#state-variablen-verwenden).

---

## <a id="state-variablen-verwenden">5. Verwendung der State-Variablen in Methoden mit eigener Logik</a>

State-Objekte verfügen über Methoden, um State zu lesen, bestehende State-Informationen zu aktualisieren und den aktuellen State zu löschen.

Jeder Gruppierungsschlüssel hat eigene, dedizierte State-Informationen.

- Der `StatefulProcessor` gibt Zeilen basierend auf eigener Logik und dem angegebenen Ausgabeschema aus. Siehe [Zeilen ausgeben](#emit-rows).
- Der `statestore`-Reader wird verwendet, um auf Werte im State-Store zuzugreifen. Dieser Reader ist für Batch-Workloads gedacht und nicht für Low-Latency-Workloads. Siehe "Read Structured Streaming state information".
- Mit `handleInputRows` angegebene Logik läuft nur, wenn Zeilen für den Schlüssel in einem Micro-Batch vorhanden sind. Siehe [Verarbeitung eingehender Zeilen](#handle-input).
- `handleExpiredTimer` wird verwendet, um zeitbasierte Logik zu implementieren, die nicht davon abhängt, dass Zeilen beobachtet werden, um auszulösen. Siehe [Behandlung abgelaufener Timer](#timers).

> **Hinweis:** State-Objekte sind nach Gruppierungsschlüssel isoliert, mit folgenden Konsequenzen:
> - State-Werte können nicht von Zeilen beeinflusst werden, die einem anderen Gruppierungsschlüssel zugeordnet sind.
> - Es kann **keine** Logik implementiert werden, die auf dem Vergleich von Werten oder der Aktualisierung von State über Gruppierungsschlüssel hinweg basiert.

Werte innerhalb eines Gruppierungsschlüssels können verglichen werden. Mit einer `MapState` kann Logik mit einem zweiten Schlüssel implementiert werden, den die eigene Logik verwenden kann. Zum Beispiel ermöglicht eine Gruppierung nach `user_id` mit `ip_address` als `MapState`-Schlüssel, gleichzeitige Benutzer-Sessions zu verfolgen.

### 5.1 Erweiterte Überlegungen zum Arbeiten mit State

State-Aktualisierungen sind fehlertolerant (fault-tolerant). Stürzt ein Task ab, bevor ein Micro-Batch fertig verarbeitet wurde, verwendet der Retry den Wert aus dem letzten erfolgreichen Micro-Batch.

Für optimierte Performance empfiehlt Databricks, alle Werte im Iterator für einen gegebenen Schlüssel zu verarbeiten und Aktualisierungen in einem einzigen Write zu committen. Beim Schreiben in eine State-Variable wird ein Write nach RocksDB ausgelöst.

State-Werte haben keine Standardwerte (defaults). Erfordert die eigene Logik das Lesen bestehender State-Informationen, wird die `exists`-Methode verwendet.

Um Logik für Null-State zu implementieren, erlauben `MapState`-Variablen, einzelne Schlüssel zu prüfen oder alle Schlüssel aufzulisten.

---

## <a id="handle-input">6. Verarbeitung eingehender Zeilen (handleInputRows)</a>

Mit der Methode `handleInputRows` wird definiert, wie die Anwendung Zeilen verarbeitet und State-Werte aktualisiert. Diese Methode läuft jedes Mal, wenn die Structured-Streaming-Query Zeilen für einen Gruppierungsschlüssel verarbeitet.

Bei den meisten mit `transformWithState` implementierten Stateful-Anwendungen wird die Kernlogik mit `handleInputRows` definiert.

Für jedes verarbeitete Micro-Batch-Update stehen alle Zeilen im Micro-Batch für einen gegebenen Gruppierungsschlüssel als Iterator zur Verfügung. Benutzerdefinierte Logik kann mit allen Zeilen des aktuellen Micro-Batches und mit Werten im State-Store interagieren.

---

## <a id="timers">7. Behandlung abgelaufener Timer (handleExpiredTimer)</a>

Mit der Methode `handleExpiredTimer` wird eigene Logik implementiert, die auf verstrichener Zeit basiert.

Innerhalb eines Gruppierungsschlüssels werden Timer eindeutig anhand ihres Zeitstempels identifiziert.

Läuft ein Timer ab, wird das Ergebnis durch die in der Anwendung implementierte Logik bestimmt. Übliche Muster sind:

- Ausgeben von Informationen, die in einer State-Variable gespeichert sind.
- Entfernen (evicting) gespeicherter State-Informationen.
- Erstellen eines neuen Timers.

Abgelaufene Timer feuern auch dann, wenn in einem Micro-Batch keine Zeilen für ihren zugehörigen Schlüssel verarbeitet werden.

### 7.1 Angabe des Zeitmodus (Time Mode)

Beim Übergeben des `StatefulProcessor` an `transformWithState` muss der Zeitmodus über den Parameter `timeMode` angegeben werden.

Folgende Optionen werden unterstützt:

| Zeitmodus | Beschreibung |
|-----------|-------------|
| `ProcessingTime` | Timer und TTL werden beide unterstützt und basierend auf der Wanduhrzeit (wall-clock time) ausgewertet, zu der Apache Spark jeden Micro-Batch verarbeitet. `ProcessingTime` wird verwendet, wenn Timer in einem festen Intervall relativ zur Verarbeitungszeit der Zeilen feuern sollen, unabhängig von Zeitstempeln in den Daten. |
| `EventTime` | Timer werden unterstützt und basierend auf dem Event-Time-Watermark ausgewertet. Das Watermark rückt vor, sobald Apache Spark Zeitstempel in den Eingabedaten beobachtet. TTL wird bei `EventTime` nicht unterstützt. `EventTime` wird verwendet, wenn die Daten Zeitstempel enthalten und Timer basierend auf dem Fortschritt dieser Zeitstempel feuern sollen. Bei Verwendung von `EventTime` muss zusätzlich der Parameter `eventTimeColumnName` angegeben werden. Siehe [eventTimeColumnName](#event-time-param). |
| `NoTime` bzw. `TimeMode.None()` | Timer und TTL werden nicht unterstützt. `NoTime` wird verwendet, wenn die Stateful-Anwendung keine zeitbasierte Logik benötigt. |

#### <a id="event-time-param">eventTimeColumnName</a>

Bei Verwendung des Zeitmodus `EventTime` gibt der Parameter `eventTimeColumnName` den Namen der Spalte im Ausgabeschema an, die den Event-Zeitstempel enthält. Apache Spark verwendet diese Spalte, um das Watermark an den Ausgabestrom weiterzugeben, was korrekte nachgelagerte zeitbasierte Operationen ermöglicht.

`eventTimeColumnName` ist ein zusätzliches Argument für `transformWithState` bzw. `transformWithStateInPandas`:

Python:

```python
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

**Scala** (aus der AWS-Doku ergänzt):

```scala
val q = spark
  .readStream
  .format("delta")
  .load(srcDeltaTableDir)
  .as[(String, String)]
  .groupByKey(x => x._1)
  .transformWithState(
    new MyProcessor(),
    "outputTimestamp",
    OutputMode.Append(),
  )
  .writeStream...
```

`transformWithState` akzeptiert `eventTimeColumnName` anstelle von `timeMode`. Dieser Ansatz verwendet immer den `EventTime`-Modus:

### 7.2 Eingebaute Timer-Werte

Databricks empfiehlt, in der eigenen Stateful-Anwendung nicht die Systemuhr aufzurufen, da dies bei Task-Fehlern zu unzuverlässigen Retries führen kann. Wenn auf Verarbeitungszeit oder Watermark zugegriffen werden muss, werden die Methoden der Klasse `TimerValues` verwendet:

| `TimerValues` | Beschreibung |
|---------------|-------------|
| `getCurrentProcessingTimeInMs` | Gibt den Zeitstempel der Verarbeitungszeit für den aktuellen Batch in Millisekunden seit Epoch zurück. |
| `getCurrentWatermarkInMs` | Gibt den Zeitstempel des Watermarks für den aktuellen Batch in Millisekunden seit Epoch zurück. |

> **Hinweis:** Verarbeitungszeit beschreibt die Zeit, zu der der Micro-Batch von Apache Spark verarbeitet wird. Viele Streaming-Quellen, wie Kafka, enthalten ebenfalls eine System-Verarbeitungszeit.
>
> Watermarks bei Streaming-Queries werden oft anhand der Event-Time oder der Verarbeitungszeit der Streaming-Quelle definiert. Siehe "Apply watermarks to control data processing thresholds".
>
> Sowohl Watermarks als auch Windows können in Kombination mit `transformWithState` verwendet werden. Ähnliche Funktionalität kann in der eigenen Stateful-Anwendung durch Nutzung von TTL, Timern sowie `MapState`- oder `ListState`-Funktionalität implementiert werden.

### 7.3 Time-to-Live (TTL) für State-Typen

Um Out-of-Memory-Fehler zu verhindern und veraltete State-Typ-Werte zu entfernen, unterstützt `transformWithState` einen optionalen Time-to-Live-Wert (TTL) für jeden State-Typ-Wert. Nach Ablauf entfernt TTL State-Typ-Werte still (silently evicts). TTL löst weder `handleExpiredTimer` noch eigene Logik aus. Um beim State-Ablauf Code auszuführen, wird stattdessen ein Timer verwendet.

> **Wichtig:** Wird TTL nicht implementiert, muss State-Eviction selbst gehandhabt werden, um Out-of-Memory-Fehler zu vermeiden.

Für alle State-Typen wird TTL beim Aktualisieren von State-Informationen zurückgesetzt. TTL wird für jeden State-Typ-Wert durchgesetzt, mit unterschiedlichen Regeln je State-Typ:

- State-Variablen sind auf Gruppierungsschlüssel begrenzt (scoped).
- Bei `ValueState`-Objekten wird pro Gruppierungsschlüssel nur ein einzelner Wert gespeichert. TTL gilt für diesen Wert.
- Bei `ListState`-Objekten kann die Liste viele Werte enthalten. TTL gilt unabhängig für jeden Wert in einer Liste.
  - Obwohl TTL auf einzelne Werte in einer `ListState` begrenzt ist, kann ein einzelner Wert nur mit der `put`-Methode aktualisiert werden, die den gesamten Inhalt der `ListState`-Variable überschreibt und die TTL für alle Werte in der Liste zurücksetzt.
- Bei `MapState`-Objekten hat jeder Map-Schlüssel einen zugehörigen State-Wert. TTL gilt unabhängig für jedes Schlüssel-Wert-Paar in einer Map.

> **Hinweis:** Timer ermöglichen es, eigene Logik über den State-Ablauf hinaus zu definieren, einschließlich des Ausgebens von Zeilen. Optional können Timer verwendet werden, um sowohl State-Informationen für einen gegebenen State-Wert zu löschen als auch Werte auszugeben oder bedingte Logik auszulösen. Siehe [Behandlung abgelaufener Timer](#timers).

---

## <a id="beispiel">8. Beispiel-Anwendung</a>

Das folgende Beispiel definiert einen eigenen Stateful-Processor, `SimpleCounterProcessor`, mitsamt Beispiel-State-Variablen. `SimpleCounterProcessor` verwendet `ValueState`, `ListState` und `MapState`, um Zeilen für jeden Gruppierungsschlüssel zu zählen.

Python (Pandas):

```python
import pandas as pd
from pyspark.sql import Row
from pyspark.sql.streaming import StatefulProcessor, StatefulProcessorHandle
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
from typing import Iterator

spark.conf.set("spark.sql.streaming.stateStore.providerClass",
"org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")

output_schema = StructType(
    [
        StructField("id", StringType(), True),
        StructField("countAsString", StringType(), True),
    ])

class SimpleCounterProcessor(StatefulProcessor):
  def init(self, handle: StatefulProcessorHandle) -> None:
    value_state_schema = StructType([StructField("count", IntegerType(), True)])
    list_state_schema = StructType([StructField("count", IntegerType(), True)])
    self.value_state = handle.getValueState(stateName="valueState", schema=value_state_schema)
    self.list_state = handle.getListState(stateName="listState", schema=list_state_schema)
    # Schema can also be defined using strings and SQL DDL syntax
    self.map_state = handle.getMapState(stateName="mapState", userKeySchema="name string", valueSchema="count int")

  def handleInputRows(self, key, rows, timerValues) -> Iterator[pd.DataFrame]:
    count = 0
    for pdf in rows:
      list_state_rows = [(120,), (20,)] # A list of tuples
      self.list_state.put(list_state_rows)
      self.list_state.appendValue((111,))
      self.list_state.appendList(list_state_rows)
      pdf_count = pdf.count()
      count += pdf_count.get("value")
    self.value_state.update((count,)) # Count is passed as a tuple
    iter = self.list_state.get()
    list_state_value = next(iter)[0]
    value = count
    user_key = ("user_key",)
    if self.map_state.exists():
      if self.map_state.containsKey(user_key):
        value += self.map_state.getValue(user_key)[0]
    self.map_state.updateValue(user_key, (value,)) # Value is a tuple
    yield pd.DataFrame({"id": key, "countAsString": str(count)})

q = (df.groupBy("key")
  .transformWithStateInPandas(
    statefulProcessor=SimpleCounterProcessor(),
    outputStructType=output_schema,
    outputMode="Update",
    timeMode="None",
  )
  .writeStream...)
```

Python (row-based):

```python
from pyspark.sql import Row
from pyspark.sql.streaming import StatefulProcessor, StatefulProcessorHandle
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
from typing import Iterator

spark.conf.set("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")

output_schema = StructType(
  [
    StructField("id", StringType(), True),
    StructField("countAsString", StringType(), True),
  ])

class SimpleCounterProcessor(StatefulProcessor):
  def init(self, handle: StatefulProcessorHandle) -> None:
    value_state_schema = StructType([StructField("count", IntegerType(), True)])
    list_state_schema = StructType([StructField("count", IntegerType(), True)])
    self.value_state = handle.getValueState(stateName="valueState", schema=value_state_schema)
    self.list_state = handle.getListState(stateName="listState", schema=list_state_schema)
    self.map_state = handle.getMapState(stateName="mapState", userKeySchema="name string", valueSchema="count int")

  def handleInputRows(self, key, rows: Iterator[Row], timerValues) -> Iterator[Row]:
    count = 0
    for row in rows:
      list_state_rows = [(120,), (20,)]  # A list of tuples
      self.list_state.put(list_state_rows)
      self.list_state.appendValue((111,))
      self.list_state.appendList(list_state_rows)
      count += 1
    self.value_state.update((count,))  # Count is passed as a tuple
    iter_list = self.list_state.get()
    list_state_value = next(iter_list)[0]
    value = count
    user_key = ("user_key",)
    if self.map_state.exists():
      if self.map_state.containsKey(user_key):
        value += self.map_state.getValue(user_key)[0]
    self.map_state.updateValue(user_key, (value,))  # Value is a tuple
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

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.streaming._
import org.apache.spark.sql.{Dataset, Encoder, Encoders , DataFrame}
import org.apache.spark.sql.types._
import org.apache.spark.sql.functions._

spark.conf.set("spark.sql.streaming.stateStore.providerClass","org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")

class SimpleCounterProcessor extends StatefulProcessor[String, (String, String), (String, String)] {
  @transient private var countState: ValueState[Int] = _
  @transient private var listState: ListState[Int] = _
  @transient private var mapState: MapState[String, Int] = _

  private val longEncoder = Encoders.scalaLong
  private val intEncoder = Encoders.scalaInt
  private val stringEncoder = Encoders.STRING

  override def init(
      outputMode: OutputMode,
      timeMode: TimeMode): Unit = {
    countState = getHandle.getValueState[Int]("countState",
      intEncoder, TTLConfig.NONE)
    listState = getHandle.getListState[Int]("listState",
      intEncoder, TTLConfig.NONE)
    mapState = getHandle.getMapState[String, Int]("mapState",
      stringEncoder, intEncoder, TTLConfig.NONE)
  }

  override def handleInputRows(
      key: String,
      inputRows: Iterator[(String, String)],
      timerValues: TimerValues): Iterator[(String, String)] = {
    var count = countState.getOption().getOrElse(0)
    for (row <- inputRows) {
      val listData = Array(120, 20)
      listState.put(listData)
      listState.appendValue(count)
      listState.appendList(listData)
      count += 1
    }
    val iter = listState.get()
    var listStateValue = 0
    if (iter.hasNext) {
      listStateValue = iter.next()
    }
    countState.update(count)
    var value = count
    val userKey = "userKey"
    if (mapState.exists()) {
      if (mapState.containsKey(userKey)) {
        value += mapState.getValue(userKey)
      }
    }
    mapState.updateValue(userKey, value)
    Iterator((key, count.toString))
  }
}

val q = spark
        .readStream
        .format("delta")
        .load("$srcDeltaTableDir")
        .as[(String, String)]
        .groupByKey(x => x._1)
        .transformWithState(
            new SimpleCounterProcessor(),
            TimeMode.None(),
            OutputMode.Update(),
        )
        .writeStream...
```

Weitere Beispiele siehe [Beispiele.md](04%20Beispiele.md) (Original: "Example stateful applications").

> **Hinweis:** In Python sind State-Werte Tupel. Tupel werden an `put` und `update` übergeben, und von `get` werden Tupel erwartet.
>
> Ist das Schema für die `ValueState` z. B. eine einzelne Ganzzahl:

```python
current_value_tuple = value_state.get() # Returns the value state as a tuple
current_value = current_value_tuple[0]  # Extracts the first item in the tuple
new_value = current_value + 1           # Calculate a new value
value_state.update((new_value,))        # Pass the new value formatted as a tuple
```

#### Beispiel komplett ausführen (aus der AWS-Doku ergänzt)

Um den `SimpleCounterProcessor` direkt per Copy-and-Paste auszuprobieren: eine kleine Delta-Tabelle als Streaming-Quelle anlegen und dann die Query starten.

```python
import uuid

# Create a dedicated schema for the example tables
spark.sql("CREATE SCHEMA IF NOT EXISTS main.stateful_examples")

# Seed a small Delta table to use as the streaming source
spark.sql("DROP TABLE IF EXISTS main.stateful_examples.tws_counter_source")
spark.createDataFrame(
  [("a", "1"), ("a", "2"), ("a", "3"), ("b", "1"), ("b", "2")],
  "key string, value string",
).write.saveAsTable("main.stateful_examples.tws_counter_source")

df = spark.readStream.table("main.stateful_examples.tws_counter_source")

q = (
  df.groupBy("key")
    .transformWithState(
      statefulProcessor=SimpleCounterProcessor(),
      outputStructType=output_schema,
      outputMode="Update",
      timeMode="None",
    )
    .writeStream.format("memory")
    .queryName("counter_output")
    .option("checkpointLocation", f"/tmp/checkpoint_{uuid.uuid4()}")
    .trigger(availableNow=True)
    .start()
)

q.awaitTermination()
```

Nach Abschluss der Query die Anzahl pro Gruppierungsschlüssel anzeigen:

```python
display(spark.sql("SELECT id, countAsString FROM counter_output ORDER BY id"))
```

Der Schlüssel `a` hat drei Zeilen, `b` zwei; die Abfrage liefert:

```text
id  countAsString
a   3
b   2
```

> Dieser Ansatz gilt auch für Elemente in einer `ListState` oder Werte in einer `MapState`.

---

## <a id="emit-rows">9. Zeilen ausgeben (Emit rows)</a>

Um für jeden Gruppierungsschlüssel festzulegen, wie `transformWithState` Zeilen ausgibt, wird `handleInputRows` oder `handleExpiredTimer` verwendet. Siehe [Verarbeitung eingehender Zeilen](#handle-input) und [Behandlung abgelaufener Timer](#timers).

Eigene Stateful-Anwendungen treffen keine Annahmen darüber, wie State-Informationen verwendet werden. Für eine gegebene Bedingung kann die Anwendung keine Zeile, eine Zeile oder viele Zeilen ausgeben.

> **Hinweis:** Es können mehrere State-Werte implementiert und mehrere Bedingungen zum Ausgeben von Zeilen definiert werden, aber alle Zeilen müssen dasselbe Schema verwenden.

Bei `transformWithStateInPandas` wird das Ausgabeschema mit dem Schlüsselwort `outputStructType` definiert.

Zeilen werden mit einem Pandas-DataFrame-Objekt und `yield` ausgegeben.

Optional kann ein leerer DataFrame per `yield` zurückgegeben werden. Bei Verwendung des Ausgabemodus `update` und Ausgabe eines leeren DataFrame werden die Werte für den Gruppierungsschlüssel auf `null` aktualisiert.

Bei `transformWithState` wird das Ausgabeschema mit dem Schlüsselwort `outputStructType` definiert.

Zeilen werden mit einem `Row`-Objekt und `yield` ausgegeben.

Optional kann ein leerer Iterator zurückgegeben werden. Bei Verwendung des Ausgabemodus `update` und Ausgabe eines leeren Iterators werden die Werte für den Gruppierungsschlüssel auf `null` aktualisiert.

In Scala werden Zeilen mit einem `Iterator`-Objekt ausgegeben. Das Schema leitet sich automatisch aus dem Schema der ausgegebenen Zeilen ab.

Optional kann ein leerer `Iterator` zurückgegeben werden. Bei Verwendung des Ausgabemodus `update` und Ausgabe eines leeren `Iterator` werden die Werte für den Gruppierungsschlüssel auf `null` aktualisiert.

---

## <a id="initial-state">10. Initialen State behandeln</a>

Optional kann dem ersten Micro-Batch ein initialer State übergeben werden.

Beispielsweise könnte dies verwendet werden, um:

- Einen bestehenden Workflow in eine neue eigene Anwendung zu migrieren.
- Einen Stateful-Operator zu aktualisieren, um Schema oder Logik zu ändern.
- Einen Fehler zu beheben, der nicht automatisch behoben werden kann und manuellen Eingriff erfordert.

> **Hinweis:** Mit dem State-Store-Reader können State-Informationen aus einem bestehenden Checkpoint abgefragt werden. Siehe "Read Structured Streaming state information".

Wird eine bestehende Delta-Tabelle in eine Stateful-Anwendung konvertiert, wird die Tabelle mit `spark.read.table("table_name")` gelesen und der resultierende DataFrame übergeben. Optional können Felder ausgewählt oder angepasst werden, um sie an die neue Stateful-Anwendung anzupassen.

Ein initialer State wird über einen DataFrame mit demselben Gruppierungsschlüssel-Schema wie die Eingabezeilen bereitgestellt.

> **Hinweis:** Python verwendet `handleInitialState`, um beim Definieren eines `StatefulProcessor` den initialen State anzugeben. Scala verwendet die eigenständige Klasse `StatefulProcessorWithInitialState`.

Das folgende Beispiel initialisiert einen Zähler pro Schlüssel aus einer bestehenden Delta-Tabelle:

Python (row-based):

> Aktualisiert auf die AWS-Fassung: Das Beispiel legt die Tabellen `existing_counts` und `tws_initial_source` selbst an, startet die Query mit `availableNow` und zeigt das Ergebnis (Startwert 10 für `x` plus zwei Quellzeilen = 12).

```python
from pyspark.sql import Row
from pyspark.sql.streaming import StatefulProcessor, StatefulProcessorHandle
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
from typing import Iterator

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

  def close(self) -> None:
    pass

output_schema = StructType([
  StructField("id", StringType(), True),
  StructField("count", IntegerType(), True),
])

import uuid

# Create a dedicated schema for the example tables
spark.sql("CREATE SCHEMA IF NOT EXISTS main.stateful_examples")

# Seed existing per-key counts to load as the initial state
spark.sql("DROP TABLE IF EXISTS main.stateful_examples.existing_counts")
spark.createDataFrame(
  [("x", 10)],
  "id string, count int",
).write.saveAsTable("main.stateful_examples.existing_counts")

# Seed a small Delta table to use as the streaming source
spark.sql("DROP TABLE IF EXISTS main.stateful_examples.tws_initial_source")
spark.createDataFrame(
  [("x", "a"), ("x", "b")],
  "id string, value string",
).write.saveAsTable("main.stateful_examples.tws_initial_source")

df = spark.readStream.table("main.stateful_examples.tws_initial_source")

# Load existing counts as initial state — must use the same grouping key as the input
initial_state = spark.read.table("main.stateful_examples.existing_counts").groupBy("id")

q = (
  df.groupBy("id")
    .transformWithState(
      statefulProcessor=CounterWithInitialState(),
      outputStructType=output_schema,
      outputMode="Update",
      timeMode="None",
      initialState=initial_state,
    )
    .writeStream.format("memory")
    .queryName("initial_state_output")
    .option("checkpointLocation", f"/tmp/checkpoint_{uuid.uuid4()}")
    .trigger(availableNow=True)
    .start()
)

q.awaitTermination()

# The initial state seeds "x" with 10, and the source adds two rows, so the count is 12
display(spark.sql("SELECT id, count FROM initial_state_output ORDER BY id"))
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.streaming._
import org.apache.spark.sql.Encoders

class CounterWithInitialState
    extends StatefulProcessorWithInitialState[String, (String, String), (String, String), (String, Int)] {

  @transient private var countState: ValueState[Int] = _

  override def init(outputMode: OutputMode, timeMode: TimeMode): Unit = {
    countState = getHandle.getValueState[Int]("countState", Encoders.scalaInt, TTLConfig.NONE)
  }

  override def handleInitialState(
      key: String, initialState: (String, Int), timerValues: TimerValues): Unit = {
    countState.update(initialState._2)
  }

  override def handleInputRows(
      key: String,
      rows: Iterator[(String, String)],
      timerValues: TimerValues): Iterator[(String, String)] = {
    val count = if (countState.exists()) countState.get() else 0
    val newCount = count + rows.size
    countState.update(newCount)
    Iterator((key, newCount.toString))
  }
}

// Load existing counts as initial state — must use the same grouping key as the input
val initialState = spark.read.table("existing_counts")
  .as[(String, Int)]
  .groupByKey(_._1)

val q = spark
  .readStream
  .format("delta")
  .load(srcDeltaTableDir)
  .as[(String, String)]
  .groupByKey(_._1)
  .transformWithState(
    new CounterWithInitialState(),
    TimeMode.None(),
    OutputMode.Update(),
    initialState,
  )
  .writeStream...
```

---

## <a id="async">11. Asynchrone Verarbeitung (Beta)</a>

Python `transformWithState` unterstützt asynchrone Verarbeitung mit [asyncio](https://docs.python.org/3/library/asyncio.html), um State-Operationen und benutzerdefinierte Logik gleichzeitig (concurrent) auszuführen. Asynchrone Verarbeitung hat einen höheren Durchsatz als synchrone Verarbeitung und erfordert nur kleine Code-Änderungen, ohne Drittanbieter-Async-Bibliotheken. Um asynchrone Verarbeitung zu nutzen, wird ein `AsyncStatefulProcessor` anstelle des synchronen `StatefulProcessor` implementiert. Siehe [Asynchrone Verarbeitung.md](02%20Asynchrone%20Verarbeitung.md) (Original: "Asynchronous processing with transformWithState (Beta)").

---

## <a id="lakeflow">12. transformWithState in Lakeflow-Pipelines verwenden</a>

Der Operator `transformWithState` wird innerhalb von Lakeflow-Pipelines verwendet, um beliebige Stateful-Logik in Streaming-Pipelines mit Python zu implementieren.

Dazu werden folgende Schritte durchgeführt:

1. Das Ausgabeschema und die Stateful-Processor-Logik für die eigenen Stateful-Transformationen definieren. Beispiele siehe [Beispiele.md](04%20Beispiele.md) (Original: "Example stateful applications").
2. Einen Lakeflow-Pipeline-Flow erstellen, der den Operator `transformWithState` auf einem DataFrame aufruft. Siehe "Tutorial: Create your first pipeline using the Lakeflow Pipelines Editor".
3. Die Pipeline ausführen und die Ergebnisse in der Zieltabelle oder Senke (Sink) validieren.

Für ein Beispiel, das mit `transformWithState` Sensor-Heartbeats überwacht, siehe "Example: Use transformWithState to monitor sensor heartbeats".

---

## <a id="quellen">13. Quellen</a>

- Build a custom stateful application with transformWithState (Original, GCP): https://docs.databricks.com/gcp/en/stateful-applications/

**Stand:** 2026-08-22; Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
