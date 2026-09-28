# `DataFrame.toLocalIterator()`

Gibt einen Iterator über alle Zeilen dieses DataFrames zurück. Der Iterator verbraucht so viel Speicher wie die größte Partition des DataFrames; mit Prefetch bis zum Speicher der zwei größten Partitionen.

## Signatur

```python
toLocalIterator(prefetchPartitions: bool = False)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `prefetchPartitions` | `bool`, optional | Ob Spark die nächste Partition vorab laden soll, bevor sie benötigt wird. |

## Rückgabewert

`Iterator`: Iterator über die Zeilen.

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
list(df.toLocalIterator())
# [Row(age=14, name='Tom'), Row(age=23, name='Alice'), Row(age=16, name='Bob')]
```

Siehe auch [`collect`](08%20collect.md).

## Quellen

- DataFrame.toLocalIterator: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/toLocalIterator

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
