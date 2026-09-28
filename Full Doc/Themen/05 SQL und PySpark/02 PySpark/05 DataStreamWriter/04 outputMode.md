# `DataStreamWriter.outputMode()`

Legt fest, wie die Daten eines Streaming-DataFrames in die Streaming-Senke geschrieben werden.

## Signatur

```python
outputMode(outputMode)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `outputMode` | `str` | Ausgabeverhalten der Senke. Zulässige Werte: `'append'`, `'complete'`, `'update'`. |

### Bedeutung der Werte

| Wert | Verhalten |
| --- | --- |
| `append` | Nur **neue** Zeilen werden in die Senke geschrieben. |
| `complete` | Bei jedem Update wird das **gesamte** Ergebnis (alle Zeilen) geschrieben. Nur für Queries mit Aggregationen. |
| `update` | Nur bei diesem Update **geänderte** Zeilen werden geschrieben. Enthält die Query keine Aggregationen, entspricht das `append`. |

## Rückgabewert

`DataStreamWriter`

## Beispiele

### Append-Modus

```python
df = spark.readStream.format("rate").load()
df.writeStream.outputMode('append')
# <...streaming.readwriter.DataStreamWriter object ...>
```

### Complete-Modus mit Aggregation

```python
import time
df = spark.readStream.format("rate").option("rowsPerSecond", 10).load()
df = df.groupby().count()
q = df.writeStream.outputMode("complete").format("console").start()
time.sleep(3)
q.stop()
```

## Quellen

- DataStreamWriter.outputMode: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/outputMode

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
