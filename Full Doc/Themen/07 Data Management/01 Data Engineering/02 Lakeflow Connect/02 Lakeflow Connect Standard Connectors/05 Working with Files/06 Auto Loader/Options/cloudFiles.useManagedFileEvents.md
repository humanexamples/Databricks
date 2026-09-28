# cloudFiles.useManagedFileEvents

| | |
|---|---|
| **Kategorie** | File Notification Mode option (File Events) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `false` |
| **Gültige Werte** | `true`, `false` |
| **`read_files`-Parameter** | `useManagedFileEvents` |
| **Seit** | Databricks Runtime 14.3 LTS und höher |

## Beschreibung

> „When set to `true`, Auto Loader uses the file events service to discover files in your external location. You can use this option only if the load path is in an external location with file events enabled. […] There are some situations when Auto Loader uses directory listing even though the file events option is enabled: During initial load […] If Auto Loader runs infrequently, this cache can expire […] To avoid this scenario, invoke Auto Loader at least once every seven days."

Aktiviert den empfohlenen **File-Events**-Modus (eine gemeinsame Queue pro External Location). Bei aktiviertem File Events sind mehrere Optionen **nicht** erlaubt: `useNotifications`, `useIncrementalListing`, `cloudFiles.fetchParallelism`, `cloudFiles.backfillInterval`, `cloudFiles.pathRewrites`, `cloudFiles.resourceTag` sowie die cloud-spezifischen Notification-/Auth-Optionen.

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

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
- [../07 Wie File Events funktionieren.md](../07%20Wie%20File%20Events%20funktionieren.md)
- [../08 Migration zu File Events.md](../08%20Migration%20zu%20File%20Events.md)
