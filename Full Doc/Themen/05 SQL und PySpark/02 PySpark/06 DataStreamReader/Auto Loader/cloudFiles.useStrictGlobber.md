# `cloudFiles.useStrictGlobber`

Schaltet auf das strikte Glob-Verhalten anderer Spark-Dateiquellen um.

## Beschreibung

> *"Whether to use a strict globber that matches the default globbing behavior of other file sources in Apache Spark."*

Verfügbar ab Databricks Runtime 12.2 LTS. Standardwert ist `false` — Auto Loader verwendet dann sein eigenes, etwas lockereres Standard-Globbing-Verhalten. Bei `true` verhält sich die Auswertung von Glob-Mustern im Pfad stattdessen genauso wie bei anderen Apache-Spark-Dateiquellen. Wie bei `inferColumnTypes` ist auch hier der Default von `read_files` (SQL) das Gegenteil des nativen `cloudFiles`-Defaults.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useStrictGlobber", "true")
      .load("/Volumes/analytics/bronze/*/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
