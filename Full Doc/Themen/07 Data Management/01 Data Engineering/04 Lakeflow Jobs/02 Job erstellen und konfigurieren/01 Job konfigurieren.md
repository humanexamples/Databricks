# Jobs konfigurieren und bearbeiten

Jobs lassen sich über die Jobs-&-Pipelines-Workspace-UI erstellen und konfigurieren — alternativ über Databricks CLI, REST API, Declarative Automation Bundles oder zeitgesteuerte Notebook-Jobs.

## Minimale Job-Konfiguration

Jeder Job benötigt:

- einen Task mit ausführbarer Logik (z. B. ein Notebook),
- eine Compute-Ressource (Serverless, Classic Jobs Compute oder All-Purpose Compute),
- einen Zeitplan oder manuelle Auslösung,
- einen eindeutigen Namen.

## Neuen Job erstellen

1. **Jobs & Pipelines** in der Sidebar.
2. **Create** → **Job**.
3. **Notebook**-Kachel wählen.
4. Task-Namen und Notebook-Pfad eingeben.
5. Task speichern.

Der Job erhält standardmäßig einen Namen wie „New Job \<Datum\> \<Uhrzeit\>"; weitere Tasks lassen sich ergänzen. Jobs mit mehr als 100 Tasks benötigen ggf. besondere Konfiguration (siehe `Grosse Jobs.md`).

## Bestehende Jobs bearbeiten

Über **Jobs & Pipelines** lassen sich im Seitenpanel u. a. bearbeiten:

- Zeitpläne und Trigger
- Job-Parameter
- Compute-Konfiguration
- Tags und Benachrichtigungen
- Limits gleichzeitiger Läufe
- Git-Einstellungen
- Job-Berechtigungen (bei aktivierter Zugriffskontrolle)

## Job-Parameter

Auf Job-Ebene konfigurierte Parameter werden an Tasks weitergereicht, die sie akzeptieren — auch an Python-Wheel-Dateien als Keyword-Argumente (siehe `07 Parameter/`).

## Job-Tags

Tags dienen als nicht-sensible Labels bzw. Schlüssel-Wert-Attribute zum Filtern und Monitoring. Sie vererben sich an Job-Cluster und lassen sich ins Cluster-Monitoring integrieren. **Wichtig:** keine sensiblen Informationen wie PII oder Passwörter in Tags speichern.

## Git-Integration

Jobs können Quellcode direkt aus einem Remote-Git-Repository auschecken, mit Sparse-Checkout-Option für große Repositories (siehe `Git-Integration.md`).

## Job-Verwaltung

- **Umbenennen:** Jobnamen anklicken, neuen Namen eingeben.
- **Klonen:** Kebab-Menü neben „Run now" → **Clone job** → Namen eingeben, bestätigen. Erstellt eine identische Kopie (außer der Job-ID).
- **Löschen:** Kebab-Menü → **Delete job**.

## Dauer- und Streaming-Metriken

Optionale Schwellenwerte für Laufdauer oder Streaming-Backlog: Erwartete Fertigstellungszeit löst eine Warnung aus, eine maximale Fertigstellungszeit führt zum Status „Timed Out". Streaming-Metrik-Schwellen können Benachrichtigungen auslösen.

## Job-Run-Queueing

Standardmäßig für über die UI erstellte Jobs seit dem 15. April 2024 aktiviert: Läufe werden bei Erreichen von Concurrency-Limits nicht übersprungen, sondern bis zu 48 Stunden in eine Warteschlange gestellt.

## Gleichzeitige Läufe

Standard-Maximum für neue Jobs ist **1**. Einstellbar über **Edit concurrent runs** in den Advanced Settings — Werte über 1 erlauben überlappende oder parametrisierte parallele Läufe.

## Quelle

- https://docs.databricks.com/aws/en/jobs/configure-job
