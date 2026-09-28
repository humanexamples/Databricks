# 06L - Deploy a Simple DAB/databricks.yml

```yaml
###########################################################################################
# DIES IST DIE HAUPTKONFIGURATION DES DATABRICKS ASSET BUNDLE FÜR DAS PROJEKT             
###########################################################################################
# Dokumentation siehe https://docs.databricks.com/dev-tools/bundles/index.html.           #
###########################################################################################

################
# Bundle-Name  
################
bundle:                       # Erforderlich
  name: demo06_lab_bundle     # Erforderlich


############################################################################
# RESSOURCEN
# - Dies sind die Standardeinstellungen für Jobs und Pipelines (derzeit nur ein Job).
# TO DO: Fügen Sie unten die YAML-Konfiguration des Jobs ein, den Sie über die UI erstellt haben.
# TO DO: Nehmen Sie die im Notebook angegebenen erforderlichen Änderungen vor.
############################################################################

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


##############################################################################################
# ZIELUMGEBUNGEN FÜR DAS DEPLOYMENT
# - Dies sind die Ziele (Targets) für Deployments und Workflow-Runs. 
# - Genau eines dieser Ziele darf auf "default: true" gesetzt sein.
# - TO DO: Vervollständigen Sie unten das Ziel dev!
##############################################################################################
targets:

  dev:
    mode: development
    default: true
    workspace:
      # Der Host kann je nach gewünschtem Deployment-Ziel geändert werden. Standardmäßig wird der aktuelle Host verwendet. Auskommentiert lassen.
      # host: https://dbc-d9be2316-40bd.cloud.databricks.com/
      # Wir geben /Workspace/Users/username explizit an, damit nur eine einzige Kopie existiert.
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

```
