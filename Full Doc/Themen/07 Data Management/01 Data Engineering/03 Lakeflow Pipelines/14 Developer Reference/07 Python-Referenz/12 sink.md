# `create_sink` — Python-Referenz

## Abschnittsübersicht

1. [Zweck](#zweck)
2. [Vollständige Signatur](#signatur)
3. [Parameter](#parameter)
4. [Einschränkungen](#einschraenkungen)
5. [Codebeispiele](#beispiele)
6. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck</a>

`create_sink()` schreibt Daten aus einer deklarativen Pipeline in einen Event-Streaming-Dienst wie Apache Kafka oder Azure Event Hubs, oder in eine Delta-Tabelle — wörtlich: *"writes to an event streaming service such as Apache Kafka or Azure Event Hubs or to a Delta table from a declarative pipeline."* `create_sink()` ist laut [SQL vs Python.md](../SQL%20vs%20Python.md) Abschnitt 5 eine Python-exklusive Funktion.

---

## <a id="signatur">2. Vollständige Signatur</a>

```python
from pyspark import pipelines as dp
dp.create_sink(name=<sink_name>, format=<format>, options=<options>)
```

---

## <a id="parameter">3. Parameter</a>

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| `name` | `str` | — | Erforderlich. Eindeutiger Bezeichner für den Sink, eindeutig innerhalb der Pipeline über alle Quelldateien hinweg. |
| `format` | `str` | — | Erforderlich. Ausgabeformat: entweder `"kafka"` oder `"delta"`. |
| `options` | `dict` | — | Optional. Sink-Konfiguration als Schlüssel-Wert-Paare (Strings); unterstützt alle Databricks-Runtime-Optionen für Kafka- und Delta-Sinks. |

---

## <a id="einschraenkungen">4. Einschränkungen</a>

Ein Sink funktioniert ausschließlich mit Append- und Update-Flows, nicht mit anderen Flow-Typen (siehe [append_flow.md](append_flow.md) und [update_flow.md](update_flow.md)).

Delta-Sinks akzeptieren voll qualifizierte Tabellennamen: `<catalog>.<schema>.<table>` für Unity Catalog bzw. `<schema>.<table>` für den Hive-Metastore.

---

## <a id="beispiele">5. Codebeispiele</a>

### Kafka-Sink

```python
from pyspark import pipelines as dp

dp.create_sink(
  "my_kafka_sink",
  "kafka",
  {
    "kafka.bootstrap.servers": "host:port",
    "topic": "my_topic"
  })
```

### Externe Delta-Tabelle als Sink (über Pfad)

```python
dp.create_sink(
  "my_delta_sink",
  "delta",
  { "path": "/path/to/my/delta/table" })
```

### Delta-Tabelle als Sink (über Tabellennamen)

```python
dp.create_sink(
  "my_delta_sink",
  "delta",
  { "tableName": "my_catalog.my_schema.my_table" })
```

---

## <a id="quellen">6. Quellen</a>

- create_sink (vollständige Signatur, Parametertabelle, Format-/Einschränkungshinweise, alle drei Codebeispiele): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-sink

**Stand:** 2026-08-19.
