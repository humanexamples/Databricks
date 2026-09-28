# `DataFrame.describe()`

Berechnet grundlegende Statistiken (count, mean, stddev, min, max) für numerische und String-Spalten.

## Signatur

```python
describe(*cols: Union[str, List[str]])
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `cols` | `str`, `list`, optional | Spaltenname oder Liste von Spaltennamen, die beschrieben werden sollen (Standard: alle Spalten). |

## Rückgabewert

`DataFrame`: Neuer DataFrame, der den gegebenen DataFrame beschreibt (Statistiken liefert).

## Hinweise

- Die Funktion ist für die explorative Datenanalyse gedacht; für die Rückwärtskompatibilität des Schemas des Ergebnis-DataFrames gibt es keine Garantie.
- Für erweiterte Statistiken und Kontrolle darüber, welche Statistiken berechnet werden, [`summary`](15%20summary.md) verwenden.

## Beispiel

```python
df = spark.createDataFrame(
    [("Bob", 13, 40.3, 150.5), ("Alice", 12, 37.8, 142.3), ("Tom", 11, 44.1, 142.2)],
    ["name", "age", "weight", "height"],
)
df.describe(['age']).show()
# +-------+----+
# |summary| age|
# +-------+----+
# |  count|   3|
# |   mean|12.0|
# | stddev| 1.0|
# |    min|  11|
# |    max|  13|
# +-------+----+

df.describe(['age', 'weight', 'height']).show()
# +-------+----+------------------+-----------------+
# |summary| age|            weight|           height|
# +-------+----+------------------+-----------------+
# |  count|   3|                 3|                3|
# |   mean|12.0| 40.73333333333333|            145.0|
# | stddev| 1.0|3.1722757341273704|4.763402145525822|
# |    min|  11|              37.8|            142.2|
# |    max|  13|              44.1|            150.5|
# +-------+----+------------------+-----------------+
```

## Quellen

- DataFrame.describe: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/describe

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
