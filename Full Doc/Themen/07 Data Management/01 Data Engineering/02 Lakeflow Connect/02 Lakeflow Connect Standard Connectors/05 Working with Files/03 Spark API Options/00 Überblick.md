# Spark API Options — Überblick

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options) (Gegenprüfung: [Azure-Spiegelseite](https://learn.microsoft.com/en-us/azure/databricks/spark/api-options)). Abgerufen 07.09.2026.

Diese Seite listet die Ein-/Ausgabe-Optionen für die Spark-APIs, die Daten lesen und schreiben. Sie sind der gemeinsame Options-Katalog hinter `spark.read` / `spark.readStream` / `spark.write` / `spark.writeStream`, der SQL-Tabellenfunktion `read_files` und `COPY INTO`.

---

## Wie Optionen übergeben werden

Optionen funktionieren mit `DataFrameReader.option()` / `.options()`, `DataStreamReader.option()` und den entsprechenden Writer-Methoden. Options-Namen sind **case-insensitiv**.

```python
df = spark.read.format("json").option("multiLine", True).load("/path/to/data")
```

```sql
SELECT * FROM read_files("/path/to/data", format => "json", multiLine => true)
```

In SQL (`read_files`, `STREAM read_files`) werden Optionen als benannte Parameter übergeben; der `cloudFiles.`-Präfix von Auto-Loader-Optionen entfällt dort.

---

## Seitenstruktur (Bereiche)

| Bereich | Datei |
|---|---|
| **DataFrameReader options** (Batch-Lesen) | |
| Common | [01 DataFrameReader — Common.md](01%20DataFrameReader%20%E2%80%94%20Common.md) |
| Avro | [02 DataFrameReader — Avro.md](02%20DataFrameReader%20%E2%80%94%20Avro.md) |
| CSV | [03 DataFrameReader — CSV.md](03%20DataFrameReader%20%E2%80%94%20CSV.md) |
| Excel | [04 DataFrameReader — Excel.md](04%20DataFrameReader%20%E2%80%94%20Excel.md) |
| JSON | [05 DataFrameReader — JSON.md](05%20DataFrameReader%20%E2%80%94%20JSON.md) |
| Kafka | [06 DataFrameReader — Kafka.md](06%20DataFrameReader%20%E2%80%94%20Kafka.md) |
| ORC | [07 DataFrameReader — ORC.md](07%20DataFrameReader%20%E2%80%94%20ORC.md) |
| Parquet | [08 DataFrameReader — Parquet.md](08%20DataFrameReader%20%E2%80%94%20Parquet.md) |
| State store | [09 DataFrameReader — State store.md](09%20DataFrameReader%20%E2%80%94%20State%20store.md) |
| Text | [10 DataFrameReader — Text.md](10%20DataFrameReader%20%E2%80%94%20Text.md) |
| XML | [11 DataFrameReader — XML.md](11%20DataFrameReader%20%E2%80%94%20XML.md) |
| **DataFrameWriter options** (Batch-Schreiben) | |
| Avro | [12 DataFrameWriter — Avro.md](12%20DataFrameWriter%20%E2%80%94%20Avro.md) |
| Delta Lake und Apache Iceberg | [13 DataFrameWriter — Delta Lake und Apache Iceberg.md](13%20DataFrameWriter%20%E2%80%94%20Delta%20Lake%20und%20Apache%20Iceberg.md) |
| CSV | [14 DataFrameWriter — CSV.md](14%20DataFrameWriter%20%E2%80%94%20CSV.md) |
| Excel | [15 DataFrameWriter — Excel.md](15%20DataFrameWriter%20%E2%80%94%20Excel.md) |
| JSON | [16 DataFrameWriter — JSON.md](16%20DataFrameWriter%20%E2%80%94%20JSON.md) |
| ORC | [17 DataFrameWriter — ORC.md](17%20DataFrameWriter%20%E2%80%94%20ORC.md) |
| Parquet | [18 DataFrameWriter — Parquet.md](18%20DataFrameWriter%20%E2%80%94%20Parquet.md) |
| Text | [19 DataFrameWriter — Text.md](19%20DataFrameWriter%20%E2%80%94%20Text.md) |
| XML | [20 DataFrameWriter — XML.md](20%20DataFrameWriter%20%E2%80%94%20XML.md) |
| **DataStreamReader options** (Streaming-Lesen) | |
| Common | [21 DataStreamReader — Common.md](21%20DataStreamReader%20%E2%80%94%20Common.md) |
| Auto Loader (Common / Directory listing / File notification) | [22 DataStreamReader — Auto Loader.md](22%20DataStreamReader%20%E2%80%94%20Auto%20Loader.md) |
| Kafka | [23 DataStreamReader — Kafka.md](23%20DataStreamReader%20%E2%80%94%20Kafka.md) |

Die Seite enthält **keinen** eigenen Abschnitt „DataStreamWriter options" — Streaming-Schreib-Optionen (`checkpointLocation`, `mergeSchema`, `txnAppId`/`txnVersion`, …) sind in den Writer-Format-Abschnitten bzw. in der Structured-Streaming-Doku beschrieben.

---

## Verwandte Projektdateien

- [`../_spark_read.md`](../_spark_read.md) — `spark.read` / `spark.readStream` im Detail
- [`../_read_files.md`](../_read_files.md) — SQL-Tabellenfunktion `read_files`
- [`../_Vergleich_read_files_vs_spark_read.md`](../_Vergleich_read_files_vs_spark_read.md)
- [`../06 Auto Loader/Options/`](../06%20Auto%20Loader/Options/README.md) — eine Datei pro `cloudFiles.*`-Option
