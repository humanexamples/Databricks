# `DataFrame.coalesce()`

Gibt einen neuen DataFrame zurück, der genau `numPartitions` Partitionen hat.

## Signatur

```python
coalesce(numPartitions: int)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `numPartitions` | `int` | Die Zielanzahl an Partitionen. |

## Rückgabewert

`DataFrame`

## Hinweise

- Ähnlich wie `coalesce` auf einem RDD führt diese Operation zu einer *narrow dependency*: Geht man z. B. von 1000 auf 100 Partitionen, gibt es keinen Shuffle – stattdessen übernimmt jede der 100 neuen Partitionen 10 der bisherigen. Wird eine größere Anzahl Partitionen angefordert, bleibt es bei der aktuellen Anzahl.
- Bei einem drastischen Coalesce, z. B. auf `numPartitions = 1`, kann die Berechnung auf weniger Knoten stattfinden als gewünscht (bei `numPartitions = 1` auf einem einzigen Knoten). Um das zu vermeiden, kann man [`repartition`](01%20repartition.md) aufrufen. Das fügt einen Shuffle-Schritt hinzu, bedeutet aber, dass die vorgelagerten Partitionen parallel ausgeführt werden (entsprechend der aktuellen Partitionierung).

## Beispiel

```python
from pyspark.sql import functions as sf
spark.range(0, 10, 1, 3).coalesce(1).select(
    sf.spark_partition_id().alias("partition")
).distinct().sort("partition").show()
# +---------+
# |partition|
# +---------+
# |        0|
# +---------+
```

## Quellen

- DataFrame.coalesce: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/coalesce

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
