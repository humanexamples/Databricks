# `DataFrame.sampleBy()`

Gibt eine geschichtete Stichprobe ohne Zurücklegen zurück, basierend auf dem für jede Schicht (Stratum) angegebenen Anteil.

## Signatur

```python
sampleBy(col: "ColumnOrName", fractions: Dict[Any, float], seed: Optional[int] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `col` | `Column` oder `str` | Spalte, die die Schichten definiert. |
| `fractions` | `dict` | Sampling-Anteil je Schicht. Ist eine Schicht nicht angegeben, wird ihr Anteil als 0 behandelt. |
| `seed` | `int`, optional | Zufalls-Seed. |

## Rückgabewert

Ein neuer DataFrame, der die geschichtete Stichprobe darstellt.

## Beispiel

```python
from pyspark.sql import functions as sf
dataset = spark.range(0, 100, 1, 5).select((sf.col("id") % 3).alias("key"))
sampled = dataset.sampleBy("key", fractions={0: 0.1, 1: 0.2}, seed=0)
sampled.groupBy("key").count().orderBy("key").show()
# +---+-----+
# |key|count|
# +---+-----+
# |  0|    4|
# |  1|    9|
# +---+-----+

dataset.sampleBy(sf.col("key"), fractions={2: 1.0}, seed=0).count()
# 33
```

## Quellen

- DataFrame.sampleBy: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/sampleBy

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
