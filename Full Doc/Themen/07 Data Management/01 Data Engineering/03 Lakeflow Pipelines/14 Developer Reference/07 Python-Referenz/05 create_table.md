# `create_table` — Python-Referenz

## Abschnittsübersicht

1. [Zweck und Abgrenzung zu `@dp.table`](#zweck)
2. [Vollständige Signatur](#signatur)
3. [Parameter](#parameter)
4. [Codebeispiel](#beispiel)
5. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck und Abgrenzung zu `@dp.table`</a>

`create_table()` ist die funktionale, nicht-dekorator-basierte Variante zum Anlegen einer Tabelle — im Unterschied zum Dekorator `@dp.table()` (siehe [table.md](table.md)) wird hier keine Funktion dekoriert; die Tabelle wird direkt aufgerufen erzeugt und typischerweise anschließend über `@dp.append_flow(target=...)` mit Daten befüllt (siehe Beispiel unten und [append_flow.md](append_flow.md)).

---

## <a id="signatur">2. Vollständige Signatur</a>

```python
from pyspark import pipelines as dp

dp.create_table(
  name="<table-name>",
  comment="<comment>",
  spark_conf={"<key>": "<value>"},
  table_properties={"<key>": "<value>"},
  partition_cols=["<partition-column>"],
  path="<storage-location-path>",
  schema="schema-definition",
  expect_all={"<key>": "<value>"},
  expect_all_or_drop={"<key>": "<value>"},
  expect_all_or_fail={"<key>": "<value>"},
  cluster_by=["<clustering-column>"],
  cluster_by_auto=False,
  row_filter="row-filter-clause",
  private=False
)
```

---

## <a id="parameter">3. Parameter</a>

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| `name` | `str` | — | Erforderlich. Der Tabellenname. |
| `comment` | `str` | — | Eine Beschreibung für die Tabelle. |
| `spark_conf` | `dict` | — | Eine Liste von Spark-Konfigurationen für die Ausführung dieser Abfrage. |
| `table_properties` | `dict` | — | Ein `dict` mit Tabelleneigenschaften für die Tabelle. |
| `partition_cols` | `list` | — | Eine Liste von einer oder mehreren Spalten zur Partitionierung der Tabelle. |
| `path` | `str` | — | Eine Speicherposition für Tabellendaten. |
| `schema` | `str` oder `StructType` | — | Schemas lassen sich als SQL-DDL-String oder mit einem Python-`StructType` definieren. |
| `expect_all` | `dict` | — | Datenqualitäts-Constraints für die Tabelle. |
| `expect_all_or_drop` | `dict` | — | Datenqualitäts-Constraints für die Tabelle (Variante "verwerfen"). |
| `expect_all_or_fail` | `dict` | — | Datenqualitäts-Constraints für die Tabelle (Variante "Abbruch"). |
| `cluster_by` | `list` | — | Aktiviert Liquid Clustering für die Tabelle und definiert die Clustering-Spalten. |
| `cluster_by_auto` | `bool` | `False` | Aktiviert automatisches Liquid Clustering für die Tabelle. |
| `row_filter` | `str` | — | (Public Preview) Eine Row-Filter-Klausel für die Tabelle. |
| `private` | `bool` | `False` | Bei `True` wird eine private Tabelle angelegt, die nicht im Katalog veröffentlicht wird. |

---

## <a id="beispiel">4. Codebeispiel</a>

Eine per `create_table()` angelegte Tabelle wird über zwei separate Append-Flows aus zwei Quellen befüllt:

```python
from pyspark import pipelines as dp

dp.create_table("combined")

@dp.append_flow(target="combined")
def from_a():
    return spark.readStream.table("source_a")

@dp.append_flow(target="combined")
def from_b():
    return spark.readStream.table("source_b")
```

---

## <a id="quellen">5. Quellen</a>

- create_table (vollständige Signatur, Parametertabelle inkl. `private`-Parameter, Codebeispiel mit zwei Append-Flows): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-create-table

**Stand:** 2026-08-19.
