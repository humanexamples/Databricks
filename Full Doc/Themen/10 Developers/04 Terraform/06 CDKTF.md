# CDKTF (Cloud Development Kit for Terraform)

Terraform-CDK mit Python für Databricks-Ressourcen — inklusive der ausdrücklichen Empfehlung, CDKTF **nicht** mehr zu verwenden. Teil der [Terraform](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Wichtiger Hinweis: nicht mehr empfohlen](#hinweis)
2. [Systemvoraussetzungen](#voraussetzungen)
3. [Projekt-Setup](#setup)
4. [Ressourcen definieren](#ressourcen)
5. [Deployment](#deployment)
6. [Ressourcen nutzen und ändern](#nutzen)
7. [Testing](#testing)
8. [Quelle](#quelle)

---

## <a id="hinweis">1. Wichtiger Hinweis: nicht mehr empfohlen</a>

„Databricks empfiehlt nicht, das Cloud Development Kit for Terraform (CDKTF) zur Verwaltung von Databricks-Ressourcen zu verwenden." HashiCorp hat das Sunset von CDKTF angekündigt — das Projekt erhält keine aktive Weiterentwicklung oder Support mehr. Die offizielle Empfehlung lautet, stattdessen direkt den Databricks-Terraform-Provider zu nutzen (siehe [01 Grundlagen.md](01%20Grundlagen.md)).

Für alle, die dennoch mit CDKTF fortfahren, dokumentiert dieser Abschnitt die Umsetzung mit Python und dem Terraform-CDK-Databricks-Provider.

## <a id="voraussetzungen">2. Systemvoraussetzungen</a>

- Terraform 1.1 oder höher (`terraform -v`).
- Node.js 16.13+ und npm (`node -v`, `npm -v`).
- CDKTF CLI (via npm installieren, `cdktf --version` prüfen).
- Python 3.7+ und pipenv 2021.5.29+ (`python --version`, `pipenv --version`).
- konfigurierte Databricks-Authentifizierung.
- ein bestehender Databricks-Workspace für das Deployment.

## <a id="setup">3. Projekt-Setup</a>

### Schritt 1 — CDKTF-Projekt initialisieren

```bash
mkdir cdktf-demo
cd cdktf-demo
cdktf init --template=python --local
```

Standardwerte für Projektname/-beschreibung übernehmen; Optionen für bestehende Terraform-Projekte und Crash-Reporting ablehnen.

Generiert: `.gitignore`, `cdktf.json`, `main.py`, `main-test.py`, `Pipfile`/`Pipfile.lock`.

## <a id="ressourcen">4. Ressourcen definieren</a>

```bash
pipenv install cdktf-cdktf-provider-databricks
```

`main.py` (erstellt ein Notebook und einen Job, der es ausführt):

```python
#!/usr/bin/env python
from constructs import Construct
from cdktf import (App, TerraformStack, TerraformOutput)
from cdktf_cdktf_provider_databricks import (
  data_databricks_current_user,
  job, notebook, provider)
import vars
from base64 import b64encode

class MyStack(TerraformStack):
  def __init__(self, scope: Construct, ns: str):
    super().__init__(scope, ns)
    provider.DatabricksProvider(
      scope = self,
      id    = "databricksAuth"
    )
    current_user = data_databricks_current_user.DataDatabricksCurrentUser(
      scope     = self,
      id_       = "currentUser"
    )

    my_notebook = notebook.Notebook(
      scope          = self,
      id_            = "notebook",
      path           = f"{current_user.home}/CDKTF/{vars.resource_prefix}-notebook.py",
      language       = "PYTHON",
      content_base64 = b64encode(b"display(spark.range(10))").decode("UTF-8")
    )

    my_job = job.Job(
      scope = self,
      id_ = "job",
      name = f"{vars.resource_prefix}-job",
      task = [
         job.JobTask(
          task_key = f"{vars.resource_prefix}-task",
          new_cluster = job.JobTaskNewCluster(
            num_workers   = vars.num_workers,
            spark_version = vars.spark_version,
            node_type_id  = vars.node_type_id
          ),
          notebook_task = job.JobTaskNotebookTask(
            notebook_path = f"{current_user.home}/CDKTF/{vars.resource_prefix}-notebook.py"
          ),
          email_notifications = job.JobTaskEmailNotifications(
            on_success = [ current_user.user_name ],
            on_failure = [ current_user.user_name ]
          )
        )
      ]
    )

    TerraformOutput(
      scope = self,
      id    = "Notebook URL",
      value = my_notebook.url
    )
    TerraformOutput(
      scope = self,
      id    = "Job URL",
      value = my_job.url
    )

app = App()
MyStack(app, "cdktf-demo")
app.synth()
```

`vars.py`:

```python
#!/usr/bin/env python
resource_prefix = "cdktf-demo"
num_workers     = 1
spark_version   = "14.3.x-scala2.12"
node_type_id    = "i3.xlarge"
```

## <a id="deployment">5. Deployment</a>

```bash
cdktf synth
cdktf diff
cdktf deploy
```

Bei der Bestätigungsabfrage Enter drücken.

## <a id="nutzen">6. Ressourcen nutzen und ändern</a>

Zugriff über die im Deployment-Output gelieferten URLs (Notebook-URL, Job-URL — „Run now" zum Ausführen). Um Ressourcen zu ändern: Notebook-Inhalt in `main.py` anpassen, dann `cdktf synth`, `cdktf diff`, `cdktf deploy` erneut ausführen. Hinweis: Python-Code innerhalb dreifacher Anführungszeichen muss korrekt eingerückt bleiben, um Whitespace-Probleme zu vermeiden.

**Aufräumen:**

```bash
cdktf destroy
```

## <a id="testing">7. Testing</a>

```python
from cdktf import App, Testing
from cdktf_cdktf_provider_databricks import job, notebook
from main import MyStack

class TestMain:
  app = App()
  stack = MyStack(app, "cdktf-demo")
  synthesized = Testing.synth(stack)

  def test_notebook_should_have_expected_base64_content(self):
    assert Testing.to_have_resource_with_properties(
      received = self.synthesized,
      resource_type = notebook.Notebook.TF_RESOURCE_TYPE,
      properties = {
        "content_base64": "ZGlzcGxheShzcGFyay5yYW5nZSgxMCkp"
      }
    )

  def test_job_should_have_expected_job_name(self):
    assert Testing.to_have_resource_with_properties(
      received = self.synthesized,
      resource_type = job.Job.TF_RESOURCE_TYPE,
      properties = {
        "name": "cdktf-demo-job"
      }
    )
```

Ausführen mit `pytest` vom Projekt-Root aus.

## <a id="quelle">8. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/terraform/cdktf

**Stand:** 2026-08-21.
