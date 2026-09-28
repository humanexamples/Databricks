# `DataStreamWriter` — Klassenreferenz

Referenz für `pyspark.sql.streaming.DataStreamWriter`, erreichbar über `df.writeStream` (bei einem Streaming-DataFrame aus `spark.readStream`). Structured-Streaming-Pendant zu [`DataFrameWriter`](../04%20DataFrameWriter/00%20Uebersicht.md).

## Beschreibung

*"Interface used to write a streaming DataFrame to external storage systems (e.g. file systems, key-value stores, etc)."*

Auf Deutsch: Schnittstelle zum kontinuierlichen Schreiben eines Streaming-DataFrames in externe Speichersysteme. Der Schreibvorgang wird mit `start()` bzw. `toTable()`/`table()` gestartet und liefert ein `StreamingQuery`-Objekt zurück.

## Methodenübersicht

| Methode | Beschreibung | Details |
| --- | --- | --- |
| `format(source)` | Legt die zugrunde liegende Ausgabe-Datenquelle (Senke) fest. | [01 format.md](01%20format.md) |
| `option(key, value)` | Fügt eine einzelne Ausgabeoption hinzu (u. a. `checkpointLocation`). | [02 option.md](02%20option.md) |
| `options(**options)` | Fügt mehrere Ausgabeoptionen auf einmal hinzu. | [03 options.md](03%20options.md) |
| `outputMode(outputMode)` | Legt fest, wie Daten in die Streaming-Senke geschrieben werden (`append`, `complete`, `update`). | [04 outputMode.md](04%20outputMode.md) |
| `partitionBy(*cols)` | Partitioniert die Ausgabe im Dateisystem nach den angegebenen Spalten. | [05 partitionBy.md](05%20partitionBy.md) |
| `clusterBy(*cols)` | Clustert die Ausgabe nach den angegebenen Spalten (auch für hohe Kardinalität). | [06 clusterBy.md](06%20clusterBy.md) |
| `trigger(...)` | Legt das Auslöse-Intervall der Streaming-Query fest (`processingTime`, `availableNow`, `continuous`, …). | [07 trigger.md](07%20trigger.md) |
| `queryName(queryName)` | Vergibt einen eindeutigen Namen für die `StreamingQuery`. | [08 queryName.md](08%20queryName.md) |
| `foreach(f)` | Verarbeitet die Ausgabe Zeile für Zeile über eine Funktion oder ein Writer-Objekt. | [09 foreach.md](09%20foreach.md) |
| `foreachBatch(func)` | Verarbeitet jede Micro-Batch als DataFrame + Batch-ID (z. B. für `MERGE`/Upsert). | [10 foreachBatch.md](10%20foreachBatch.md) |
| `start(path, format, outputMode, partitionBy, queryName, **options)` | Startet die Streaming-Query gegen eine Datenquelle/-senke. | [11 start.md](11%20start.md) |
| `toTable(tableName, format, outputMode, partitionBy, queryName, **options)` | Startet die Streaming-Query mit kontinuierlicher Ausgabe in eine Tabelle. | [12 toTable.md](12%20toTable.md) |
| `table(tableName)` | Alias für `toTable()`. | [13 table.md](13%20table.md) |

## Ausgabemodi (`outputMode`)

| Modus | Verhalten |
| --- | --- |
| `append` | Nur neue Zeilen werden in die Senke geschrieben (Standard). |
| `complete` | Bei jedem Update wird das **gesamte** Ergebnis geschrieben (nur mit Aggregationen). |
| `update` | Nur bei diesem Update geänderte Zeilen werden geschrieben; ohne Aggregation entspricht das `append`. |

Details siehe [04 outputMode.md](04%20outputMode.md).

## Typisches Grundgerüst

```python
df = spark.readStream.format("cloudFiles") \
    .option("cloudFiles.format", "json") \
    .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_chk/bronze") \
    .load("/Volumes/catalog/schema/landing/")

q = (df.writeStream
       .option("checkpointLocation", "/Volumes/catalog/schema/_chk/bronze")
       .trigger(availableNow=True)
       .toTable("catalog.schema.bronze"))
```

## Quellen

- DataStreamWriter (Klassenreferenz): https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
