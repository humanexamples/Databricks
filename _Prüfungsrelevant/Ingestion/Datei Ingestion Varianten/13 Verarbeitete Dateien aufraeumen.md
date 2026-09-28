[← Übersicht](00%20Uebersicht.md)

# Fall 13 – Verarbeitete Dateien aufräumen (archivieren / löschen)

**A) Auto Loader `cloudFiles.cleanSource`**

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", checkpoint)
  .option("cloudFiles.cleanSource", "MOVE")   # OFF (Default) | DELETE | MOVE
  .option("cloudFiles.cleanSource.moveDestination", "s3://my-bucket/archive/landing/")
  .option("cloudFiles.cleanSource.retentionDuration", "30 days")
  .load("s3://my-bucket/landing/")
  .writeStream.option("checkpointLocation", checkpoint)
  .trigger(availableNow=True)
  .toTable("catalog.schema.bronze"))
```

SQL-Äquivalent:

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.bronze
AS SELECT * FROM STREAM read_files(
  's3://my-bucket/landing/',
  format => 'json',
  cleanSource => 'MOVE',
  `cleanSource.moveDestination` => 's3://my-bucket/archive/landing/');
```

**B) Manuell nach dem Lauf** (`dbutils.fs.mv` / `rm`) – **nicht** mit `foreachBatch` kombinieren: dort gelten Dateien schon als „verbraucht", sobald `foreachBatch` erfolgreich zurückkehrt, auch wenn nur ein Teil verarbeitet wurde.

---
[← Vorheriger Fall](12%20Zeitfenster-%20und%20gefilterte%20Ingestion.md) · [Übersicht](00%20Uebersicht.md)
