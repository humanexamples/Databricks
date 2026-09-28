# Auto Loader — Produktionsbetrieb: Kosten, Retention, Rate Limiting

Quelle: [Configure Auto Loader for production workloads](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/production).

Databricks empfiehlt, Auto Loader in Lakeflow-Pipelines für inkrementelle Datenaufnahme zu verwenden. Vorteile: Autoscaling, Datenqualitätsprüfungen (Expectations), automatisches Schema-Evolution-Handling, Event-Log-Monitoring.

---

## Monitoring in der Produktion

Über die Tabellenfunktion `cloud_files_state` lassen sich Metadaten zu Dateien finden, die von einem Auto-Loader-Stream entdeckt wurden (Details: [13 Observability.md](13%20Observability.md)):

```sql
SELECT * FROM cloud_files_state('path/to/checkpoint');
```

Auto Loader meldet bei jedem Batch Metriken an den Streaming Query Listener; Metriken wie `numFilesOutstanding` und `numBytesOutstanding` erscheinen im "Raw Data"-Tab. `approximateQueueSize` ist nur im File-Notification-Modus verfügbar (ab Databricks Runtime 10.4 LTS).

---

## Kostenüberlegungen

Die Hauptkostenquellen sind Compute-Ressourcen und Datei-Erkennung. Wird keine Anforderung an niedrige Latenz gestellt, sollten `Trigger.AvailableNow`-Batch-Jobs (mit Lakeflow Jobs) statt Continuous-Triggern verwendet werden.

- **Niedrige Latenz:** File Events (eine Queue, inkrementelle Erkennung).
- **Ultra-latenzkritisch:** klassischer File-Notification-Modus.

---

## Aufbewahrung der Quelldaten

Sammeln sich Dateien im Quellverzeichnis an, steigen die Speicherkosten, und die Datei-Erkennung wird langsamer.

Die Option `cloudFiles.cleanSource` (ab Databricks Runtime 16.4) ermöglicht automatisches Datei-Management mit den Modi `MOVE` oder `DELETE`:

```python
.option("cloudFiles.cleanSource", "MOVE")
.option("cloudFiles.cleanSource.moveDestination", archive_path)
.option("cloudFiles.cleanSource.retentionDuration", "14 days")
```

Anschließend Cloud-Lifecycle-Richtlinien anwenden (S3 Glacier, Azure Cool, GCS Coldline). Vollständige Referenz und Einschränkungen: [10 Clean Source (Quelldateien aufräumen).md](10%20Clean%20Source%20%28Quelldateien%20aufräumen%29.md).

---

## `Trigger.AvailableNow` und Rate Limiting

Der `AvailableNow`-Trigger weist Auto Loader an, alle Dateien zu verarbeiten, die vor dem Start der Abfrage eingetroffen sind. Auto Loader verarbeitet standardmäßig maximal **1000 Dateien pro Micro-Batch**:

- `cloudFiles.maxFilesPerTrigger`: harte Grenze.
- `cloudFiles.maxBytesPerTrigger`: weiche Grenze (Bytes können überschritten werden).

Details: [09 Datei-Tracking und Checkpoints.md](09%20Datei-Tracking%20und%20Checkpoints.md).

---

## Checkpoint-Speicherort und Datei-Zustandsverfolgung

- Checkpoint-Speicherort **ohne** Cloud-Objekt-Lifecycle-Richtlinie betreiben — Löschen von Checkpoint-Dateien beschädigt den Stream-Zustand.
- Auto Loader verfolgt entdeckte Dateien am Checkpoint-Speicherort mittels **RocksDB**, um Exactly-once-Ingestion-Garantien zu bieten.
- Der Minimalwert für `cloudFiles.maxFileAge` zur Begrenzung des Zustandswachstums ist `"14 days"` (90 Tage empfohlen).
- Ab **Databricks Runtime 15.4 LTS** asynchrones State-Loading — beschleunigt den Stream-Start bei großen Checkpoint-Zuständen.

---

## Regelmäßige Backfills

`cloudFiles.backfillInterval` setzen, um asynchrone Backfills in einem festgelegten Intervall auszulösen (verursacht keine Duplikate). Bei File Events nicht nötig — dort automatisch.

---

## Stream mindestens alle 7 Tage ausführen (bei File Events)

Wird der Stream so häufig ausgeführt, bleibt die Datei-Erkennung inkrementell (technische Begründung: [07 Wie File Events funktionieren.md](07%20Wie%20File%20Events%20funktionieren.md)).
