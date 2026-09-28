# `DataFrameWriter` — Klassenreferenz

Referenz für `pyspark.sql.DataFrameWriter`, erreichbar über `df.write`.

## Beschreibung

*"Interface used to write a DataFrame to external storage systems (e.g. file systems, key-value stores, etc)."*

Auf Deutsch: Schnittstelle zum Schreiben eines DataFrames in externe Speichersysteme (Dateisysteme, Key-Value-Stores usw.), erreichbar über `df.write`.

## Methodenübersicht

| Methode | Beschreibung | Details |
| --- | --- | --- |
| `mode(saveMode)` | Legt das Verhalten fest, wenn Daten/Tabelle bereits existieren. | [02 mode.md](02%20mode.md) |
| `format(source)` | Legt das Ausgabeformat fest. | [01 format.md](01%20format.md) |
| `option(key, value)` | Fügt eine Ausgabeoption hinzu. | [03 option.md](03%20option.md) |
| `options(**options)` | Fügt mehrere Ausgabeoptionen hinzu. | [04 options.md](04%20options.md) |
| `partitionBy(*cols)` | Partitioniert die Ausgabe im Dateisystem nach den angegebenen Spalten. | [11 partitionBy.md](11%20partitionBy.md) |
| `bucketBy(numBuckets, col, *cols)` | Bucketed die Ausgabe nach den angegebenen Spalten. | — |
| `sortBy(col, *cols)` | Sortiert die Ausgabe innerhalb jedes Buckets nach den angegebenen Spalten. | [12 sortBy.md](12%20sortBy.md) |
| `clusterBy(*cols)` | Clustert die Daten nach den angegebenen Spalten, um die Query-Performance zu optimieren. | [13 clusterBy.md](13%20clusterBy.md) |
| `save(path, format, mode, partitionBy, **options)` | Speichert den Inhalt des DataFrames in einer Datenquelle. | [05 save.md](05%20save.md) |
| `insertInto(tableName, overwrite)` | Fügt den Inhalt des DataFrames in die angegebene Tabelle ein. | [10 insertInto.md](10%20insertInto.md) |
| `saveAsTable(name, format, mode, partitionBy, **options)` | Speichert den Inhalt des DataFrames als die angegebene Tabelle. | [09 saveAsTable.md](09%20saveAsTable.md) |
| `json(path, mode, compression, ...)` | Speichert den Inhalt im JSON-Format. | [07 json.md](07%20json.md) |
| `parquet(path, mode, partitionBy, compression)` | Speichert den Inhalt im Parquet-Format. | — |
| `text(path, compression, lineSep)` | Speichert den Inhalt als Textdatei. | [08 text.md](08%20text.md) |
| `csv(path, mode, compression, sep, ...)` | Speichert den Inhalt im CSV-Format. | [06 csv.md](06%20csv.md) |
| `xml(path, rowTag, mode, ...)` | Speichert den Inhalt im XML-Format. | — |
| `orc(path, mode, partitionBy, compression)` | Speichert den Inhalt im ORC-Format. | — |
| `excel(path, mode, dataAddress, headerRows)` | Speichert den Inhalt im Excel-Format. | — |
| `jdbc(url, table, mode, properties)` | Speichert den Inhalt in einer externen Datenbanktabelle über JDBC. | — |

## Schreibmodi (`mode`)

| Modus | Verhalten |
| --- | --- |
| `append` | Hängt an bestehende Daten an. |
| `overwrite` | Überschreibt bestehende Daten. |
| `error` / `errorifexists` | Wirft eine Exception, falls die Daten bereits existieren (**Standard**). |
| `ignore` | Ignoriert den Schreibvorgang stillschweigend, falls die Daten bereits existieren. |

Details siehe [02 mode.md](02%20mode.md).

## Streaming-Pendant: `DataStreamWriter`

Für Structured-Streaming-DataFrames (`spark.readStream`) gibt es `df.writeStream` mit der Klasse `DataStreamWriter` (`outputMode`, `trigger`, `foreachBatch`, `toTable`, …). Siehe [../05 DataStreamWriter/00 Uebersicht.md](../05%20DataStreamWriter/00%20Uebersicht.md).

## Quellen

- DataFrameWriter (Klassenreferenz): https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
