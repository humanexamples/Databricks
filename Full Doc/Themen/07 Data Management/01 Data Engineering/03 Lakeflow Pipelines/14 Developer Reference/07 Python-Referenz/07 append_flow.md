# `append_flow` — Python-Referenz

## Abschnittsübersicht

1. [Zweck](#zweck)
2. [Vollständige Signatur](#signatur)
3. [Parameter](#parameter)
4. [Codebeispiele](#beispiele)
5. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck</a>

`@dp.append_flow` erzeugt Append-Flows oder Backfills für Pipeline-Tabellen — wörtlich: *"The `@dp.append_flow` decorator creates append flows or backfills for your pipeline tables. The function must return an Apache Spark streaming DataFrame."* Die dekorierte Funktion muss eine Apache-Spark-Streaming-DataFrame zurückgeben (außer bei `once = True`, siehe unten).

---

## <a id="signatur">2. Vollständige Signatur</a>

```python
@dp.append_flow(
  target = "<target-table-name>",
  name = "<flow-name>",
  once = False,
  spark_conf = {"<key>" : "<value>", "<key>" : "<value>"},
  comment = "<comment>"
)
def <function-name>():
  return (<streaming-query>)
```

---

## <a id="parameter">3. Parameter</a>

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| *(Funktion selbst)* | `function` | — | Erforderlich. Eine Funktion, die eine Apache-Spark-Streaming-DataFrame aus einer benutzerdefinierten Abfrage zurückgibt. |
| `target` | `str` | — | Erforderlich. Name der Tabelle oder des Sinks, den der Append-Flow adressiert. |
| `name` | `str` | Funktionsname | Der Flow-Name; wenn nicht angegeben, wird standardmäßig der Funktionsname verwendet. |
| `once` | `bool` | `False` | Definiert optional einen einmaligen Flow (z. B. für einen Backfill). Bei `once=True`: Der Rückgabewert muss eine Batch-DataFrame sein, keine Streaming-DataFrame; der Flow läuft standardmäßig nur einmal, außer die Pipeline durchläuft einen vollständigen Refresh. |
| `comment` | `str` | — | Eine Beschreibung für den Flow. |
| `spark_conf` | `dict` | — | Eine Liste von Spark-Konfigurationen für die Ausführung dieser Abfrage. |

---

## <a id="beispiele">4. Codebeispiele</a>

### Append-Flow und Backfill in einen Delta-Sink

```python
from pyspark import pipelines as dp
dp.create_sink("my_sink", "delta", {"path": "/tmp/delta_sink"})

@dp.append_flow(name = "flow", target = "my_sink")
def flowFunc():
  return <streaming-query>

@dp.append_flow(name = "backfill", target = "my_sink", once = True)
def backfillFlowFunc():
    return (
      spark.read
      .format("json")
      .load("/path/to/backfill/")
    )
```

### Append-Flow in einen Kafka-Sink

```python
dp.create_sink(
  "my_kafka_sink",
  "kafka",
  {
    "kafka.bootstrap.servers": "host:port",
    "topic": "my_topic"
  })

@dp.append_flow(name = "flow", target = "my_kafka_sink")
def myFlow():
  return read_stream("xxx").select(F.to_json(F.struct("*")).alias("value"))
```

---

## <a id="quellen">5. Quellen</a>

- append_flow (vollständige Signatur, Parametertabelle, beide Codebeispiele): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-append-flow

**Stand:** 2026-08-19.
