# databricks.yml

```yaml
###########################################################################################
# DIES IST DIE HAUPTKONFIGURATION DES DATABRICKS ASSET BUNDLE FÜR DAS PROJEKT             
###########################################################################################
# Dokumentation siehe https://docs.databricks.com/dev-tools/bundles/index.html.           #
###########################################################################################


################################################################################
# Bundle-Name  
# - Das Mapping bundle ist erforderlich und muss einen Bundle-Namen enthalten.
################################################################################
bundle:                   # Erforderlich
  name: demo05_bundle     # Erforderlich


############################################################################
# RESSOURCEN
# - Dies sind die Standardeinstellungen für Jobs und Pipelines (derzeit nur ein Job).
# TO DO: Fügen Sie unten IHRE in den vorherigen Schritten erhaltene Job-YAML-Konfiguration ein.
############################################################################

resources:
  jobs:
    demo05_simple_dab_labuser15933383_1787966030:
      name: demo05_simple_dab_labuser15933383_1787966030
      tasks:
        - task_key: create_bronze_table
          notebook_task:
            notebook_path: ./src/create_bronze_table.ipynb
            source: WORKSPACE
        - task_key: create_silver_table
          depends_on:
            - task_key: create_bronze_table
          notebook_task:
            notebook_path: ./src/create_silver_table.ipynb
            source: WORKSPACE
      parameters:
        - name: display_target
          default: development
        - name: catalog_name
          default: labuser1234_1_dev



##############################################################################################
# ZIELUMGEBUNGEN FÜR DAS DEPLOYMENT
# - Dies sind die Ziele (Targets) für Deployments und Workflow-Runs. 
# - Genau eines dieser Ziele darf auf "default: true" gesetzt sein.
# - In diesem Beispiel stellen wir nur mit dem Entwicklungskatalog bereit.
##############################################################################################
targets:

  development:
    # Das Standardziel verwendet 'mode: development', um eine Entwicklungskopie zu erstellen.
    # - Im Development-Modus bereitgestellte Ressourcen erhalten das Präfix '[dev my_user_name]'
    mode: development
    default: true
    workspace:
      # Der Host kann je nach gewünschtem Deployment-Ziel geändert werden. Standardmäßig wird der aktuelle Host verwendet. Auskommentiert lassen.
      # host: https://dbc-d9be2316-40bd.cloud.databricks.com/
      # Wir geben /Workspace/Users/username explizit an, damit nur eine einzige Kopie existiert.
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

```
