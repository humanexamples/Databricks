# `DataFrame.selectExpr()`

Projiziert eine Menge von SQL-Ausdrücken und gibt einen neuen DataFrame zurück.

## Signatur

```python
selectExpr(*expr: Union[str, List[str]])
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `expr` | `str` oder Liste von `str` | SQL-Ausdrucks-Strings, die projiziert werden. |

## Rückgabewert

`DataFrame`: DataFrame mit neuen/alten, durch Ausdrücke transformierten Spalten.

## Beispiel

```python
df = spark.createDataFrame([
    (2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.selectExpr("age * 2", "abs(age)").show()
# +---------+--------+
# |(age * 2)|abs(age)|
# +---------+--------+
# |        4|       2|
# |       10|       5|
# +---------+--------+
```

Siehe auch [`select`](01%20select.md).

## Quellen

- DataFrame.selectExpr: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/selectExpr

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
