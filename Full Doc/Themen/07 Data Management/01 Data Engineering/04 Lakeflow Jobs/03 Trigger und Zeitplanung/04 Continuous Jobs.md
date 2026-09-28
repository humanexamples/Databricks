# Jobs kontinuierlich ausführen

Databricks empfiehlt den **Continuous**-Modus für dauerhaft laufende Streaming-Workloads — er ersetzt die frühere Empfehlung, unbegrenzte Retry-Policies mit maximal einem gleichzeitigen Lauf für Structured-Streaming-Tasks zu kombinieren.

## Hinweis zu Serverless Compute

Kontinuierliche Zeitpläne auf Serverless Compute funktionieren nur mit begrenzten Structured-Streaming-Triggern wie `Trigger.AvailableNow`. Der Job-Scheduler startet Tasks nach Abschluss neu; Streaming-Checkpoints verhindern erneute Verarbeitung. Zeitbasierte Trigger wie `Trigger.ProcessingTime` und `Trigger.Continuous` werden auf Serverless **nicht** unterstützt.

## Job auf Continuous Mode konfigurieren

1. **Jobs & Pipelines** in der Sidebar.
2. Optional Filter **Jobs**/**Owned by me**.
3. Job-Namen anklicken.
4. **Add trigger**, Trigger-Typ **Continuous**.
5. Optional **Task retry mode** (**On failure** oder **Never**, Standard: **On failure**).
6. **Save**.

**Steuerung:** **Pause** stoppt, **Resume** startet neu.

## Wichtige Einschränkungen

- Nur eine laufende Instanz pro Continuous Job.
- Verzögerung zwischen Läufen typischerweise unter 60 Sekunden.
- Keine Task-Abhängigkeiten oder Retry-Policies auf Task-Ebene nutzbar (stattdessen automatisches Job-Level-Retry mit Exponential Backoff; optionale Task-Level-Retries verfügbar).
- Für Konfigurationsänderungen an pausierten Jobs: **Run now**, sonst **Restart run**.

## Fehlerbehandlung

Fehlschläge nutzen Exponential Backoff. Bei „On failure"-Retry-Modus werden fehlgeschlagene Tasks mit wachsenden Verzögerungen erneut versucht (maximal drei bei Ein-Task-Jobs). Nach Erreichen der maximalen Retries wird der Lauf abgebrochen und ein neuer gestartet.

Bei wiederholten Fehlschlägen verlängert das System die Wartezeit bis zu einem Schwellenwert progressiv. Nach erfolgreichem Abschluss (oder Ausbleiben weiterer Fehler) kehrt der Job in den gesunden Zustand zurück, und die Backoff-Sequenz wird zurückgesetzt.

## Quelle

- https://docs.databricks.com/aws/en/jobs/continuous
