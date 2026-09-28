# `DataFrame.repartitionByRange()`

Gibt einen neuen DataFrame zurück, der nach den angegebenen Partitionierungsausdrücken partitioniert ist. Der resultierende DataFrame ist range-partitioniert.

## Signatur

```python
repartitionByRange(numPartitions: Union[int, "ColumnOrName"], *cols: "ColumnOrName")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `numPartitions` | `int` | Ein `int` für die Zielanzahl an Partitionen oder eine `Column`. Ist es eine `Column`, wird sie als erste Partitionierungsspalte verwendet. Ohne Angabe wird die Standardanzahl an Partitionen verwendet. |
| `cols` | `str` oder `Column` | Partitionierungsspalten. |

## Rückgabewert

`DataFrame`: Neu partitionierter DataFrame.

## Hinweise

- Mindestens ein Partitionierungsausdruck muss angegeben werden. Ohne explizite Sortierreihenfolge wird „ascending nulls first“ angenommen.
- Aus Performancegründen schätzt die Methode die Bereiche per Sampling. Das Ergebnis ist daher nicht zwingend konsistent, da das Sampling unterschiedliche Werte liefern kann. Die Stichprobengröße lässt sich über die Konfiguration `spark.sql.execution.rangeExchange.sampleSizePerPartition` steuern.

## Beispiel

```python
from pyspark.sql import functions as sf
spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"]
).repartitionByRange(2, "age").select(
    "age", "name", sf.spark_partition_id()
).show()
# +---+-----+--------------------+
# |age| name|SPARK_PARTITION_ID()|
# +---+-----+--------------------+
# | 14|  Tom|                   0|
# | 16|  Bob|                   0|
# | 23|Alice|                   1|
# +---+-----+--------------------+
```

## Quellen

- DataFrame.repartitionByRange: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/repartitionByRange

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
