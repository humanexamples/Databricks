# 06L - Deploy a Simple DAB/solution/solution_databricks.yml

```yaml
###########################################################################################
# BEISPIELLÖSUNG FÜR DAS LAB               
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
    lab06_job_peter:    ## <--- Benennen Sie dies beliebig um 
      name: lab06_job_peter
      email_notifications:
        on_success:
          - fake@databricks.com
      tasks:
        - task_key: create_nyc_tables
          notebook_task:
            notebook_path: ./src/our_project_code.ipynb
            source: WORKSPACE
          existing_cluster_id: 0205-212942-5t9srjjck     ## <--- Ändern Sie dies in Ihre Cluster-ID
      queue:
        enabled: true
      parameters:
        - name: catalog_name
          default: labuser1234_1_dev    ## <--- Ändern Sie dies in den Namen Ihres catalog_1_dev
        - name: display_target
          default: Development

##############################################################################################
# ZIELUMGEBUNGEN FÜR DAS DEPLOYMENT
# - Dies sind die Ziele (Targets) für Deployments und Workflow-Runs. 
# - Genau eines dieser Ziele darf auf "default: true" gesetzt sein.
# - TO DO: Vervollständigen Sie unten das Ziel dev!
##############################################################################################
targets:
    
  # Fügen Sie hier Ihre Konfiguration für das Ziel 'dev' hinzu.
  dev:
    # Geben Sie unbedingt die Deployment-Details für die Entwicklungsumgebung an.
    mode: development

    # Stellen Sie sicher, dass 'default: true' für das Ziel gesetzt ist, das standardmäßig bereitgestellt werden soll.
    default: true

    workspace:
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}
```
