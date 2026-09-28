# `cloudFiles.cleanSource`

Löscht oder verschiebt bereits verarbeitete Quelldateien automatisch.

## Beschreibung

> *"Whether to automatically delete or move processed files from the input directory. When set to `OFF` (default), no files are deleted. When set to `DELETE` or `MOVE`, Auto Loader deletes or moves files after they are processed."*

Verfügbar ab Databricks Runtime 16.4. Setzt voraus, dass der Stream exklusiven Zugriff auf das Quellverzeichnis hat — sonst könnten gerade erst gelandete, noch unverarbeitete Dateien versehentlich gelöscht werden. Bei Verwendung von `foreachBatch` gelten Dateien bereits als Kandidaten für die Bereinigung, sobald der jeweilige Aufruf erfolgreich zurückkehrt. Das Aktivieren erhöht den Checkpoint-Overhead etwas, schaltet dafür aber zusätzliche Archiv-Felder in der `cloud_files_state`-Funktion frei.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.cleanSource", "MOVE")
      .option("cloudFiles.cleanSource.moveDestination", "s3://my-bucket/archive/landing/")
      .option("cloudFiles.cleanSource.retentionDuration", "14 days")
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
