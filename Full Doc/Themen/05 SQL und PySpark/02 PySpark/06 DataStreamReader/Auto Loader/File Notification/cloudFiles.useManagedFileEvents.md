# `cloudFiles.useManagedFileEvents`

Aktiviert den empfohlenen File-Events-Modus.

## Beschreibung

> *"When set to `true`, Auto Loader uses the file events service to discover files in your external location. You can use this option only if the load path is in an external location with file events enabled. […] There are some situations when Auto Loader uses directory listing even though the file events option is enabled: During initial load […] If Auto Loader runs infrequently, this cache can expire […] To avoid this scenario, invoke Auto Loader at least once every seven days."*

Verfügbar ab Databricks Runtime 14.3 LTS. Bei `true` nutzt Auto Loader den File-Events-Dienst, der eine gemeinsame Queue pro External Location verwaltet, statt für jeden Stream einzeln Cloud-Ressourcen einzurichten — der von Databricks empfohlene Nachfolger des klassischen `cloudFiles.useNotifications`. Voraussetzung ist, dass der Ladepfad in einer External Location mit aktivierten File Events liegt. Bei aktiviertem File-Events-Modus sind mehrere andere Optionen **nicht erlaubt**: `cloudFiles.useNotifications`, `cloudFiles.useIncrementalListing`, `cloudFiles.fetchParallelism`, `cloudFiles.backfillInterval`, `cloudFiles.pathRewrites`, `cloudFiles.resourceTag` sowie die cloud-spezifischen Notification-/Auth-Optionen. Läuft ein Stream sehr selten, kann der interne Cache ablaufen — Databricks empfiehlt daher, Auto Loader mindestens alle sieben Tage einmal laufen zu lassen.

## Beispiel

```python
autoLoaderStream = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.useManagedFileEvents", True)
  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
  .load("/Volumes/analytics/bronze/events"))
```

```sql
CREATE OR REFRESH STREAMING TABLE t
AS SELECT * FROM STREAM read_files('abfss://path/to/external/location',
  format => 'json', useManagedFileEvents => 'True');
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
