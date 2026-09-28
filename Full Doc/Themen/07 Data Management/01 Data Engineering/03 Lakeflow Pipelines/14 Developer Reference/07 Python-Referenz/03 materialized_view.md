# `@dp.materialized_view` — Python-Referenz

## Abschnittsübersicht

1. [Zweck](#zweck)
2. [Vollständige Signatur](#signatur)
3. [Parameter](#parameter)
4. [Codebeispiel](#beispiel)
5. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck</a>

`@dp.materialized_view` definiert eine Materialized View über eine dekorierte Funktion, die eine Apache-Spark-**Batch**-DataFrame aus einer benutzerdefinierten Abfrage zurückgibt (typischerweise via `spark.read`, im Unterschied zu `@dp.table` mit `spark.readStream` — siehe [Python-Entwicklung.md](../Python-Entwicklung.md) Abschnitt 2).

---

## <a id="signatur">2. Vollständige Signatur</a>

```python
@dp.materialized_view(
    name="<name>",
    comment="<comment>",
    spark_conf = {"<key>" : "<value>", "<key>" : "<value>"},
    table_properties = {"<key>" : "<value>", "<key>" : "<value>"},
    path = "<storage-location-path>",
    partition_cols = ["<partition-column>", "<partition-column>"],
    cluster_by_auto = False,
    cluster_by = ["<clustering-column>", "<clustering-column>"],
    schema = "schema-definition",
    refresh_policy = None,
    row_filter = "row-filter-clause",
    private = False)
@dp.expect(...)
def <function-name>():
    return (<query>)
```

---

## <a id="parameter">3. Parameter</a>

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| *(Funktion selbst)* | `function` | — | Erforderlich. Eine Funktion, die eine Apache-Spark-Batch-DataFrame aus einer benutzerdefinierten Abfrage zurückgibt. |
| `name` | `str` | Funktionsname | Tabellenname; wenn nicht angegeben, standardmäßig der Funktionsname. |
| `comment` | `str` | — | Beschreibung der Tabelle. |
| `spark_conf` | `dict` | — | Spark-Konfigurationen für die Ausführung der Abfrage. |
| `table_properties` | `dict` | — | Dictionary mit Tabelleneigenschaften. |
| `path` | `str` | — | Speicherposition für Tabellendaten. |
| `partition_cols` | `list` | — | Spalten zur Tabellenpartitionierung. |
| `cluster_by_auto` | `bool` | `False` | Aktiviert automatisches Liquid Clustering. |
| `cluster_by` | `list` | — | Spalten für Liquid-Clustering-Schlüssel. |
| `schema` | `str` oder `StructType` | — | SQL-DDL-String oder Python-`StructType`-Schemadefinition. |
| `refresh_policy` | `str` | `"auto"` | Beta-Feature: `auto`, `incremental`, `incremental_strict` oder `full`. |
| `row_filter` | `str` | — | (Public Preview) Row-Filter-Klausel für Zugriffskontrolle auf Zeilenebene. |
| `private` | `bool` | `False` | Erstellt die Tabelle ohne Veröffentlichung im Metastore. |

---

## <a id="beispiel">4. Codebeispiel</a>

```python
from pyspark import pipelines as dp

@dp.materialized_view(
    comment="Raw data on sales",
    schema="""
        customer_id STRING,
        customer_name STRING,
        order_number LONG
    """,
    cluster_by = ["customer_id"])
def sales():
    return ("...")
```

---

## <a id="quellen">5. Quellen</a>

- materialized_view (vollständige Signatur, Parametertabelle inkl. `refresh_policy`-Beta-Feature, Codebeispiel): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-materialized-view

**Stand:** 2026-08-19.
