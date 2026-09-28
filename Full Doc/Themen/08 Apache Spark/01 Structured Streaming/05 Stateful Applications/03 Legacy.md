# Legacy Arbitrary Stateful Operators — Referenz

Dieses Dokument beschreibt die Legacy-Operatoren `mapGroupsWithState` und `flatMapGroupsWithState` für beliebige (arbitrary) Stateful-Verarbeitung in Structured Streaming. Der Original-Inhalt bei `https://docs.databricks.com/gcp/en/stateful-applications/legacy` wurde von WebFetch nur stark verkürzt (zusammengefasst) zurückgegeben; als vollständige, wortgetreue Quelle wurde daher die inhaltsgleiche Azure-Mirror-Seite `https://learn.microsoft.com/en-us/azure/databricks/stateful-applications/legacy` per WebFetch abgerufen und verifiziert. Die Codebeispiele wurden am 2026-09-28 aus dem Roh-HTML der AWS-Seite ergänzt.

## Abschnittsübersicht
1. [Einleitung](#einleitung)
2. [Initialen State für mapGroupsWithState angeben](#initial-state)
3. [Die Update-Funktion von mapGroupsWithState testen](#test-funktion)
4. [Quellen](#quellen)

---

## <a id="einleitung">1. Einleitung</a>

> **Hinweis:** Databricks empfiehlt, `transformWithState` zum Bauen eigener Stateful-Anwendungen zu verwenden. Siehe [00 Uebersicht.md](00%20Uebersicht.md) (Original: "Build a custom stateful application with transformWithState").

Dieser Artikel enthält Informationen zu Features, die `mapGroupsWithState` und `flatMapGroupsWithState` unterstützen. Weitere Details zu diesen Operatoren finden sich im "Apache Spark Structured Streaming Programming Guide" (Abschnitt "Arbitrary Stateful Operations").

---

## <a id="initial-state">2. Initialen State für mapGroupsWithState angeben</a>

Ein benutzerdefinierter initialer State für Structured-Streaming-Stateful-Verarbeitung kann mit `flatMapGroupsWithState` oder `mapGroupsWithState` angegeben werden. Damit wird vermieden, Daten erneut verarbeiten zu müssen, wenn ein Stateful-Stream ohne gültigen Checkpoint gestartet wird.

Signaturen der beiden Operatoren mit Parameter `initialState`:

```scala
def mapGroupsWithState[S: Encoder, U: Encoder](
    timeoutConf: GroupStateTimeout,
    initialState: KeyValueGroupedDataset[K, S])(
    func: (K, Iterator[V], GroupState[S]) => U): Dataset[U]

def flatMapGroupsWithState[S: Encoder, U: Encoder](
    outputMode: OutputMode,
    timeoutConf: GroupStateTimeout,
    initialState: KeyValueGroupedDataset[K, S])(
    func: (K, Iterator[V], GroupState[S]) => Iterator[U])
```

Beispiel mit initialem State für den Operator `flatMapGroupsWithState`:

```scala
val fruitCountFunc =(key: String, values: Iterator[String], state: GroupState[RunningCount]) => {
  val count = state.getOption.map(_.count).getOrElse(0L) + valList.size
  state.update(new RunningCount(count))
  Iterator((key, count.toString))
}

val fruitCountInitialDS: Dataset[(String, RunningCount)] = Seq(
  ("apple", new RunningCount(1)),
  ("orange", new RunningCount(2)),
  ("mango", new RunningCount(5)),
).toDS()

val fruitCountInitial = initialState.groupByKey(x => x._1).mapValues(_._2)

fruitStream
  .groupByKey(x => x)
  .flatMapGroupsWithState(Update, GroupStateTimeout.NoTimeout, fruitCountInitial)(fruitCountFunc)
```

Beispiel mit initialem State für den Operator `mapGroupsWithState`:

```scala
val fruitCountFunc =(key: String, values: Iterator[String], state: GroupState[RunningCount]) => {
  val count = state.getOption.map(_.count).getOrElse(0L) + valList.size
  state.update(new RunningCount(count))
  (key, count.toString)
}

val fruitCountInitialDS: Dataset[(String, RunningCount)] = Seq(
  ("apple", new RunningCount(1)),
  ("orange", new RunningCount(2)),
  ("mango", new RunningCount(5)),
).toDS()

val fruitCountInitial = initialState.groupByKey(x => x._1).mapValues(_._2)

fruitStream
  .groupByKey(x => x)
  .mapGroupsWithState(GroupStateTimeout.NoTimeout, fruitCountInitial)(fruitCountFunc)
```

**Unterschied der beiden Varianten:** `flatMapGroupsWithState` gibt einen `Iterator` zurück (0 bis n Ausgabezeilen pro Key) und verlangt zusätzlich einen `OutputMode`; `mapGroupsWithState` gibt genau **einen** Wert pro Key zurück.

> **Hinweis zum Doku-Code (unverändert übernommen):** Die Beispiele sind Skizzen und so nicht direkt lauffähig. Die Funktion verwendet `valList.size`, obwohl der Parameter `values` heißt, und `fruitCountInitial` wird aus `initialState` gebildet statt aus dem zuvor definierten `fruitCountInitialDS`. Gemeint ist jeweils `values` bzw. `fruitCountInitialDS`.

---

## <a id="test-funktion">3. Die Update-Funktion von mapGroupsWithState testen</a>

Die `TestGroupState`-API ermöglicht es, die State-Update-Funktion zu testen, die für `Dataset.groupByKey(...).mapGroupsWithState(...)` und `Dataset.groupByKey(...).flatMapGroupsWithState(...)` verwendet wird.

Die State-Update-Funktion nimmt den vorherigen State als Eingabe über ein Objekt vom Typ `GroupState` entgegen. Siehe die Apache-Spark-`GroupState`-Referenzdokumentation. Beispiel:

```scala
import org.apache.spark.sql.streaming._
import org.apache.spark.api.java.Optional

test("flatMapGroupsWithState's state update function") {
  var prevState = TestGroupState.create[UserStatus](
    optionalState = Optional.empty[UserStatus],
    timeoutConf = GroupStateTimeout.EventTimeTimeout,
    batchProcessingTimeMs = 1L,
    eventTimeWatermarkMs = Optional.of(1L),
    hasTimedOut = false)

  val userId: String = ...
  val actions: Iterator[UserAction] = ...

  assert(!prevState.hasUpdated)

  updateState(userId, actions, prevState)

  assert(prevState.hasUpdated)
}
```

Der Test erzeugt mit `TestGroupState.create` einen leeren State (Event-Time-Timeout, Watermark 1 ms), prüft, dass er noch nicht aktualisiert ist, ruft die eigene Update-Funktion `updateState` auf und prüft danach mit `hasUpdated`, dass die Funktion den State geändert hat.

---

## <a id="quellen">4. Quellen</a>

- Legacy arbitrary stateful operators (Original, GCP): https://docs.databricks.com/gcp/en/stateful-applications/legacy
- Legacy arbitrary stateful operators (Mirror, verifiziert/vollständig abgerufen, Azure): https://learn.microsoft.com/en-us/azure/databricks/stateful-applications/legacy
- Legacy arbitrary stateful operators (AWS, Codebeispiele): https://docs.databricks.com/aws/en/stateful-applications/legacy

**Stand:** 2026-09-28 (Codebeispiele aus der AWS-Doku ergänzt; ursprünglich 2026-08-22).
