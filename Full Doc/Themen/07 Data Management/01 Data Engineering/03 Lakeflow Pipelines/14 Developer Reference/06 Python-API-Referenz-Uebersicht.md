# Python-API-Referenz — Übersicht

## Abschnittsübersicht

1. [Modul-Import](#import)
2. [Verfügbare Funktionen und Dekoratoren](#funktionen)
3. [Vorgaben für den Funktionskörper](#vorgaben)
4. [Legacy-Modul `dlt`](#legacy)
5. [Quellen](#quellen)

---

## <a id="import">1. Modul-Import</a>

Die Python-Schnittstelle von Lakeflow-Pipelines ist im Modul `pyspark.pipelines` definiert, das als `dp` importiert wird — wörtlich: *"The Lakeflow pipelines Python interface is defined in the `pyspark.pipelines` module, imported as `dp`."*

```python
from pyspark import pipelines as dp
```

---

## <a id="funktionen">2. Verfügbare Funktionen und Dekoratoren</a>

Die API-Referenz listet folgende Funktionen/Dekoratoren (jeweils mit eigener Detailseite im Unterordner [`Python-Referenz/`](Python-Referenz/)):

| Funktion/Dekorator | Detailseite |
|---|---|
| `append_flow` | [append_flow.md](Python-Referenz/append_flow.md) |
| `create_auto_cdc_flow` | [apply_changes.md](Python-Referenz/apply_changes.md) |
| `create_auto_cdc_from_snapshot_flow` | [apply_changes_from_snapshot.md](Python-Referenz/apply_changes_from_snapshot.md) |
| `create_table` | [create_table.md](Python-Referenz/create_table.md) |
| `create_sink` | [sink.md](Python-Referenz/sink.md) |
| `create_streaming_table` | [streaming_table.md](Python-Referenz/streaming_table.md) |
| `Expectations` (`expect`/`expect_or_drop`/`expect_or_fail`/`expect_all`/`expect_all_or_drop`/`expect_all_or_fail`) | [expectations.md](Python-Referenz/expectations.md) |
| `foreach_batch_sink` | [foreach_batch_sink.md](Python-Referenz/foreach_batch_sink.md) |
| `materialized_view` | [materialized_view.md](Python-Referenz/materialized_view.md) |
| `replace_flow` | [replace_flow.md](Python-Referenz/replace_flow.md) |
| `table` | [table.md](Python-Referenz/table.md) |
| `temporary_view` | [view.md](Python-Referenz/view.md) |
| `update_flow` | [update_flow.md](Python-Referenz/update_flow.md) |

---

## <a id="vorgaben">3. Vorgaben für den Funktionskörper</a>

Die Doku betont, dass Entwickler "nur den zur Definition der Tabelle bzw. Sicht erforderlichen Code" einschließen sollen (*"should include only the code required to define the table or view"*) und untersagt innerhalb von Pipeline-Code insbesondere folgende Operationen:

- `collect()`, `count()`, `toPandas()`
- `save()`, `saveAsTable()`, `start()`, `toTable()`

(Details und Begründung siehe [Definition-Funktion.md](Definition-Funktion.md).)

---

## <a id="legacy">4. Legacy-Modul `dlt`</a>

Das ältere `dlt`-Modul wurde durch `pyspark.pipelines` abgelöst, bleibt aber weiterhin nutzbar. Databricks empfiehlt für aktuelle Entwicklungsarbeit den Umstieg auf den neueren `pyspark.pipelines`-Ansatz.

---

## <a id="quellen">5. Quellen</a>

- Lakeflow pipelines Python language reference (Modul-Import, Funktionsliste, Coding-Vorgaben, `dlt`-Legacy-Hinweis): https://docs.databricks.com/aws/en/ldp/developer/python-ref

**Stand:** 2026-08-19.
