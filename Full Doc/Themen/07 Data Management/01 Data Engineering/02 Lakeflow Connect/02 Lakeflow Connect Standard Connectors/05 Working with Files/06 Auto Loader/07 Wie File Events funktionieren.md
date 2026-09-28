# Auto Loader — Wie File Events technisch funktionieren

Quelle: [Auto Loader with file events explained](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-events-explained).

Auto Loader mit File Events nutzt die von Cloud-Providern bereitgestellte Datei-Ereignis-Benachrichtigungsfunktionalität über einen Drei-Phasen-Mechanismus.

---

## Diagramme aus der Doku

![Cloud storage event notification systems](https://docs.databricks.com/aws/en/assets/images/cloud-storage-event-notification-systems-dfa53e36957ad28b1c038182a76a64fc.png)

![Auto Loader with file events](https://docs.databricks.com/aws/en/assets/images/auto-loader-with-file-events-a22c49fbd36146c6bc2be943e51213c0.png)

![Side-by-side diagram comparing file events mode (left) and classic file notifications mode (right).](https://docs.databricks.com/aws/en/assets/images/file-events-vs-classic-file-events-761dedde768661a357b53a42602e862c.png)

---

## Drei-Phasen-Mechanismus

1. **Cloud-Speicher-Ereignisse:** Cloud-Speicher-Container lassen sich so konfigurieren, dass sie bei Datei-Ereignissen wie Neuerstellung und Änderung Benachrichtigungen veröffentlichen. Cloud-Anbieter (z. B. S3) routen diese Benachrichtigungen über SNS-Topics an verwaltete Queues wie SQS.
2. **Managed-File-Events-Dienst:** Databricks File Events ist ein Dienst, der Cloud-Ressourcen einrichtet, um auf Datei-Ereignisse zu lauschen. Der Dienst "cacht" Datei-Metadaten und etabliert eine Leseposition innerhalb dieses Caches, die im Checkpoint des Streams gespeichert wird.
3. **Inkrementelle Erkennung:** Auto Loader verwendet diesen Cache zur Datei-Erkennung, wenn es mit `cloudFiles.useManagedFileEvents` auf `true` ausgeführt wird. Nachfolgende Läufe erkennen neue Dateien, indem sie direkt aus dem File-Events-Cache anhand der gespeicherten Leseposition lesen — ohne Verzeichnisauflistung.

> *"[Auto Loader] discovers new files by reading directly from the file events cache using the stored read position and do not require directory listing."*

---

## Wann führt Auto Loader mit File Events eine Verzeichnisauflistung durch?

Auto Loader führt eine vollständige Verzeichnisauflistung durch:

- beim Start eines neuen Streams;
- bei Migration eines Streams von Directory Listing oder klassischen File Notifications;
- wenn Auto Loader mit File Events länger als **sieben Tage** nicht ausgeführt wird;
- bei Änderungen an der External-Location-Konfiguration, die die Leseposition von Auto Loader ungültig machen (File Events deaktivieren/aktivieren, Pfad-Änderungen, Queue-Änderungen);
- auch wenn `includeExistingFiles` auf `false` gesetzt ist, führt der erste Lauf immer eine vollständige Auflistung durch, um die Basis-Leseposition zu etablieren.

---

## 24-Stunden-Regel

Der Databricks-Dienst führt vollständige Verzeichnisauflistungen auf der External Location durch, um zu verifizieren, dass keine Dateien übersehen wurden. Der erste Scan beginnt unmittelbar beim Aktivieren von File Events. **Jede nachfolgende Auflistung erfolgt 24 Stunden nach dem letzten vollständigen Scan**, solange mindestens ein Auto-Loader-Stream File Events zur Datenaufnahme verwendet.

---

## Verpasste Dateien bei fehlkonfigurierter Queue

Bei einer fehlkonfigurierten File-Events-Queue liest Auto Loader weiterhin aus dem File-Events-Cache und nimmt automatisch alle während der Fehlkonfiguration verpassten Dateien auf.
