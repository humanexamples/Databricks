# 13 Demo - Continuous Integration and Continuous Deployment with DABs/Full Project/databricks.yml

```yaml
bundle:
  name: health_etl_bundle


include:
  - "./resources/variables.yml" 
  - "./resources/pipeline/health_etl_pipeline.pipeline.yml" # Declarative Pipeline resource
  - "./resources/job/dabs_workflow.job.yml" # Job resources


targets:

  development:
    mode: development
    default: true
    resources:
      jobs:
        health_etl_workflow:    # <----- Name des auszuführenden Jobs
          name: health_etl_workflow_${bundle.target}  # <---- Job name
          tasks:
            - task_key: Unit_Tests
              existing_cluster_id: ${var.cluster_id}
            - task_key: Visualization
              existing_cluster_id: ${var.cluster_id}
    workspace:
      # host: Host kann geändert werden, wenn nach Workspace isoliert wird
      # Wir geben /Workspace/Users/username explizit an, damit nur eine einzige Kopie existiert.
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}


  stage:
    mode: development
      # In Stage verwenden wir für unsere Tasks Classic Compute 
    resources:
      jobs:
        health_etl_workflow:    # <----- Name des auszuführenden Jobs
          name: health_etl_workflow_${bundle.target}  # <---- Job name
          tasks:
            - task_key: Unit_Tests
              existing_cluster_id: ${var.cluster_id}
            - task_key: Visualization
              existing_cluster_id: ${var.cluster_id}
    workspace:
      # host: Host kann geändert werden, wenn nach Workspace isoliert wird
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}
    variables:
      target_catalog: ${var.catalog_stage}
      raw_data_path: /Volumes/${var.catalog_stage}/default/health


  production:
    mode: production
    workspace:
      # host: Host kann geändert werden, wenn nach Workspace isoliert wird
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}
    variables:
      target_catalog: ${var.catalog_prod}
      raw_data_path: /Volumes/${var.catalog_prod}/default/health
```
