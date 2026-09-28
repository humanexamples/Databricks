# `DataFrame.take()`

Gibt die ersten `num` Zeilen als Liste von `Row` zurück.

## Signatur

```python
take(num: int)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `num` | `int` | Anzahl der zurückzugebenden Datensätze. Es werden genau so viele Datensätze zurückgegeben – oder alle, falls der DataFrame weniger enthält. |

## Rückgabewert

`list`: Liste von Zeilen.

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])

df.take(2)
# [Row(age=14, name='Tom'), Row(age=23, name='Alice')]
```

Siehe auch [`head`](10%20head.md), [`tail`](12%20tail.md), [`collect`](08%20collect.md).

## Quellen

- DataFrame.take: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/take

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
