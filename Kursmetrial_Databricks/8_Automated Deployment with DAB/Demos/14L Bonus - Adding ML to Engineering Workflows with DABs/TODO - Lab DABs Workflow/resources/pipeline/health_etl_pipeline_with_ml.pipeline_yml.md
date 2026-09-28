# 14L Bonus - Adding ML to Engineering Workflows with DABs/TODO - Lab DABs Workflow/resources/pipeline/health_etl_pipeline_with_ml.pipeline.yml

```yaml
######################################
# THE SDP PIPELINE CONFIGURATION     #
######################################
# HINWEIS: Der Notebook-Pfad muss relativ zum Speicherort der YAML-Datei angegeben werden

resources:
  pipelines:
    health_etl_pipeline:
      name: health_etl_pipeline_with_ml_${bundle.target}
      libraries:
        - glob:
            include: ../../src/dlt_pipelines/gold_tables_dlt.sql
        - glob:
            include: ../../src/dlt_pipelines/ingest-bronze-silver_dlt.py
        - glob:
            include: ../../tests/integration_test/integration_tests_dlt
        - glob:
            include: ../../src/dlt_pipelines/silver_sample_dlt.sql
      schema: ${var.schema}
      photon: true
      catalog: ${var.target_catalog}
      serverless: true
      root_path: ../../src/dlt_pipelines
      configuration:
        target: ${bundle.target}
        raw_data_path: ${var.raw_data_path}
```
