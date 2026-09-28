# `@dp.table` — Python-Referenz

## Abschnittsübersicht

1. [Zweck](#zweck)
2. [Vollständige Signatur](#signatur)
3. [Parameter](#parameter)
4. [Integrierte `replace_using`/`sequence_by`-Parameter](#replace-using)
5. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck</a>

Der `@table`-Dekorator dient zur Definition von Streaming-Tabellen in einer Pipeline — wörtlich: *"The `@table` decorator can be used to define streaming tables in a pipeline."* Er funktioniert mit Abfragen, die Streaming-Lesevorgänge gegen Datenquellen ausführen.

---

## <a id="signatur">2. Vollständige Signatur</a>

Die Signatur wurde per WebFetch zweifach unabhängig abgerufen und dabei identisch bestätigt:

```python
from pyspark import pipelines as dp

@dp.table(
  name="<name>",
  comment="<comment>",
  spark_conf={"<key>" : "<value>", "<key>" : "<value>"},
  table_properties={"<key>" : "<value>", "<key>" : "<value>"},
  path="<storage-location-path>",
  partition_cols=["<partition-column>", "<partition-column>"],
  cluster_by_auto = False,
  cluster_by = ["<clustering-column>", "<clustering-column>"],
  schema="schema-definition",
  row_filter = "row-filter-clause",
  private = False,
  replace_using = ["<key-column>", "<key-column>"],
  sequence_by = "<sequence-column>")
@dp.expect(...)
def <function-name>():
    return (<query>)
```

---

## <a id="parameter">3. Parameter</a>

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| *(Funktion selbst)* | `function` | — | Erforderlich. Muss eine Apache-Spark-Streaming-DataFrame zurückgeben. |
| `name` | `str` | Funktionsname | Tabellenbezeichner; wenn nicht angegeben, standardmäßig der Funktionsname. |
| `comment` | `str` | — | Dokumentationstext für die Tabelle. |
| `spark_conf` | `dict` | — | Spark-Konfigurationseinstellungen für die Ausführung der Abfrage. |
| `table_properties` | `dict` | — | Delta-Lake-Tabelleneigenschaften-Zuordnungen. |
| `path` | `str` | Verwaltete Speicherposition | Speicherposition; verwendet die verwaltete Speicherposition, wenn nicht angegeben. |
| `partition_cols` | `list` | — | Spaltennamen zur Datenpartitionierung. |
| `cluster_by_auto` | `bool` | — | Aktiviert automatisches Liquid Clustering (Databricks wählt die Schlüssel selbst). |
| `cluster_by` | `list` | — | Explizite Clustering-Spalten-Bezeichner. |
| `schema` | `str` oder `StructType` | — | Strukturdefinition als SQL-DDL oder Python-Objekt. |
| `row_filter` | `str` | — | Row-Level-Zugriffsfilter-Ausdruck. |
| `private` | `bool` | — | Verbirgt die Tabelle vor dem Metastore; nur innerhalb der Pipeline zugänglich. |
| `replace_using` | `list` | — | Schlüsselspalten für REPLACE-USING-Flows (erfordert `sequence_by`). |
| `sequence_by` | `str` oder `Column` | — | Ordnungsspalte für Updates bei REPLACE-USING-Flows. |

---

## <a id="replace-using">4. Integrierte `replace_using`/`sequence_by`-Parameter</a>

Bemerkenswert: Die Referenzseite für den `@table`-Dekorator selbst listet — zusätzlich zu den Standard-Tabellenparametern — auch `replace_using` und `sequence_by` als Parameter, also dieselben Parameter, die auch bei `@dp.replace_flow` (siehe [replace_flow.md](replace_flow.md)) auftreten. Das deutet darauf hin, dass sich REPLACE-USING-Semantik direkt über `@dp.table(replace_using=..., sequence_by=...)` aktivieren lässt, ohne separaten `@dp.replace_flow`-Dekorator.

**Ungeklärt:** Ob `@dp.table(replace_using=..., sequence_by=...)` funktional vollständig äquivalent zu einem separaten `@dp.replace_flow`-Aufruf ist, oder ob es Unterschiede im Verhalten gibt (z. B. bezüglich mehrerer Flows in dieselbe Zieltabelle) — die geprüfte Referenzseite liefert dazu keinen erläuternden Beispielcode, nur die reine Signatur.

---

## <a id="quellen">5. Quellen</a>

- table (vollständige Signatur — zweifach per WebFetch abgerufen und identisch bestätigt —, Parametertabelle inkl. `replace_using`/`sequence_by`): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-table

**Stand:** 2026-08-19.
