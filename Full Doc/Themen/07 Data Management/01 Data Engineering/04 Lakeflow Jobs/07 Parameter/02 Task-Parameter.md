# Task-Parameter konfigurieren

Task-Parameter parametrisieren Tasks mit statischen, dynamischen oder von vorgelagerten Tasks erzeugten Werten.

**Hinweis:** Manche Tasks unterstützen Parametrisierung ohne eigenes Parameter-Feld, z. B. dbt-Kommandos oder die Verzweigungslogik des If/else-Tasks.

## Key-Value-Parameter

Gilt für: Notebook-Tasks, Python-Wheel-Tasks (nur Keyword-Argumente), SQL-Query-/-File-Tasks, Run-Job-Tasks.

Job-Parameter propagieren automatisch an Tasks, die Key-Value-Parameter unterstützen. Die UI warnt, wenn Task-Parameter dieselben Schlüssel wie Job-Parameter verwenden (siehe `Job-Parameter.md`, Abschnitt „Weitergabe an Tasks").

## JSON-Array-Parameter

Gilt für: Python-Script-Tasks, Python-Wheel-Tasks (nur positionale Argumente), JAR-Tasks, Spark-Submit-Tasks, For-each-Tasks.

Der For-each-Task iteriert über dieses Array für bedingte Logik; andere Task-Typen erhalten den Array-Inhalt als Kommandozeilenargumente.

Job-Parameter propagieren **nicht** automatisch an JSON-Array-Tasks, lassen sich aber über `{{job.parameters.<name>}}` referenzieren. Job-Parameterwerte unterstützen beliebige gültige JSON-Konstrukte, was dynamische Wertreferenzen zur Task-Bedingungslogik ermöglicht.

## Quelle

- https://docs.databricks.com/aws/en/jobs/task-parameters
