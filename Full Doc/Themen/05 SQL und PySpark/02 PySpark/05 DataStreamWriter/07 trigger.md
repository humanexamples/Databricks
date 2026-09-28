# `DataStreamWriter.trigger()`

Legt den Trigger (das Auslöse-Verhalten) der Streaming-Query fest. Ohne `trigger()` läuft die Query so schnell wie möglich – äquivalent zu `processingTime='0 seconds'`. Es darf immer nur **ein** Trigger-Parameter gesetzt werden.

## Signatur

```python
trigger(*, processingTime=None, once=None, continuous=None, availableNow=None, realTime=None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `processingTime` | `str`, optional | Intervall-String (z. B. `'5 seconds'`, `'1 minute'`). Führt die Micro-Batch-Query periodisch im angegebenen Abstand aus. |
| `once` | `bool`, optional | Bei `True` wird genau **eine** Batch verarbeitet, danach terminiert die Query. (Veraltet – stattdessen `availableNow=True`.) |
| `continuous` | `str`, optional | Intervall-String (z. B. `'5 seconds'`). Führt eine Continuous-Query mit dem angegebenen Checkpoint-Intervall aus. **Nicht** auf Databricks Serverless Compute unterstützt. |
| `availableNow` | `bool`, optional | Bei `True` werden **alle** aktuell verfügbaren Daten in mehreren Batches verarbeitet, danach terminiert die Query. |
| `realTime` | `str`, optional | Batch-Dauer-String (z. B. `'5 seconds'`). Führt die Query im Real-Time-Modus mit Batches der angegebenen Dauer aus. |

## Rückgabewert

`DataStreamWriter`

## Beispiele

### Micro-Batch periodisch

```python
df = spark.readStream.format("rate").load()
df.writeStream.trigger(processingTime='5 seconds')
```

### Continuous-Ausführung

```python
df.writeStream.trigger(continuous='5 seconds')
```

> Nicht auf Databricks Serverless Compute unterstützt.

### Alle verfügbaren Daten verarbeiten, dann stoppen

```python
df.writeStream.trigger(availableNow=True)
```

### Real-Time-Modus

```python
df.writeStream.trigger(realTime='5 seconds')
```

## Quellen

- DataStreamWriter.trigger: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/trigger

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
