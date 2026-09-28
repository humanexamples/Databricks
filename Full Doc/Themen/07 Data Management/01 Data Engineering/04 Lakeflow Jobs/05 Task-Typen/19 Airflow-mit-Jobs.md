# Lakeflow Jobs mit Apache Airflow orchestrieren

Apache Airflow lässt sich über den quelloffenen Databricks-Provider zur Orchestrierung von Databricks-Jobs nutzen. **Hinweis:** Diese Pakete (Databricks-Provider für Airflow, inkl. Airflow-Operatoren) werden nicht direkt von Databricks unterstützt.

Airflow bildet Datenpipelines als gerichtete azyklische Graphen (DAGs) von Operationen ab.

## Voraussetzungen

- Airflow 2.5.0+ (getestet mit 2.6.1).
- Python 3.8–3.11 (getestet mit 3.8).
- `pipenv` für virtuelle Python-Umgebungen.

## Databricks-Operatoren für Airflow

| Operator | Verhalten |
|---|---|
| `DatabricksRunNowOperator` | benötigt einen bestehenden Databricks-Job, nutzt `POST /api/2.1/jobs/run-now` |
| `DatabricksSubmitRunOperator` | benötigt keinen bestehenden Job, nutzt `POST /api/2.1/jobs/runs/submit` |
| `DatabricksCreateJobsOperator` | erstellt/setzt Jobs zurück über `POST /api/2.1/jobs/create`/`reset` |

Databricks empfiehlt `DatabricksRunNowOperator` — reduziert doppelte Job-Definitionen, ausgelöste Läufe erscheinen in der Jobs-UI.

## Installation

```bash
mkdir airflow
cd airflow
pipenv --python 3.8
pipenv shell
export AIRFLOW_HOME=$(pwd)
pipenv install apache-airflow
pipenv install apache-airflow-providers-databricks
mkdir dags
airflow db init
airflow users create --username admin --firstname <firstname> --lastname <lastname> --role Admin --email <email>
```

## Airflow starten

**Webserver:**

```bash
pipenv shell
export AIRFLOW_HOME=$(pwd)
airflow webserver
```

**Scheduler** (neues Terminal):

```bash
pipenv shell
export AIRFLOW_HOME=$(pwd)
airflow scheduler
```

## Installation testen

`http://localhost:8080/home` öffnen, einloggen, ein Beispiel-DAG (z. B. `example_python_operator`) entpausieren, **Trigger DAG**, DAG-Namen anklicken zur Lauf-Ansicht.

## Personal Access Token

Als Sicherheits-Best-Practice empfiehlt Databricks OAuth-Tokens; alternativ Personal Access Tokens von Service Principals (statt Workspace-Nutzern).

## Databricks-Connection konfigurieren

`http://localhost:8080/connection/list/` → `databricks_default` bearbeiten → **Host** auf die Workspace-Instanz setzen (z. B. `https://adb-123456789.cloud.databricks.com`) → Token ins **Password**-Feld → **Save**.

## Beispiel: Airflow-DAG für einen Databricks-Job

**Schritt 1 — Notebook erstellen:**

```python
dbutils.widgets.text("greeting", "world", "Greeting")
greeting = dbutils.widgets.get("greeting")
```

```python
print("hello {}".format(greeting))
```

**Schritt 2 — Job erstellen:** Notebook-Task mit Parameter `greeting` = `Airflow user`, Job-ID aus dem Job-Details-Panel kopieren.

**Schritt 3 — Airflow-DAG erstellen** (`airflow/dags/databricks_dag.py`):

```python
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.utils.dates import days_ago

default_args = {
  'owner': 'airflow'
}

with DAG('databricks_dag',
  start_date = days_ago(2),
  schedule_interval = None,
  default_args = default_args
  ) as dag:
  opr_run_now = DatabricksRunNowOperator(
    task_id = 'run_now',
    databricks_conn_id = 'databricks_default',
    job_id = JOB_ID
  )
```

`JOB_ID` durch die tatsächliche Job-ID ersetzen.

**Schritt 4 — DAG auslösen und prüfen:** `http://localhost:8080/home` → `databricks_dag` entpausieren → **Trigger DAG** → Lauf in Spalte **Runs** öffnen.

## Quelle

- https://docs.databricks.com/aws/en/jobs/how-to/use-airflow-with-jobs
