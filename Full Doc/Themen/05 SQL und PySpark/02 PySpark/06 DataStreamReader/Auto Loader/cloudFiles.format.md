# `cloudFiles.format`

Pflichtoption für Auto Loader (`spark.readStream.format("cloudFiles")`).

## Beschreibung

> *"The data file format in the source path. Valid values include: `avro`, `binaryFile`, `csv`, `json`, `orc`, `parquet`, `text`, `xml`."*

Legt fest, welches Dateiformat im Quellpfad gelesen wird. Es gibt keinen Standardwert — die Option muss immer explizit gesetzt werden. Vorkomprimierte Varianten der genannten Formate werden ebenfalls erkannt und gelesen.

## Beispiel

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
  .load("/Volumes/analytics/bronze/events"))
```

```sql
CREATE OR REFRESH STREAMING TABLE events
AS SELECT * FROM STREAM read_files('/Volumes/analytics/bronze/events', format => 'json');
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
