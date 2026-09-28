# Workload Identity Federation für Azure DevOps Pipelines aktivieren

Konfiguration von OAuth Token Federation (OIDC) für Azure-DevOps-Pipelines. Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Überblick

OAuth Token Federation (OIDC) erlaubt automatisierten Workloads außerhalb von Databricks den sicheren Zugriff **ohne Databricks-Secrets**. Zwei Aufgaben:

1. **Federation Policy erstellen.**
2. **Azure-DevOps-Pipeline-YAML konfigurieren.**

Danach holen die Databricks-SDKs und die CLI die Workload-Identity-Tokens von Azure DevOps automatisch und tauschen sie gegen Databricks-OAuth-Tokens.

---

## 1. Federation Policy erstellen

Werte für Azure DevOps:

| Feld | Wert |
|---|---|
| **Issuer URL** | `https://vstoken.dev.azure.com/<org_id>` (`<org_id>` = GUID deiner Azure-DevOps-Organisation) |
| **Audiences** | `api://AzureADTokenExchange` |
| **Subject** | `p://<org-name>/<project-name>/<pipeline-name>` |

### Beispiel-Befehl

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

---

## 2. Azure-DevOps-Pipeline-YAML konfigurieren

Umgebungsvariablen in der Pipeline-YAML:

| Variable | Wert |
|---|---|
| `DATABRICKS_AUTH_TYPE` | `azure-devops-oidc` |
| `DATABRICKS_HOST` | Deine Databricks-Workspace-URL |
| `DATABRICKS_CLIENT_ID` | Client-/Application-ID des Service Principals |
| `SYSTEM_ACCESSTOKEN` | auf die Pipeline-Variable `$(System.AccessToken)` mappen |

### Beispiel-YAML

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

> `SYSTEM_ACCESSTOKEN` muss explizit im `env:`-Block des Steps gesetzt werden — Azure DevOps stellt `System.AccessToken` sonst nicht als Umgebungsvariable bereit.

---

## Quelle

- https://docs.databricks.com/aws/en/dev-tools/auth/provider-azure-devops

**Stand:** 2026-08-28.
