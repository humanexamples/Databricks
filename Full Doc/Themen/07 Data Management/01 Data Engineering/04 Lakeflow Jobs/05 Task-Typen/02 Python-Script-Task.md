# Python-Script-Task

Führt eine Python-Datei innerhalb eines Jobs aus. Databricks empfiehlt Workspace-Dateien für Python-Skripte.

## Konfiguration

1. Tab **Tasks** → **Add task**.
2. Task-Namen eingeben.
3. Typ **Python script**.

## Quellorte

- **Workspace:** Datei über Dialog auswählen; unterstützt Skripte in Databricks-Git-Ordnern.
- **DBFS/S3:** für Skripte in Volumes, Cloud-Speicher oder DBFS-Root, z. B. `dbfs:/path/to/script.py` oder `s3://bucket-name/path/to/script.py`.
- **Git Provider:** relativer Pfad, ohne führendes `/` oder `./`.

## Compute und Bibliotheken

Passenden Compute-Cluster wählen. Bei Serverless: Environment und Bibliotheken konfigurieren. Sonst: abhängige Bibliotheken über die UI hinzufügen.

## Abschluss

Optional Parameter als CLI-Argumente konfigurieren; optional erweiterte Task-Einstellungen (Retries, Benachrichtigungen); **Save task**.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/python-script
