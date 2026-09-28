# Dataset-Definitionsfunktionen

## Abschnittsübersicht

1. [Grundmuster](#grundmuster)
2. [Lesevorgänge am Funktionsanfang](#lesen)
3. [Verbotene Operationen](#verboten)
4. [Rückgabewert und Dekoratorwahl](#rueckgabe)
5. [Verkettung von Transformationen](#verkettung)
6. [Quellen](#quellen)

---

## <a id="grundmuster">1. Grundmuster</a>

Lakeflow-Pipelines definieren Datasets über Dekoratoren aus dem Modul `pyspark.pipelines` (als `dp` importiert), die auf eine Python-Funktion angewendet werden:

```python
from pyspark import pipelines as dp

@dp.table()
def function_name():
    return (<query>)
```

---

## <a id="lesen">2. Lesevorgänge am Funktionsanfang</a>

Funktionen, die Pipeline-Datasets definieren, beginnen typischerweise mit einer `spark.read`- oder `spark.readStream`-Operation — wörtlich: *"Functions used to define pipeline datasets typically begin with a `spark.read` or `spark.readStream` operation."* Beispiele hierfür:

- Batch-Lesevorgänge über `spark.read.table()` oder Dateipfade,
- Streaming-Lesevorgänge über `spark.readStream.table()` oder Cloud-Speicher,
- SQL-Abfragen über `spark.sql()`.

---

## <a id="verboten">3. Verbotene Operationen</a>

Die Doku betont, dass Funktionen keine "beliebige, mit dem Dataset in keinem Zusammenhang stehende Python-Logik, einschließlich Aufrufen an Drittanbieter-APIs" enthalten dürfen (*"arbitrary Python logic unrelated to the dataset, including calls to third-party APIs"*). Explizit untersagt sind unter anderem:

- `collect()`, `count()`, `toPandas()`
- `save()`, `saveAsTable()`, `start()`, `toTable()`

Zusätzlich dürfen Funktionen "niemals außerhalb der Funktion definierte DataFrames referenzieren" (*"never reference DataFrames defined outside the function"*), um unerwartetes Verhalten zu vermeiden.

---

## <a id="rueckgabe">4. Rückgabewert und Dekoratorwahl</a>

Funktionen müssen eine Spark-DataFrame zurückgeben. Die Wahl des Dekorators bestimmt dabei die Art des Ergebnisses: `@dp.table()` für Streaming-Ergebnisse, `@dp.materialized_view()` für Batch-Ergebnisse.

---

## <a id="verkettung">5. Verkettung von Transformationen</a>

Mehrere Transformationsschritte lassen sich entweder innerhalb einer einzigen Funktion verketten, oder Zwischenergebnisse werden als temporäre Sichten über `@dp.temporary_view()` definiert, um sie in nachgelagerten Definitionen wiederzuverwenden.

---

## <a id="quellen">6. Quellen</a>

- Author a dataset with a Python function (Grundmuster, Lese-Konventionen, verbotene Operationen, Rückgabewert-Regeln): https://docs.databricks.com/aws/en/ldp/developer/definition-function

**Stand:** 2026-08-19.
