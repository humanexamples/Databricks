# 09L - Deploy a DAB to Multiple Environments/resources/lab09_nyc.job.yml

```yaml
######################################################################
# Job YAML Configuration
# TO DO: Fügen Sie den Parametern die nötigen Variablen hinzu, um dynamisch nach dev oder prod bereitzustellen
######################################################################
resources:
  jobs:
    lab09_dab:
      name:             # <----- lab09_dab_ + Ihren Benutzernamen an das Ende des Job-Namens anhängen
      tasks:
        - task_key: create_nyc_tables
          notebook_task:
            notebook_path: ../src/our_project_code.ipynb
            source: WORKSPACE
      parameters:
        - name: display_target
          default:       # <---- Hier die Variable bundle.target als Job-Parameter hinzufügen
```
