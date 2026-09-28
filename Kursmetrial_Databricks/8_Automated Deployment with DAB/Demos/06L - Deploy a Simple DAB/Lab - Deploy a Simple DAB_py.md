# 06L - Ein einfaches Declarative Automation Bundle (DAB) bereitstellen

Sie sind dafür verantwortlich, Databricks-Projekte über den CI/CD-Prozess Ihrer Organisation mit **Declarative Automation Bundles (DABs)** bereitzustellen.

Ein Kollege hat ein Notebook unter `./src/our_project_code` freigegeben.

Ihre Aufgabe ist es, den Deployment-Prozess zu beginnen, indem Sie das Projekt für die **Development**-Umgebung konfigurieren und bereitstellen.

```yaml
bundle:                       # Erforderlich
  name: demo06_lab_bundle     # Erforderlich


resources:
  jobs:
    lab06_job_huam:
      name: lab06_job_huam
      tasks:
        - task_key: create_nyc_tables
          notebook_task:
            notebook_path: ./src/our_project_code.ipynb
            base_parameters:
              catalog_name: labuser15933383_1787984676_1_dev
              display_target: Development
            source: WORKSPACE
          existing_cluster_id: 0829-062521-v2oh1khu
      queue:
        enabled: true


targets:

  dev:
    mode: development
    default: true
    workspace:
    root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

```

```python
%sh

# Schritt 1: Bundle validieren, falls databricks.yml vorhanden
databricks bundle validate

# Schritt 2: Bundle bereitstellen
databricks bundle deploy -t dev

# Schritt 3: Den Job ausführen
databricks bundle run -t dev lab06_job_huam

# Schritt 4: Den bereitgestellten Job entfernen
# Standardmäßig werden Sie aufgefordert, das endgültige Löschen der zuvor bereitgestellten 
# Jobs, Pipelines und Artefakte zu bestätigen. Um diese Abfragen zu überspringen und automatisch 
# endgültig zu löschen, fügen Sie dem Befehl bundle destroy die Option --auto-approve hinzu.
databricks bundle destroy --auto-approve
```





