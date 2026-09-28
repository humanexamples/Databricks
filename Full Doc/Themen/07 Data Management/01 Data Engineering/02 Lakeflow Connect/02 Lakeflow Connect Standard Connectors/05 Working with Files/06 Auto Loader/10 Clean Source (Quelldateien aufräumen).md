# Auto Loader — Clean Source (Quelldateien aufräumen)

Quelle: [Clean up processed files with Auto Loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/clean-source).

Mit `cloudFiles.cleanSource` verschiebt oder löscht Auto Loader verarbeitete Dateien automatisch. **Verfügbar ab Databricks Runtime 16.4.**

---

## Drei Modi

| Modus | Verhalten |
|---|---|
| `OFF` | Standard; keine Dateien werden verschoben oder gelöscht. |
| `MOVE` | Dateien werden nach Ablauf der Retention an ein angegebenes Ziel verschoben. |
| `DELETE` | Dateien werden nach Ablauf der Retention gelöscht. |

```python
df = (spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.cleanSource", "MOVE")
  .option("cloudFiles.cleanSource.moveDestination", "s3://my-bucket/archive/landing/")
  .option("cloudFiles.cleanSource.retentionDuration", "14 days")
  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
  .load("s3://my-bucket/landing/"))
```

---

## Konfigurationsparameter

### `cloudFiles.cleanSource.retentionDuration`

- Standard: **30 Tage**.
- Format: CalendarInterval-Strings (z. B. `"14 days"`, `"2 weeks"`, `"1 month"`).
- Minimum bei `DELETE`: mindestens 7 Tage; bei `MOVE` kein Minimum.

### `cloudFiles.cleanSource.moveDestination`

- Nur erforderlich, wenn der Modus `MOVE` ist.
- Akzeptiert Cloud-Speicher- oder Unity-Catalog-Volume-Pfade.
- **Darf kein Kindverzeichnis des Quellverzeichnisses sein** — sonst würden die Dateien erneut aufgenommen.
- Muss in derselben External Location / demselben Volume / DBFS-Mount liegen. Verschiebungen über Buckets bzw. Container hinweg werden **nicht unterstützt** und führen zu einem Fehler.
- Auto Loader benötigt Schreibberechtigung auf dem Ziel. Liegen Quelle und Ziel in derselben External Location, dürfen keine benachbarten Managed-Storage-Verzeichnisse (Managed Volume/Catalog) vorliegen, da Auto Loader sonst keine Schreibberechtigung erhält.

### Auf Abschluss warten

- Standard: `false`.
- Verfügbar ab Databricks Runtime 19+.
- Erzwingt, dass Streams Cleanup-Operationen vor dem Beenden abschließen.

---

## Zeitpunkt des Cleanups

- Cleanup erfolgt **nur während aktiver Ingestion-Läufe mit neuen Dateien** — es gibt keinen von Streaming-Operationen unabhängigen Hintergrund-Cleanup.
- Dateien benötigen zwei Bedingungen: Ablauf der Retention-Dauer **und** ein gesetztes `commit_time` (im Lauf N+1 nach der Ingestion).
- Dateien werden frühestens im Lauf N+2 zu Cleanup-Kandidaten.

---

## Setting-Präzedenz

Ändert sich die Konfiguration zwischen Verarbeitung und Cleanup-Berechtigung, gilt die **aktuelle** Einstellung (z. B. Wechsel von `MOVE` zu `DELETE` löscht die Datei).

---

## Warnungen

- **Multi-Stream-Risiko:** `cloudFiles.cleanSource` sollte **nicht** aktiviert werden, wenn mehrere Auto-Loader-Streams oder andere Clients aus demselben Quellverzeichnis lesen — die Funktion setzt exklusiven Zugriff des Streams auf den Quellspeicherort voraus, da schnellere Streams Dateien löschen könnten, die langsamere noch nicht verarbeitet haben.
- **`foreachBatch`:** Werden Dateien über `foreachBatch` verarbeitet, gelten sie bereits als Verschiebe-/Lösch-Kandidaten, sobald der `foreachBatch`-Aufruf erfolgreich zurückkehrt — selbst wenn nur ein Teil der Batch-Dateien tatsächlich konsumiert wurde.
- Das Aktivieren der Funktion erhöht den Checkpoint-Overhead, ermöglicht aber Observability über die Tabellenfunktion `cloud_files_state` (Felder `archive_time`, `archive_mode`, `move_location` — siehe [13 Observability.md](13%20Observability.md)).

---

## Verschieben in kalten Speicher (Beispiel)

```python
.option("cloudFiles.cleanSource", "MOVE")
.option("cloudFiles.cleanSource.moveDestination", archive_path)
.option("cloudFiles.cleanSource.retentionDuration", "14 days")
```

Anschließend kann auf das Archiv-Verzeichnis eine Cloud-Lifecycle-Richtlinie angewendet werden (S3 Glacier, Azure Cool, GCS Coldline). Bei `DELETE` empfiehlt sich Bucket-Versionierung für Soft-Deletes.
