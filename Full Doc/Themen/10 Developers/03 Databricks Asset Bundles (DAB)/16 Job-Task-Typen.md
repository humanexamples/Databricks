# Job-Task-Typen (Referenz)

Referenz aller Task-Typen, die sich innerhalb eines `jobs`-Ressourcenblocks in `databricks.yml` verwenden lassen, mit den jeweils wichtigsten Feldern. Ergänzt die Ressourcenübersicht in [15 Ressourcentypen (Referenz).md](15%20Ressourcentypen%20%28Referenz%29.md). Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Übersichtstabelle](#uebersicht)
2. [Gemeinsame Task-Einstellungen](#gemeinsam)
3. [Quelle](#quelle)

---

## <a id="uebersicht">1. Übersichtstabelle</a>

| Task-Typ (Mapping-Key) | Wichtige Felder | Besonderheiten |
|---|---|---|
| **AI-Runtime-Task** (`ai_runtime_task`) | `deployments`, `experiment`, `mlflow_experiment_directory`, `mlflow_run` | Multi-GPU-Compute-Workloads auf Databricks AI Runtime, z. B. Training auf 8-GPU-H100-Knoten mit MLflow-Tracking |
| **Alert-Task (v2)** (`alert_task`) | `alert_id`, `workspace_path`, `warehouse_id`, `subscribers` | wertet einen Alert aus und benachrichtigt Subscriber; Identifikation per ID oder Workspace-Pfad |
| **Clean-Room-Notebook-Task** (`clean_rooms_notebook_task`) | `clean_room_name`, `notebook_name`, `object`, `etag` | führt Notebooks innerhalb von Databricks Clean Rooms aus, unterstützt Base Parameters |
| **Condition-Task** (`condition_task`) | `left`, `op`, `right` | If/Else-Verzweigungslogik mit Operatoren wie `EQUAL_TO`, `GREATER_THAN`; Operanden können String, Job-State oder dynamische Wertreferenz sein |
| **Dashboard-Task** (`dashboard_task`) | `dashboard_id`, `warehouse_id`, `subscription` | aktualisiert ein Dashboard und versendet Snapshots an Subscriber; erfordert bestehende Dashboard-ID |
| **dbt-Task** (`dbt_task`) | `commands`, `project_directory`, `warehouse_id`, `catalog`, `schema`, `profiles_directory`, `source` | führt dbt-Befehle sequenziell aus (max. 10 Befehle); Projekt-Quelle aus Workspace oder Git |
| **For-Each-Task** (`for_each_task`) | `inputs`, `task`, `concurrency` | iteriert über Array-Eingaben und führt einen verschachtelten Task aus; unterstützt parallele Iteration mit Concurrency-Limit — jedes Array-Element wird einer Iteration übergeben |
| **JAR-Task** (`spark_jar_task`) | `main_class_name`, `parameters`, `jar_uri` (deprecated) | führt Java-/Scala-Code über JAR-Dateien aus; statt des veralteten `jar_uri` das `libraries`-Feld nutzen |
| **Notebook-Task** (`notebook_task`) | `notebook_path`, `base_parameters`, `source`, `warehouse_id` | führt Workspace- oder Git-Notebooks aus; Parameterübergabe via `base_parameters` |
| **Pipeline-Task** (`pipeline_task`) | `pipeline_id`, `full_refresh` | löst eine Spark-Declarative-Pipeline aus; Boolean-Flag steuert Full-Refresh vs. inkrementell |
| **Power-BI-Task** (`power_bi_task`) | `connection_resource_name`, `power_bi_model`, `tables`, `warehouse_id`, `refresh_after_update` | aktualisiert Power-BI-Semantikmodelle aus Databricks-Daten; aktuell Public Preview |
| **Python-Script-Task** (`spark_python_task`) | `python_file`, `parameters`, `source` | führt Python-Dateien aus Workspace oder Git aus; Workspace-Pfade müssen absolut, Git-Pfade relativ sein |
| **Python-Wheel-Task** (`python_wheel_task`) | `package_name`, `entry_point`, `parameters`, `named_parameters` | führt Python-Pakete mit positionalen oder benannten Argumenten aus; `parameters` und `named_parameters` schließen sich gegenseitig aus |
| **Run-Job-Task** (`run_job_task`) | `job_id`, `job_parameters`, `pipeline_params` | führt einen bestehenden Job innerhalb eines anderen Job-Workflows aus; übergibt Job-Parameter an den Ziel-Job |
| **SQL-Task** (`sql_task`) | `warehouse_id`, `file`, `query`, `alert`, `dashboard`, `parameters` | unterstützt SQL-Dateien, Queries, Alerts oder Dashboard-Refreshes; erfordert SQL-Warehouse-ID; Parameterreferenzen über `{{parameter_key}}` |

## <a id="gemeinsam">2. Gemeinsame Task-Einstellungen</a>

Unabhängig vom Task-Typ unterstützen alle Tasks: `task_key`, `depends_on`, `description`, `timeout_seconds`, `max_retries`, `min_retry_interval_millis`, `retry_on_timeout`, `libraries` (siehe [22 Bibliotheksabhaengigkeiten.md](22%20Bibliotheksabhaengigkeiten.md)), `email_notifications`, `webhook_notifications`, `notification_settings`, `run_if`, `existing_cluster_id`, `new_cluster`, `job_cluster_key`, `environment_key`, `disable_auto_optimization`, `health` und `compute`.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/bundles/job-task-types

**Stand:** 2026-08-26.
