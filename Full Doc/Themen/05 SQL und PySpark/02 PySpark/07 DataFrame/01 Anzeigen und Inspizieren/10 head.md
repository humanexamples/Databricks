# `DataFrame.head()`

Gibt die ersten `n` Zeilen zurück.

## Signatur

```python
head(n: Optional[int] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `n` | `int`, optional | Standard 1. Anzahl der zurückzugebenden Zeilen. |

## Rückgabewert

Wird `n` angegeben: Liste von `Row` der Länge `n` (oder kürzer, wenn der DataFrame weniger Zeilen hat). Ohne `n`: eine einzelne `Row`.

## Hinweise

Diese Methode sollte nur verwendet werden, wenn das Ergebnis voraussichtlich klein ist, da alle Daten in den Speicher des Drivers geladen werden.

## Beispiel

```python
df = spark.createDataFrame([
    (2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.head()
# Row(age=2, name='Alice')
df.head(1)
# [Row(age=2, name='Alice')]
df.head(0)
# []
```

Siehe auch [`first`](11%20first.md), [`take`](09%20take.md), [`tail`](12%20tail.md).

## Quellen

- DataFrame.head: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/head

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
