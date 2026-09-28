# Unity Catalog automatisieren

Voraussetzungen und Umgebungsvariablen für die Automatisierung des Unity-Catalog-Setups auf AWS über den Databricks-Terraform-Provider. Teil der [Terraform](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Voraussetzungen](#voraussetzungen)
2. [Erforderliche Umgebungsvariablen](#env-vars)
3. [Lokale Entwicklungsvoraussetzungen](#lokal)
4. [Sicherheitshinweis](#sicherheit)
5. [Deployment-Anleitung](#deployment)
6. [Terraform-Befehle](#befehle)
7. [Quelle](#quelle)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

**Account- und Service-Anforderungen:**

- Premium-Plan oder höher auf Databricks.
- AWS-Fähigkeiten zum Erstellen von S3-Buckets, IAM-Rollen, Policies und Cross-Account-Trust-Beziehungen.
- Mindestens ein Databricks-Workspace.

**Für Metastore-Konfiguration via Terraform:** ein AWS-Account, ein Databricks-on-AWS-Account sowie ein Service Principal mit Account-Admin-Berechtigungen.

## <a id="env-vars">2. Erforderliche Umgebungsvariablen</a>

| Variable | Zweck |
|---|---|
| `DATABRICKS_CLIENT_ID` | Application ID des Service Principal |
| `DATABRICKS_CLIENT_SECRET` | Secret des Service Principal |
| `DATABRICKS_ACCOUNT_ID` | Databricks-Account-ID |
| `TF_VAR_databricks_account_id` | dasselbe wie oben, als Terraform-Variable |
| `AWS_ACCESS_KEY_ID` | AWS Access Key |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Key |
| `AWS_REGION` | AWS-Regionscode |

## <a id="lokal">3. Lokale Entwicklungsvoraussetzungen</a>

- Terraform CLI.
- Entweder Databricks CLI (≥ 0.205) mit Personal Access Token, oder Umgebungsvariablen (`DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`/`DATABRICKS_CLIENT_SECRET`, oder `DATABRICKS_TOKEN`).

## <a id="sicherheit">4. Sicherheitshinweis</a>

Die Doku „empfiehlt, OAuth-Tokens" statt Personal Access Tokens für automatisierte Systeme zu nutzen.

## <a id="deployment">5. Deployment-Anleitung</a>

Für die vollständige Deployment-Anleitung verweist die Doku auf den Leitfaden „Deploying pre-requisite resources and enabling Unity Catalog" in der offiziellen Terraform-Provider-Dokumentation auf `registry.terraform.io`. Für die konzeptionellen Grundlagen (Governance-Modelle, Metastore-Design-Patterns, Catalog-Struktur) siehe [Platform/Architecture/Production Planning/03 Unity Catalog Architektur.md](../../Platform/Architecture/Production%20Planning/03%20Unity%20Catalog%20Architektur.md); für die konkrete GRANT-/Setup-Syntax siehe [Governance/Data Governance](../../Governance/Data%20Governance/).

## <a id="befehle">6. Terraform-Befehle</a>

```bash
terraform validate
terraform plan
terraform apply
terraform destroy
```

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/terraform/automate-uc

**Stand:** 2026-08-21.
