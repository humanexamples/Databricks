# Dashboard-Task

Aktualisiert die Ergebnisse eines veröffentlichten Databricks-Dashboards als Teil eines Job-Workflows.

## Voraussetzungen

- Dashboard muss veröffentlicht und für den konfigurierenden Nutzer zugänglich sein.
- Mindestens `CAN VIEW` auf dem Dashboard für das Deployment.

## Konfiguration

1. Tab **Tasks** → Task-Namen eingeben.
2. Typ **Dashboard**.
3. Zu aktualisierendes Dashboard im Dropdown wählen.
4. Optional SQL-Warehouse für den Refresh wählen (Serverless oder Pro erforderlich).
5. Optional Subscriber für E-Mail-Benachrichtigungen wählen.
6. Optional **Dashboard filters** konfigurieren: **Add filter** → Filter-Widget des Dashboards wählen → Wert eingeben.
7. Optional Duration Threshold, Notifications oder Retries in den Advanced Task Settings.
8. **Save task**.

## Ausführung und Zugriff

Abhängig von der Veröffentlichungsart:

- **Mit Shared-Data-Permissions:** Betrachter greifen mit den Credentials des Dashboard-Publishers auf Daten zu.
- **Ohne Shared-Data-Permissions:** Die „Run as"-Identität des Jobs (standardmäßig der Job-Eigentümer) aktualisiert das Dashboard.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/dashboard
