# Benutzerzugriff auf Databricks mit OAuth autorisieren (U2M)

OAuth 2.0 User-to-Machine (U2M) für Entwicklerwerkzeuge und REST-APIs — automatischer Ablauf (empfohlen) und manueller Ablauf für Werkzeuge ohne Unified-Authentication-Unterstützung. Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Autorisierungsmethoden](#methoden)
3. [Automatische Autorisierung einrichten](#automatisch)
4. [Manuelle OAuth-Token-Generierung](#manuell)
5. [Service-Principal-Authentifizierung](#sp)
6. [OAuth-Consent verwalten](#consent)
7. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

Databricks nutzt **OAuth 2.0** als bevorzugtes Autorisierungsprotokoll für Entwicklerwerkzeuge und REST-APIs. Unterschieden wird zwischen *Autorisierung* (Zugriffsgewährung per OAuth) und *Authentifizierung* (Validierung der Credentials über Access-Tokens). Jedes Token ist **eine Stunde** gültig und wird danach automatisch erneuert.

## <a id="methoden">2. Autorisierungsmethoden</a>

1. **Automatisch (empfohlen):** nutzt Unified Authentication mit kompatiblen Werkzeugen (CLI, Terraform, SDKs …); Token-Generierung und -Refresh laufen automatisch.
2. **Manuell:** für Drittanbieter-Werkzeuge ohne Unified-Authentication-Unterstützung; erfordert das Erzeugen von Code-Verifier/Code-Challenge-Paaren und das Eintauschen von Authorization Codes gegen Tokens.

## <a id="automatisch">3. Automatische Autorisierung einrichten</a>

### Umgebungsvariablen — Account-Ebene

```bash
DATABRICKS_HOST=https://accounts.cloud.databricks.com
DATABRICKS_ACCOUNT_ID=<your-account-id>
```

### Umgebungsvariablen — Workspace-Ebene

```bash
DATABRICKS_HOST=https://dbc-a1b2345c-d6e7.cloud.databricks.com
```

### Konfigurationsprofil (`.databrickscfg`)

**Account-Ebene:**

```ini
[profile-name]
host=https://accounts.cloud.databricks.com
account_id=<account-id>
```

**Workspace-Ebene:**

```ini
[profile-name]
host=<workspace-url>
```

Anschließend `databricks auth login` verwenden (siehe [14 Konfigurationsprofile.md](14%20Konfigurationsprofile.md)).

## <a id="manuell">4. Manuelle OAuth-Token-Generierung</a>

### Schritt 1: Code-Verifier und Code-Challenge erzeugen

```python
import hashlib, base64, secrets, string

allowed_chars = string.ascii_letters + string.digits + "-._~"
code_verifier = ''.join(secrets.choice(allowed_chars) for _ in range(64))
sha256_hash = hashlib.sha256(code_verifier.encode()).digest()
code_challenge = base64.urlsafe_b64encode(sha256_hash).decode().rstrip("=")

print(f"code_verifier:  {code_verifier}")
print(f"code_challenge: {code_challenge}")
```

Der Code-Verifier muss **43–128 Zeichen** aus dem erlaubten Zeichensatz (PKCE-Standard) haben; die Code-Challenge ist der Base64-URL-kodierte SHA256-Hash davon.

### Schritt 2: Authorization Code erzeugen

**Account-Ebene:**

```
https://accounts.cloud.databricks.com/oidc/accounts/<account-id>/v1/authorize?client_id=databricks-cli&redirect_uri=<redirect-url>&response_type=code&state=<state>&code_challenge=<code-challenge>&code_challenge_method=S256&scope=all-apis+offline_access
```

**Workspace-Ebene:**

```
https://<databricks-instance>/oidc/v1/authorize?client_id=databricks-cli&redirect_uri=<redirect-url>&response_type=code&state=<state>&code_challenge=<code-challenge>&code_challenge_method=S256&scope=all-apis+offline_access
```

Nach dem Login den Authorization Code aus dem `code=`-Parameter der Redirect-URL kopieren und prüfen, dass der `state`-Wert dem ursprünglich gesendeten entspricht.

### Schritt 3: Code gegen Access-Token tauschen

**Account-Ebene:**

```bash
curl --request POST \
https://accounts.cloud.databricks.com/oidc/accounts/<account-id>/v1/token \
--data "client_id=databricks-cli" \
--data "grant_type=authorization_code" \
--data "scope=all-apis offline_access" \
--data "redirect_uri=<redirect-url>" \
--data "code_verifier=<code-verifier>" \
--data "code=<authorization-code>"
```

**Workspace-Ebene:**

```bash
curl --request POST \
https://<databricks-instance>/oidc/v1/token \
--data "client_id=databricks-cli" \
--data "grant_type=authorization_code" \
--data "scope=all-apis offline_access" \
--data "redirect_uri=<redirect-url>" \
--data "code_verifier=<code-verifier>" \
--data "code=<authorization-code>"
```

Die Antwort enthält `access_token`, `refresh_token`, `token_type`, `scope` und `expires_in` (3600 Sekunden).

### Schritt 4: API-Anfragen

**Account-Ebene:**

```bash
export OAUTH_TOKEN=<oauth-access-token>
curl --request GET --header "Authorization: Bearer $OAUTH_TOKEN" \
"https://accounts.cloud.databricks.com/api/2.0/accounts/<account-id>/workspaces"
```

**Workspace-Ebene:**

```bash
export OAUTH_TOKEN=<oauth-access-token>
curl --request GET --header "Authorization: Bearer $OAUTH_TOKEN" \
"https://<databricks-instance>/api/2.0/clusters/list"
```

## <a id="sp">5. Service-Principal-Authentifizierung (Beta)</a>

Beta-Feature: Token-Generierung im Namen eines Service Principals. Benutzer mit der Rolle **„Service Principal Manager"** können sich authentifizieren, indem sie den Service Principal während des OAuth-Flows auswählen. Das resultierende Token trägt die Identität des Service Principals im `sub`-Claim.

## <a id="consent">6. OAuth-Consent verwalten</a>

Genehmigte Scopes anzeigen:

```bash
curl --request GET \
  --header "Authorization: Bearer $OAUTH_TOKEN" \
  "https://<databricks-instance>/api/2.0/oauth-app-integrations/<app-integration-id>/user-consent/me"
```

Consent widerrufen:

```bash
curl --request DELETE \
  --header "Authorization: Bearer $OAUTH_TOKEN" \
  "https://<databricks-instance>/api/2.0/oauth-app-integrations/<app-integration-id>/user-consent/me"
```

> **Hinweis:** Das Widerrufen des Consent macht bestehende Tokens nicht ungültig; Refresh-Tokens bleiben bis zum Ablauf gültig.

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/auth/oauth-u2m

**Stand:** 2026-08-28.
