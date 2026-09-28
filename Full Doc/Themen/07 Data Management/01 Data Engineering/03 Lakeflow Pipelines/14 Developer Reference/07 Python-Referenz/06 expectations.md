# Expectations — Python-Referenz

## Abschnittsübersicht

1. [Zweck](#zweck)
2. [Die sechs Dekoratoren](#dekoratoren)
3. [Syntax](#syntax)
4. [Parameter](#parameter)
5. [Verhalten von `@dp.expect`](#verhalten)
6. [Kombinierbarkeit](#kombinierbarkeit)
7. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck</a>

Expectations sind Dekoratorfunktionen, die Datenqualitäts-Constraints auf Materialized Views, Streaming-Tabellen oder temporären Sichten in Lakeflow-Pipelines erzwingen.

---

## <a id="dekoratoren">2. Die sechs Dekoratoren</a>

Das `dp`-Modul stellt sechs Expectation-Dekoratoren bereit, die sich in zwei Dimensionen unterscheiden:

- **Aktion bei Verstoß:** Zeile einbeziehen, Zeile verwerfen, oder sofortiger Abbruch.
- **Anzahl der Expectations:** einzelner oder mehrere Constraints gleichzeitig.

| Dekorator | Aktion bei Verstoß | Anzahl Constraints |
|---|---|---|
| `@dp.expect()` | Zeile einbeziehen | Einzeln |
| `@dp.expect_or_drop()` | Zeile verwerfen | Einzeln |
| `@dp.expect_or_fail()` | Abbruch | Einzeln |
| `@dp.expect_all()` | Zeile einbeziehen | Mehrere |
| `@dp.expect_all_or_drop()` | Zeile verwerfen | Mehrere |
| `@dp.expect_all_or_fail()` | Abbruch | Mehrere |

---

## <a id="syntax">3. Syntax</a>

Expectation-Dekoratoren stehen nach `@dp.table()`, `@dp.materialized_view()` oder `@dp.temporary_view()` und vor der Dataset-Definitionsfunktion:

```python
from pyspark import pipelines as dp

@dp.table()
@dp.expect(description, constraint)
def <function-name>():
    return (<query>)
```

Vollständige Übersicht aller sechs Dekoratoren in derselben Positions-Syntax:

```python
from pyspark import pipelines as dp

@dp.table()
@dp.expect(description, constraint)
@dp.expect_or_drop(description, constraint)
@dp.expect_or_fail(description, constraint)
@dp.expect_all({description: constraint, ...})
@dp.expect_all_or_drop({description: constraint, ...})
@dp.expect_all_or_fail({description: constraint, ...})
def <function-name>():
    return (<query>)
```

Praxisbeispiel mit `@dp.expect_or_drop` (bereits mehrfach in diesem Projekt referenziert, u. a. in [Python-Entwicklung.md](../Python-Entwicklung.md)):

```python
from pyspark import pipelines as dp

@dp.table()
@dp.expect_or_drop("valid_date", "order_datetime IS NOT NULL AND length(order_datetime) > 0")
def orders_valid():
    return (spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/databricks-datasets/retail-org/sales_orders")
    )
```

---

## <a id="parameter">4. Parameter</a>

| Parameter | Typ | Beschreibung |
|---|---|---|
| `description` | `str` | Erforderlich. Identifiziert den Constraint; muss pro Dataset eindeutig sein. |
| `constraint` | `str` | Erforderlich. SQL-Bedingungsausdruck, der pro Datensatz ausgewertet wird; löst aus, wenn er `false` ergibt. |

Bei den `expect_all`-Varianten werden `description` und `constraint`-Paare stattdessen als `dict` übergeben (`{description: constraint, ...}`).

---

## <a id="verhalten">5. Verhalten von `@dp.expect`</a>

Für das einfache `@dp.expect` (ohne `_or_drop`/`_or_fail`) gilt laut Doku: Die Zeile wird in das Ziel-Dataset einbezogen, unabhängig vom Constraint-Ergebnis. Die Anzahl gültiger und ungültiger Datensätze wird zusammen mit anderen Dataset-Metriken protokolliert — wörtlich: *"Include the row in the target dataset. The count of valid and invalid records is logged alongside other dataset metrics."*

---

## <a id="kombinierbarkeit">6. Kombinierbarkeit</a>

Mehrere Expectation-Dekoratoren lassen sich auf ein Dataset anwenden: *"You can add multiple expectation decorators to your datasets."*

**Ungeklärt:** Die genauen Kompatibilitätsregeln zwischen gleichzeitig verwendeten `@dp.expect`- und `_or_drop`/`_or_fail`-Varianten auf demselben Dataset (z. B. ob sich die Aktionen bei mehreren gleichzeitig verletzten Constraints unterschiedlicher Varianten gegenseitig beeinflussen) werden auf der geprüften Referenzseite nicht explizit spezifiziert.

---

## <a id="quellen">7. Quellen</a>

- Expectations for pyspark.pipelines (Übersicht aller sechs Dekoratoren, Syntax, Parametertabelle, Verhalten von `@dp.expect`, Kombinierbarkeit): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-expectations
- Develop pipeline code with Python (Praxisbeispiel `@dp.expect_or_drop`, Cross-Referenz): https://docs.databricks.com/aws/en/ldp/developer/python-dev

**Stand:** 2026-08-19.
