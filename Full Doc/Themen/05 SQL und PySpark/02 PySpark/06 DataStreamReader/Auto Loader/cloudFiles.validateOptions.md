# `cloudFiles.validateOptions`

Steuert, ob unbekannte oder widersprüchliche Optionen als Fehler gemeldet werden.

## Beschreibung

> *"Whether to validate Auto Loader options and return an error for unknown or inconsistent options."*

Standardwert ist `true`. Bei `false` meldet Auto Loader unbekannte oder inkonsistente Optionen nicht mehr als Fehler — unter anderem Teil eines dokumentierten Workarounds für den Fehler `CF_MANAGED_FILE_EVENTS_INVALID_CONTINUATION_TOKEN`.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.validateOptions", False)
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
