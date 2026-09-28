# `cloudFiles.cleanSource.retentionDuration`

Wartezeit, bevor verarbeitete Dateien für die Bereinigung infrage kommen.

## Beschreibung

> *"Amount of time to wait before processed files become candidates for cleanup with clean source."*

Standardwert ist `30 days`. Nur wirksam, wenn [`cloudFiles.cleanSource`](cloudFiles.cleanSource.md) auf `DELETE` oder `MOVE` gesetzt ist. Bei `DELETE` gilt ein Mindestwert von 7 Tagen; bei `MOVE` gibt es keine Mindestgrenze.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.cleanSource", "DELETE")
      .option("cloudFiles.cleanSource.retentionDuration", "14 days")
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
