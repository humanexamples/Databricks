# `DataFrame.explain()`

Gibt die (logischen und physischen) Pläne zu Debugging-Zwecken auf der Konsole aus.

## Signatur

```python
explain(extended: Optional[Union[bool, str]] = None, mode: Optional[str] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `extended` | `bool`, optional | Standard `False`. Bei `False` wird nur der physische Plan ausgegeben. Ist der Wert ein String und `mode` nicht angegeben, wirkt er so, als wäre `mode` gesetzt. |
| `mode` | `str`, optional | Ausgabeformat der Pläne: `simple` – nur physischer Plan; `extended` – logischer und physischer Plan; `codegen` – physischer Plan und generierter Code (falls verfügbar); `cost` – logischer Plan und Statistiken (falls verfügbar); `formatted` – Ausgabe in zwei Abschnitten: Übersicht des physischen Plans und Knotendetails. |

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df.explain()
# == Physical Plan ==
# *(1) Scan ExistingRDD[age...,name...]

df.explain(extended=True)
# == Parsed Logical Plan ==
# ...
# == Analyzed Logical Plan ==
# ...
# == Optimized Logical Plan ==
# ...
# == Physical Plan ==
# ...

df.explain(mode="formatted")
# == Physical Plan ==
# * Scan ExistingRDD (...)
# (1) Scan ExistingRDD [codegen id : ...]
# Output [2]: [age..., name...]
# ...
```

## Quellen

- DataFrame.explain: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/explain

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
