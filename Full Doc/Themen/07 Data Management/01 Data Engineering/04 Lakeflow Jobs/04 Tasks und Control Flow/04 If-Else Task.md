# If/else-Task: Verzweigungslogik

Der **If/else-Condition**-Task ermöglicht Boolean-Bedingungslogik in Task-Graphen über Operatoren und Operandenpaare. Operanden können Job-/Task-Zustand über konfigurierte oder dynamische Parameter und Task Values referenzieren.

**Beispiel:** Ein Task `process_records` führt einen Zähler ungültiger Datensätze `bad_records` als Task Value. Ein If/else-Task mit dem Ausdruck `{{tasks.process_records.values.bad_records}} > 0` verzweigt die Verarbeitung, wenn ungültige Datensätze auftreten. Nach dem Lauf lassen sich Ergebnis und Auswertungsdetails in den Job-Run-Details der UI einsehen.

## Wichtige Hinweise zur Wertauswertung

- `==` und `!=` vergleichen als **String** (`12.0 == 12` ist `false`).
- `>`, `>=`, `<`, `<=` vergleichen **numerisch** (`12.0 >= 12` ist `true`).
- Nur numerische, String- und Boolean-Werte sind bei Task-Value-Referenzen erlaubt; andere Typen werden zu Strings serialisiert.

## If/else-Task konfigurieren

1. Plus-Icon → **Add task**.
2. Task-Namen eingeben.
3. Typ **If/else condition** wählen.
4. Ersten Operanden im Condition-Feld eingeben — möglich sind:
   - Job-Parameter: `{{job.parameters.<name>}}`
   - Task-Parameter
   - Task Value: `{{tasks.<task_name>.values.<value_name>}}`
5. Boolean-Operator wählen.
6. Vergleichswert im zweiten Condition-Feld eingeben.
7. Optional Retries, Laufdauer-/Streaming-Backlog-Schwellen oder Benachrichtigungen konfigurieren.
8. **Save task**.

## Abhängigkeiten vom If/else-Ergebnis konfigurieren

1. If/else-Task im Task-Graphen wählen.
2. Plus-Icon → **Add task**.
3. **Depends on** ist standardmäßig `<task-name> (true)`.
4. Für den False-Zweig `<task-name> (false)` wählen.

Mehrere Tasks lassen sich seriell oder parallel je nach If/else-Ergebnis konfigurieren; für zusätzliche Fehlerbehandlung eignet sich „Run if dependencies".

**Einschränkung:** Ein If/else-Task schlägt fehl, wenn der vorgelagerte Task, der seinen Bedingungswert liefert, deaktiviert ist.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/if-else
