# cloudFiles.includeExistingFiles

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `true` |
| **Gültige Werte** | `true`, `false` |
| **`read_files`-Parameter** | `includeExistingFiles` |
| **Seit** | alle Versionen |

## Beschreibung

> „Whether to include existing files in the stream processing input path or to only process new files arriving after initial setup. This option is evaluated only when you start a stream for the first time. Changing this option after restarting the stream has no effect."

Wird nur beim allerersten Start eines Streams mit frischem Checkpoint ausgewertet.

**Wichtig:** Auch bei `false` führt Auto Loader beim Erststart eine Verzeichnisauflistung durch, um nach dem Stream-Start erstellte Dateien zu erkennen — eine anfängliche Auflistung lässt sich also nicht vollständig vermeiden.

## Beispiel

```sql
CREATE OR REFRESH STREAMING TABLE events_new_only
AS SELECT * FROM STREAM read_files('/Volumes/analytics/bronze/events',
  format => 'json', includeExistingFiles => false);
```

## Siehe auch

- [../09 Datei-Tracking und Checkpoints.md](../09%20Datei-Tracking%20und%20Checkpoints.md)
