# Authentifizierung für Entwicklerwerkzeuge — Überblick

Diese Reihe fasst die offizielle Databricks-Dokumentation zum Thema **„Authenticate access to Databricks"** (Entwicklerwerkzeuge und Automatisierung) auf Deutsch zusammen. Sie deckt ab, wie sich Benutzer, Service Principals und automatisierte Workloads gegenüber Databricks-Workspaces und dem Databricks-Account authentifizieren — von OAuth-Token-Federation über Service Principals bis hin zu den Legacy Personal Access Tokens.

## Kernaussagen

- **Zwei Identitätstypen:** *Benutzerkonten* für interaktive Nutzung (CLI-Befehle, API-Aufrufe) und *Service Principals* für automatisierte, unbeaufsichtigte Abläufe (CI/CD).
- **Zwei API-Ebenen:** *Account-Level-APIs* (nur Account-Owner/-Admins) und *Workspace-Level-APIs* (Workspace-Benutzer und -Admins).
- **Empfohlene Autorisierungsmethoden (in dieser Reihenfolge):**
  1. **OAuth Token Federation** — Tokens des eigenen Identity Providers (IdP) für Benutzer oder Service Principals; keine Databricks-Secrets mehr zu verwalten oder zu rotieren.
  2. **OAuth M2M (Machine-to-Machine)** — kurzlebige Tokens für Service Principals in CI/CD und vollautomatisierten Abläufen.
  3. **OAuth U2M (User-to-Machine)** — kurzlebige Tokens für Benutzer-Szenarien mit browserbasierter Anmeldung.
- **Databricks Unified Authentication** vereinheitlicht die Credential-Verwaltung über alle Databricks-Werkzeuge und SDKs hinweg (gleiche Umgebungsvariablen, gleiche `.databrickscfg`-Profile).
- **Personal Access Tokens (PATs)** gelten als *Legacy*; Databricks empfiehlt stattdessen OAuth.

## Themen in diesem Kapitel

1. **Zugriff auf Databricks autorisieren** — Account-/API-Typen und Methodenüberblick. Siehe [01 Zugriff auf Databricks autorisieren.md](01%20Zugriff%20auf%20Databricks%20autorisieren.md).
2. **OAuth Token Federation — Überblick** — was Token Federation ist und welche Typen es gibt. Siehe [02 OAuth Token Federation — Ueberblick.md](02%20OAuth%20Token%20Federation%20%E2%80%94%20Ueberblick.md).
3. **Federation Policy konfigurieren** — Account-weite Policy und Service-Principal-Policy (UI, CLI, API). Siehe [03 Federation Policy konfigurieren.md](03%20Federation%20Policy%20konfigurieren.md).
4. **Workload Identity Federation in CI/CD aktivieren** — Provider-Übersicht. Siehe [04 Workload Identity Federation in CI-CD aktivieren.md](04%20Workload%20Identity%20Federation%20in%20CI-CD%20aktivieren.md).
5. **Provider — GitHub Actions**. Siehe [05 Provider — GitHub Actions.md](05%20Provider%20%E2%80%94%20GitHub%20Actions.md).
6. **Provider — Azure DevOps Pipelines**. Siehe [06 Provider — Azure DevOps.md](06%20Provider%20%E2%80%94%20Azure%20DevOps.md).
7. **Provider — AWS IAM Workloads**. Siehe [07 Provider — AWS IAM.md](07%20Provider%20%E2%80%94%20AWS%20IAM.md).
8. **Provider — Terraform Cloud, Bitbucket Pipelines, Jenkins, GitLab, CircleCI**. Siehe [08 Provider — Terraform Cloud, Bitbucket, Jenkins.md](08%20Provider%20%E2%80%94%20Terraform%20Cloud%2C%20Bitbucket%2C%20Jenkins.md).
9. **Mit einem IdP-Token authentifizieren (Token Exchange)** — den föderierten JWT gegen ein Databricks-OAuth-Token tauschen. Siehe [09 Mit IdP-Token authentifizieren (Token Exchange).md](09%20Mit%20IdP-Token%20authentifizieren%20%28Token%20Exchange%29.md).
10. **OAuth U2M — Benutzerzugriff autorisieren** — automatischer und manueller OAuth-Flow. Siehe [10 OAuth U2M — Benutzerzugriff.md](10%20OAuth%20U2M%20%E2%80%94%20Benutzerzugriff.md).
11. **Service Principals für CI/CD**. Siehe [11 Service Principals für CI-CD.md](11%20Service%20Principals%20f%C3%BCr%20CI-CD.md).
12. **Databricks Unified Authentication** — Auswertungsreihenfolge der Methoden. Siehe [12 Unified Authentication.md](12%20Unified%20Authentication.md).
13. **Umgebungsvariablen und Felder** — Referenztabellen für alle Auth-Felder. Siehe [13 Umgebungsvariablen und Felder.md](13%20Umgebungsvariablen%20und%20Felder.md).
14. **Konfigurationsprofile (`.databrickscfg`)**. Siehe [14 Konfigurationsprofile.md](14%20Konfigurationsprofile.md).
15. **Personal Access Tokens (PAT) — Legacy**. Siehe [15 Personal Access Tokens (PAT).md](15%20Personal%20Access%20Tokens%20%28PAT%29.md).

## Verwandte Kapitel

- [Databricks Asset Bundles → Deployment-Modi und Authentifizierung](../03%20Databricks%20Asset%20Bundles/07%20Deployment-Modi%20und%20Authentifizierung.md)
- [CI-CD](../02%20CI-CD/)
- [Terraform](../04%20Terraform/)

## Quellen

- https://docs.databricks.com/aws/en/dev-tools/auth/
- (weitere Quellen je Unterdatei)

**Stand:** 2026-08-28.
