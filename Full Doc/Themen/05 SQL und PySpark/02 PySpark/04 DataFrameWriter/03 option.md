# `DataFrameWriter.option()`

Fügt eine einzelne Ausgabeoption für die zugrunde liegende Datenquelle hinzu.

## Signatur

```python
option(key, value)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `key` | `str` | Der Options-Schlüssel. |
| `value` | `str`, `int`, `float` oder `bool` | Der Options-Wert. |

## Rückgabewert

`DataFrameWriter`

## Verfügbare Optionen

Anders als beim Lesen (`DataFrameReader`) führt die [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options) für `DataFrameWriter` **keinen** formatübergreifenden „Common"-Abschnitt — jedes Zielformat hat seine eigene Optionstabelle. Auf Databricks am wichtigsten ist **Delta Lake / Apache Iceberg** (Standardformat, siehe [13 DataFrameWriter — Delta Lake und Apache Iceberg.md](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/13%20DataFrameWriter%20%E2%80%94%20Delta%20Lake%20und%20Apache%20Iceberg.md)):

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `mergeSchema` | `None` | `true`/`false` | Aktiviert Schema Evolution für den Schreibvorgang — neue Spalten aus der Quelle werden dem Zielschema hinzugefügt. Gilt sowohl für Batch- als auch für Streaming-Appends. |
| `overwriteSchema` | `None` | `true`/`false` | Ersetzt Schema und Partitionierung beim Überschreiben. Erfordert `mode("overwrite")` ohne `replaceWhere`, nicht kombinierbar mit `partitionOverwriteMode`. |
| `replaceWhere` | `None` | Prädikat-Ausdruck | Überschreibt atomar nur die Datensätze, die dem Prädikat entsprechen (selektives Überschreiben). |
| `replaceOn` | `None` | Boolean-Ausdruck | Boolean-Ausdruck, der Zielzeilen zum Ersetzen durch Quellzeilen matcht (ab Runtime 17.1). |
| `replaceUsing` | `None` | kommagetrennte Spaltenliste | Spalten, über die Ziel- und Quellzeilen für den Ersatz gematcht werden (ab Runtime 16.3). |
| `targetAlias` | `None` | String | Alias für die Zieltabelle, zur Disambiguierung bei `replaceOn`/`replaceWhere`. |
| `partitionOverwriteMode` | `None` | `static`/`dynamic` | Bei `dynamic` werden nur Partitionen mit neuen Daten überschrieben (Legacy, nicht auf Serverless/DBSQL). |
| `clusterByAuto` | `false` | `true`/`false` | Aktiviert Automatic Liquid Clustering (Keys werden von Databricks gewählt); nur mit `mode("overwrite")`, ab Runtime 16.4. |
| `optimizeWrite` | `None` | `true`/`false` | Aktiviert Auto Optimize Write für diesen Schreibvorgang (überschreibt die Spark-Konfiguration). |
| `userMetadata` | `None` | String | Benutzerdefinierter String im Commit, sichtbar in `DESCRIBE HISTORY`. |
| `txnAppId` | `None` | String | Eindeutige Anwendungs-ID für idempotente Schreibvorgänge in `foreachBatch` — zusammen mit `txnVersion` für Exactly-once-Writes über mehrere Delta-Tabellen. |
| `txnVersion` | `None` | monoton steigende Ganzzahl | Transaktionsversion für idempotente `foreachBatch`-Writes, zusammen mit `txnAppId`. |

Für andere Zielformate gilt je eine eigene Optionstabelle — Auswahl an gemeinsamen Schlüsseln, die (mit format-eigenen erlaubten Werten) in fast jedem Format wiederkehren:

| Option | Beispielwerte (formatabhängig) | Beschreibung |
|---|---|---|
| `compression` | CSV/JSON/Text/XML: `none`,`bzip2`,`gzip`,`lz4`,`snappy`,`deflate`,`zstd`; Parquet zusätzlich `lzo`,`brotli`,`lz4_raw`; ORC: `uncompressed`,`zlib`,`lzo`,`zstd`,`lz4`,`brotli`; Avro: `uncompressed`,`deflate`,`snappy`,`bzip2`,`xz`,`zstandard` | Komprimierungscodec beim Schreiben — Standardwert und erlaubte Werte unterscheiden sich je Format. |
| `dateFormat` | z. B. `yyyy-MM-dd` | Formatstring für Datumsspalten (CSV, JSON, XML). |
| `timestampFormat` | z. B. `yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]` | Formatstring für Timestamp-Spalten (CSV, JSON, XML). |
| `encoding` | `UTF-8` | Zeichenkodierung der Ausgabedateien (CSV, JSON, Text, XML). |
| `lineSep` | `\n` | Zeilentrenner zwischen Datensätzen (CSV, JSON, Text). |

Format-eigene Tabellen (vollständig): [12 Avro](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/12%20DataFrameWriter%20%E2%80%94%20Avro.md), [14 CSV](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/14%20DataFrameWriter%20%E2%80%94%20CSV.md), [15 Excel](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/15%20DataFrameWriter%20%E2%80%94%20Excel.md), [16 JSON](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/16%20DataFrameWriter%20%E2%80%94%20JSON.md), [17 ORC](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/17%20DataFrameWriter%20%E2%80%94%20ORC.md), [18 Parquet](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/18%20DataFrameWriter%20%E2%80%94%20Parquet.md), [19 Text](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/19%20DataFrameWriter%20%E2%80%94%20Text.md), [20 XML](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/20%20DataFrameWriter%20%E2%80%94%20XML.md).

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="option") as d:
    df = spark.createDataFrame([(100, None)], "age INT, name STRING")
    df.write.option("nullValue", "Alice").mode("overwrite").format("csv").save(d)
    spark.read.schema(df.schema).format('csv').load(d).show()
    # +---+------------+
    # |age|        name|
    # +---+------------+
    # |100|Alice|
    # +---+------------+
```

Für die vollständige Liste verfügbarer Optionen verweist die Dokumentation auf die `DataFrameWriter`-Batch-Write-Optionen (`/aws/en/spark/api-options#batch-write-options`).

## Quellen

- DataFrameWriter.option: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/option

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
