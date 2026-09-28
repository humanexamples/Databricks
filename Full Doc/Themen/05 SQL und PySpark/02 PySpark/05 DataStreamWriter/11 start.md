# `DataStreamWriter.start()`

Streamt den Inhalt des DataFrames in eine Datenquelle/-senke und gibt ein `StreamingQuery`-Objekt zurück.

## Signatur

```python
start(path=None, format=None, outputMode=None, partitionBy=None, queryName=None, **options)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str`, optional | Pfad in einem Hadoop-kompatiblen Dateisystem. |
| `format` | `str`, optional | Format, in dem gespeichert wird. |
| `outputMode` | `str`, optional | Wie Daten in die Senke geschrieben werden: `append`, `complete` oder `update`. |
| `partitionBy` | `str` oder `list`, optional | Namen der Partitionierungsspalten. |
| `queryName` | `str`, optional | Eindeutiger Name für die Query. |
| `**options` | — | Weitere String-Optionen; für die meisten Streams wird `checkpointLocation` empfohlen. |

## Rückgabewert

`StreamingQuery`

## Beispiele

### Grundlegende Nutzung

```python
df = spark.readStream.format("rate").load()
q = df.writeStream.format('memory').queryName('this_query').start()
q.isActive  # True
q.name      # 'this_query'
q.stop()
q.isActive  # False
```

### Mit Trigger und Parametern

```python
q = df.writeStream.trigger(processingTime='5 seconds').start(
    queryName='that_query', outputMode="append", format='memory')
q.name      # 'that_query'
q.isActive  # True
q.stop()
```

## Quellen

- DataStreamWriter.start: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/start

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
