# 09L - Deploy a DAB to Multiple Environments/solution/solution_lab09_nyc.job.yml

```yaml
######################################################################
# Job YAML Configuration SOLUTION
# TO DO: Fügen Sie den Parametern die nötigen Variablen hinzu, um dynamisch nach dev oder prod bereitzustellen
######################################################################
resources:
  jobs:
    lab09_dab:
      name: lab09_dab_${workspace.current_user.userName}             # <----- lab09_dab_ + den Wert Ihrer Benutzernamen-Variablen an das Ende des Job-Namens anhängen
      tasks:
        - task_key: create_nyc_tables
          notebook_task:
            notebook_path: ../src/our_project_code.ipynb
            source: WORKSPACE
      parameters:
        - name: display_target
          default: ${bundle.target}       # <---- Hier die Variable bundle.target als Job-Wert hinzufügen
```
