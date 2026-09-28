# Workload Identity Federation in CI/CD aktivieren

Übersichtsseite: Wie automatisierte Workloads außerhalb von Databricks sich per OAuth Token Federation (OIDC) ohne Databricks-Secrets authentifizieren. Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Überblick

OAuth Token Federation, auch **OpenID Connect (OIDC)** genannt, ermöglicht automatisierten Workloads externen zu Databricks den sicheren Zugriff auf Databricks-APIs **ohne Databricks-Secrets**. Der Workload authentifiziert sich bei Databricks als **Service Principal** mit Identity-Tokens aus der Automatisierungsumgebung.

## Zentrale Empfehlung

Databricks betont, dass Organisationen **Workload Identity Federation priorisieren** sollten, da sie „das Verwalten und Rotieren von Databricks-Secrets überflüssig macht" und damit alternativen Authentifizierungsmethoden überlegen ist.

## Unterstützte CI/CD-Werkzeuge

Die Doku liefert Konfigurationsanleitungen für folgende Identity Provider:

| Provider | Detailseite |
|---|---|
| GitHub Actions | [05 Provider — GitHub Actions.md](05%20Provider%20%E2%80%94%20GitHub%20Actions.md) |
| Azure DevOps Pipelines | [06 Provider — Azure DevOps.md](06%20Provider%20%E2%80%94%20Azure%20DevOps.md) |
| AWS IAM Workloads | [07 Provider — AWS IAM.md](07%20Provider%20%E2%80%94%20AWS%20IAM.md) |
| GitLab CI/CD | [08 Provider — Terraform Cloud, Bitbucket, Jenkins.md](08%20Provider%20%E2%80%94%20Terraform%20Cloud%2C%20Bitbucket%2C%20Jenkins.md) |
| CircleCI | [08 …](08%20Provider%20%E2%80%94%20Terraform%20Cloud%2C%20Bitbucket%2C%20Jenkins.md) |
| Jenkins | [08 …](08%20Provider%20%E2%80%94%20Terraform%20Cloud%2C%20Bitbucket%2C%20Jenkins.md) |
| Terraform Cloud | [08 …](08%20Provider%20%E2%80%94%20Terraform%20Cloud%2C%20Bitbucket%2C%20Jenkins.md) |
| Atlassian Bitbucket Pipelines | [08 …](08%20Provider%20%E2%80%94%20Terraform%20Cloud%2C%20Bitbucket%2C%20Jenkins.md) |

## Integrationsfähigkeit

Workload Identity Federation ermöglicht sowohl den **Databricks-SDKs** als auch der **Databricks CLI**, sich sicher bei Databricks zu authentifizieren, **ohne** Secret-Credentials in der CI/CD-Umgebung vorzuhalten.

## Ablauf (allgemein)

1. **Federation Policy erstellen** (Service-Principal-Federation-Policy) — siehe [03 Federation Policy konfigurieren.md](03%20Federation%20Policy%20konfigurieren.md).
2. **CI/CD-Pipeline konfigurieren** — Umgebungsvariablen setzen (`DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_AUTH_TYPE` bzw. OIDC-Token-Variable).
3. SDK/CLI holen das Workload-Identity-Token automatisch und tauschen es gegen ein Databricks-OAuth-Token.

## Quelle

- https://docs.databricks.com/aws/en/dev-tools/auth/oauth-federation-provider

**Stand:** 2026-08-28.
