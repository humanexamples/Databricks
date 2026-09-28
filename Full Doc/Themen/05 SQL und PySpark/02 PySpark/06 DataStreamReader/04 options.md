# `DataStreamReader.options()`

Fügt mehrere Eingabeoptionen auf einmal hinzu.

## Signatur

```python
options(**options)
```

## Beschreibung

*"Adds multiple input options for the underlying data source."*

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `**options` | `dict` | Schlüssel-Wert-Paare von Optionen. |

## Rückgabewert

`DataStreamReader`

## Verfügbare Optionen (Common)

Die folgenden Schlüssel gelten laut [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options) für die dateibasierte Streaming-Quelle (`spark.readStream.format("<file-format>")`), unabhängig von Auto Loader:

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `cleanSource` | `off` | enum (`off`, `archive`, `delete`) | „How to handle source files after they are processed by the stream." |
| `fileNameOnly` | `false` | boolean | „Whether to identify already-processed files by filename only rather than by full path." |
| `latestFirst` | `false` | boolean | „Whether to process the most recently modified files first within each micro-batch." |
| `maxBytesPerTrigger` | `None` | Ganzzahl | „Soft maximum for the amount of data processed for each micro-batch." |
| `maxCachedFiles` | `10000` | Ganzzahl | „Maximum number of unprocessed files to cache for subsequent micro-batches." |
| `maxFileAge` | `7d` | Dauer | „Maximum age of files considered for processing." |
| `maxFilesPerTrigger` | `1000` (Delta / Auto Loader); kein Maximum (andere Quellen) | Ganzzahl | „Upper bound for the number of new files processed in each micro-batch." |
| `sourceArchiveDir` | `None` | Pfad | „Path to the archive directory when `cleanSource` is set to `archive`." |

> Für **Auto Loader** (`format("cloudFiles")`) gelten stattdessen die `cloudFiles.*`-Optionen — vollständige Referenz in [07 Data Management/.../03 Spark API Options/22 DataStreamReader — Auto Loader.md](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/22%20DataStreamReader%20%E2%80%94%20Auto%20Loader.md). Für Kafka als Quelle: [23 DataStreamReader — Kafka.md](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/23%20DataStreamReader%20%E2%80%94%20Kafka.md).

## Beispiele

```python
spark.readStream.options(x="1", y=2)
# <...streaming.readwriter.DataStreamReader object ...>
```

```python
spark.readStream.options(**{"k1": "v1", "k2": "v2"})
# <...streaming.readwriter.DataStreamReader object ...>
```

```python
import time
q = spark.readStream.format("rate").options(
    rowsPerSecond=10, numPartitions=10).load().writeStream.format("console").start()
time.sleep(3)
q.stop()
```

## Quellen

- DataStreamReader.options: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/options

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
