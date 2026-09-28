# `@dp.replace_flow` — Python-Referenz

## Abschnittsübersicht

1. [Zweck](#zweck)
2. [Vollständige Signatur](#signatur)
3. [Parameter](#parameter)
4. [Codebeispiele](#beispiele)
5. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck</a>

`@dp.replace_flow` ersetzt gezielt Zeilen einer bestehenden Streaming-Tabelle anhand von Schlüsselspalten, statt reine Anhänge (Appends) vorzunehmen — die dekorierte Funktion muss eine Apache-Spark-**Streaming**-DataFrame aus einer benutzerdefinierten Abfrage zurückgeben.

---

## <a id="signatur">2. Vollständige Signatur</a>

```python
@dp.replace_flow(
  target = "<target-table-name>",
  replace_using = ["<key-column>", "<key-column>"],
  sequence_by = "<sequence-column>",
  name = "<flow-name>",
  comment = "<comment>",
  spark_conf = {"<key>" : "<value>", "<key>" : "<value>"}
)
def <function-name>():
  return (<streaming-query>)
```

---

## <a id="parameter">3. Parameter</a>

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| *(Funktion selbst)* | `function` | — | Erforderlich. Gibt eine Apache-Spark-Streaming-DataFrame aus einer benutzerdefinierten Abfrage zurück. |
| `target` | `str` | — | Erforderlich. Name der Streaming-Tabelle, die die Updates erhält. |
| `replace_using` | `list` | — | Erforderlich. Schlüsselspalten, die die zu ersetzenden Zielzeilen identifizieren; mindestens eine Spalte erforderlich. |
| `sequence_by` | `str` oder `Column` | — | Erforderlich. Spalte zur Ordnung von Updates; pro Schlüssel gewinnt der höchste Sequenzwert. |
| `name` | `str` | Funktionsname | Flow-Name; wenn nicht angegeben, standardmäßig der Funktionsname. |
| `comment` | `str` | — | Beschreibung für den Flow. |
| `spark_conf` | `dict` | — | Spark-Konfigurationen für die Ausführung der Abfrage. |

---

## <a id="beispiele">4. Codebeispiele</a>

### Einzelne Schlüsselspalte

```python
from pyspark import pipelines as dp

dp.create_streaming_table("orders_current")
@dp.replace_flow(
  target = "orders_current",
  replace_using = ["order_id"],
  sequence_by = "updated_at")
def orders_flow():
  return spark.readStream.table("order_updates")
```

### Mehrere Schlüsselspalten

```python
dp.create_streaming_table("accounts_current")
@dp.replace_flow(
  target = "accounts_current",
  replace_using = ["region", "account_id"],
  sequence_by = "updated_at")
def accounts_flow():
  return spark.readStream.table("account_updates")
```

---

## <a id="quellen">5. Quellen</a>

- replace_flow (vollständige Signatur, Parametertabelle, beide Codebeispiele mit einzelner bzw. mehrfacher Schlüsselspalte): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-replace-flow

**Stand:** 2026-08-19.
