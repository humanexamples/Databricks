# Azure DevOps Integration

Vollständiges Setup einer CI/CD-Pipeline mit Azure DevOps: Python-Wheel bauen, Unit Tests ausführen, Notebooks in einen Databricks-Workspace deployen — getrennte Build- und Release-Pipeline. Teil der [CI/CD](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Voraussetzungen](#voraussetzungen)
2. [Repository-Dateistruktur](#dateistruktur)
3. [Bundle-Konfiguration](#bundle-config)
4. [Build-Pipeline-Definition](#build-pipeline)
5. [Release-Pipeline-Konfiguration](#release-pipeline)
6. [Manuelle Pipeline-Ausführung](#ausfuehrung)
7. [Architektur-Hinweise](#architektur)
8. [Quelle](#quelle)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

- Aktives Azure-DevOps-Projekt.
- Mit Azure DevOps verbundenes Git-Repository.
- Microsoft-Entra-ID-Service-Principal mit Databricks-OAuth-Credentials.
- Grundverständnis von CI/CD-Workflows.

## <a id="dateistruktur">2. Repository-Dateistruktur</a>

### Python-Wheel-Komponente

```
└── Libraries
    └── python
        └── dabdemo
            ├── dabdemo
            │   ├── __init__.py
            │   ├── __main__.py
            │   ├── addcol.py
            │   └── test_addcol.py
            └── setup.py
```

**`addcol.py`** (Kernfunktion):

```python
import pyspark.sql.functions as F

def with_status(df):
  return df.withColumn("status", F.lit("checked"))
```

**`test_addcol.py`** (Unit Test):

```python
import pytest
from pyspark.sql import SparkSession
from dabdemo.addcol import *

class TestAppendCol(object):
  def test_with_status(self):
    spark = SparkSession.builder.getOrCreate()
    source_data = [
      ("paula", "white", "paula.white@example.com"),
      ("john", "baer", "john.baer@example.com")
    ]
    source_df = spark.createDataFrame(
      source_data,
      ["first_name", "last_name", "email"]
    )
    actual_df = with_status(source_df)
    expected_data = [
      ("paula", "white", "paula.white@example.com", "checked"),
      ("john", "baer", "john.baer@example.com", "checked")
    ]
    expected_df = spark.createDataFrame(
      expected_data,
      ["first_name", "last_name", "email", "status"]
    )
    assert(expected_df.collect() == actual_df.collect())
```

**`__init__.py`:**

```python
__version__ = '0.0.1'
__author__ = '<my-author-name>'
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
```

**`__main__.py`:**

```python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from addcol import *

def main():
  pass

if __name__ == "__main__":
  main()
```

**`setup.py`:**

```python
from setuptools import setup, find_packages
import dabdemo

setup(
  name = "dabdemo",
  version = dabdemo.__version__,
  author = dabdemo.__author__,
  url = "https://<my-url>",
  author_email = "<my-author-name>@<my-organization>",
  description = "<my-package-description>",
  packages = find_packages(include = ["dabdemo"]),
  entry_points={"group_1": "run=dabdemo.__main__:main"},
  install_requires = ["setuptools"]
)
```

### Test- und Anwendungs-Notebooks

**`run_unit_tests.py`:**

```python
# Databricks notebook source
# COMMAND ----------
# MAGIC %sh
# MAGIC
# MAGIC mkdir -p "/Workspace${WORKSPACEBUNDLEPATH}/Validation/reports/junit/test-reports"
# COMMAND ----------
import sys, pytest, os

sys.dont_write_bytecode = True

retcode = pytest.main([
  "--junit-xml",
  f"/Workspace{os.getenv('WORKSPACEBUNDLEPATH')}/Validation/reports/junit/test-reports/TEST-libout.xml",
  f"/Workspace{os.getenv('WORKSPACEBUNDLEPATH')}/files/Libraries/python/dabdemo/dabdemo/"
])

assert retcode == 0, "The pytest invocation failed. See the log for details."
```

**`dabdemo_notebook.py`:**

```python
# Databricks notebook source
# COMMAND ----------
dbutils.library.restartPython()
# COMMAND ----------
from dabdemo.addcol import with_status

df = (spark.createDataFrame(
  schema = ["first_name", "last_name", "email"],
  data = [
    ("paula", "white", "paula.white@example.com"),
    ("john", "baer", "john.baer@example.com")
  ]
))

new_df = with_status(df)
display(new_df)
```

## <a id="bundle-config">3. Bundle-Konfiguration</a>

**`databricks.yml`:**

```yaml
bundle:
  name: <bundle-name>

variables:
  job_prefix:
    description: A unifying prefix for this bundle's job and task names.
    default: <job-prefix-name>
  spark_version:
    description: The cluster's Spark version ID.
    default: <spark-version-id>
  node_type_id:
    description: The cluster's node type ID.
    default: <cluster-node-type-id>

artifacts:
  dabdemo-wheel:
    type: whl
    path: ./Libraries/python/dabdemo

resources:
  jobs:
    run-unit-tests:
      name: ${var.job_prefix}-run-unit-tests
      tasks:
        - task_key: ${var.job_prefix}-run-unit-tests-task
          new_cluster:
            spark_version: ${var.spark_version}
            node_type_id: ${var.node_type_id}
            num_workers: 1
            spark_env_vars:
              WORKSPACEBUNDLEPATH: ${workspace.root_path}
          notebook_task:
            notebook_path: ./run_unit_tests.py
            source: WORKSPACE
          libraries:
            - pypi:
                package: pytest

    run-dabdemo-notebook:
      name: ${var.job_prefix}-run-dabdemo-notebook
      tasks:
        - task_key: ${var.job_prefix}-run-dabdemo-notebook-task
          new_cluster:
            spark_version: ${var.spark_version}
            node_type_id: ${var.node_type_id}
            num_workers: 1
            spark_env_vars:
              WORKSPACEBUNDLEPATH: ${workspace.root_path}
          notebook_task:
            notebook_path: ./dabdemo_notebook.py
            source: WORKSPACE
          libraries:
            - whl: '/Workspace${workspace.root_path}/files/Libraries/python/dabdemo/dist/dabdemo-0.0.1-py3-none-any.whl'

targets:
  dev:
    mode: development
```

## <a id="build-pipeline">4. Build-Pipeline-Definition</a>

In Azure DevOps Pipelines: **`azure-pipelines.yml`**:

```yaml
trigger:
  - release

pool:
  vmImage: ubuntu-22.04

steps:
  - checkout: self
    persistCredentials: true
    clean: true

  - script: |
      git diff --name-only --diff-filter=AMR HEAD^1 HEAD | xargs -I '{}' cp --parents -r '{}' $(Build.BinariesDirectory)
      mkdir -p $(Build.BinariesDirectory)/Libraries/python/dabdemo/dabdemo
      cp $(Build.Repository.LocalPath)/Libraries/python/dabdemo/dabdemo/*.* $(Build.BinariesDirectory)/Libraries/python/dabdemo/dabdemo
      cp $(Build.Repository.LocalPath)/Libraries/python/dabdemo/setup.py $(Build.BinariesDirectory)/Libraries/python/dabdemo
      cp $(Build.Repository.LocalPath)/*.* $(Build.BinariesDirectory)
    displayName: 'Get Changes'

  - task: ArchiveFiles@2
    inputs:
      rootFolderOrFile: '$(Build.BinariesDirectory)'
      includeRootFolder: false
      archiveType: 'zip'
      archiveFile: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
      replaceExistingArchive: true

  - task: PublishBuildArtifacts@1
    inputs:
      ArtifactName: 'DatabricksBuild'
```

**Kernkonfiguration:** Trigger bei Merges auf den `release`-Branch; Ubuntu-22.04-Agent; sammelt geänderte Dateien via `git diff`; archiviert Dateien als Zip-Artefakt für die Release-Pipeline.

## <a id="release-pipeline">5. Release-Pipeline-Konfiguration</a>

### 5.1 Umgebungsvariablen (Scope: Stage 1)

| Variable | Wert |
|---|---|
| `BUNDLE_TARGET` | `dev` (entspricht dem Target in `databricks.yml`) |
| `DATABRICKS_HOST` | `https://adb-<workspace-id>.<random>.azuredatabricks.net` |
| `DATABRICKS_CLIENT_ID` | Application ID des Service Principal |
| `DATABRICKS_CLIENT_SECRET` | OAuth Secret des Service Principal |

### 5.2 Agent-Konfiguration

Agent Pool: Azure Pipelines; Agent Specification: `ubuntu-22.04`.

### 5.3–5.10 Task-Sequenz

1. **Use Python Version** — Version Spec `3.10`.
2. **Extract files** — Archive-Datei-Pattern `**/*.zip`, Zielordner `$(Release.PrimaryArtifactSourceAlias)/Databricks`.
3. **Environment Variables** — `BUNDLE_ROOT=$(Agent.ReleaseDirectory)/$(Release.PrimaryArtifactSourceAlias)/Databricks`.
4. **Bash (Inline)** — Databricks CLI und Python-Wheel-Build-Tools installieren:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
   pip install wheel
   ```
5. **Bash (Inline)** — Bundle validieren: `databricks bundle validate -t $(BUNDLE_TARGET)`.
6. **Bash (Inline)** — Bundle deployen: `databricks bundle deploy -t $(BUNDLE_TARGET)`.
7. **Bash (Inline)** — Unit Tests ausführen: `databricks bundle run -t $(BUNDLE_TARGET) run-unit-tests`.
8. **Bash (Inline)** — Anwendungs-Notebook ausführen: `databricks bundle run -t $(BUNDLE_TARGET) run-dabdemo-notebook`.

## <a id="ausfuehrung">6. Manuelle Pipeline-Ausführung</a>

**Build-Pipeline:** Pipelines > Pipelines → Build-Pipeline wählen → „Run pipeline" → `release`-Branch wählen → „Run" → Job-Logs überwachen.

**Release-Pipeline:** nach erfolgreichem Build zu Pipelines > Releases → Release-Pipeline wählen → „Create release" → „Create" → Logs in Stage 1 überwachen.

## <a id="architektur">7. Architektur-Hinweise</a>

„Die Trennung von Build- und Release-Pipeline erlaubt es, ein Build-Artefakt zu erstellen, ohne es zu deployen, oder gleichzeitig Artefakte aus mehreren Builds zu deployen."

**Ablauf:** Git-Commit löst Build-Pipeline auf dem `release`-Branch aus → Build-Agent sammelt Dateien und erstellt Zip-Artefakt → Release-Pipeline extrahiert das Artefakt → Databricks CLI validiert, deployt und führt Jobs aus → Ergebnisse werden in Azure-DevOps-Logs berichtet. Diese Trennung von Artefakterzeugung und Deployment unterstützt mehrere Deployment-Szenarien und ermöglicht Qualitäts-Gates zwischen den Stufen.

## <a id="quelle">8. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/ci-cd/azure-devops

**Stand:** 2026-08-21.
