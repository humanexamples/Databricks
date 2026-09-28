# `create_streaming_table` — Python-Referenz

## Abschnittsübersicht

1. [Zweck](#zweck)
2. [Vollständige Signatur](#signatur)
3. [Parameter](#parameter)
4. [Codebeispiel](#beispiel)
5. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck</a>

`create_streaming_table()` legt in einer Pipeline eine Zieltabelle für Streaming-Operationen an — wörtlich: *"Use the `create_streaming_table()` function in a pipeline to create a target table"* für die Ausgabe von Streaming-Operationen. Typischerweise wird die so erzeugte Tabelle anschließend als `target` für `create_auto_cdc_flow()`, `create_auto_cdc_from_snapshot_flow()`, `append_flow` oder `replace_flow` verwendet (siehe [apply_changes.md](apply_changes.md), [apply_changes_from_snapshot.md](apply_changes_from_snapshot.md)).

---

## <a id="signatur">2. Vollständige Signatur</a>

```python
from pyspark import pipelines as dp

dp.create_streaming_table(
  name = "<table-name>",
  comment = "<comment>",
  spark_conf={"<key>" : "<value", "<key" : "<value>"},
  table_properties={"<key>" : "<value>", "<key>" : "<value>"},
  path="<storage-location-path>",
  partition_cols=["<partition-column>", "<partition-column>"],
  cluster_by_auto = False,
  cluster_by = ["<clustering-column>", "<clustering-column>"],
  schema="schema-definition",
  expect_all = {"<key>" : "<value", "<key" : "<value>"},
  expect_all_or_drop = {"<key>" : "<value", "<key" : "<value>"},
  expect_all_or_fail = {"<key>" : "<value", "<key" : "<value>"},
  row_filter = "row-filter-clause")
```

---

## <a id="parameter">3. Parameter</a>

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| `name` | `str` | — | Erforderlich. Der Tabellenname. |
| `comment` | `str` | — | Eine Beschreibung für die Tabelle. |
| `spark_conf` | `dict` | — | Eine Liste von Spark-Konfigurationen für die Ausführung dieser Abfrage. |
| `table_properties` | `dict` | — | Ein `dict` mit Tabelleneigenschaften für die Tabelle. |
| `path` | `str` | Verwaltete Speicherposition des Schemas | Eine Speicherposition für Tabellendaten. Falls nicht gesetzt, wird die verwaltete Speicherposition des die Tabelle enthaltenden Schemas verwendet. |
| `partition_cols` | `list` | — | Eine Liste von einer oder mehreren Spalten zur Partitionierung der Tabelle. |
| `cluster_by_auto` | `bool` | — | Aktiviert automatisches Liquid Clustering für die Tabelle. |
| `cluster_by` | `list` | — | Aktiviert Liquid Clustering für die Tabelle und definiert die als Clustering-Schlüssel zu verwendenden Spalten. |
| `schema` | `str` oder `StructType` | — | Eine Schema-Definition für die Tabelle. Schemas lassen sich als SQL-DDL-String oder mit einem Python-`StructType` definieren. |
| `expect_all` | `dict` | — | Datenqualitäts-Constraints für die Tabelle (Variante "einbeziehen", siehe [expectations.md](expectations.md)). |
| `expect_all_or_drop` | `dict` | — | Datenqualitäts-Constraints für die Tabelle (Variante "verwerfen bei Verstoß"). |
| `expect_all_or_fail` | `dict` | — | Datenqualitäts-Constraints für die Tabelle (Variante "Abbruch bei Verstoß"). |
| `row_filter` | `str` | — | (Public Preview) Eine Row-Filter-Klausel für die Tabelle. |

---

## <a id="beispiel">4. Codebeispiel</a>

Verwendung als Zieltabelle für `create_auto_cdc_from_snapshot_flow()` (identisches Muster wie in `_fileIngestionScenarios.md` dieses Projekts):

```python
from pyspark import pipelines as dp

dp.create_streaming_table("target")
dp.create_auto_cdc_from_snapshot_flow(
  target = "target",
  source = "source",
  keys = ["log_id"],
  stored_as_scd_type = 1)
```

---

## <a id="quellen">5. Quellen</a>

- create_streaming_table (vollständige Signatur, Parametertabelle, Verwendungszweck): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-streaming-table

**Stand:** 2026-08-19.
