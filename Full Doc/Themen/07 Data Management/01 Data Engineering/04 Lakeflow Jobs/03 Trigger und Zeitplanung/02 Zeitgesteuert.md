# Jobs zeitgesteuert ausführen

Der Trigger-Typ **Scheduled** löst Jobs zeitbasiert aus, mit zwei Varianten:

- **Simple:** periodische Ausführung nach Zeiteinheit und Intervall (z. B. alle 12 Stunden, beginnend mit dem ersten Lauf). Der Startzeitpunkt des ersten Laufs lässt sich hierbei **nicht** vorgeben — der Scheduler wählt ihn selbst.
- **Advanced:** mehr Kontrolle über Periode, Uhrzeit und Zeitzone.

## Zeitplan hinzufügen

1. **Jobs & Pipelines** in der Sidebar.
2. Optional Filter **Jobs** und **Owned by me** setzen.
3. Job-Namen anklicken.
4. Im **Job details**-Panel **Add trigger**.
5. **Trigger type** → **Scheduled**.
6. **Schedule type** → **Simple** oder **Advanced**.
   - **Simple:** Intervall und Zeiteinheit angeben.
   - **Advanced:** Periode, Startzeit, Zeitzone angeben. Optional **Show Cron Syntax** aktivieren, um den Zeitplan in Quartz-Cron-Syntax anzuzeigen/zu bearbeiten.
7. **Save**.

Ein Notebook-Job lässt sich auch direkt aus der Notebook-UI heraus zeitplanen.

## Wichtige Hinweise

- Databricks erzwingt ein **Mindestintervall von 10 Sekunden** zwischen aufeinanderfolgenden, per Zeitplan ausgelösten Läufen.
- Die Zeitzonenwahl beeinflusst das Verhalten bei der Sommerzeitumstellung — für stündliche, absolute Ausführungszeiten wird UTC empfohlen.
- Der Job-Scheduler ist nicht für niedrige Latenzanforderungen ausgelegt — Verzögerungen von bis zu mehreren Minuten sind möglich.

## Quelle

- https://docs.databricks.com/aws/en/jobs/scheduled
