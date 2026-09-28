# Zugriff auf Databricks-Ressourcen autorisieren

Einstiegsseite der Databricks-Dokumentation zur Authentifizierung von Entwicklerwerkzeugen. Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Abschnittsübersicht

1. [Account- und API-Typen](#account-api)
2. [Autorisierungsmethoden](#methoden)
3. [Unified-Authentication-Konfiguration](#unified)
4. [Integrationen von Drittanbietern](#drittanbieter)
5. [Quelle](#quelle)

---

## <a id="account-api">1. Account- und API-Typen</a>

Databricks kennt zwei **Account-Typen** für die Authentifizierung:

- **Benutzerkonten (user accounts)** — für interaktive CLI-Befehle und API-Aufrufe.
- **Service Principals** — für automatisierte, unbeaufsichtigte Abläufe.

Die Plattform unterstützt zwei **API-Ebenen**:

- **Account-Level-APIs** — verfügbar für Account-Owner und Account-Admins.
- **Workspace-Level-APIs** — verfügbar für Workspace-Benutzer und Workspace-Admins.

## <a id="methoden">2. Autorisierungsmethoden</a>

Databricks empfiehlt drei primäre Ansätze:

1. **OAuth Token Federation** — „OAuth-Tokens deines Identity Providers für Benutzer oder Service Principals", die das Verwalten von Databricks-Secrets überflüssig machen. Siehe [02 OAuth Token Federation — Überblick.md](02%20OAuth%20Token%20Federation%20%E2%80%94%20Ueberblick.md).

2. **OAuth M2M (Machine-to-Machine)** — kurzlebige Tokens für Service Principals in CI/CD und vollautomatisierten Workflows.

3. **OAuth U2M (User-to-Machine)** — kurzlebige Tokens für Benutzer-Szenarien, die eine browserbasierte Authentifizierung erfordern. Siehe [10 OAuth U2M — Benutzerzugriff.md](10%20OAuth%20U2M%20%E2%80%94%20Benutzerzugriff.md).

## <a id="unified">3. Unified-Authentication-Konfiguration</a>

Unified Authentication standardisiert die Credential-Verwaltung über alle Databricks-Werkzeuge hinweg. Die Konfiguration erfolgt typischerweise über Umgebungsvariablen:

| Umgebungsvariable | Bedeutung |
|---|---|
| `DATABRICKS_HOST` | URL der Account-Konsole **oder** des Workspaces |
| `DATABRICKS_ACCOUNT_ID` | Databricks-Account-ID |
| `DATABRICKS_CLIENT_ID` | Client-ID des Service Principals (nur OAuth) |
| `DATABRICKS_CLIENT_SECRET` | Secret des Service Principals (nur OAuth) |

Statt Umgebungsvariablen manuell zu setzen, können Organisationen Credentials in **`.databrickscfg`-Konfigurationsprofilen** lokal ablegen. Siehe [14 Konfigurationsprofile.md](14%20Konfigurationsprofile.md) und [12 Unified Authentication.md](12%20Unified%20Authentication.md).

## <a id="drittanbieter">4. Integrationen von Drittanbietern</a>

Databricks integriert sich über Service-Principal-Authentifizierung mit **Terraform, GitHub, GitLab, Bitbucket und Jenkins**.

## <a id="quelle">5. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/auth/

**Stand:** 2026-08-28.
