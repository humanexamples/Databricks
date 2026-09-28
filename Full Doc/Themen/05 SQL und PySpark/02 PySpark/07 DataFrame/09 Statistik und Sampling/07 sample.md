# `DataFrame.sample()`

Gibt eine Stichprobe (Teilmenge) dieses DataFrames zurück.

## Signatur

```python
sample(withReplacement: Optional[Union[float, bool]] = None, fraction: Optional[Union[int, float]] = None, seed: Optional[int] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `withReplacement` | `bool`, optional | Stichprobe mit oder ohne Zurücklegen (Standard `False`). |
| `fraction` | `float`, optional | Anteil der zu erzeugenden Zeilen, Bereich [0.0, 1.0]. |
| `seed` | `int`, optional | Seed für das Sampling (Standard: zufälliger Seed). |

## Rückgabewert

`DataFrame`: Stichprobe der Zeilen des gegebenen DataFrames.

## Hinweise

- Es ist nicht garantiert, dass genau der angegebene Anteil der Gesamtzeilen geliefert wird.
- `fraction` ist erforderlich, `withReplacement` und `seed` sind optional.

## Beispiel

```python
df = spark.range(0, 10, 1, 1)
df.sample(0.5, 3).count()
# 7
df.sample(fraction=0.5, seed=3).count()
# 4
df.sample(withReplacement=True, fraction=0.5, seed=3).count()
# 2
df.sample(1.0).count()
# 10
df.sample(fraction=1.0).count()
# 10
df.sample(False, fraction=1.0).count()
# 10
```

Siehe auch [`sampleBy`](08%20sampleBy.md), [`randomSplit`](09%20randomSplit.md).

## Quellen

- DataFrame.sample: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/sample

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
