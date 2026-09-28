# `DataFrame.withWatermark()`

Definiert ein Event-Time-Watermark für diesen DataFrame. Ein Watermark markiert einen Zeitpunkt, vor dem angenommen wird, dass keine verspäteten Daten mehr eintreffen.

## Signatur

```python
withWatermark(eventTime: str, delayThreshold: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `eventTime` | `str` | Name der Spalte, die die Event-Time der Zeile enthält. |
| `delayThreshold` | `str` | Minimale Wartezeit auf verspätete Daten, relativ zum zuletzt verarbeiteten Datensatz, als Intervall (z. B. `"1 minute"` oder `"5 hours"`). |

## Rückgabewert

`DataFrame`: DataFrame mit Watermark.

## Hinweise

Diese Funktion ist nur für Structured Streaming relevant.

Spark verwendet das Watermark für mehrere Zwecke:

- Um zu erkennen, wann eine Aggregation über ein Zeitfenster abgeschlossen werden und damit bei Output-Modes, die keine Updates erlauben, ausgegeben werden kann.
- Um die Menge an State zu minimieren, die für laufende Aggregationen gehalten werden muss.

Das aktuelle Watermark ergibt sich aus dem über alle Partitionen der Query gesehenen `MAX(eventTime)` abzüglich des benutzerdefinierten `delayThreshold`. Wegen der Kosten, diesen Wert über Partitionen hinweg zu koordinieren, ist nur garantiert, dass das tatsächlich verwendete Watermark mindestens `delayThreshold` hinter der tatsächlichen Event-Time liegt.

## Beispiel

```python
from pyspark.sql import Row
from pyspark.sql.functions import timestamp_seconds
df = spark.readStream.format("rate").load().selectExpr(
    "value % 5 AS value", "timestamp")
df.select("value", df.timestamp.alias("time")).withWatermark("time", '10 minutes')
# DataFrame[value: bigint, time: timestamp]
```

Siehe auch [`dropDuplicatesWithinWatermark`](../07%20Mengenoperationen%20und%20Deduplizierung/09%20dropDuplicatesWithinWatermark.md), [`writeStream`](04%20writeStream.md).

## Quellen

- DataFrame.withWatermark: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/withWatermark

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
