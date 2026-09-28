# Umgebungsvariablen und Felder für Unified Authentication

Referenz aller Konfigurationsoptionen, die einheitlich über Databricks CLI, Terraform Provider und die SDKs für Python, Java und Go funktionieren. Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Abschnittsübersicht

1. [Allgemeine Konfigurationsfelder](#allgemein)
2. [Felder für Benutzer und Service Principals](#user-sp)
3. [`.databrickscfg`-spezifische Felder](#cfg)
4. [Authentifizierungsfelder](#auth)
5. [Unterstützte Authentifizierungstypen](#auth-typen)
6. [Quelle](#quelle)

---

## <a id="allgemein">1. Allgemeine Konfigurationsfelder</a>

| Gebräuchlicher Name | Beschreibung | Umgebungsvariable | `.databrickscfg`- / Terraform-Feld | `Config`-Feld |
|---|---|---|---|---|
| Databricks host | (String) Host-URL des Workspace-Endpunkts **oder** des Account-Endpunkts. | `DATABRICKS_HOST` | `host` | `host` (Python), `setHost` (Java), `Host` (Go) |
| Databricks token | (String) Der Databricks Personal Access Token. | `DATABRICKS_TOKEN` | `token` | `token` (Python), `setToken` (Java), `Token` (Go) |
| Databricks account ID | (String) Account-ID für den Account-Endpunkt. Nur wirksam, wenn der Host auch auf `https://accounts.cloud.databricks.com` gesetzt ist. | `DATABRICKS_ACCOUNT_ID` | `account_id` | `account_id` (Python), `setAccountID` (Java), `AccountID` (Go) |
| Cluster ID | (String) ID des zu verwendenden Clusters. | `DATABRICKS_CLUSTER_ID` | `cluster_id` | `cluster_id` |
| Serverless compute | (String) Auto-Enablement für Serverless Compute. Gültiger Wert: `auto`. | `DATABRICKS_SERVERLESS_COMPUTE_ID` | `serverless_compute_id` | `serverless_compute_id` |

## <a id="user-sp">2. Felder für Benutzer und Service Principals</a>

| Gebräuchlicher Name | Beschreibung | Umgebungsvariable | `.databrickscfg`- / Terraform-Feld | `Config`-Feld |
|---|---|---|---|---|
| Databricks username | (String) Benutzername des Databricks-Benutzers. | `DATABRICKS_USERNAME` | `username` | `username` (Python), `setUsername` (Java), `Username` (Go) |
| Service principal client ID | (String) Client-ID des Databricks-Service-Principals. | `DATABRICKS_CLIENT_ID` | `client_id` | `client_id` (Python), `setClientId` (Java), `ClientId` (Go) |
| Service principal secret | (String) Secret des Databricks-Service-Principals. | `DATABRICKS_CLIENT_SECRET` | `client_secret` | `client_secret` (Python), `setClientSecret` (Java), `ClientSecret` (Go) |

## <a id="cfg">3. `.databrickscfg`-spezifische Felder</a>

Für nicht-standardmäßige `.databrickscfg`-Einstellungen (siehe [14 Konfigurationsprofile.md](14%20Konfigurationsprofile.md)):

| Gebräuchlicher Name | Beschreibung | Umgebungsvariable | Terraform-Feld | `Config`-Feld |
|---|---|---|---|---|
| `.databrickscfg`-Dateipfad | (String) Nicht-Standard-Pfad zur `.databrickscfg`-Datei. | `DATABRICKS_CONFIG_FILE` | `config_file` | `config_file` (Python), `setConfigFile` (Java), `ConfigFile` (Go) |
| `.databrickscfg`-Default-Profil | (String) Zu verwendendes Default-Profil (statt `DEFAULT`). | `DATABRICKS_CONFIG_PROFILE` | `profile` | `profile` (Python), `setProfile` (Java), `Profile` (Go) |

## <a id="auth">4. Authentifizierungsfelder</a>

Zum Erzwingen eines bestimmten Authentifizierungstyps:

| Gebräuchlicher Name | Beschreibung | Umgebungsvariable | Terraform-Feld | `Config`-Feld |
|---|---|---|---|---|
| Databricks authentication type | (String) Wenn mehrere Auth-Attribute in der Umgebung verfügbar sind, den hier angegebenen Typ verwenden. | `DATABRICKS_AUTH_TYPE` | `auth_type` | `auth_type` (Python), `setAuthType` (Java), `AuthType` (Go) |
| OIDC token environment variable | (String) Name der Umgebungsvariable mit dem vom IdP ausgestellten OIDC-Token. Für Auth-Typ `env-oidc`. Default: `DATABRICKS_OIDC_TOKEN`. | `DATABRICKS_OIDC_TOKEN_ENV` | `oidc_token_env` | `oidc_token_env` (Python), `setOIDCTokenEnv` (Java), `OIDCTokenEnv` (Go) |
| OIDC token file path | (String) Pfad zu einer lokalen Datei mit dem vom IdP ausgestellten OIDC-Token. Für Auth-Typ `file-oidc`. | `DATABRICKS_OIDC_TOKEN_FILEPATH` | `oidc_token_filepath` | `oidc_token_filepath` (Python), `setOIDCTokenFilepath` (Java), `OIDCTokenFilepath` (Go) |

## <a id="auth-typen">5. Unterstützte Authentifizierungstypen</a>

Gültige Werte für das Feld `auth_type` / `DATABRICKS_AUTH_TYPE`:

| Wert | Bedeutung |
|---|---|
| `oauth-m2m` | Machine-to-Machine-Authentifizierung mit einem Service Principal über OAuth 2.0. |
| `pat` | Authentifizierung mit einem Databricks Personal Access Token. |
| `databricks-cli` | Interaktive Anmeldung mit der Databricks CLI über OAuth 2.0. |
| `oidc-token` | Token Federation mit einem IdP; Databricks tauscht ein vom IdP ausgestelltes OIDC-Token gegen ein Databricks-OAuth-Token. |
| `env-oidc` | Federation, wenn das IdP-Token in einer Umgebungsvariable liegt (`DATABRICKS_OIDC_TOKEN`). |
| `file-oidc` | Federation, wenn das IdP-Token in einer lokalen Datei liegt (`DATABRICKS_OIDC_TOKEN_FILEPATH`). |
| `github-oidc` | Föderierte GitHub-Actions-Authentifizierung über OIDC-Tokens. |
| `azure-devops-oidc` | Föderierte Azure-DevOps-Authentifizierung über OIDC-Tokens. |

## <a id="quelle">6. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/auth/env-vars

**Stand:** 2026-08-28.
