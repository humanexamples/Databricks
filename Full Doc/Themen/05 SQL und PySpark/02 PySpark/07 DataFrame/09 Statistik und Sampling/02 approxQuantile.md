# `DataFrame.approxQuantile()`

Berechnet die approximativen Quantile numerischer Spalten eines DataFrames.

## Signatur

```python
approxQuantile(col: Union[str, List[str], Tuple[str]], probabilities: Union[List[float], Tuple[float]], relativeError: float)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `col` | `str`, `tuple` oder `list` | Ein einzelner Spaltenname oder eine Liste von Namen für mehrere Spalten. |
| `probabilities` | `list` oder `tuple` aus `float` | Liste von Quantil-Wahrscheinlichkeiten. Jeder Wert muss ein Float im Bereich [0, 1] sein. Beispiel: 0.0 ist das Minimum, 0.5 der Median, 1.0 das Maximum. |
| `relativeError` | `float` | Die angestrebte relative Genauigkeit (>= 0). Bei 0 werden die exakten Quantile berechnet, was sehr teuer sein kann. Werte größer als 1 werden akzeptiert, liefern aber dasselbe Ergebnis wie 1. |

## Rückgabewert

`list`: Die approximativen Quantile zu den angegebenen Wahrscheinlichkeiten. Ist `col` ein String, ist das Ergebnis eine Liste von Floats. Ist `col` eine Liste oder ein Tupel von Strings, ist das Ergebnis ebenfalls eine Liste, deren Elemente jeweils Listen von Floats sind.

## Hinweise

NULL-Werte in numerischen Spalten werden vor der Berechnung ignoriert. Für Spalten, die nur NULL-Werte enthalten, wird eine leere Liste zurückgegeben.

## Beispiel

```python
data = [(1,), (2,), (3,), (4,), (5,)]
df = spark.createDataFrame(data, ["values"])
quantiles = df.approxQuantile("values", [0.0, 0.5, 1.0], 0.05)
quantiles
# [1.0, 3.0, 5.0]

data = [(1, 10), (2, 20), (3, 30), (4, 40), (5, 50)]
df = spark.createDataFrame(data, ["col1", "col2"])
quantiles = df.approxQuantile(["col1", "col2"], [0.0, 0.5, 1.0], 0.05)
quantiles
# [[1.0, 3.0, 5.0], [10.0, 30.0, 50.0]]
```

## Quellen

- DataFrame.approxQuantile: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/approxQuantile

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
