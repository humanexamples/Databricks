# JAR-Task

Führt in Scala oder Java kompilierten und als JAR verpackten Code aus.

## Voraussetzungen

- Passende Compute-Konfiguration wählen.
- JAR-Datei an einem kompatiblen Ort oder Maven-Repository hochladen.
- Bei Standard Access Mode: Admins müssen Maven-Koordinaten und JAR-Pfade auf eine Allowlist setzen.

## Konfiguration

1. Tab **Tasks** → **Add task**.
2. Task-Namen eingeben, Typ **JAR**.
3. **Main class** angeben (voller Klassenname mit der `main`-Methode; muss in einer als Dependent Library konfigurierten JAR enthalten sein).
4. **Compute** wählen (Classic oder Serverless).
5. Environment und Abhängigkeiten:
   - **Classic:** **Add** unter **Dependent libraries** → bestehende JAR wählen oder hochladen (nicht jeder Speicherort unterstützt JAR-Dateien).
   - **Serverless:** Environment wählen/bearbeiten, Environment Version 4+, JAR-Datei und weitere Abhängigkeiten hinzufügen (Spark-Abhängigkeiten ausgenommen).
6. **Parameters** als optionale String-Liste, die als Argumente an die Main-Class übergeben werden.
7. Optional erweiterte Einstellungen (Retries, Laufdauer-/Streaming-Backlog-Schwellen, Benachrichtigungen).
8. **Save task**.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/jar
