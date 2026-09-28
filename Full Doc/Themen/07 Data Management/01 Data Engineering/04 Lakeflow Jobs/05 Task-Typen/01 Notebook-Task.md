# Notebook-Task

Notebooks lassen sich als Task in Lakeflow Jobs bereitstellen. Das Notebook muss an einem für den konfigurierenden Nutzer zugänglichen Ort liegen.

## Konfiguration

1. Tab **Tasks** → **Add task**.
2. Task-Namen eingeben.
3. Typ **Notebook** wählen.

## Quellort

- **Workspace:** Pfad-Feld anklicken → **Select Notebook**-Dialog → Notebook wählen. Unterstützt Notebooks in Databricks-Git-Ordnern (Databricks empfiehlt jedoch Git-Provider-Optionen für die Versionierung zeitgesteuerter Assets).
- **Git Provider:** für Notebooks in Remote-Git-Repositories. Nur ein Remote-Repository über alle Job-Tasks hinweg nutzbar. Relative Pfade ohne führendes `/` oder `./` (z. B. `etl/bronze/ingest.py`).

**Wichtig:** Von Lakeflow Jobs aus Remote-Git-Repositories heraus ausgeführte Notebooks sind **ephemer** und eignen sich nicht zuverlässig zum Tracking von MLflow-Runs, -Experimenten oder -Modellen.

## Compute und Bibliotheken

SQL-Warehouses eignen sich nur als Compute für reine SQL-Notebooks mit SQL als Standardsprache. Bei Serverless Compute werden Bibliotheken direkt im Notebook installiert; sonst über die UI (bestehende Bibliothek wählen oder neue hochladen).

## Parameter

Optionale Task-Parameter als Key-Value-Paare, zugänglich über `dbutils.widgets`.

## Visual Data Prep

Erstellt Notebook-Tasks aus `.designer.ipynb`-Dateien, die mit Lakeflow Designer gebaut wurden.

## Einschränkung

Die gesamte Zellen-Ausgabe eines Notebooks ist auf **30 MB** begrenzt, einzelne Zellen-Ausgaben auf **8 MB**.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/notebook
