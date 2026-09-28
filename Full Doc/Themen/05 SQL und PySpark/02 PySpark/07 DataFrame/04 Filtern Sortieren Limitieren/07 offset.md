# `DataFrame.offset()`

Gibt einen neuen DataFrame zurück, bei dem die ersten `n` Zeilen übersprungen werden.

*Hinzugefügt in Databricks Runtime 13.1*

## Signatur

```python
offset(num: int)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `num` | `int` | Anzahl der zu überspringenden Datensätze. |

## Rückgabewert

`DataFrame`: Teilmenge der Datensätze.

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df.offset(1).show()
# +---+-----+
# |age| name|
# +---+-----+
# | 23|Alice|
# | 16|  Bob|
# +---+-----+
df.offset(10).show()
# +---+----+
# |age|name|
# +---+----+
# +---+----+
```

Siehe auch [`limit`](06%20limit.md).

## Quellen

- DataFrame.offset: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/offset

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
