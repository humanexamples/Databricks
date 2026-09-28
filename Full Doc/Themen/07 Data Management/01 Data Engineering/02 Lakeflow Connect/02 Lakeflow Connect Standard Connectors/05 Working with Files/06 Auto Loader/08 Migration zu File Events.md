# Auto Loader — Migration zu File Events

Quelle: [Migrating to file events](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/migrating-to-file-events).

Für die Vorteile von File Events (Performance, Skalierbarkeit, geringere Kosten) siehe [04 Datei-Erkennungsmodi.md](04%20Datei-Erkennungsmodi.md) und [07 Wie File Events funktionieren.md](07%20Wie%20File%20Events%20funktionieren.md).

---

## Migration von Directory Listing

1. Prüfen, dass die Voraussetzungen für File Events erfüllt sind (siehe [06 File Notification Mode.md](06%20File%20Notification%20Mode.md)).
2. Prüfen, dass sich der Ladepfad in einer External Location mit aktivierten File Events befindet.
3. Den Stream-Code anpassen, um `cloudFiles.useManagedFileEvents` auf `true` zu setzen. **Denselben Checkpoint-Speicherort weiterverwenden.**
4. Nicht unterstützte Einstellungen aus dem Stream-Code entfernen (siehe Tabelle in [06 File Notification Mode.md](06%20File%20Notification%20Mode.md)).
5. Den Stream neu starten — beim ersten Lauf mit aktivierten File Events führt Auto Loader eine Verzeichnisauflistung durch, um mit dem File-Events-Cache auf den aktuellen Stand zu kommen.

**Rollback:** Die Option `cloudFiles.useManagedFileEvents` aus dem Stream-Code entfernen und den Stream neu starten.

---

## Migration von klassischen File Notifications

### S3-Quelldaten — Besonderheit

S3 erlaubt **keine** Ereignis-Benachrichtigungskonfigurationen mit überlappenden Präfixen. Bestehende Notification-Setups müssen daher vor dem Aktivieren von File Events entfernt werden.

**Klassisch → File Events (S3):**

1. Den Auto-Loader-Stream stoppen und die zugehörigen Benachrichtigungsressourcen abbauen (z. B. über die `tearDownNotificationResources`-API von `CloudFilesAWSResourceManager`).
2. Voraussetzungen für File Events prüfen.
3. Prüfen, dass die External Location File Events aktiviert hat.
4. `cloudFiles.useManagedFileEvents` auf `true` setzen.
5. Nicht unterstützte Einstellungen und cloud-spezifische Optionen entfernen (z. B. `cloudFiles.queueUrl`, `databricks.serviceCredential`, `cloudFiles.awsAccessKey`).
6. Den Stream neu starten.

**File Events → Klassisch (S3):**

1. Den Stream stoppen und File Events für die External Location über die UI deaktivieren.
2. Die Option `cloudFiles.useManagedFileEvents` entfernen.
3. Die Option `cloudFiles.useNotifications` auf `true` setzen.
4. Die erforderlichen cloud-spezifischen Optionen wieder hinzufügen (`cloudFiles.queueUrl`, Zugangsdaten).
5. Den Stream neu starten.

Databricks empfiehlt, das vorherige Setup abzubauen und ein neues Queue-Setup anzulegen, um verpasste Dateien zu vermeiden.

### Azure/GCP-Quelldaten

**Klassisch → File Events (Azure, GCP):**

1. Voraussetzungen prüfen.
2. `cloudFiles.useManagedFileEvents` auf `true` setzen.
3. Nicht unterstützte Einstellungen und cloud-spezifische Notification-Optionen entfernen (z. B. `cloudFiles.queueName`, `cloudFiles.subscription`, `databricks.serviceCredential`, `cloudFiles.privateKey`, `cloudFiles.clientSecret`).
4. Den Stream neu starten.
5. Die im klassischen Modus angelegten Benachrichtigungsressourcen über die `tearDownNotificationResources`-API entfernen.

**File Events → Klassisch (Azure, GCP):**

1. Die Option `cloudFiles.useManagedFileEvents` entfernen.
2. `cloudFiles.useNotifications` auf `true` setzen.
3. Die cloud-spezifischen Notification-Optionen wieder hinzufügen (`cloudFiles.queueName` / `cloudFiles.subscription`, Zugangsdaten).
4. Den Stream neu starten.

---

**Hinweis:** Die Migrationsseite besteht aus Prosa-Schritten, die auf Optionen aus [06 File Notification Mode.md](06%20File%20Notification%20Mode.md) verweisen; eigenständige Python-/SQL-Codebeispiele enthält sie nicht.
