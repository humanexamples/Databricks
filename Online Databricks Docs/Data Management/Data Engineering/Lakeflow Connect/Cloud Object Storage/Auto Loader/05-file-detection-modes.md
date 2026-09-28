# Dateierkennungsmodi in Auto Loader

Auto Loader bietet zwei unterschiedliche Ansätze, um neue Dateien im Cloud-Speicher zu erkennen. Der Modus lässt sich über Stream-Neustarts hinweg wechseln, während die Exactly-once-Verarbeitungsgarantie erhalten bleibt.

## Directory Listing Mode

Dies ist der Standardansatz von Auto Loader. Das System erkennt neue Dateien, indem es das Eingabeverzeichnis scannt – dafür sind lediglich Cloud-Speicher-Zugriffsrechte nötig.

Ab Databricks Runtime 9.1 kann Auto Loader automatisch erkennen, ob Dateien in lexikalischer Reihenfolge im Cloud-Speicher ankommen, und dadurch die Anzahl der zur Erkennung neuer Dateien benötigten API-Aufrufe deutlich reduzieren.

## File Notification Mode (empfohlen)

Dieser Ansatz nutzt Benachrichtigungs- und Warteschlangendienste der Cloud-Infrastruktur. Das System abonniert automatisch Datei-Ereignisse des Zielverzeichnisses. Sind File Events für die betreffende External Location aktiviert, sind keine zusätzlichen Berechtigungen nötig.

File Notification Mode mit File Events ist performanter und skalierbarer als Directory Listing. Databricks empfiehlt, bestehende Directory-Listing-Implementierungen auf File Notification Mode zu migrieren, um die Performance zu verbessern.

## Unterstützung nach Cloud-Anbieter

- **AWS S3, ADLS, GCS:** Unterstützen alle drei Modi (Directory Listing, File Notifications ohne Events, File Notifications mit Events).
- **Azure Blob Storage:** Unterstützt nur Directory Listing und File Notifications ohne Events.
- **DBFS & Unity-Catalog-Volumes:** Unterstützung variiert je nach Runtime-Version und Konfiguration.

File Notifications mit Events erfordern Databricks Runtime 14.3 LTS oder höher – für AWS S3, ADLS und GCS.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-detection-modes  
**Stand:** 2026-08-07
