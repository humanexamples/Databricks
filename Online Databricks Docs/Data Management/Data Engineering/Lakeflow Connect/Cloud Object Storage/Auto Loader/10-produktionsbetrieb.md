# Auto Loader im Produktionsbetrieb

Databricks empfiehlt, Auto Loader für inkrementelle Ingestion innerhalb von Lakeflow-Pipelines einzusetzen. Das bietet autoskalierende Compute-Infrastruktur für Kosteneinsparungen sowie automatische Behandlung von Schema Evolution.

## Empfohlene Komponenten im Produktivbetrieb

- Autoskalierende Compute-Infrastruktur
- Datenqualitätsprüfungen mit Expectations
- Automatische Behandlung von Schema Evolution
- Monitoring über Metriken im Event-Log

Alternative für Workloads ohne Niedriglatenz-Anforderung, bei denen Kostenreduktion im Vordergrund steht: Auto Loader als getriggerten Batch-Job mit `Trigger.AvailableNow` planen.

## Auto Loader überwachen

**Cloud-Files-State-Abfrage:** Die Funktion `cloud_files_state` (ab Databricks Runtime 11.3) ermöglicht die SQL-Inspektion des Stream-Status:

```sql
%sql
SELECT * FROM cloud_files_state('path/to/checkpoint');
```

**Streaming Query Listener:** Der Backlog lässt sich über Metriken wie `numFilesOutstanding` und `numBytesOutstanding` im Raw-Data-Tab des Streaming-Query-Progress-Dashboards überwachen.

Ab Runtime 10.4 liefert der File Notification Mode zusätzlich `approximateQueueSize`-Metriken für AWS und Azure.

## Kostenoptimierung

**Dateierkennungsmodi:**

- Niedrige Latenz: Auto Loader mit File Events (eine Queue pro Bucket, inkrementelle Erkennung)
- Sehr latenzsensitiv: Klassischer File Notification Mode (direktes Lesen der Cloud-Queue)

**Batch-Verarbeitung:** Geplante Batch-Jobs senken die Rechenkosten gegenüber kontinuierlichen Triggern wie `Trigger.ProcessingTime`.

## Aufbewahrung der Quelldaten (ab Runtime 16.4)

**Archivierungsstrategie:** `cloudFiles.cleanSource` mit der Option `MOVE` konfigurieren, um verarbeitete Dateien automatisch zu verschieben. Anforderungen:

- Quelle und Ziel im selben Bucket/Container
- Ziel kann ein Volume-Pfad sein
- Keine benachbarten Managed-Storage-Verzeichnisse

**Migration in Cold Storage:** Dateien in Archivverzeichnisse verschieben und anschließend Cloud-Lifecycle-Richtlinien anwenden, um sie in günstigere Speicherklassen zu überführen (S3 Glacier, Azure Cool/Archive).

## Rate Limiting mit Trigger.AvailableNow

Standardmäßig verarbeitet Auto Loader maximal 1.000 Dateien pro Micro-Batch. Begrenzung über:

- `cloudFiles.maxFilesPerTrigger` (harte Grenze)
- `cloudFiles.maxBytesPerTrigger` (weiche Grenze)

Sind beide angegeben, verarbeitet Auto Loader so viele Dateien, wie nötig sind, um eine der beiden Grenzen zu erreichen.

## Checkpoint-Verwaltung

Den Checkpoint-Speicherort auf Systemen ohne Lifecycle-Richtlinien ablegen. Dateibereinigungsrichtlinien beschädigen den Stream-Zustand und erfordern einen Neustart.

## File-Event-Tracking

Die RocksDB-Zustandsverwaltung garantiert Exactly-once-Verarbeitung. Ab Runtime 15.4 wird der Start optimiert, indem ein vollständiger Zustands-Download vermieden wird.

**Datei-Ablaufzeit:** `cloudFiles.maxFileAge` konservativ setzen (mindestens 14 Tage, empfohlen 90 Tage), um Duplikate oder übersehene Dateien zu vermeiden.

**Backfill-Trigger:** Mit `cloudFiles.backfillInterval` regelmäßige asynchrone Backfills einrichten, um verpasste Benachrichtigungen ohne Duplikate zu berücksichtigen.

**Ausführungsfrequenz:** Bei Nutzung von File Events die Auto-Loader-Streams mindestens einmal alle 7 Tage ausführen, um die inkrementelle Erkennung aufrechtzuerhalten.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/production  
**Stand:** 2026-08-07
