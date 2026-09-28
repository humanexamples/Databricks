# Einen einzelnen Job-Lauf auslösen

## Sofort ausführen

**Run now** klickt einen Job sofort an — auch als Testlauf für einen Notebook-Task geeignet.

## Mit anderen Einstellungen ausführen

Über **Run now with different settings** (blauer Pfeil neben „Run now") lässt sich:

- eine Teilmenge der Tasks aus-/abwählen,
- neue Job-Parameter als Key-Value-Paare eingeben,
- die Einstellung „Performance optimized" für Serverless-Workloads ändern.

## Teilmenge von Tasks samt Abhängigkeiten ausführen

Bei „Run now with different settings" lassen sich einzelne Tasks auswählen, optional erweitert um Abhängigkeiten über das `+`-Präfix/Suffix:

| Syntax | Bedeutung |
|---|---|
| `my_task` | nur dieser Task |
| `+my_task` | Task plus vorgelagerte Abhängigkeiten |
| `my_task+` | Task plus nachgelagerte Abhängigkeiten |
| `+my_task+` | Task mit vor- und nachgelagerten Abhängigkeiten |

Diese Syntax lässt sich auch über REST API und CLI verwenden.

## Manuelle Trigger bei Continuous Jobs

Bei kontinuierlichen Jobs ersetzt der Button **Restart run** den „Run now"-Button, um weiterhin nur einen gleichzeitigen Lauf zu gewährleisten. Beim Pausieren des Triggers erscheint wieder „Run now".

## Quelle

- https://docs.databricks.com/aws/en/jobs/run-now
