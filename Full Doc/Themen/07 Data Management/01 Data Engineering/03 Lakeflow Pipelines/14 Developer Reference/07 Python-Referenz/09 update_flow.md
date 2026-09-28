# `@dp.update_flow` — Python-Referenz

## Abschnittsübersicht

1. [Zweck](#zweck)
2. [Vollständige Signatur](#signatur)
3. [Parameter](#parameter)
4. [Rückgabetyp](#rueckgabe)
5. [Einschränkung: keine Delta-Tabellen-Sinks](#einschraenkung)
6. [Codebeispiele](#beispiele)
7. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck</a>

`@dp.update_flow` definiert einen Flow, der fortlaufend aktualisierte Ergebnisse (z. B. laufende Aggregationen) in einen Sink schreibt — im Unterschied zu `@dp.append_flow`, das nur anhängt (siehe [append_flow.md](append_flow.md)).

---

## <a id="signatur">2. Vollständige Signatur</a>

```python
@dp.update_flow(
    target = "<sink-name>",
    name = "<flow-name>",
    spark_conf = {"<key>" : "<value>", "<key>" : "<value>"},
    comment = "<comment>",
    import_checkpoint = "<checkpoint-path>"
)
def <function-name>():
    return (<streaming-query>)
```

---

## <a id="parameter">3. Parameter</a>

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| *(Funktion selbst)* | `function` | — | Erforderlich. Eine Funktion, die eine Apache-Spark-Streaming-DataFrame aus einer benutzerdefinierten Abfrage zurückgibt. |
| `target` | `str` | — | Erforderlich. Name des Sinks, in den dieser Flow schreibt. |
| `name` | `str` | Funktionsname | Der Flow-Name. Wenn nicht angegeben, standardmäßig der Funktionsname. |
| `comment` | `str` | — | Eine Beschreibung für den Flow. |
| `spark_conf` | `dict` | — | Ein Dict von Spark-Konfigurationen für die Ausführung dieser Abfrage. |
| `import_checkpoint` | `str` | — | Ein externer Checkpoint-Pfad, der vor Start des Flows importiert wird. |

---

## <a id="rueckgabe">4. Rückgabetyp</a>

Implizite Rückgabe einer Streaming-DataFrame, konfiguriert zum Schreiben in den angegebenen Sink.

---

## <a id="einschraenkung">5. Einschränkung: keine Delta-Tabellen-Sinks</a>

Die Doku stellt ausdrücklich klar: *"Delta table sinks are not supported as targets for update flows."* — Delta-Tabellen-Sinks werden als Ziel von Update-Flows nicht unterstützt (im Unterschied zu Append-Flows, die sowohl Kafka- als auch Delta-Sinks als Ziel akzeptieren, siehe [sink.md](sink.md)).

---

## <a id="beispiele">6. Codebeispiele</a>

### Kafka-Aggregation

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

### Real-Time-Modus (`pipelines.trigger`)

```python
@dp.update_flow(
    name="my_rtm_flow",
    target="my_kafka_sink",
    spark_conf={
        "pipelines.trigger": "RealTime",
        "pipelines.trigger.interval": "5 minutes",
    }
)
def my_real_time_flow():
    return (
        spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", broker_address)
            .option("subscribe", input_topic)
            .load()
    )
```

---

## <a id="quellen">7. Quellen</a>

- update_flow (vollständige Signatur, Parametertabelle, Delta-Sink-Einschränkung, beide Codebeispiele inkl. Real-Time-Modus): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-update-flow

**Stand:** 2026-08-19.
