# `DataFrame.repartitionById()`

Gibt einen neuen DataFrame zurück, der nach den angegebenen Partitionierungsausdrücken partitioniert ist. Der resultierende DataFrame wird anhand eines Spaltenbezeichners (Partitions-ID) partitioniert.

## Signatur

```python
repartitionById(numPartitions: int, *cols: "ColumnOrName")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `numPartitions` | `int` | Die Zielanzahl an Partitionen. |
| `cols` | `str` oder `Column` | Partitionierungsspalten. |

## Rückgabewert

`DataFrame`: Neu partitionierter DataFrame.

## Hinweise

- Mindestens ein Partitionierungsausdruck muss angegeben werden. Die Verteilung ähnelt [`repartition`](01%20repartition.md), die Reihenfolge der Zeilen innerhalb jeder Partition bleibt aber erhalten.
- Dies ist eine experimentelle API.

## Beispiel

```python
from pyspark.sql import functions as sf
spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob"), (18, "Alice"), (21, "Alice")],
    ["age", "name"]
).repartitionById(2, "name").select(
    "age", "name", sf.spark_partition_id()
).show()
# +---+-----+--------------------+
# |age| name|SPARK_PARTITION_ID()|
# +---+-----+--------------------+
# | 14|  Tom|                   0|
# | 23|Alice|                   1|
# | 18|Alice|                   1|
# | 21|Alice|                   1|
# | 16|  Bob|                   0|
# +---+-----+--------------------+
```

## Quellen

- DataFrame.repartitionById: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/repartitionById

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
