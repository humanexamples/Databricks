# Workload Identity Federation für GitHub Actions aktivieren

Konfiguration von OAuth Token Federation (OIDC) für GitHub-Actions-Workloads. Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Überblick

OAuth Token Federation (OIDC) erlaubt automatisierten Workloads außerhalb von Databricks den sicheren Zugriff **ohne Databricks-Secrets**. Zwei Schritte:

1. **Federation Policy erstellen.**
2. **GitHub-Actions-YAML konfigurieren.**

Danach holen die Databricks-SDKs und die Databricks CLI die Workload-Identity-Tokens von GitHub Actions automatisch und tauschen sie gegen Databricks-OAuth-Tokens.

---

## 1. Federation Policy erstellen

Parameter für GitHub Actions:

| Feld | Wert |
|---|---|
| **Organization** | Deine GitHub-Organisation (z. B. `databricks-inc` aus `https://github.com/databricks-inc/data-platform`) |
| **Repository** | Das erlaubte Repository (z. B. `data-platform`) |
| **Entity type** | Empfohlen: **Environment** |
| **Issuer URL** | `https://token.actions.githubusercontent.com` |
| **Audiences** | Deine Databricks-Account-ID (Default, falls weggelassen) |
| **Subject claim** | Üblicherweise `sub` für Standard-Workflows |

### Beispiel: Policy anlegen (Databricks CLI)

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

(`5581763342009999` = numerische ID des Service Principals; `a2222dd9-…` = Audience / Account-ID.)

---

## 2. GitHub-Actions-YAML konfigurieren

Umgebungsvariablen im Workflow:

| Variable | Wert |
|---|---|
| `DATABRICKS_AUTH_TYPE` | `github-oidc` |
| `DATABRICKS_HOST` | Deine Workspace-URL |
| `DATABRICKS_CLIENT_ID` | Client-/Application-ID des Service Principals |

### Basis-Workflow

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

> `permissions: id-token: write` ist erforderlich, damit GitHub überhaupt ein OIDC-Token ausstellt.

---

## 3. Authentifizierung aus wiederverwendbaren Workflows (Reusable Workflows)

Für wiederverwendbare Workflows den `subject_claim` in der Policy auf `job_workflow_ref` setzen.

### Policy für Reusable Workflow

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

### Reusable-Workflow-Datei (`deploy.yml`)

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

### Aufrufender Workflow (Calling Workflow)

```yaml
on: workflow_dispatch
permissions:
  id-token: write
  contents: read
jobs:
  call-deploy:
    uses: my-github-org/shared-workflows/.github/workflows/deploy.yml@main
```

> **Wichtig:** `permissions: id-token: write` **nur im aufrufenden Workflow** setzen. „GitHub nimmt den `job_workflow_ref`-Claim nur dann in das OIDC-Token auf, wenn `id-token: write` im aufrufenden Workflow gewährt ist."

---

## Quelle

- https://docs.databricks.com/aws/en/dev-tools/auth/provider-github

**Stand:** 2026-08-28.
