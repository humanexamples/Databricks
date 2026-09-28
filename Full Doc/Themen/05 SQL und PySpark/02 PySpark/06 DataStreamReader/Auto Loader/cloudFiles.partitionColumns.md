# `cloudFiles.partitionColumns`

Steuert die Erkennung von Hive-Style-Partitionsspalten.

## Beschreibung

> *"A comma-separated list of Hive-style partition columns that you would like inferred from the directory structure of the files. Hive-style partition columns are key-value pairs combined by an equality sign such as `<base-path>/a=x/b=1/c=y/file.format`. In this example, the partition columns are `a`, `b`, and `c`."*

Bei Schema-Inferenz werden diese Spalten automatisch zum Schema hinzugefügt, sofern man auf `<base-path>` lädt. Ist stattdessen ein explizites Schema angegeben, erwartet Auto Loader diese Spalten bereits als Teil davon. Eine leere Zeichenkette `""` ignoriert alle Partitionsspalten. Wichtig: Auto Loader berücksichtigt Partitionsspalten **nicht** bei der Schema-Evolution — taucht später eine neue Partitionsspalte im Verzeichnisbaum auf, muss sie hier explizit ergänzt werden, sonst wird sie ignoriert.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.partitionColumns", "event,date,hour")
      .load("/Volumes/analytics/bronze/events"))
```

```sql
CREATE OR REFRESH STREAMING TABLE events
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaLocation => '/Volumes/analytics/bronze/_schema',
  partitionColumns => 'event,date,hour'
);
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
