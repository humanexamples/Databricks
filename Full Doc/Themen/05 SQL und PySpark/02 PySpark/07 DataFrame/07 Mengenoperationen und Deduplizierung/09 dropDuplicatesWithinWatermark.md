# `DataFrame.dropDuplicatesWithinWatermark()`

Gibt einen neuen DataFrame zurück, aus dem doppelte Zeilen innerhalb des Watermarks entfernt wurden – optional nur unter Berücksichtigung bestimmter Spalten.

## Signatur

```python
dropDuplicatesWithinWatermark(subset: Optional[List[str]] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `subset` | Liste von Spaltennamen, optional | Spalten, die für den Duplikatvergleich herangezogen werden (Standard: alle Spalten). |

## Rückgabewert

`DataFrame`: DataFrame ohne Duplikate.

## Hinweise

- Funktioniert nur mit Streaming-DataFrames; das Watermark des Eingabe-DataFrames muss über [`withWatermark`](../14%20Schreiben%20und%20Streaming/06%20withWatermark.md) gesetzt sein.
- Bei einem Streaming-DataFrame werden alle Daten über Trigger hinweg als Zwischenzustand gehalten, um doppelte Zeilen zu entfernen. Der State wird gehalten, um folgende Semantik zu garantieren: *„Events werden dedupliziert, solange der zeitliche Abstand zwischen frühestem und spätestem Event kleiner ist als der Delay-Threshold des Watermarks.“* Es wird empfohlen, den Delay-Threshold des Watermarks größer zu wählen als die maximale Zeitstempel-Differenz zwischen doppelten Events.
- Zu späte Daten, die älter als das Watermark sind, werden verworfen.
- Unterstützt Spark Connect.

## Beispiel

```python
from pyspark.sql import Row
from pyspark.sql.functions import timestamp_seconds
df = spark.readStream.format("rate").load().selectExpr(
    "value % 5 AS value", "timestamp")
df.select("value", df.timestamp.alias("time")).withWatermark("time", '10 minutes')
# DataFrame[value: bigint, time: timestamp]

df.dropDuplicatesWithinWatermark()

df.dropDuplicatesWithinWatermark(['value'])
```

## Quellen

- DataFrame.dropDuplicatesWithinWatermark: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/dropDuplicatesWithinWatermark

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
