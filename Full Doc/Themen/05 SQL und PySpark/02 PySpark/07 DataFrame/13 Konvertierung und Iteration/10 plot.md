# `DataFrame.plot` (Eigenschaft)

Gibt einen `PySparkPlotAccessor` für Plot-Funktionen zurück.

Plots lassen sich auf zwei Arten erstellen:

- Verkettungsstil: `df.plot.line(...)`
- Expliziter Stil: `df.plot(kind="line", ...)`

## Rückgabewert

`plot.core.PySparkPlotAccessor`

## Beispiel

```python
data = [("A", 10, 1.5), ("B", 30, 2.5), ("C", 20, 3.5)]
columns = ["category", "int_val", "float_val"]
df = spark.createDataFrame(data, columns)
type(df.plot)
# <class 'pyspark.sql.plot.core.PySparkPlotAccessor'>
df.plot.line(x="category", y=["int_val", "float_val"])
df.plot(kind="line", x="category", y=["int_val", "float_val"])
```

## Quellen

- DataFrame.plot: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/plot

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
