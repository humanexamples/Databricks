# `DataStreamWriter.options()`

Fügt der zugrunde liegenden Datenquelle (Senke) mehrere Ausgabeoptionen auf einmal hinzu.

## Signatur

```python
options(**options)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `**options` | `dict` | Schlüssel-Wert-Paare von Optionen. |

Für die vollständige Liste siehe die [Stream-Write-Optionen](https://docs.databricks.com/aws/en/spark/api-options#stream-write-options).

## Rückgabewert

`DataStreamWriter`

## Verfügbare Optionen

Die [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options) führt keinen eigenen Abschnitt „DataStreamWriter options"/„Stream write options" — Streaming-Schreib-Optionen sind in der Structured-Streaming-Doku bzw. den `DataFrameWriter`-Formatabschnitten beschrieben (dort ausdrücklich als „für Batch- und Streaming-Appends" gültig markiert):

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `checkpointLocation` | *(erforderlich)* | Pfad (z. B. Unity-Catalog-Volume) | Verzeichnis für Offsets, Commits, State und Metadata der Query. Muss vor Query-Start gesetzt werden; **jede Query braucht ein eigenes** Verzeichnis. |
| `mergeSchema` | `None` | `true`/`false` | Schema Evolution beim Schreiben in eine Delta-Tabelle, auch für Streaming-Appends gültig. |
| `txnAppId` | `None` | String | Anwendungs-ID für idempotente `foreachBatch`-Writes, zusammen mit `txnVersion`. |
| `txnVersion` | `None` | monoton steigende Ganzzahl | Transaktionsversion für idempotente `foreachBatch`-Writes. |

```python
q = (df.writeStream
     .options(checkpointLocation="/Volumes/catalog/schema/volume/path", mergeSchema="true")
     .toTable("catalog.schema.table"))
```

Sink-spezifische Optionen (z. B. bei Kafka als Ziel: `kafka.bootstrap.servers`, `topic`) richten sich nach dem jeweiligen Format-/Connector, nicht nach dieser generischen Methode.

## Beispiele

### Mehrere Optionen setzen

```python
df = spark.readStream.format("rate").load()
df.writeStream.options(**{"k1": "v1", "k2": "v2"})
# <...streaming.readwriter.DataStreamWriter object ...>
```

### 3 Zeilen pro Batch ohne Kürzung ausgeben

```python
import time
q = spark.readStream.format(
    "rate").option("rowsPerSecond", 10).load().writeStream.format(
        "console").options(numRows=3, truncate=False).start()
time.sleep(3)
q.stop()
```

## Quellen

- DataStreamWriter.options: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/options

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
