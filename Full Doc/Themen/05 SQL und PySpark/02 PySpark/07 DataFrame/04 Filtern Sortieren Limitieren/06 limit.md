# `DataFrame.limit()`

Begrenzt die Anzahl der Ergebniszeilen auf die angegebene Zahl.

## Signatur

```python
limit(num: int)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `num` | `int` | Anzahl der zurückzugebenden Datensätze. Es werden genau so viele Datensätze zurückgegeben – oder alle, falls der DataFrame weniger enthält. |

## Rückgabewert

`DataFrame`: Teilmenge der Datensätze.

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df.limit(1).show()
# +---+----+
# |age|name|
# +---+----+
# | 14| Tom|
# +---+----+
df.limit(0).show()
# +---+----+
# |age|name|
# +---+----+
# +---+----+
```

Siehe auch [`offset`](07%20offset.md), [`take`](../01%20Anzeigen%20und%20Inspizieren/09%20take.md).

## Quellen

- DataFrame.limit: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/limit

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
