# `foreach_batch_sink` — Python-Referenz

## Abschnittsübersicht

1. [Zweck](#zweck)
2. [Vollständige Signatur](#signatur)
3. [Parameter](#parameter)
4. [Verhalten bei `batch_id == 0`](#batch-id)
5. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck</a>

`@dp.foreach_batch_sink` definiert einen ForEachBatch-Sink, der einen Stream als Serie von Micro-Batches verarbeitet, die in Python mit benutzerdefinierter Logik behandelt werden — wörtlich: *"defines a ForEachBatch sink, which processes a stream as a series of micro-batches that you handle in Python with custom logic."* `foreach_batch_sink()` ist laut [SQL vs Python.md](../SQL%20vs%20Python.md) Abschnitt 5 eine Python-exklusive Funktion. Als Ziel (`target`) eines Append-Flows referenziert, dient er zum Schreiben transformierter Daten mit benutzerdefinierter Logik.

---

## <a id="signatur">2. Vollständige Signatur</a>

```python
from pyspark import pipelines as dp

@dp.foreach_batch_sink(name="<name>")
def batch_handler(df, batch_id):
    # benutzerdefinierte Logik
```

---

## <a id="parameter">3. Parameter</a>

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| `name` | `str` | Name der UDF | Optional. Ein eindeutiger Name zur Identifikation des Sinks innerhalb der Pipeline. Wenn nicht angegeben, wird standardmäßig der Name der UDF verwendet. |
| *(dekorierte Funktion / UDF)* | `function(df, batch_id)` | — | Die benutzerdefinierte Funktion (UDF), die für jeden Micro-Batch aufgerufen wird. |
| `df` (Parameter der UDF) | `DataFrame` | — | Spark-DataFrame mit den Daten des aktuellen Micro-Batches. |
| `batch_id` (Parameter der UDF) | `int` | — | Die ganzzahlige ID des Micro-Batches. Spark erhöht diese ID bei jedem Trigger-Intervall. |

---

## <a id="batch-id">4. Verhalten bei `batch_id == 0`</a>

Eine `batch_id` von `0` zeigt entweder den Stream-Start oder den Beginn eines vollständigen Refreshs (Full Refresh) an. Die Doku weist ausdrücklich darauf hin, dass der Code in `foreach_batch_sink` einen Full Refresh für nachgelagerte Datenquellen korrekt behandeln sollte — wörtlich: *"foreach_batch_sink code should properly handle a full refresh for downstream data sources."*

---

## <a id="quellen">5. Quellen</a>

- foreach_batch_sink (vollständige Signatur, Parametertabelle, Verhalten bei `batch_id == 0`): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-foreach-batch-sink

**Stand:** 2026-08-19.
