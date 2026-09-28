# Auto Loader — Datei-Tracking und Checkpoints

Quellen: [Configure Auto Loader for production workloads](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/production), Auto Loader FAQ, Spark API options reference.

Sobald Dateien erkannt werden, wird ihre Metadaten in einem skalierbaren Key-Value-Store (RocksDB) am Checkpoint-Speicherort der Auto-Loader-Pipeline persistiert. Dieser Zustand ermöglicht Exactly-once-Verarbeitung ohne manuelle Zustandsverwaltung.

---

## Checkpoint-Speicherort

- Databricks empfiehlt, den Checkpoint-Speicherort **ohne** Cloud-Objekt-Lifecycle-Richtlinie zu betreiben — bereinigen solche Richtlinien Dateien im Checkpoint-Verzeichnis, wird der Stream-Zustand beschädigt und ein Neustart von Grund auf nötig.
- Für jeden Stream und jedes Quellverzeichnis sollten **separate Checkpoints** verwendet werden.
- Ändert sich der Checkpoint-Speicherort beim Neustart eines Streams, gilt der vorherige Stream als aufgegeben — es wird effektiv ein neuer Stream gestartet.

---

## Standard-Tracking-Parameter (Dateipfad) und `cloudFiles.allowOverwrites`

Auto Loader nimmt jede Datei normalerweise nur einmal auf, basierend auf ihrem **Dateipfad**. Der Dateipfad ist der alleinige Standard-Tracking-Parameter; ein inhaltsbasiertes Tracking (z. B. Prüfsumme) ist nicht dokumentiert.

Mit der Standardeinstellung `cloudFiles.allowOverwrites = false` gilt: Dateien werden genau einmal verarbeitet. Wenn an eine Datei angehängt oder sie überschrieben wird, kann Auto Loader nicht garantieren, welche Dateiversion verarbeitet wird. Wird die Option auf `true` gesetzt, erweitert sich der Tracking-Parameter um den **letzten Änderungszeitpunkt** der Datei: Es ist garantiert, dass Auto Loader die neueste Version verarbeitet — nicht aber, welche Zwischenversion.

**Zwei wörtlich bestätigte Warnungen:**

- Bei aktiviertem `cloudFiles.allowOverwrites` müssen doppelte Datensätze selbst behandelt werden. Auto Loader verarbeitet die gesamte Datei erneut, selbst wenn nur an sie angehängt oder sie teilweise aktualisiert wurde. Generell empfiehlt Databricks, mit Auto Loader ausschließlich **unveränderliche (immutable) Dateien** aufzunehmen und die Standardeinstellung `false` zu verwenden.
- Speziell im File-Notification-Modus: Da sich der Zeitpunkt des File-Notification-Ereignisses und der Zeitpunkt der Dateiänderung unterscheiden können, kann Auto Loader zwei unterschiedliche Zeitstempel erhalten und dieselbe Datei zweimal aufnehmen, selbst wenn die Datei nicht aktualisiert wurde.

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.allowOverwrites", "true")
  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
  .load("/Volumes/analytics/bronze/daily_drop"))
```

---

## `cloudFiles.includeExistingFiles`: Anfangszustand steuern

Standardwert **`true`**: Ob vorhandene Dateien im Eingabepfad in die Stream-Verarbeitung einbezogen werden sollen, oder ob nur neue Dateien verarbeitet werden sollen, die nach der ursprünglichen Einrichtung eintreffen. Diese Option wird **ausschließlich beim allerersten Start** eines Streams mit frischem Checkpoint ausgewertet — ein späteres Ändern hat keine Wirkung mehr.

**Wichtige Einschränkung (FAQ, wörtlich):** *"Kann ich eine vollständige Verzeichnisauflistung beim Erststart vermeiden? Nein. Selbst wenn `includeExistingFiles` auf `false` gesetzt ist, führt Auto Loader eine Verzeichnisauflistung durch, um Dateien zu erkennen, die nach dem Stream-Start erstellt wurden."*

```sql
-- Streaming Table, die NUR Dateien verarbeitet, die NACH Tabellenerstellung erscheinen
CREATE OR REFRESH STREAMING TABLE events_new_only
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  includeExistingFiles => false
);
```

---

## `cloudFiles.maxFileAge`

Der Mindestwert für `cloudFiles.maxFileAge` ist `"14 days"`. Databricks empfiehlt eine konservative Einstellung, mindestens **90 Tage**, für langlebige, hochvolumige Streams, um das Wachstum des Zustands zu begrenzen (Deletes erscheinen in RocksDB zunächst als Tombstone-Einträge, wodurch der Speicherverbrauch vorübergehend steigen kann).

**Warnung laut Doku:** Eine zu aggressive Einstellung kann zu doppelter Ingestion oder übersehenen Dateien führen — die Option ist als Kostenkontrollmechanismus für hochvolumige Datensätze gedacht, nicht als Standardeinstellung.

---

## Startzeit-Optimierung

Ab **Databricks Runtime 15.4 LTS** wartet Auto Loader nicht darauf, dass der gesamte RocksDB-Zustand heruntergeladen ist, bevor der Stream startet, was die Startzeit bei umfangreichen/langlebigen Streams beschleunigt.

---

## `cloudFiles.backfillInterval`

Es empfiehlt sich, `cloudFiles.backfillInterval` zu setzen, um asynchrone Backfills in einem festgelegten Intervall auszulösen — beispielsweise auf einen Tag für tägliche Backfills oder auf eine Woche für wöchentliche Backfills. Regelmäßige Backfills verursachen laut Doku **keine** Duplikate.

Databricks empfahl dieses Setting früher speziell für den klassischen File-Notification-Modus, weil Cloud-Speicher-Benachrichtigungssysteme zu verpassten oder verspätet eintreffenden Dateien führen konnten — bei File Events entfällt diese Notwendigkeit, da Backfills dort automatisch gehandhabt werden.

---

## Rate Limiting: `maxFilesPerTrigger` / `maxBytesPerTrigger`

Auto Loader verarbeitet standardmäßig maximal **1000 Dateien** pro Micro-Batch. `cloudFiles.maxFilesPerTrigger` ist eine **harte** Grenze, `cloudFiles.maxBytesPerTrigger` eine **weiche** (es können mehr Bytes verarbeitet werden als angegeben). Sind beide gesetzt, verarbeitet Auto Loader so viele Dateien, wie nötig sind, um eines der beiden Limits zu erreichen.

Der `Trigger.AvailableNow`-Trigger weist Auto Loader an, alle Dateien zu verarbeiten, die vor dem Start der Abfrage eingetroffen sind (verfügbar ab Databricks Runtime 10.4 LTS). Für nicht latenzkritische Workloads sind `Trigger.AvailableNow`-Batch-Jobs statt Continuous-Triggern kostengünstiger.

---

## Quelldaten aufräumen

Sammeln sich Dateien im Quellverzeichnis an, steigen die Speicherkosten, und die Datei-Erkennung wird langsamer. Über `cloudFiles.cleanSource` können verarbeitete Dateien automatisch verschoben oder gelöscht werden — siehe [10 Clean Source (Quelldateien aufräumen).md](10%20Clean%20Source%20%28Quelldateien%20aufräumen%29.md).
