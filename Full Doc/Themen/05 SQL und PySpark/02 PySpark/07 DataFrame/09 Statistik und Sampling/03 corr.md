# `DataFrame.corr()`

Berechnet die Korrelation zweier Spalten eines DataFrames als Double-Wert. Aktuell wird nur der Pearson-Korrelationskoeffizient unterstützt. `DataFrame.corr` und `DataFrameStatFunctions.corr` sind Aliase voneinander.

## Signatur

```python
corr(col1: str, col2: str, method: Optional[str] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `col1` | `str` | Name der ersten Spalte. |
| `col2` | `str` | Name der zweiten Spalte. |
| `method` | `str`, optional | Die Korrelationsmethode. Aktuell wird nur `"pearson"` unterstützt. |

## Rückgabewert

`float`: Pearson-Korrelationskoeffizient der beiden Spalten.

## Beispiel

```python
df = spark.createDataFrame([(1, 12), (10, 1), (19, 8)], ["c1", "c2"])
df.corr("c1", "c2")
# -0.3592106040535498
df = spark.createDataFrame([(11, 12), (10, 11), (9, 10)], ["small", "bigger"])
df.corr("small", "bigger")
# 1.0
```

## Quellen

- DataFrame.corr: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/corr

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
