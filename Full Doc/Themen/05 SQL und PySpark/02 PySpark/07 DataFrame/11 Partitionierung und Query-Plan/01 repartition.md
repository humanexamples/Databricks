# `DataFrame.repartition()`

Gibt einen neuen DataFrame zurück, der nach den angegebenen Partitionierungsausdrücken partitioniert ist. Der resultierende DataFrame ist hash-partitioniert.

## Signatur

```python
repartition(numPartitions: Union[int, "ColumnOrName"], *cols: "ColumnOrName")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `numPartitions` | `int` | Ein `int` für die Zielanzahl an Partitionen oder eine `Column`. Ist es eine `Column`, wird sie als erste Partitionierungsspalte verwendet. Ohne Angabe wird die Standardanzahl an Partitionen verwendet. |
| `cols` | `str` oder `Column` | Partitionierungsspalten. |

## Rückgabewert

`DataFrame`: Neu partitionierter DataFrame.

## Beispiel

```python
from pyspark.sql import functions as sf
df = spark.range(0, 64, 1, 9).withColumn(
    "name", sf.concat(sf.lit("name_"), sf.col("id").cast("string"))
).withColumn(
    "age", sf.col("id") - 32
)
df.repartition(10).select(
    sf.spark_partition_id().alias("partition")
).distinct().sort("partition").show()
# +---------+
# |partition|
# +---------+
# |        0|
# ...
# |        9|
# +---------+

df.repartition(7, "age").select(
    sf.spark_partition_id().alias("partition")
).distinct().sort("partition").show()
# +---------+
# |partition|
# +---------+
# |        0|
# ...
# |        6|
# +---------+
```

Siehe auch [`coalesce`](04%20coalesce.md), [`repartitionByRange`](02%20repartitionByRange.md), [`repartitionById`](03%20repartitionById.md).

## Quellen

- DataFrame.repartition: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/repartition

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
