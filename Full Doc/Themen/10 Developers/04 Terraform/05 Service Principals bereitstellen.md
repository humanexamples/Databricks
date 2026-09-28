# Service Principals bereitstellen

Einen Service Principal samt optionalem Personal-Access-Token per Terraform anlegen. Teil der [Terraform](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Voraussetzungen](#voraussetzungen)
3. [Schritt-für-Schritt-Umsetzung](#umsetzung)
4. [Optional: Personal-Access-Token-Generierung aktivieren](#token-generierung)
5. [Wichtige Hinweise](#hinweise)
6. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

Ein Service Principal repräsentiert „eine Identität für automatisierte Tools und Systeme wie Skripte, Apps und CI/CD-Plattformen." Dieser Ansatz nutzt den Databricks-Terraform-Provider, um solche Identitäten im Workspace zu erstellen.

## <a id="voraussetzungen">2. Voraussetzungen</a>

1. **Databricks Personal Access Token** — nötig, um die API-Aufrufe des Terraform-Providers zu autorisieren.
2. **Databricks CLI ≥ 0.205**, konfiguriert mit einem Auth-Profil, das auf den PAT verweist.
3. **Terraform CLI**.

**Konfigurationsprofil einrichten:** `databricks configure --profile DEFAULT` ausführen — fragt nach Workspace-Instanz-URL und Personal Access Token.

## <a id="umsetzung">3. Schritt-für-Schritt-Umsetzung</a>

### Schritt 1 — Arbeitsverzeichnis erstellen

```bash
mkdir terraform_service_principal_demo && cd terraform_service_principal_demo
```

### Schritt 2 — `main.tf` erstellen

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

### Schritt 3 — `terraform.tfvars` erstellen

```hcl
databricks_connection_profile           = "<Databricks authentication configuration profile name>"
service_principal_display_name          = "<Service principal display name>"
service_principal_access_token_lifetime = 3600
```

Platzhalter durch tatsächliche Werte ersetzen.

### Schritt 4 — Konfiguration validieren

```bash
terraform init
terraform validate
```

### Schritt 5 — Ressourcen deployen

```bash
terraform apply
```

## <a id="token-generierung">4. Optional: Personal-Access-Token-Generierung aktivieren</a>

Um Access Tokens für den Service Principal zu generieren, folgende Ressourcen in `main.tf` einkommentieren:

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

## <a id="hinweise">5. Wichtige Hinweise</a>

- Pro Workspace kann nur eine `authorization = "tokens"`-Ressource existieren.
- Das Einkommentieren der Token-Berechtigungen widerruft vorherigen Nutzerzugriff auf Token-Authentifizierung.
- Generierte Tokens sind workspace-gebunden und können nicht für Account-Ebenen-Operationen genutzt werden.
- Abgerufene Tokens erscheinen in der `terraform.tfstate`-Datei.

## <a id="quelle">6. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/terraform/service-principals

**Stand:** 2026-08-21.
