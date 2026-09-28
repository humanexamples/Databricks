# File Notification Mode konfigurieren

Im File Notification Mode richtet Auto Loader automatisch Benachrichtigungs- und Warteschlangendienste ein, die Datei-Ereignisse aus Eingabeverzeichnissen überwachen. File Notification Mode ist schneller und skalierbarer als Directory-Listing-Ansätze und kann Millionen von Dateien pro Stunde verarbeiten.

<cell_type>markdown</cell_type>## Zwei Konfigurationsansätze

### 1. File Events (empfohlen)

Moderne File Events nutzen eine gemeinsame Benachrichtigungswarteschlange pro External Location, statt pro Stream eine eigene Warteschlange zu verwalten. Vorteile:

- Databricks übernimmt die Infrastruktureinrichtung, ohne zusätzliche Anmeldedaten zu benötigen.
- Reduziert die Komplexität der IAM-Rollen.
- Automatische Ressourcenanpassung ohne manuelle Parameterjustierung.
- Eingebautes Lifecycle-Management für Benachrichtigungen.

**Voraussetzungen:**

- Unity-Catalog-aktivierter Workspace
- Berechtigung zum Erstellen von Storage-Credential- und External-Location-Objekten in Unity Catalog
- Databricks Runtime 14.3 LTS oder neuer

**Konfiguration:** File Events auf der External Location aktivieren, dann `cloudFiles.useManagedFileEvents` in Auto-Loader-Streams auf `true` setzen.

### 2. Klassischer File Notification Mode

Hier verwaltet die Organisation einzelne Warteschlangen pro Stream. Auto Loader richtet automatisch einen Benachrichtigungs- und Warteschlangendienst ein, der Datei-Ereignisse der angegebenen Verzeichnisse abonniert.

## Nicht unterstützte Einstellungen bei File Events

Bei Nutzung von File Events werden folgende Parameter nicht unterstützt:

- `useIncremental`
- `useNotifications`
- `cloudFiles.fetchParallelism`
- `cloudFiles.backfillInterval`
- `cloudFiles.pathRewrites`
- `resourceTags`

## Cloud-Ressourcen je Anbieter

| Anbieter | Subscription | Queue | Ressourcen-Präfix | Limit |
| --- | --- | --- | --- | --- |
| Amazon S3 | AWS SNS | AWS SQS | databricks-auto-ingest | 100/Bucket |
| Azure (ADLS/Blob) | Event Grid | Queue Storage | databricks | 500/Konto |
| GCS | Google Pub/Sub | Google Pub/Sub | databricks-auto-ingest | 100/Bucket |

## Berechtigungsanforderungen

**Azure:** Contributor-Rolle, Storage Queue Data Contributor und EventGrid EventSubscription Contributor.

**S3:** Berechtigungen zur Verwaltung von SNS/SQS, Bucket-Benachrichtigungen und Warteschlangenoperationen.

**GCS:** Pub/Sub-Publisher-Rolle sowie diverse Berechtigungen zur Verwaltung von Subscriptions und Topics.

## Best Practices

- Für jeden Pfad bzw. jedes Unterverzeichnis ein separates externes Volume anlegen, um die Erkennungsperformance zu optimieren.
- Auto Loader mindestens einmal wöchentlich ausführen, um Cache-Ablauf zu verhindern.
- Pipelines so gestalten, dass sie mit außerhalb der Reihenfolge eintreffenden Dateien umgehen können – File Notification Mode mit File Events verbessert Kosten und Skalierbarkeit, garantiert aber keine Zustellreihenfolge.

<cell_type>markdown</cell_type>---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-notification-mode  
**Stand:** 2026-08-09
