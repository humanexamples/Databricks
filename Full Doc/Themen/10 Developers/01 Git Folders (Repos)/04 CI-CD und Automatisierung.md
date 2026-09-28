# CI/CD und Automatisierung mit Git Folders

Behandelt CI/CD-Muster mit Git Folders (Produktions-Ordner, Berechtigungsstruktur, Synchronisationsansätze), Automatisierung über einen Service Principal sowie Automatisierung via Terraform. Teil der [Git Folders (Repos)](01%20Grundlagen.md)-Reihe.

## Abschnittsübersicht

1. [Drei primäre Nutzungsmuster](#nutzungsmuster)
2. [Kollaborations-Workflow](#workflow)
3. [Produktions-Git-Folder](#produktion)
4. [Berechtigungsstruktur](#berechtigungen)
5. [Synchronisationsansätze](#synchronisation)
6. [CI/CD-Strategie-Empfehlung](#strategie)
7. [Automatisierung mit Service Principal](#service-principal)
8. [Automatisierung mit Terraform](#terraform)
9. [Quelle](#quelle)

---

## <a id="nutzungsmuster">1. Drei primäre Nutzungsmuster</a>

- **Administratives Setup:** Workspace-Admins richten Top-Level-Ordner außerhalb der Nutzerverzeichnisse ein, um produktionsreife Git-Repositories zu hosten. Sie klonen Repositories auf bestimmten Branches und organisieren Ordner nach Zweck (Production, Test, Staging).
- **Entwickler-Kollaboration:** einzelne Mitwirkende erstellen Git Folders innerhalb ihrer nutzerspezifischen Workspace-Pfade, arbeiten auf dedizierten Branches und pushen Commits zurück ins Remote-Repository.
- **Integration via Merge:** Nach dem Mergen von Pull Requests löst Automatisierung Pull-Operationen in Produktions-Ordner über die Databricks Repos API aus.

Vor der Einrichtung von Automatisierung sollten Teams „die zu nutzenden Remote-Git-Repositories überprüfen" und „die richtigen Repos und Branches für jede Stufe wählen".

## <a id="workflow">2. Kollaborations-Workflow</a>

1. Bestehendes Git-Repository in den Workspace klonen.
2. Feature-Branch vom Main-Branch über die Git-Folders-UI erstellen.
3. Notebooks und Repository-Dateien ändern.
4. Änderungen committen und ins Remote pushen.
5. Andere Mitwirkende führen die gleichen Schritte auf ihren Branches aus.
6. Pull Request erstellen, Team-Review durchführen, in den Deployment-Branch mergen.

„Databricks empfiehlt, dass jeder Entwickler auf einem eigenen Branch arbeitet."

## <a id="produktion">3. Produktions-Git-Folder</a>

Produktions-Ordner unterscheiden sich grundlegend von Nutzer-Ebenen-Ordnern: Nutzer-Ebenen-Ordner dienen als „lokale Checkouts, in denen Nutzer entwickeln und Änderungen pushen", während Produktions-Ordner „von Admins außerhalb der Nutzerordner erstellt werden, Deployment-Branches enthalten und die Quelle für automatisierte Workflows sind."

Produktions-Ordner „sollten nur durch Automatisierung aktualisiert werden, wenn PRs in Deployment-Branches gemerged werden" — der Zugriff sollte „für die meisten Nutzer auf Run-only-Zugriff beschränkt" werden.

## <a id="berechtigungen">4. Berechtigungsstruktur</a>

Drei empfohlene Berechtigungsstufen:

- **Can Run** — für Projekt-Nutzer, die Workflows ausführen.
- **Can Run** — für Databricks-Service-Principals, die Automatisierung ausführen.
- **Can View** (optional) — für Workspace-Nutzer zur Unterstützung der Auffindbarkeit.

## <a id="synchronisation">5. Synchronisationsansätze</a>

Zwei Methoden, um Produktions-Ordner mit Remote-Branches synchron zu halten:

**Externe CI/CD-Tools:** Systeme wie GitHub Actions pullen die neuesten Commits, wenn Pull Requests in Deployment-Branches gemerged werden.

**Geplante Job-Automatisierung:** ein Notebook-basierter Ansatz läuft nach Zeitplan mit folgendem Muster:

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
w.repos.update(w.workspace.get_status(path="<git-folder-workspace-full-path>").object_id, branch="<branch-name>")
```

## <a id="strategie">6. CI/CD-Strategie-Empfehlung</a>

Die Doku empfiehlt **Databricks Asset Bundles** (Declarative Automation Bundles) als bevorzugte CI/CD-Methodik — code-only-Deployment via Produktions-Git-Folders wird als alternativer Ansatz anerkannt. Siehe [Databricks Asset Bundles](../Databricks%20Asset%20Bundles/) für die vertiefte Bundles-Referenz.

## <a id="service-principal">7. Automatisierung mit Service Principal</a>

Service Principals ermöglichen automatisierten Workflows den Zugriff auf Git Folders. Sie benötigen dedizierte Git-Credentials für Operationen wie Code-Pull oder Notebook-Updates in CI/CD-Pipelines.

### UI-basierte Konfiguration

1. Als Workspace-Admin anmelden.
2. Username > **Settings**.
3. Tab „Identity and access".
4. **Manage** neben Service Principals klicken.
5. Ziel-Service-Principal wählen.
6. Tab „Git integration" öffnen.
7. **Add Git credential** wählen.
8. Git-Provider aus dem Dropdown wählen, erforderliche Felder ausfüllen.
9. **Save** bzw. **Link** klicken (variiert je Provider).

### CLI-basierte Konfiguration

**Voraussetzungen:** installierte und konfigurierte Databricks CLI; Personal Access Token des Git-Providers.

**Schritt 1 — Service Principal erstellen:**

```bash
databricks service-principals create \
  --display-name "Git Automation Service Principal"
```

`applicationId` und `id` notieren.

**Schritt 2 — OAuth Secret generieren:**

```bash
databricks service-principal-secrets-proxy create \
  <service-principal-id>
```

Den zurückgegebenen `secret`-Wert kopieren.

**Schritt 3 — CLI-Authentifizierung konfigurieren und Git-Credentials hinzufügen:**

```bash
export DATABRICKS_HOST=<workspace-url>
export DATABRICKS_CLIENT_ID=<application-id>
export DATABRICKS_CLIENT_SECRET=<oauth-secret>

databricks git-credentials create <git-provider> \
  --personal-access-token <git-pat> \
  --git-email <git-email>
```

Platzhalter durch Workspace-URL, Application ID, OAuth Secret, Provider-Namen (z. B. `gitHub`), PAT und E-Mail-Adresse ersetzen.

### Programmatischer Abruf

Service Principals lassen sich über das Databricks SDK für Python, REST-APIs, die CLI oder Terraform abrufen. SDK-Beispiel: `%pip install databricks-sdk --upgrade`, dann `ApiClient` importieren und die Service-Principals-API aufrufen.

**Empfehlung:** „Einen Service Principal für automatisierte oder gemeinsam genutzte Workflows wie CI/CD-Pipelines und geplante Jobs verwenden. Wer interaktiv als Einzelperson arbeitet, sollte stattdessen die eigenen Git-Credentials nutzen."

## <a id="terraform">8. Automatisierung mit Terraform</a>

Die Automatisierung erfolgt zweistufig, da „Terraform Provider-Konfigurationen vor der Erstellung jeglicher Ressourcen auswertet, sodass kein Ressourcenwert innerhalb derselben Konfiguration referenziert werden kann."

### Teil 1: Service Principal erstellen (Verzeichnis `setup/`)

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

**Sicherheitshinweis:** `terraform.tfvars` zur `.gitignore` hinzufügen, um das Committen von Credentials zu verhindern.

### Teil 2: Git-Credentials konfigurieren (Verzeichnis `git-credentials/`)

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

### Design-Prinzipien

- Zweigeteilter Konfigurationsansatz trennt Service-Principal-Erstellung von der Git-Integration.
- OBO-Tokens (On-Behalf-Of) ermöglichen sichere Service-Principal-Authentifizierung, ohne langlebige Credentials einzubetten.
- Die `depends_on`-Deklaration stellt sicher, dass Credentials vor der Repository-Erstellung existieren.
- Sensible Variablen sind entsprechend markiert, um versehentliche Exposition zu verhindern.

## <a id="quelle">9. Quelle</a>

- https://docs.databricks.com/aws/en/repos/ci-cd
- https://docs.databricks.com/aws/en/repos/automate-with-sp
- https://docs.databricks.com/aws/en/repos/automate-with-terraform
- https://docs.databricks.com/aws/en/dev-tools/sdk-python (`WorkspaceClient`-Beispiel oben sowie SDK-Abruf von Service Principals; vollständige SDK-Referenz siehe [Databricks SDK für Python.md](../07%20Databricks%20SDK%20fuer%20Python.md))

**Stand:** 2026-09-01.
