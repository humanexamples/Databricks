# Spark-Submit-Task: Deprecation und Migration

Databricks stuft den Spark-Submit-Task-Typ wegen technischer Einschränkungen und Feature-Lücken gegenüber JAR-, Notebook- und Python-Script-Tasks als veraltet ein. Ab **November 2025** ist das Erstellen neuer Spark-Submit-Tasks auf Nutzer beschränkt, die Spark Submit im Vormonat aktiv genutzt haben.

## Migrationswege

- **JVM-Workloads:** zu JAR-Tasks migrieren — Main-Class-Name und JAR-Dateipfad aus den Spark-Submit-Parametern extrahieren und im JAR-Task-Format konfigurieren (siehe `JAR-Task.md`).
- **R-Workloads:** entweder R-Skripte zu Databricks-Notebooks migrieren (voller Funktionsumfang), oder R-Skripte per `source()` aus einem Notebook-Task heraus bootstrappen.

## Betroffene Jobs finden

Zwei Python-Skripte von Databricks:

1. **Fast Scan** (empfohlener erster Schritt): scannt nur persistente Jobs über die `/jobs/create`-API — deutlich schneller.
2. **Comprehensive Scan:** untersucht alle Läufe der letzten 30 Tage, inkl. ephemerer Jobs über `/runs/submit` — kann in großen Workspaces Stunden dauern.

Beide liefern CSV-Ergebnisse mit Job-IDs, Eigentümer-E-Mails und Job-Namen.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/spark-submit
