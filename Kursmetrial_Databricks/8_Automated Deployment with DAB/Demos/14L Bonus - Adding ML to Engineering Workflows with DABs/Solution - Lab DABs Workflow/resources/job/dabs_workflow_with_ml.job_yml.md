# 14L Bonus - Adding ML to Engineering Workflows with DABs/Solution - Lab DABs Workflow/resources/job/dabs_workflow_with_ml.job.yml

```yaml
######################################
# SOLUTION EXAMPLE
######################################
# THE JOB CONFIGURATION              #
######################################
# HINWEIS: Der Notebook-Pfad muss relativ zum Speicherort der YAML-Datei angegeben werden

# Beispiel: Diese YAML-Datei liegt in /Workspace/Shared/databricks-devops-for-pipeline-source/Source/Databricks Devops for Pipelines/resrouces/job/ und Run Unit Tests liegt in /Workspace/Shared/databricks-devops-for-pipeline-source/Source/Databricks Devops for Pipelines/. In diesem Fall wäre notebook_path ../../Run Unit Tests.ipynb. 

resources:
  jobs:
    ml_health_etl_workflow:                          # <----- Job key name 
      name: ml_health_etl_workflow_${bundle.target}  # <----- Job name
      description: Final Workflow SDK
      email_notifications:
        on_failure:
          - ${var.my_email}
      tasks:
        - task_key: Unit_Tests
          notebook_task:
            notebook_path: ../../run_unit_tests.ipynb  #<----- Setzt den relativen Pfad zur Datei ausgehend vom Speicherort dieser Datei
            source: WORKSPACE
          description: Execute unit tests for project.
        - task_key: Visualization
          depends_on:
            - task_key: Health_ETL
          notebook_task:
            notebook_path: ../../src/Final Visualization.ipynb #<----- Setzt den relativen Pfad zur Datei ausgehend vom Speicherort dieser Datei
            base_parameters:
              catalog_name: ${var.target_catalog}
            source: WORKSPACE
          description: Final visualization for project.
        ### ------------------------------------------------------
        ### Vervollständigen Sie hier Ihren ML-TASK
        ### ------------------------------------------------------
        - task_key: ML_test  #<----- Name your task ML_test
          depends_on:
            - task_key: Health_ETL
          existing_cluster_id: ${var.cluster_id}  #<----- Verweist auf Ihre Variable cluster_id aus variables.yml
          notebook_task:
            notebook_path: ../../src/Inference.ipynb #<----- Relativen Pfad zur Datei Interference.py ausgehend vom Speicherort dieser Datei setzen
            base_parameters:
              base_model_name: ${var.base_model_name}
              silver_table_name: ${var.silver_table_name}
              catalog_name: ${var.target_catalog}
            source: WORKSPACE
          description: Inference an ML model.
        ### ------------------------------------------------------
        ### END ML TASK 
        ### ------------------------------------------------------
        - task_key: Health_ETL
          depends_on:
            - task_key: Unit_Tests
          pipeline_task:
            pipeline_id: ${resources.pipelines.health_etl_pipeline.id}
            full_refresh: true
          description: Spark Declarative Pipeline ETL
      
      ####################################################
      # Dynamische Job-Parameter auf Basis unserer Variablen    #
      ####################################################
      parameters:
        - name: target
          default: ${bundle.target}
        - name: catalog_name
          default: ${var.target_catalog}
```
