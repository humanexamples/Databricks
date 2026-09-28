# `DataFrame.foreachPartition()`

Wendet die Funktion `f` auf jede Partition dieses DataFrames an.

## Signatur

```python
foreachPartition(f: Callable[[Iterator[Row]], None])
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `f` | Funktion | Funktion mit einem Parameter, die jede zu verarbeitende Partition (als Iterator von `Row`) erhält. |

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
def func(itr):
    for person in itr:
        print(person.name)

df.foreachPartition(func)
```

Siehe auch [`foreach`](08%20foreach.md).

## Quellen

- DataFrame.foreachPartition: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/foreachPartition

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
