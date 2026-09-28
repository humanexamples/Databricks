# `DataFrame.foreach()`

Wendet die Funktion `f` auf jede `Row` dieses DataFrames an.

## Signatur

```python
foreach(f: Callable[[Row], None])
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `f` | Funktion | Funktion mit einem Parameter, die jede zu verarbeitende Zeile erhält. |

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
def func(person):
    print(person.name)

df.foreach(func)
```

Siehe auch [`foreachPartition`](09%20foreachPartition.md).

## Quellen

- DataFrame.foreach: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/foreach

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
