# `cloudFiles.cleanSource.moveDestination`

Zielpfad für archivierte Quelldateien bei `cleanSource = MOVE`.

## Beschreibung

> *"Path to archive processed files to when `cloudFiles.cleanSource` is set to `MOVE`."*

Nur erforderlich, wenn [`cloudFiles.cleanSource`](cloudFiles.cleanSource.md) auf `MOVE` steht. Der Zielpfad darf **kein** Kindverzeichnis des Quellverzeichnisses sein — sonst würden die verschobenen Dateien versehentlich erneut eingelesen. Er muss außerdem in derselben External Location, demselben Volume bzw. demselben DBFS-Mount liegen wie die Quelle; Verschiebungen über Bucket-/Container-Grenzen hinweg schlagen fehl. Auto Loader benötigt Schreibberechtigung auf dem Zielpfad.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.cleanSource", "MOVE")
      .option("cloudFiles.cleanSource.moveDestination", "s3://my-bucket/archive/landing/")
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
