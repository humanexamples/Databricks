# Asynchrone Verarbeitung mit transformWithState (Beta) — Referenz

Dieses Dokument beschreibt die asynchrone Verarbeitung der zeilenbasierten Python-`transformWithState`-API mit `asyncio`. Der Original-Inhalt bei `https://docs.databricks.com/gcp/en/stateful-applications/async` wurde von WebFetch nur stark verkürzt (zusammengefasst) zurückgegeben; als vollständige, wortgetreue Quelle wurde daher die inhaltsgleiche Azure-Mirror-Seite `https://learn.microsoft.com/en-us/azure/databricks/stateful-applications/async` per WebFetch abgerufen und verifiziert.

## Abschnittsübersicht
1. [Einleitung](#einleitung)
2. [Implementierung eines AsyncStatefulProcessor](#implementierung)
3. [Beispiel: Zeilen pro Gruppierungsschlüssel zählen](#beispiel-zaehlen)
4. [Eine Query mit einem Async-Processor ausführen](#query-ausfuehren)
5. [Beispiel: Events im events-Beispieldatensatz zählen](#beispiel-events)
6. [Asynchrone State- und Timer-Operationen](#async-operationen)
7. [Optimierung mit Async-Programmiermustern](#optimierung)
8. [Quellen](#quellen)

---

## <a id="einleitung">1. Einleitung</a>

> **Wichtig:** Die asynchrone Verarbeitung für die zeilenbasierte Python-`transformWithState`-API befindet sich im Beta-Status. Siehe "Databricks Preview-Releases".
>
> Asynchrone Verarbeitung ist ab Databricks Runtime 19 und höher verfügbar.

Python `transformWithState` unterstützt asynchrone Verarbeitung, aufgebaut auf [`asyncio`](https://docs.python.org/3/library/asyncio.html). Durch gleichzeitiges (concurrent) Ausführen von State-Operationen und benutzerdefinierter Logik über Gruppierungsschlüssel hinweg sowie durch Batching der Interprozesskommunikation hat asynchrone Verarbeitung einen höheren Durchsatz als synchrone Verarbeitung — bei nur kleinen Code-Änderungen. Dieser Durchsatzgewinn erfordert keine Drittanbieter-Async-Bibliotheken. Fortgeschrittene Nutzer können ihre Anwendungen mit Async-Programmiermustern und async-fähigen Bibliotheken weiter optimieren.

Um asynchrone Verarbeitung zu nutzen, wird ein `AsyncStatefulProcessor` anstelle des synchronen `StatefulProcessor` implementiert. Die `AsyncStatefulProcessor`-API spiegelt die synchrone `StatefulProcessor`-API, sodass die meisten Anwendungen nur kleine Änderungen benötigen, um die asynchrone API zu nutzen. Siehe [Implementierung eines AsyncStatefulProcessor](#implementierung).

Für die synchrone `transformWithState`-API und die Kernkonzepte siehe [Uebersicht.md](00%20Uebersicht.md) (Original: "Build a custom stateful application with transformWithState").

> **Hinweis:** Asynchrone Verarbeitung ist nur für die zeilenbasierte Python-`transformWithState`-API verfügbar. Sie wird weder für `transformWithStateInPandas` noch für die Scala-`transformWithState`-API unterstützt. Asynchrone Verarbeitung wird auf Serverless Compute nicht unterstützt.

---

## <a id="implementierung">2. Implementierung eines AsyncStatefulProcessor</a>

Um einen synchronen `StatefulProcessor` in einen `AsyncStatefulProcessor` umzuwandeln, sind folgende Änderungen nötig:

- Die API-Methoden (`init`, `close`, `handleInputRows`, `handleExpiredTimer` und `handleInitialState`) werden mit dem Schlüsselwort `async def` definiert.
- State- und Timer-Werte werden mit `await` gelesen und aktualisiert, oder mit Python's `asyncio`-Bibliothek ausgeführt. Dies gilt für State-Operationen wie `valueState.get()` und für Timer-Operationen wie `registerTimer`. Das Erstellen von State-Objekten, z. B. `handle.getValueState`, bleibt synchron.

Für die asynchrone Verarbeitung gelten folgende Überlegungen:

- Speichert die Anwendung Daten in Member-Variablen oder externen Systemen, empfiehlt Databricks, die Logik so umzuschreiben, dass sie für gleichzeitige Ausführung sicher ist. Da `handleInputRows` und `handleExpiredTimer` über Gruppierungsschlüssel hinweg gleichzeitig laufen können, dürfen verschachtelte (interleaved) Ausführungen gemeinsam genutzte Daten nicht korrumpieren. Die meisten Anwendungen erfüllen diese Anforderung bereits.
- Databricks empfiehlt, Fehler aus State-Operationen nicht abzufangen oder zu unterdrücken. Apache Spark behandelt diese Fehler selbst. Schlägt eine State-Operation fehl, lässt Apache Spark den Task fehlschlagen und wiederholt ihn (retry).
  - In einem `AsyncStatefulProcessor` werden Fehler von State-Operationen selbst verwaltet und nie an den eigenen Code weitergegeben.
  - In einem synchronen `StatefulProcessor` werden Fehler von State-Operationen im eigenen Code ausgelöst, aber ihr Unterdrücken kann die Datenkorrektheit gefährden.

### <a id="beispiel-zaehlen">2.1 Beispiel: Zeilen pro Gruppierungsschlüssel zählen</a>

Das folgende Beispiel definiert einen `AsyncCountProcessor`, der die Anzahl der Zeilen für jeden Gruppierungsschlüssel zählt. Die Variable `value_schema` definiert das Schema der `ValueState`, die den laufenden Zähler speichert. Im Vergleich zu einem synchronen `StatefulProcessor` sind die Änderungen das Schlüsselwort `async def` bei jeder Methode und `await` bei den State-Lese- und -Schreiboperationen. Der Aufruf von `getValueState` in `init` bleibt synchron. Der Processor wird wie folgt definiert:

```python
from pyspark.sql import Row
from pyspark.sql.streaming import AsyncStatefulProcessor, AsyncStatefulProcessorHandle
from pyspark.sql.types import StructType, StructField, LongType

value_schema = StructType([StructField("count", LongType(), True)])

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

---

## <a id="query-ausfuehren">3. Eine Query mit einem Async-Processor ausführen</a>

Um eine Query mit einem Async-Processor auszuführen, wird der eigene `AsyncStatefulProcessor` an `transformWithState` übergeben. Die Query verwendet dieselbe Syntax wie der synchrone Pfad. Die Async- und die synchrone API teilen sich dasselbe State-Format, sodass eine bestehende Query zwischen einem `AsyncStatefulProcessor` und einem synchronen `StatefulProcessor` gewechselt werden kann, während derselbe Checkpoint weiterverwendet wird.

### <a id="beispiel-events">3.1 Beispiel: Events im events-Beispieldatensatz zählen</a>

Das folgende Beispiel führt `AsyncCountProcessor` gegen den `events`-Beispieldatensatz aus. Jeder Datensatz hat ein `time`-Feld (Epoch-Sekunden) und ein `action`-Feld mit dem Wert `Open` oder `Close`. Die Query gruppiert nach `action` und zählt die Events für jeden Aktionstyp. Weitere Beispieldatensätze siehe "Sample datasets".

Die Variable `input_schema` definiert das Schema der Quelldatensätze, und die Variable `output_schema` definiert das Schema der Zeilen, die der Processor ausgibt. Um den Beispieldatensatz als Stream zu lesen, werden beide Schemas definiert, dann wird die Query wie folgt gestartet:

```python
from pyspark.sql.types import StructType, StructField, StringType, LongType

input_schema = StructType([
  StructField("time", LongType(), True),
  StructField("action", StringType(), True),
])

output_schema = StructType([
  StructField("action", StringType(), True),
  StructField("count", LongType(), True),
])

events = (
  spark.readStream.schema(input_schema)
    .option("maxFilesPerTrigger", 10)
    .json("/databricks-datasets/structured-streaming/events")
)

q = (
  events.groupBy("action")
    .transformWithState(
      statefulProcessor=AsyncCountProcessor(),
      outputStructType=output_schema,
      outputMode="Update",
      timeMode="None",
    )
    .writeStream.format("memory")
    .queryName("async_counts")
    .trigger(availableNow=True)
    .start()
)

q.awaitTermination()
```

Nachdem die Query abgeschlossen ist, wird der laufende Zähler für jeden Aktionstyp wie folgt angezeigt:

```python
display(spark.sql("SELECT action, MAX(count) AS count FROM async_counts GROUP BY action ORDER BY action"))
```

---

## <a id="async-operationen">4. Asynchrone State- und Timer-Operationen</a>

In einem `AsyncStatefulProcessor` sind State-Variablen- und Timer-Operationen, die Werte lesen oder schreiben, asynchron. Die meisten dieser Operationen geben ein einzelnes Ergebnis zurück, das mit `await` abgerufen wird. Operationen, die stattdessen eine Sammlung zurückgeben, liefern einen asynchronen Iterator, der mit `async for` konsumiert wird. Eine Einführung in `async`/`await` und asynchrone Iteratoren in Python findet sich in der "Python asyncio-Dokumentation".

Die folgende Tabelle listet Operationen auf, die ein einzelnes Ergebnis zurückgeben, das mit `await` abgerufen werden kann:

| Klasse | Operationen mit `await` |
| --- | --- |
| `AsyncValueState` | `exists`, `get`, `update`, `clear` |
| `AsyncMapState` | `exists`, `getValue`, `containsKey`, `updateValue`, `removeKey`, `clear` |
| `AsyncListState` | `exists`, `put`, `appendValue`, `appendList`, `clear` |
| `AsyncStatefulProcessorHandle` | `registerTimer`, `deleteTimer` |

Die folgende Tabelle listet Operationen auf, die einen asynchronen Iterator zurückgeben, der mit `async for` abgerufen werden kann:

| Klasse | Operationen mit `async for` |
| --- | --- |
| `AsyncMapState` | `iterator`, `keys`, `values` |
| `AsyncListState` | `get` |
| `AsyncStatefulProcessorHandle` | `listTimers` |

### 4.1 Beispiel: `async for`

Um z. B. die Werte in einer `AsyncListState` zu lesen, wird mit `async for` iteriert:

```python
total = 0
async for value in self.items.get():
  total += value[0]
```

Die Methoden, die State-Objekte erstellen und State-Variablen löschen, bleiben synchron: `getValueState`, `getMapState`, `getListState` und `deleteIfExists`.

Eine Beschreibung jedes State-Typs findet sich unter "Custom state types" (siehe [Uebersicht.md](00%20Uebersicht.md), Abschnitt 4.2).

---

## <a id="optimierung">5. Optimierung mit Async-Programmiermustern</a>

Asynchrone Verarbeitung ist nützlich, wenn die eigene Logik auf externe Operationen wartet, z. B. Netzwerkanfragen. Statt auf jede Anfrage nacheinander zu warten, wird `asyncio` verwendet, um die Anfragen gleichzeitig auszuführen und Leerlaufzeit zu reduzieren.

### 5.1 Beispiel: Gleichzeitige Anfragen mit `asyncio.gather`

Das folgende Beispiel verwendet `asyncio.gather`, um alle HTTP-Anfragen pro Zeile gleichzeitig auszulösen und auf deren Abschluss zu warten, und speichert dann den maximalen Score im State. Der Processor wird wie folgt definiert:

```python
import asyncio
import aiohttp
from pyspark.sql import Row
from pyspark.sql.streaming import AsyncStatefulProcessor

class HttpScoreRowGatherProcessor(AsyncStatefulProcessor):
  async def init(self, handle):
    self._score_state = handle.getValueState("last_score", "score double")
    self._session = aiohttp.ClientSession()

  async def _fetch_score(self, row) -> float:
    async with self._session.get(
      f"https://api.example.com/score/{row.event_id}"
    ) as resp:
      return (await resp.json())["score"]

  async def handleInputRows(self, key, rows, timerValues):
    user_id = key[0]
    scores = await asyncio.gather(*[self._fetch_score(row) for row in rows])

    max_score = max(scores)
    await self._score_state.update((max_score,))
    yield Row(user_id=user_id, score=max_score)

  async def close(self):
    await self._session.close()
```

---

## <a id="quellen">6. Quellen</a>

- Asynchronous processing with transformWithState (Beta) (Original, GCP): https://docs.databricks.com/gcp/en/stateful-applications/async
- Asynchronous processing with transformWithState (Beta) (Mirror, verifiziert/vollständig abgerufen, Azure): https://learn.microsoft.com/en-us/azure/databricks/stateful-applications/async

**Stand:** 2026-08-22.
