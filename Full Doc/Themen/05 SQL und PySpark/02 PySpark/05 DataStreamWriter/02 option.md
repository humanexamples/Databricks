# `DataStreamWriter.option()`

Fügt der zugrunde liegenden Datenquelle (Senke) eine einzelne Ausgabeoption hinzu.

## Signatur

```python
option(key, value)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `key` | `str` | Der Options-Schlüssel. |
| `value` | `str`, `int`, `float` oder `bool` | Der Options-Wert. |

Für die verfügbaren Optionen siehe die [Stream-Write-Optionen](https://docs.databricks.com/aws/en/spark/api-options#stream-write-options). Praktisch am wichtigsten ist `checkpointLocation`.

## Rückgabewert

`DataStreamWriter`

## Verfügbare Optionen

Die [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options) führt keinen eigenen Abschnitt „DataStreamWriter options" bzw. „Stream write options" — Streaming-Schreib-Optionen sind stattdessen in der Structured-Streaming-Doku bzw. in den `DataFrameWriter`-Formatabschnitten beschrieben (die laut Doku „für Batch- und Streaming-Appends" gelten).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `checkpointLocation` | *(erforderlich)* | Pfad (z. B. Unity-Catalog-Volume) | Verzeichnis, in dem die Query Offsets (verarbeiteter Fortschritt), Commits (für Exactly-once-Semantik), State (bei zustandsbehafteten Queries) und Metadata (eindeutige Query-ID) ablegt. Muss vor dem Start der Query gesetzt werden; **jede Query braucht ein eigenes** Checkpoint-Verzeichnis — mehrere Queries dürfen es sich nie teilen. |
| `mergeSchema` | `None` | `true`/`false` | Aktiviert Schema Evolution beim Schreiben in eine Delta-Tabelle — gilt laut Doku ausdrücklich auch für Streaming-Appends (siehe [13 DataFrameWriter — Delta Lake und Apache Iceberg.md](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/13%20DataFrameWriter%20%E2%80%94%20Delta%20Lake%20und%20Apache%20Iceberg.md)). |
| `txnAppId` | `None` | String | Eindeutige Anwendungs-ID für idempotente Schreibvorgänge **in `foreachBatch`** — zusammen mit `txnVersion`, um Exactly-once-Writes in mehrere Delta-Tabellen sicherzustellen. |
| `txnVersion` | `None` | monoton steigende Ganzzahl | Transaktionsversion für idempotente `foreachBatch`-Writes, zusammen mit `txnAppId`. |

```python
(df.writeStream
  .option("checkpointLocation", "/Volumes/catalog/schema/volume/path")
  .toTable("catalog.schema.table"))
```

Für Sink-spezifische Optionen (z. B. `kafka.bootstrap.servers`/`topic` bei Kafka als Ziel) gelten die jeweiligen Format-/Connector-Referenzen, nicht diese generische `option()`-Methode.

## Beispiele

### Option setzen

```python
df = spark.readStream.format("rate").load()
df.writeStream.option("x", 1)
# <...streaming.readwriter.DataStreamWriter object ...>
```

### 3 Zeilen pro Batch auf die Konsole ausgeben

```python
import time
q = spark.readStream.format(
    "rate").option("rowsPerSecond", 10).load().writeStream.format(
        "console").option("numRows", 3).start()
time.sleep(3)
q.stop()
```

## Quellen

- DataStreamWriter.option: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/option

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
