# 14L Bonus - Adding ML to Engineering Workflows with DABs/TODO - Lab DABs Workflow/databricks.yml

```yaml
###########################################################################################
# DIES IST DIE HAUPTKONFIGURATION DES DATABRICKS ASSET BUNDLE FÜR DAS PROJEKT                  
# - Dies schließt Folgendes ein:
#   - variables.yml
#   - health_etl_pipeline.pipeline.yml
#   - dabs_workflow.job.yml
###########################################################################################
# Dokumentation siehe https://docs.databricks.com/dev-tools/bundles/index.html.           #
###########################################################################################

################
# Bundle name  #
################
bundle:
  name: ml_health_etl_bundle


#################################################################
## Zusätzliche YAML-Konfigurationen, die in das Deployment aufgenommen werden #
#################################################################
include:
  - "./resources/variables.yml"                           # Sie können Ihre Variablen in einer separaten YAML-Datei definieren
  - "./resources/pipeline/health_etl_pipeline_with_ml.pipeline.yml"  # Declarative pipeline YAML
  - "./resources/job/dabs_workflow_with_ml.job.yml"                  # Job YAML

##############################################################################################
# Dies sind die Ziele (Targets) für Deployments und Workflow-Runs. Genau eines dieser Ziele  #
##############################################################################################
targets:

  development:
    # Das Standardziel verwendet 'mode: development', um eine Entwicklungskopie zu erstellen.
    # - Deployed resources get prefixed with '[dev my_user_name]'
    # - Alle Job-Zeitpläne und Trigger sind standardmäßig pausiert.
    # Siehe auch https://docs.databricks.com/dev-tools/bundles/deployment-modes.html.
    mode: development
    default: true
    workspace:
      # Wir geben /Workspace/Users/username explizit an, damit nur eine einzige Kopie existiert.
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}


  stage:
    mode: development
    workspace:
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}
    variables:
      # Bereits für Sie erledigt. Ändert Standardkatalog, Rohdatenpfad und Speicherort der Silber-Tabelle über Variablen-Überschreibungen
      target_catalog: ${var.catalog_stage}                               ## Zielkatalog auf unseren Stage-Katalog geändert
      raw_data_path: /Volumes/${var.catalog_stage}/default/health        ## Rohdaten aus unseren Stage-Daten
      silver_table_name: ${var.target_catalog}.default.silver_sample_ml  ## References the labuser_2_stage silver table
```
