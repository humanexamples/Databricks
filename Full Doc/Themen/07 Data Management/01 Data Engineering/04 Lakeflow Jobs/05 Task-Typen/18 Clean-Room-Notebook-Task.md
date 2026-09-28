# Clean-Room-Notebook-Task

Führt ein Databricks-Notebook innerhalb eines Clean Rooms als Teil eines Workflows aus.

## Voraussetzung

Der ausführende Principal benötigt das Privileg `EXECUTE CLEAN ROOM TASK` auf dem betreffenden Clean Room.

## Konfiguration

**Neuer Job:** Jobs & Pipelines → **New** → **Job** → Typ `Clean Room notebook`.

**Bestehender Job:** Jobs & Pipelines → Job wählen → Tab **Tasks** → **Add task** → **Clean Room notebook**.

## Einrichtung

1. Clean Room mit dem gewünschten Notebook wählen.
2. Notebook auswählen.
3. Optional Abhängigkeiten über **Depends on** konfigurieren.
4. Nutzt das Notebook `dbutils.widgets`: Parameter als Key-Value-Paare konfigurieren.
5. Optional Retries, Laufdauer-/Streaming-Backlog-Schwellen oder Benachrichtigungen setzen.
6. Task speichern.
7. Notebook-Vorschau prüfen.
8. **Continue** klicken.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/clean-room-notebook
