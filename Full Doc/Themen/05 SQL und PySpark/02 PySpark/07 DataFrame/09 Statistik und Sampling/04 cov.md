# `DataFrame.cov()`

Berechnet die Stichproben-Kovarianz der beiden per Namen angegebenen Spalten als Double-Wert. `DataFrame.cov` und `DataFrameStatFunctions.cov` sind Aliase.

## Signatur

```python
cov(col1: str, col2: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `col1` | `str` | Name der ersten Spalte. |
| `col2` | `str` | Name der zweiten Spalte. |

## Rückgabewert

`float`: Kovarianz der beiden Spalten.

## Beispiel

```python
df = spark.createDataFrame([(1, 12), (10, 1), (19, 8)], ["c1", "c2"])
df.cov("c1", "c2")
# -18.0
df = spark.createDataFrame([(11, 12), (10, 11), (9, 10)], ["small", "bigger"])
df.cov("small", "bigger")
# 1.0
```

## Quellen

- DataFrame.cov: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/cov

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
