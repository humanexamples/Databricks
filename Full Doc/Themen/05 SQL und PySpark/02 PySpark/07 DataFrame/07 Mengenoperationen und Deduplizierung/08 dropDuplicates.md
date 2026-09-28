# `DataFrame.dropDuplicates()`

Gibt einen neuen DataFrame zurück, aus dem doppelte Zeilen entfernt wurden – optional nur unter Berücksichtigung bestimmter Spalten.

## Signatur

```python
dropDuplicates(subset: Optional[List[str]] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `subset` | Liste von Spaltennamen, optional | Spalten, die für den Duplikatvergleich herangezogen werden (Standard: alle Spalten). |

## Rückgabewert

`DataFrame`: DataFrame ohne Duplikate.

## Hinweise

Bei einem statischen Batch-DataFrame werden einfach doppelte Zeilen entfernt. Bei einem Streaming-DataFrame werden alle Daten über Trigger hinweg als Zwischenzustand (State) gehalten, um Duplikate zu entfernen. Mit [`withWatermark`](../14%20Schreiben%20und%20Streaming/06%20withWatermark.md) lässt sich begrenzen, wie spät doppelte Daten eintreffen dürfen; das System begrenzt den State entsprechend. Zusätzlich werden Daten, die älter als das Watermark sind, verworfen, um jede Möglichkeit von Duplikaten auszuschließen.

## Beispiel

```python
from pyspark.sql import Row
df = spark.createDataFrame([
    Row(name='Alice', age=5, height=80),
    Row(name='Alice', age=5, height=80),
    Row(name='Alice', age=10, height=80)
])

df.dropDuplicates().show()
# +-----+---+------+
# | name|age|height|
# +-----+---+------+
# |Alice|  5|    80|
# |Alice| 10|    80|
# +-----+---+------+

df.dropDuplicates(['name', 'height']).show()
# +-----+---+------+
# | name|age|height|
# +-----+---+------+
# |Alice|  5|    80|
# +-----+---+------+
```

Siehe auch [`distinct`](07%20distinct.md), [`dropDuplicatesWithinWatermark`](09%20dropDuplicatesWithinWatermark.md).

## Quellen

- DataFrame.dropDuplicates: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/dropDuplicates

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
