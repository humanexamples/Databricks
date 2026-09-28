# `cloudFiles.allowOverwrites`

Steuert, ob nachträglich geänderte Dateien erneut verarbeitet werden.

## Beschreibung

> *"Whether to allow input directory file changes to overwrite existing data."*

Bei `false` (Standard) verarbeitet Auto Loader jede Datei genau einmal, identifiziert anhand ihres Dateipfads — wird eine Datei später angehängt oder überschrieben, wird sie nicht erneut aufgenommen. Bei `true` fließt zusätzlich der letzte Änderungszeitpunkt ins Tracking mit ein, sodass die neueste Version einer geänderten Datei garantiert verarbeitet wird — dabei liest Auto Loader die gesamte Datei erneut, selbst wenn sie nur teilweise geändert wurde, und entstehende doppelte Datensätze müssen selbst behandelt werden. Databricks empfiehlt, ausschließlich unveränderliche Dateien aufzunehmen und den Standardwert `false` beizubehalten.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.allowOverwrites", "true")
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
