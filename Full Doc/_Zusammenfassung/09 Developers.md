# 10 Developers — Übersicht

Dieses Dokument bündelt alle Themen aus dem Kursordner `10 Developers` (82 Original-Dateien): Git Folders (Repos), CI/CD, Databricks Asset Bundles (Declarative Automation Bundles), Terraform, UDFs, Databricks Utils, Databricks SDK für Python sowie Authenticate developer tools. Jeder Abschnitt enthält eine kurze, einfache Erklärung sowie alle Code-Beispiele aus der jeweiligen Originaldatei.

## Inhaltsverzeichnis

- 1. Git Folders (Repos) — Überblick
- 2. Git Folders — Grundlagen
- 3. Git-Integration konfigurieren
- 4. Git-Operationen im Alltag
- 5. CI/CD und Automatisierung mit Git Folders
- 6. Administration und private Netzwerke (Git Folders)
- 7. Fehlerbehebung bei Git Folders
- 8. CI/CD — Überblick
- 9. CI/CD — Grundlagen und Empfehlungen
- 10. CI/CD-Workflows und Best Practices
- 11. Azure DevOps Integration
- 12. GitHub Actions Integration
- 13. Jenkins Integration
- 14. Terraform — Überblick
- 15. Terraform — Grundlagen
- 16. Terraform: Workspace bereitstellen und verwalten
- 17. Terraform: Cluster, Notebook und Job bereitstellen
- 18. Terraform: Unity Catalog automatisieren
- 19. Terraform: Service Principals bereitstellen
- 20. Terraform: CDKTF (Cloud Development Kit for Terraform)
- 21. Terraform: Fehlerbehebung
- 22. Überblick: Databricks Asset Bundles (Declarative Automation Bundles)
- 23. Grundlagen: Kernkomponenten und Lebenszyklus
- 24. Tutorials: Job, Pipeline und App mit Bundles
- 25. Python- und Scala-Artefakte in Bundles
- 26. Bundle-Templates
- 27. Konfiguration: databricks.yml
- 28. Bundles im Workspace (Web-UI)
- 29. Deployment-Modi und Authentifizierung
- 30. Zusammenarbeit und gemeinsame Dateien
- 31. Manuelle Bundle-Erstellung und Ressourcen-Migration
- 32. MLOps Stacks
- 33. Direct Deployment Engine
- 34. Air-Gapped-Umgebungen
- 35. FAQ
- 36. VS Code Extension
- 37. Ressourcentypen (Referenz)
- 38. Job-Task-Typen (Referenz)
- 39. Job-Parameter vs. Bundle-Variablen
- 40. Run As: Deployment- vs. Ausführungsidentität
- 41. Berechtigungen (Permissions)
- 42. Overrides zwischen Targets
- 43. Private Artefakte
- 44. Bibliotheksabhängigkeiten (libraries)
- 45. Beispiele (bundle-examples Repo)
- 46. Was sind User-Defined Functions (UDFs)?
- 47. SQL- und Python-UDFs in Unity Catalog: Erstellen, Aufrufen und Berechtigungen
- 48. Scala- und Java-UDFs in Unity Catalog: JAR bauen, registrieren, testen
- 49. Batch Python UDFs in Unity Catalog (`PARAMETER STYLE PANDAS`)
- 50. Python UDTFs (User-Defined Table Functions) in Unity Catalog
- 51. Python Scalar UDFs (Session-scoped)
- 52. Pandas UDFs (vektorisierte UDFs mit Apache Arrow)
- 53. Python UDTFs (Session-scoped)
- 54. Session-scoped Scala- und Java-UDFs
- 55. Scala User-Defined Aggregate Functions (UDAFs)
- 56. Task-Kontext in einer UDF abrufen (`TaskContext`)
- 57. Databricks Utils (`dbutils`) — Überblick
- 58. Credentials Utility (`dbutils.credentials`)
- 59. Data Utility (`dbutils.data`)
- 60. File System Utility (`dbutils.fs`)
- 61. Jobs Utility (`dbutils.jobs`)
- 62. Library Utility (`dbutils.library`)
- 63. Notebook Utility (`dbutils.notebook`)
- 64. Secrets Utility (`dbutils.secrets`)
- 65. Widgets Utility (`dbutils.widgets`)
- 66. Databricks SDK für Python
- 67. Authentifizierung für Entwicklerwerkzeuge — Überblick
- 68. Zugriff auf Databricks-Ressourcen autorisieren
- 69. OAuth Token Federation — Überblick
- 70. Federation Policy konfigurieren
- 71. Workload Identity Federation in CI/CD aktivieren — Provider-Übersicht
- 72. Provider: GitHub Actions
- 73. Provider: Azure DevOps Pipelines
- 74. Provider: AWS IAM Workloads
- 75. Provider: Terraform Cloud, Bitbucket Pipelines, Jenkins (und generische OIDC-Provider)
- 76. Mit einem IdP-Token authentifizieren (Token Exchange)
- 77. OAuth U2M — Benutzerzugriff autorisieren
- 78. Service Principals für CI/CD
- 79. Databricks Unified Authentication
- 80. Umgebungsvariablen und Felder für Unified Authentication
- 81. Konfigurationsprofile (`.databrickscfg`)
- 82. Personal Access Tokens (PAT) — Legacy
- 83. Blog: Arrow-optimierte Python-UDFs (Performance)
- 84. Blog: Terraform Databricks Modules (Community-Registry-Module)
- 85. Verifikationsprotokoll (Databricks-Blog-Abgleich)

---

## 1. Git Folders (Repos) — Überblick

**Einfach erklärt:** Databricks Git Folders (früher „Repos") sind die Brücke zwischen dem Databricks-Workspace und einem echten Git-Repository. Man kann darin klonen, branchen, committen und pushen, direkt aus der Databricks-Oberfläche heraus — so lassen sich Notebooks und Code wie normaler Software-Code versionieren. Dieses Kapitel besteht aus sechs Unterthemen (Grundlagen, Integration konfigurieren, Git-Operationen, CI/CD, Administration/private Netzwerke, Fehlerbehebung), die im Folgenden jeweils eigene Abschnitte bekommen.

Keine Code-Beispiele in dieser Datei — reiner Überblick/Inhaltsverzeichnis.

---

## 2. Git Folders — Grundlagen

**Einfach erklärt:** Git Folders sind ein visueller Git-Client plus API, der Git-Repositories direkt in den Databricks-Workspace integriert. Sie unterstützen die üblichen Git-Operationen (Klonen, Push, Pull, Branching, Merging), bieten einen visuellen Diff/Merge-Konflikt-Editor und lassen sich über verschiedene Cloud- und On-Premises-Git-Provider anbinden. Es gibt klare Regeln, welche Asset-Typen (Notebooks, Dateien, Ordner, Queries, Dashboards, Alerts) versioniert werden können und welche nicht (z. B. Legacy Alerts, MLflow-Experimente, Genie Agents).

**Unterstützte Cloud-Provider:** GitHub (inkl. GitHub Advanced Enterprise/Enterprise Cloud), Atlassian Bitbucket Cloud, GitLab/GitLab EE, Microsoft Azure DevOps (Azure Repos), AWS CodeCommit.

**Unterstützte On-Premises-Provider:** GitHub Enterprise Server, Bitbucket Server/Data Center, GitLab Self-Managed, Azure DevOps Server.

Keine Code-Beispiele in dieser Datei — reiner Konzeptüberblick (Fähigkeiten, API, Provider, Asset-Typen, Namensregeln).

---

## 3. Git-Integration konfigurieren

**Einfach erklärt:** Bevor man mit Git Folders arbeiten kann, müssen Git-Credentials (Personal Access Token oder OAuth) im Databricks-Workspace hinterlegt werden — entweder individuell pro Nutzer oder als geteiltes Credential für eine Gruppe/Rolle. Zusätzlich lässt sich die Commit-Identität (Name/E-Mail, wie Commits beim Provider erscheinen) konfigurieren, ebenso Netzwerkzugriff, Sicherheitsfeatures (URL-Allowlists, Secrets Detection, Audit Logging) und provider-spezifische Token-Erstellung (GitHub, GitLab, AWS CodeCommit, Azure DevOps, Bitbucket).

Keine Code-Beispiele in dieser Datei — ausschließlich UI-Klickpfade, Konfigurationsschritte und Provider-Tabellen (keine Fenced Code Blocks im Original).

---

## 4. Git-Operationen im Alltag

**Einfach erklärt:** Dieser Abschnitt beschreibt die Kern-Git-Operationen in Git Folders: Klonen (über UI oder Web-Terminal), Branch-Management, Commit/Push, Pull, Merge, Merge-Konflikt-Auflösung, Rebase, Reset, Sparse Checkout für große Repos sowie Team-Kollaborationsmuster. Wichtig: Nur ein Nutzer sollte gleichzeitig auf einem Git Folder arbeiten, und riskante Operationen wie Rebase/Reset schreiben die Historie um bzw. können Daten unwiderruflich löschen.

**Über das Web Terminal klonen:**

```bash
cd /Workspace/Users/<your-email>/<project>
git clone <remote-url>
```

---

## 5. CI/CD und Automatisierung mit Git Folders

**Einfach erklärt:** Für produktive Nutzung richten Admins spezielle „Produktions-Git-Folders" außerhalb der Nutzerverzeichnisse ein, die nur per Automatisierung (nach PR-Merge) aktualisiert werden — Entwickler arbeiten dagegen in eigenen Git Folders unter ihrem Nutzerpfad. Die Synchronisation der Produktions-Ordner erfolgt entweder über externe CI/CD-Tools oder über einen geplanten Job, der die Databricks-Repos-API aufruft. Für automatisierte Workflows wird ein Service Principal statt eines persönlichen Nutzer-Credentials empfohlen; Terraform kann sowohl den Service Principal als auch dessen Git-Credential zweistufig automatisieren (da Terraform-Provider-Konfigurationen vor der Ressourcenerstellung ausgewertet werden).

**Geplante Job-Automatisierung (Python/SDK):**

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
w.repos.update(w.workspace.get_status(path="<git-folder-workspace-full-path>").object_id, branch="<branch-name>")
```

**Service Principal per CLI erstellen:**

```bash
databricks service-principals create \
  --display-name "Git Automation Service Principal"
```

**OAuth Secret generieren:**

```bash
databricks service-principal-secrets-proxy create \
  <service-principal-id>
```

**CLI-Authentifizierung konfigurieren und Git-Credentials hinzufügen:**

```bash
export DATABRICKS_HOST=<workspace-url>
export DATABRICKS_CLIENT_ID=<application-id>
export DATABRICKS_CLIENT_SECRET=<oauth-secret>

databricks git-credentials create <git-provider> \
  --personal-access-token <git-pat> \
  --git-email <git-email>
```

**Terraform — Teil 1: Service Principal erstellen (Verzeichnis `setup/`):**

```terraform
terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

variable "databricks_host" {}
variable "databricks_admin_token" {
  sensitive = true
}
variable "service_principal_name" {}

provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_admin_token
}

resource "databricks_service_principal" "sp" {
  display_name = var.service_principal_name
}

resource "databricks_obo_token" "this" {
  application_id   = databricks_service_principal.sp.application_id
  comment          = "PAT on behalf of ${databricks_service_principal.sp.display_name}"
  lifetime_seconds = 3600
}

output "obo_token_value" {
  value     = databricks_obo_token.this.token_value
  sensitive = true
}
```

Ausführen:

```bash
terraform init
terraform apply
terraform output -raw obo_token_value
```

`terraform.tfvars` im Verzeichnis `git-credentials/` anlegen:

```terraform
databricks_host           = "https://<your-workspace>.cloud.databricks.com"
obo_token_value           = "<token from previous step>"
git_username              = "<your-git-username>"
git_provider              = "<gitHub|gitLab|azureDevOpsServices|...>"
git_personal_access_token = "<your-git-PAT>"
repo_url                  = "https://github.com/<your-org>/<your-repo>.git"
```

**Terraform — Teil 2: Git-Credentials konfigurieren (Verzeichnis `git-credentials/`):**

```terraform
terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

variable "databricks_host" {}
variable "obo_token_value" {
  sensitive = true
}
variable "git_username" {}
variable "git_provider" {}
variable "git_personal_access_token" {
  sensitive = true
}
variable "repo_url" {}

provider "databricks" {
  alias = "sp"
  host  = var.databricks_host
  token = var.obo_token_value
}

resource "databricks_git_credential" "sp" {
  provider              = databricks.sp
  git_username          = var.git_username
  git_provider          = var.git_provider
  personal_access_token = var.git_personal_access_token
}

resource "databricks_repo" "this" {
  provider   = databricks.sp
  url        = var.repo_url
  depends_on = [databricks_git_credential.sp]
}
```

Ausführen:

```bash
terraform init
terraform apply
```

---

## 6. Administration und private Netzwerke (Git Folders)

**Einfach erklärt:** Workspace-Admins können Git Folders per CLI aktivieren/deaktivieren. Für privat gehostete oder On-Premises-Git-Server (hinter Firewall/VPN) gibt es zwei Anbindungswege: den klassischen Git-Server-Proxy (dauerhaft laufender Proxy-Cluster in der Compute Plane) oder das neuere Serverless Private Git (Public Preview, nutzt PrivateLink und Serverless Compute nur bei Bedarf — ressourcenschonender und sicherer). Serverless Private Git wird über eine JSON-Konfigurationsdatei im Workspace gesteuert und hat bei aktivierter Konfiguration Vorrang vor dem klassischen Proxy.

**Git Folders per CLI aktivieren/deaktivieren:**

```bash
# Aktivieren
databricks workspace-conf set-status --json '{"enableProjectTypeInWorkspace": "true"}'

# Deaktivieren
databricks workspace-conf set-status --json '{"enableProjectTypeInWorkspace": "false"}'
```

**Troubleshooting-Umgebungsvariablen für den Git-Server-Proxy:**

| Variable | Zweck |
|---|---|
| `GIT_PROXY_ENABLE_SSL_VERIFICATION` | auf `false` setzen für selbstsignierte Zertifikate |
| `GIT_PROXY_CA_CERT_PATH` | Pfad zur CA-Zertifikatsdatei |
| `GIT_PROXY_HTTP_PROXY` | HTTPS-URL für den Netzwerk-Firewall-Proxy |
| `GIT_PROXY_CUSTOM_HTTP_PORT` | benutzerdefinierte Git-Server-Portnummer |

**Serverless Private Git — Konfigurationsdatei `/Workspace/.git_settings/config.json` (Grundgerüst):**

```json
{
  "default": { },
  "remotes": [ ]
}
```

**Felder im `default`-Abschnitt:**

| Feld | Typ | Pflicht | Standard | Zweck |
|---|---|---|---|---|
| `sslVerify` | boolean | Nein | `true` | SSL-Zertifikatsvalidierung |
| `caCertPath` | string | Nein | `""` | Workspace-Pfad zum benutzerdefinierten CA-Zertifikat |
| `httpProxy` | string | Nein | `""` | HTTP-Proxy-Routing |
| `customHttpPort` | integer | Nein | unspezifiziert | benutzerdefinierter Git-Server-HTTP-Port |

**Minimalbeispiel:**

```json
{
  "default": {
    "sslVerify": false
  }
}
```

**Umfassendes Beispiel:**

```json
{
  "default": {
    "sslVerify": true,
    "caCertPath": "/Workspace/my_ca_cert.pem",
    "httpProxy": "https://git-proxy-server.company.com",
    "customHttpPort": "8080"
  },
  "remotes": [
    {
      "urlPrefix": "https://my-private-git.company.com/",
      "caCertPath": "/Workspace/my_ca_cert_2.pem"
    },
    {
      "urlPrefix": "https://another-git-server.com/project.git",
      "sslVerify": false
    }
  ]
}
```

---

## 7. Fehlerbehebung bei Git Folders

**Einfach erklärt:** Dieser Abschnitt sammelt bekannte Fehlerbilder rund um Git Folders: ungültige Credentials, SSL-Verbindungsfehler, Detached-HEAD-Zustände, inkonsistente Repository-States, Notebook-Namenskonflikte, Timeouts bei großen Repos, 404-Fehler und Zeilenenden-Probleme (LF vs. CRLF) zwischen Linux und Windows. Zu jedem Fehler gibt es konkrete Ursachen und Lösungsschritte, außerdem eine Tabelle, welche Aktionen wiederherstellbar sind (z. B. über den Trash-Ordner) und welche nicht (z. B. Hard Reset).

**Credentials über die Kommandozeile testen:**

```bash
git clone https://<username>:<token>@github.com/<org>/<repo>.git
```

**Wiederherstellbarkeit von Dateien:**

| Aktion | Wiederherstellbar? | Wiederherstellungsmethode |
|---|---|---|
| Löschen über den Workspace-Browser | Ja | Trash-Ordner |
| Neue Datei über den Git-Dialog verwerfen | Ja | Trash-Ordner |
| Geänderte Datei über den Git-Dialog verwerfen | Nein | — |
| Hard Reset bei uncommitteten Änderungen | Nein | — |
| Hard Reset bei neuen uncommitteten Dateien | Nein | — |
| Branch-Wechsel über den Git-Dialog | Ja | Remote-Git-Repo |
| Commit-/Push-Operationen über den Git-Dialog | Ja | Remote-Git-Repo |
| PATCH-Operationen auf `/repos/id` über die API | Ja | Remote-Git-Repo |

---

## 8. CI/CD — Überblick

**Einfach erklärt:** CI/CD (Continuous Integration/Continuous Delivery) bedeutet, Software in kurzen, häufigen Zyklen über automatisierte Pipelines zu entwickeln und auszuliefern. Auch im Data-Engineering- und Data-Science-Umfeld auf Databricks wird das zunehmend Standard. Dieses Kapitel behandelt die Grundlagen, Best Practices sowie konkrete Integrationen mit Azure DevOps, GitHub Actions und Jenkins.

Keine Code-Beispiele in dieser Datei — reines Inhaltsverzeichnis.

---

## 9. CI/CD — Grundlagen und Empfehlungen

**Einfach erklärt:** Databricks beschreibt eine siebenstufige CI/CD-Pipeline: Version (Git), Code (Notebooks/IDE), Build (Bundles/Pylint), Deploy (Bundles mit Azure DevOps/GitHub Actions/Jenkins), Test (pytest), Run (`databricks bundle run`) und Monitor (Job-Monitoring). Als primärer, empfohlener Ansatz gelten **Databricks Asset Bundles** — alternativ lassen sich auch der Git-Folder-Ansatz (Produktions-Ordner werden per Automatisierung aktualisiert) oder „Git mit Jobs" (Job-Definitionen referenzieren direkt ein Remote-Repository, aber nur Code-Dateien sind dabei quellcodeverwaltet, nicht die Job-Konfiguration selbst) nutzen.

**Empfohlene Tools:**

| Tool | Zweck |
|---|---|
| **Databricks Asset Bundles** | Primäre Empfehlung zur programmatischen Definition, Deployment und Ausführung von Databricks-Ressourcen (Jobs, Pipelines, MLOps Stacks) |
| **Databricks Terraform Provider** | Provisionierung und Verwaltung von Workspaces und Infrastruktur |
| **Azure DevOps Integration** | CI/CD-Pipelines mit Azure DevOps entwickeln |
| **GitHub Actions** | Databricks-spezifische GitHub Actions in CI/CD-Workflows einbinden |
| **Jenkins** | CI/CD-Pipelines mit der Jenkins-Plattform entwickeln |
| **Apache Airflow** | Data Pipelines orchestrieren und zeitplanen |
| **Service Principals** | CI/CD-Authentifizierung ohne Nutzerkonten ermöglichen |
| **OAuth Token Federation** | sicherste Authentifizierungsmethode, eliminiert die Notwendigkeit für Secrets |

Keine eigenen Code-Beispiele in dieser Datei.

---

## 10. CI/CD-Workflows und Best Practices

**Einfach erklärt:** Dieser Abschnitt nennt sechs Kernprinzipien für CI/CD auf Databricks (alles versionieren, Testen automatisieren, Infrastructure as Code, Umgebungen isolieren, Tools passend zum Cloud-Ökosystem wählen, Überwachen/Rollbacks automatisieren) und beschreibt den empfohlenen vierstufigen Bundles-Workflow (Kompilieren/Testen → Artefakte hochladen → Bundle validieren → Bundle deployen). Zusätzlich werden rollenspezifische CI/CD-Ansätze für Machine Learning (MLOps Stacks, MLflow Registry), SQL-Entwickler (parametrisierte `.sql`-Dateien) und Dashboard-Entwickler (`databricks bundle generate` für `.lvdash.json`-Dateien) beschrieben. Sicherheitsempfehlung: Workload Identity Federation statt gespeicherter Secrets nutzen.

**Parametrisierte SQL-Datei für Umgebungsisolation:**

```sql
CREATE OR REFRESH STREAMING TABLE ${env}_sales_ingest AS 
SELECT * FROM read_files('s3://${env}-sales-data')
```

**Dashboard-Ressource in der Bundle-Konfiguration:**

```yaml
resources:
  dashboards:
    sales_dashboard:
      display_name: 'Sales Dashboard'
      file_path: ./dashboards/sales_dashboard.lvdash.json
      warehouse_id: ${var.warehouse_id}
```

---

## 11. Azure DevOps Integration

**Einfach erklärt:** Dieser Abschnitt zeigt ein vollständiges Setup einer CI/CD-Pipeline mit Azure DevOps: Ein Python-Wheel (`dabdemo`) wird gebaut, Unit Tests laufen mit pytest, und Notebooks werden per Databricks Asset Bundle in einen Workspace deployt. Es gibt eine getrennte Build-Pipeline (sammelt geänderte Dateien, erstellt ein Zip-Artefakt) und eine Release-Pipeline (installiert Databricks CLI, validiert/deployt das Bundle, führt Tests und Notebook aus). Diese Trennung erlaubt Qualitäts-Gates zwischen Build und Deployment.

**Python-Wheel-Komponente — Verzeichnisstruktur:**

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

**`addcol.py` (Kernfunktion):**

```python
import pyspark.sql.functions as F

def with_status(df):
  return df.withColumn("status", F.lit("checked"))
```

**`test_addcol.py` (Unit Test):**

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

**`databricks.yml` (Bundle-Konfiguration):**

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

**`azure-pipelines.yml` (Build-Pipeline-Definition):**

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

**Release-Pipeline — Umgebungsvariablen (Scope: Stage 1):**

| Variable | Wert |
|---|---|
| `BUNDLE_TARGET` | `dev` (entspricht dem Target in `databricks.yml`) |
| `DATABRICKS_HOST` | `https://adb-<workspace-id>.<random>.azuredatabricks.net` |
| `DATABRICKS_CLIENT_ID` | Application ID des Service Principal |
| `DATABRICKS_CLIENT_SECRET` | OAuth Secret des Service Principal |

**Release-Pipeline — Bash-Inline-Schritt zur Tool-Installation:**

```bash
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
pip install wheel
```

Weitere Release-Pipeline-Schritte (als einzelne Bash-Inline-Tasks, nicht als zusammenhängender Code-Block im Original): `databricks bundle validate -t $(BUNDLE_TARGET)`, `databricks bundle deploy -t $(BUNDLE_TARGET)`, `databricks bundle run -t $(BUNDLE_TARGET) run-unit-tests`, `databricks bundle run -t $(BUNDLE_TARGET) run-dabdemo-notebook`.

---

## 12. GitHub Actions Integration

**Einfach erklärt:** GitHub Actions können CI/CD-Läufe direkt aus GitHub-Repositories auslösen (aktuell Public Preview auf Databricks). Die zentrale Composite Action ist `databricks/setup-cli`, die die Databricks CLI im Workflow einrichtet. Dieser Abschnitt zeigt drei Beispiel-Workflows: (1) Aktualisieren eines Workspace-Git-Folders bei Remote-Branch-Änderungen über Workload Identity Federation, (2) Validieren/Deployen/Ausführen eines Bundles für Dev- und Prod-Umgebungen über Service-Principal-Tokens, und (3) Bauen einer Java-JAR-Datei, Hochladen in ein Volume, Validieren und Deployen eines Bundles.

**Workflow 1 — Git-Folder-Update:**

```yaml
name: Sync Git Folder
concurrency: prod_environment
on:
  push:
    branches:
      - git-folder-cicd-example
permissions:
  id-token: write
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    name: 'Update git folder'
    environment: Prod
    env:
      DATABRICKS_AUTH_TYPE: github-oidc
      DATABRICKS_HOST: ${{ vars.DATABRICKS_HOST }}
      DATABRICKS_CLIENT_ID: ${{ secrets.DATABRICKS_CLIENT_ID }}
    steps:
      - uses: actions/checkout@v3
      - uses: databricks/setup-cli@main
      - name: Update git folder
        run: databricks repos update /Workspace/<git-folder-path> --branch git-folder-cicd-example
```

**Workflow 2 — Bundle-Pipeline-Update: Dev-Deployment:**

```yaml
name: 'Dev deployment'
concurrency: 1
on:
  pull_request:
    types:
      - opened
      - synchronize
    branches:
      - main
jobs:
  deploy:
    name: 'Deploy bundle'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: databricks/setup-cli@main
      - run: databricks bundle deploy
        working-directory: .
        env:
          DATABRICKS_TOKEN: ${{ secrets.SP_TOKEN }}
          DATABRICKS_BUNDLE_ENV: dev

  pipeline_update:
    name: 'Run pipeline update'
    runs-on: ubuntu-latest
    needs:
      - deploy
    steps:
      - uses: actions/checkout@v3
      - uses: databricks/setup-cli@main
      - run: databricks bundle run sample_job --refresh-all
        working-directory: .
        env:
          DATABRICKS_TOKEN: ${{ secrets.SP_TOKEN }}
          DATABRICKS_BUNDLE_ENV: dev
```

**Production-Deployment:** identisch, mit `on: push: branches: [main]` statt `pull_request`, sowie `DATABRICKS_BUNDLE_ENV: prod`.

**Beispiel-Bundle-Konfiguration für Workflow 2:**

```yaml
bundle:
  name: pipeline_update

include:
  - resources/*.yml

variables:
  catalog:
    description: The catalog to use
  schema:
    description: The schema to use

resources:
  jobs:
    sample_job:
      name: sample_job
      parameters:
        - name: catalog
          default: ${var.catalog}
        - name: schema
          default: ${var.schema}
      tasks:
        - task_key: refresh_pipeline
          pipeline_task:
            pipeline_id: ${resources.pipelines.sample_pipeline.id}
      environments:
        - environment_key: default
          spec:
            environment_version: '4'

  pipelines:
    sample_pipeline:
      name: sample_pipeline
      catalog: ${var.catalog}
      schema: ${var.schema}
      serverless: true
      root_path: '../src/sample_pipeline'
      libraries:
        - glob:
            include: ../src/sample_pipeline/transformations/**
      environment:
        dependencies:
          - --editable ${workspace.file_path}

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: <dev-workspace-url>
    variables:
      catalog: my_catalog
      schema: ${workspace.current_user.short_name}

  prod:
    mode: production
    workspace:
      host: <production-workspace-url>
      root_path: /Workspace/Users/someone@example.com/.bundle/${bundle.name}/${bundle.target}
    variables:
      catalog: my_catalog
      schema: prod
    permissions:
      - user_name: someone@example.com
        level: CAN_MANAGE
```

**Workflow 3 — JAR-Build und Bundle-Deployment:**

```yaml
name: Build JAR and deploy with bundle

on:
  pull_request:
    branches:
      - main
  push:
    branches:
      - main

jobs:
  build-test-upload:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Cache Maven dependencies
        uses: actions/cache@v4
        with:
          path: ~/.m2/repository
          key: ${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}
          restore-keys: |
            ${{ runner.os }}-maven-

      - name: Build and test JAR with Maven
        run: mvn clean verify

      - name: Databricks CLI Setup
        uses: databricks/setup-cli@v0.9.0

      - name: Upload JAR to a volume
        env:
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
        run: |
          databricks fs cp target/my-app-1.0.jar dbfs:/Volumes/artifacts/my-app-${{ github.sha }}.jar --overwrite

  validate:
    needs: build-test-upload
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Databricks CLI Setup
        uses: databricks/setup-cli@v0.9.0
      - name: Validate bundle
        env:
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
        run: databricks bundle validate

  deploy:
    needs: validate
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Databricks CLI Setup
        uses: databricks/setup-cli@v0.9.0
      - name: Deploy bundle
        env:
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
        run: databricks bundle deploy --target prod
```

---

## 13. Jenkins Integration

**Einfach erklärt:** Dieser Abschnitt beschreibt eine achtstufige Jenkins-Pipeline (Checkout, Validate Bundle, Deploy Bundle, Run Unit Tests, Run Notebook, Evaluate Notebook Runs, Import Test Results, Publish Test Results), die per `Jenkinsfile` ein Python-Wheel samt Notebooks baut, testet und deployt — gesteuert über die Databricks CLI und Databricks Asset Bundles. Voraussetzungen sind lokal installierte Databricks CLI, Jenkins, `jq` sowie die Python-Wheel-Build-Tools; drei globale Umgebungsvariablen (`DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`) werden in Jenkins hinterlegt. Hinweis: Die Originaldatei beschreibt die einzelnen Pipeline-Stufen und deren CLI-Befehle in Prosa/Tabellenform, enthält aber keinen zusammenhängenden `Jenkinsfile`-Groovy-Code-Block — die genannten Befehle je Stage sind: `databricks bundle validate -t ${BUNDLETARGET}`, `databricks bundle deploy -t ${BUNDLETARGET}`, `databricks bundle run -t ${BUNDLETARGET} run-unit-tests`, `databricks bundle run -t ${BUNDLETARGET} run-dabdemo-notebook`, `databricks bundle run -t ${BUNDLETARGET} evaluate-notebook-runs`, `databricks workspace export-dir`.

**Python-Wheel-Bibliotheksstruktur:**

```
Libraries/
└── python/
    └── dabdemo/
        ├── dabdemo/
        │   ├── __init__.py
        │   ├── __main__.py
        │   ├── addcol.py
        │   └── test_addcol.py
        └── setup.py
```

**`.gitignore`-Ergänzung vor dem Push:**

```
.databricks/
.vscode/
Libraries/python/dabdemo/build/
Libraries/python/dabdemo/__pycache__/
Libraries/python/dabdemo/dabdemo.egg-info/
Validation/
```

---

## 14. Terraform — Überblick

**Einfach erklärt:** Der Databricks-Terraform-Provider erlaubt Infrastructure-as-Code-Verwaltung für Databricks-Workspaces und zugehörige Cloud-Ressourcen (AWS, Azure, GCP) über HashiCorp Terraform. Dieses Kapitel gliedert sich in sieben Unterthemen: Grundlagen, Workspace-Ressourcen, ein End-to-End-Beispiel (Cluster/Notebook/Job), Unity-Catalog-Automatisierung, Service-Principal-Bereitstellung, CDKTF (nicht mehr empfohlen) und Fehlerbehebung.

Keine Code-Beispiele in dieser Datei — reines Inhaltsverzeichnis.

---

## 15. Terraform — Grundlagen

**Einfach erklärt:** Der Databricks-Terraform-Provider unterstützt die Provisionierung von Workspaces, Clustern, Jobs, Notebooks, Datenzugriffs-Konfigurationen und Unity-Catalog-Setups. Um zu starten, braucht man die Terraform CLI, ein Projektverzeichnis, den Provider-Block (`source = "databricks/databricks"`) sowie konfigurierte Authentifizierung. Eine typische Beispielkonfiguration besteht aus mehreren `.tf`-Dateien (`me.tf`, `notebook.tf`, `cluster.tf`, `job.tf`) plus `*.auto.tfvars`-Dateien für Variablenwerte. Für Tests gibt es zwei Ansätze: Integrationstests mit `command = apply` (echtes Deployment) oder Unit Tests mit `command = plan`/Mock-Provider (ohne Deployment).

Keine eigenen Code-Beispiele in dieser Datei — das vollständige End-to-End-Beispiel folgt im nächsten Abschnitt.

---

## 16. Terraform: Workspace bereitstellen und verwalten

**Einfach erklärt:** Dieser Abschnitt zeigt, wie man mit dem Databricks-Terraform-Provider Standardressourcen ohne Admin-Rechte (Secrets, Notebooks, Jobs, Cluster, Cluster-Policies, Instance Pools) sowie sicherheitsrelevante Ressourcen mit Admin-Rechten (Gruppen, Nutzer, Berechtigungen für Notebooks/Jobs/Cluster/Policies/Pools) anlegt. Zusätzlich werden Storage-Optionen (DBFS-Dateien, S3-Mounts) und fortgeschrittene Konfiguration wie IP-Access-Lists behandelt. Neue Workspaces selbst werden primär über die Ressource `databricks_mws_workspaces` automatisiert.

**Provider-Grundkonfiguration:**

```hcl
terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
    }
  }
}

provider "databricks" {}

data "databricks_current_user" "me" {}
data "databricks_spark_version" "latest" {}
data "databricks_node_type" "smallest" {
  local_disk = true
}
```

**Secret Management:**

```hcl
resource "databricks_secret_scope" "this" {
  name = "demo-${data.databricks_current_user.me.alphanumeric}"
}

resource "databricks_token" "pat" {
  comment          = "Created from ${abspath(path.module)}"
  lifetime_seconds = 3600
}

resource "databricks_secret" "token" {
  string_value = databricks_token.pat.token_value
  scope        = databricks_secret_scope.this.name
  key          = "token"
}
```

**Notebook-Erstellung:**

```hcl
resource "databricks_notebook" "this" {
  path     = "${data.databricks_current_user.me.home}/Terraform"
  language = "PYTHON"
  content_base64 = base64encode(<<-EOT
    token = dbutils.secrets.get('${databricks_secret_scope.this.name}', '${databricks_secret.token.key}')
    print(f'This should be redacted: {token}')
    EOT
  )
}
```

**Job-Konfiguration:**

```hcl
resource "databricks_job" "this" {
  name = "Terraform Demo (${data.databricks_current_user.me.alphanumeric})"
  task {
    task_key = "demo_task"
    new_cluster {
      num_workers   = 1
      spark_version = data.databricks_spark_version.latest.id
      node_type_id  = data.databricks_node_type.smallest.id
    }
    notebook_task {
      notebook_path = databricks_notebook.this.path
    }
  }
  email_notifications {}
}
```

**Cluster-Verwaltung:**

```hcl
resource "databricks_cluster" "this" {
  cluster_name = "Exploration (${data.databricks_current_user.me.alphanumeric})"
  spark_version           = data.databricks_spark_version.latest.id
  instance_pool_id        = databricks_instance_pool.smallest_nodes.id
  autotermination_minutes = 20
  autoscale {
    min_workers = 1
    max_workers = 10
  }
}
```

**Cluster-Policy:**

```hcl
resource "databricks_cluster_policy" "this" {
  name = "Minimal (${data.databricks_current_user.me.alphanumeric})"
  definition = jsonencode({
    "dbus_per_hour" : {
      "type" : "range",
      "maxValue" : 10
    },
    "autotermination_minutes" : {
      "type" : "fixed",
      "value" : 20,
      "hidden" : true
    }
  })
}
```

**Instance Pool:**

```hcl
resource "databricks_instance_pool" "smallest_nodes" {
  instance_pool_name = "Smallest Nodes (${data.databricks_current_user.me.alphanumeric})"
  min_idle_instances = 0
  max_capacity       = 30
  node_type_id       = data.databricks_node_type.smallest.id
  preloaded_spark_versions = [
    data.databricks_spark_version.latest.id
  ]
  idle_instance_autotermination_minutes = 20
}
```

**Outputs:**

```hcl
output "notebook_url" {
  value = databricks_notebook.this.url
}

output "job_url" {
  value = databricks_job.this.url
}
```

**Secret ACL:**

```hcl
resource "databricks_secret_acl" "spectators" {
  principal  = databricks_group.spectators.display_name
  scope      = databricks_secret_scope.this.name
  permission = "READ"
}
```

**Gruppen- und Nutzerverwaltung:**

```hcl
resource "databricks_group" "spectators" {
  display_name = "Spectators (by ${data.databricks_current_user.me.alphanumeric})"
}

resource "databricks_user" "dummy" {
  user_name    = "dummy+${data.databricks_current_user.me.alphanumeric}@example.com"
  display_name = "Dummy ${data.databricks_current_user.me.alphanumeric}"
}

resource "databricks_group_member" "a" {
  group_id  = databricks_group.spectators.id
  member_id = databricks_user.dummy.id
}
```

**Notebook-Berechtigungen:**

```hcl
resource "databricks_permissions" "notebook" {
  notebook_path = databricks_notebook.this.id
  access_control {
    user_name        = databricks_user.dummy.user_name
    permission_level = "CAN_RUN"
  }
  access_control {
    group_name       = databricks_group.spectators.display_name
    permission_level = "CAN_READ"
  }
}
```

**Job-Berechtigungen:**

```hcl
resource "databricks_permissions" "job" {
  job_id = databricks_job.this.id
  access_control {
    user_name        = databricks_user.dummy.user_name
    permission_level = "IS_OWNER"
  }
  access_control {
    group_name       = databricks_group.spectators.display_name
    permission_level = "CAN_MANAGE_RUN"
  }
}
```

**Cluster-Berechtigungen:**

```hcl
resource "databricks_permissions" "cluster" {
  cluster_id = databricks_cluster.this.id
  access_control {
    user_name        = databricks_user.dummy.user_name
    permission_level = "CAN_RESTART"
  }
  access_control {
    group_name       = databricks_group.spectators.display_name
    permission_level = "CAN_ATTACH_TO"
  }
}
```

**Cluster-Policy-Berechtigungen:**

```hcl
resource "databricks_permissions" "policy" {
  cluster_policy_id = databricks_cluster_policy.this.id
  access_control {
    group_name       = databricks_group.spectators.display_name
    permission_level = "CAN_USE"
  }
}
```

**Instance-Pool-Berechtigungen:**

```hcl
resource "databricks_permissions" "pool" {
  instance_pool_id = databricks_instance_pool.smallest_nodes.id
  access_control {
    group_name       = databricks_group.spectators.display_name
    permission_level = "CAN_ATTACH_TO"
  }
}
```

**IP-Access-Lists:**

```hcl
data "http" "my" {
  url = "https://ifconfig.me"
}

resource "databricks_workspace_conf" "this" {
  custom_config = {
    "enableIpAccessLists": "true"
  }
}

resource "databricks_ip_access_list" "only_me" {
  label = "only ${data.http.my.body} is allowed to access workspace"
  list_type = "ALLOW"
  ip_addresses = ["${data.http.my.body}/32"]
  depends_on = [databricks_workspace_conf.this]
}
```

---

## 17. Terraform: Cluster, Notebook und Job bereitstellen

**Einfach erklärt:** Dieser Abschnitt liefert ein vollständiges End-to-End-Beispiel: In einem bestehenden Workspace werden per Terraform ein Cluster (wahlweise Unity-Catalog-kompatibel mit `data_security_mode` oder als klassischer All-Purpose-Cluster), ein Notebook und ein Job (der das Notebook auf dem Cluster ausführt) erstellt — inklusive dreier vollständiger Beispiel-Notebooks (ETL Quick Start, SQL Quick Start, Lakehouse E2E). Am Ende steht die Ausführung (`terraform validate/plan/apply`) sowie das Aufräumen (`terraform destroy`).

**`cluster.tf`, Unity-Catalog-kompatibel:**

```hcl
variable "cluster_name" {}
variable "cluster_autotermination_minutes" {}
variable "cluster_num_workers" {}
variable "cluster_data_security_mode" {}

data "databricks_node_type" "smallest" {
  local_disk = true
}

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}

resource "databricks_cluster" "this" {
  cluster_name            = var.cluster_name
  node_type_id            = data.databricks_node_type.smallest.id
  spark_version           = data.databricks_spark_version.latest_lts.id
  autotermination_minutes = var.cluster_autotermination_minutes
  num_workers             = var.cluster_num_workers
  data_security_mode      = var.cluster_data_security_mode
}

output "cluster_url" {
  value = databricks_cluster.this.url
}
```

**`cluster.auto.tfvars`, Unity-Catalog-kompatibel:**

```hcl
cluster_name                    = "My Cluster"
cluster_autotermination_minutes = 60
cluster_num_workers             = 1
cluster_data_security_mode      = "SINGLE_USER"
```

**`cluster.tf`, All-Purpose-Cluster (ohne `data_security_mode`-Variable):**

```hcl
variable "cluster_name" {
  description = "A name for the cluster."
  type        = string
  default     = "My Cluster"
}

variable "cluster_autotermination_minutes" {
  description = "Minutes before automatic termination due to inactivity."
  type        = number
  default     = 60
}

variable "cluster_num_workers" {
  description = "The number of workers."
  type        = number
  default     = 1
}

data "databricks_node_type" "smallest" {
  local_disk = true
}

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}

resource "databricks_cluster" "this" {
  cluster_name            = var.cluster_name
  node_type_id            = data.databricks_node_type.smallest.id
  spark_version           = data.databricks_spark_version.latest_lts.id
  autotermination_minutes = var.cluster_autotermination_minutes
  num_workers             = var.cluster_num_workers
}

output "cluster_url" {
  value = databricks_cluster.this.url
}
```

**`cluster.auto.tfvars`, All-Purpose:**

```hcl
cluster_name                    = "My Cluster"
cluster_autotermination_minutes = 60
cluster_num_workers             = 1
```

**`notebook.tf`:**

```hcl
variable "notebook_subdirectory" {
  description = "Subdirectory name for storing the notebook."
  type        = string
  default     = "Terraform"
}

variable "notebook_filename" {
  description = "The notebook's filename."
  type        = string
}

variable "notebook_language" {
  description = "The language of the notebook."
  type        = string
}

resource "databricks_notebook" "this" {
  path     = "${data.databricks_current_user.me.home}/${var.notebook_subdirectory}/${var.notebook_filename}"
  language = var.notebook_language
  source   = "./${var.notebook_filename}"
}

output "notebook_url" {
  value = databricks_notebook.this.url
}
```

**Beispiel-Notebook 1 — Python ETL Quick Start (`notebook-getting-started-etl-quick-start.py`):**

```python
# Databricks notebook source
from pyspark.sql.functions import col, current_timestamp

file_path = "/databricks-datasets/structured-streaming/events"
username = spark.sql("SELECT regexp_replace(session_user(), '[^a-zA-Z0-9]', '_')").first()[0]
table_name = f"{username}_etl_quickstart"
checkpoint_path = f"/tmp/{username}/_checkpoint/etl_quickstart"

spark.sql(f"DROP TABLE IF EXISTS {table_name}")
dbutils.fs.rm(checkpoint_path, True)

(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", checkpoint_path)
  .load(file_path)
  .select("*", col("_metadata.file_path").alias("source_file"), current_timestamp().alias("processing_time"))
  .writeStream
  .option("checkpointLocation", checkpoint_path)
  .trigger(availableNow=True)
  .toTable(table_name))

# COMMAND ----------
df = spark.read.table(table_name)

# COMMAND ----------
display(df)
```

`notebook.auto.tfvars` dazu: `notebook_subdirectory = "Terraform"`, `notebook_filename = "notebook-getting-started-etl-quick-start.py"`, `notebook_language = "PYTHON"`.

**Beispiel-Notebook 2 — SQL Quick Start (`notebook-getting-started-quickstart.sql`):**

```sql
-- Databricks notebook source
-- MAGIC %python
-- MAGIC diamonds = (spark.read
-- MAGIC   .format("csv")
-- MAGIC   .option("header", "true")
-- MAGIC   .option("inferSchema", "true")
-- MAGIC   .load("/databricks-datasets/Rdatasets/data-001/csv/ggplot2/diamonds.csv")
-- MAGIC )
-- MAGIC
-- MAGIC diamonds.write.format("delta").save("/mnt/delta/diamonds")

-- COMMAND ----------
DROP TABLE IF EXISTS diamonds;
CREATE TABLE diamonds USING DELTA LOCATION '/mnt/delta/diamonds/'

-- COMMAND ----------
SELECT color, avg(price) AS price FROM diamonds GROUP BY color ORDER BY COLOR
```

`notebook.auto.tfvars` dazu: `notebook_filename = "notebook-getting-started-quickstart.sql"`, `notebook_language = "SQL"`.

**Beispiel-Notebook 3 — Python Lakehouse E2E (`notebook-getting-started-lakehouse-e2e.py`):**

```python
# Databricks notebook source
external_location = "<your_external_location>"
catalog = "<your_catalog>"

dbutils.fs.put(f"{external_location}/foobar.txt", "Hello world!", True)
display(dbutils.fs.head(f"{external_location}/foobar.txt"))
dbutils.fs.rm(f"{external_location}/foobar.txt")
display(spark.sql(f"SHOW SCHEMAS IN {catalog}"))

# COMMAND ----------
from pyspark.sql.functions import col

username = spark.sql("SELECT regexp_replace(session_user(), '[^a-zA-Z0-9]', '_')").first()[0]
database = f"{catalog}.e2e_lakehouse_{username}_db"
source = f"{external_location}/e2e-lakehouse-source"
table = f"{database}.target_table"
checkpoint_path = f"{external_location}/_checkpoint/e2e-lakehouse-demo"

spark.sql(f"SET c.username='{username}'")
spark.sql(f"SET c.database={database}")
spark.sql(f"SET c.source='{source}'")
spark.sql("DROP DATABASE IF EXISTS ${c.database} CASCADE")
spark.sql("CREATE DATABASE ${c.database}")
spark.sql("USE ${c.database}")

dbutils.fs.rm(source, True)
dbutils.fs.rm(checkpoint_path, True)

class LoadData:
  def __init__(self, source):
    self.source = source

  def get_date(self):
    try:
      df = spark.read.format("json").load(source)
    except:
        return "2016-01-01"
    batch_date = df.selectExpr("max(distinct(date(tpep_pickup_datetime))) + 1 day").first()[0]
    if batch_date.month == 3:
      raise Exception("Source data exhausted")
    return batch_date

  def get_batch(self, batch_date):
    return (
      spark.table("samples.nyctaxi.trips")
        .filter(col("tpep_pickup_datetime").cast("date") == batch_date)
    )

  def write_batch(self, batch):
    batch.write.format("json").mode("append").save(self.source)

  def land_batch(self):
    batch_date = self.get_date()
    batch = self.get_batch(batch_date)
    self.write_batch(batch)

RawData = LoadData(source)

# COMMAND ----------
RawData.land_batch()

# COMMAND ----------
from pyspark.sql.functions import col, current_timestamp

(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", checkpoint_path)
  .load(source)
  .select("*", col("_metadata.file_path").alias("source_file"), current_timestamp().alias("processing_time"))
  .writeStream
  .option("checkpointLocation", checkpoint_path)
  .trigger(availableNow=True)
  .option("mergeSchema", "true")
  .toTable(table))

# COMMAND ----------
df = spark.read.table(table)

# COMMAND ----------
display(df)
```

`notebook.auto.tfvars` dazu: `notebook_filename = "notebook-getting-started-lakehouse-e2e.py"`, `notebook_language = "PYTHON"`.

**`job.tf`:**

```hcl
variable "job_name" {
  description = "A name for the job."
  type        = string
  default     = "My Job"
}

variable "task_key" {
  description = "A name for the task."
  type        = string
  default     = "my_task"
}

resource "databricks_job" "this" {
  name = var.job_name
  task {
    task_key = var.task_key
    existing_cluster_id = databricks_cluster.this.cluster_id
    notebook_task {
      notebook_path = databricks_notebook.this.path
    }
  }
  email_notifications {
    on_success = [ data.databricks_current_user.me.user_name ]
    on_failure = [ data.databricks_current_user.me.user_name ]
  }
}

output "job_url" {
  value = databricks_job.this.url
}
```

**`job.auto.tfvars`:**

```hcl
job_name = "My Job"
task_key = "my_task"
```

**Konfigurationen ausführen:**

```bash
terraform validate
terraform plan
terraform apply
```

**Aufräumen:**

```bash
terraform plan
terraform destroy
```

---

## 18. Terraform: Unity Catalog automatisieren

**Einfach erklärt:** Um Unity Catalog per Terraform zu automatisieren (z. B. Metastore-Setup), braucht man einen Premium-Plan oder höher, AWS-Rechte zum Erstellen von S3-Buckets/IAM-Rollen/Policies/Cross-Account-Trust sowie einen Service Principal mit Account-Admin-Berechtigungen. Die Authentifizierung erfolgt über eine Reihe von Umgebungsvariablen; Databricks empfiehlt dabei OAuth-Tokens statt Personal Access Tokens für automatisierte Systeme.

**Erforderliche Umgebungsvariablen:**

| Variable | Zweck |
|---|---|
| `DATABRICKS_CLIENT_ID` | Application ID des Service Principal |
| `DATABRICKS_CLIENT_SECRET` | Secret des Service Principal |
| `DATABRICKS_ACCOUNT_ID` | Databricks-Account-ID |
| `TF_VAR_databricks_account_id` | dasselbe wie oben, als Terraform-Variable |
| `AWS_ACCESS_KEY_ID` | AWS Access Key |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Key |
| `AWS_REGION` | AWS-Regionscode |

**Terraform-Befehle:**

```bash
terraform validate
terraform plan
terraform apply
terraform destroy
```

---

## 19. Terraform: Service Principals bereitstellen

**Einfach erklärt:** Ein Service Principal ist eine Identität für automatisierte Tools und Systeme (Skripte, Apps, CI/CD-Plattformen). Dieser Abschnitt zeigt Schritt für Schritt, wie man per Terraform einen Service Principal im Workspace anlegt und optional ein zeitlich begrenztes Personal Access Token für ihn generiert (über eine `databricks_permissions`-Ressource plus `databricks_obo_token`). Wichtig: Pro Workspace darf nur eine `authorization = "tokens"`-Ressource existieren, generierte Tokens sind workspace-gebunden, und abgerufene Tokens landen im Klartext in der `terraform.tfstate`-Datei.

**Arbeitsverzeichnis erstellen:**

```bash
mkdir terraform_service_principal_demo && cd terraform_service_principal_demo
```

**`main.tf`:**

```hcl
variable "databricks_connection_profile" {
  description = "The name of the Databricks authentication configuration profile to use."
  type        = string
}

variable "service_principal_display_name" {
  description = "The display name for the service principal."
  type        = string
}

variable "service_principal_access_token_lifetime" {
  description = "The lifetime of the service principal's access token, in seconds."
  type        = number
  default     = 3600
}

terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

provider "databricks" {
  profile = var.databricks_connection_profile
}

resource "databricks_service_principal" "sp" {
  provider     = databricks
  display_name = var.service_principal_display_name
}

output "service_principal_name" {
  value = databricks_service_principal.sp.display_name
}

output "service_principal_id" {
  value = databricks_service_principal.sp.application_id
}
```

**`terraform.tfvars`:**

```hcl
databricks_connection_profile           = "<Databricks authentication configuration profile name>"
service_principal_display_name          = "<Service principal display name>"
service_principal_access_token_lifetime = 3600
```

**Konfiguration validieren:**

```bash
terraform init
terraform validate
```

**Ressourcen deployen:**

```bash
terraform apply
```

**Optional: Personal-Access-Token-Generierung aktivieren (in `main.tf` einkommentieren):**

```hcl
resource "databricks_permissions" "token_usage" {
  authorization    = "tokens"
  access_control {
    service_principal_name = databricks_service_principal.sp.application_id
    permission_level       = "CAN_USE"
  }
}

resource "databricks_obo_token" "this" {
  depends_on       = [databricks_permissions.token_usage]
  application_id   = databricks_service_principal.sp.application_id
  comment          = "Personal access token on behalf of ${databricks_service_principal.sp.display_name}"
  lifetime_seconds = var.service_principal_access_token_lifetime
}

output "service_principal_access_token" {
  value     = databricks_obo_token.this.token_value
  sensitive = true
}
```

---

## 20. Terraform: CDKTF (Cloud Development Kit for Terraform)

**Einfach erklärt:** CDKTF erlaubt es, Terraform-Konfigurationen statt in HCL direkt in Python zu schreiben. Wichtig: Databricks empfiehlt CDKTF für die Verwaltung von Databricks-Ressourcen **nicht mehr** — HashiCorp hat das Sunset von CDKTF angekündigt, es gibt keine aktive Weiterentwicklung/Support mehr. Empfohlen wird stattdessen der direkte Databricks-Terraform-Provider (klassisches HCL). Für alle, die trotzdem mit CDKTF arbeiten, dokumentiert dieser Abschnitt Projekt-Setup, Ressourcendefinition (Notebook + Job), Deployment und Testing.

**CDKTF-Projekt initialisieren:**

```bash
mkdir cdktf-demo
cd cdktf-demo
cdktf init --template=python --local
```

**Provider-Paket installieren:**

```bash
pipenv install cdktf-cdktf-provider-databricks
```

**`main.py` (erstellt ein Notebook und einen Job, der es ausführt):**

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

**`vars.py`:**

```python
#!/usr/bin/env python
resource_prefix = "cdktf-demo"
num_workers     = 1
spark_version   = "14.3.x-scala2.12"
node_type_id    = "i3.xlarge"
```

**Deployment:**

```bash
cdktf synth
cdktf diff
cdktf deploy
```

**Aufräumen:**

```bash
cdktf destroy
```

**Testing:**

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

---

## 21. Terraform: Fehlerbehebung

**Einfach erklärt:** Die zwei häufigsten Terraform-Provider-Fehler sind „Failed to install provider" und „Failed to query available provider packages" — beide treten typischerweise bei `terraform init` ohne eingecheckte `terraform.lock.hcl`-Datei auf und werden durch veraltete Provider-Referenzen (`databrickslabs/databricks` statt `databricks/databricks`) verursacht. Die Lösung ist, alle Provider-Referenzen zu aktualisieren, den State entsprechend umzuschreiben und danach `terraform init` erneut auszuführen. Für tiefere Diagnose lässt sich detailliertes Logging über `TF_LOG`/`TF_LOG_PATH` aktivieren.

**Provider-Referenzen automatisiert aktualisieren:**

```bash
python3 -c "$(curl -Ls https://dbricks.co/updtfns)"
```

**State-Provider-Replacement:**

```bash
terraform state replace-provider databrickslabs/databricks databricks/databricks
```

**Logging aktivieren:**

```bash
TF_LOG=DEBUG TF_LOG_PATH=tf.log terraform apply -no-color
```

---

## 22. Überblick: Databricks Asset Bundles (Declarative Automation Bundles)

**Einfach erklärt:** Databricks Asset Bundles heißen inzwischen offiziell **Declarative Automation Bundles** (Kurzform weiterhin DAB) — ein Tool, mit dem man Databricks-Ressourcen wie Jobs, Pipelines, Dashboards und Apps als YAML-Quelldateien beschreibt und als ein einziges, versionierbares Projekt deployt. Die Umbenennung ist nicht-brechend: der `bundle`-CLI-Befehl und alle bestehenden Konfigurationen bleiben unverändert. Dieses Kapitel bündelt 23 Unterthemen von den Grundlagen über Tutorials, Templates, Konfiguration, Berechtigungen bis zu Referenztabellen für Ressourcen- und Task-Typen.

Keine Code-Beispiele in dieser Datei.

---

## 23. Grundlagen: Kernkomponenten und Lebenszyklus

**Einfach erklärt:** Ein Bundle bündelt Cloud-Infrastruktur/Workspace-Konfiguration, Quelldateien (Notebooks, Python-Dateien), Ressourcendefinitionen (Jobs, Pipelines, Dashboards, Modelle) sowie Tests zu einem einzigen deploybaren Projekt. Die Entwicklung folgt einem sechsstufigen Lebenszyklus: Create → Develop → Validate → Deploy → Run → Destroy. Projekte lassen sich aus einem Standard- oder eigenen Template initialisieren, oder komplett manuell mit `databricks.yml` als einziger Pflichtdatei aufgebaut werden.

**Sechsstufiger Lebenszyklus:**
1. Create — Bundle-Grundgerüst aus einem Projekt-Template initialisieren.
2. Develop — Konfigurationsdateien lokal erstellen.
3. Validate — Einstellungen gegen Schemas prüfen.
4. Deploy — Bundle in den Ziel-Workspace pushen.
5. Run — Workflow-Ressourcen ausführen.
6. Destroy — Bundle-Ressourcen dauerhaft entfernen.

**Standard-Template initialisieren:**

```bash
databricks bundle init
```

**Eigenes Template:**

```bash
databricks bundle init <project-template-local-path-or-url>
```

**Validieren:**

```bash
databricks bundle validate
```

**Deployen:**

```bash
databricks bundle deploy
```

**Ausführen:**

```bash
databricks bundle run hello_job
databricks bundle run -t dev hello_job
```

**Zerstören:**

```bash
databricks bundle destroy
databricks bundle destroy --auto-approve
```

Quelle(n): https://docs.databricks.com/aws/en/dev-tools/bundles/ · https://docs.databricks.com/aws/en/dev-tools/bundles/work-tasks

---

## 24. Tutorials: Job, Pipeline und App mit Bundles

**Einfach erklärt:** Drei zentrale Standard-Tutorials führen Schritt für Schritt durch Authentifizierung, Bundle-Initialisierung, Validierung, Deployment, Ausführung und Aufräumen — jeweils für einen Job, eine Lakeflow-Pipeline und eine Databricks App. Zusätzlich zeigt das Kursmaterial einen praktischen Weg, einen bereits in der UI erstellten Job über „View as code" / „Edit as YAML" direkt als Bundle-Ressource zu übernehmen.

**Job als YAML aus der UI exportieren:** Job in Jobs & Pipelines öffnen → Kebab-Menü → **View as code** (JSON) oder **Edit as YAML** → Ausgabe per Copy-Paste in eine Bundle-Ressourcendatei übernehmen.

**Job-Tutorial:**

Authentifizierung:

```bash
databricks auth login --host <workspace-url>
```

Bundle initialisieren:

```bash
databricks bundle init
```

Validieren:

```bash
databricks bundle validate
```

Deployen:

```bash
databricks bundle deploy --target dev
```

Ausführen:

```bash
databricks bundle run --target dev sample_job
```

Tests ausführen:

```bash
uv run pytest
```

Aufräumen:

```bash
databricks bundle destroy --target dev
```

**Pipeline-Tutorial:**

Authentifizierung:

```bash
databricks auth login --host <workspace-url>
databricks auth token --host <workspace-url>
```

Bundle erstellen:

```bash
databricks pipelines init
```

Bundle-Struktur:

```
my_pipeline_project
├── databricks.yml
├── pyproject.toml
├── README.md
├── resources
│   ├── my_pipeline_project_etl.pipeline.yml
│   └── sample_job.job.yml
└── src
    └── my_pipeline_project_etl
        ├── explorations
        │   └── sample_exploration.ipynb
        ├── README.md
        └── transformations
            ├── sample_trips_my_pipeline_project.py
            └── sample_zones_my_pipeline_project.py
```

Validieren:

```bash
databricks bundle validate
```

Deployen:

```bash
databricks bundle deploy --target dev
# oder:
databricks pipelines deploy --target dev
```

Pipeline ausführen:

```bash
databricks pipelines run my_pipeline_project_etl --target dev
```

Logs und Historie:

```bash
databricks pipelines history my_pipeline_project_etl
databricks pipelines logs my_pipeline_project_etl
```

Aufräumen:

```bash
databricks pipelines destroy --target dev
```

**App-Tutorial:**

Bestehende Workspace-App synchronisieren:

```bash
mkdir hello-world-app
cd hello-world-app
databricks workspace export-dir /Workspace/Users/someone@example.com/databricks_apps/[app-path] .
```

GitHub-Templates:

```bash
git clone https://github.com/databricks/app-templates
```

Bestehende App zum Bundle hinzufügen:

```bash
databricks bundle generate app --existing-app-name hello-world-app
databricks bundle bind
```

Lokale Entwicklung und Debugging:

```bash
databricks apps run-local --prepare-environment --debug
```

Bundle-Konfiguration und Deployment:

```yaml
bundle:
  name: hello_world_bundle

resources:
  apps:
    hello_world_app:
      name: 'hello-world-app'
      source_code_path: .
      description: 'A Databricks app'

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://myworkspace.cloud.databricks.com

  prod:
    mode: production
    workspace:
      host: https://myworkspace.cloud.databricks.com
      root_path: /Workspace/Users/someone@example.com/.bundle/${bundle.name}/${bundle.target}
    permissions:
      - user_name: someone@example.com
        level: CAN_MANAGE
```

```bash
databricks bundle validate
databricks bundle deploy
databricks apps deploy
databricks bundle summary
```

Berechtigungen und Testen:

```yaml
resources:
  apps:
    hello_world_app:
      name: 'hello-world-app'
      source_code_path: .
      description: 'A Databricks app'
      permissions:
        - level: CAN_USE
          group_name: users
```

```bash
databricks bundle run hello_world_app
```

Produktions-Deployment — Option A (direkter Schema-Grant):

```yaml
resources:
  apps:
    hello_world_app:
      name: 'hello-world-app'
      source_code_path: .
      description: 'A Databricks app'
  schemas:
    my_schema:
      name: my_schema
      grants:
        - principal: '${resources.apps.hello_world_app.service_principal_client_id}'
          privileges:
            - CREATE_TABLE
      catalog_name: main
```

Produktions-Deployment — Option B (Job-basierter Grant), `grant_notebook.ipynb`:

```python
app_service_principal = dbutils.widgets.get("app_service_principal")
spark.sql(f"GRANT ALL PRIVILEGES ON SCHEMA <schema-name> TO `{app_service_principal}`")
```

```yaml
resources:
  jobs:
    grant_job:
      name: 'grant-job'
      parameters:
        - name: app_service_principal
          default: '${resources.apps.hello_world_app.service_principal_client_id}'
      tasks:
        - task_key: setup_grants
          notebook_task:
            notebook_path: ./grant_notebook.ipynb
```

Produktions-Deployment ausführen:

```bash
databricks bundle deploy -t prod
databricks bundle run grant_job -t prod
databricks bundle run hello_world_app -t prod
```

Bundle-Init-Template für eine Streamlit-App:

```bash
databricks bundle init https://github.com/databricks/bundle-examples --template-dir contrib/templates/streamlit-app
```

---

## 25. Python- und Scala-Artefakte in Bundles

**Einfach erklärt:** Bundles können Python-Wheels und Scala-JARs bauen, deployen und als Job-Tasks ausführen — entweder über das Standard-Template, oder über eigene Poetry-/Setuptools-Konfigurationen. Zusätzlich lässt sich ein Bundle komplett in Python statt in YAML konfigurieren (PyDABs), inklusive programmatischer Ressourcenerzeugung und Mutator-Funktionen.

**Python-Wheel: Template-basiertes Setup**

Bundle erstellen:

```bash
databricks bundle init
```

Kompatibilitätshinweis für Runtime 12.2 LTS, in `databricks.yml`:

```yaml
experimental:
  python_wheel_wrapper: true
```

Validieren:

```bash
databricks bundle validate
```

Deployen:

```bash
databricks bundle deploy --target dev
```

Job ausführen:

```bash
databricks bundle run --target dev sample_job
```

**Python-Wheel: Poetry und Setuptools**

Gemeinsame Dateistruktur:

```
├── src
│   └── my_package
│       ├── __init__.py
│       ├── main.py
│       └── my_module.py
└── pyproject.toml   (Poetry) bzw. setup.py (Setuptools)
```

Poetry — `pyproject.toml`:

```toml
[tool.poetry]
name = "my_package"
version = "0.0.1"
description = "<package-description>"
authors = ["<author> <email@organization>"]

[tool.poetry.dependencies]
python = "^3.10"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.scripts]
main = "my_package.main:main"
```

Poetry — Bundle-Konfiguration:

```yaml
bundle:
  name: my-wheel-bundle

artifacts:
  default:
    type: whl
    build: poetry build
    path: .

resources:
  jobs:
    wheel-job:
      name: wheel-job
      tasks:
        - task_key: wheel-task
          new_cluster:
            spark_version: 13.3.x-scala2.12
            node_type_id: i3.xlarge
            data_security_mode: USER_ISOLATION
            num_workers: 1
          python_wheel_task:
            entry_point: main
            package_name: my_package
          libraries:
            - whl: ./dist/*.whl

targets:
  dev:
    workspace:
      host: <workspace-url>
```

Setuptools — `setup.py`:

```python
from setuptools import setup, find_packages

setup(
  name = "my_package",
  version = "0.0.1",
  author = "<author-name>",
  url = "https://<organization-url>",
  author_email = "<email@organization>",
  description = "<package-description>",
  packages=find_packages(where='./src'),
  package_dir={'': 'src'},
  entry_points={
    "packages": [
      "main=my_package.main:main"
    ]
  },
  install_requires=[
    "setuptools"
  ]
)
```

Setuptools — Bundle-Konfiguration:

```yaml
bundle:
  name: my-wheel-bundle

artifacts:
  default:
    type: whl
    build: python3 setup.py bdist_wheel
    path: .

resources:
  jobs:
    wheel-job:
      name: wheel-job
      tasks:
        - task_key: wheel-task
          new_cluster:
            spark_version: 13.3.x-scala2.12
            node_type_id: i3.xlarge
            data_security_mode: USER_ISOLATION
            num_workers: 1
          python_wheel_task:
            entry_point: main
            package_name: my_package
          libraries:
            - whl: ./dist/*.whl

targets:
  dev:
    workspace:
      host: <workspace-url>
```

**Scala-JAR bauen**

Bundle erstellen:

```bash
databricks bundle init default-scala
```

VM-Option (IntelliJ Run-Konfiguration):

```
--add-opens=java.base/java.nio=ALL-UNNAMED
```

Alternative (VS Code) — `build.sbt`:

```sbt
fork := true
javaOptions += "--add-opens=java.base/java.nio=ALL-UNNAMED"
```

Validieren:

```bash
databricks bundle validate
```

Deployen:

```bash
databricks bundle deploy -t dev
```

Ausführen:

```bash
databricks bundle run -t dev my_scala_project
```

**Python als Bundle-Konfigurationssprache (PyDABs)**

Projekt initialisieren:

```bash
databricks bundle init pydabs
```

Konfigurationsstruktur (`databricks.yml`):

```yaml
python:
  venv_path: .venv
  resources:
    - 'resources:load_resources'
```

Deployment:

```bash
databricks bundle deploy --target dev
databricks bundle summary --target dev
databricks bundle run [job_name]
```

Programmatische Ressourcenerzeugung:

```python
def create_job(country: str):
    return Job.from_dict({
        "name": f"my_job_{country}",
        "tasks": [...]
    })

def load_resources(bundle: Bundle) -> Resources:
    resources = load_resources_from_current_package_module()
    for country in ["US", "NL"]:
        resources.add_resource(f"my_job_{country}", create_job(country))
    return resources
```

Variablenzugriff über den `@variables`-Decorator:

```python
from databricks.bundles.core import Bundle, Variable, variables

@variables
class Variables:
    warehouse_id: Variable[str]

def load_resources(bundle: Bundle) -> Resources:
    warehouse_id = bundle.resolve_variable(Variables.warehouse_id)
```

Ressourcen-Mutation über Mutator-Funktionen:

```python
from databricks.bundles.core import job_mutator

@job_mutator
def add_email_notifications(bundle: Bundle, job: Job) -> Job:
    if job.email_notifications:
        return job
    email_notifications = JobEmailNotifications.from_dict({
        "on_failure": ["${workspace.current_user.userName}"],
    })
    return replace(job, email_notifications=email_notifications)
```

---

## 26. Bundle-Templates

**Einfach erklärt:** Templates sorgen für konsistente, wiederholbare Bundle-Erstellung, indem sie Ordnerstruktur, Build-Schritte und Best Practices vorgeben. Databricks liefert sieben Standard-Templates mit, eigene Templates lassen sich mit einer `databricks_template_schema.json` und Go-Template-Syntax (`.tmpl`-Dateien) selbst bauen und über Git oder eine zentrale Workspace-Konfiguration teilen.

**Sieben Standard-Templates:**

| Template | Zweck |
|---|---|
| `default-minimal` | leeres Bundle mit nur den essenziellen Dateien und Catalog-Variablen-Konfiguration |
| `default-python` | Python-basiertes Bundle mit Job und ETL-Pipeline; benötigt den `uv`-Paketmanager |
| `default-scala` | Scala-JAR-Kompilierung, konfiguriert für Serverless-Compute-Deployment |
| `default-sql` | SQL-Queries, ausgeführt auf einem SQL-Warehouse über einen konfigurierten Job |
| `dbt-sql` | dbt-core-Integration, kombiniert lokale Entwicklung mit Bundle-Deployment |
| `mlops-stacks` | fortgeschrittenes Full-Stack-Template für MLOps-Stacks-Projekte |
| `pydabs` | modifiziertes Python-Template, das Python statt YAML zur Konfiguration nutzt |

**`databricks_template_schema.json`-Felder:**

| Feld | Zweck |
|---|---|
| `properties` | definiert die während der Initialisierung abgefragten Eingabevariablen |
| `properties.<var>.default` | Standardwert ohne Nutzereingabe |
| `properties.<var>.description` | Prompt-Text für den Nutzer |
| `properties.<var>.enum` | Liste wählbarer Werte als CLI-Menü |
| `properties.<var>.order` | Ganzzahl zur Steuerung der Prompt-Reihenfolge |
| `properties.<var>.pattern` | Regexp zur Eingabevalidierung |
| `properties.<var>.pattern_match_failure_message` | Fehlermeldung bei Validierungsfehlschlag |
| `properties.<var>.skip_prompt_if` | Prompt bedingt überspringen |
| `template_dir` | Pfad zum Template-Verzeichnis bei Multi-Schema-Templates |
| `welcome_message` | Einleitende Nachricht vor den Prompts |
| `success_message` | Nachricht nach erfolgreicher Initialisierung |
| `min_databricks_cli_version` | Mindest-CLI-Versionsanforderung |

**Eingebaute Template-Helper:**

| Helper | Beschreibung |
|---|---|
| `{{url}}` | URL-Parsing aus Gos `net/url`-Paket |
| `{{regexp}}` | Regex-Kompilierung aus Gos `regexp`-Paket |
| `{{random_int}}` | nicht-negative Pseudozufallszahl |
| `{{uuid}}` | RFC-4122-konforme 128-Bit-UUID |
| `{{bundle_uuid}}` | stabile eindeutige ID des Bundles über Template-Ausführungen hinweg |
| `{{pair}}` | Key-Value-Paar-Utility zur Map-Erstellung |
| `{{map}}` | konvertiert Paarlisten zu Map-Objekten für Template-Argumente |
| `{{smallest_node_type}}` | gibt den kleinsten verfügbaren Node-Typ zurück |
| `{{path_separator}}` | Betriebssystem-Pfadtrenner (`/` oder `\`) |
| `{{workspace_host}}` | aktuelle Workspace-Host-URL |
| `{{user_name}}` | vollständiger Name des initialisierenden Nutzers |
| `{{short_name}}` | verkürzter Nutzername |
| `{{default_catalog}}` | Standard-Workspace-Catalog |
| `{{is_service_principal}}` | boolescher Wert, ob der Nutzer ein Service Principal ist |
| `{{ skip <glob-pattern> }}` | Dateien/Verzeichnisse überspringen |

**Grundsyntax:**

```bash
databricks bundle init [template-name]
databricks bundle init default-python
databricks bundle init /projects/my-custom-bundle-templates/dab-container-template
```

**Eigenes Template erstellen — Schritt 1: Schema-Datei anlegen**

```bash
mkdir dab-container-template
cd dab-container-template
touch databricks_template_schema.json
```

```json
{
  "properties": {
    "project_name": {
      "type": "string",
      "default": "project_name",
      "description": "Project name",
      "order": 1
    }
  }
}
```

**Schritt 2 — Ordnerstruktur anlegen:**

```bash
mkdir -p "template/{{.project_name}}"
mkdir -p "template/{{.project_name}}/resources"
mkdir -p "template/{{.project_name}}/src"
```

**Schritt 3 — YAML-Konfigurationstemplates**, `template/{{.project_name}}/databricks.yml.tmpl`:

```yaml
# This is a bundle definition for {{.project_name}}.
bundle:
  name: {{.project_name}}
include:
  - resources/*.yml
targets:
  dev:
    mode: development
    default: true
    workspace:
      host: {{workspace_host}}
  prod:
    mode: production
    workspace:
      host: {{workspace_host}}
      root_path: /Workspace/Production/.bundle/${bundle.name}
    {{- if not is_service_principal}}
    run_as:
      user_name: {{user_name}}
    {{end -}}
```

`template/{{.project_name}}/resources/{{.project_name}}_job.yml.tmpl`:

```yaml
resources:
  jobs:
    {{.project_name}}_job:
      name: {{.project_name}}_job
      tasks:
        - task_key: python_task
          job_cluster_key: job_cluster
          spark_python_task:
            python_file: ../src/task.py
      job_clusters:
        - job_cluster_key: job_cluster
          new_cluster:
            docker_image:
              url: databricksruntime/python:10.4-LTS
            node_type_id: i3.xlarge
            spark_version: 13.3.x-scala2.12
```

**Schritt 4 — referenzierte Dateien**, `template/{{.project_name}}/src/task.py`:

```python
print(f'Spark version{spark.version}')
```

**Schritt 5 — Struktur prüfen:**

```
dab-container-template
├── databricks_template_schema.json
└── template
    └── {{.project_name}}
        ├── databricks.yml.tmpl
        ├── resources
        │   └── {{.project_name}}_job.yml.tmpl
        └── src
            └── task.py
```

**Schritt 6 — Template testen:**

```bash
databricks bundle init dab-container-template
```

**Schema-Beispiel:**

```json
{
  "properties": {
    "project_name": {
      "type": "string",
      "default": "basic_bundle",
      "description": "What is the name of the bundle you want to create?",
      "order": 1
    }
  },
  "success_message": "\nYour bundle '{{.project_name}}' has been created."
}
```

**Eigene Helper** in `library/`-Dateien mit Go-Template-Syntax:

```go
{{ define `cli_version` -}}
    v0.240.0{{- end }}
{{ define `model_name` -}}
    {{ .input_project_name }}-model{{- end }}
```

**Konfigurationstemplate** (`databricks.yml.tmpl`):

```yaml
bundle:
  name: {{.project_name}}
include:
  - resources/*.yml
targets:
  dev:
    mode: development
    default: true
    workspace:
      host: {{workspace_host}}
  prod:
    mode: production
    workspace:
      host: {{workspace_host}}
      root_path: /Workspace/Production/.bundle/${bundle.name}
```

**Templates testen:**

```bash
databricks bundle init basic-bundle-template
```

**Templates teilen — über Versionskontrolle:**

```bash
databricks bundle init <git-url> --template-dir <folder-path>
```

**Erforderliche Ordnerstruktur bei zentraler Workspace-Konfiguration:**

```
folder-for-custom-templates/
├── example-custom-template/
├── custom-template-2/
├── custom-template-3/
└── ...
```

---

## 27. Konfiguration: databricks.yml

**Einfach erklärt:** `databricks.yml` ist die einzige Pflichtdatei eines Bundles und muss mindestens `bundle.name` sowie ein `targets`-Mapping mit einem Default-Ziel enthalten. Top-Level-Mappings steuern Metadaten, Ressourcen, Berechtigungen, Datei-Synchronisation und Build-Artefakte. Werte lassen sich über vordefinierte Substitutionen (systemseitig, z. B. `${bundle.name}`) oder benutzerdefinierte Variablen (einfach, komplex, Lookup) dynamisch statt hartkodiert einsetzen.

**Top-Level-Mappings:**

| Mapping | Inhalt |
|---|---|
| `bundle` | Kern-Metadaten: Name, CLI-Version, Cluster-ID, Deployment-Einstellungen, Git-Konfiguration |
| `run_as` | Identität für die Bundle-Ausführung — Nutzername oder Service-Principal-Name |
| `include` | referenziert zusätzliche Konfigurationsdateien oder Glob-Patterns |
| `scripts` | definiert ausführbare Skripte mit eindeutigen Namen und Inhalt |
| `sync` | steuert Datei-Synchronisation über Include-/Exclude-Patterns und spezifische Pfade |
| `artifacts` | verwaltet Build-Artefakte (Build-Befehle, Versionierung, Executables, Dateien, Pfade, Typdefinitionen) |
| `variables` | benutzerdefinierte Konfigurationsvariablen |
| `workspace` | Workspace-Konnektivität: Artefakt-Pfade, Host-URL, Auth-Profil, Ressourcen-Pfade, Root-Pfad, State-Pfad |
| `permissions` | ressourcenweite Zugriffskontrolle |
| `resources` | definiert Infrastruktur-Ressourcen |
| `targets` | Deployment-Umgebungen — genau ein Target muss `default: true` gesetzt haben |

**Ressourcentypen (Kurzübersicht):** Alerts, Apps, Catalogs, Clusters, Dashboards, Database Catalogs, Database Instances, Experiments, Jobs, Model-Serving-Endpoints, Pipelines, Postgres-Branches/-Endpoints/-Projects, Quality Monitors, Registered Models, Schemas, Secret Scopes, SQL Warehouses, Synced Database Tables, Volumes.

**Vordefinierte Substitutionen — Beispiele:** `${bundle.name}`, `${bundle.target}`, `${workspace.host}`, `${workspace.current_user.userName}`, `${workspace.current_user.short_name}`, `${workspace.current_user.domain_friendly_name}`, `${workspace.file_path}`, `${workspace.root_path}`, `${resources.jobs.<job-name>.id}`, `${resources.pipelines.<pipeline-name>.name}`, `${resources.models.<model-name>.name}`.

```yaml
workspace:
  root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/my-envs/${bundle.target}
```

**Einfache benutzerdefinierte Variablen:**

```yaml
variables:
  <variable-name>:
    description: <Text>
    default: <Wert>
```

```yaml
variables:
  my_cluster_id:
    description: The ID of an existing cluster.
    default: 1234-567890-abcde123
```

**Komplexe Variablen:**

```yaml
variables:
  my_cluster:
    description: 'My cluster definition'
    type: complex
    default:
      spark_version: '13.2.x-scala2.11'
      node_type_id: 'Standard_DS3_v2'
      num_workers: 2
      spark_conf:
        spark.speculation: true
        spark.databricks.delta.retentionDurationCheck.enabled: false

resources:
  jobs:
    my_job:
      job_clusters:
        - job_cluster_key: my_cluster_key
          new_cluster: ${var.my_cluster}
      tasks:
        - task_key: hello_task
          job_cluster_key: my_cluster_key
```

**Lookup-Variablen:**

```yaml
variables:
  <variable-name>:
    lookup:
      <object-type>: '<object-name>'
```

```yaml
variables:
  my_cluster_id:
    description: An existing cluster
    lookup:
      cluster: '12.2 shared'

resources:
  jobs:
    my_job:
      name: 'My Job'
      tasks:
        - task_key: TestTask
          existing_cluster_id: ${var.my_cluster_id}
```

Praxisbeispiel aus dem Kurs:

```yaml
variables:
  my_cluster_id:
    description: Get the lab cluster ID using a lookup variable.
    lookup:
      cluster: labuser15933383_1784728005   # Cluster-Name statt hartkodierter ID

targets:
  development:
    mode: development
    default: true
    resources:
      jobs:
        demo03_job:
          tasks:
            - task_key: create_bronze_table
              existing_cluster_id: ${var.my_cluster_id}
            - task_key: create_silver_table
              existing_cluster_id: ${var.my_cluster_id}
```

**Variablenwerte per Target-Level-Konfiguration setzen:**

```yaml
targets:
  dev:
    variables:
      my_cluster_id: 1234-567890-abcde123
      my_notebook_path: ./hello.py
  prod:
    variables:
      my_cluster_id: 2345-678901-bcdef234
      my_notebook_path: ./hello.py
```

**Unterschiede im Überblick:**

| Typ | Deklariert in `variables`? | Wert | Wann aufgelöst | Referenzsyntax |
|---|---|---|---|---|
| Vordefinierte Substitution | Nein — systemseitig bereitgestellt | Skalar, aus Kontext/bereits deployten Ressourcen | Deployment-/Config-Zeit | `${bundle.name}`, `${workspace.host}`, `${resources.jobs.<name>.id}`, … |
| Einfache benutzerdefinierte Variable | Ja | String (Default-Typ ohne `type`-Angabe) | Deployment-Zeit, per `default` oder Override | `${var.<name>}` |
| Komplexe Variable | Ja, mit `type: complex` | Strukturiertes Objekt/Map | Deployment-Zeit; als Ganzes referenziert | `${var.<name>}` |
| Lookup-Variable | Ja, mit `lookup:`-Mapping | ID eines bestehenden, per Name gesuchten Workspace-Objekts | Deployment-Zeit, per Namenssuche im Workspace | `${var.<name>}` |

**Deployment-Befehle:**

```bash
databricks bundle validate
databricks bundle deploy
databricks bundle run
```

**Workspace-Pfade:**

| Pfad-Feld | Zweck |
|---|---|
| `root_path` | Basis-Pfad für alles, was das Bundle im Workspace ablegt; Default: `/Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}` |
| `file_path` | Zielpfad für synchronisierte Quelldateien (Notebooks, Skripte) unterhalb des Root-Pfads |
| `artifact_path` | Zielpfad für gebaute Artefakte (Wheels, JARs) — auf einen Unity-Catalog-Volumes-Pfad gesetzt, lädt das Bundle referenzierte Artefakte automatisch nach Unity Catalog hoch |

---

## 28. Bundles im Workspace (Web-UI)

**Einfach erklärt:** Bundles lassen sich vollständig im Browser erstellen, bearbeiten und deployen, ohne YAML-Kenntnisse oder die lokale CLI zu benötigen. Ordner mit einer `databricks.yml` im Root werden automatisch als Bundle erkannt; über das Deployments-Panel lassen sich Job-, Pipeline- und Dashboard-Definitionen anlegen, bestehende Ressourcen einbinden und das Bundle in verschiedene Targets deployen.

**Job-Definition im Bundle-Editor:**

```yaml
resources:
  jobs:
    run_notebook:
      name: run-notebook
      queue:
        enabled: true
      tasks:
        - task_key: my-notebook-task
          notebook_task:
            notebook_path: ../helloworld.ipynb
```

**Pipeline-Definition:**

```yaml
resources:
  pipelines:
    test_pipeline:
      name: test_pipeline
      libraries:
        - notebook:
            path: ../test_pipeline.ipynb
      serverless: true
      catalog: main
      target: test_pipeline_${bundle.environment}
```

**Tutorial: Job definieren** — generierte `run-notebook.job.yml`:

```yaml
resources:
  jobs:
    run_notebook:
      name: run-notebook
      queue:
        enabled: true
      tasks:
        - task_key: my-notebook-task
          notebook_task:
            notebook_path: ../helloworld.ipynb
```

---

## 29. Deployment-Modi und Authentifizierung

**Einfach erklärt:** Der `development`-Modus vereinfacht schnelles Iterieren (Ressourcen-Präfixe, pausierte Zeitpläne, Cluster-Overrides erlaubt, kein Deployment-Lock), während der `production`-Modus striktere Validierung erzwingt (Pipeline-Status, Git-Branch, Service-Principal-Empfehlung, keine Cluster-Overrides). Für die Authentifizierung wird zwischen attended (User-to-Machine, für lokale Entwicklung) und unattended (Machine-to-Machine, für CI/CD) unterschieden.

**Development-Modus:**

```yaml
targets:
  dev:
    mode: development
```

**Production-Modus:**

```yaml
targets:
  prod:
    mode: production
```

Git-Branch-Validierung (optional):

```yaml
git:
  branch: main
```

**Benutzerdefinierte Presets:**

```yaml
targets:
  dev:
    presets:
      name_prefix: 'testing_'
      pipelines_development: true
      trigger_pause_status: PAUSED
      jobs_max_concurrent_runs: 10
      tags:
        department: finance
```

---

## 30. Zusammenarbeit und gemeinsame Dateien

**Einfach erklärt:** Organisationen mit vielen Bundles können Konfiguration und Code über ein dediziertes `shared/`-Verzeichnis in einem gemeinsamen Repository teilen. Externe Dateien werden über den `paths`-Key des `sync`-Mappings eingebunden, gemeinsame YAML-Konfiguration über `include`. Unterschiedliche Berechtigungsstufen (`CAN_VIEW`, `CAN_MANAGE`, `CAN_RUN`) steuern, wer Bundles einsehen, deployen oder ausführen darf.

**Empfohlene Repository-Struktur:**

```
databricks-bundle-repo/
├── shared/
│   ├── variables.yml
│   └── shared_library.py
├── job_bundle/
│   ├── databricks.yml
│   ├── resources/
│   ├── src/
│   └── README.md
├── pipeline_bundle/
│   ├── databricks.yml
│   ├── resources/
│   ├── src/
│   └── README.md
```

`shared/shared_library.py`:

```python
def multiply(a: int, b: int) -> int:
    return a * b
```

`shared/variables.yml`:

```yaml
variables:
  cluster_id:
    default: 1234-567890-abcde123
```

`job_bundle/databricks.yml`:

```yaml
bundle:
  name: job_bundle
sync:
  paths:
    - ../shared
    - ./src
include:
  - resources/*.yml
  - ../shared/*.yml
targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://my-workspace.cloud.databricks.com
  prod:
    mode: production
    workspace:
      host: https://my-workspace.cloud.databricks.com
      root_path: /Workspace/Users/someone@example.com/.bundle/${bundle.name}/${bundle.target}
    permissions:
      - user_name: someone@example.com
        level: CAN_MANAGE
```

`resources/job_bundle.job.yml`:

```yaml
resources:
  jobs:
    my_python_job:
      name: my_python_job
      tasks:
        - task_key: python_task
          spark_python_task:
            python_file: src/my_python.py
    my_notebook_job:
      name: my_notebook_job
      tasks:
        - task_key: notebook_task
          existing_cluster_id: ${var.cluster_id}
          notebook_task:
            notebook_path: src/notebook.ipynb
```

`src/my_python.py` — Zugriff auf die gemeinsame Bibliothek:

```python
import os
import sys

# Zum Sync-Root-Pfad navigieren.
# Hinweis: erfordert DBR >= 14 oder Serverless.
shared_path = os.getcwd() + "/../../shared"

sys.path.append(shared_path)

from shared_library import multiply

result = multiply(2, 3)
print(result)
```

Validierung vor jedem Deployment:

```bash
databricks bundle validate
```

**Berechtigungen für gemeinsam genutzte Bundles:**

```yaml
bundle:
  name: shared_bundle
include:
  - resources/*.yml
permissions:
  - level: CAN_VIEW
    group_name: all_users
  - level: CAN_MANAGE
    group_name: data_engineering_users
  - level: CAN_RUN
    service_principal_name: 123456-abcdef
targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://my-workspace.cloud.databricks.com
  prod:
    mode: production
    workspace:
      host: https://my-workspace.cloud.databricks.com
      root_path: /Workspace/Users/someone@example.com/.bundle/${bundle.name}/${bundle.target}
    permissions:
      - user_name: someone@example.com
        level: CAN_MANAGE
```

---

## 31. Manuelle Bundle-Erstellung und Ressourcen-Migration

**Einfach erklärt:** Ein Bundle lässt sich komplett ohne Template von Grund auf bauen — gezeigt am vollständigen „baby-names"-Beispiel mit zwei Notebooks, einem Job mit zwei abhängigen Tasks und einem `development`-Target. Bestehende Jobs/Pipelines lassen sich nachträglich per `databricks bundle generate` (automatische Konfigurationserzeugung) plus `databricks bundle deployment bind` (Verknüpfung mit dem Workspace-Objekt) in ein Bundle übernehmen, alternativ manuell über „Edit as YAML"/„View settings YAML" in der UI.

**Notebooks des baby-names-Bundles**, `retrieve-baby-names.py`:

```python
# Databricks notebook source
import requests
response = requests.get('http://health.data.ny.gov/api/views/jxy9-yhdk/rows.csv')
csvfile = response.content.decode('utf-8')
dbutils.fs.put("/Volumes/main/default/my-volume/babynames.csv", csvfile, True)
```

`filter-baby-names.py`:

```python
# Databricks notebook source
babynames = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load("/Volumes/main/default/my-volume/babynames.csv")
babynames.createOrReplaceTempView("babynames_table")
years = spark.sql("select distinct(Year) from babynames_table").toPandas()['Year'].tolist()
years.sort()
dbutils.widgets.dropdown("year", "2014", [str(x) for x in years])
display(babynames.filter(babynames.Year == dbutils.widgets.get("year")))
```

Bundle-Schema generieren (optional, empfohlen):

```bash
databricks bundle schema > bundle_config_schema.json
```

`databricks.yml`:

```yaml
# yaml-language-server: $schema=bundle_config_schema.json
bundle:
  name: baby-names
resources:
  jobs:
    retrieve-filter-baby-names-job:
      name: retrieve-filter-baby-names-job
      job_clusters:
        - job_cluster_key: common-cluster
          new_cluster:
            spark_version: 12.2.x-scala2.12
            node_type_id: i3.xlarge
            num_workers: 1
      tasks:
        - task_key: retrieve-baby-names-task
          job_cluster_key: common-cluster
          notebook_task:
            notebook_path: ./retrieve-baby-names.py
        - task_key: filter-baby-names-task
          depends_on:
            - task_key: retrieve-baby-names-task
          job_cluster_key: common-cluster
          notebook_task:
            notebook_path: ./filter-baby-names.py
targets:
  development:
    workspace:
      host: <workspace-url>
```

Validieren:

```bash
databricks bundle validate
```

Deployen:

```bash
databricks bundle deploy -t development
```

Job ausführen:

```bash
databricks bundle run -t development retrieve-filter-baby-names-job
```

Aufräumen:

```bash
databricks bundle destroy
```

**Programmatische Job-/Pipeline-Generierung:**

```bash
databricks bundle generate job --existing-job-id 6565621249
databricks bundle generate pipeline --existing-pipeline-id 6565621249
databricks pipelines generate --existing-pipeline-dir src/my_pipeline
```

**Ressourcen binden:**

```bash
databricks bundle deployment bind hello_job 6565621249
databricks bundle deployment unbind hello_job
```

**Multi-Workspace-Migrationsstrategie:**

```bash
databricks bundle generate job --existing-job-id <dev_job_id> --target dev
databricks bundle deployment bind my_job <dev_job_id> --target dev
databricks bundle deployment bind my_job <prod_job_id> --target prod
databricks bundle deploy --target dev
databricks bundle deploy --target prod
```

---

## 32. MLOps Stacks

**Einfach erklärt:** Ein MLOps Stack ist ein produktionsreifes ML-Projekt-Framework, aufgebaut auf Bundles und der Databricks CLI — es liefert von Haus aus Best Practices für ML-Code und CI/CD-Infrastruktur. Es gibt drei Setup-Varianten: vollständig (Code + CI/CD), nur ML-Code oder nur CI/CD-Infrastruktur.

Authentifizierung:

```bash
databricks auth login --host <workspace-url>
```

Bundle-Projekt erstellen:

```bash
databricks bundle init mlops-stacks
```

Validierung:

```bash
databricks bundle validate
```

Deployment:

```bash
databricks bundle deploy -t <target-name>
```

Ausführung:

```bash
databricks bundle run -t <target-name> <job-name>
```

Aufräumen (optional):

```bash
databricks bundle destroy -t <target-name>
```

---

## 33. Direct Deployment Engine

**Einfach erklärt:** Die Direct Deployment Engine ist eine neuere, auf dem Databricks Go SDK basierende Alternative zur klassischen Terraform-Engine — bis zu 40 % schnellere Deployments, detaillierte JSON-Diffs, Plan-Wiederholbarkeit und Support für Ressourcen wie Catalogs, External Locations, AI-Search-Endpoints und Genie Spaces, die mit Terraform gar nicht definierbar sind. Ab CLI 0.279.0 stehen beide Engines (`terraform` und `direct`) zur Wahl.

**Migration bestehender Bundles:**

```bash
databricks bundle deploy -t my_target
```

```bash
databricks bundle deployment migrate -t my_target
```

```bash
databricks bundle plan -t my_target
```

```bash
databricks bundle deploy -t my_target
```

Bei Fehlschlag die neue State-Datei entfernen:

```bash
rm .databricks/bundle/my_target/resources.json
```

**Direct Deployment für neue Bundles konfigurieren — Methode 1 (YAML):**

```yaml
bundle:
  engine: direct
```

**Methode 2 (Umgebungsvariable):**

```bash
DATABRICKS_BUNDLE_ENGINE=direct databricks bundle deploy -t my_target
```

**Exklusiv unterstützte Ressourcen:** Unity-Catalog-Catalogs, Unity-Catalog-External-Locations, Unity-Catalog-Secrets, Genie Spaces, Instance Pools, AI-Search-Endpoints — sowie das Feld `lifecycle.started` (Apps, Clusters, SQL Warehouses).

---

## 34. Air-Gapped-Umgebungen

**Einfach erklärt:** Ohne Internetzugriff lassen sich Bundle-Befehle über das offizielle Databricks-CLI-Docker-Image (ARM64 und AMD64) ausführen — entweder direkt per einzelnem `docker run`-Aufruf oder interaktiv in einer Container-Shell mit bidirektionaler Dateisynchronisation zum lokalen Verzeichnis.

Docker-Image herunterladen (neueste Version):

```bash
docker pull ghcr.io/databricks/cli:latest
```

Bestimmte Version:

```bash
docker pull ghcr.io/databricks/cli:v0.218.0
```

Direkte Ausführung:

```bash
docker run -v /my-bundle:/my-bundle -e DATABRICKS_HOST=... \
-e DATABRICKS_TOKEN=... --workdir /my-bundle \
ghcr.io/databricks/cli:latest bundle deploy
```

Interaktive Ausführung:

```bash
docker run -v /my-bundle:/my-bundle -e DATABRICKS_HOST=... \
-e DATABRICKS_TOKEN=... -it --entrypoint /bin/sh \
--workdir /my-bundle ghcr.io/databricks/cli:latest
```

Befehle innerhalb der Sitzung:

```bash
/my-bundle # databricks bundle deploy
```

---

## 35. FAQ

**Einfach erklärt:** Diese Datei beantwortet neun häufige Fragen zu Declarative Automation Bundles in Fließtext-Form — von der Namensänderung über CI/CD-Integration, Dev/Prod-Trennung, Templates zur Standardisierung, Variablen gegen Wiederholung, acht Deployment-Best-Practices, Ressourcen-Migration bis hin zu iterativem Testen. Sie enthält keine eigenständigen Code-Beispiele, sondern verweist auf die entsprechenden Detail-Kapitel.

**Acht Best Practices für den Deployment-Flow:**
1. Von manuellen zu automatisierten, Git-integrierten Deployment-Workflows wechseln.
2. Bundles mit `databricks bundle validate` innerhalb von CI/CD validieren.
3. Deploy-Schritte für Review und bewusste Änderungen trennen.
4. Umgebungen (Dev, Staging, Prod) über Overrides parametrisieren.
5. Integrationstests nach dem Deployment ausführen.
6. GitHub Actions, Azure DevOps oder GitLab CI nutzen, um Deployments auszulösen.
7. Deployment-Tracking pflegen, das jedes Deployment mit einem bestimmten Commit verknüpft.
8. Deployment-Versionen und -Orte systematisch überwachen.

Keine Code-Beispiele in dieser Datei.

---

## 36. VS Code Extension

**Einfach erklärt:** Die „Databricks IDE extension" für Visual Studio Code (und Cursor) verbindet lokale Entwicklung mit Remote-Ausführung auf Databricks: Python-Dateien und Notebooks remote ausführen, interaktiv debuggen, Code synchronisieren — und speziell für Bundles einen Bundle Resource Explorer, Target-Selector, Single-Click-Deploy sowie eine Bundle-Variables-View bereitstellen. Empfohlene Authentifizierung ist OAuth U2M; Personal Access Tokens gelten als Legacy-Methode.

**Voraussetzungen:** VS Code ≥ 1.86.0; konfigurierter Python-Interpreter; mindestens ein Databricks-Cluster. SQL Warehouses werden von der Extension nicht unterstützt.

**Praktischer Ablauf: Workspace-URL in einem Notebook ermitteln:**

```python
lab_databricks_url = f'{spark.conf.get("spark.databricks.workspaceUrl")}/'
print(lab_databricks_url)
```

---

## 37. Ressourcentypen (Referenz)

**Einfach erklärt:** Diese Referenztabelle listet alle über `resources` in `databricks.yml` definierbaren Ressourcentypen mit ihren wichtigsten Feldern — von Compute (Clusters, Jobs, Pipelines) über Daten/Analytics (Dashboards, SQL Warehouses, Quality Monitors), Unity-Catalog-Objekte (Catalogs, Schemas, Volumes, Secrets), ML/Serving (Experiments, Model Serving, Apps), Lakebase/Postgres bis zu Such-/KI-Ressourcen (Vector Search, Genie Spaces) und Alerts/Instance Pools.

**Compute und Orchestrierung:**

| Ressource | Wichtige Felder | Besonderheiten |
|---|---|---|
| `clusters` | `spark_version`, `node_type_id`, `num_workers`, `autoscale`, `autotermination_minutes` | Cloud-spezifische Attribute für AWS/Azure/GCP; Init-Scripts über DBFS, S3, Workspace-Dateien oder Volumes |
| `jobs` | siehe Job-Task-Typen-Referenz | Python-Unterstützung (PyDABs) verfügbar |
| `pipelines` | Spark-Declarative-Pipelines-Definition | Python-Unterstützung verfügbar |

**Daten und Analytics:**

| Ressource | Wichtige Felder | Besonderheiten |
|---|---|---|
| `dashboards` (Lakeview) | `display_name`, `file_path`, `warehouse_id`, `embed_credentials` | Dateiendung `.lvdash.json`; weicht das lokale Dashboard-JSON vom Remote-Stand ab, schlägt das Deployment fehl — Überschreiben nur explizit über `--force` |
| `sql_warehouses` | dedizierte SQL-Analytics-Compute | — |
| `quality_monitors` | Data-Quality-Automatisierung | — |

**Unity-Catalog-Ressourcen:**

| Ressource | Wichtige Felder | Besonderheiten |
|---|---|---|
| `catalogs` | `name`, `comment`, `storage_root`, `connection_name` | erfordert die Direct Deployment Engine — mit der Terraform-Engine nicht definierbar |
| `schemas` | Organisation von Objekten innerhalb eines Catalogs | Python-Unterstützung verfügbar |
| `volumes` | unstrukturierte Datenablage | Python-Unterstützung verfügbar |
| `external_locations` | Anbindung an Cloud-Storage | Teil der Unity-Catalog-Governance |
| `registered_models` | Modell-Lebenszyklus | Unity-Catalog-Integration |
| `secrets` | sichere Credential-Ablage | von den (legacy) `secret_scopes` zu unterscheiden |
| `secret_scopes` (Legacy) | Workspace-Ebenen-Secrets | — |

**ML und Serving:**

| Ressource | Wichtige Felder | Besonderheiten |
|---|---|---|
| `experiments` | MLflow-Experiment-Tracking | — |
| `model_serving_endpoints` | REST-API-Objektreferenz | kein `run_as`-Support |
| `apps` | `name`, `source_code_path`, `compute_size`, `description` | Namensregel: nur Kleinbuchstaben, Ziffern und Bindestriche |

**Lakebase/Postgres:**

| Ressource | Beschreibung |
|---|---|
| `synced_database_tables` | Lakebase-Tabellensynchronisation |
| `database_instances` | Lakebase-Provisionierung |
| `database_catalogs` | registriert Lakebase-Datenbanken als UC-Catalogs — Felder `database_name`, `database_instance_name` |
| `postgres`-Endpoints, -Projects, -Catalogs, -Databases, -Branches, -Roles, Synced Tables | vollständige Postgres-kompatible Stack-Verwaltung |

**Suche und KI:**

| Ressource | Beschreibung |
|---|---|
| Vector-Search-Endpoints | als „AI-Search-Endpoint"-Objekt bezeichnet |
| Vector-Search-Indexes | Index-Verwaltung für Embeddings |
| Genie Spaces | KI-Agent-Konfiguration mit natürlichsprachlicher Schnittstelle |

**Alerts und Instance Pools:**

| Ressource | Wichtige Felder | Besonderheiten |
|---|---|---|
| `alerts` | `display_name`, `query_text`, `warehouse_id`, `schedule` | unterstützt Aggregationsfunktionen (SUM, COUNT, STDDEV usw.); unterstützt `run_as` |
| Instance Pools | vorkonfigurierte Compute-Node-Gruppen | — |

Keine Code-Beispiele in dieser Datei.

---

## 38. Job-Task-Typen (Referenz)

**Einfach erklärt:** Diese Referenztabelle listet alle Task-Typen, die sich innerhalb eines `jobs`-Ressourcenblocks in `databricks.yml` verwenden lassen — von Notebook- und Python-Script-Tasks über SQL-, dbt-, JAR- und Python-Wheel-Tasks bis zu Kontrollfluss-Tasks (Condition, For-Each, Run-Job) und spezialisierten Tasks (Dashboard, Power BI, Clean Rooms, AI Runtime, Alert).

| Task-Typ (Mapping-Key) | Wichtige Felder | Besonderheiten |
|---|---|---|
| AI-Runtime-Task (`ai_runtime_task`) | `deployments`, `experiment`, `mlflow_experiment_directory`, `mlflow_run` | Multi-GPU-Compute-Workloads auf Databricks AI Runtime |
| Alert-Task v2 (`alert_task`) | `alert_id`, `workspace_path`, `warehouse_id`, `subscribers` | wertet einen Alert aus und benachrichtigt Subscriber |
| Clean-Room-Notebook-Task (`clean_rooms_notebook_task`) | `clean_room_name`, `notebook_name`, `object`, `etag` | führt Notebooks innerhalb von Databricks Clean Rooms aus |
| Condition-Task (`condition_task`) | `left`, `op`, `right` | If/Else-Verzweigungslogik mit Operatoren wie `EQUAL_TO`, `GREATER_THAN` |
| Dashboard-Task (`dashboard_task`) | `dashboard_id`, `warehouse_id`, `subscription` | aktualisiert ein Dashboard und versendet Snapshots |
| dbt-Task (`dbt_task`) | `commands`, `project_directory`, `warehouse_id`, `catalog`, `schema`, `profiles_directory`, `source` | max. 10 Befehle sequenziell |
| For-Each-Task (`for_each_task`) | `inputs`, `task`, `concurrency` | iteriert über Array-Eingaben, unterstützt parallele Iteration |
| JAR-Task (`spark_jar_task`) | `main_class_name`, `parameters`, `jar_uri` (deprecated) | statt `jar_uri` das `libraries`-Feld nutzen |
| Notebook-Task (`notebook_task`) | `notebook_path`, `base_parameters`, `source`, `warehouse_id` | führt Workspace- oder Git-Notebooks aus |
| Pipeline-Task (`pipeline_task`) | `pipeline_id`, `full_refresh` | löst eine Spark-Declarative-Pipeline aus |
| Power-BI-Task (`power_bi_task`) | `connection_resource_name`, `power_bi_model`, `tables`, `warehouse_id`, `refresh_after_update` | aktualisiert Power-BI-Semantikmodelle; Public Preview |
| Python-Script-Task (`spark_python_task`) | `python_file`, `parameters`, `source` | Workspace-Pfade absolut, Git-Pfade relativ |
| Python-Wheel-Task (`python_wheel_task`) | `package_name`, `entry_point`, `parameters`, `named_parameters` | `parameters` und `named_parameters` schließen sich gegenseitig aus |
| Run-Job-Task (`run_job_task`) | `job_id`, `job_parameters`, `pipeline_params` | führt einen bestehenden Job innerhalb eines anderen Job-Workflows aus |
| SQL-Task (`sql_task`) | `warehouse_id`, `file`, `query`, `alert`, `dashboard`, `parameters` | Parameterreferenzen über `{{parameter_key}}` |

**Gemeinsame Task-Einstellungen** (unabhängig vom Typ): `task_key`, `depends_on`, `description`, `timeout_seconds`, `max_retries`, `min_retry_interval_millis`, `retry_on_timeout`, `libraries`, `email_notifications`, `webhook_notifications`, `notification_settings`, `run_if`, `existing_cluster_id`, `new_cluster`, `job_cluster_key`, `environment_key`, `disable_auto_optimization`, `health`, `compute`.

Keine Code-Beispiele in dieser Datei.

---

## 39. Job-Parameter vs. Bundle-Variablen

**Einfach erklärt:** Bundle-Variablen werden beim Deployment aufgelöst und eignen sich für pro-Umgebung wechselnde Werte (z. B. Cluster-Größe). Job-Parameter werden erst beim Job-Lauf aufgelöst und lassen sich ohne erneutes Deployment überschreiben — ideal für pro-Lauf wechselnde Werte (z. B. Verarbeitungsdatum). Job-Level-`parameters` und Task-Level-`base_parameters` dürfen nicht gemeinsam im selben Job verwendet werden.

| Änderungshäufigkeit | Mechanismus | Anwendungsfall |
|---|---|---|
| pro Umgebung (dev/staging/prod) | Bundle-Variablen | Cluster-Größe, Warehouse-ID |
| pro Job-Lauf | Job-Parameter | Verarbeitungsdatum, Quelltabelle |
| pro Task (keine Job-Parameter vorhanden) | Task-`base_parameters` | task-spezifische Dateipfade |

**Vollständiges Beispiel mit umgebungsspezifischen Defaults:**

```yaml
# databricks.yml
variables:
  default_catalog:
    description: Environment-specific catalog
    default: dev_catalog

targets:
  dev:
    variables:
      default_catalog: biz_dev
  prod:
    variables:
      default_catalog: biz_prod

resources:
  jobs:
    etl_pipeline:
      name: etl_pipeline
      parameters:
        - name: catalog
          default: ${var.default_catalog}
        - name: processing_date
          default: '{{job.start_time.iso_date}}'
        - name: mode
          default: incremental
      tasks:
        - task_key: process_data
          notebook_task:
            notebook_path: ./notebooks/process.py
```

**Nur Job-Level-Parameter:**

```yaml
resources:
  jobs:
    my_job:
      parameters:
        - name: catalog
          default: dev
        - name: schema
          default: default
      tasks:
        - task_key: task1
          notebook_task:
            notebook_path: ./notebook.py
```

**Zur Laufzeit überschreiben — CLI:**

```bash
databricks bundle run my_job -- --catalog=prod --mode=full_refresh
```

**REST API:**

```json
{
  "job_id": 123,
  "job_parameters": {
    "catalog": "prod",
    "mode": "full_refresh"
  }
}
```

---

## 40. Run As: Deployment- vs. Ausführungsidentität

**Einfach erklärt:** `run_as` trennt die Identität, die ein Bundle deployt, von der Identität, unter der die deployten Ressourcen tatsächlich laufen — konfigurierbar auf Top-Level (alle Ressourcen) oder pro Target. Sind Deployer- und `run_as`-Identität identisch, funktionieren alle Ressourcentypen; unterscheiden sie sich, werden nur Jobs und Pipelines unterstützt. Model-Serving-Endpoints unterstützen `run_as` gar nicht.

```yaml
bundle:
  name: example
  run_as:
    service_principal_name: 'ID-here'
```

**Unterstützte Identitäten:**

| Feld | Format |
|---|---|
| `user_name` | E-Mail-Adresse |
| `service_principal_name` | Application-ID |

**Ressourcen-Support je nach Identitätskonstellation:**

| Konstellation | Unterstützte Ressourcen |
|---|---|
| Deployer-Identität und `run_as`-Identität sind identisch | alle Bundle-Ressourcen |
| Deployer-Identität und `run_as`-Identität unterscheiden sich | nur Jobs und Pipelines |

---

## 41. Berechtigungen (Permissions)

**Einfach erklärt:** Berechtigungen lassen sich entweder global im Top-Level-`permissions`-Mapping (Stufen `CAN_VIEW`, `CAN_MANAGE`, `CAN_RUN`) oder granular pro Ressource setzen — dürfen sich aber für denselben Prinzipal nicht überlappen. Bei mehreren Ebenen gilt eine klare Präzedenzreihenfolge: Target-Ressourcen-Permissions schlagen Target-Permissions, die wiederum Top-Level-Ressourcen-Permissions und Top-Level-Bundle-Permissions schlagen.

**Berechtigungsstufen je Ressourcentyp:**

| Ressource | Erlaubte Stufen |
|---|---|
| Alerts | `CAN_EDIT`, `CAN_MANAGE`, `CAN_READ`, `CAN_RUN` |
| Apps | `CAN_MANAGE`, `CAN_USE` |
| Clusters | `CAN_ATTACH_TO`, `CAN_MANAGE`, `CAN_RESTART` |
| Dashboards | `CAN_EDIT`, `CAN_MANAGE`, `CAN_RUN`, `CAN_READ` |
| Database Instances | `CAN_MANAGE`, `CAN_USE`, `CAN_CREATE` |
| Genie Agents | `CAN_EDIT`, `CAN_MANAGE`, `CAN_RUN`, `CAN_VIEW` |
| Experiments | `CAN_EDIT`, `CAN_MANAGE`, `CAN_READ`, `CAN_RUN` |
| Jobs | `CAN_MANAGE`, `CAN_MANAGE_RUN`, `CAN_VIEW`, `IS_OWNER` |
| Models | `CAN_EDIT`, `CAN_MANAGE`, `CAN_MANAGE_STAGING_VERSIONS`, `CAN_MANAGE_PRODUCTION_VERSIONS`, `CAN_READ` |
| Pipelines | `CAN_MANAGE`, `CAN_RUN`, `CAN_VIEW`, `IS_OWNER` |
| Secret Scopes | `READ`, `WRITE`, `MANAGE` |
| SQL Warehouses | `CAN_MANAGE`, `CAN_USE`, `CAN_VIEW`, `CAN_MONITOR`, `IS_OWNER` |

**Top-Level-Permissions-Mapping:**

```yaml
bundle:
  name: my-bundle
resources:
  jobs:
    my-job:
      # ...
targets:
  dev:
    permissions:
      - user_name: someone@example.com
        level: CAN_RUN
```

**Präzedenz bei mehreren Ebenen — Beispiel:**

```yaml
bundle:
  name: my-bundle
permissions:
  - group_name: test-group
    level: CAN_VIEW
resources:
  jobs:
    my-job:
      permissions:
        - group_name: test-group
          level: CAN_MANAGE_RUN
targets:
  dev:
    resources:
      jobs:
        my-job:
          permissions:
            - group_name: test-group
              level: CAN_MANAGE   # gewinnt für dev
  prod:
    # kein Override -> CAN_MANAGE_RUN gilt
```

**Target-spezifische Ressourcen-Permissions:**

```yaml
targets:
  <target-id>:
    resources:
      pipelines:
        <pipeline-id>:
          permissions:
            - user_name: <name>
              level: <permission-level>
```

---

## 42. Overrides zwischen Targets

**Einfach erklärt:** Ist eine Einstellung sowohl im Top-Level-Mapping als auch im `targets`-Mapping definiert, gewinnt die Target-Einstellung. Bei Artifacts, Clustern (über `job_cluster_key`/`label`) und Job-Tasks (über `task_key`) werden nicht-konfliktbehaftete Felder zusammengeführt (gemergt), konfliktbehaftete Felder vollständig durch den Target-Wert ersetzt.

**Artifact-Overrides:**

```yaml
artifacts:
  my-artifact:
    type: whl
    path: ./my_package
targets:
  dev:
    artifacts:
      my-artifact:
        path: ./my_other_package
```

**Cluster-Overrides — Merge nicht-konfliktbehafteter Felder:**

```yaml
resources:
  jobs:
    my-job:
      job_clusters:
        - job_cluster_key: my-cluster
          new_cluster:
            spark_version: 13.3.x-scala2.12
targets:
  development:
    resources:
      jobs:
        my-job:
          job_clusters:
            - job_cluster_key: my-cluster
              new_cluster:
                node_type_id: i3.xlarge
                num_workers: 1
```

**Cluster-Overrides — konfliktbehaftete Felder:**

```yaml
resources:
  jobs:
    my-job:
      job_clusters:
        - job_cluster_key: my-cluster
          new_cluster:
            spark_version: 13.3.x-scala2.12
            num_workers: 1
targets:
  development:
    resources:
      jobs:
        my-job:
          job_clusters:
            - job_cluster_key: my-cluster
              new_cluster:
                spark_version: 12.2.x-scala2.12
                num_workers: 2
```

**Job-Task-Overrides:**

```yaml
resources:
  jobs:
    my-job:
      tasks:
        - task_key: my-task
          new_cluster:
            spark_version: 13.3.x-scala2.12
targets:
  development:
    resources:
      jobs:
        my-job:
          tasks:
            - task_key: my-task
              new_cluster:
                node_type_id: i3.xlarge
                num_workers: 1
```

---

## 43. Private Artefakte

**Einfach erklärt:** Stammt eine Abhängigkeit aus einer privaten Quelle (privates PyPI-Repository, JFrog Artifactory), kann Databricks sie nicht automatisch zur Deploy-Zeit herunterladen — das Artefakt muss vorab lokal beschafft und dann per lokalem Pfad oder Unity-Catalog-Volumes-Pfad referenziert werden. Setzt man `artifact_path` auf einen UC-Volumes-Pfad, lädt das Bundle referenzierte Artefakte automatisch nach Unity Catalog hoch.

Lokal herunterladen:

```bash
pip download -d dist my-wheel==1.0
```

Für authentifizierte Quellen:

```bash
export PYPI_TOKEN=<YOUR TOKEN>
pip download -d dist my-package==1.0.0 --index-url https://$PYPI_TOKEN@<package-index-url> --no-deps
```

Optional nach Unity Catalog hochladen:

```bash
databricks fs cp my-wheel-1.0-*.whl dbfs:/Volumes/myorg_test/myorg_volumes/packages
```

In der Bundle-Konfiguration referenzieren — lokale Referenz:

```yaml
libraries:
  - whl: ../dist/my-wheel-1.0-*.whl
```

Unity-Catalog-Referenz:

```yaml
libraries:
  - whl: /Volumes/myorg_test/myorg_volumes/packages/my-wheel-1.0-py3-none-any.whl
```

---

## 44. Bibliotheksabhängigkeiten (libraries)

**Einfach erklärt:** Das `libraries`-Mapping auf Task- bzw. Pipeline-Ebene unterstützt Python-Wheels, JARs, PyPI-Pakete, Maven-Koordinaten und `requirements.txt` aus lokalen, Workspace- oder Unity-Catalog-Volume-Pfaden. Für modernes Python-Dependency-Management empfiehlt Databricks `uv` mit `pyproject.toml`. Bibliotheken im DBFS-Root sind ab Runtime 15.1 deprecated.

**Python-Wheel-Dateien:**

```yaml
resources:
  jobs:
    my_job:
      tasks:
        - task_key: my_task
          libraries:
            - whl: ./my-wheel-0.1.0.whl
            - whl: /Workspace/Shared/Libraries/my-wheel-0.0.1-py3-none-any.whl
            - whl: /Volumes/main/default/my-volume/my-wheel-0.1.0.whl
```

**JAR-Dateien:**

```yaml
resources:
  jobs:
    my_job:
      tasks:
        - task_key: my_task
          libraries:
            - jar: /Volumes/main/default/my-volume/my-java-library-1.0.jar
```

**PyPI-Pakete:**

```yaml
resources:
  jobs:
    my_job:
      tasks:
        - task_key: my_task
          libraries:
            - pypi:
                package: wheel==0.41.2
            - pypi:
                package: numpy==1.25.2
                repo: https://pypi.org/simple/
```

**Maven-Pakete:**

```yaml
resources:
  jobs:
    my_job:
      tasks:
        - task_key: my_task
          libraries:
            - maven:
                coordinates: com.databricks:databricks-sdk-java:0.8.1
            - maven:
                coordinates: com.databricks:databricks-dbutils-scala_2.13:0.1.4
                repo: https://mvnrepository.com/
                exclusions:
                  - org.scala-lang:scala-library:2.13.0-RC*
```

**`requirements.txt`:**

```yaml
resources:
  jobs:
    my_job:
      tasks:
        - task_key: my_task
          libraries:
            - requirements: ./local/path/requirements.txt
```

**`uv` und `pyproject.toml`:**

```toml
[project]
name = "test"
version = "0.0.1"
requires-python = ">=3.10,<3.13"
dependencies = [
    "numpy==1.25.2"
]
```

Einbindung in eine Pipeline-Ressource:

```yaml
resources:
  pipelines:
    test_uv_etl:
      name: test_uv_etl
      libraries:
        - glob:
            include: ../src/test_uv_etl/transformations/**
      environment:
        dependencies:
          - --editable ${workspace.file_path}
```

Artefakt-Build über `uv`:

```yaml
artifacts:
  python_artifact:
    type: whl
    build: uv build --wheel
```

---

## 45. Beispiele (bundle-examples Repo)

**Einfach erklärt:** Das offizielle GitHub-Repository `databricks/bundle-examples` enthält vollständige, lauffähige Bundle-Beispiele nach Anwendungsfall gruppiert — von Apps/Dashboards über Job-Workflows und Infrastruktur/Daten bis zu fortgeschrittenen Mustern wie privater Paketverteilung, Serverless-Jobs und Vector Search. Sie dienen als praktische Vorlagen, ohne dass man Konfiguration von Grund auf schreiben muss.

**Apps und Dashboards:**

| Beispiel | Beschreibung |
|---|---|
| `app_with_database` | Databricks App, unterstützt von einer OLTP-Postgres-Datenbank |
| `app_with_genie_space` | Bundle mit einer App, die einen Genie-Agent nutzt |
| `databricks_app` | grundlegendes App-Definitionsbeispiel |
| `dashboard_nyc_taxi` | AI/BI-Dashboard plus Job, der einen Snapshot des Dashboards erfasst und per E-Mail versendet |
| `genie_space_nyc_taxi` | Genie-Agent, der Fragen zur Tabelle `samples.nyctaxi.trips` beantwortet |

**Job-Workflows:**

| Beispiel | Beschreibung |
|---|---|
| `job_backfill_data` | SQL-Task mit Datumsparametern für historische Datenverarbeitung |
| `job_conditional_execution` | Job mit bedingter Task-Ausführung basierend auf Data-Quality-Checks |
| `job_file_arrival` | Job mit Datei-Ankunfts-Trigger zur automatischen Verarbeitung neuer Dateien |
| `job_read_secret` | Secret-Scope-Integration in Job-Tasks |
| `job_table_update_trigger` | ereignisgesteuerter Workflow, ausgelöst durch Tabellen-Updates |
| `job_with_multiple_wheels` | mehrere Python-Wheel-Abhängigkeiten in einem Job |
| `job_with_run_job_tasks` | Orchestrierung mehrerer Jobs über `run_job_task` |
| `job_with_sql_notebook` | Ausführung eines SQL-Notebook-Tasks |

**Infrastruktur und Daten:**

| Beispiel | Beschreibung |
|---|---|
| `database_with_catalog` | OLTP-Database-Instance plus Database-Catalog |
| `development_cluster` | Definition und Nutzung eines All-Purpose-Clusters |
| `metric_view` | Unity-Catalog Metric View, abfragbar über die `MEASURE()`-SQL-Funktion |
| `pipeline_with_schema` | Pipeline mit Schema-Verwaltung |

**Fortgeschrittene Muster:**

| Beispiel | Beschreibung |
|---|---|
| `private_wheel_packages` | private Paketverteilung aus Jobs heraus |
| `python_wheel_poetry` | Wheel-Build auf Basis von Poetry |
| `serverless_job` | Ausführung auf Serverless Compute |
| `share_files_across_bundles` | Datei-Sharing über Bundle-Grenzen hinweg |
| `spark_jar_task` | Ausführung eines Java-Artefakts |
| `target_includes` | Job-Konfigurationen über verschiedene Umgebungen hinweg organisieren, ohne Duplizierung |
| `vector_search_product_discovery` | semantische Produktsuche mit Databricks Vector Search |
| `write_from_job_to_volume` | Schreiboperation von einem Job in ein Unity-Catalog-Volume |

Keine Code-Beispiele in dieser Datei (Verweise auf externe Repository-Beispiele statt inline-Code).

---

## 46. Was sind User-Defined Functions (UDFs)?

**Einfach erklärt:** UDFs sind selbst geschriebene Funktionen, mit denen man Databricks um eigene Logik erweitert, die es mit den eingebauten Spark-Funktionen nicht (oder nur schwer) gibt. Sie eignen sich vor allem für Ad-hoc-Analysen, Datenbereinigung und kleine bis mittelgroße Datenmengen — für große, regelmäßig laufende ETL-/Streaming-Workloads sollten stattdessen eingebaute Apache-Spark-Funktionen verwendet werden, weil diese für verteilte Verarbeitung optimiert sind. Es gibt fünf Kategorien: Scalar UDFs (eine Zeile rein, ein Wert raus), Batch Scalar UDFs (verarbeiten Zeilen-Batches mit 1:1-Parität), Non-Scalar/Pandas-UDFs (flexibles Input/Output-Verhältnis), UDAFs (Aggregation mehrerer Zeilen zu einem Ergebnis) und UDTFs (geben eine ganze Ergebnistabelle zurück).

SQL-UDF für die Namenslänge:

```sql
-- SQL-UDF für die Namenslänge erstellen
CREATE OR REPLACE FUNCTION main.test.get_name_length(name STRING)
RETURNS INT
RETURN LENGTH(name);

-- Die UDF in einer SQL-Query verwenden
SELECT name, main.test.get_name_length(name) AS name_length
FROM your_table;
```

Äquivalente Implementierung in PySpark:

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType

@udf(returnType=IntegerType())
def get_name_length(name):
  return len(name)

df = df.withColumn("name_length", get_name_length(df.name))

# Ergebnis anzeigen
display(df)
```

Batch-Unity-Catalog-Python-UDF für BMI (Batch Scalar UDF, verarbeitet Zeilen-Batches):

```sql
CREATE OR REPLACE FUNCTION main.test.calculate_bmi_pandas(weight_kg DOUBLE, height_m DOUBLE)
RETURNS DOUBLE
LANGUAGE PYTHON
PARAMETER STYLE PANDAS
HANDLER 'handler_function'
AS $$
import pandas as pd
from typing import Iterator, Tuple

def handler_function(batch_iter: Iterator[Tuple[pd.Series, pd.Series]]) -> Iterator[pd.Series]:
  for weight_series, height_series in batch_iter:
    yield weight_series / (height_series ** 2)
$$;

select main.test.calculate_bmi_pandas(cast(70 as double), cast(1.8 as double));
```

Series-to-Series-Pandas-UDF (Non-Scalar UDF) für BMI:

```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

df = spark.createDataFrame([(70, 1.75), (80, 1.80), (60, 1.65)], ["Weight", "Height"])

@pandas_udf("double")
def calculate_bmi_pandas(weight: pd.Series, height: pd.Series) -> pd.Series:
    return weight / (height ** 2)

df.withColumn("BMI", calculate_bmi_pandas(df["Weight"], df["Height"])).display()
```

---

## 47. SQL- und Python-UDFs in Unity Catalog: Erstellen, Aufrufen und Berechtigungen

**Einfach erklärt:** In Unity Catalog registrierte SQL- und Python-UDFs sind "governed" Objekte — sie werden wie Tabellen über `catalog.schema.function_name` benannt, über GRANT/REVOKE gesteuert und sind katalogweit auffindbar und teilbar. Python-Code in solchen UDFs benötigt serverloses/Pro-SQL-Warehouse oder Runtime 13.3 LTS+. Eine session-scoped PySpark-UDF lässt sich leicht zu einer Unity-Catalog-UDF "upgraden", indem man dieselbe Logik in eine `CREATE FUNCTION`-Anweisung packt.

SQL-UDF:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.calculate_bmi(weight DOUBLE, height DOUBLE)
RETURNS DOUBLE
LANGUAGE SQL
RETURN
SELECT weight / (height * height);
```

Python-UDF:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.calculate_bmi(weight_kg DOUBLE, height_m DOUBLE)
RETURNS DOUBLE
LANGUAGE PYTHON
AS $$
return weight_kg / (height_m ** 2)
$$;
```

Aufruf:

```sql
SELECT person_id, my_catalog.my_schema.calculate_bmi(weight_kg, height_m) AS bmi
FROM person_data;
```

UDF mit Custom Dependencies (PyPI-Paket, Volume-Wheel, signierte URL):

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.mixed_process(data STRING)
RETURNS STRING
LANGUAGE PYTHON
ENVIRONMENT (
  dependencies = '["simplejson==3.19.3", "/Volumes/my_catalog/my_schema/my_volume/packages/custom_package-1.0.0.whl", "https://my-bucket.s3.amazonaws.com/packages/special_package-2.0.0.whl?Expires=2043167927&Signature=abcd"]',
  environment_version = '3'
)
AS $$
import simplejson as json
import custom_package
return json.dumps(custom_package.process(data))
$$;
```

| Feld | Beschreibung | Typ | Beispielnutzung |
|---|---|---|---|
| `dependencies` | Liste kommagetrennter Abhängigkeiten im pip-Requirements-Format | STRING | `dependencies = '["simplejson==3.19.3", "/Volumes/catalog/schema/volume/packages/my_package-1.0.0.whl"]'` |
| `environment_version` | Feste serverlose Environment-Version für die UDF, unabhängig von Runtime | STRING | `environment_version = '3'` |

Unity-Catalog-UDF aus PySpark aufrufen:

```python
from pyspark.sql.functions import expr

result = df.withColumn("bmi", expr("my_catalog.my_schema.calculate_bmi(weight_kg, height_m)"))
display(result)
```

Session-scoped UDF (Ausgangspunkt für ein Upgrade):

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

@udf(StringType())
def greet(name):
    return f"Hello, {name}!"

result = df.withColumn("greeting", greet("name"))
result.show()
```

Äquivalente Unity-Catalog-UDF nach dem Upgrade:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.greet(name STRING)
RETURNS STRING
LANGUAGE PYTHON
AS $$
return f"Hello, {name}!"
$$
```

Berechtigungen über SQL vergeben/entziehen:

```sql
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.calculate_bmi TO `user@example.com`;
```

```sql
REVOKE EXECUTE ON FUNCTION my_catalog.my_schema.calculate_bmi FROM `user@example.com`;
```

Strict Isolation (eigene, vollständig isolierte Sandbox statt geteilter Isolation Environment) — Beispiel: Python-Code sicher ausführen:

```sql
CREATE OR REPLACE TEMPORARY FUNCTION run_python_snippet(python_code STRING)
RETURNS STRING
LANGUAGE PYTHON
STRICT ISOLATION
AS $$
import sys
from io import StringIO

# Capture standard output and error streams
captured_output = StringIO()
captured_errors = StringIO()
sys.stdout = captured_output
sys.stderr = captured_errors

try:
    # Execute the user-provided Python code in an empty namespace
    exec(python_code, {})
except SyntaxError:
    # Retry with escaped characters decoded (for cases like "\n")
    def decode_code(raw_code):
        return raw_code.encode('utf-8').decode('unicode_escape')
    python_code = decode_code(python_code)
    exec(python_code, {})

# Return everything printed to stdout and stderr
return captured_output.getvalue() + captured_errors.getvalue()
$$
```

UDF für den Zugriff auf eine externe API:

```sql
CREATE FUNCTION my_catalog.my_schema.get_food_calories(food_name STRING)
RETURNS DOUBLE
LANGUAGE PYTHON
AS $$
import requests

api_url = f"https://example-food-api.com/nutrition?food={food_name}"
response = requests.get(api_url)

if response.status_code == 200:
   data = response.json()
   # Assume the API returns a JSON object with a 'calories' field
   calories = data.get('calories', 0)
   return calories
else:
   return None  # API request failed

$$;
```

UDF für Sicherheit/Compliance — E-Mail maskieren:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.mask_email(email STRING)
RETURNS STRING
LANGUAGE PYTHON
DETERMINISTIC
AS $$
parts = email.split('@', 1)
if len(parts) == 2:
  username, domain = parts
else:
  return None
masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
return f"{masked_username}@{domain}"
$$
```

```sql
-- Zuerst die View anlegen
CREATE OR REPLACE VIEW my_catalog.my_schema.masked_customer_view AS
SELECT
  id,
  name,
  my_catalog.my_schema.mask_email(email) AS masked_email
FROM my_catalog.my_schema.customer_data;

-- Jetzt lässt sich die View abfragen
SELECT * FROM my_catalog.my_schema.masked_customer_view;
```

```text
+---+------------+------------------------+------------------------+
| id|        name|                   email|           masked_email |
+---+------------+------------------------+------------------------+
|  1|    John Doe|   john.doe@example.com |  j*******e@example.com |
|  2| Alice Smith|alice.smith@company.com |a**********h@company.com|
|  3|   Bob Jones|    bob.jones@email.org |   b********s@email.org |
+---+------------+------------------------+------------------------+
```

Best Practice: Docstring mit Version, Changelog, Zweck und Beispiel:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.calculate_bmi(weight_kg DOUBLE, height_m DOUBLE)
RETURNS DOUBLE
COMMENT "Calculates Body Mass Index (BMI) from weight and height."
LANGUAGE PYTHON
DETERMINISTIC
AS $$
 """
Parameters:
calculate_bmi (version 1.2):
- weight_kg (float): Weight of the individual in kilograms.
- height_m (float): Height of the individual in meters.

Returns:
- float: The calculated BMI.

Example Usage:

SELECT calculate_bmi(weight, height) AS bmi FROM person_data;

Change Log:
- 1.0: Initial version.
- 1.1: Improved error handling for zero or negative height values.
- 1.2: Optimized calculation for performance.

 Note: BMI is calculated as weight in kilograms divided by the square of height in meters.
 """
if height_m <= 0:
 return None  # Avoid division by zero and ensure height is positive
return weight_kg / (height_m ** 2)
$$;
```

Zeitzonenverhalten bei Timestamp-Inputs (Verhaltensänderung ab Databricks Runtime 18.0: `tzinfo` fehlt nun):

```sql
CREATE FUNCTION timezone_udf(date TIMESTAMP)
RETURNS STRING
LANGUAGE PYTHON
AS $$
return f"{type(date)} {date} {date.tzinfo}"
$$;

SELECT timezone_udf(TIMESTAMP '2024-10-23 10:30:00');
```

Ausgabe vor Runtime 18.0:

```text
<class 'datetime.datetime'> 2024-10-23 10:30:00+00:00 Etc/UTC
```

Ausgabe ab Runtime 18.0:

```text
<class 'datetime.datetime'> 2024-10-23 10:30:00+00:00 None
```

Zeitzone bei Bedarf explizit wiederherstellen:

```python
from datetime import timezone

date = date.replace(tzinfo=timezone.utc)
```

---

## 48. Scala- und Java-UDFs in Unity Catalog: JAR bauen, registrieren, testen

**Einfach erklärt:** Scala- und Java-UDFs in Unity Catalog sind governed, wiederverwendbare Funktionen, die als kompiliertes Fat-JAR in ein Unity-Catalog-Volume hochgeladen und dann per `CREATE FUNCTION ... LANGUAGE SCALA/JAVA` registriert werden. Sie laufen in einer isolierten Sandbox ohne Zugriff auf Spark-APIs, unterstützen nur skalare Rückgabewerte (keine UDAFs/UDTFs) und benötigen Scala 2.13.16 bzw. JDK 17. Für vier Stellen (einfaches Scala-Beispiel, Scala-Beispiel mit Drittanbieter-Abhängigkeit, Scala-Caching-Beispiel, Scala-ScalaTest-Beispiel) liegt kein Scala-Code-Beispiel vor — nur die jeweiligen Java-Äquivalente.

Umgebung einrichten (lokal), Scala (sbt):

```bash
brew install openjdk@17
brew install sbt
```

```bash
java -version   # Should show Java 17
sbt --version   # Should show sbt version
```

Java (Maven):

```bash
brew install openjdk@17
brew install maven
```

```bash
java -version   # Should show Java 17
mvn --version   # Should show Maven version
```

Projekt anlegen, Scala:

```bash
sbt new scala/scala-seed.g8
```

Java (Maven):

```bash
mvn archetype:generate \
  -DgroupId=com.example \
  -DartifactId=my-udf \
  -DarchetypeArtifactId=maven-archetype-quickstart \
  -DinteractiveMode=false
```

```xml
<properties>
  <maven.compiler.source>17</maven.compiler.source>
  <maven.compiler.target>17</maven.compiler.target>
  <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>
```

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-shade-plugin</artifactId>
            <version>3.5.0</version>
            <executions>
                <execution>
                    <phase>package</phase>
                    <goals>
                        <goal>shade</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

Einfaches Beispiel, Scala: **[im Original leer/kein Code vorhanden]**

Komplexeres Beispiel mit Drittanbieter-Abhängigkeit (Scala): **[im Original leer/kein Code vorhanden]**

Einfaches Beispiel, Java:

```java
package com.example;

public class MyUDF {
    public static int addOne(int x) {
        return x + 1;
    }
}
```

Komplexeres Beispiel mit Drittanbieter-Abhängigkeit (Java):

```xml
<dependencies>
    <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-lang3</artifactId>
        <version>3.12.0</version>
    </dependency>
</dependencies>
```

```java
package com.example;

import org.apache.commons.lang3.StringUtils;
import java.util.Map;
import java.util.HashMap;

public class CurrencyUDF {
    private static final Map<String, Double> rates = new HashMap<>();

    static {
        rates.put("USD", 1.0);
        rates.put("EUR", 1.1);
        rates.put("GBP", 1.3);
        rates.put("JPY", 0.007);
    }

    public static double convertToUSD(double price, String currency) {
        if (currency == null) {
            throw new IllegalArgumentException("Currency must not be null");
        }

        String normalizedCurrency = StringUtils.upperCase(currency);

        if (!rates.containsKey(normalizedCurrency)) {
            throw new IllegalArgumentException("Unsupported currency: " + currency);
        }

        return price * rates.get(normalizedCurrency);
    }
}
```

Das Fat-JAR bauen:

```bash
sbt clean assembly
```

```bash
mvn clean package
```

Volume für JARs anlegen und Berechtigung vergeben:

```sql
CREATE VOLUME IF NOT EXISTS my_catalog.my_schema.udf_jars
COMMENT 'Storage for UDF JAR files';
```

```sql
GRANT READ VOLUME ON VOLUME my_catalog.my_schema.udf_jars TO `user@example.com`;
```

Alternative: JAR direkt aus einem Python-Notebook bauen (Java-Handler ohne externe Build-Toolchain):

```python
import os
import subprocess
import shutil

build_dir = "/tmp/udf_build"
package_dir = f"{build_dir}/src/com/databricks/udf"
classes_dir = f"{build_dir}/classes"
os.makedirs(package_dir, exist_ok=True)
os.makedirs(classes_dir, exist_ok=True)

# The UDF handler: a public static method on a plain Java class.
# The doubled backslashes produce a single backslash in the Java source (\\s+).
udf_code = """package com.databricks.udf;
public class StringCleanUDF {
    public static String clean(String input) {
        if (input == null) return null;
        return input.trim().replaceAll("\\\\s+", " ").toLowerCase();
    }
}
"""
with open(f"{package_dir}/StringCleanUDF.java", "w") as f:
    f.write(udf_code)

# Compile with JDK 17 to match Environment Version 4.
subprocess.run(
    ["javac", "--release", "17", "-d", classes_dir, f"{package_dir}/StringCleanUDF.java"],
    check=True,
)

# Package the compiled class into a JAR.
jar_path = f"{build_dir}/string_clean_udf.jar"
subprocess.run(["jar", "cf", jar_path, "-C", classes_dir, "."], check=True)

# Copy the JAR to a Unity Catalog volume.
volume_path = "/Volumes/my_catalog/my_schema/udf_jars/string_clean_udf.jar"
os.makedirs(os.path.dirname(volume_path), exist_ok=True)
shutil.copy2(jar_path, volume_path)

print(f"JAR uploaded to: {volume_path}")
```

Registrierung in Unity Catalog, Scala:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.add_one(x INT)
RETURNS INT
LANGUAGE SCALA
DETERMINISTIC
ENVIRONMENT (
  java_dependencies = '["/Volumes/my_catalog/my_schema/udf_jars/my-udf-assembly-0.1.0-SNAPSHOT.jar"]',
  environment_version = '4'
)
HANDLER 'com.example.MyUDF.addOne';
```

Java:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.add_one(x INT)
RETURNS INT
LANGUAGE JAVA
DETERMINISTIC
ENVIRONMENT (
  java_dependencies = '["/Volumes/my_catalog/my_schema/udf_jars/my-udf-1.0-SNAPSHOT.jar"]',
  environment_version = '4'
)
HANDLER 'com.example.MyUDF.addOne';
```

UDF in SQL und Notebooks aufrufen:

```sql
-- Simple select
SELECT my_catalog.my_schema.add_one(5) AS result;

-- With table data
SELECT
  id,
  price,
  currency,
  my_catalog.my_schema.convert_to_usd(price, currency) AS price_usd
FROM my_catalog.my_schema.transactions;

-- Filtering
SELECT *
FROM my_catalog.my_schema.products
WHERE my_catalog.my_schema.convert_to_usd(price, currency) > 100;

-- Aggregation
SELECT
  category,
  SUM(my_catalog.my_schema.convert_to_usd(price, currency)) AS total_usd
FROM my_catalog.my_schema.sales
GROUP BY category;
```

Berechtigungen über SQL erteilen/entziehen:

```sql
-- Grant to a specific user
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.add_one TO `user@example.com`;

-- Grant to a group
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.add_one TO `data-engineers`;
```

```sql
-- Revoke from specific user
REVOKE EXECUTE ON FUNCTION my_catalog.my_schema.add_one FROM `user@example.com`;

-- Revoke from a group
REVOKE EXECUTE ON FUNCTION my_catalog.my_schema.add_one FROM `data-engineers`;
```

UDFs über System Tables auffinden:

```sql
SELECT
  routine_catalog,
  routine_schema,
  routine_name,
  routine_definition,
  created
FROM system.information_schema.routines
WHERE routine_catalog = 'my_catalog'
  AND routine_schema = 'my_schema';
```

Teure Berechnungen cachen, Scala: **[im Original leer/kein Code vorhanden]**

Java:

```java
package example;

import java.util.Map;
import java.util.HashMap;

public class CachedUDF {
    // Computed once and cached
    private static Map<String, Double> expensiveData;

    static {
        // Load data from somewhere expensive
        expensiveData = new HashMap<>();
        expensiveData.put("key1", 1.0);
        expensiveData.put("key2", 2.0);
    }

    public static double lookup(String key) {
        return expensiveData.getOrDefault(key, 0.0);
    }
}
```

UDFs lokal testen, Scala (ScalaTest): **[im Original leer/kein Code vorhanden]**

```bash
sbt test
```

Java (JUnit 5):

```java
package com.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class MyUDFTest {
    @Test
    public void testAddOne() {
        assertEquals(6, MyUDF.addOne(5));
    }

    @Test
    public void testAddOneWithNegativeNumbers() {
        assertEquals(0, MyUDF.addOne(-1));
    }
}
```

```xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.0</version>
    <scope>test</scope>
</dependency>
```

```bash
mvn test
```

---

## 49. Batch Python UDFs in Unity Catalog (`PARAMETER STYLE PANDAS`)

**Einfach erklärt:** Batch-Unity-Catalog-Python-UDFs verarbeiten Daten nicht zeilenweise, sondern in Batches über Pandas-Iteratoren, wobei die Zeilenanzahl von Input und Output immer gleich bleiben muss (1:1-Parität). Das reduziert Overhead und erlaubt Zustand zwischen Batches. Sie benötigen Databricks Runtime 16.3+, eine Handler-Funktion (`HANDLER`) und können über `CREDENTIALS` sicher auf externe Dienste wie AWS Lambda zugreifen.

Grundlegendes Beispiel (BMI):

```sql
%sql
CREATE OR REPLACE TEMPORARY FUNCTION calculate_bmi_pandas(weight_kg DOUBLE, height_m DOUBLE)
RETURNS DOUBLE
LANGUAGE PYTHON
DETERMINISTIC
PARAMETER STYLE PANDAS
HANDLER 'handler_function'
AS $$
import pandas as pd
from typing import Iterator, Tuple

def handler_function(batch_iter: Iterator[Tuple[pd.Series, pd.Series]]) -> Iterator[pd.Series]:
  for weight_series, height_series in batch_iter:
    yield weight_series / (height_series ** 2)
$$;
```

```sql
SELECT person_id, calculate_bmi_pandas(weight_kg, height_m) AS bmi
FROM (
  SELECT 1 AS person_id, CAST(70.0 AS DOUBLE) AS weight_kg, CAST(1.75 AS DOUBLE) AS height_m UNION ALL
  SELECT 2 AS person_id, CAST(80.0 AS DOUBLE) AS weight_kg, CAST(1.80 AS DOUBLE) AS height_m
);
```

Ein Parameter:

```sql
%sql
CREATE OR REPLACE TEMPORARY FUNCTION one_parameter_udf(value INT)
RETURNS STRING
LANGUAGE PYTHON
DETERMINISTIC
PARAMETER STYLE PANDAS
HANDLER 'handler_func'
AS $$
import pandas as pd
from typing import Iterator
def handler_func(batch_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
  for value_batch in batch_iter:
    d = {"min": value_batch.min(), "max": value_batch.max()}
    yield pd.Series([str(d)] * len(value_batch))
$$;
SELECT one_parameter_udf(id), count(*) from range(0, 100000, 3, 8) GROUP BY ALL;
```

Zwei Parameter:

```sql
%sql
CREATE OR REPLACE TEMPORARY FUNCTION two_parameter_udf(p1 INT, p2 INT)
RETURNS INT
LANGUAGE PYTHON
DETERMINISTIC
PARAMETER STYLE PANDAS
HANDLER 'handler_function'
AS $$
import pandas as pd
from typing import Iterator, Tuple

def handler_function(batch_iter: Iterator[Tuple[pd.Series, pd.Series]]) -> Iterator[pd.Series]:
  for p1, p2 in batch_iter: # same order as arguments above
    yield p1 + p2
$$;
SELECT two_parameter_udf(id , id + 1) from range(0, 100000, 3, 8);
```

Performance: teure Operationen außerhalb der Handler-Funktion (Modulebene, nur einmal pro Isolation Environment ausgeführt):

```sql
%sql
CREATE OR REPLACE TEMPORARY FUNCTION expensive_computation_udf(value INT)
RETURNS INT
LANGUAGE PYTHON
DETERMINISTIC
PARAMETER STYLE PANDAS
HANDLER 'handler_func'
AS $$
def compute_value():
  # expensive computation...
  return 1

expensive_value = compute_value()
def handler_func(batch_iter):
  for batch in batch_iter:
    yield batch * expensive_value
$$;
SELECT expensive_computation_udf(id), count(*) from range(0, 100000, 3, 8) GROUP BY ALL
```

Strict Isolation (z. B. bei `eval()`/`exec()` oder Umgebungsvariablen-Manipulation):

```sql
CREATE OR REPLACE TEMPORARY FUNCTION eval_string(input STRING)
RETURNS STRING
LANGUAGE PYTHON
PARAMETER STYLE PANDAS
HANDLER 'handler_func'
STRICT ISOLATION
AS $$
import pandas as pd
from typing import Iterator

def handler_func(batch_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
  for code_series in batch_iter:
    def eval_func(code):
      try:
        return str(eval(code))
      except Exception as e:
        return f"Error: {e}"
    yield code_series.apply(eval_func)
$$;
```

Service Credentials mit Alias:

```sql
CREATE OR REPLACE TEMPORARY FUNCTION example_udf(data STRING)
RETURNS STRING
LANGUAGE PYTHON
PARAMETER STYLE PANDAS
HANDLER 'handler_function'
CREDENTIALS (
  `credential-name` DEFAULT,
  `complicated-credential-name` AS short_name,
  `simple-cred`,
  cred_no_quotes
)
AS $$
# Python code here
$$;
```

Default Credentials und Aliase nutzen:

```python
from databricks.service_credentials import getServiceCredentialsProvider
import boto3

# Assuming credential definition: CREDENTIALS(`aws-cred` AS testcred)
boto3_session = boto3.Session(botocore_session=getServiceCredentialsProvider('testcred'))
s3 = boto3_session.client('s3')
```

Service-Credential-Beispiel — AWS-Lambda-Funktion aufrufen:

```sql
%sql
CREATE OR REPLACE FUNCTION main.test.call_lambda_func(data STRING, debug BOOLEAN) RETURNS STRING LANGUAGE PYTHON
PARAMETER STYLE PANDAS
HANDLER 'batchhandler'
CREDENTIALS (
  `batch-udf-service-creds-example-cred` DEFAULT
)
AS $$
import boto3
import json
import pandas as pd
import base64
from pyspark.taskcontext import TaskContext


def batchhandler(it):
  # Automatically picks up DEFAULT credential:
  session = boto3.Session()

  client = session.client("lambda", region_name="us-west-2")

  # Propagate TaskContext information to lambda context:
  user_ctx = {"custom": {"user": TaskContext.get().getLocalProperty("user")}}

  for vals, is_debug in it:
    payload = json.dumps({"values": vals.to_list(), "is_debug": bool(is_debug[0])})

    res = client.invoke(
      FunctionName="HashValuesFunction",
      InvocationType="RequestResponse",
      ClientContext=base64.b64encode(json.dumps(user_ctx).encode("utf-8")).decode(
        "utf-8"
      ),
      Payload=payload,
    )

    response_payload = json.loads(res["Payload"].read().decode("utf-8"))
    if "errorMessage" in response_payload:
      raise Exception(str(response_payload))

    yield pd.Series(response_payload["values"])
$$;
```

```sql
SELECT main.test.call_lambda_func(data, false)
FROM VALUES
('abc'),
('def')
AS t(data)
```

---

## 50. Python UDTFs (User-Defined Table Functions) in Unity Catalog

**Einfach erklärt:** Eine UDTF gibt statt eines einzelnen Werts eine ganze Ergebnistabelle zurück — nützlich, um Arrays in mehrere Zeilen aufzuteilen, externe APIs anzubinden, Daten anzureichern oder zustandsbehaftete Verarbeitung über mehrere Zeilen hinweg zu implementieren. Die zentrale Methode `eval()` läuft einmal pro Eingabezeile, die optionale Methode `terminate()` einmal am Ende jeder Partition für finale/aggregierte Ergebnisse. Polymorphe UDTFs berechnen ihr Ausgabeschema dynamisch über eine `analyze()`-Methode.

Basis-UDTF (Quadratzahlen berechnen):

```sql
CREATE OR REPLACE FUNCTION square_numbers(start INT, end INT)
RETURNS TABLE (num INT, squared INT)
LANGUAGE PYTHON
HANDLER 'SquareNumbers'
DETERMINISTIC
AS $$
class SquareNumbers:
    """
    Basic UDTF that computes a sequence of integers
    and includes the square of each number in the range.
    """
    def eval(self, start: int, end: int):
        for num in range(start, end + 1):
            yield (num, num * num)
$$;

SELECT * FROM square_numbers(1, 5);
```

```text
+-----+---------+
| num | squared |
+-----+---------+
| 1   | 1       |
| 2   | 4       |
| 3   | 9       |
| 4   | 16      |
| 5   | 25      |
+-----+---------+
```

Polymorphe UDTF mit dynamischem Ausgabeschema (`analyze`):

```sql
CREATE OR REPLACE FUNCTION extract_fields(json_str STRING, fields STRING)
RETURNS TABLE
LANGUAGE PYTHON
HANDLER 'ExtractFields'
AS $$
class ExtractFields:
    @staticmethod
    def analyze(json_str, fields):

        # Build the output schema from the requested field names
        from pyspark.sql.types import StructType, StructField, StringType
        from pyspark.sql.udtf import AnalyzeResult
        col_names = [f.strip() for f in fields.value.split(",")]
        return AnalyzeResult(
            StructType([StructField(name, StringType()) for name in col_names])
        )

    def eval(self, json_str: str, fields: str):
        # Parse the JSON and yield only the requested fields
        import json
        data = json.loads(json_str)
        col_names = [f.strip() for f in fields.split(",")]
        yield tuple(data.get(name) for name in col_names)
$$;

-- Extract the name and city
SELECT * FROM extract_fields(
  '{"name": "Alice", "age": 30, "city": "Seattle"}',
  'name, city'
);
```

```text
+-------+---------+
| name  | city    |
+-------+---------+
| Alice | Seattle |
+-------+---------+
```

| `AnalyzeArgument`-Feld | Beschreibung |
|---|---|
| `dataType` | Der Typ des Eingabearguments als `DataType`. Für Table-Argumente ein `StructType`. |
| `value` | Der Wert des Eingabearguments als `Optional[Any]`. `None` für Table-Argumente/nicht-konstante Ausdrücke. |
| `isTable` | Ob das Argument ein Table-Argument ist. |
| `isConstantExpression` | Ob das Argument ein konstant-auswertbarer Ausdruck ist. |

| `AnalyzeResult`-Feld | Beschreibung |
|---|---|
| `schema` | Schema der Ergebnistabelle als `StructType`. |
| `withSinglePartition` | Wenn `True`, gehen alle Eingabezeilen an dieselbe UDTF-Instanz. |
| `partitionBy` | Partitionierung der Eingabezeilen anhand der angegebenen Ausdrücke. |
| `orderBy` | Reihenfolge der Zeilen innerhalb jeder Partition. |
| `select` | Welche Spalten des Eingabe-`TABLE`-Arguments die UDTF erhält. |

Zustand von `analyze` an `eval` weitergeben:

```sql
CREATE OR REPLACE FUNCTION tag_language(t TABLE, lang_code STRING)
RETURNS TABLE
LANGUAGE PYTHON
HANDLER 'TagLanguage'
AS $$
class TagLanguage:
    @staticmethod
    def analyze(t, lang_code):
        from dataclasses import dataclass
        from pyspark.sql.types import StructType, StructField, StringType
        from pyspark.sql.udtf import AnalyzeResult

        @dataclass
        class LangResult(AnalyzeResult):
            language: str = ""

        # Resolve the language code to a full name once during planning
        languages = {"en": "English", "es": "Spanish", "fr": "French", "de": "German"}
        return LangResult(
            schema=StructType([
                StructField("text", StringType()),
                StructField("language", StringType())
            ]),
            language=languages.get(lang_code.value, "Unknown")
        )

    def __init__(self, result):
        self._language = result.language

    def eval(self, row, lang_code: str):
        # Tag each row with the pre-resolved language name
        yield (row['text'], self._language)
$$;

SELECT * FROM tag_language(
  TABLE(VALUES ('Hola mundo'), ('Buenos días') t(text)),
  'es'
);
```

```text
+-------------+----------+
| text        | language |
+-------------+----------+
| Hola mundo  | Spanish  |
| Buenos días | Spanish  |
+-------------+----------+
```

Strict Isolation (Beispiel mit Umgebungsvariable):

```sql
CREATE OR REPLACE TEMPORARY FUNCTION multiply_numbers(factor STRING)
RETURNS TABLE (original INT, scaled INT)
LANGUAGE PYTHON
STRICT ISOLATION
HANDLER 'Multiplier'
AS $$
import os

class Multiplier:
    def eval(self, factor: str):
        # Save the factor as an environment variable
        os.environ["FACTOR"] = factor

        # Read it back and convert it to a number
        scale = int(os.getenv("FACTOR", "1"))

        # Multiply 0 through 4 by the factor
        for i in range(5):
            yield (i, i * scale)
$$;

SELECT * FROM multiply_numbers("3");
```

Praxisbeispiel: `explode` neu implementieren:

```sql
CREATE OR REPLACE FUNCTION my_explode(arr ARRAY<STRING>)
RETURNS TABLE (element STRING)
LANGUAGE PYTHON
HANDLER 'MyExplode'
DETERMINISTIC
AS $$
class MyExplode:
    def eval(self, arr):
        if arr is None:
            return
        for element in arr:
            yield (element,)
$$;
```

```sql
SELECT element FROM my_explode(array('apple', 'banana', 'cherry'));
```

```text
+---------+
| element |
+---------+
| apple   |
| banana  |
| cherry  |
+---------+
```

```sql
SELECT s.*, e.element
FROM my_items AS s,
LATERAL my_explode(s.items) AS e;
```

Praxisbeispiel: IP-Adress-Geolokalisierung über REST-API:

```sql
CREATE OR REPLACE FUNCTION ip_to_location(ip_address STRING)
RETURNS TABLE (city STRING, country STRING)
LANGUAGE PYTHON
HANDLER 'IPToLocationAPI'
AS $$
class IPToLocationAPI:
    def eval(self, ip_address):
        import requests
        api_url = f"https://api.ip-lookup.example.com/{ip_address}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            yield (data.get('city'), data.get('country'))
        except requests.exceptions.RequestException as e:
            # Return nothing if the API request fails
            return
$$;
```

```sql
SELECT
  l.timestamp,
  l.request_path,
  geo.city,
  geo.country
FROM web_logs AS l,
LATERAL ip_to_location(l.ip_address) AS geo;
```

Praxisbeispiel: IP-Adressen gegen CIDR-Netzblöcke matchen:

```sql
-- An example IP logs with both IPv4 and IPv6 addresses
CREATE OR REPLACE TEMPORARY VIEW ip_logs AS
VALUES
  ('log1', '192.168.1.100'),
  ('log2', '10.0.0.5'),
  ('log3', '172.16.0.10'),
  ('log4', '8.8.8.8'),
  ('log5', '2001:db8::1'),
  ('log6', '2001:db8:85a3::8a2e:370:7334'),
  ('log7', 'fe80::1'),
  ('log8', '::1'),
  ('log9', '2001:db8:1234:5678::1')
t(log_id, ip_address);
```

```sql
CREATE OR REPLACE TEMPORARY FUNCTION ip_cidr_matcher(t TABLE)
RETURNS TABLE(log_id STRING, ip_address STRING, network STRING, ip_version INT)
LANGUAGE PYTHON
HANDLER 'IpMatcher'
COMMENT 'Match IP addresses against a list of network CIDR blocks'
AS $$
class IpMatcher:
    def __init__(self):
        import ipaddress
        # Heavy initialization - load networks once per partition
        self.nets = []
        cidrs = ['192.168.0.0/16', '10.0.0.0/8', '172.16.0.0/12',
                 '2001:db8::/32', 'fe80::/10', '::1/128']
        for cidr in cidrs:
            self.nets.append(ipaddress.ip_network(cidr))

    def eval(self, row):
        import ipaddress
	    # Validate that required fields exist
        required_fields = ['log_id', 'ip_address']
        for field in required_fields:
            if field not in row:
                raise ValueError(f"Missing required field: {field}")
        try:
            ip = ipaddress.ip_address(row['ip_address'])
            for net in self.nets:
                if ip in net:
                    yield (row['log_id'], row['ip_address'], str(net), ip.version)
                    return
            yield (row['log_id'], row['ip_address'], None, ip.version)
        except ValueError:
            yield (row['log_id'], row['ip_address'], 'Invalid', None)
$$;
```

```sql
-- Process all IP addresses
SELECT
  *
FROM
  ip_cidr_matcher(t => TABLE(ip_logs))
ORDER BY
  log_id;
```

```text
+--------+-------------------------------+-----------------+-------------+
| log_id | ip_address                    | network         | ip_version  |
+--------+-------------------------------+-----------------+-------------+
| log1   | 192.168.1.100                 | 192.168.0.0/16  | 4           |
| log2   | 10.0.0.5                      | 10.0.0.0/8      | 4           |
| log3   | 172.16.0.10                   | 172.16.0.0/12   | 4           |
| log4   | 8.8.8.8                       | null            | 4           |
| log5   | 2001:db8::1                   | 2001:db8::/32   | 6           |
| log6   | 2001:db8:85a3::8a2e:370:7334  | 2001:db8::/32   | 6           |
| log7   | fe80::1                       | fe80::/10       | 6           |
| log8   | ::1                           | ::1/128         | 6           |
| log9   | 2001:db8:1234:5678::1         | 2001:db8::/32   | 6           |
+--------+-------------------------------+-----------------+-------------+
```

Praxisbeispiel: Batch-Bildbeschriftung über Databricks-Vision-Endpoints:

```sql
CREATE OR REPLACE TEMPORARY VIEW sample_images AS
VALUES
    ('https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg', 'scenery'),
    ('https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/1024px-Camponotus_flavomarginatus_ant.jpg', 'animals'),
    ('https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Cat_August_2010-4.jpg/1200px-Cat_August_2010-4.jpg', 'animals'),
    ('https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/M101_hires_STScI-PRC2006-10a.jpg/1024px-M101_hires_STScI-PRC2006-10a.jpg', 'scenery')
images(image_url, category);
```

```sql
CREATE OR REPLACE TEMPORARY FUNCTION batch_inference_image_caption(data TABLE, api_token STRING)
RETURNS TABLE (caption STRING)
LANGUAGE PYTHON
HANDLER 'BatchInferenceImageCaption'
COMMENT 'batch image captioning by sending groups of image URLs to a Databricks vision endpoint and returning concise captions for each image.'
AS $$
class BatchInferenceImageCaption:
    def __init__(self):
        self.batch_size = 3
        self.vision_endpoint = "databricks-claude-sonnet-4-5"
        self.workspace_url = "<workspace-url>"
        self.image_buffer = []
        self.results = []

    def eval(self, row, api_token):
        self.image_buffer.append((str(row[0]), api_token))
        if len(self.image_buffer) >= self.batch_size:
            self._process_batch()

    def terminate(self):
        if self.image_buffer:
            self._process_batch()
        for caption in self.results:
            yield (caption,)

    def _process_batch(self):
        batch_data = self.image_buffer.copy()
        self.image_buffer.clear()

        import base64
        import httpx
        import requests

        # API request timeout in seconds
        api_timeout = 60
        # Maximum tokens for vision model response
        max_response_tokens = 300
        # Temperature controls randomness (lower = more deterministic)
        model_temperature = 0.3

        # create a batch for the images
        batch_images = []
        api_token = batch_data[0][1] if batch_data else None

        for image_url, _ in batch_data:
            image_response = httpx.get(image_url, timeout=15)
            image_data = base64.standard_b64encode(image_response.content).decode("utf-8")
            batch_images.append(image_data)

        content_items = [{
            "type": "text",
            "text": "Provide brief captions for these images, one per line."
        }]
        for img_data in batch_images:
            content_items.append({
                "type": "image_url",
                "image_url": {
                    "url": "data:image/jpeg;base64," + img_data
                }
            })

        payload = {
            "messages": [{
                "role": "user",
                "content": content_items
            }],
            "max_tokens": max_response_tokens,
            "temperature": model_temperature
        }

        response = requests.post(
            self.workspace_url + "/serving-endpoints/" +
            self.vision_endpoint + "/invocations",
            headers={
                'Authorization': 'Bearer ' + api_token,
                'Content-Type': 'application/json'
            },
            json=payload,
            timeout=api_timeout
        )

        result = response.json()
        batch_response = result['choices'][0]['message']['content'].strip()

        lines = batch_response.split('\n')
        captions = [line.strip() for line in lines if line.strip()]

        while len(captions) < len(batch_data):
            captions.append(batch_response)

        self.results.extend(captions[:len(batch_data)])
$$;
```

```sql
SELECT
  caption
FROM
  batch_inference_image_caption(
    data => TABLE(sample_images),
    api_token => secret('your_secret_scope', 'api_token')
  )
```

```text
+---------------------------------------------------------------------------------------------------------------+
| caption                                                                                                       |
+---------------------------------------------------------------------------------------------------------------+
| Wooden boardwalk cutting through vibrant wetland grasses under blue skies                                     |
| Black ant in detailed macro photography standing on a textured surface                                        |
| Tabby cat lounging comfortably on a white ledge against a white wall                                          |
| Stunning spiral galaxy with bright central core and sweeping blue-white arms against the black void of space. |
+---------------------------------------------------------------------------------------------------------------+
```

Mit expliziter Partitionierung nach `category`:

```sql
SELECT
  *
FROM
  batch_inference_image_caption(
    TABLE(sample_images)
    PARTITION BY category ORDER BY (category),
    secret('your_secret_scope', 'api_token')
  )
```

```text
+------------------------------------------------------------------------------------------------------+
| caption                                                                                                |
+------------------------------------------------------------------------------------------------------+
| Black ant in detailed macro photography standing on a textured surface                               |
| Stunning spiral galaxy with bright center and sweeping blue-tinged arms against the black of space.  |
| Tabby cat lounging comfortably on white ledge against white wall                                     |
| Wooden boardwalk cutting through lush wetland grasses under blue skies                               |
+------------------------------------------------------------------------------------------------------+
```

Praxisbeispiel: ROC-Kurve und AUC-Berechnung (mit `terminate()`, scikit-learn, Fehlerbehandlung):

```sql
CREATE OR REPLACE TEMPORARY FUNCTION compute_roc_curve(t TABLE)
RETURNS TABLE (threshold DOUBLE, true_positive_rate DOUBLE, false_positive_rate DOUBLE, auc DOUBLE)
LANGUAGE PYTHON
HANDLER 'ROCCalculator'
COMMENT 'Compute ROC curve and AUC using scikit-learn'
AS $$
class ROCCalculator:
    def __init__(self):
        from sklearn import metrics
        self._roc_curve = metrics.roc_curve
        self._roc_auc_score = metrics.roc_auc_score

        self._true_labels = []
        self._predicted_scores = []

    def eval(self, row):
        if 'y_true' not in row or 'y_score' not in row:
            raise KeyError("Required columns 'y_true' and 'y_score' not found")

        true_label = row['y_true']
        predicted_score = row['y_score']

        label = float(true_label)
        self._true_labels.append(label)
        self._predicted_scores.append(float(predicted_score))

    def terminate(self):
        false_pos_rate, true_pos_rate, thresholds = self._roc_curve(
            self._true_labels,
            self._predicted_scores,
            drop_intermediate=False
        )

        auc_score = float(self._roc_auc_score(self._true_labels, self._predicted_scores))

        for threshold, tpr, fpr in zip(thresholds, true_pos_rate, false_pos_rate):
            yield float(threshold), float(tpr), float(fpr), auc_score
$$;
```

```sql
CREATE OR REPLACE TEMPORARY VIEW binary_classification_data AS
SELECT *
FROM VALUES
  ( 1, 1.0, 0.95, 'high_confidence_positive'),
  ( 2, 1.0, 0.87, 'high_confidence_positive'),
  ( 3, 1.0, 0.82, 'medium_confidence_positive'),
  ( 4, 0.0, 0.78, 'false_positive'),
  ( 5, 1.0, 0.71, 'medium_confidence_positive'),
  ( 6, 0.0, 0.65, 'false_positive'),
  ( 7, 0.0, 0.58, 'true_negative'),
  ( 8, 1.0, 0.52, 'low_confidence_positive'),
  ( 9, 0.0, 0.45, 'true_negative'),
  (10, 0.0, 0.38, 'true_negative'),
  (11, 1.0, 0.31, 'low_confidence_positive'),
  (12, 0.0, 0.15, 'true_negative'),
  (13, 0.0, 0.08, 'high_confidence_negative'),
  (14, 0.0, 0.03, 'high_confidence_negative')
AS data(sample_id, y_true, y_score, prediction_type);
```

```sql
SELECT
    threshold,
    true_positive_rate,
    false_positive_rate,
    auc
FROM compute_roc_curve(
  TABLE(
    SELECT y_true, y_score
    FROM binary_classification_data
    WHERE y_true IS NOT NULL AND y_score IS NOT NULL
    ORDER BY sample_id
  )
)
ORDER BY threshold DESC;
```

```text
+-----------+---------------------+----------------------+-------+
| threshold | true_positive_rate  | false_positive_rate  | auc   |
+-----------+---------------------+----------------------+-------+
| 1.95      | 0.0                 | 0.0                  | 0.786 |
| 0.95      | 0.167               | 0.0                  | 0.786 |
| 0.87      | 0.333               | 0.0                  | 0.786 |
| 0.82      | 0.5                 | 0.0                  | 0.786 |
| 0.78      | 0.5                 | 0.125                | 0.786 |
| 0.71      | 0.667               | 0.125                | 0.786 |
| 0.65      | 0.667               | 0.25                 | 0.786 |
| 0.58      | 0.667               | 0.375                | 0.786 |
| 0.52      | 0.833               | 0.375                | 0.786 |
| 0.45      | 0.833               | 0.5                  | 0.786 |
| 0.38      | 0.833               | 0.625                | 0.786 |
| 0.31      | 1.0                 | 0.625                | 0.786 |
| 0.15      | 1.0                 | 0.75                 | 0.786 |
| 0.08      | 1.0                 | 0.875                | 0.786 |
| 0.03      | 1.0                 | 1.0                  | 0.786 |
+-----------+---------------------+----------------------+-------+
```

Praxisbeispiel: Dynamische Spaltenprojektion aus einem Table-Argument:

```sql
CREATE OR REPLACE FUNCTION project_columns(t TABLE, columns STRING)
RETURNS TABLE
LANGUAGE PYTHON
HANDLER 'ProjectColumns'
AS $$
class ProjectColumns:
    @staticmethod
    def analyze(t, columns):
        from pyspark.sql.types import StructType
        from pyspark.sql.udtf import AnalyzeResult

        requested = [c.strip() for c in columns.value.split(",")]
        input_schema = t.dataType
        output_fields = []
        for field in input_schema.fields:
            if field.name in requested:
                output_fields.append(field)
        if not output_fields:
            raise ValueError(
                f"None of the requested columns {requested} "
                f"exist in the input table"
            )
        return AnalyzeResult(schema=StructType(output_fields))

    def eval(self, row, columns: str):
        requested = [c.strip() for c in columns.split(",")]
        yield tuple(row[col] for col in requested if col in row)
$$;
```

```sql
SELECT * FROM project_columns(
  TABLE(SELECT * FROM samples.nyctaxi.trips LIMIT 5),
  'pickup_zip, dropoff_zip, fare_amount'
);
```

---

## 51. Python Scalar UDFs (Session-scoped)

**Einfach erklärt:** Session-scoped Python-UDFs werden direkt über die PySpark-API in einer Notebook-/Job-Session registriert (`spark.udf.register` oder der `@udf`-Dekorator) — sie sind nicht in Unity Catalog governed, sondern nur an die aktuelle `SparkSession` gebunden. Sie lassen sich in Spark SQL, mit DataFrames, mit Variant-Typen und mit dem neuen (Beta) Datei-Typ `FileType` verwenden. Seit Databricks Runtime 13.3 LTS werden sie auf allen Access Modes unterstützt.

Funktion als UDF registrieren:

```python
def squared(s):
  return s * s
spark.udf.register("squaredWithPython", squared)
```

Mit explizitem Rückgabetyp:

```python
from pyspark.sql.types import LongType
def squared_typed(s):
  return s * s
spark.udf.register("squaredWithPython", squared_typed, LongType())
```

In Spark SQL aufrufen:

```python
spark.range(1, 20).createOrReplaceTempView("test")
```

```sql
%sql select id, squaredWithPython(id) as id_squared from test
```

Mit DataFrames verwenden:

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import LongType
squared_udf = udf(squared, LongType())
df = spark.table("test")
display(df.select("id", squared_udf("id").alias("id_squared")))
```

Als Dekorator:

```python
from pyspark.sql.functions import udf

@udf("long")
def squared_udf(s):
  return s * s
df = spark.table("test")
display(df.select("id", squared_udf("id").alias("id_squared")))
```

Variant-Typen mit UDFs — Rückgabe eines `Variant`:

```python
from pyspark.sql.types import VariantType

# Return Variant
@udf(returnType = VariantType())
def toVariant(jsonString):
  return VariantVal.parseJson(jsonString)

spark.range(1).select(lit('{"a" : 1}').alias("json")).select(toVariant(col("json"))).display()
```

```text
+---------------+
|toVariant(json)|
+---------------+
|        {"a":1}|
+---------------+
```

Rückgabe eines `Struct<Variant>`:

```python
# Return Struct<Variant>
@udf(returnType = StructType([StructField("v", VariantType(), True)]))
def toStructVariant(jsonString):
  return {"v": VariantVal.parseJson(jsonString)}

spark.range(1).select(lit('{"a" : 1}').alias("json")).select(toStructVariant(col("json"))).display()
```

```text
+---------------------+
|toStructVariant(json)|
+---------------------+
|        {"v":{"a":1}}|
+---------------------+
```

Rückgabe eines `Array<Variant>`:

```python
# Return Array<Variant>
@udf(returnType = ArrayType(VariantType()))
def toArrayVariant(jsonString):
  return [VariantVal.parseJson(jsonString)]

spark.range(1).select(lit('{"a" : 1}').alias("json")).select(toArrayVariant(col("json"))).display()
```

```text
+--------------------+
|toArrayVariant(json)|
+--------------------+
|           [{"a":1}]|
+--------------------+
```

Rückgabe eines `Map<String, Variant>`:

```python
# Return Map<String, Variant>
@udf(returnType = MapType(StringType(), VariantType(), True))
def toArrayVariant(jsonString):
  return {"v1": VariantVal.parseJson(jsonString), "v2": VariantVal.parseJson("[" + jsonString + "]")}

spark.range(1).select(lit('{"a" : 1}').alias("json")).select(toArrayVariant(col("json"))).display()
```

```text
+-----------------------------+
|         toArrayVariant(json)|
+-----------------------------+
|{"v2":[{"a":1}],"v1":{"a":1}}|
+-----------------------------+
```

Auswertungsreihenfolge und Null-Prüfung — Spark SQL garantiert keine feste Auswertungsreihenfolge von Subexpressions:

```python
spark.udf.register("strlen", lambda s: len(s), "int")
spark.sql("select s from test1 where s is not null and strlen(s) > 1") # no guarantee
```

Zwei Lösungswege (null-aware UDF, `IF`/`CASE WHEN`):

```python
spark.udf.register("strlen_nullsafe", lambda s: len(s) if not s is None else -1, "int")
spark.sql("select s from test1 where s is not null and strlen_nullsafe(s) > 1") // ok
spark.sql("select s from test1 where if(s is not null, strlen(s), null) > 1")   // ok
```

Service Credentials in Scalar Python UDFs:

```python
@udf
def use_service_credential():
    from databricks.service_credentials import getServiceCredentialsProvider
    import boto3

    # Assuming there is a service credential named 'testcred' set up in Unity Catalog
    boto3_session = boto3.Session(botocore_session=getServiceCredentialsProvider('testcred'))
    # Use the S3 session to perform operations
```

Default Credentials:

```python
@udf
def use_service_credential():
    from databricks.service_credentials import getServiceCredentialsProvider
    import boto3

    # The default service credential for the compute is automatically used
    boto3_session = boto3.Session()
    # Use the S3 client to perform operations
```

Service-Credential-Beispiel — AWS-Lambda-Funktion aufrufen:

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

@udf(StringType())
def call_lambda_udf(input_str):
    import boto3
    import json
    import base64
    from databricks.service_credentials import getServiceCredentialsProvider
    from pyspark.taskcontext import TaskContext

    # Create a session using the default Unity Catalog service credential
    session = boto3.Session()
    client = session.client("lambda", region_name="us-west-2")

    # Optionally attach Spark TaskContext metadata to the Lambda request
    user_ctx = {"custom": {"user": TaskContext.get().getLocalProperty("user")}}

    # Build the Lambda payload
    payload = json.dumps({
        "values": [input_str],
        "is_debug": False
    })

    # Encode context for Lambda's client context
    encoded_ctx = base64.b64encode(json.dumps(user_ctx).encode("utf-8")).decode("utf-8")

    # Call the Lambda function
    response = client.invoke(
        FunctionName="HashValuesFunction",
        InvocationType="RequestResponse",
        ClientContext=encoded_ctx,
        Payload=payload,
    )

    response_payload = json.loads(response["Payload"].read().decode("utf-8"))

    if "errorMessage" in response_payload:
        raise Exception(response_payload["errorMessage"])

    return response_payload["values"][0]
```

---

## 52. Pandas UDFs (vektorisierte UDFs mit Apache Arrow)

**Einfach erklärt:** Pandas-UDFs nutzen Apache Arrow für den Datentransfer und pandas für die Verarbeitung — dadurch sind sie deutlich schneller als klassische zeilenweise Python-UDFs, weil sie ganze Batches statt einzelner Zeilen verarbeiten. Es gibt vier Muster: Series-to-Series, Iterator-of-Series-to-Iterator-of-Series, Iterator-of-multiple-Series-to-Iterator-of-Series und Series-to-scalar (für Aggregationen/Fenster). Die Batch-Größe lässt sich über `spark.sql.execution.arrow.maxRecordsPerBatch` steuern (Standard 10.000).

Series to Series UDF:

```python
import pandas as pd
from pyspark.sql.functions import col, pandas_udf
from pyspark.sql.types import LongType

# Declare the function and create the UDF
def multiply_func(a: pd.Series, b: pd.Series) -> pd.Series:
    return a * b

multiply = pandas_udf(multiply_func, returnType=LongType())

# The function for a pandas_udf should be able to execute with local pandas data
x = pd.Series([1, 2, 3])
print(multiply_func(x, x))
# 0    1
# 1    4
# 2    9
# dtype: int64

# Create a Spark DataFrame, 'spark' is an existing SparkSession
df = spark.createDataFrame(pd.DataFrame(x, columns=["x"]))

# Execute function as a Spark vectorized UDF
df.select(multiply(col("x"), col("x"))).show()
# +-------------------+
# |multiply_func(x, x)|
# +-------------------+
# |                  1|
# |                  4|
# |                  9|
# +-------------------+
```

Iterator of Series to Iterator of Series UDF:

```python
import pandas as pd
from typing import Iterator
from pyspark.sql.functions import col, pandas_udf, struct

pdf = pd.DataFrame([1, 2, 3], columns=["x"])
df = spark.createDataFrame(pdf)

# When the UDF is called with the column,
# the input to the underlying function is an iterator of pd.Series.
@pandas_udf("long")
def plus_one(batch_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
    for x in batch_iter:
        yield x + 1

df.select(plus_one(col("x"))).show()
# +-----------+
# |plus_one(x)|
# +-----------+
# |          2|
# |          3|
# |          4|
# +-----------+

# In the UDF, you can initialize some state before processing batches.
# Wrap your code with try/finally or use context managers to ensure
# the release of resources at the end.
y = 1  # value captured by the UDF closure

@pandas_udf("long")
def plus_y(batch_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
    try:
        for x in batch_iter:
            yield x + y
    finally:
        pass  # release resources here, if any

df.select(plus_y(col("x"))).show()
# +---------+
# |plus_y(x)|
# +---------+
# |        2|
# |        3|
# |        4|
# +---------+
```

Iterator of multiple Series to Iterator of Series UDF:

```python
from typing import Iterator, Tuple
import pandas as pd

from pyspark.sql.functions import col, pandas_udf, struct

pdf = pd.DataFrame([1, 2, 3], columns=["x"])
df = spark.createDataFrame(pdf)

@pandas_udf("long")
def multiply_two_cols(
        iterator: Iterator[Tuple[pd.Series, pd.Series]]) -> Iterator[pd.Series]:
    for a, b in iterator:
        yield a * b

df.select(multiply_two_cols("x", "x")).show()
# +-----------------------+
# |multiply_two_cols(x, x)|
# +-----------------------+
# |                      1|
# |                      4|
# |                      9|
# +-----------------------+
```

Series to scalar UDF:

```python
import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql import Window

df = spark.createDataFrame(
    [(1, 1.0), (1, 2.0), (2, 3.0), (2, 5.0), (2, 10.0)],
    ("id", "v"))

# Declare the function and create the UDF
@pandas_udf("double")
def mean_udf(v: pd.Series) -> float:
    return v.mean()

df.select(mean_udf(df['v'])).show()
# +-----------+
# |mean_udf(v)|
# +-----------+
# |        4.2|
# +-----------+

df.groupby("id").agg(mean_udf(df['v'])).show()
# +---+-----------+
# | id|mean_udf(v)|
# +---+-----------+
# |  1|        1.5|
# |  2|        6.0|
# +---+-----------+

w = Window \
    .partitionBy('id') \
    .rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)
df.withColumn('mean_v', mean_udf(df['v']).over(w)).show()
# +---+----+------+
# | id|   v|mean_v|
# +---+----+------+
# |  1| 1.0|   1.5|
# |  1| 2.0|   1.5|
# |  2| 3.0|   6.0|
# |  2| 5.0|   6.0|
# |  2|10.0|   6.0|
# +---+----+------+
```

---

## 53. Python UDTFs (Session-scoped)

**Einfach erklärt:** Session-scoped Python-UDTFs werden als Python-Klasse mit verpflichtender `eval`-Methode implementiert, die Ausgabezeilen per `yield` zurückgibt, und über `spark.udtf.register()` an die aktuelle SparkSession gebunden (im Gegensatz zur Unity-Catalog-Variante). Sie unterstützen variable Argumentlisten (`*args`/`**kwargs`), statische oder dynamisch berechnete Ausgabeschemata (`analyze`-Methode) sowie skalare und Table-Argumente inklusive `PARTITION BY`/`ORDER BY`/`WITH SINGLE PARTITION`.

Grundlegende UDTF-Syntax:

```python
from pyspark.sql.functions import lit, udtf

@udtf(returnType="sum: int, diff: int")
class GetSumDiff:
    def eval(self, x: int, y: int):
        yield x + y, x - y

GetSumDiff(lit(1), lit(2)).show()
```

```text
+----+-----+
| sum| diff|
+----+-----+
|   3|   -1|
+----+-----+
```

Eine UDTF registrieren:

```python
spark.udtf.register("get_sum_diff", GetSumDiff)
```

Eine registrierte UDTF aufrufen:

```python
spark.udtf.register("get_sum_diff", GetSumDiff)
spark.sql("SELECT * FROM get_sum_diff(1,2);").show()
```

```python
%sql
SELECT * FROM get_sum_diff(1,2);
```

Upgrade zu Unity Catalog (SQL DDL):

```sql
CREATE OR REPLACE FUNCTION get_sum_diff(x INT, y INT)
RETURNS TABLE (sum INT, diff INT)
LANGUAGE PYTHON
HANDLER 'GetSumDiff'
AS $$
class GetSumDiff:
    def eval(self, x: int, y: int):
        yield x + y, x - y
$$;

SELECT * FROM get_sum_diff(10, 3);
```

```text
+-----+------+
| sum | diff |
+-----+------+
| 13  | 7    |
+-----+------+
```

Apache Arrow nutzen (`useArrow=True`):

```python
@udtf(returnType="c1: int, c2: int", useArrow=True)
```

Variable Argumentlisten, `*args`:

```python
@udtf(returnType="sum: int, diff: int")
class GetSumDiff:
    def eval(self, *args):
        assert(len(args) == 2)
        assert(isinstance(arg, int) for arg in args)
        x = args[0]
        y = args[1]
        yield x + y, x - y

GetSumDiff(lit(1), lit(2)).show()
```

`**kwargs`:

```python
@udtf(returnType="sum: int, diff: int")
class GetSumDiff:
    def eval(self, **kwargs):
        x = kwargs["x"]
        y = kwargs["y"]
        yield x + y, x - y

GetSumDiff(x=lit(1), y=lit(2)).show()
```

Statisches Schema, als `StructType`:

```python
StructType().add("c1", StringType())
```

oder als DDL-String:

```text
c1: string
```

Dynamisches Schema zur Aufrufzeit berechnen (`analyze`):

```python
from pyspark.sql.functions import lit, udtf
from pyspark.sql.types import StructType, IntegerType
from pyspark.sql.udtf import AnalyzeArgument, AnalyzeResult


@udtf
class MyUDTF:
  @staticmethod
  def analyze(text: AnalyzeArgument) -> AnalyzeResult:
    schema = StructType()
    for index, word in enumerate(sorted(list(set(text.value.split(" "))))):
      schema = schema.add(f"word_{index}", IntegerType())
    return AnalyzeResult(schema=schema)

  def eval(self, text: str):
    counts = {}
    for word in text.split(" "):
      if word not in counts:
            counts[word] = 0
      counts[word] += 1
    result = []
    for word in sorted(list(set(text.split(" ")))):
      result.append(counts[word])
    yield result

MyUDTF(lit("hello world")).columns
```

```text
['word_0', 'word_1']
```

Zustand für zukünftige `eval`-Aufrufe weitergeben (Subklasse von `AnalyzeResult`):

```python
from pyspark.sql.functions import lit, udtf
from pyspark.sql.types import StructType, IntegerType
from pyspark.sql.udtf import AnalyzeArgument, AnalyzeResult

@dataclass
class AnalyzeResultWithBuffer(AnalyzeResult):
    buffer: str = ""

@udtf
class TestUDTF:
  def __init__(self, analyze_result=None):
    self._total = 0
    if analyze_result is not None:
      self._buffer = analyze_result.buffer
    else:
      self._buffer = ""

  @staticmethod
  def analyze(argument, _) -> AnalyzeResult:
    if (
      argument.value is None
      or argument.isTable
      or not isinstance(argument.value, str)
      or len(argument.value) == 0
    ):
      raise Exception("The first argument must be a non-empty string")
    assert argument.dataType == StringType()
    assert not argument.isTable
    return AnalyzeResultWithBuffer(
      schema=StructType()
        .add("total", IntegerType())
        .add("buffer", StringType()),
      withSinglePartition=True,
      buffer=argument.value,
    )

  def eval(self, argument, row: Row):
    self._total += 1

  def terminate(self):
    yield self._total, self._buffer

spark.udtf.register("test_udtf", TestUDTF)

spark.sql(
  """
  WITH t AS (
    SELECT id FROM range(1, 21)
  )
  SELECT total, buffer
  FROM test_udtf("abc", TABLE(t))
  """
).show()
```

```text
+-------+-------+
| count | buffer|
+-------+-------+
|    20 |  "abc"|
+-------+-------+
```

Ausgabezeilen per `yield` zurückgeben — als Tupel:

```python
def eval(self, x, y, z):
  yield (x, y, z)
```

Ohne Klammern:

```python
def eval(self, x, y, z):
  yield x, y, z
```

Einzelspaltige Zeile (Komma am Ende):

```python
def eval(self, x, y, z):
  yield x,
```

Als `pyspark.sql.Row`:

```python
def eval(self, x, y, z):
  from pyspark.sql.types import Row
  yield Row(x, y, z)
```

Aus `terminate` über eine Python-Liste:

```python
def terminate(self):
  yield [self.x, self.y, self.z]
```

Skalare Argumente übergeben:

```sql
SELECT * FROM get_sum_diff(1, y => 2)
```

Table-Argumente an eine UDTF übergeben:

```python
from pyspark.sql.functions import udtf
from pyspark.sql.types import Row

@udtf(returnType="id: int")
class FilterUDTF:
    def eval(self, row: Row):
        if row["id"] > 5:
            yield row["id"],

spark.udtf.register("filter_udtf", FilterUDTF)
```

```sql
SELECT * FROM filter_udtf(TABLE(SELECT * FROM range(10)));
```

```text
+---+
| id|
+---+
|  6|
|  7|
|  8|
|  9|
+---+
```

Partitionierung der Eingabezeilen — Beispiel-UDTF:

```python
from pyspark.sql.functions import udtf
from pyspark.sql.types import Row

@udtf(returnType="a: string, b: int")
class FilterUDTF:
  def __init__(self):
    self.key = ""
    self.max = 0

  def eval(self, row: Row):
    self.key = row["a"]
    self.max = max(self.max, row["b"])

  def terminate(self):
    yield self.key, self.max

spark.udtf.register("filter_udtf", FilterUDTF)
```

```sql
-- Create an input table with some example values.
DROP TABLE IF EXISTS values_table;
CREATE TABLE values_table (a STRING, b INT);
INSERT INTO values_table VALUES ('abc', 2), ('abc', 4), ('def', 6), ('def', 8);
SELECT * FROM values_table;
```

```text
+-------+----+
|     a |  b |
+-------+----+
| "abc" | 2  |
| "abc" | 4  |
| "def" | 6  |
| "def" | 8  |
+-------+----+
```

```sql
-- Query the UDTF with the input table as an argument and a directive to partition the input
-- rows such that all rows with each unique value in the `a` column are processed by the same
-- instance of the UDTF class. Within each partition, the rows are ordered by the `b` column.
SELECT * FROM filter_udtf(TABLE(values_table) PARTITION BY a ORDER BY b) ORDER BY 1;
```

```text
+-------+----+
|     a |  b |
+-------+----+
| "abc" | 4  |
| "def" | 8  |
+-------+----+
```

```sql
-- Query the UDTF with the input table as an argument and a directive to partition the input
-- rows such that all rows with each unique result of evaluating the "LENGTH(a)" expression are
-- processed by the same instance of the UDTF class. Within each partition, the rows are ordered
-- by the `b` column.
SELECT * FROM filter_udtf(TABLE(values_table) PARTITION BY LENGTH(a) ORDER BY b) ORDER BY 1;
```

```text
+-------+---+
|     a | b |
+-------+---+
| "def" | 8 |
+-------+---+
```

```sql
-- Query the UDTF with the input table as an argument and a directive to consider all the input
-- rows in one single partition such that exactly one instance of the UDTF class consumes all of
-- the input rows. Within each partition, the rows are ordered by the `b` column.
SELECT * FROM filter_udtf(TABLE(values_table) WITH SINGLE PARTITION ORDER BY b) ORDER BY 1;
```

```text
+-------+----+
|     a |  b |
+-------+----+
| "def" | 8 |
+-------+----+
```

Partitionierung aus der `analyze`-Methode heraus festlegen:

```python
@staticmethod
def analyze(*args) -> AnalyzeResult:
  """
  The input table will be partitioned across several UDTF calls based on the monthly
  values of each `date` column. The rows within each partition will arrive ordered by the `date`
  column. The UDTF will only receive the `date` and `word` columns from the input table.
  """
  from pyspark.sql.functions import (
    AnalyzeResult,
    OrderingColumn,
    PartitioningColumn,
  )

  assert len(args) == 1, "This function accepts one argument only"
  assert args[0].isTable, "Only table arguments are supported"
  return AnalyzeResult(
    schema=StructType()
      .add("month", DateType())
      .add("longest_word", IntegerType()),
    partitionBy=[
      PartitioningColumn("extract(month from date)")],
    orderBy=[
      OrderingColumn("date")],
    select=[
      SelectedColumn("date"),
      SelectedColumn(
        name="length(word)",
        alias="length_word")])
```

---

## 54. Session-scoped Scala- und Java-UDFs

**Einfach erklärt:** Neben Unity-Catalog-governed Scala-/Java-UDFs gibt es zwei session-scoped Ansätze: inline Scala-UDFs direkt im Notebook (nicht auf serverlosem Compute verfügbar) und Java-UDFs aus einer vorkompilierten JAR über `spark.udf.registerJavaFunction` (auch auf Serverless verfügbar, ab Runtime 18 LTS). Für mehrere Abschnitte (Funktion als UDF registrieren, UDF mit DataFrames verwenden, Scala-Projekt-Setup, Null-Prüfungs-Beispiele, typisierte Dataset-API) liegt kein Code-Beispiel vor.

| Ansatz | Beschreibung |
|---|---|
| Inline Scala-UDF | direkt im Notebook definiert, session-scoped, nicht auf Serverless |
| Java-UDF aus einer JAR | über `spark.udf.registerJavaFunction`, session-scoped, auf Serverless verfügbar |
| Unity-Catalog-governed Scala/Java-UDF | governed, Serverless-fähig (siehe eigener Abschnitt oben) |

Eine Funktion als UDF registrieren: **[im Original leer/kein Code vorhanden]**

Die UDF in Spark SQL aufrufen:

```sql
%sql select id, square(id) as id_squared from test
```

UDF mit DataFrames verwenden: **[im Original leer/kein Code vorhanden]**

Eine Java-UDF aus einer JAR registrieren — Schritt 1: Projekt anlegen, Scala:

```bash
sbt new scala/scala-seed.g8
```

Java (Maven):

```bash
mvn archetype:generate \
  -DgroupId=com.example \
  -DartifactId=my-udf \
  -DarchetypeArtifactId=maven-archetype-quickstart \
  -DinteractiveMode=false
```

```xml
<properties>
  <maven.compiler.source>17</maven.compiler.source>
  <maven.compiler.target>17</maven.compiler.target>
  <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>

<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-shade-plugin</artifactId>
      <version>3.5.0</version>
      <executions>
        <execution>
          <phase>package</phase>
          <goals>
            <goal>shade</goal>
          </goals>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

Schritt 2: Die UDF-Klasse schreiben:

```java
package com.example;

import org.apache.spark.sql.api.java.UDF1;

public class MyIntegerUDF implements UDF1<Integer, Integer> {
  @Override
  public Integer call(Integer x) {
    return x + 1;
  }
}
```

Schritt 3: Das Fat-JAR bauen:

```bash
sbt clean assembly
```

```bash
mvn clean package
```

Schritt 4: JAR in ein Unity-Catalog-Volume hochladen:

```sql
CREATE VOLUME IF NOT EXISTS my_catalog.my_schema.udf_jars
COMMENT 'Storage for UDF JAR files';
```

Schritt 5: UDF registrieren und aufrufen:

```python
# Add the JAR containing your UDF class to the session
spark.addArtifact("/Volumes/my_catalog/my_schema/udf_jars/my-udf-assembly-0.1.0-SNAPSHOT.jar")

# Register the UDF class, providing the SQL function name,
# the fully qualified class name, and the return type
from pyspark.sql.types import IntegerType

spark.udf.registerJavaFunction(
    "my_udf",
    "com.example.MyIntegerUDF",
    IntegerType(),
)

# Call the UDF from Spark SQL
spark.sql("SELECT my_udf(21)").show()
```

```text
+----------+
| my_udf(21)|
+----------+
|        22|
+----------+
```

Auswertungsreihenfolge und Null-Prüfung: **[im Original leer/kein Code vorhanden]**

Typisierte Dataset-APIs: **[im Original leer/kein Code vorhanden]**

Scala-UDF-Feature-Kompatibilität nach Databricks-Runtime:

| Feature | Minimale Databricks-Runtime-Version |
|---|---|
| Scalar UDFs | Databricks Runtime 14.2 |
| `Dataset.map`, `Dataset.mapPartitions`, `Dataset.filter`, `Dataset.reduce`, `Dataset.flatMap` | Databricks Runtime 15.4 |
| `KeyValueGroupedDataset.flatMapGroups`, `KeyValueGroupedDataset.mapGroups` | Databricks Runtime 15.4 |
| (Streaming) `foreachWriter` Sink | Databricks Runtime 15.4 |
| (Streaming) `foreachBatch` | Databricks Runtime 16.1 |
| (Streaming) `KeyValueGroupedDataset.flatMapGroupsWithState` | Databricks Runtime 16.2 |
| `spark.udf.registerJavaFunction` (Java-UDF aus einer JAR) | Databricks Runtime 18 LTS |

---

## 55. Scala User-Defined Aggregate Functions (UDAFs)

**Einfach erklärt:** UDAFs fassen mehrere Zeilen (z. B. innerhalb eines `GROUP BY`) zu einem einzigen Ergebnis zusammen — anders als Scalar-UDFs, die pro Zeile genau einen Wert liefern. In Scala werden sie über die `UserDefinedAggregateFunction`-API implementiert, mit den Bestandteilen `inputSchema`, `bufferSchema`, `dataType`, `initialize`, `update`, `merge` und `evaluate`. Für Implementierung, Registrierung und DataFrame-API-Aufruf liegt kein Code-Beispiel vor — nur das SQL-Aufrufbeispiel über `GROUP BY`.

Eine `UserDefinedAggregateFunction` implementieren (geometrisches Mittel als Beispiel): **[im Original leer/kein Code vorhanden]**

Die Klasse implementiert dabei: `inputSchema` (Eingabefelder), `bufferSchema` (interne Felder für die Berechnung), `dataType` (Ausgabetyp), `initialize` (Startwert), `update` (Buffer-Update anhand einer Eingabe), `merge` (Zusammenführen zweier Buffer-Objekte), `evaluate` (finaler Wert).

Die UDAF bei Spark SQL registrieren: **[im Original leer/kein Code vorhanden]**

Die UDAF verwenden — Test-DataFrame und Spark-SQL-Tabelle anlegen: **[im Original leer/kein Code vorhanden]**

Aufruf über eine `GROUP BY`-Anweisung in SQL:

```sql
-- Use a group_by statement and call the UDAF.
select group_id, gm(id) from simple group by group_id
```

Aufruf über die DataFrame-API: **[im Original leer/kein Code vorhanden]**

---

## 56. Task-Kontext in einer UDF abrufen (`TaskContext`)

**Einfach erklärt:** Über die `TaskContext`-PySpark-API lassen sich während der Ausführung einer Batch-Unity-Catalog-Python-UDF oder einer PySpark-Scalar-UDF Kontextinformationen abrufen — etwa die Identität des aktuell ausführenden Nutzers, Cluster-Tags oder die Databricks-Runtime-Version. Das ist z. B. nützlich, um die Nutzeridentität an einen externen Dienst weiterzugeben. `TaskContext` wird ab Databricks Runtime 16.3 unterstützt.

PySpark-UDF-Beispiel (Nutzerkontext ausgeben):

```python
@udf
def log_context():
  import json
  from pyspark.taskcontext import TaskContext
  tc = TaskContext.get()

  # Returns current user executing the UDF
  session_user = tc.getLocalProperty("user")

  # Returns cluster tags
  tags = dict(item.values() for item in json.loads(tc.getLocalProperty("spark.databricks.clusterUsageTags.clusterAllTags  ") or "[]"))

  # Returns current version details
  current_version = {
    "dbr_version": tc.getLocalProperty("spark.databricks.clusterUsageTags.sparkVersion"),
    "dbsql_version": tc.getLocalProperty("spark.databricks.clusterUsageTags.dbsqlVersion")
  }

  return {
    "user": session_user,
    "job_group_id": job_group_id,
    "tags": tags,
    "current_version": current_version
  }
```

Hinweis: Im Rückgabe-Dictionary wird `job_group_id` verwendet, obwohl sie im gezeigten Code nirgends zugewiesen wird. Vermutlich fehlt eine Zeile wie `job_group_id = tc.getLocalProperty("spark.jobGroup.id")`.

Batch-Unity-Catalog-Python-UDF-Beispiel (Nutzeridentität für AWS-Lambda-Aufruf):

```sql
%sql
CREATE OR REPLACE FUNCTION main.test.call_lambda_func(data STRING, debug BOOLEAN) RETURNS STRING LANGUAGE PYTHON
PARAMETER STYLE PANDAS
HANDLER 'batchhandler'
CREDENTIALS (
  `batch-udf-service-creds-example-cred` DEFAULT
)
AS $$
import boto3
import json
import pandas as pd
import base64
from pyspark.taskcontext import TaskContext


def batchhandler(it):
  # Automatically picks up DEFAULT credential:
  session = boto3.Session()

  client = session.client("lambda", region_name="us-west-2")

  # Can propagate TaskContext information to lambda context:
  user_ctx = {"custom": {"user": TaskContext.get().getLocalProperty("user")}}

  for vals, is_debug in it:
    payload = json.dumps({"values": vals.to_list(), "is_debug": bool(is_debug[0])})

    res = client.invoke(
      FunctionName="HashValuesFunction",
      InvocationType="RequestResponse",
      ClientContext=base64.b64encode(json.dumps(user_ctx).encode("utf-8")).decode(
        "utf-8"
      ),
      Payload=payload,
    )

    response_payload = json.loads(res["Payload"].read().decode("utf-8"))
    if "errorMessage" in response_payload:
      raise Exception(str(response_payload))

    yield pd.Series(response_payload["values"])
$$;
```

```sql
SELECT main.test.call_lambda_func(data, false)
FROM VALUES
('abc'),
('def')
AS t(data)
```

`TaskContext`-Eigenschaften (`getLocalProperty()`):

| Property-Schlüssel | Beschreibung | Beispielnutzung |
|---|---|---|
| `user` | Der Nutzer, der die UDF aktuell ausführt | `tc.getLocalProperty("user")` → `"alice"` |
| `spark.jobGroup.id` | Spark-Job-Group-ID der aktuellen UDF | `tc.getLocalProperty("spark.jobGroup.id")` → `"jobGroup-92318"` |
| `spark.databricks.clusterUsageTags.clusterAllTags` | Cluster-Metadaten-Tags als JSON-String | `tc.getLocalProperty("spark.databricks.clusterUsageTags.clusterAllTags")` → `[{"Department": "Finance"}]` |
| `spark.databricks.clusterUsageTags.region` | Region des Workspace | `tc.getLocalProperty("spark.databricks.clusterUsageTags.region")` → `"us-west-2"` |
| `accountId` | Databricks-Account-ID | `tc.getLocalProperty("accountId")` → `"1234567890123456"` |
| `orgId` | Workspace-ID (auf DBSQL nicht verfügbar) | `tc.getLocalProperty("orgId")` → `"987654321"` |
| `spark.databricks.clusterUsageTags.sparkVersion` | Databricks-Runtime-Version (Nicht-DBSQL) | `tc.getLocalProperty("spark.databricks.clusterUsageTags.sparkVersion")` → `"16.3"` |
| `spark.databricks.clusterUsageTags.dbsqlVersion` | DBSQL-Version (DBSQL-Umgebungen) | `tc.getLocalProperty("spark.databricks.clusterUsageTags.dbsqlVersion")` → `"2024.35"` |

---

## 57. Databricks Utils (`dbutils`) — Überblick

**Einfach erklärt:** `dbutils` ist eine Sammlung vorinstallierter Hilfsfunktionen in Databricks-Notebooks und -Jobs für Dateisystemzugriff, Secrets, Widgets, Notebook-Verkettung, Job-Task-Kommunikation und mehr. Das Modul gliedert sich in acht Sub-Utilities: Credentials, Data, File System, Jobs, Library, Notebook, Secrets und Widgets — jede davon mit eigenem Befehlssatz.

Keine Code-Beispiele in dieser Datei — reiner Überblick mit Verweisen auf die Sub-Utility-Dateien.

---

## 58. Credentials Utility (`dbutils.credentials`)

**Einfach erklärt:** Dieses Utility dient dazu, innerhalb eines Notebooks die IAM-Rolle zu wechseln, die beim Zugriff auf S3 angenommen wird — verfügbar ist es aber nur auf Clustern mit aktiviertem Credential Passthrough.

| Befehl | Signatur | Beschreibung |
|---|---|---|
| `assumeRole` | `assumeRole(role: String): boolean` | setzt den IAM-Rollen-ARN, der bei der S3-Authentifizierung angenommen wird |
| `getServiceCredentialsProvider` | `getServiceCredentialsProvider(credentialName: String): Object` | liefert einen Service-Credentials-Provider für das angegebene Service Credential — Rückgabetyp cloud-spezifisch; nicht in R verfügbar |
| `showCurrentRole` | `showCurrentRole: List` | listet die aktuell gesetzte(n) IAM-Rolle(n) |
| `showRoles` | `showRoles: List` | listet alle möglichen, annehmbaren IAM-Rollen |

```python
dbutils.credentials.assumeRole("arn:aws:iam::123456789012:roles/my-role")
# Out[1]: True

dbutils.credentials.showCurrentRole()
# Out[1]: ['arn:aws:iam::123456789012:role/my-role-a']

dbutils.credentials.showRoles()
# Out[1]: ['arn:aws:iam::123456789012:role/my-role-a', 'arn:aws:iam::123456789012:role/my-role-b']
```

---

## 59. Data Utility (`dbutils.data`)

**Einfach erklärt:** `dbutils.data.summarize` berechnet und zeigt automatisch Übersichtsstatistiken für einen Spark- oder pandas-DataFrame an — praktisch zum schnellen Erkunden eines Datensatzes. Das Feature ist Public Preview und erfordert Databricks Runtime 9.0+. Standardmäßig werden Näherungswerte genutzt (`precise=false`); ab Runtime 10.4 LTS lässt sich mit `precise=true` höhere Genauigkeit bei höheren Laufzeitkosten erzwingen. Wichtig: Der Befehl analysiert den kompletten DataFrame-Inhalt, was bei sehr großen DataFrames teuer werden kann.

**Signatur:**

```
summarize(df: Object, precise: boolean): void
```

| Parameter | Bedeutung |
|---|---|
| `df` | zu analysierender Spark- oder pandas-DataFrame |
| `precise` | Boolean (ab Databricks Runtime 10.4 LTS); Standard `false` |

```python
df = spark.read.format('csv').load(
  '/databricks-datasets/Rdatasets/data-001/csv/ggplot2/diamonds.csv',
  header=True,
  inferSchema=True)
dbutils.data.summarize(df)
```

---

## 60. File System Utility (`dbutils.fs`)

**Einfach erklärt:** `dbutils.fs` bietet Befehle für den Zugriff auf das Databricks-Dateisystem (DBFS) — kopieren, verschieben, löschen, auflisten, lesen/schreiben kleiner Dateien und (veraltet) Mount-Operationen. Die Python-Implementierung nutzt `snake_case` statt `camelCase` bei Keyword-Argumenten. `mount`/`mounts` gelten als Auslaufmodell, weil sie nicht mit der Serverless-Compute-Architektur kompatibel sind.

| Befehl | Signatur | Beschreibung |
|---|---|---|
| `cp` | `cp(from: String, to: String, recurse: boolean = false): boolean` | kopiert eine Datei/ein Verzeichnis, ggf. über Dateisystemgrenzen hinweg |
| `head` | `head(file: String, max_bytes: int = 65536): String` | gibt bis zu `max_bytes` einer Datei als UTF-8-Text zurück |
| `ls` | `ls(dir: String): Seq` | listet Verzeichnisinhalt auf (Pfad, Name, Größe, Änderungszeit als `FileInfo`-Objekte) |
| `mkdirs` | `mkdirs(dir: String): boolean` | legt das Verzeichnis samt fehlender übergeordneter Verzeichnisse an |
| `mount` | `mount(source: String, mountPoint: String, encryptionType: String = "", owner: String = null, extraConfigs: Map = Map.empty[String, String]): boolean` | hängt ein Quellverzeichnis an einem Mount-Punkt in DBFS ein |
| `mounts` | `mounts: Seq` | zeigt Informationen zu allen aktuell eingehängten Mounts (`MountInfo`-Objekte) |
| `mv` | `mv(from: String, to: String, recurse: boolean = false): boolean` | verschiebt eine Datei/ein Verzeichnis (intern: Kopie + Löschung) |
| `put` | `put(file: String, contents: String, overwrite: boolean = false): boolean` | schreibt einen String UTF-8-kodiert in eine Datei |
| `refreshMounts` | `refreshMounts: boolean` | weist alle Cluster-Maschinen an, ihren Mount-Informations-Cache zu aktualisieren |
| `rm` | `rm(dir: String, recurse: boolean = false): boolean` | löscht eine Datei/ein Verzeichnis; Fehler bei nicht-leerem Verzeichnis ohne `recurse` |
| `unmount` | `unmount(mountPoint: String): boolean` | entfernt einen DBFS-Mount-Punkt |
| `updateMount` | `updateMount(source: String, mountPoint: String, encryptionType: String = "", owner: String = null, extraConfigs: Map = Map.empty[String, String]): boolean` | ändert einen bestehenden Mount-Punkt statt einen neuen anzulegen — ab Databricks Runtime 10.4 LTS |

```python
dbutils.fs.cp("/Volumes/main/default/my-volume/data.csv",
              "/Volumes/main/default/my-volume/new-data.csv")
# Out[4]: True

dbutils.fs.head("/Volumes/main/default/my-volume/data.csv", 25)
# Out[12]: 'Year,First Name,County,Se'

dbutils.fs.ls("/Volumes/main/default/my-volume/")
# Out[13]: [FileInfo(path='dbfs:/Volumes/main/default/my-volume/data.csv',
#           name='data.csv', size=2258987, modificationTime=1711357839000)]

dbutils.fs.mkdirs("/Volumes/main/default/my-volume/my-data")
# Out[15]: True

dbutils.fs.mv("/Volumes/main/default/my-volume/rows.csv",
              "/Volumes/main/default/my-volume/my-data/")
# Out[2]: True

dbutils.fs.put("/Volumes/main/default/my-volume/hello.txt",
               "Hello, Databricks!", True)
# Out[6]: True

dbutils.fs.rm("/Volumes/main/default/my-volume/my-data/", True)
# Out[8]: True

# Mounting (siehe Mounts und Migration.md für Auth-Details)
aws_bucket_name = "my-bucket"
mount_name = "s3-my-bucket"
dbutils.fs.mount("s3a://%s" % aws_bucket_name, "/mnt/%s" % mount_name)

dbutils.fs.mounts()
# Out[11]: [MountInfo(mountPoint='/mnt/databricks-results',
#           source='databricks-results', encryptionType='sse-s3')]

dbutils.fs.refreshMounts()

dbutils.fs.updateMount("s3a://%s" % aws_bucket_name, "/mnt/%s" % mount_name)

dbutils.fs.unmount("/mnt/<mount-name>")
```

Wichtige Hinweise: `mount`/`mounts` sind Serverless-inkompatibel; einen Mount-Punkt nie ändern, während andere Jobs ihn nutzen; `%fs` ist die Magic-Command-Kurzform (z. B. `%fs ls /Volumes/main/default/my-volume/`); für Workspace-Dateien stattdessen `%sh ls` nutzen; `dbutils`-Aufrufe innerhalb von Executors können zu unerwarteten Ergebnissen führen.

---

## 61. Jobs Utility (`dbutils.jobs`)

**Einfach erklärt:** `dbutils.jobs` (nur Python) dreht sich im Kern um die Subutility `taskValues`, mit der Job-Tasks beliebige Werte setzen und in anderen Tasks desselben Laufs wieder abrufen können — etwa um IDs oder Metriken zwischen Tasks weiterzugeben. Maximal 250 Task Values pro Task und Job-Lauf.

**`get`-Signatur:**

```
get(taskKey: String, key: String, default: int, debugValue: int): Seq
```

| Parameter | Pflicht | Bedeutung |
|---|---|---|
| `taskKey` | ja | Name des Tasks, der den Wert gesetzt hat |
| `key` | ja | Name des Task-Value-Keys |
| `default` | optional | Rückgabewert, falls `key` nicht gefunden wird |
| `debugValue` | optional | Rückgabewert, wenn außerhalb eines Job-Kontexts ausgeführt |

```python
dbutils.jobs.taskValues.get(taskKey    = "my-task",
                            key        = "my-key",
                            default    = 7,
                            debugValue = 42)
```

**`set`-Signatur:**

```
set(key: String, value: String): boolean
```

| Parameter | Pflicht | Bedeutung |
|---|---|---|
| `key` | ja | Key des Task Value — muss innerhalb des Tasks eindeutig sein |
| `value` | ja | zu speichernder Wert — muss JSON-darstellbar sein, maximal 48 KiB |

```python
dbutils.jobs.taskValues.set(key   = "my-key",
                            value = 5)

dbutils.jobs.taskValues.set(key   = "my-other-key",
                            value = "my other value")
```

---

## 62. Library Utility (`dbutils.library`)

**Einfach erklärt:** `dbutils.library` ist größtenteils deprecated — Databricks empfiehlt, für Bibliotheksverwaltung moderne Alternativen (Asset Bundles, `%pip install`) zu nutzen. Der einzige noch aktiv dokumentierte Befehl ist `restartPython`, der den Python-Prozess neu startet, damit lokal installierte oder aktualisierte Bibliotheken im Python-Kernel korrekt funktionieren — in der Praxis meist über die Magic-Command-Kurzform `%restart_python` verwendet.

**Syntax:** `dbutils.library.restartPython`

Keine weiteren Code-Beispiele in dieser Datei (nur die Syntaxangabe des Befehls selbst).

---

## 63. Notebook Utility (`dbutils.notebook`)

**Einfach erklärt:** Mit `dbutils.notebook` lassen sich Notebooks verketten (`run`) und mit einem Rückgabewert beenden (`exit`) — der Kern klassischer Notebook-Workflows. `run` führt ein anderes Notebook im aktuellen Cluster aus und liefert dessen Exit-Wert (max. 5 MB) zurück; ein Timeout löst eine Exception aus. Laufen im Hintergrund Structured-Streaming-Queries, beendet `exit()` diese nicht automatisch.

**Signatur `exit`:**

```python
dbutils.notebook.exit(value: String): void
```

```python
dbutils.notebook.exit("Exiting from My Other Notebook")
# Output: Notebook exited: Exiting from My Other Notebook
```

**Signatur `run`:**

```python
dbutils.notebook.run(path: String, timeoutSeconds: int, arguments: Map): String
```

| Parameter | Bedeutung |
|---|---|
| `path` | Dateipfad zum auszuführenden Notebook |
| `timeoutSeconds` | maximale Ausführungszeit in Sekunden, bevor eine Timeout-Exception ausgelöst wird |
| `arguments` | optionale Key-Value-Paare, die als Parameter an das aufgerufene Notebook übergeben werden |

```python
dbutils.notebook.run("My Other Notebook", 60)
# Output: 'Exiting from My Other Notebook'
```

---

## 64. Secrets Utility (`dbutils.secrets`)

**Einfach erklärt:** `dbutils.secrets` erlaubt das Speichern und Abrufen sensibler Credentials, ohne sie im Notebook-Code offenzulegen. Secret-Werte, die angezeigt würden, werden als `[REDACTED]` maskiert — das schützt aber nur die Notebook-Ausgabe, nicht den eigentlichen Zugriff: autorisierte Nutzer können die tatsächlichen Werte weiterhin auslesen.

| Befehl | Signatur | Beschreibung |
|---|---|---|
| `get` | `get(scope: String, key: String): String` | liefert die String-Repräsentation eines Secret-Werts |
| `getBytes` | `getBytes(scope: String, key: String): byte[]` | liefert die Bytes-Repräsentation eines Secret-Werts |
| `list` | `list(scope: String): Seq` | listet Metadaten aller Secrets innerhalb eines Scopes (`SecretMetadata`-Objekte) |
| `listScopes` | `listScopes: Seq` | listet alle verfügbaren Secret-Scopes (`SecretScope`-Objekte) |
| `help` | `help()` / `help("<command-name>")` | zeigt verfügbare Befehle bzw. befehlsspezifische Dokumentation |

```python
dbutils.secrets.get(scope="my-scope", key="my-key")
# Out[14]: '[REDACTED]'

dbutils.secrets.getBytes(scope="my-scope", key="my-key")
# Out[1]: b'a1!b2@c3#'

dbutils.secrets.list("my-scope")
# Out[10]: [SecretMetadata(key='my-key')]

dbutils.secrets.listScopes()
# Out[14]: [SecretScope(name='my-scope')]

dbutils.secrets.help()
dbutils.secrets.help("get")
```

---

## 65. Widgets Utility (`dbutils.widgets`)

**Einfach erklärt:** `dbutils.widgets` parametrisiert Notebooks über interaktive Eingabeelemente (Text, Dropdown, Combobox, Multiselect). Widget-Werte werden immer als String zurückgegeben; Python nutzt `snake_case` für Keyword-Argumente. `getAll()` (ab Runtime 13.3 LTS, nur Python/Scala) liefert alle Widget-Werte gebündelt, z. B. für eine parametrisierte SQL-Query.

| Befehl | Signatur | Auswahltyp | Eingabemethode |
|---|---|---|---|
| `text` | `text(name: String, defaultValue: String, label: String): void` | — | freie Texteingabe |
| `dropdown` | `dropdown(name: String, defaultValue: String, choices: Seq, label: String): void` | einfach | vordefinierte Liste |
| `combobox` | `combobox(name: String, defaultValue: String, choices: Seq, label: String): void` | einfach | vordefinierte Liste + Textsuche |
| `multiselect` | `multiselect(name: String, defaultValue: String, choices: Seq, label: String): void` | mehrfach | vordefinierte Liste (Checkboxen) |

```python
dbutils.widgets.text(
  name='your_name_text',
  defaultValue='Enter your name',
  label='Your name')

dbutils.widgets.dropdown(
  name='toys_dropdown',
  defaultValue='basketball',
  choices=['alphabet blocks', 'basketball', 'cape', 'doll'],
  label='Toys')

dbutils.widgets.combobox(
  name='fruits_combobox',
  defaultValue='banana',
  choices=['apple', 'banana', 'coconut', 'dragon fruit'],
  label='Fruits')

dbutils.widgets.multiselect(
  name='days_multiselect',
  defaultValue='Tuesday',
  choices=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
  label='Days of the Week')
```

| Befehl | Signatur | Beschreibung |
|---|---|---|
| `get` | `get(name: String): String` | liefert den aktuellen Wert eines Widgets |
| `getAll` | `getAll: map` | liefert ein Dictionary aller Widget-Namen samt aktuellem Wert |
| `getArgument` (deprecated) | `getArgument(name: String, optional: String): String` | wie `get`, mit optionalem Fallback-Text — durch `get()` ersetzt |

```python
dbutils.widgets.get('fruits_combobox')
# Rückgabe: banana

# getAll() eignet sich, um mehrere Widget-Werte gebündelt an eine Spark-SQL-Query zu übergeben:
df = spark.sql("SELECT * FROM table where col1 = :param",
               dbutils.widgets.getAll())
```

| Befehl | Signatur | Beschreibung |
|---|---|---|
| `remove` | `remove(name: String): void` | löscht ein einzelnes Widget anhand seines Namens |
| `removeAll` | `removeAll: void` | löscht alle Widgets des Notebooks gleichzeitig |

```python
dbutils.widgets.remove('fruits_combobox')
dbutils.widgets.removeAll()
```

```python
dbutils.widgets.help()
dbutils.widgets.help("combobox")
```

---

## 66. Databricks SDK für Python

**Einfach erklärt:** Das Databricks SDK für Python automatisiert Databricks-Operationen (Cluster, Jobs, Volumes, Gruppen usw.) über den `WorkspaceClient` (Workspace-Ebene) bzw. `AccountClient` (Account-Ebene) und implementiert die Databricks "Unified Authentication" für einen einheitlichen Auth-Ansatz über mehrere Tools hinweg. Status: Beta, aber für den Produktiveinsatz freigegeben. Empfohlen wird Default Authentication über ein Konfigurationsprofil statt hartkodierter Credentials.

Installation lokal (venv):

```bash
pip3 install databricks-sdk
pip3 install databricks-sdk==0.1.6   # bestimmte Version
pip3 install --upgrade databricks-sdk
pip3 show databricks-sdk             # Version prüfen
```

Installation lokal (Poetry):

```bash
poetry add databricks-sdk
poetry add databricks-sdk==0.1.6     # bestimmte Version
poetry add databricks-sdk@latest     # aktualisieren
poetry show databricks-sdk           # Version prüfen
```

Installation im Databricks-Notebook:

```python
%pip install databricks-sdk --upgrade
```

```python
dbutils.library.restartPython()
```

```python
%pip show databricks-sdk | grep -oP '(?<=Version: )\S+'
```

Authentifizierung — Default Authentication (empfohlen):

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
```

Hartkodierte Credentials (nicht empfohlen):

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient(
  host = 'https://...',
  token = '...')
```

| Methode | Verfügbar ab |
|---|---|
| Personal-Access-Token-Authentifizierung | alle SDK-Versionen |
| OAuth Machine-to-Machine (M2M) | alle SDK-Versionen |
| OAuth User-to-Machine (U2M) | SDK-Version 0.1.9+ |
| Standard-Notebook-Authentifizierung | SDK-Version 0.6.0+ (die meisten Runtimes); 0.20.0+ für Runtime 15.1 |

Cluster auflisten:

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
for c in w.clusters.list():
  print(c.cluster_name)
```

Cluster erstellen:

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
print("Attempting to create cluster. Please wait...")
c = w.clusters.create_and_wait(
  cluster_name = 'my-cluster',
  spark_version = '12.2.x-scala2.12',
  node_type_id = 'i3.xlarge',
  autotermination_minutes = 15,
  num_workers = 1)
print(f"The cluster is now ready at " \
      f"{w.config.host}#setting/clusters/{c.cluster_id}/configuration\n")
```

Cluster dauerhaft löschen:

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
c_id = input('ID of cluster to delete (for example, 1234-567890-ab123cd4): ')
w.clusters.permanent_delete(cluster_id = c_id)
```

Job erstellen:

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import Task, NotebookTask, Source
w = WorkspaceClient()
job_name = input("Some short name for the job (for example, my-job): ")
description = input("Some short description for the job (for example, My job): ")
existing_cluster_id = input("ID of the existing cluster in the workspace to run the job on (for example, 1234-567890-ab123cd4): ")
notebook_path = input("Workspace path of the notebook to run (for example, /Users/someone@example.com/my-notebook): ")
task_key = input("Some key to apply to the job's tasks (for example, my-key): ")
print("Attempting to create the job. Please wait...\n")
j = w.jobs.create(
  name = job_name,
  tasks = [
    Task(
      description = description,
      existing_cluster_id = existing_cluster_id,
      notebook_task = NotebookTask(
        base_parameters = dict(""),
        notebook_path = notebook_path,
        source = Source("WORKSPACE")
      ),
      task_key = task_key
    )
  ])
print(f"View the job at {w.config.host}/#job/{j.job_id}\n")
```

Job mit Serverless Compute erstellen:

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import NotebookTask, Source, Task
w = WorkspaceClient()
j = w.jobs.create(
  name = "My Serverless Job",
  tasks = [
    Task(
      notebook_task = NotebookTask(
      notebook_path = "/Users/someone@example.com/MyNotebook",
      source = Source("WORKSPACE")
      ),
      task_key = "MyTask",
   )
  ])
```

Unity-Catalog-Volume-Dateien verwalten:

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
# Volume-, Ordner- und Dateidetails definieren.
catalog = 'main'
schema = 'default'
volume = 'my-volume'
volume_path = f"/Volumes/{catalog}/{schema}/{volume}"
volume_folder = 'my-folder'
volume_folder_path = f"{volume_path}/{volume_folder}"
volume_file = 'data.csv'
volume_file_path = f"{volume_folder_path}/{volume_file}"
upload_file_path = './data.csv'

# Leeren Ordner in einem Volume anlegen.
w.files.create_directory(volume_folder_path)

# Datei in ein Volume hochladen (Methode 1: empfohlen bei Daten aus lokaler Datei)
w.files.upload_from(volume_file_path, upload_file_path, overwrite=True)

# Datei in ein Volume hochladen (Methode 2: empfohlen bei In-Memory-Daten)
with open(upload_file_path, "rb") as f:
    w.files.upload(volume_file_path, io.BytesIO(f.read()), overwrite=True)

# Volume-Inhalt auflisten.
for item in w.files.list_directory_contents(volume_path):
  print(item.path)

# Ordnerinhalt im Volume auflisten.
for item in w.files.list_directory_contents(volume_folder_path):
  print(item.path)

# Datei aus Volume herunterladen (Methode 1: empfohlen für lokalen Storage)
w.files.download_to(volume_file_path, local_download_path)

# Datei aus Volume herunterladen (Methode 2: empfohlen bei In-Memory-Daten)
resp = w.files.download(volume_file_path)
chunk_size = 8192
with resp.contents as f:
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        print(f"Read {len(chunk)} characters")

# Datei aus Volume löschen.
w.files.delete(volume_file_path)

# Ordner aus Volume löschen.
w.files.delete_directory(volume_folder_path)
```

Account-Ebenen-Gruppen auflisten (`AccountClient`, explizite Credentials nötig):

```python
from databricks.sdk import AccountClient
a = AccountClient()
for g in a.groups.list():
  print(g.display_name)
```

Databricks Utilities über das SDK nutzen — über `WorkspaceClient`:

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
d = w.dbutils.fs.ls('/')
for f in d:
  print(f.path)
```

Direkter Import (nur mit Standard-Notebook-Authentifizierung):

```python
from databricks.sdk.runtime import *
d = dbutils.fs.ls('/')
for f in d:
  print(f.path)
```

| Kontext | Verfügbare Command Groups |
|---|---|
| Lokale Entwicklung | `dbutils.fs`, `dbutils.secrets`, `dbutils.widgets`, `dbutils.jobs` |
| Notebooks | alle Command Groups (`dbutils.notebook` dabei auf zwei Verschachtelungsebenen begrenzt) |

Testen mit Mocking — Hilfsfunktion `helpers.py`:

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.compute import ClusterDetails

def create_cluster(
  w: WorkspaceClient,
  cluster_name: str,
  spark_version: str,
  node_type_id: str,
  autotermination_minutes: int,
  num_workers: int) -> ClusterDetails:
  response = w.clusters.create(
    cluster_name = cluster_name,
    spark_version = spark_version,
    node_type_id = node_type_id,
    autotermination_minutes = autotermination_minutes,
    num_workers = num_workers
  )
  return response
```

Testdatei `test_helpers.py` (mockt `WorkspaceClient` über `unittest.mock.create_autospec`):

```python
from databricks.sdk import WorkspaceClient
from helpers import *
from unittest.mock import create_autospec

def test_create_cluster():
  # Einen Mock-WorkspaceClient erstellen.
  mock_workspace_client = create_autospec(WorkspaceClient)
  # Den cluster_id-Rückgabewert des Mocks setzen.
  mock_workspace_client.clusters.create.return_value.cluster_id = '123abc'
  # Die tatsächliche Funktion mit dem Mock aufrufen.
  response = create_cluster(
    w = mock_workspace_client,
    cluster_name = 'Test Cluster',
    spark_version = '<spark-version>',
    node_type_id = '<node-type-id>',
    autotermination_minutes = 15,
    num_workers = 1
  )
  # Erwarteten Rückgabewert prüfen.
  assert response.cluster_id == '123abc'
```

Ausführen mit:

```bash
pytest
```

Lokal vs. im Notebook ausführen — lokal mit venv:

```bash
python3.10 main.py
```

Lokal mit Poetry:

```bash
poetry run python3.10 main.py
```

---

## 67. Authentifizierung für Entwicklerwerkzeuge — Überblick

**Einfach erklärt:** Databricks unterscheidet bei der Authentifizierung zwei Identitätstypen — Benutzerkonten für interaktive Nutzung und Service Principals für automatisierte Abläufe wie CI/CD — sowie zwei API-Ebenen (Account- und Workspace-Level). Empfohlen wird primär OAuth Token Federation (eigene IdP-Tokens ohne Databricks-Secrets), danach OAuth M2M für Service Principals und OAuth U2M für Benutzer mit Browser-Login. Personal Access Tokens gelten als Legacy-Methode. Die "Databricks Unified Authentication" sorgt dafür, dass dieselben Umgebungsvariablen und `.databrickscfg`-Profile über alle Werkzeuge (CLI, Terraform, SDKs) hinweg funktionieren.

Keine Code-Beispiele in dieser Datei — reiner Überblick über die Kapitelstruktur.

---

## 68. Zugriff auf Databricks-Ressourcen autorisieren

**Einfach erklärt:** Diese Einstiegsseite erklärt die Grundstruktur der Databricks-Authentifizierung: Benutzerkonten vs. Service Principals, Account-Level- vs. Workspace-Level-APIs, und die drei empfohlenen Autorisierungsmethoden (OAuth Token Federation, OAuth M2M, OAuth U2M). Unified Authentication standardisiert die Konfiguration über Umgebungsvariablen wie `DATABRICKS_HOST` oder `DATABRICKS_CLIENT_ID`, alternativ über `.databrickscfg`-Profile. Databricks integriert sich zudem über Service-Principal-Authentifizierung mit Terraform, GitHub, GitLab, Bitbucket und Jenkins.

| Umgebungsvariable | Bedeutung |
|---|---|
| `DATABRICKS_HOST` | URL der Account-Konsole **oder** des Workspaces |
| `DATABRICKS_ACCOUNT_ID` | Databricks-Account-ID |
| `DATABRICKS_CLIENT_ID` | Client-ID des Service Principals (nur OAuth) |
| `DATABRICKS_CLIENT_SECRET` | Secret des Service Principals (nur OAuth) |

Keine Code-Beispiele in dieser Datei.

---

## 69. OAuth Token Federation — Überblick

**Einfach erklärt:** OAuth Token Federation erlaubt den Zugriff auf Databricks-APIs mit Tokens des eigenen Identity Providers (IdP), sodass keine Databricks-Secrets wie PATs oder OAuth-Client-Secrets mehr verwaltet und rotiert werden müssen. Benutzer und Service Principals tauschen ein JWT ihres IdP gegen ein Databricks-OAuth-Token. Es gibt zwei Typen: **Account-weite Token Federation** (alle Benutzer/Service Principals im Account, meist zusammen mit SCIM) und **Workload Identity Federation** (automatisierte Workloads außerhalb von Databricks, z. B. CI/CD-Pipelines, ohne Secrets).

Keine Code-Beispiele in dieser Datei — reiner Konzeptüberblick.

---

## 70. Federation Policy konfigurieren

**Einfach erklärt:** Damit OAuth Token Federation funktioniert, muss eine Federation Policy angelegt werden — entweder eine **Service-Principal-Federation-Policy** (für einzelne Workloads/Service Principals, max. 20 pro Service Principal) oder eine **Account-Federation-Policy** (account-weit, max. 20 pro Account). Beide legen fest, welcher Issuer (IdP) vertraut wird, welches Subject als Identität akzeptiert wird und welche Audience passen muss. Konfiguration erfolgt über UI, Databricks CLI oder die Account-API. Best Practice: pro externer Workload-Identität einen dedizierten Service Principal anlegen und Rechte über Gruppen bündeln statt viele Policies auf einen Service Principal zu häufen.

| Tool | Federation Policy | Beispiel-Token (passend) |
|---|---|---|
| **GitHub Actions** | Issuer: `https://token.actions.githubusercontent.com`; Audience: `https://github.com/<github-org>`; Subject: `repo:<github-org>/<repo>:environment:prod` | `{ "iss": "https://token.actions.githubusercontent.com", "aud": "https://github.com/<github-org>", "sub": "repo:<github-org>/<repo>:environment:prod" }` |
| **Kubernetes** | Issuer: `https://kubernetes.default.svc`; Audience: `https://kubernetes.default.svc`; Subject: `system:serviceaccount:namespace:serviceaccountname`; JWKS JSON: `{"keys":[{"kty":"rsa","e":"AQAB","use":"sig","kid":"<key-id>","alg":"RS256","n":"uPUViFv..."}]}` | `{ "iss": "https://kubernetes.default.svc", "aud": ["https://kubernetes.default.svc"], "sub": "system:serviceaccount:namespace:serviceaccountname" }` |
| **Azure DevOps** | Issuer: `https://vstoken.dev.azure.com/<org_id>`; Audience: `api://AzureADTokenExchange`; Subject: `sc://my-org/my-project/my-connection` | `{ "iss": "https://vstoken.dev.azure.com/<org_id>", "aud": "api://AzureADTokenExchange", "sub": "sc://my-org/my-project/my-connection" }` |
| **GitLab** | Issuer: `https://gitlab.example.com`; Audience: `https://gitlab.example.com`; Subject: `project_path:my-group/my-project:...` | `{ "iss": "https://gitlab.example.com", "aud": "https://gitlab.example.com", "sub": "project_path:my-group/my-project:..." }` |
| **CircleCI** | Issuer: `https://oidc.circleci.com/org/<org_id>`; Audience: `<org_id>`; Subject: `7cc1d11b-46c8-4eb2-9482-4c56a910c7ce`; Subject claim: `oidc.circleci.com/project-id` | `{ "iss": "https://oidc.circleci.com/org/<org_id>", "aud": "<org_id>", "oidc.circleci.com/project-id": "7cc1d11b-46c8-4eb2-9482-4c56a910c7ce" }` |
| **AWS IAM Outbound Identity Federation** | Issuer: `https://<uuid>.tokens.sts.global.api.aws`; Audience: `databricks`; Subject: `arn:aws:iam::<account>:role/<role-name>` | `{ "iss": "https://<uuid>.tokens.sts.global.api.aws", "aud": ["databricks"], "sub": "arn:aws:iam::123456789012:role/my-workload-role" }` |

| Account-Federation-Policy | Beispiel-Token (passend) |
|---|---|
| Issuer: `https://idp.mycompany.com/oidc`; Audience: `2ff814a6-3304-4ab8-85cb-cd0e6f879c1d` | `{ "iss": "https://idp.mycompany.com/oidc", "aud": "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d", "sub": "username@mycompany.com" }` |
| Issuer: `https://idp.mycompany.com/oidc`; Audience: `2ff814a6-...`; Subject claim: `preferred_username` | `{ "iss": "https://idp.mycompany.com/oidc", "aud": ["2ff814a6-...", "other-audience"], "preferred_username": "username@mycompany.com", "sub": "some-other-ignored-value" }` |
| Issuer: `https://idp.mycompany.com/oidc`; Audience: `2ff814a6-...`; JWKS JSON: `{"keys":[{"kty":"RSA","e":"AQAB","use":"sig","kid":"<key-id>","alg":"RS256","n":"uPUViFv..."}]}` | `{ "iss": "...", "aud": "2ff814a6-...", "sub": "username@mycompany.com" }` (Signatur mit öffentlichem Schlüssel aus der Policy geprüft) |
| Issuer: `https://idp.mycompany.com/oidc`; Audience: `2ff814a6-...`; JWKS URI: `https://idp.mycompany.com/jwks.json` | `{ "iss": "...", "aud": "2ff814a6-...", "sub": "username@mycompany.com" }` (Signatur mit über `jwks_uri` geholtem öffentlichen Schlüssel geprüft) |

JWT-Body für eine Service-Principal-Federation-Policy (GitHub Actions):

```json
{
  "iss": "https://token.actions.githubusercontent.com",
  "aud": "https://github.com/my-github-org",
  "sub": "repo:my-github-org/my-repo:environment:prod"
}
```

Account-Admin am Databricks-Account anmelden:

```bash
databricks auth login --host ${ACCOUNT_CONSOLE_URL} --account-id ${ACCOUNT_ID}
```

Numerische Service-Principal-ID über die Application-ID (GUID) ermitteln:

```bash
databricks account service-principals list --filter 'applicationId eq "<service-principal-application-id>"'
```

Service-Principal-Federation-Policy anlegen (Databricks CLI, Beispiel GitHub Action):

```bash
databricks account service-principal-federation-policy create ${SERVICE_PRINCIPAL_NUMERIC_ID} --json '{
  "oidc_policy": {
    "issuer": "https://token.actions.githubusercontent.com",
    "audiences": [
      "https://github.com/my-github-org"
    ],
    "subject": "repo:my-github-org/my-repo:environment:prod"
  }
}'
```

Service-Principal-Federation-Policy über die Databricks Account API anlegen:

```bash
curl --request POST \
  --header "Authorization: Bearer $TOKEN" \
  "${ACCOUNT_CONSOLE_URL}/api/2.0/accounts/${ACCOUNT_ID}/servicePrincipals/${SERVICE_PRINCIPAL_NUMERIC_ID}/federationPolicies" \
  --data '{
    "oidc_policy": {
      "issuer": "https://token.actions.githubusercontent.com",
      "audiences": [
        "https://github.com/my-github-org"
      ],
      "subject": "repo:my-github-org/my-repo:environment:prod"
    }
  }'
```

JWT-Body für eine Account-Federation-Policy (account-weit):

```json
{
  "iss": "https://idp.mycompany.com/oidc",
  "aud": "databricks",
  "sub": "username@mycompany.com"
}
```

Account-Federation-Policy über die Databricks CLI anlegen:

```bash
databricks account federation-policy create --json '{
  "oidc_policy": {
    "issuer": "https://idp.mycompany.com/oidc",
    "audiences": [
      "databricks"
    ],
    "subject_claim": "sub"
  }
}'
```

Account-Federation-Policy über die Databricks Account API anlegen:

```bash
curl --request POST \
  --header "Authorization: Bearer $TOKEN" \
  "${ACCOUNT_CONSOLE_URL}/api/2.0/accounts/${ACCOUNT_ID}/federationPolicies" \
  --data '{
    "oidc_policy": {
      "issuer": "https://idp.mycompany.com/oidc",
      "audiences": [
        "databricks"
      ],
      "subject_claim": "sub"
    }
  }'
```

---

## 71. Workload Identity Federation in CI/CD aktivieren — Provider-Übersicht

**Einfach erklärt:** Diese Übersichtsseite erklärt, wie automatisierte Workloads außerhalb von Databricks (CI/CD-Pipelines) sich per OAuth Token Federation (OIDC) als Service Principal authentifizieren können, ganz ohne Databricks-Secrets. Databricks empfiehlt diesen Ansatz ausdrücklich vor allen anderen Methoden, weil er das Verwalten und Rotieren von Secrets überflüssig macht. Die Doku liefert konkrete Konfigurationsanleitungen für GitHub Actions, Azure DevOps Pipelines, AWS IAM Workloads, GitLab CI/CD, CircleCI, Jenkins, Terraform Cloud und Atlassian Bitbucket Pipelines.

| Provider | Detailseite in diesem Kapitel |
|---|---|
| GitHub Actions | 05 Provider — GitHub Actions |
| Azure DevOps Pipelines | 06 Provider — Azure DevOps |
| AWS IAM Workloads | 07 Provider — AWS IAM |
| GitLab CI/CD | 08 Provider — Terraform Cloud, Bitbucket, Jenkins |
| CircleCI | 08 Provider — Terraform Cloud, Bitbucket, Jenkins |
| Jenkins | 08 Provider — Terraform Cloud, Bitbucket, Jenkins |
| Terraform Cloud | 08 Provider — Terraform Cloud, Bitbucket, Jenkins |
| Atlassian Bitbucket Pipelines | 08 Provider — Terraform Cloud, Bitbucket, Jenkins |

Keine eigenen Code-Beispiele in dieser Datei — reiner Provider-Überblick (Details in den jeweiligen Unterseiten).

---

## 72. Provider: GitHub Actions

**Einfach erklärt:** Für GitHub Actions wird eine Federation Policy mit Issuer `https://token.actions.githubusercontent.com` angelegt, die Organisation, Repository und Entity-Type (empfohlen: Environment) festlegt. Im GitHub-Workflow werden dann drei Umgebungsvariablen gesetzt (`DATABRICKS_AUTH_TYPE=github-oidc`, `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`), und GitHub muss die Berechtigung `id-token: write` erteilen, damit überhaupt ein OIDC-Token ausgestellt wird. Für wiederverwendbare (reusable) Workflows muss der `subject_claim` in der Policy auf `job_workflow_ref` gesetzt werden, und `id-token: write` darf nur im aufrufenden Workflow gesetzt werden, damit GitHub den `job_workflow_ref`-Claim überhaupt ins Token aufnimmt.

Beispiel: Federation Policy für einen GitHub-Actions-Workload anlegen:

```bash
databricks account service-principal-federation-policy create 5581763342009999 --json '{
  "oidc_policy": {
    "issuer": "https://token.actions.githubusercontent.com",
    "audiences": [
      "a2222dd9-33f6-455z-8888-999fbbd77900"
    ],
    "subject": "repo:my-github-org/my-repo:environment:prod"
  }
}'
```

Basis-Workflow:

```yaml
name: GitHub Actions Demo
run-name: ${{ github.actor }} is testing out GitHub Actions 🚀
on: workflow_dispatch
permissions:
  id-token: write
  contents: read
jobs:
  my_script_using_wif:
    runs-on: ubuntu-latest
    environment: prod
    env:
      DATABRICKS_AUTH_TYPE: github-oidc
      DATABRICKS_HOST: https://my-workspace.cloud.databricks.com/
      DATABRICKS_CLIENT_ID: a1b2c3d4-ee42-1eet-1337-f00b44r
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Install Databricks CLI
        uses: databricks/setup-cli@main
      - name: Run Databricks CLI commands
        run: databricks current-user me
```

Federation Policy für einen Reusable Workflow (mit `subject_claim: job_workflow_ref`):

```bash
databricks account service-principal-federation-policy create 5581763342009999 --json '{
  "oidc_policy": {
    "issuer": "https://token.actions.githubusercontent.com",
    "audiences": [
      "a2222dd9-33f6-455z-8888-999fbbd77900"
    ],
    "subject": "my-github-org/shared-workflows/.github/workflows/deploy.yml@refs/heads/main",
    "subject_claim": "job_workflow_ref"
  }
}'
```

Reusable-Workflow-Datei (`deploy.yml`):

```yaml
on:
  workflow_call:
jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      DATABRICKS_AUTH_TYPE: github-oidc
      DATABRICKS_HOST: https://my-workspace.cloud.databricks.com/
      DATABRICKS_CLIENT_ID: a1b2c3d4-ee42-1eet-1337-f00b44r
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Install Databricks CLI
        uses: databricks/setup-cli@main
      - name: Run Databricks CLI commands
        run: databricks current-user me
```

Aufrufender Workflow (Calling Workflow):

```yaml
on: workflow_dispatch
permissions:
  id-token: write
  contents: read
jobs:
  call-deploy:
    uses: my-github-org/shared-workflows/.github/workflows/deploy.yml@main
```

Quelle: https://docs.databricks.com/aws/en/dev-tools/auth/provider-github

---

## 73. Provider: Azure DevOps Pipelines

**Einfach erklärt:** Für Azure DevOps Pipelines wird eine Federation Policy mit Issuer `https://vstoken.dev.azure.com/<org_id>` (GUID der Azure-DevOps-Organisation), Audience `api://AzureADTokenExchange` und Subject im Format `p://<org-name>/<project-name>/<pipeline-name>` angelegt. In der Pipeline-YAML werden `DATABRICKS_AUTH_TYPE=azure-devops-oidc`, `DATABRICKS_HOST` und `DATABRICKS_CLIENT_ID` als Variablen gesetzt; zusätzlich muss `SYSTEM_ACCESSTOKEN` explizit im `env:`-Block des Steps auf `$(System.AccessToken)` gemappt werden, da Azure DevOps dieses Token sonst nicht als Umgebungsvariable bereitstellt.

Beispiel: Federation Policy anlegen:

```bash
databricks account service-principal-federation-policy create 5581763342009999 --json '{
  "oidc_policy": {
    "issuer": "https://vstoken.dev.azure.com/7f1078d6-b20d-4a20-9d88-05a2f0d645a3",
    "audiences": [
      "api://AzureADTokenExchange"
    ],
    "subject": "p://my-org/my-project/my-pipeline"
  }
}'
```

Beispiel-Pipeline-YAML:

```yaml
trigger: none
pool: test # Name des selbst-gehosteten Pools
variables:
  DATABRICKS_HOST: https://my-workspace.cloud.databricks.com/
  DATABRICKS_AUTH_TYPE: azure-devops-oidc
  DATABRICKS_CLIENT_ID: a1b2c3d4-ee42-1eet-1337-f00b44r
steps:
  - script: |
      databricks current-user me
    displayName: 'Display Databricks current user information'
    env:
      SYSTEM_ACCESSTOKEN: $(System.AccessToken)
```

Quelle: https://docs.databricks.com/aws/en/dev-tools/auth/provider-azure-devops

---

## 74. Provider: AWS IAM Workloads

**Einfach erklärt:** Für Workloads, die mit einer AWS-IAM-Rolle laufen (Lambda, EC2, ECS, EKS), wird zunächst in AWS "Outbound Web Identity Federation" aktiviert und der Workload-Rolle die Berechtigung `sts:GetWebIdentityToken` gewährt (Tokens nur für Audience `databricks`, max. 300–3600 Sekunden Lebensdauer). Danach wird die account-spezifische Issuer-URL (`https://<uuid>.tokens.sts.global.api.aws`) ermittelt und eine Databricks-Federation-Policy auf Account-Ebene angelegt, wobei der `sub`-Claim der IAM-Rollen-ARN ist. Zur Authentifizierung liefert das Databricks-SDK-for-Python-Beispiel ein `IdTokenSource`-Muster, das ein AWS-STS-Token holt und automatisch gegen ein Databricks-OAuth-Token tauscht — komplett ohne Secrets.

Schritt 1: AWS IAM Outbound Identity Federation aktivieren:

```python
import boto3
boto3.client('iam').enable_outbound_web_identity_federation()
```

Schritt 2: Berechtigung `sts:GetWebIdentityToken` gewähren:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["sts:GetWebIdentityToken"],
      "Resource": "*",
      "Condition": {
        "ForAllValues:StringEquals": {
          "sts:IdentityTokenAudience": "databricks"
        },
        "NumericLessThanEquals": {
          "sts:DurationSeconds": 300
        }
      }
    }
  ]
}
```

Schritt 3: Account-spezifische Issuer-URL notieren:

```python
import boto3
info = boto3.client('iam').get_outbound_web_identity_federation_info()
print(info['IssuerUrl'])  # https://<uuid>.tokens.sts.global.api.aws
```

Federation Policy erstellen (auf Account-Ebene, Host `https://accounts.cloud.databricks.com`, Account-Admin erforderlich):

```bash
databricks account service-principal-federation-policy create ${SP_ID} --json '{
  "oidc_policy": {
    "issuer": "https://<uuid>.tokens.sts.global.api.aws",
    "audiences": ["databricks"],
    "subject": "arn:aws:iam::<account-id>:role/<workload-role-name>"
  }
}'
```

Bei Databricks authentifizieren (Databricks SDK for Python, `IdTokenSource`-Muster):

```python
import boto3
from databricks.sdk import WorkspaceClient
from databricks.sdk import oidc
from databricks.sdk.core import Config, credentials_strategy, oidc_credentials_provider

class AwsStsTokenSource(oidc.IdTokenSource):
    def __init__(self, audience="databricks", region="us-east-1"):
        self._audience = audience
        self._region = region

    def id_token(self) -> oidc.IdToken:
        sts = boto3.client("sts", region_name=self._region)
        resp = sts.get_web_identity_token(
            Audience=[self._audience],
            SigningAlgorithm="RS256",
            DurationSeconds=300,
        )
        return oidc.IdToken(jwt=resp["WebIdentityToken"])

@credentials_strategy("aws-sts-wif", [])
def aws_sts_wif_strategy(cfg: Config):
    return oidc_credentials_provider(cfg, AwsStsTokenSource())

w = WorkspaceClient(
    host="https://my-workspace.cloud.databricks.com",
    client_id="<service-principal-uuid>",
    credentials_strategy=aws_sts_wif_strategy)

# Keine Secrets nötig
clusters = w.clusters.list()
```

Quelle: https://docs.databricks.com/aws/en/dev-tools/auth/provider-aws-iam

---

## 75. Provider: Terraform Cloud, Bitbucket Pipelines, Jenkins (und generische OIDC-Provider)

**Einfach erklärt:** Für CI/CD-Werkzeuge ohne eigene Databricks-spezifische Integration (Terraform Cloud, Bitbucket Pipelines, Jenkins, GitLab) wird eine generische Workload-Identity-Federation-Policy mit Issuer-URL, Audience und Subject des jeweiligen Providers angelegt. Anschließend wird der Databricks-Auth-Typ auf `env-oidc` (Token liegt in einer Umgebungsvariable) oder `file-oidc` (Token liegt in einer Datei) gesetzt. Terraform Cloud liefert sein Token z. B. in `TFC_WORKLOAD_IDENTITY_TOKEN`, Jenkins über `DATABRICKS_OIDC_TOKEN` oder eine Token-Datei, und Bitbucket Pipelines aktiviert `oidc: true` im Step, wodurch das Token in `BITBUCKET_STEP_OIDC_TOKEN` erscheint.

Beispiel (GitLab): Federation Policy anlegen:

```bash
databricks account service-principal-federation-policy create 5581763342009999 --json '{
  "oidc_policy": {
    "issuer": "https://gitlab.com/example-group",
    "audiences": [
      "https://gitlab.com/example-group"
    ],
    "subject": "project_path:my-group/my-project:..."
  }
}'
```

Terraform Cloud (Workload-Identity-Token-Umgebungsvariable):

```
DATABRICKS_OIDC_TOKEN_ENV = TFC_WORKLOAD_IDENTITY_TOKEN
```

Bitbucket Pipelines:

```yaml
image: atlassian/default-image:3
pipelines:
  default:
    - step:
        oidc: true
        script:
          - export DATABRICKS_CLIENT_ID=a1b2c3d4-ee42-1eet-1337-f00b44r
          - export DATABRICKS_HOST=https://my-workspace.cloud.databricks.com/
          - export DATABRICKS_OIDC_TOKEN_ENV=BITBUCKET_STEP_OIDC_TOKEN
          - export DATABRICKS_AUTH_TYPE=env-oidc
          - curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
          - databricks --version
          - databricks current-user me
```

Quelle: https://docs.databricks.com/aws/en/dev-tools/auth/provider-other

---

## 76. Mit einem IdP-Token authentifizieren (Token Exchange)

**Einfach erklärt:** Diese Seite beschreibt, wie ein föderierter Identity-Token (JWT) technisch gegen ein Databricks-OAuth-Token getauscht wird — automatisch über SDK/CLI (Databricks OAuth 2.0 Token Exchange) oder manuell per `curl`. Notwendig sind eine vorhandene Federation Policy und ein gültiger JWT (signiert mit RS256 oder ES256). Die Konfiguration erfolgt über Umgebungsvariablen oder `.databrickscfg`-Felder (`auth_type=env-oidc`/`file-oidc`, `oidc_token_env`, `oidc_token_filepath`). Für Sonderfälle können auch benutzerdefinierte Authorization Provider implementiert werden (Python, Java, Go), die ein eigenes `IdTokenSource`/`IDTokenSource` bereitstellen.

Umgebungsvariablen:

```bash
export DATABRICKS_HOST=<workspace-url-or-account-console-url>
export DATABRICKS_ACCOUNT_ID=<account-id>
export DATABRICKS_CLIENT_ID=<client-id>
export DATABRICKS_AUTH_TYPE=<auth-method>
export DATABRICKS_OIDC_TOKEN_ENV=<token-env-name>
export DATABRICKS_OIDC_TOKEN_FILEPATH=<token-filepath-name>
```

`.databrickscfg`-Profil:

```ini
[<profile-name>]
host = <workspace-url-or-account-console-url>
account_id = <account-id>
client_id = <client-id>
auth_type = <auth-method>
oidc_token_env = <token-env-name>
oidc_token_filepath = <token-filepath-name>
```

Zugriff auf Databricks-APIs — CLI:

```bash
databricks clusters list
```

Python:

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
clusters = w.clusters.list()
```

Java:

```java
import com.databricks.sdk.WorkspaceClient;
WorkspaceClient w = new WorkspaceClient();
List<ClusterDetails> clusters = w.clusters().list();
```

Go:

```go
import "github.com/databricks/databricks-sdk-go"
w := databricks.Must(databricks.NewWorkspaceClient())
clusters := w.Clusters.ListAll(context.Background(), compute.List{})
```

Benutzerdefinierter Authorization Provider für AWS-IAM-Workloads (Python):

```python
import boto3
from databricks.sdk import WorkspaceClient
from databricks.sdk import oidc
from databricks.sdk.core import Config, credentials_strategy, oidc_credentials_provider

class AwsStsTokenSource(oidc.IdTokenSource):
    def __init__(self, audience="databricks", region="us-east-1"):
        self._audience = audience
        self._region = region

    def id_token(self) -> oidc.IdToken:
        sts = boto3.client("sts", region_name=self._region)
        resp = sts.get_web_identity_token(
            Audience=[self._audience],
            SigningAlgorithm="RS256",
            DurationSeconds=300,
        )
        return oidc.IdToken(jwt=resp["WebIdentityToken"])

@credentials_strategy("aws-sts-wif", [])
def aws_sts_wif_strategy(cfg: Config):
    return oidc_credentials_provider(cfg, AwsStsTokenSource())

w = WorkspaceClient(
    host="https://my-workspace.cloud.databricks.com",
    client_id="<service-principal-uuid>",
    credentials_strategy=aws_sts_wif_strategy)

clusters = w.clusters.list()
```

Roher Token-Austausch (Python):

```python
import boto3
import requests

sts = boto3.client("sts", region_name="us-east-1")
resp = sts.get_web_identity_token(
    Audience=["databricks"],
    SigningAlgorithm="RS256",
    DurationSeconds=300,
)
aws_jwt = resp["WebIdentityToken"]

token_resp = requests.post(
    "https://<workspace>.cloud.databricks.com/oidc/v1/token",
    data={
        "client_id": "<service-principal-uuid>",
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": aws_jwt,
        "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "scope": "all-apis",
    },
)
access_token = token_resp.json()["access_token"]
```

Generische benutzerdefinierte Implementierung (Python):

```python
from databricks.sdk import oidc
from databricks.sdk.core import (Config, CredentialsProvider, credentials_strategy, oidc_credentials_provider)

class MyCustomIdTokenSource(oidc.IdTokenSource):
    def id_token(self) -> oidc.IdToken:
        token = ...
        return oidc.IdToken(jwt=token)

@credentials_strategy("my-custom-oidc", [])
def my_custom_oidc_strategy(cfg: Config) -> CredentialsProvider:
    return oidc_credentials_provider(cfg, MyCustomIdTokenSource())

if __name__ == "__main__":
    cfg = Config(
        host="https://my-workspace.cloud.databricks.com",
        credentials_strategy=my_custom_oidc_strategy
    )
    from databricks.sdk import WorkspaceClient
    w = WorkspaceClient(config=cfg)
```

Generische benutzerdefinierte Implementierung (Java):

```java
import com.databricks.sdk.WorkspaceClient;
import com.databricks.sdk.core.DatabricksConfig;
import com.databricks.sdk.core.CredentialsProvider;
import com.databricks.sdk.core.oauth.IDTokenSource;
import com.databricks.sdk.core.oauth.IDToken;

public class CustomOIDCExample {
    static class MyCustomIdTokenSource implements IDTokenSource {
        @Override
        public IDToken getIDToken(String audience) {
            String jwt = "...";
            return new IDToken(jwt);
        }
    }

    public static void main(String[] args) {
        CredentialsProvider provider = ...;
        DatabricksConfig cfg = new DatabricksConfig()
            .setHost("https://my-workspace.cloud.databricks.com")
            .setCredentialsProvider(provider);
        WorkspaceClient w = new WorkspaceClient(cfg);
        System.out.println("Databricks client initialized: " + w);
    }
}
```

Generische benutzerdefinierte Implementierung (Go):

```go
package main

import (
    "context"
    "fmt"
    "github.com/databricks/databricks-sdk-go"
    "github.com/databricks/databricks-sdk-go/config"
    "github.com/databricks/databricks-sdk-go/credentials"
)

type MyCustomIdTokenSource struct{}

func (s *MyCustomIdTokenSource) IDToken(ctx context.Context) (*credentials.IDToken, error) {
    token := "..."
    return &credentials.IDToken{JWT: token}, nil
}

func myCustomOIDCStrategy(cfg *config.Config) (credentials.CredentialsProvider, error) {
    return credentials.NewOIDCCredentialsProvider(cfg, &MyCustomIdTokenSource{}), nil
}

func main() {
    cfg := &config.Config{
        Host: "https://my-workspace.cloud.databricks.com",
    }
    credentials.Register("my-custom-oidc", myCustomOIDCStrategy)
    w, err := databricks.NewWorkspaceClientWithConfig(cfg)
    if err != nil {
        panic(err)
    }
    fmt.Println("Databricks client initialized:", w)
}
```

Manueller Token-Austausch — Account-weite Federation Policies:

```bash
curl --request POST https://<databricks-workspace-host>/oidc/v1/token \
  --data "subject_token=${FEDERATED_JWT_TOKEN}" \
  --data 'subject_token_type=urn:ietf:params:oauth:token-type:jwt' \
  --data 'grant_type=urn:ietf:params:oauth:grant-type:token-exchange' \
  --data 'scope=all-apis'
```

Manueller Token-Austausch — Service-Principal-Federation-Policies:

```bash
curl --request POST https://<databricks-workspace-host>/oidc/v1/token \
  --data "client_id=${CLIENT_ID}" \
  --data "subject_token=${FEDERATED_JWT_TOKEN}" \
  --data 'subject_token_type=urn:ietf:params:oauth:token-type:jwt' \
  --data 'grant_type=urn:ietf:params:oauth:grant-type:token-exchange' \
  --data 'scope=all-apis'
```

Beispiel-Antwort (Token-Austausch):

```json
{
  "access_token": "eyJraWQ...odi0WFNqQw",
  "scope": "all-apis",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

OAuth-Token zum Aufruf von Databricks-APIs verwenden:

```bash
TOKEN='<your-databricks-oauth-token>'
curl --header "Authorization: Bearer $TOKEN" \
  --url https://${DATABRICKS_WORKSPACE_HOSTNAME}/api/2.0/preview/scim/v2/Me
```

Beispiel-Antwort:

```json
{
  "userName": "username@mycompany.com",
  "displayName": "Firstname Lastname"
}
```

Quelle: https://docs.databricks.com/aws/en/dev-tools/auth/oauth-federation-exchange

---

## 77. OAuth U2M — Benutzerzugriff autorisieren

**Einfach erklärt:** OAuth 2.0 User-to-Machine (U2M) ist der bevorzugte Weg, wie einzelne Benutzer sich interaktiv gegenüber Databricks-Entwicklerwerkzeugen und -APIs authentifizieren. Jedes Access-Token gilt eine Stunde und wird danach automatisch erneuert. Der **automatische** Weg nutzt Unified Authentication mit kompatiblen Werkzeugen (CLI, Terraform, SDKs); der **manuelle** Weg (für Drittanbieter-Tools ohne Unified-Auth-Unterstützung) folgt dem klassischen OAuth-Authorization-Code-Flow mit PKCE (Code-Verifier/Code-Challenge, Authorization Code, Token-Austausch). Zusätzlich existiert eine Beta-Funktion zur Service-Principal-Authentifizierung im OAuth-Flow sowie APIs zum Anzeigen/Widerrufen von erteiltem OAuth-Consent.

Umgebungsvariablen — Account-Ebene:

```bash
DATABRICKS_HOST=https://accounts.cloud.databricks.com
DATABRICKS_ACCOUNT_ID=<your-account-id>
```

Umgebungsvariablen — Workspace-Ebene:

```bash
DATABRICKS_HOST=https://dbc-a1b2345c-d6e7.cloud.databricks.com
```

Konfigurationsprofil (`.databrickscfg`) — Account-Ebene:

```ini
[profile-name]
host=https://accounts.cloud.databricks.com
account_id=<account-id>
```

Konfigurationsprofil — Workspace-Ebene:

```ini
[profile-name]
host=<workspace-url>
```

Manuelle OAuth-Token-Generierung — Schritt 1: Code-Verifier und Code-Challenge erzeugen (PKCE):

```python
import hashlib, base64, secrets, string

allowed_chars = string.ascii_letters + string.digits + "-._~"
code_verifier = ''.join(secrets.choice(allowed_chars) for _ in range(64))
sha256_hash = hashlib.sha256(code_verifier.encode()).digest()
code_challenge = base64.urlsafe_b64encode(sha256_hash).decode().rstrip("=")

print(f"code_verifier:  {code_verifier}")
print(f"code_challenge: {code_challenge}")
```

Schritt 2: Authorization Code erzeugen — Account-Ebene (Aufruf-URL):

```
https://accounts.cloud.databricks.com/oidc/accounts/<account-id>/v1/authorize?client_id=databricks-cli&redirect_uri=<redirect-url>&response_type=code&state=<state>&code_challenge=<code-challenge>&code_challenge_method=S256&scope=all-apis+offline_access
```

Workspace-Ebene:

```
https://<databricks-instance>/oidc/v1/authorize?client_id=databricks-cli&redirect_uri=<redirect-url>&response_type=code&state=<state>&code_challenge=<code-challenge>&code_challenge_method=S256&scope=all-apis+offline_access
```

Schritt 3: Code gegen Access-Token tauschen — Account-Ebene:

```bash
curl --request POST \
https://accounts.cloud.databricks.com/oidc/accounts/<account-id>/v1/token \
--data "client_id=databricks-cli" \
--data "grant_type=authorization_code" \
--data "scope=all-apis offline_access" \
--data "redirect_uri=<redirect-url>" \
--data "code_verifier=<code-verifier>" \
--data "code=<authorization-code>"
```

Workspace-Ebene:

```bash
curl --request POST \
https://<databricks-instance>/oidc/v1/token \
--data "client_id=databricks-cli" \
--data "grant_type=authorization_code" \
--data "scope=all-apis offline_access" \
--data "redirect_uri=<redirect-url>" \
--data "code_verifier=<code-verifier>" \
--data "code=<authorization-code>"
```

Schritt 4: API-Anfragen — Account-Ebene:

```bash
export OAUTH_TOKEN=<oauth-access-token>
curl --request GET --header "Authorization: Bearer $OAUTH_TOKEN" \
"https://accounts.cloud.databricks.com/api/2.0/accounts/<account-id>/workspaces"
```

Workspace-Ebene:

```bash
export OAUTH_TOKEN=<oauth-access-token>
curl --request GET --header "Authorization: Bearer $OAUTH_TOKEN" \
"https://<databricks-instance>/api/2.0/clusters/list"
```

OAuth-Consent verwalten — genehmigte Scopes anzeigen:

```bash
curl --request GET \
  --header "Authorization: Bearer $OAUTH_TOKEN" \
  "https://<databricks-instance>/api/2.0/oauth-app-integrations/<app-integration-id>/user-consent/me"
```

Consent widerrufen:

```bash
curl --request DELETE \
  --header "Authorization: Bearer $OAUTH_TOKEN" \
  "https://<databricks-instance>/api/2.0/oauth-app-integrations/<app-integration-id>/user-consent/me"
```

Quelle: https://docs.databricks.com/aws/en/dev-tools/auth/oauth-u2m

---

## 78. Service Principals für CI/CD

**Einfach erklärt:** Ein Service Principal ist eine eigene Identität für automatisierte Werkzeuge und Anwendungen — empfohlen für CI/CD-Plattformen wie GitHub Actions, Azure Pipelines, GitLab CI/CD, Airflow und Jenkins. Vorteile gegenüber persönlichen Access-Tokens von Benutzern: unabhängige Zugriffssteuerung, Benutzer müssen ihre eigenen Tokens nicht offenlegen, einfaches Deaktivieren/Löschen ohne andere zu beeinträchtigen, und Unabhängigkeit von organisatorischen Änderungen (z. B. wenn Mitarbeitende das Unternehmen verlassen). Setup: Service Principal erstellen, Access-Token generieren, Token als verschlüsseltes Secret in der CI/CD-Plattform hinterlegen. Alternative zu langlebigen Tokens: OAuth Token Federation ohne Secrets.

| Secret/Variable | Wert |
|---|---|
| `DATABRICKS_HOST` | `https://` + Workspace-Instanzname |
| `DATABRICKS_TOKEN` | `token_value` des Service Principals |

GitHub-Actions-Workflow (PAT-Authentifizierung über Secrets):

```yaml
name: Run Databricks CLI
on:
  push:
    branches: [main]
jobs:
  databricks:
    runs-on: ubuntu-latest
    env:
      DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
      DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
    steps:
      - uses: actions/checkout@v4
      - name: Install Databricks CLI
        uses: databricks/setup-cli@main
      - name: Verify authentication
        run: databricks current-user me
```

GitLab-CI/CD (`.gitlab-ci.yml`):

```yaml
databricks:
  image: ubuntu:latest
  variables:
    DATABRICKS_HOST: $DATABRICKS_HOST
    DATABRICKS_TOKEN: $DATABRICKS_TOKEN
  script:
    - curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
    - databricks current-user me
```

Quelle: https://docs.databricks.com/aws/en/dev-tools/auth/service-principals

---

## 79. Databricks Unified Authentication

**Einfach erklärt:** Unified Authentication gibt Databricks-CLI, Terraform Provider, Databricks Connect, der VS-Code-Erweiterung sowie den SDKs für Python, Java und Go einen konsistenten Weg, Credentials einmal zu definieren und über alle Werkzeuge hinweg zu nutzen. Beim Auflösen der Authentifizierung werden zuerst die Methoden in fester Reihenfolge durchprobiert (1. Personal Access Tokens/Legacy, 2. OAuth M2M, 3. OAuth U2M), und für jede Methode wird in dieser Reihenfolge nach Credentials gesucht: SDK-`Config`-Felder im Code, dann Umgebungsvariablen, dann das `DEFAULT`-Profil in `.databrickscfg`. Best Practice: eigenes Konfigurationsprofil anlegen und über die Umgebungsvariable `DATABRICKS_CONFIG_PROFILE` referenzieren.

Keine Code-Beispiele in dieser Datei — reine Konzept-/Reihenfolgenbeschreibung.

Quelle: https://docs.databricks.com/aws/en/dev-tools/auth/unified-auth

---

## 80. Umgebungsvariablen und Felder für Unified Authentication

**Einfach erklärt:** Diese Referenzseite listet alle Konfigurationsfelder, die einheitlich über Databricks CLI, Terraform Provider und die SDKs für Python, Java und Go funktionieren — jeweils als Umgebungsvariable, `.databrickscfg`-/Terraform-Feld und SDK-`Config`-Feld. Dazu gehören allgemeine Felder (Host, Token, Account-ID, Cluster-ID), Benutzer-/Service-Principal-Felder (Username, Client-ID, Client-Secret), `.databrickscfg`-spezifische Felder (Config-Dateipfad, Profilname) und Auth-Typ-Felder zum Erzwingen einer bestimmten Methode.

| Gebräuchlicher Name | Beschreibung | Umgebungsvariable | `.databrickscfg`- / Terraform-Feld | `Config`-Feld |
|---|---|---|---|---|
| Databricks host | Host-URL des Workspace- oder Account-Endpunkts | `DATABRICKS_HOST` | `host` | `host` (Python), `setHost` (Java), `Host` (Go) |
| Databricks token | Databricks Personal Access Token | `DATABRICKS_TOKEN` | `token` | `token` (Python), `setToken` (Java), `Token` (Go) |
| Databricks account ID | Account-ID für den Account-Endpunkt | `DATABRICKS_ACCOUNT_ID` | `account_id` | `account_id` (Python), `setAccountID` (Java), `AccountID` (Go) |
| Cluster ID | ID des zu verwendenden Clusters | `DATABRICKS_CLUSTER_ID` | `cluster_id` | `cluster_id` |
| Serverless compute | Auto-Enablement für Serverless Compute (`auto`) | `DATABRICKS_SERVERLESS_COMPUTE_ID` | `serverless_compute_id` | `serverless_compute_id` |
| Databricks username | Benutzername des Databricks-Benutzers | `DATABRICKS_USERNAME` | `username` | `username` (Python), `setUsername` (Java), `Username` (Go) |
| Service principal client ID | Client-ID des Service Principals | `DATABRICKS_CLIENT_ID` | `client_id` | `client_id` (Python), `setClientId` (Java), `ClientId` (Go) |
| Service principal secret | Secret des Service Principals | `DATABRICKS_CLIENT_SECRET` | `client_secret` | `client_secret` (Python), `setClientSecret` (Java), `ClientSecret` (Go) |
| `.databrickscfg`-Dateipfad | Nicht-Standard-Pfad zur `.databrickscfg`-Datei | `DATABRICKS_CONFIG_FILE` | `config_file` | `config_file` (Python), `setConfigFile` (Java), `ConfigFile` (Go) |
| `.databrickscfg`-Default-Profil | Zu verwendendes Default-Profil (statt `DEFAULT`) | `DATABRICKS_CONFIG_PROFILE` | `profile` | `profile` (Python), `setProfile` (Java), `Profile` (Go) |
| Databricks authentication type | Erzwingt einen bestimmten Auth-Typ | `DATABRICKS_AUTH_TYPE` | `auth_type` | `auth_type` (Python), `setAuthType` (Java), `AuthType` (Go) |
| OIDC token environment variable | Name der Variable mit dem IdP-OIDC-Token (`env-oidc`), Default `DATABRICKS_OIDC_TOKEN` | `DATABRICKS_OIDC_TOKEN_ENV` | `oidc_token_env` | `oidc_token_env` (Python), `setOIDCTokenEnv` (Java), `OIDCTokenEnv` (Go) |
| OIDC token file path | Pfad zu einer Datei mit dem IdP-OIDC-Token (`file-oidc`) | `DATABRICKS_OIDC_TOKEN_FILEPATH` | `oidc_token_filepath` | `oidc_token_filepath` (Python), `setOIDCTokenFilepath` (Java), `OIDCTokenFilepath` (Go) |

Gültige Werte für `auth_type` / `DATABRICKS_AUTH_TYPE`:

| Wert | Bedeutung |
|---|---|
| `oauth-m2m` | Machine-to-Machine-Authentifizierung mit einem Service Principal über OAuth 2.0 |
| `pat` | Authentifizierung mit einem Databricks Personal Access Token |
| `databricks-cli` | Interaktive Anmeldung mit der Databricks CLI über OAuth 2.0 |
| `oidc-token` | Token Federation mit einem IdP (OIDC-Token gegen Databricks-OAuth-Token) |
| `env-oidc` | Federation, IdP-Token liegt in einer Umgebungsvariable (`DATABRICKS_OIDC_TOKEN`) |
| `file-oidc` | Federation, IdP-Token liegt in einer lokalen Datei (`DATABRICKS_OIDC_TOKEN_FILEPATH`) |
| `github-oidc` | Föderierte GitHub-Actions-Authentifizierung über OIDC-Tokens |
| `azure-devops-oidc` | Föderierte Azure-DevOps-Authentifizierung über OIDC-Tokens |

Keine eigenständigen Codeblöcke in dieser Datei — reine Referenztabellen.

Quelle: https://docs.databricks.com/aws/en/dev-tools/auth/env-vars

---

## 81. Konfigurationsprofile (`.databrickscfg`)

**Einfach erklärt:** Konfigurationsprofile speichern Authentifizierungs-Credentials, die Workspace-/Account-URL und optionale Einstellungen in der Datei `.databrickscfg`, sodass zwischen Workspaces, Umgebungen oder Auth-Methoden gewechselt werden kann, ohne Code zu ändern. Profile lassen sich per `databricks auth login` oder manuell anlegen; mehrere benannte Profile (z. B. `DEFAULT`, `DEVELOPMENT`, `STAGING`) können in derselben Datei koexistieren und über CLI-Flag `--profile`, die Umgebungsvariable `DATABRICKS_CONFIG_PROFILE` oder den SDK-Parameter `profile=` ausgewählt werden. Best Practices: `DEFAULT` für den Hauptworkspace, sprechende Profilnamen, restriktive Dateiberechtigungen, `.gitignore`, Service Principals für Produktion, regelmäßige Credential-Rotation.

Profil über die CLI erstellen:

```bash
databricks auth login --host <workspace-url>
```

Manuelles Profil-Format:

```ini
[<profile-name>]
<field-name> = <field-value>
```

Beispiel: OAuth M2M:

```ini
[DEFAULT]
host          = https://<workspace-url>
client_id     = <client-id>
client_secret = <client-secret>
```

Mehrere Profile:

```ini
[DEFAULT]
host          = https://production-workspace-url
client_id     = <production-client-id>
client_secret = <production-client-secret>

[DEVELOPMENT]
host          = https://dev-workspace-url
client_id     = <dev-client-id>
client_secret = <dev-client-secret>

[STAGING]
host          = https://staging-workspace-url
client_id     = <staging-client-id>
client_secret = <staging-client-secret>
```

Profile verwenden — CLI:

```bash
databricks workspace list --profile DEVELOPMENT
```

Umgebungsvariable:

```bash
export DATABRICKS_CONFIG_PROFILE=DEVELOPMENT
databricks workspace list
```

Python SDK:

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient(profile="DEVELOPMENT")
```

Profile testen:

```bash
# Ein bestimmtes Profil inspizieren
databricks auth env --profile DEVELOPMENT

# Alle Profile auflisten
databricks auth profiles
```

Quelle: https://docs.databricks.com/aws/en/dev-tools/auth/config-profiles

---

## 82. Personal Access Tokens (PAT) — Legacy

**Einfach erklärt:** Personal Access Tokens (PATs) sind der klassische, ältere Weg zur Authentifizierung auf Workspace-Ebene — Databricks empfiehlt inzwischen OAuth statt PATs für stärkere Sicherheit. Jeder PAT gilt für genau einen Workspace, es sind bis zu 600 PATs pro Workspace und Benutzer erlaubt, ungenutzte PATs werden automatisch nach 90 Tagen widerrufen, und PATs können keine Account-Level-Funktionalität automatisieren. Es gibt Scoped Tokens (Berechtigung auf bestimmte API-Bereiche wie `sql`, `unity-catalog`, `scim` beschränkt) und Auto-Scoping (beobachtet 30 Tage API-Nutzung und verengt automatisch die Scopes bestehender oder neuer langlebiger Tokens, mit Erinnerungsmail 7 Tage vor Durchsetzung). Für Service Principals werden PATs über den Befehl `databricks token-management create-obo-token` (erster Token, als Workspace-Admin) bzw. `databricks tokens create` (weitere Tokens) erzeugt.

Auto-scoping deaktivieren (Scopes manuell setzen):

```bash
PATCH /api/2.0/token/{token_id_sha256}
```

Ersten PAT für den Service Principal erstellen:

```bash
databricks token-management create-obo-token \
  <application-id> \
  --lifetime-seconds <lifetime-seconds> \
  -p <profile-name>
```

Weitere PATs für den Service Principal erstellen:

```bash
databricks tokens create \
  --lifetime-seconds <lifetime-seconds> \
  -p <profile-name>
```

Umgebungsvariablen für PAT-Authentifizierung:

```bash
DATABRICKS_HOST=https://dbc-a1b2345c-d6e7.cloud.databricks.com
DATABRICKS_TOKEN=<token-string>
```

Konfigurationsprofil:

```ini
[<some-unique-configuration-profile-name>]
host  = <workspace-url>
token = <token>
```

Databricks CLI konfigurieren:

```bash
databricks configure --profile DEFAULT
```

Databricks Connect mit Cluster-Auswahl konfigurieren:

```bash
databricks configure \
  --configure-cluster \
  --profile DEFAULT
```

PAT über die REST-API erstellen (`/api/2.0/token/create`):

```bash
curl -X POST https://<databricks-instance>/api/2.0/token/create \
  -H "Authorization: Bearer <your-existing-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
  "lifetime_seconds": <lifetime-seconds>,
  "scopes": [
    "sql",
    "authentication"
  ],
  "autoscope_enabled": true
}'
```

Erfolgreiche Antwort:

```json
{
  "token_value": "<your-newly-issued-pat>",
  "token_info": {
    "token_id": "<token-id>",
    "creation_time": <creation-timestamp>,
    "expiry_time": <expiry-timestamp>,
    "comment": "<comment>",
    "scopes": ["authentication", "sql"],
    "last_accessed_time": 0
  }
}
```

Neues Token verwenden — Bash:

```bash
curl -X GET "https://<databricks-instance>/api/2.0/<path-to-endpoint>" \
  -H "Authorization: Bearer <your-new-pat>"
```

Python:

```python
import requests

headers = {
    'Authorization': 'Bearer <your-new-pat>'
}

# Beispiel für eine HTTP-GET-Operation.
response = requests.get('https://<databricks-instance>/api/2.0/<path-to-endpoint>', headers=headers)
```

Token-Scopes aktualisieren (`/api/2.0/token/<token_id>`):

```bash
curl -X PATCH https://<databricks-instance>/api/2.0/token/<token_id> \
  -H "Authorization: Bearer <your-existing-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
  "token": {
    "scopes": ["sql", "unity-catalog"]
  },
  "update_mask": "scopes"
}'
```

Alle verfügbaren Scopes anzeigen:

```
GET /api/2.0/token-scopes
```

Quelle: https://docs.databricks.com/aws/en/dev-tools/auth/pat


---

## 83. Blog: Arrow-optimierte Python-UDFs (Performance)

**Einfach erklärt:** Session-scoped Python-Scalar-UDFs (Abschnitt 51) lassen sich durch Apache Arrow statt der klassischen Pickle-Serialisierung beschleunigen — analog zu UDTFs (`useArrow=True`, siehe Abschnitt 53) und Pandas-UDFs (Abschnitt 52), die Arrow bereits standardmäßig nutzen. Arrow speichert Daten spaltenorientiert statt zeilenweise-objektbasiert (bessere Kompression und Speicherlokalität) und definiert standardisierte, verlustärmere Typkonvertierungsregeln: Arrow-optimierte UDFs konvertieren kompatible Typen erfolgreich (z. B. String zu Integer), während gepickelte UDFs bei Typ-Mismatches stillschweigend auf `NULL` zurückfallen.

**Aktivierung pro UDF** über den `useArrow`-Parameter von `functions.udf()` (Standard: deaktiviert):

```python
from pyspark.sql.functions import udf

@udf(returnType="long", useArrow=True)
def squared_arrow(s):
    return s * s
```

**Globale Aktivierung** für die gesamte Session:

```python
spark.conf.set("spark.sql.execution.pythonUDF.arrow.enabled", "true")
```

**Benchmark-Ergebnisse** (Testcluster: 3 Worker + 1 Driver, je 16 vCPUs/122 GB RAM): Arrow-optimierte UDFs sind bei einer einzelnen Transformation rund **1,6x schneller** als gepickelte Python-UDFs; bei verketteten (mehrfach hintereinander angewendeten) UDFs auf 32-GB-Datensätzen wächst der Vorteil auf rund **1,9x**. Verfügbar seit Apache Spark 3.5 / Databricks Runtime 14.0 (Referenzimplementierung: SPARK-40307).

Quelle(n): https://www.databricks.com/blog/arrow-optimized-python-udfs-apache-sparktm-35

---

## 84. Blog: Terraform Databricks Modules (Community-Registry-Module)

**Einfach erklärt:** Ergänzend zum offiziellen Databricks-Terraform-Provider (Abschnitte 14–21) stellt Databricks Field Engineering über das Projekt **terraform-databricks-examples** mehr als 30 wiederverwendbare, experimentelle Terraform-Module und -Beispiele im offiziellen Terraform Registry bereit: `registry.terraform.io/modules/databricks/examples/databricks/latest` (Quellcode: `github.com/databricks/terraform-databricks-examples`). Jedes Beispiel ist eigenständig nutzbar und mit eigener README dokumentiert — entweder als Referenzcode zum Abschauen oder durch direktes Referenzieren als Submodul in der eigenen Terraform-Konfiguration. Ziel ist ein standardisierter, wiederholbarer Ansatz zur Ressourcen-Definition organisationsweit.

**Wichtiger Hinweis:** Die Module sind explizit **experimentell** und ein Community-Projekt „as-is" — „Databricks does not offer official support", Beiträge per Pull Request sind willkommen. Das ist ausdrücklich zu unterscheiden vom offiziell unterstützten Terraform-Provider selbst (Abschnitt 15). Der Databricks-Terraform-Provider hatte zum Zeitpunkt der Ankündigung (Mai 2023) bereits über 10 Millionen Installationen erreicht.

**Praxisbeispiel im Blog — `adb-vnet-injection`:** stellt einen VNet-injizierten Azure-Databricks-Workspace mit Auto-Scaling-Cluster bereit. Nutzung als Submodul (Namensmuster gemäß Registry-Pfad):

```hcl
module "vnet_injection" {
  source = "databricks/examples/databricks//modules/adb-vnet-injection"
}
```

Ablauf wie bei jeder Terraform-Konfiguration: `terraform init`, `terraform plan`, `terraform apply`.

Quelle(n): https://www.databricks.com/blog/announcing-terraform-databricks-modules

---

## 85. Verifikationsprotokoll (Databricks-Blog-Abgleich)

Die folgenden Tabellen fassen die Web-Recherche-Ergebnisse aus vier parallel arbeitenden Teilrecherchen zusammen (Themengruppen: Git Folders/CI-CD/Terraform, Databricks Asset Bundles, UDFs/Databricks Utils/SDK, Authenticate developer tools). Jede Zeile ordnet einen Kursinhalt einer aktuellen Databricks-Blog- oder Doku-Quelle zu und bewertet die Übereinstimmung (✅ deckungsgleich, ⚠️ Ergänzung/kleinere Lücke, ❌ Widerspruch).

### Git Folders (Repos), CI/CD, Terraform

| Thema | Blog-Quelle | Ergebnis |
|---|---|---|
| Git Folders / Repos: Umbenennung und Feature-Unterschiede | [What happened to Databricks Repos?](https://docs.databricks.com/aws/en/repos/what-happened-repos) / [Flexera-Blog: How to set up Databricks Git folders from scratch (2026)](https://www.flexera.com/blog/finops/how-to-set-up-databricks-git-folders-repos-from-scratch-2026/) | ⚠️ Keine neue GA-Ankündigung auf databricks.com/blog gefunden; die Doku-Seite bestätigt aber zusätzliche Details, die in den Originaldateien fehlen: Git Folders können — anders als klassische Repos — an beliebiger Stelle im Workspace-Dateibaum liegen (nicht nur unter `/Workspace/Repos/...`) und unterstützen zusätzliche Asset-Typen wie SQL-Assets. Ergänzenswert, aber kein GA-relevantes Sicherheits-/Funktionsrisiko. |
| CI/CD Best Practices mit Databricks Asset Bundles | [Announcing Public Preview: Databricks Asset Bundles](https://databricks.com/blog/announcing-public-preview-databricks-asset-bundles-apply-software-development-best-practices) / [Databricks Community: CI/CD on Databricks with DABs and GitHub Actions](https://community.databricks.com/t5/community-articles/ci-cd-on-databricks-with-asset-bundles-dabs-and-github-actions/td-p/149565) | ✅ Bestätigt den in den Originaldateien beschriebenen Ansatz (Bundles als primäre CI/CD-Empfehlung, Versionierung/Code-Review/Testing/Automatisierung). Hinweis: Aktuelle Doku spricht teils bereits von „Declarative Automation Bundles" als Nachfolgebezeichnung — siehe dazu die ausführliche Bestätigung im DAB-Themenblock unten. |
| Terraform-Provider: neue Ressourcen 2025/2026 | [terraform-provider-databricks Releases (GitHub)](https://github.com/databricks/terraform-provider-databricks/releases) / [CHANGELOG.md](https://github.com/databricks/terraform-provider-databricks/blob/main/CHANGELOG.md) | ⚠️ Kein dedizierter databricks.com/blog-Artikel gefunden (Blog-Ankündigung „GA" stammt noch von 2022). Laut GitHub-Release-Notes kamen seither aber neue Ressourcentypen hinzu (u. a. Lakebase-Ressourcen, Clean Rooms, Materialized Features, Alert-V2-Permissions) — diese fehlen komplett in den 8 Original-Terraform-Dateien des Kurses, da diese sich auf klassische Ressourcen (Cluster, Job, Notebook, Service Principal, UC) beschränken. Keine falschen Aussagen, aber Lücke bei neueren Ressourcentypen. |
| GitHub Actions für Databricks | [Automate your data and ML workflows with GitHub Actions for Databricks (2022)](https://www.databricks.com/blog/2022/06/02/automate-your-data-and-ml-workflows-with-github-actions-for-databricks.html) | ✅ Der ursprüngliche Blog-Post von 2022 bestätigt weiterhin die Grundarchitektur (`databricks/setup-cli`, Bundle-Deploy-Workflows). Keine neuere GA-Ankündigung mit substanziell neuen Actions gefunden — Originaldatei korrekt als „Public Preview" markiert und weiterhin aktuell. |
| Serverless Private Git | [Configure Databricks Serverless Private Git (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/databricks/repos/serverless-private-git) / [docs.databricks.com/aws/en/repos/serverless-private-git](https://docs.databricks.com/aws/en/repos/serverless-private-git) | ✅ Bestätigt den Public-Preview-Status und die in der Originaldatei beschriebenen Vorteile (nur bei Bedarf Serverless Compute, PrivateLink/Private-Link-Anbindung). Keine GA-Ankündigung für 2026 gefunden — Feature-Status in der Originaldatei ist weiterhin korrekt. |
| Workload Identity Federation für CI/CD-Authentifizierung | [Enable workload identity federation in CI/CD](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-federation-provider) / [Databricks Community: CI/CD using Workload Identity Federation](https://community.databricks.com/t5/community-articles/ci-cd-using-workload-identity-federation/td-p/157324) | ✅ Bestätigt die in den CI/CD- und Git-Folders-Dateien genannte Empfehlung, Workload Identity Federation/OAuth Token Federation statt gespeicherter Secrets zu nutzen — kein dedizierter Blog-Post, aber die Doku deckt sich vollständig mit den Kursinhalten (z. B. GitHub-Actions-Workflow mit `id-token: write` und `github-oidc`). Wird im Themenblock „Authenticate developer tools" unten vertieft. |

### Databricks Asset Bundles (DAB / Declarative Automation Bundles)

| Thema | Blog-Quelle | Ergebnis |
|---|---|---|
| Umbenennung "Databricks Asset Bundles" → "Declarative Automation Bundles" | [Announcing the General Availability of Declarative Automation Bundles](https://www.databricks.com/blog/announcing-general-availability-databricks-asset-bundles) · [Databricks Asset Bundles is now Declarative Automation Bundles (Community)](https://community.databricks.com/t5/mvp-articles/databricks-asset-bundles-is-now-declarative-automation-bundles/td-p/151594) | ✅ Bestätigt und bereits korrekt in allen 24 Originaldateien reflektiert. Die Umbenennung erfolgte mit CLI v0.287+ im März 2026; die Originaldateien (Stand 2026-08/09) liegen zeitlich danach und sind konsistent. Die Namensänderung ist wie dokumentiert nicht-brechend. |
| Direct Deployment Engine — Terraform-Ablösung | [Databricks transitioning to the Direct Deployment Engine (Medium/Towards Data Engineering)](https://medium.com/towards-data-engineering/transitioning-to-the-direct-deployment-engine-for-declarative-automation-bundles-e0e5a45bb9db) · [databricks/cli docs/direct.md](https://github.com/databricks/cli/blob/main/docs/direct.md) | ⚠️ **Ergänzungsbedarf:** Ab CLI **1.3.0** nutzen neu erstellte Bundles die Direct Engine standardmäßig, und Databricks plant, die Terraform-Engine im Lauf von 2026 vollständig abzulösen (Direct Engine wird alleiniger unterstützter Pfad). Die Originaldatei zu Kapitel 11 beschreibt korrekt den Stand „beide Engines wählbar ab CLI 0.279.0", erwähnt aber weder den neuen Default ab CLI 1.3.0 noch die geplante vollständige Terraform-Deprecation — sollte bei einer künftigen Aktualisierung ergänzt werden. |
| Ursprüngliche GA-Ankündigung von Databricks Asset Bundles | [Announcing the General Availability of Databricks Asset Bundles (databricks.com/blog)](https://www.databricks.com/blog/announcing-general-availability-databricks-asset-bundles) | ✅ Bestätigt als historischer Ausgangspunkt (GA am 23. April 2024, damals unter dem alten Namen). Die Kernfunktionalität „Ressourcen bündeln, versionieren, testen, deployen" deckt sich mit der Grundidee in den Kapiteln 22/23. |
| MLOps Stacks als Bundle-Template | [Databricks MLOps Stacks GitHub-Repo](https://github.com/databricks/mlops-stacks) · [MLOps Stacks: model development process as code (Doku)](https://docs.databricks.com/aws/en/machine-learning/mlops/mlops-stacks) | ✅ Bestätigt. Keine Hinweise auf einen neuen Namen oder ein Nachfolgeprodukt für MLOps Stacks; CLI-Mindestversion (≥ 0.212.2) und Drei-Wege-Setup (CICD_and_Project/Project_Only/CICD_Only) stimmen mit dem entsprechenden Kapitel überein. |
| Neue 2026-Ressourcen exklusiv für Direct Engine (Catalogs, External Locations, Genie Spaces, AI-Search-Endpoints) | [databricks/cli docs/direct.md](https://github.com/databricks/cli/blob/main/docs/direct.md) · [SunnyData: Databricks Direct Engine – What It Is & How to Migrate](https://www.sunnydata.ai/blog//databricks-direct-engine-dabs) | ✅ Bestätigt, keine über die Originaldateien hinausgehenden neuen Ressourcentypen gefunden. Die genannte Liste (Catalogs, External Locations, Secrets, Genie Spaces, Instance Pools, AI-Search-Endpoints) deckt sich mit den Kapiteln zu Direct Deployment Engine und Ressourcentypen. |
| VS Code Extension / "Databricks IDE extension" Namensgebung | Offizielle Doku, wie bereits im entsprechenden Kapitel zitiert; keine dedizierte databricks.com/blog-Fundstelle mit neuen 2026-Fakten identifiziert | ⚠️ Keine zusätzlichen Blog-Funde über die bereits zitierte offizielle Doku hinaus; die dort dokumentierten Abweichungen (PAT als Legacy, fehlende explizite „autocomplete/schema validation"-Begriffe) bleiben der aktuellste bekannte Stand. |

**Gesamteinschätzung DAB:** Die 24 Originaldateien sind inhaltlich auf aktuellem Stand (Namensänderung zu Declarative Automation Bundles korrekt übernommen, Direct Deployment Engine als Alternative zu Terraform korrekt beschrieben). Einziger konkreter Ergänzungsbedarf: der ab CLI 1.3.0 geänderte Default (Direct Engine statt Terraform für neue Bundles) sowie die für 2026 angekündigte vollständige Terraform-Deprecation.

### UDFs, Databricks Utils, Databricks SDK für Python

| Thema | Blog-Quelle | Ergebnis |
|---|---|---|
| Neue Features für Unity-Catalog-Python-UDFs (Custom Dependencies, Batch Input, Service Credentials) | [Announcing support for New UC Python UDF Features](https://www.databricks.com/blog/announcing-support-new-uc-python-udf-features) | ✅ Deckt sich vollständig mit den Originaldateien zu SQL/Python-UDFs und Batch-Python-UDFs — Custom Dependencies (PyPI/Volume/URL), Batch-Modus über `PARAMETER STYLE PANDAS` und `CREDENTIALS`-Klausel sind dort bereits ausführlich dokumentiert. |
| Python UDTFs Unity Catalog / Apache Spark 3.5 & 4.0 | [Introducing Apache Spark 4.0](https://www.databricks.com/blog/introducing-apache-spark-40) und [Introducing Python User-Defined Table Functions (UDTFs) Unity Catalog](https://www.databricks.com/blog/introducing-python-user-defined-table-functions-udtfs-unity-catalog) | ✅ Polymorphe UDTFs mit `analyze()`, Table-Argumente und Partitionierung sind in den Originaldateien zu UC-UDTFs und Session-scoped-UDTFs bereits vollständig beschrieben. |
| **Arrow UDFs als Nachfolger der Pandas UDFs (Databricks Runtime 18.0)** | [Introducing Arrow UDFs in PySpark: A Faster, Leaner Replacement for Pandas UDFs](https://www.databricks.com/blog/introducing-arrow-udfs-pyspark-faster-leaner-replacement-pandas-udfs) | ⚠️ **Lücke in den Originaldateien:** Native Arrow UDFs (ab Databricks Runtime 18.0) operieren direkt auf Arrow-Daten ohne Pandas-/NumPy-Konvertierung — laut Blog rund 10 % schnellere Ausführung, ~40 % weniger Speicherverbrauch und bessere Unterstützung komplexer Datentypen als klassische Pandas-UDFs, bei ähnlicher Dekorator-Syntax. Weder die Pandas-UDF- noch die Python-Scalar-UDF-Datei erwähnen dieses neuere Feature — die Kursunterlagen sind hier noch nicht auf dem neuesten Stand. |
| Databricks SDK für Python — aktuelle Nutzung | [How to Build Production-Ready Data and AI Apps with Databricks Apps and Lakebase](https://www.databricks.com/blog/how-build-production-ready-data-and-ai-apps-databricks-apps-and-lakebase), [How to use Lakebase as a transactional data layer for Databricks Apps](https://www.databricks.com/blog/how-use-lakebase-transactional-data-layer-databricks-apps) | ✅ Kein neuer SDK-Kernmechanismus gefunden, der der Originaldatei zum Databricks SDK für Python widerspricht — `WorkspaceClient`/Unified Authentication bleiben der Standardweg. Neuere Blogs zeigen vor allem neue Anwendungsfälle (Lakebase, Databricks Apps), keine neue Auth- oder Kernklassen-Änderung. |
| dbutils / Widgets in Notebooks | [Databricks and Jupyter: Announcing ipywidgets in the Databricks Notebook](https://www.databricks.com/blog/2022/08/09/databricks-and-jupyter-announcing-ipywidgets-in-the-databricks-notebook.html) | ⚠️ Ergänzung, keine Lücke im engeren Sinn: Seit Databricks Runtime 11.0 werden zusätzlich zu `dbutils.widgets` auch klassische **ipywidgets** (Slider, Buttons, Checkboxen, Dropdowns, Tabs) in Databricks-Notebooks unterstützt. Die Originaldatei zur Widgets Utility behandelt ausschließlich `dbutils.widgets`, nicht ipywidgets — für reine `dbutils`-Widget-Funktionalität ist sie aber weiterhin korrekt und vollständig. |
| Unity Catalog Governance allgemein (Kontext für UDFs) | [What's new with Unity Catalog at Data + AI Summit 2026](https://www.databricks.com/blog/whats-new-unity-catalog-data-ai-summit-2026) | ✅ Keine direkten Auswirkungen auf UDF-/UDTF-Governance-Mechanik in den Originaldateien; der Blog bestätigt lediglich den fortgesetzten Ausbau von Unity Catalog als zentrale Governance-Schicht, auf der UC-UDFs bereits aufbauen. |

*Hinweis zur Vollständigkeit der Quell-Dateien:* In den Original-Dateien zu Scala/Java-UDFs (Unity Catalog und Session-scoped) sowie zu Scala-UDAFs fehlen an mehreren Stellen konkrete Scala-Code-Beispiele im Quelltext selbst (nur Überschriften, kein Code) — dies wurde in den jeweiligen Abschnitten wortgetreu als „[im Original leer/kein Code vorhanden]" markiert statt Code zu erfinden. In der Datei zu UDF Task Context findet sich zudem eine Inkonsistenz der offiziellen Databricks-Dokumentation selbst (`job_group_id` wird im Beispielcode verwendet, aber nie zugewiesen) — diese wurde wortgetreu übernommen und als Auffälligkeit kenntlich gemacht.

### Authenticate developer tools

| Thema | Blog-Quelle | Ergebnis |
|---|---|---|
| OAuth Token Federation — GA-Status | [Introducing next-level identity security on Databricks](https://databricks.com/blog/introducing-next-level-identity-security-databricks) | ✅ OAuth Token Federation ist laut Databricks-Blog inzwischen **generally available (GA)** über AWS, Azure und GCP hinweg. Die Originaldateien behandeln Token Federation bereits als produktionsreif und empfehlen sie klar als primäre Methode — inhaltlich deckungsgleich, GA-Status bestätigt und ergänzt den Kursinhalt sinnvoll. |
| Workload Identity Federation in CI/CD | [Enable workload identity federation in CI/CD](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-federation-provider) / Databricks Community Artikel „CI/CD using Workload Identity Federation" | ✅ Bestätigt: Databricks empfiehlt Workload Identity Federation ausdrücklich vor allen Alternativen für CI/CD-Workloads, exakt wie im entsprechenden Kapitel beschrieben. Keine neuen Provider über die in den Originaldateien (GitHub, Azure DevOps, AWS IAM, GitLab, CircleCI, Jenkins, Terraform Cloud, Bitbucket) hinaus gefunden. |
| Unified Authentication — Auswertungsreihenfolge | Offizielle Doku (`docs.databricks.com/aws/en/dev-tools/auth/unified-auth`), erneut geprüft | ⚠️ Kleine Ergänzung: Aktuelle Doku nennt in der Methoden-Reihenfolge zusätzlich **Google Cloud service account credentials** und **Google Cloud identity** als vierten/fünften Schritt (nach PAT, OAuth M2M, OAuth U2M) — relevant nur für Databricks on GCP, für AWS/Azure-Kontext des Kurses ohne Auswirkung, aber als Vollständigkeitshinweis vermerkt. |
| Personal Access Tokens — Deprecation/Security-Trend | [Personal access tokens (PATs) is legacy in Databricks – use OAuth token federation](https://rebricked.org/databricks/personal-access-tokens/); Databricks-Doku „Monitor and revoke personal access tokens" | ⚠️ PATs sind weiterhin nicht vollständig abgeschaltet, aber der Sicherheitsdruck hat 2026 zugenommen: Databricks hat inzwischen zusätzlich zur automatischen 90-Tage-Inaktivitäts-Revocation eine **maximale Lebensdauer von 2 Jahren für neu erstellte PATs** eingeführt sowie **Scoped PATs im April 2026 GA** gesetzt. Das entsprechende Kapitel nennt bereits 90-Tage-Revocation und Scoped Tokens, aber nicht explizit das neue 2-Jahres-Maximum für neue Tokens — sinnvolle Ergänzung. |
| AWS IAM Outbound Identity Federation | AWS-Blog „Simplify access to external services using AWS IAM Outbound Identity Federation"; Databricks-Doku Provider-AWS-IAM | ✅ Kein eigener Databricks-Blogpost gefunden, aber AWS- und Databricks-Doku bestätigen Mechanismus und Motivation (Secrets-Manager-Eliminierung) exakt wie im Kapitel zum AWS-IAM-Provider beschrieben; keine Abweichungen. |
| Service Principals als CI/CD-Best-Practice | Databricks Community Artikel „Git credentials for service principals running jobs" | ✅ Bestätigt den beschriebenen Trend, Service Principals statt persönlicher Benutzer-Tokens für CI/CD zu verwenden; keine neuen Erkenntnisse, die über die Originaldatei hinausgehen. |

### Gesamteinschätzung „10 Developers"

Die Kursunterlagen zu Git Folders, CI/CD, Terraform, Databricks Asset Bundles, UDFs, Databricks Utils, dem Python-SDK und der Developer-Tool-Authentifizierung sind überwiegend aktuell und decken sich mit den offiziellen Databricks-Quellen. Die wichtigsten Ergänzungspunkte für eine künftige Aktualisierung sind:

1. **Direct Deployment Engine:** Seit CLI 1.3.0 ist sie für neue Bundles der Standard statt einer reinen Option, und Databricks plant die vollständige Ablösung der Terraform-Engine im Lauf von 2026 (Kapitel Direct Deployment Engine).
2. **Arrow UDFs (Databricks Runtime 18.0):** Als schnellerer, speichersparenderer Nachfolger der Pandas-UDFs in den Originaldateien noch nicht erwähnt.
3. **Terraform-Provider:** Neuere Ressourcentypen (Lakebase, Clean Rooms, Materialized Features u. a.) fehlen in den Terraform-Kapiteln, da diese sich auf klassische Ressourcen beschränken.
4. **PAT-Sicherheitsverschärfung 2026:** Neues 2-Jahres-Maximum für neu erstellte Personal Access Tokens ergänzt die bereits dokumentierte 90-Tage-Inaktivitäts-Revocation.

Keine der gefundenen Abweichungen widerspricht (❌) den Originaldateien inhaltlich — es handelt sich durchweg um Ergänzungen (⚠️) zu neueren Entwicklungen bzw. Bestätigungen (✅) bestehender Inhalte.
