# Python-Wheel-Task

Führt paketierten Python-Code über eine Python-Wheel-Datei aus. Das Wheel muss an einem kompatiblen Ort hochgeladen sein; Paketname und Entry Point aus `setup.py` müssen bekannt sein.

## Konfiguration

1. Task hinzufügen, Namen vergeben.
2. Typ **Python wheel**.
3. **Package name** aus `setup.py` eingeben.
4. **Entry point**-Funktion aus dem `entry_points`-Dictionary angeben.
5. Passendes Compute wählen/konfigurieren.
6. Bei Serverless: Environment und Bibliotheken konfigurieren; sonst: Wheel-Dateien hochladen/auswählen.
7. Optional Parameter als positionale oder Keyword-Argumente konfigurieren.
8. Optional erweiterte Einstellungen (Retries, Benachrichtigungen).
9. Task speichern.

**Hinweis:** Die Jobs-UI zeigt Optionen dynamisch je nach anderen konfigurierten Einstellungen an. Wheel-Dateien müssen an einem von der Compute-Konfiguration unterstützten Ort liegen.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/python-wheel
