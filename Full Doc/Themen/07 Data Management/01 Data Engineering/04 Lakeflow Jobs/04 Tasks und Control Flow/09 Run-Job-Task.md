# Run-Job-Task: andere Jobs auslösen

Der **Run Job**-Task löst einen anderen, im Workspace konfigurierten Job aus.

**Wichtig:** Zirkuläre Abhängigkeiten (Job A löst Job B aus, Job B löst Job A aus, direkt oder indirekt) sowie mehr als drei verschachtelte Run-Job-Tasks werden nicht unterstützt — Databricks kann das Deployment solcher Muster in künftigen Releases blockieren.

## Konfiguration

1. Tab **Tasks** → **Add task**.
2. Task-Namen eingeben.
3. Typ **Run Job**.
4. Job aus dem Dropdown wählen (durchsuchbar).
5. Optional Job-Parameter zum Überschreiben der Standardwerte des Ziel-Jobs setzen.
6. Optional Retries, Laufdauer-/Streaming-Backlog-Schwellen oder Benachrichtigungen unter Advanced Task Settings konfigurieren.
7. **Save task**.

Für Bearbeiten, Klonen, Deaktivieren oder Löschen siehe `Task konfigurieren.md`.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/run-job
