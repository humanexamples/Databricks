# `DataFrame.stat` (Eigenschaft)

Gibt ein `DataFrameStatFunctions`-Objekt für Statistikfunktionen zurück (u. a. `approxQuantile`, `corr`, `cov`, `crosstab`, `freqItems`, `sampleBy`).

## Rückgabewert

`DataFrameStatFunctions`

## Beispiel

```python
import pyspark.sql.functions as f
df = spark.range(3).withColumn("c", f.expr("id + 1"))
type(df.stat)
# <class '...dataframe.DataFrameStatFunctions'>
df.stat.corr("id", "c")
# 1.0
```

Siehe auch [`approxQuantile`](02%20approxQuantile.md), [`corr`](03%20corr.md), [`cov`](04%20cov.md), [`crosstab`](05%20crosstab.md), [`freqItems`](06%20freqItems.md), [`sampleBy`](08%20sampleBy.md).

## Quellen

- DataFrame.stat: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/stat

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
