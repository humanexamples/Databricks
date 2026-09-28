# Workload Identity Federation für Terraform Cloud, Bitbucket Pipelines oder Jenkins aktivieren

Konfiguration von OAuth Token Federation (OIDC) für generische bzw. dateibasierte/umgebungsbasierte OIDC-Token-Provider. Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Überblick

OAuth Token Federation (OIDC) erlaubt automatisierten Workloads außerhalb von Databricks den sicheren Zugriff **ohne Databricks-Secrets**. Nach der Konfiguration holen die Databricks-SDKs und die CLI die Workload-Identity-Tokens automatisch vom Identity Provider und tauschen sie gegen Databricks-OAuth-Tokens.

---

## Schritt 1: Federation Policy erstellen

Eine benutzerdefinierte Workload-Identity-Federation-Policy anlegen mit:

- **Issuer URL** — Token-URL des Providers
- **Audiences** — ein Organisations-Identifier
- **Subject** — Wert, der den Job-/Projekt-Kontext angibt

Beispiel (Databricks CLI) für eine GitLab-Konfiguration:

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

---

## Schritt 2: Identity Provider konfigurieren

Umgebungsvariablen je nach CI/CD-Plattform. Relevante Databricks-Auth-Typen: `env-oidc` (Token in Umgebungsvariable) und `file-oidc` (Token in Datei).

### Jenkins

`DATABRICKS_OIDC_TOKEN` setzen **oder** `DATABRICKS_OIDC_TOKEN_FILEPATH` auf eine Token-Datei zeigen lassen.

### Terraform Cloud

```bash
DATABRICKS_OIDC_TOKEN_ENV = TFC_WORKLOAD_IDENTITY_TOKEN
```

(Terraform Cloud stellt sein Workload-Identity-Token in der Umgebungsvariable `TFC_WORKLOAD_IDENTITY_TOKEN` bereit; `DATABRICKS_OIDC_TOKEN_ENV` verweist Databricks darauf.)

### Bitbucket Pipelines

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

> `oidc: true` im Step aktiviert die Ausgabe des OIDC-Tokens in `BITBUCKET_STEP_OIDC_TOKEN`.

---

## Relevante Databricks-Auth-Typen

| Auth-Typ | Bedeutung |
|---|---|
| `env-oidc` | IdP-Token liegt in einer Umgebungsvariable (Name über `DATABRICKS_OIDC_TOKEN_ENV`, Default `DATABRICKS_OIDC_TOKEN`) |
| `file-oidc` | IdP-Token liegt in einer lokalen Datei (Pfad über `DATABRICKS_OIDC_TOKEN_FILEPATH`) |
| `oidc-token` | generischer Token-Exchange gegen einen IdP |

---

## Quelle

- https://docs.databricks.com/aws/en/dev-tools/auth/provider-other

**Stand:** 2026-08-28.
