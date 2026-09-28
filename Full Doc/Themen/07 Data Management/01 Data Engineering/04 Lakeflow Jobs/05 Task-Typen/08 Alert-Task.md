# SQL-Alert-Task

Wertet einen Databricks-SQL-Alert als Teil eines Jobs aus — integriert Alert-basiertes Monitoring in Datenpipelines.

## Voraussetzungen

- Ein bestehender Databricks-SQL-Alert im Workspace.
- Mindestens `CAN RUN` auf dem Alert.
- Zugriff auf ein Serverless- oder Pro-SQL-Warehouse.

## Konfiguration

1. **Jobs & Pipelines** → **Create** → **Job**.
2. **Add another task type** → „SQL Alert" suchen und wählen.
3. Task-Namen eingeben.
4. Im **Alert**-Dropdown den auszuwertenden Alert wählen.
5. Optional **SQL warehouse** wählen (sonst wird das interne Warehouse des Alerts genutzt) — muss Serverless oder Pro sein.
6. Optional **Subscribers** für Ergebnisbenachrichtigungen wählen (sonst interne Subscriber des Alerts, falls vorhanden). Anpassung von Betreff/Inhalt der Benachrichtigung über die Notification-Vorlage des zugrunde liegenden Alerts.
7. Optional **Notifications** für Start/Abschluss/Fehlschlag des Tasks (E-Mail/Webhook).
8. Optional **Duration threshold**/**Retries**.
9. **Save task**.

## Verhalten

1. Die Alert-Query läuft auf dem angegebenen Warehouse.
2. Die Alert-Bedingung wird gegen das Ergebnis ausgewertet.
3. Konfigurierte Subscriber erhalten Benachrichtigungen je nach Ergebnis.

**Status:** „Succeeded" — Alert erfolgreich ausgewertet, unabhängig davon, ob die Bedingung ausgelöst wurde. „Failed" — Fehler bei der Auswertung (z. B. Warehouse-Verbindungsproblem, Query-Fehler).

Der SQL-Alert-Task wertet den Alert **unabhängig** vom eigenen Zeitplan des Alerts aus — dieser bleibt unberührt.

## Einschränkungen

- Keine Parameter-Unterstützung — für parametrisierte Queries stattdessen einen SQL-Task nutzen.
- Nur Databricks-SQL-Alerts unterstützt, keine Legacy-Alerts.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/alert
