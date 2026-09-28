# 09L - Deploy a DAB to Multiple Environments/solution/solution_databricks.yml

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
  name: demo09_lab_bundle     # Required


#################################################################
## Zusätzliche YAML-Konfigurationen, die in das Deployment aufgenommen werden
# - TO DO: Den relativen Pfad zu ./resources/ hinzufügen
#################################################################
include:
  - "./resources/lab09_nyc.job.yml"                      ## <--- Hier Ihre Datei ./resources/lab09_nyc.job.yml hinzufügen


################################################################
# VARIABLES   
# - TO DO: Die benutzerdefinierten Variablen für das Bundle vervollständigen
################################################################
variables:
  user_name:
    description: TODO - PLEASE REPLACE THE TEXT BELOW WITH YOUR LAB USER NAME!!!
    default: labuser1234       ## <---- Ihren Lab-Benutzernamen hinzufügen

# Ändern Sie die folgenden Variablen nicht. Sie verwenden den Standardwert der Variablen user_name und erzeugen die nötigen Variablen. Sehen Sie sich die folgenden Variablen an.
  catalog_dev:
    description: Development catalog for the project. Append _1_dev to the user name.
    default: ${var.user_name}_1_dev
    
  catalog_prod:
    description: Production catalog for the project. Append _3_prod to the user name.
    default: ${var.user_name}_3_prod



##############################################################################################
# ZIELUMGEBUNGEN FÜR DAS DEPLOYMENT
# - Dies sind die Ziele (Targets) für Deployments und Workflow-Runs. 
# - Genau eines dieser Ziele darf auf "default: true" gesetzt sein
##############################################################################################
targets:

  dev:
    # Das Standardziel verwendet 'mode: development', um eine Entwicklungskopie zu erstellen.
    # - Deployed resources get prefixed with '[dev my_user_name]'
    mode: development
    default: true
    workspace:
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}
    
    # Einen Job-Parameter für DEV hinzufügen
    resources:
      jobs:
        lab09_dab:
          parameters:
            - name: catalog_name
              default: ${var.catalog_dev}              # <----- Hier den Entwicklungskatalog für den Job-Parameter hinzufügen


  prod:
    mode: production
    workspace:
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

    # Einen Job-Parameter für PROD hinzufügen
    resources:
      jobs:
        lab09_dab:
          parameters:
            - name: catalog_name
              default: ${var.catalog_prod}              # <----- Hier den Produktionskatalog für den Job-Parameter hinzufügen
```
