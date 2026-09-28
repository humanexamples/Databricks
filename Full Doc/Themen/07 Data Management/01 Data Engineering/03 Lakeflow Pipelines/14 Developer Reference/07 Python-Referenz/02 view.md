# `@dp.temporary_view` — Python-Referenz

## Abschnittsübersicht

1. [Namensklärung: `temporary_view` statt `view`](#namensklaerung)
2. [Zweck](#zweck)
3. [Vollständige Signatur](#signatur)
4. [Parameter](#parameter)
5. [Rückgabetyp](#rueckgabe)
6. [Quellen](#quellen)

---

## <a id="namensklaerung">1. Namensklärung: `temporary_view` statt `view`</a>

Der offizielle Seitentitel der geprüften Referenzseite lautet *"temporary_view | Databricks on AWS"*. Ein Dekorator namens `@dp.view` wird auf dieser Seite **nicht** dokumentiert. Stattdessen erklärt die Doku ausdrücklich das Verhältnis zum älteren `dlt`-Modul: *"The older `dlt` module used the `@view` decorator to define a temporary view. Databricks recommends using the pyspark.pipelines module (imported as `dp`) and the `@temporary_view` decorator"* — das ältere `dlt`-Modul verwendete den `@view`-Dekorator zur Definition einer temporären Sicht; Databricks empfiehlt stattdessen das `pyspark.pipelines`-Modul (als `dp` importiert) mit dem `@temporary_view`-Dekorator.

**Cross-Referenz-Hinweis:** `_fileIngestionScenarios.md` (Ordner "Working with Files") verwendet in einem Codebeispiel `@dp.view(name="source")` — laut der hier geprüften Referenzseite ist `dp.view` (also `@view` im `pyspark.pipelines`-Modul) nicht als aktueller, dokumentierter Name belegt; die Doku dokumentiert nur `@view` als Namen des **alten** `dlt`-Moduls und `@temporary_view` als dessen Nachfolger im `dp`-Modul. Diese Diskrepanz wird hier benannt, nicht selbst behoben (siehe Abschlussbericht).

---

## <a id="zweck">2. Zweck</a>

Über den `@temporary_view`-Dekorator lassen sich Sichten definieren, die anschließend unter ihrem Namen in anderen Abfragen referenziert werden können — einschließlich Materialized Views und Streaming-Tabellen: *"Apply the `@temporary_view` decorator, then reference views by name in other queries, including materialized views and streaming tables."* Ergebnisse werden bei Abfrage berechnet.

---

## <a id="signatur">3. Vollständige Signatur</a>

```python
from pyspark import pipelines as dp

@dp.temporary_view(
    name="<name>",
    comment="<comment>"
)
@dp.expect(...)
def <function-name>():
    return (<query>)
```

---

## <a id="parameter">4. Parameter</a>

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| *(Funktion selbst)* | `function` | — | Erforderlich. Eine Funktion, die eine Apache-Spark-DataFrame oder Streaming-DataFrame zurückgibt. |
| `name` | `str` | Funktionsname | Sichtname; wenn nicht angegeben, standardmäßig der Funktionsname. Muss innerhalb von Katalog/Schema eindeutig sein. |
| `comment` | `str` | — | Eine Beschreibung für die Tabelle. |

---

## <a id="rueckgabe">5. Rückgabetyp</a>

Die dekorierte Funktion gibt je nach benutzerdefinierter Abfrage entweder eine Apache-Spark-DataFrame oder eine Streaming-DataFrame zurück.

---

## <a id="quellen">6. Quellen</a>

- temporary_view (Seitentitel, Namensklärung `view`/`dlt` vs. `temporary_view`/`dp`, vollständige Signatur, Parametertabelle, Rückgabetyp): https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-view
- Cross-Referenz-Quelle innerhalb dieses Projekts (verwendet `@dp.view(name="source")`): `Lakeflow Connect/Lakeflow Connect Standard Connectors/Working with Files/_fileIngestionScenarios.md`

**Stand:** 2026-08-19.
