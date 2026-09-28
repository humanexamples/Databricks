# File Events erklärt

Die Option `cloudFiles.useManagedFileEvents` von Auto Loader nutzt Datei-Ereignis-Benachrichtigungen der Cloud-Anbieter zur effizienten Dateierkennung. Das System verarbeitet Benachrichtigungen z. B. von Amazon S3 und cached Dateimetadaten – so kann Auto Loader Dateien erkennen, ohne wiederholt Verzeichnisse zu scannen.

## Funktionsweise

Der Mechanismus besteht aus drei Phasen:

1. **Cloud-Speicher-Ereignisse:** Cloud-Container veröffentlichen Benachrichtigungen, wenn Dateien erstellt oder geändert werden (z. B. S3-Events an SNS-Topics, mit SQS-Queues für die asynchrone Verarbeitung).
2. **Managed-File-Events-Dienst:** Der Dienst von Databricks lauscht auf diese Ereignisse und pflegt einen Dateimetadaten-Cache – alternativ können eigene Cloud-Ressourcen konfiguriert werden.
3. **Inkrementelle Erkennung:** Läuft ein Stream mit `cloudFiles.useManagedFileEvents = true` zum ersten Mal, führt Auto Loader eine vollständige Verzeichnisauflistung durch, um einen Checkpoint zu erstellen; danach werden die zwischengespeicherten Daten für nachfolgende Läufe genutzt.

## File Events vs. klassischer Modus

Der File-Events-Modus nutzt ein einziges gemeinsames SNS-Topic und eine SQS-Queue für mehrere Konsumenten (Auto Loader, Trigger), während der klassische Modus separate Subscriptions pro Konsument benötigt. Das vermeidet Limits bei Benachrichtigungen pro Bucket.

## Auslöser für vollständige Verzeichnisauflistungen

Auto Loader führt vollständige Verzeichnisscans durch:

- beim Start eines neuen Streams
- bei der Migration von anderen Modi
- wenn der Stream mehr als sieben Tage nicht gelaufen ist
- bei Änderungen der External-Location-Konfiguration

Der Dienst selbst scannt zusätzlich alle 24 Stunden erneut, um sicherzustellen, dass keine Dateien übersehen wurden.

## Best Practices

- **Volumes verwenden:** Für jeden Pfad bzw. jedes Unterverzeichnis ein externes Volume anlegen, um die Erkennungsperformance zu verbessern.
- **Ereignisgesteuerte Verarbeitung:** File-Arrival-Trigger statt kontinuierlicher Pipelines nutzen, für bessere Ressourceneffizienz.
- **Trigger-Intervalle:** Bei Continuous-Triggern ein Intervall von mindestens 1 Minute setzen, um die Abfragefrequenz zu reduzieren.

## Einschränkungen

Auto Loader unterstützt keine Pfad-Neuschreibungen (Path Rewrites), und die Caching-Schicht fügt im Vergleich zum klassischen File Notification Mode bei sehr latenzsensitiven Szenarien zusätzliche Latenz hinzu.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-events-explained  
**Stand:** 2026-08-07
