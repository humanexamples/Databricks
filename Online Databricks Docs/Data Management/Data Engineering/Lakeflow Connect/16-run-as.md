# Run-as-Identität für eine Pipeline konfigurieren

Die Einstellung **Run as** legt fest, mit welchen Berechtigungen eine Managed-Ingestion-Pipeline ausgeführt wird. Standardmäßig läuft eine Pipeline unter der Identität ihres Owners (eines Nutzers). Databricks empfiehlt stattdessen die Nutzung eines Service Principal, damit die Pipeline auch dann weiterläuft, wenn der Owner das Unternehmen verlässt oder den Workspace-Zugriff verliert.

## Run as bei der Pipeline-Erstellung konfigurieren

1. Im Schritt **Ingestion setup** die **Advanced settings** aufklappen.
2. Im Dropdown **Run as** einen Service Principal auswählen (Standard: Ausführung als Owner belassen).
3. Die restlichen Einrichtungsschritte abschließen und speichern.

## Run-as-Einstellung einsehen

Auf der Pipeline-Überwachungsseite zeigt das Panel **Pipeline details** die aktuell konfigurierte Identität der Pipeline an.

## Run as für bestehende Pipelines ändern

1. Die Pipeline-Überwachungsseite öffnen.
2. Auf **Edit pipeline** klicken.
3. Das Dropdown **Run as** in den **Advanced settings** aktualisieren.
4. Die Pipeline speichern.

**Gilt für:** SaaS-Connectors, Datenbank-Connectors und Query-basierte Connectors.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/run-as  
**Stand:** 2026-08-07
