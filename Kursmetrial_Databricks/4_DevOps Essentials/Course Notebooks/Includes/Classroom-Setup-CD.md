```python
%run ./Classroom-Setup-Common
```

---

```python
## Die DA-Schlüssel für die Kataloge des Benutzers erstellen
DA.create_DA_keys()

## Kurskatalog und Schemanamen für den Benutzer anzeigen.
DA.display_config_values(
  [
    ('DEV catalog reference: DA.catalog_dev', DA.catalog_dev),
    ('STAGE catalog reference: DA.catalog_stage', DA.catalog_stage),
    ('PROD catalog reference: DA.catalog_prod', DA.catalog_prod)
   ]
)
```

---

```python
def obtain_pipeline_id_or_create_if_not_exists():
    '''
    Checks to see if the required Spark Declarative Pipeline is created from the previous demo.

    If the job exists it returns the pipeline id.

    If the job does not exist it creates the Spark Declarative Pipeline and returns the pipeline id.
    '''
    from databricks.sdk.service import pipelines
    from databricks.sdk import WorkspaceClient
    w = WorkspaceClient()

    try:
        # Neue Art, die Pipeline zu deklarieren
        pipeline = DeclarativePipelineCreator(
                            pipeline_name=f"sdk_health_etl_{DA.catalog_dev}", 
                            catalog_name = DA.catalog_name,
                            schema_name = 'default',
                            root_path_folder_name='src',
                            source_folder_names=[
                                'src/sdp/**', 
                                'tests/integration_test/**'],
                            configuration = {
                                'target': 'dev',
                                'raw_data_path':f'/Volumes/{DA.catalog_name}/default/health'
                            })

        # print(f'----- Pipeline sdk_health_etl_{DA.catalog_dev} not found for the demonstration -----')

        pipeline.create_pipeline()
        pipeline.start_pipeline()
        return pipeline.pipeline_id
    except:
        for pipeline in w.pipelines.list_pipelines():
            if pipeline.name == f"sdk_health_etl_{DA.catalog_dev}":
                print('Pipeline found and pipeline id has been stored')
                return pipeline.pipeline_id
```

---

```python
def create_demo_cd_job(my_pipeline_id, job_name):
    import os
    from databricks.sdk.service import jobs
    from databricks.sdk import WorkspaceClient

    email_me = [DA.username] # Die E-Mail über das DA-Objekt ermitteln 
    target_catalog = DA.catalog_name

    ## Eine Instanz der Klasse WorkspaceClient aus dem Databricks SDK erstellen
    w = WorkspaceClient()

    ## Fehler, wenn der Job-Name bereits existiert
    for job in w.jobs.list():
        if job.settings.name == job_name:
            test_job_name = False
            assert test_job_name, f'You already have a job with the same name. Please manually delete the job {job_name}'


    ## Den Pfad des Hauptkursordners (2 Ordner zurück) speichern
    current_path = os.path.dirname(os.path.dirname(os.getcwd()))


    ##
    ## Create individual tasks
    ##
    ## Unit tests task
    unit_tests_notebook_path = f'{current_path}/Run Unit Tests'
    task_unit_tests = jobs.Task(task_key="Unit_Tests",
                                description="Execute unit tests for project.",
                                notebook_task=jobs.NotebookTask(notebook_path=unit_tests_notebook_path),
                                timeout_seconds=0)


    ## SDP Execution
    task_sdp = jobs.Task(task_key="Health_ETL",
                        description="Spark Declarative Pipeline",
                        pipeline_task=jobs.PipelineTask(pipeline_id=my_pipeline_id, full_refresh=True),
                        depends_on = [
                                    jobs.TaskDependency(task_key="Unit_Tests")
                                ],
                        timeout_seconds=0)



    ## Data visualization task
    visualization_notebook_path = f'{current_path}/src/Final Visualization'
    task_visualization = jobs.Task(task_key="Visualization",
                                description="Final visualization for project.",
                                notebook_task=jobs.NotebookTask(
                                    notebook_path=visualization_notebook_path,
                                    base_parameters = {'catalog_name': DA.catalog_name} # Den Katalognamen über das DA-Objekt ermitteln
                                    ),
                                depends_on = [
                                    jobs.TaskDependency(task_key="Health_ETL")
                                ],
                                timeout_seconds=0)



    ##
    ## Den gesamten Job mit den obigen Tasks erstellen
    ##
    created_job = w.jobs.create(
            name=job_name,
            description='Final Workflow SDK',
            tasks=[
                task_unit_tests,
                task_visualization,
                task_sdp
                ],
            parameters = [
                    jobs.JobParameterDefinition(name='target', default='dev'),
                    jobs.JobParameterDefinition(name='catalog_name', default=target_catalog)
                ]
            )
    
    print('Creating Workflow using the Databricks SDK for the demonstration.')
```
