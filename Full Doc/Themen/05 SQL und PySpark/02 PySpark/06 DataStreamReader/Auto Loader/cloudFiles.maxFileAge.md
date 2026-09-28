# `cloudFiles.maxFileAge`

Steuert, wie lange Dateien zur Deduplizierung nachverfolgt werden.

## Beschreibung

> *"How long a file event is tracked for deduplication purposes. Databricks does not recommend tuning this parameter unless you are ingesting data at the order of millions of files an hour. […] Tuning `cloudFiles.maxFileAge` too aggressively can cause data quality issues such as duplicate ingestion or missing files. Therefore, Databricks recommends a conservative setting for `cloudFiles.maxFileAge`, such as 90 days, which is similar to what comparable data ingestion solutions recommend."*

Es gibt keinen Standardwert — die Option ist ein Kostenkontrollmechanismus, um das Wachstum des RocksDB-Zustands bei sehr großen, lange laufenden Streams zu begrenzen, und wird von Databricks nur bei Ingestion im Bereich von Millionen Dateien pro Stunde empfohlen. Der Mindestwert liegt bei `"14 days"`. Gelöschte Einträge erscheinen in RocksDB zunächst als Tombstones, was vorübergehend zu höherem Speicherverbrauch führt.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.maxFileAge", "90 days")
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
