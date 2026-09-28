# 08 Demo - Deploying a DAB to Multiple Environments/resources/demo_08_job.job.yml

```yaml
############################################################################
# RESSOURCEN
# - Dies sind die Standardeinstellungen für Jobs und Pipelines (derzeit nur ein Job)
# TO DO: Ersetzen Sie das folgende Ressourcenbeispiel und fügen Sie IHRE Job-YAML-Konfiguration ein
############################################################################
resources:
  jobs:
    demo_08_job:
      name: ${bundle.target}_demo_08_dab_${workspace.current_user.userName}
      tasks:
        - task_key: create_bronze_table
          notebook_task:
            notebook_path: ../src/create_bronze_table.ipynb
            source: WORKSPACE
        - task_key: create_silver_table
          depends_on:
            - task_key: create_bronze_table
          notebook_task:
            notebook_path: ../src/create_silver_table.ipynb
            source: WORKSPACE
      parameters:
      - name: display_target
        default: ${bundle.target}
      - name: catalog_name
        default: ${var.target_catalog}
```
