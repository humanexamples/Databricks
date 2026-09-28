# 13 Demo - Continuous Integration and Continuous Deployment with DABs/Full Project/resources/job/dabs_workflow.job.yml

```yaml
######################################
# THE JOB CONFIGURATION              #
######################################
# HINWEIS: Der Notebook-Pfad muss relativ zum Speicherort der YAML-Datei angegeben werden

# Beispiel: Diese YAML-Datei liegt in /Workspace/Shared/databricks-devops-for-pipeline-source/Source/Databricks Devops for Pipelines/resrouces/job/ und Run Unit Tests liegt in /Workspace/Shared/databricks-devops-for-pipeline-source/Source/Databricks Devops for Pipelines/. In diesem Fall wäre notebook_path ../../Run Unit Tests.ipynb. 

resources:
  jobs:
    health_etl_workflow:    # <----- Name des auszuführenden Jobs
      name: health_etl_workflow_${bundle.target}  # <---- Job name
      description: Final Workflow SDK
      email_notifications:
        on_failure:
          - ${var.my_email}
      tasks:
        - task_key: Unit_Tests
          notebook_task:
            notebook_path: ../../run_unit_tests.ipynb #<----- Relativ zum Speicherort der Datei dabs_workflow.job.yml
            # notebook_path: ../src/test.ipynb
            source: WORKSPACE
          description: Execute unit tests for project.
        - task_key: Visualization
          depends_on:
            - task_key: Health_ETL
          notebook_task:
            notebook_path: ../../src/Final Visualization.ipynb #<----- Relativ zum Speicherort der Datei databricks.yml
            base_parameters:
              catalog_name: ${var.target_catalog}
            source: WORKSPACE
          description: Final visualization for project.
        - task_key: Health_ETL
          depends_on:
            - task_key: Unit_Tests
          pipeline_task:
            pipeline_id: ${resources.pipelines.health_etl_pipeline.id}
            full_refresh: true
          description: Spark Declarative Pipeline
      
      ####################################################
      # Dynamische Job-Parameter auf Basis unserer Variablen    #
      ####################################################
      parameters:
        - name: target
          default: ${bundle.target}
        - name: catalog_name
          default: ${var.target_catalog}
```
