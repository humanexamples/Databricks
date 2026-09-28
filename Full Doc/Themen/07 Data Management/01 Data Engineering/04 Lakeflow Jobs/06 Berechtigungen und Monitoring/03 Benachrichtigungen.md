# Benachrichtigungen für Jobs

Benachrichtigungen lassen sich für Job-Läufe und einzelne Tasks bei folgenden Ereignissen einrichten: Start, erfolgreicher Abschluss, Fehlschlag, Überschreitung eines Laufdauer-Schwellenwerts, Überschreitung eines Streaming-Backlog-Schwellenwerts. Ziele: E-Mail-Adressen oder Drittanbieter (Slack, Microsoft Teams, PagerDuty, Webhooks).

## Drittanbieter-Ziele einrichten

Ein Admin konfiguriert System-Ziele über die Admin-Einstellungen: **Edit system notifications** → **Create new destination**. Maximal drei System-Ziele je Benachrichtigungsereignis pro Job/Task.

**Hinweis:** Externe Systeme wie Amazon SES/SNS lassen sich über E-Mail-Benachrichtigungen integrieren. Der Inhalt von Slack-/Teams-Nachrichten kann sich in künftigen Releases ändern — für feste Schema-Anforderungen einen benutzerdefinierten Webhook konfigurieren.

## Benachrichtigungen konfigurieren

**Zu beachten:**

- Job-Level-Benachrichtigungen werden bei Retries fehlgeschlagener Tasks **nicht** gesendet — dafür Task-Benachrichtigungen nutzen.
- Maximal drei System-Ziele je Ereignistyp pro Job/Task.
- Läufe im Status „Succeeded with failures" gelten als erfolgreich — für Benachrichtigungen **Success** wählen.
- Für Laufdauer-Schwellen-Benachrichtigungen muss ein Duration Limit gesetzt sein.

**Benötigtes Privileg:** `CAN MANAGE` oder `IS OWNER` auf dem Job.

**Schritte:**

1. Job-Details-Panel → Abschnitt **Job notifications** → **Edit notifications**.
2. **Add notification** unten links.
3. Ziel wählen: E-Mail-Adresse oder System-Ziel.
4. Ereignistypen ankreuzen: Start, Success, Failure, Duration warning, Streaming backlog.
5. Weitere Ziele analog hinzufügen.
6. **Save**.

Zum Entfernen: **Edit notifications** → Papierkorb-Icon → speichern.

## Benachrichtigungen für langsame Jobs

Bei konfigurierter erwarteter Laufdauer: **Duration Warning** beim Hinzufügen/Bearbeiten einer Benachrichtigung wählen.

Für Streaming-Backlog-Metriken: Benachrichtigung, wenn der durchschnittliche Backlog über 10 Minuten den Schwellenwert überschreitet; eine 30-Minuten-Wartezeit verhindert zu viele Nachrichten, danach alle 30 Minuten erneute Updates, solange der Backlog hoch bleibt.

**Hinweis:** Streaming-Backlog-Benachrichtigungen setzen voraus, dass der Jobs-Service die aktive Streaming-Query verfolgen kann — `awaitTermination()` in Jobs vermeiden.

## Benachrichtigungen für übersprungene/abgebrochene Läufe filtern

- „Mute notifications for skipped runs"
- „Mute notifications for canceled runs"

Für Task-Benachrichtigungen: „Mute notifications until the last retry" (Tasks werden standardmäßig dreimal wiederholt). Job-Level-Filterung filtert **nicht** automatisch Task-Level-Benachrichtigungen — getrennt konfigurieren.

## HTTP-Webhook-Payloads

| `event_type`-Code | Ausgelöst bei |
|---|---|
| `jobs.on_start` | Laufstart |
| `jobs.on_success` | Abschluss in Status „successful" oder „succeeded with failures" |
| `jobs.on_failure` | Abschluss in nicht erfolgreichem Status |
| `jobs.on_duration_warning_threshold_exceeded` | Überschreitung des konfigurierten Laufdauer-Schwellenwerts |

**Beispiel — Job-Run-Start:**

```json
{
  "event_type": "jobs.on_start",
  "workspace_id": "your_workspace_id",
  "run": {
    "run_id": "run_id"
  },
  "job": {
    "job_id": "job_id",
    "name": "job_name"
  }
}
```

**Beispiel — Task-Run-Start:**

```json
{
  "event_type": "jobs.on_start",
  "workspace_id": "your_workspace_id",
  "task": {
    "task_key": "task_name"
  },
  "run": {
    "run_id": "run_id_of_task",
    "parent_run_id": "run_id_of_parent_job_run"
  },
  "job": {
    "job_id": "job_id",
    "name": "job_name"
  }
}
```

**Beispiel — Job-Run-Fehlschlag:**

```json
{
  "event_type": "jobs.on_failure",
  "workspace_id": "your_workspace_id",
  "run": {
    "run_id": "run_id"
  },
  "job": {
    "job_id": "job_id",
    "name": "job_name"
  }
}
```

**Beispiel — Task-Run-Erfolg:**

```json
{
  "event_type": "jobs.on_success",
  "workspace_id": "your_workspace_id",
  "task": {
    "task_key": "task_name"
  },
  "run": {
    "run_id": "run_id_of_task",
    "parent_run_id": "run_id_of_parent_job_run"
  },
  "job": {
    "job_id": "job_id",
    "name": "job_name"
  }
}
```

## Quelle

- https://docs.databricks.com/aws/en/jobs/notifications
