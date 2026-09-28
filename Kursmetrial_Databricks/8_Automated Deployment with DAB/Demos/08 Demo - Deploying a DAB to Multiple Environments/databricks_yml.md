# 08 Demo - Deploying a DAB to Multiple Environments/databricks.yml

```yaml
bundle:                   # Erforderlich
  name: demo08_bundle     # Erforderlich


#################################################################
## Zusätzliche YAML-Konfigurationen, die in das Deployment aufgenommen werden #
## - Das Array include gibt eine Liste von Pfaden mit Konfigurationsdateien an, die in das Bundle aufgenommen werden.
#################################################################
include:
  - "./resources/demo_08_job.job.yml"       # Vollständige Job-Konfiguration im Ordner resources


variables:
  my_lab_user_name:
    description: Add your lab user name
    default: ${workspace.current_user.short_name}      #<----- Ermittelt Ihren Lab-Benutzernamen dynamisch

# Ändern Sie die folgenden Variablen nicht. Sie verwenden den Standardwert der Variablen my_lab_user_name und erzeugen die nötigen Variablen. Sehen Sie sich die folgenden Variablen an.
  catalog_dev:
    description: Development catalog for the project. Append _1_dev to the user name.
    default: ${var.my_lab_user_name}_1_dev
    
  catalog_prod:
    description: Production catalog for the project. Append _3_prod to the user name.
    default: ${var.my_lab_user_name}_3_prod

  target_catalog:
    description: Target catalog to use for deployment - default is 'dev'.
    default: ${var.catalog_dev}
    
  raw_data_path:
    description: Path to source CSV files to ingest (dev/stage/prod) - default is 'dev'.
    default: /Volumes/${var.target_catalog}/default/health

  my_cluster_id:
    description: Get the lab cluster ID using a lookup variable.
    lookup:
      cluster: labuser15933383_1788034912




##############################################################################################
# ZIELUMGEBUNGEN FÜR DAS DEPLOYMENT
# - Dies sind die Ziele (Targets) für Deployments und Workflow-Runs. 
# - Genau eines dieser Ziele darf auf "default: true" gesetzt sein.
##############################################################################################
targets:

  development:
    mode: development
    default: true
    workspace:
      # host: https://dbc-d9be2316-40bd.cloud.databricks.com/
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

    # Im Development-Modus Ihren kleinen Lab-Cluster für die Tasks verwenden. Dadurch wird der Cluster jedem Task im Ressourcen-Mapping des Jobs demo_08_job hinzugefügt.
    resources:
      jobs:
        demo_08_job:
          tasks:
            - task_key: create_bronze_table
              existing_cluster_id: ${var.my_cluster_id}
            - task_key: create_silver_table
              existing_cluster_id: ${var.my_cluster_id}


  production:
    mode: production
    workspace:
      # host: https://dbc-d9be2316-40bd.cloud.databricks.com/
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

    ## In der Produktionsumgebung Variablenwerte ändern, um den Produktionskatalog username_3_prod zu verwenden
    variables:
        target_catalog: ${var.catalog_prod}
```
