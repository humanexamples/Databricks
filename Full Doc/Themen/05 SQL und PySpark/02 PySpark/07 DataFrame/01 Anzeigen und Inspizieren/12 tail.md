# `DataFrame.tail()`

Gibt die letzten `num` Zeilen als Liste von `Row` zurück.

## Signatur

```python
tail(num: int)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `num` | `int` | Anzahl der zurückzugebenden Datensätze. Es werden genau so viele Datensätze zurückgegeben – oder alle, falls der DataFrame weniger enthält. |

## Rückgabewert

`list`: Liste von Zeilen.

## Hinweise

`tail` verschiebt Daten in den Driver-Prozess der Anwendung; ein sehr großes `num` kann den Driver mit einem `OutOfMemoryError` zum Absturz bringen.

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])

df.tail(2)
# [Row(age=23, name='Alice'), Row(age=16, name='Bob')]
```

Siehe auch [`take`](09%20take.md), [`head`](10%20head.md).

## Quellen

- DataFrame.tail: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/tail

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
