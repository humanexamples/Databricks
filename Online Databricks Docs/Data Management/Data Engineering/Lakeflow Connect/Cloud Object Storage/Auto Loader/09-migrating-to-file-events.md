# Migration zu File Events

Diese Seite beschreibt, wie bestehende Auto-Loader-Streams von Directory Listing oder klassischen Notifications auf den File-Events-Modus migriert werden.

## Migration von Directory Listing

Der Prozess umfasst fünf Schritte: Voraussetzungen für File Events prüfen, Einrichtung der External Location bestätigen, Stream-Code anpassen (`cloudFiles.useManagedFileEvents` auf `true` setzen), nicht unterstützte Einstellungen entfernen und den Stream neu starten. Beim ersten Lauf mit aktivierten File Events führt Auto Loader eine Verzeichnisauflistung durch, um mit dem File-Events-Cache auf den aktuellen Stand zu kommen.

Für ein Zurücksetzen wird die Option für Managed File Events entfernt und der Stream neu gestartet.

## Migration von klassischen Notifications (S3)

Bei S3-Migrationen ist wegen AWS-Einschränkungen besondere Vorsicht geboten: S3 erlaubt keine Event-Notification-Konfigurationen mit überlappenden Präfixen.

**Schritte:**

1. Stream stoppen
2. Bestehende Benachrichtigungsressourcen über `CloudFilesAWSResourceManager` abbauen
3. Voraussetzungen bestätigen
4. `cloudFiles.useManagedFileEvents` aktivieren
5. Nicht unterstützte Einstellungen entfernen
6. Cloud-spezifische Optionen wie `cloudFiles.queueUrl` entfernen
7. Stream neu starten

Um zu klassischen Notifications zurückzukehren: File Events deaktivieren, die Managed-File-Events-Option entfernen, `cloudFiles.useNotifications` aktivieren und die erforderlichen Authentifizierungsparameter ergänzen.

## Migration von klassischen Notifications (Azure/GCP)

Bei diesen Plattformen ist vor der Migration keine Bereinigung von Ressourcen nötig. Die Schritte entsprechen dem S3-Prozess, jedoch ohne den vorherigen Abbau-Schritt. Nach der Migration sollten Administratoren die Notification-Ressourcen über die jeweilige API entfernen.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/migrating-to-file-events  
**Stand:** 2026-08-07
