# `DataStreamReader` — Klassenreferenz

Referenz für `pyspark.sql.streaming.DataStreamReader`, erreichbar über `spark.readStream`. Structured-Streaming-Pendant zu [`DataFrameReader`](../03%20DataFrameReader/00%20Uebersicht.md).

## Beschreibung

*"Interface used to load a streaming DataFrame from external storage systems (for example, file systems and key-value stores). Use `spark.readStream` to access this."*

Auf Deutsch: Schnittstelle zum Laden eines Streaming-DataFrames aus externen Speichersystemen (Dateisysteme, Key-Value-Stores). Der Lesevorgang liefert einen Streaming-DataFrame, der anschließend über `df.writeStream` ([`DataStreamWriter`](../05%20DataStreamWriter/00%20Uebersicht.md)) geschrieben wird.

## Methodenübersicht

| Methode | Beschreibung | Details |
| --- | --- | --- |
| `format(source)` | Legt das Format der Eingabe-Datenquelle fest. | [01 format.md](01%20format.md) |
| `schema(schema)` | Legt das Schema des Streaming-DataFrames fest (überspringt Schema-Inferenz). | [02 schema.md](02%20schema.md) |
| `option(key, value)` | Fügt eine einzelne Eingabeoption der zugrunde liegenden Datenquelle hinzu. | [03 option.md](03%20option.md) |
| `options(**options)` | Fügt mehrere Eingabeoptionen auf einmal hinzu. | [04 options.md](04%20options.md) |
| `load(path, format, schema, **options)` | Lädt einen Datenstrom aus einer Datenquelle und gibt ihn als DataFrame zurück. | [05 load.md](05%20load.md) |
| `csv(path, schema, **options)` | Lädt einen CSV-Datei-Stream als DataFrame. | [06 csv.md](06%20csv.md) |
| `json(path, schema, **options)` | Lädt einen JSON-Datei-Stream als DataFrame. | [07 json.md](07%20json.md) |
| `parquet(path, **options)` | Lädt einen Parquet-Datei-Stream als DataFrame. | [08 parquet.md](08%20parquet.md) |
| `orc(path, **options)` | Lädt einen ORC-Datei-Stream als DataFrame. | [09 orc.md](09%20orc.md) |
| `text(path, **options)` | Lädt einen Text-Datei-Stream als DataFrame (`value`-Spalte). | [10 text.md](10%20text.md) |
| `xml(path, schema, **options)` | Lädt einen XML-Datei-Stream als DataFrame. | [11 xml.md](11%20xml.md) |
| `excel(path, **options)` | Lädt einen Excel-Datei-Stream als DataFrame. | [12 excel.md](12%20excel.md) |
| `table(tableName)` | Definiert einen Streaming-DataFrame auf einer Tabelle (Quelle muss Streaming unterstützen). | [13 table.md](13%20table.md) |
| `name(source_name)` | Vergibt einen Namen für die Streaming-Quelle (Checkpoint-Evolution). | [14 name.md](14%20name.md) |
| `changes(tableName)` | Gibt Zeilen-Änderungen (Change Data Capture) einer Tabelle als Streaming-DataFrame zurück. | [15 changes.md](15%20changes.md) |

## Typisches Grundgerüst

```python
import time
df = spark.readStream.format("rate").load()
df = df.selectExpr("value % 3 as v")
q = df.writeStream.format("console").start()
time.sleep(3)
q.stop()
```

```python
# Auto Loader über spark.readStream
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_chk/bronze")
      .load("/Volumes/catalog/schema/landing/"))
```

## Quellen

- DataStreamReader (Klassenreferenz): https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader

**Stand:** 2026-09-07, per `WebFetch` verifiziert (Seiten zuletzt aktualisiert 2026-06-04).
