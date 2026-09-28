# Smart Closure für integrierte CDC-Pipelines

Smart Closure ist eine Richtlinie, die bestimmt, wann Updates einer CDC-Pipeline beendet werden. Statt fester Laufzeiten passt sie sich am Umfang der verfügbaren Änderungsdaten der Quelle an.

## Wann Updates enden

Zwei Bedingungen beenden ein Update:

1. **Aufholung zur Quelle erreicht (`lag-converged`):** Das Update hat den ausstehenden Änderungsrückstand verarbeitet und ist nahezu auf dem aktuellen Stand der Quelle.
2. **Laufzeitgrenze erreicht (`max-runtime-cap-hit`):** Die Quelle hatte einen großen Rückstand (z. B. weil die Pipeline lange nicht ausgeführt wurde), sodass das Update nach einer begrenzten Laufzeit gestoppt wurde.

## Vorteile

- **Kosteneffizienz:** Updates enden, sobald sie aufgeholt haben, statt fest vorgegebene Laufzeiten zu durchlaufen – das reduziert den Rechenaufwand für inkrementelle Änderungen.
- **Vorhersehbare Laufzeit:** Große Rückstände können nicht zu unbegrenzt langen Läufen führen; jedes Update hat eine Obergrenze, sodass große Workloads über mehrere geplante Ausführungen verteilt werden.
- **Klare Nachvollziehbarkeit:** Jeder Abschluss enthält eine Grund-Kennzeichnung, ob die Quelle eingeholt wurde oder das Laufzeitlimit erreicht wurde.

## Abschlussgrund überwachen

Der Abschlussgrund erscheint im `COMPLETED`-Ereignis des Pipeline-Event-Logs. Abfrage über folgendes SQL-Muster:

```sql
%sql
SELECT timestamp, message
FROM event_log('<pipeline-id>')
WHERE message LIKE '%Direct Cdc Extraction has COMPLETED%'
ORDER BY timestamp DESC
```

## Zeitplanung

Da die Update-Dauer je nach Datenvolumen der Quelle variiert, werden wiederkehrende geplante Updates empfohlen. Ein Startwert von 60 Minuten eignet sich für die meisten Workloads.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/smart-closure  
**Stand:** 2026-08-07
