# `DataFrame.summary()`

Berechnet die angegebenen Statistiken für numerische und String-Spalten. Verfügbare Statistiken: `count`, `mean`, `stddev`, `min`, `max` sowie beliebige approximative Perzentile, angegeben als Prozentwert (z. B. `75%`).

## Signatur

```python
summary(*statistics: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `statistics` | `str`, optional | Die zu berechnenden Statistiken (ohne Angabe: count, mean, stddev, min, 25 %, 50 %, 75 %, max). *Die Referenz beschreibt den Parameter als „Column names to calculate statistics by (default All columns)“; tatsächlich werden hier Statistiknamen übergeben, wie das Beispiel zeigt.* |

## Rückgabewert

`DataFrame`: Neuer DataFrame mit Statistiken zum gegebenen DataFrame.

## Hinweise

Die Funktion ist für die explorative Datenanalyse gedacht; für die Rückwärtskompatibilität des Schemas des Ergebnis-DataFrames gibt es keine Garantie.

## Beispiel

```python
df = spark.createDataFrame(
    [("Bob", 13, 40.3, 150.5), ("Alice", 12, 37.8, 142.3), ("Tom", 11, 44.1, 142.2)],
    ["name", "age", "weight", "height"],
)
df.select("age", "weight", "height").summary().show()
# +-------+----+------------------+-----------------+
# |summary| age|            weight|           height|
# +-------+----+------------------+-----------------+
# |  count|   3|                 3|                3|
# |   mean|12.0| 40.73333333333333|            145.0|
# | stddev| 1.0|3.1722757341273704|4.763402145525822|
# |    min|  11|              37.8|            142.2|
# |    25%|  11|              37.8|            142.2|
# |    50%|  12|              40.3|            142.3|
# |    75%|  13|              44.1|            150.5|
# |    max|  13|              44.1|            150.5|
# +-------+----+------------------+-----------------+

df.select("age", "weight", "height").summary("count", "min", "25%", "75%", "max").show()
# +-------+---+------+------+
# |summary|age|weight|height|
# +-------+---+------+------+
# |  count|  3|     3|     3|
# |    min| 11|  37.8| 142.2|
# |    25%| 11|  37.8| 142.2|
# |    75%| 13|  44.1| 150.5|
# |    max| 13|  44.1| 150.5|
# +-------+---+------+------+
```

Siehe auch [`describe`](14%20describe.md).

## Quellen

- DataFrame.summary: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/summary

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
