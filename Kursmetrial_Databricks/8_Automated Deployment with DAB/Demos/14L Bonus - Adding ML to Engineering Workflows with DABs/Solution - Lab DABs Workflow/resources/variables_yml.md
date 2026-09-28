# 14L Bonus - Adding ML to Engineering Workflows with DABs/Solution - Lab DABs Workflow/resources/variables.yml

```yaml
#########################################
# SOLUTION EXAMPLE
#########################################
# DIE IM DAB VERWENDETEN VARIABLEN DEFINIEREN  #
#########################################

variables:
  ###############################################################
  ## BITTE NUR DIE VARIABLEN IM FOLGENDEN ABSCHNITT ÄNDERN  #
  ###############################################################
  username:
    description: Paste your username here
    default: labuser1234      # <-- Ihren Benutzernamen hinzufügen (Beispiel labuserxxx)
  my_email:
    description: Email address to send an alert notification to
    default: peter@fakeemail.com       # <-- Ihre E-Mail-Adresse für Benachrichtigungen eingeben
  cluster_id:
    description: Get the cluster ID using a lookup variable
    lookup:
      cluster: labuser1234   # <-- Ihren Benutzernamen kopieren und einfügen (beginnt mit labuserxxx)
  base_model_name:
    description: This is the base model to be used in the ML task
    default: diabetes_model_dev     # <-- Hier den Namen Ihres Basismodells "diabetes_model_dev" eingeben, das sich in Ihrem labuser_dev-Katalog unter models befindet 
  silver_table_name:
    description: This is the name of the silver table stored in DEV 
    default: ${var.username}_1_dev.default.silver_sample_ml  # <-- Bereits für Sie erledigt. Unverändert lassen.

  ##########################################
  ## ÄNDERN SIE KEINE DER FOLGENDEN WERTE!!!     #
  ## ÄNDERN SIE KEINE DER FOLGENDEN WERTE!!!     #
  ##########################################

  ###############################################
  # Die Variable catalog_dev dynamisch setzen    #
  ###############################################
  dev_tag:
    description: Sets the dev tag for the catalog name
    default: _1_dev
  catalog_dev:
    description: Sets the catalog to create tables in
    default: ${var.username}${var.dev_tag}

  ###############################################
  # Die Variable catalog_stage dynamisch setzen  #
  ###############################################
  stage_tag:
    description: Sets the stage tag for the catalog name
    default: _2_stage
  catalog_stage:
    description: Sets the catalog to create tables in
    default: ${var.username}${var.stage_tag}

  ###############################################
  # Die Variable catalog_prod dynamisch setzen   #
  ###############################################
  prod_tag:
    description: Sets the prod tag for the catalog name
    default: _3_prod
  catalog_prod:
    description: Sets the catalog to create tables in
    default: ${var.username}${var.prod_tag}

  schema:
    description: Schema to write to
    default: default

##############################################################################################
# Die Standardwerte für raw_data_path und target_catalog verweisen auf die Dev-Rohdaten und den Dev-Katalog. #
# Diese Werte werden je nach bereitgestelltem Ziel in der Datei databricks.yml geändert.      #
##############################################################################################
  raw_data_path:
    description: Path to source csv files to ingest (dev/stage/prod) - default is 'dev'
    default: /Volumes/${var.catalog_dev}/default/health
  target_catalog:
    description: Target catalog to use for deployment
    default: ${var.catalog_dev}
```
