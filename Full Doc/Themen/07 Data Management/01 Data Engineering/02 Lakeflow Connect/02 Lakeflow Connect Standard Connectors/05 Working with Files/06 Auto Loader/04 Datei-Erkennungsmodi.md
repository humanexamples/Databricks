# Auto Loader — Datei-Erkennungsmodi im Überblick

Quelle: [Compare Auto Loader file detection modes](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-detection-modes).

Auto Loader unterstützt zwei Modi zur Erkennung neuer Dateien: **Directory Listing** und **File Notification**. Auto Loader verwendet standardmäßig den Directory-Listing-Modus.

- Man kann die Datei-Erkennungsmodi über Stream-Neustarts hinweg wechseln und dabei weiterhin Exactly-once-Garantien für die Datenverarbeitung erhalten.
- Auto Loader garantiert **in keinem** der beiden Modi eine Reihenfolge, in der Dateien erkannt oder verarbeitet werden. Pipelines sollten so gestaltet sein, dass sie nicht-geordnet eintreffende Dateien handhaben können (siehe [00 Überblick.md](00%20Überblick.md), "Handle out-of-order data").

> *"Auto Loader does not guarantee the order in which files are discovered or processed, regardless of file detection mode."*

Databricks empfiehlt für die meisten Workloads den **File-Notification-Modus mit File Events** anstelle des Directory-Listing-Modus; File Notification mit File Events ist performanter und skalierbarer als Directory Listing. Wer Auto Loader aktuell im Directory-Listing-Modus betreibt, sollte laut Doku zu File Notification mit File Events migrieren (siehe [08 Migration zu File Events.md](08%20Migration%20zu%20File%20Events.md)).

**Ungeklärt:** Die genaue technische Begründung, *warum* File Notification performanter/skalierbarer ist als Directory Listing, wird auf der Vergleichsseite selbst nicht ausgeführt — nur die Tatsache wird festgestellt.

---

## Cloud-Speicher-Unterstützung je Modus

(Zweifach bestätigt, identische Tabelle auf AWS- und Azure-Spiegelseite.)

| Cloud-Speicher | Directory Listing | File Notification **ohne** File Events | File Notification **mit** File Events |
|---|---|---|---|
| AWS S3 | Alle Versionen | Alle Versionen | Ab Databricks Runtime 14.3 LTS |
| ADLS | Alle Versionen | Alle Versionen | Ab Databricks Runtime 14.3 LTS |
| GCS | Alle Versionen | Alle Versionen | Ab Databricks Runtime 14.3 LTS |
| Azure Blob Storage | Alle Versionen | Alle Versionen | **Nicht unterstützt** |
| DBFS | Alle Versionen | Nur für Mountpoints | Ab Databricks Runtime 14.3 LTS, sofern der DBFS-Mountpoint eine in Unity Catalog definierte External Location besitzt |
| Unity-Catalog-Volume | Ab Databricks Runtime 13.3 LTS | Nicht unterstützt | Ab Databricks Runtime 14.3 LTS |

**Wichtige Einschränkung:** Azure Blob Storage unterstützt den File-Events-Mechanismus **nicht** — dort bleibt nur Directory Listing oder klassische File Notification ohne File Events verfügbar.

---

## Directory Listing — Kurzüberblick

Directory-Listing-Modus erlaubt es, Auto-Loader-Streams schnell zu starten, ohne andere Berechtigungskonfigurationen als den Zugriff auf die Daten im Cloud-Speicher selbst. Ab Databricks Runtime 9.1 kann Auto Loader automatisch erkennen, ob Dateien in lexikalischer Reihenfolge im Cloud-Speicher eintreffen, und dadurch die Anzahl der zur Erkennung neuer Dateien benötigten API-Aufrufe erheblich reduzieren. Details: [05 Directory Listing Mode.md](05%20Directory%20Listing%20Mode.md).

## File Notification — Kurzüberblick

Im File-Notification-Modus richtet Auto Loader automatisch einen Benachrichtigungsdienst und einen Warteschlangendienst ein, der Datei-Ereignisse aus dem Eingabeverzeichnis abonniert. Sind File Events auf der External Location aktiviert, die die betreffenden Dateien enthält, müssen beim Einrichten des Auto-Loader-Streams keine zusätzlichen Berechtigungen angegeben werden. Details: [06 File Notification Mode.md](06%20File%20Notification%20Mode.md), [07 Wie File Events funktionieren.md](07%20Wie%20File%20Events%20funktionieren.md).

Vergleichstabelle (Setup / Skalierbarkeit / Kosten / Einsatzempfehlung): siehe [11 Best Practices.md](11%20Best%20Practices.md).
