# Service Principals für CI/CD

Service Principals als Identität für automatisierte Werkzeuge und Anwendungen (CI/CD). Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Warum Service Principals statt Benutzerkonten?](#warum)
3. [Einrichtung in drei Schritten](#setup)
4. [GitHub Actions](#github)
5. [GitLab CI/CD](#gitlab)
6. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

„Ein Service Principal ist eine Identität, die für den Einsatz mit automatisierten Werkzeugen und Anwendungen erstellt wird." Empfohlen für CI/CD-Plattformen wie **GitHub Actions, Azure Pipelines und GitLab CI/CD** sowie **Airflow** und **Jenkins**.

## <a id="warum">2. Warum Service Principals statt Benutzerkonten?</a>

Databricks empfiehlt Service Principals gegenüber Personal Access Tokens von Benutzern, weil sie mehrere Vorteile bieten:

- **Unabhängige Zugriffssteuerung:** „Zugriff auf Databricks-Ressourcen kann für einen Databricks-Service-Principal unabhängig von einem Benutzer gewährt und eingeschränkt werden."
- **Token-Schutz:** Benutzer müssen ihre persönlichen Access-Tokens nicht gegenüber CI/CD-Plattformen offenlegen.
- **Einfaches Deprovisioning:** „Ein Databricks-Service-Principal kann vorübergehend deaktiviert oder dauerhaft gelöscht werden, ohne andere Benutzer zu beeinträchtigen."
- **Organisatorische Änderungen:** Wenn Mitarbeitende das Unternehmen verlassen, bleibt der Service-Principal-Zugriff unberührt.

## <a id="setup">3. Einrichtung in drei Schritten</a>

1. **Service Principal im Workspace erstellen.**
2. **Databricks-Access-Token für den Service Principal generieren.**
3. **Das Token der CI/CD-Plattform bereitstellen.**

> Für Schritt 1 und 2 verweist die Doku auf die allgemeine **Service-principals**-Dokumentation (Account-/Workspace-Verwaltung) und auf [15 Personal Access Tokens (PAT).md](15%20Personal%20Access%20Tokens%20%28PAT%29.md) → Abschnitt *„Personal Access Tokens für Service Principals erstellen"* (Befehl `databricks token-management create-obo-token`).
>
> Alternativ zu langlebigen Tokens: **OAuth Token Federation** ohne Secrets — siehe [04 Workload Identity Federation in CI-CD aktivieren.md](04%20Workload%20Identity%20Federation%20in%20CI-CD%20aktivieren.md).

## <a id="github">4. GitHub Actions</a>

Zwei **verschlüsselte GitHub-Secrets** (encrypted secrets) im Repository registrieren — **nicht** direkt in die Workflow-Datei schreiben:

| Secret | Wert |
|---|---|
| `DATABRICKS_HOST` | `https://` gefolgt vom Workspace-Instanznamen, z. B. `https://dbc-a1b2345c-d6e7.cloud.databricks.com` |
| `DATABRICKS_TOKEN` | der `token_value`, den du nach dem Erstellen des Access-Tokens kopiert hast |

Repräsentativer Workflow (Databricks CLI mit PAT-Authentifizierung über die beiden Umgebungsvariablen):

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

## <a id="gitlab">5. GitLab CI/CD</a>

Analog zu GitHub: **CI/CD-Variablen** auf Projektebene anlegen (GitLab-Doku: *„Add a CI/CD variable to a project"*), mit denselben Namen und Werten:

| Variable | Wert |
|---|---|
| `DATABRICKS_HOST` | Workspace-URL (`https://…`) |
| `DATABRICKS_TOKEN` | `token_value` des Service Principals |

Repräsentative `.gitlab-ci.yml`:

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

## <a id="quelle">6. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/auth/service-principals

**Stand:** 2026-08-28.
