# `DataFrame.randomSplit()`

Teilt diesen DataFrame zufällig gemäß den angegebenen Gewichten auf.

## Signatur

```python
randomSplit(weights: List[float], seed: Optional[int] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `weights` | `list` | Liste von Doubles als Gewichte für die Aufteilung. Summieren sich die Gewichte nicht zu 1.0, werden sie normalisiert. |
| `seed` | `int`, optional | Seed für das Sampling. |

## Rückgabewert

`list`: Liste von DataFrames.

## Beispiel

```python
from pyspark.sql import Row
df = spark.createDataFrame([
    Row(age=10, height=80, name="Alice"),
    Row(age=5, height=None, name="Bob"),
    Row(age=None, height=None, name="Tom"),
    Row(age=None, height=None, name=None),
])

splits = df.randomSplit([1.0, 2.0], 24)
splits[0].count()
# 2
splits[1].count()
# 2
```

## Quellen

- DataFrame.randomSplit: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/randomSplit

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
