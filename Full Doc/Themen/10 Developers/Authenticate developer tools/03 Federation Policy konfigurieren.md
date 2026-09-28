# Federation Policy konfigurieren

OAuth Token Federation erfordert eine **Federation Policy** — entweder Account-weit oder pro Workload (Service Principal). Diese Seite beschreibt Erstellung und Konfiguration. Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Abschnittsübersicht

1. [Workload Identity Federation](#workload)
2. [Service-Principal-Federation-Policy konfigurieren](#sp-policy)
3. [Beispiel-Policies für Service Principals](#beispiele-sp)
4. [Best Practices für Service-Principal-Federation-Policies](#best-practices)
5. [Account-weite Token Federation](#account-wide)
6. [Account-Federation-Policy konfigurieren](#account-policy)
7. [Beispiel-Account-Federation-Policies](#beispiele-account)
8. [Nächste Schritte](#next)
9. [Quelle](#quelle)

---

## <a id="workload">1. Workload Identity Federation</a>

Workload Identity Federation erlaubt automatisierten Workloads außerhalb von Databricks den Zugriff auf Databricks-APIs **ohne Databricks-Secrets**. Account-Admins konfigurieren dies über eine **Service-Principal-Federation-Policy**.

Eine Service-Principal-Federation-Policy ist mit einem Service Principal im Databricks-Account verknüpft und legt fest:

- Den **Identity Provider (Issuer)**, von dem sich der Service Principal authentifizieren darf.
- Die **Workload Identity (Subject)**, die als Databricks-Service-Principal authentifiziert werden darf.

**Beispiel** einer Service-Principal-Federation-Policy für einen GitHub-Actions-Workload:

- **Issuer:** `https://token.actions.githubusercontent.com`
- **Audiences:** `https://github.com/my-github-org`
- **Subject:** `repo:my-github-org/my-repo:environment:prod`

Passender JWT-Body zur Authentifizierung bei Databricks:

```json
{
  "iss": "https://token.actions.githubusercontent.com",
  "aud": "https://github.com/my-github-org",
  "sub": "repo:my-github-org/my-repo:environment:prod"
}
```

## <a id="sp-policy">2. Service-Principal-Federation-Policy konfigurieren</a>

Account-Admins konfigurieren die Policy über die [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/) oder die Databricks-API. **Maximal 20 Service-Principal-Federation-Policies pro Service Principal.**

Anzugebende Felder:

- **Issuer-URL:** HTTPS-URL, die den Workload-Identity-Provider identifiziert; steht im `iss`-Claim der Workload-Identity-Tokens.
- **Subject:** eindeutige Kennung des Workloads in dessen Laufzeitumgebung. Ohne Angabe: Default `sub`.
- **Audiences:** vorgesehener Empfänger des Tokens (`aud`-Claim). Match, wenn die Audience mindestens einer Audience in der Policy entspricht. Ohne Angabe: Default = Databricks-Account-ID.
- **Subject claim (optional):** Token-Claim, der die Workload Identity (das Subject) enthält. Ohne Angabe verwendet Databricks `sub`. Databricks **empfiehlt, bei `sub` zu bleiben**; ein anderer Claim nur, wenn `sub` kein geeigneter/stabiler Identifier ist (selten).
- **Token-Signaturvalidierung (optional):** öffentliche Schlüssel bzw. deren URL im **JWKS-Format** (JSON Web Key Sets). JWKS-JSON unterstützt bis zu 5 Schlüssel; bei mehr eine **JWKS-URI** verwenden.
  - Ohne Angabe holt Databricks die Schlüssel vom Well-Known-Endpoint des Issuers (empfohlen). Der IdP muss OpenID Provider Metadata unter `<issuer-url>/.well-known/openid-configuration` bereitstellen, inklusive `jwks_uri`.

### 2a. Über die Databricks-UI

1. Als Account-Admin bei der Account-Konsole anmelden: `https://accounts.cloud.databricks.com`.
2. **User management** öffnen.
3. Zum Tab **Service principals** wechseln.
4. Den Service Principal auswählen, für den die Policy gelten soll.
5. Tab **Credentials & secrets** öffnen.
6. Unter **Federation policies** auf **Create policy** klicken.
7. Einen föderierten Credential Provider wählen und die zugehörigen Felder ausfüllen.
8. **Create policy** klicken.

> Die Databricks CLI kann **nicht** im [Web-Terminal](https://docs.databricks.com/aws/en/compute/web-terminal) des Workspaces zum Anlegen einer Federation Policy verwendet werden.

### 2b. Über die Databricks CLI

1. Neueste Version der Databricks CLI installieren bzw. aktualisieren.
2. Als Account-Admin am Databricks-Account authentifizieren. `ACCOUNT_CONSOLE_URL` und `ACCOUNT_ID` angeben:

   ```bash
   databricks auth login --host ${ACCOUNT_CONSOLE_URL} --account-id ${ACCOUNT_ID}
   ```

3. Die **numerische ID** des Service Principals ermitteln (z. B. `3659993829438643`). Wenn die Application-ID (GUID, z. B. `bc3cfe6c-469e-4130-b425-5384c4aa30bb`) bekannt ist:

   ```bash
   databricks account service-principals list --filter 'applicationId eq "<service-principal-application-id>"'
   ```

4. Die Service-Principal-Federation-Policy erstellen. Beispiel für eine GitHub Action:

   ```bash
   databricks account service-principal-federation-policy create ${SERVICE_PRINCIPAL_NUMERIC_ID} --json '{
     "oidc_policy": {
       "issuer": "https://token.actions.githubusercontent.com",
       "audiences": [
         "https://github.com/my-github-org"
       ],
       "subject": "repo:my-github-org/my-repo:environment:prod"
     }
   }'
   ```

### 2c. Über die Databricks Account API

1. Numerische Service-Principal-ID (z. B. `3659993829438643`) aus der Account-Konsole oder über die [Service Principals API](https://docs.databricks.com/aws/en/reference/scim-2-1) holen.
2. Policy erstellen. `ACCOUNT_CONSOLE_URL`, `ACCOUNT_ID`, `SERVICE_PRINCIPAL_NUMERIC_ID` und ein Bearer-`TOKEN` angeben:

   ```bash
   curl --request POST \
     --header "Authorization: Bearer $TOKEN" \
     "${ACCOUNT_CONSOLE_URL}/api/2.0/accounts/${ACCOUNT_ID}/servicePrincipals/${SERVICE_PRINCIPAL_NUMERIC_ID}/federationPolicies" \
     --data '{
       "oidc_policy": {
         "issuer": "https://token.actions.githubusercontent.com",
         "audiences": [
           "https://github.com/my-github-org"
         ],
         "subject": "repo:my-github-org/my-repo:environment:prod"
       }
     }'
   ```

   Vollständige API-Referenz: **Account Federation Policy API** (`https://docs.databricks.com/api/account/accountfederationpolicy/create`).

## <a id="beispiele-sp">3. Beispiel-Policies für Service Principals</a>

| Tool | Federation Policy | Beispiel-Token (passend) |
|---|---|---|
| **GitHub Actions** | **Issuer:** `https://token.actions.githubusercontent.com`<br>**Audience:** `https://github.com/<github-org>`<br>**Subject:** `repo:<github-org>/<repo>:environment:prod` | `{ "iss": "https://token.actions.githubusercontent.com", "aud": "https://github.com/<github-org>", "sub": "repo:<github-org>/<repo>:environment:prod" }` |
| **Kubernetes** | **Issuer:** `https://kubernetes.default.svc`<br>**Audience:** `https://kubernetes.default.svc`<br>**Subject:** `system:serviceaccount:namespace:serviceaccountname`<br>**JWKS JSON:** `{"keys":[{"kty":"rsa","e":"AQAB","use":"sig","kid":"<key-id>","alg":"RS256","n":"uPUViFv..."}]}` | `{ "iss": "https://kubernetes.default.svc", "aud": ["https://kubernetes.default.svc"], "sub": "system:serviceaccount:namespace:serviceaccountname" }` |
| **Azure DevOps** | **Issuer:** `https://vstoken.dev.azure.com/<org_id>`<br>**Audience:** `api://AzureADTokenExchange`<br>**Subject:** `sc://my-org/my-project/my-connection` | `{ "iss": "https://vstoken.dev.azure.com/<org_id>", "aud": "api://AzureADTokenExchange", "sub": "sc://my-org/my-project/my-connection" }` |
| **GitLab** | **Issuer:** `https://gitlab.example.com`<br>**Audience:** `https://gitlab.example.com`<br>**Subject:** `project_path:my-group/my-project:...` | `{ "iss": "https://gitlab.example.com", "aud": "https://gitlab.example.com", "sub": "project_path:my-group/my-project:..." }` |
| **CircleCI** | **Issuer:** `https://oidc.circleci.com/org/<org_id>`<br>**Audience:** `<org_id>`<br>**Subject:** `7cc1d11b-46c8-4eb2-9482-4c56a910c7ce`<br>**Subject claim:** `oidc.circleci.com/project-id` | `{ "iss": "https://oidc.circleci.com/org/<org_id>", "aud": "<org_id>", "oidc.circleci.com/project-id": "7cc1d11b-46c8-4eb2-9482-4c56a910c7ce" }` |
| **AWS IAM Outbound Identity Federation** | **Issuer:** `https://<uuid>.tokens.sts.global.api.aws` (account-spezifische Issuer-URL)<br>**Audience:** `databricks` (oder ein vereinbarter Wert, der an `GetWebIdentityToken` übergeben wird)<br>**Subject:** `arn:aws:iam::<account>:role/<role-name>` | `{ "iss": "https://<uuid>.tokens.sts.global.api.aws", "aud": ["databricks"], "sub": "arn:aws:iam::123456789012:role/my-workload-role" }` |

> **Hinweis:** Bei AWS IAM Outbound Identity Federation ist der `sub`-Claim des Tokens der **IAM-Rollen-ARN** des aufrufenden Workloads (z. B. Lambda Execution Role, ECS Task Role oder EC2 Instance Role).

## <a id="best-practices">4. Best Practices für Service-Principal-Federation-Policies</a>

Jeder Service Principal unterstützt **max. 20 Federation Policies**. So bleibst du unter diesem Limit:

### 4a. Eine externe Identität pro Service Principal abbilden

Lege pro externer Workload-Identität einen **dedizierten** Service Principal an. Mehrere Policies auf einem Service Principal sind nur sinnvoll, wenn dieselbe logische Identität über **verschiedene IdPs** authentifiziert (z. B. Workload läuft in GitHub Actions *und* Azure DevOps → zwei Policies, eine pro Provider, auf demselben Service Principal).

Nutze **nicht** mehrere Policies, um unterschiedliche Workloads (z. B. je Region eigene Kubernetes-Pods) auf einen Service Principal abzubilden — lege stattdessen je Workload einen eigenen Service Principal an. Das erhält die Audit-Log-Zuordnung und erlaubt, Zugriff für einen Workload zu entziehen, ohne andere zu beeinträchtigen.

### 4b. Berechtigungen über Gruppen bündeln

Brauchen mehrere Service Principals dieselben Rechte: als Mitglieder einer Databricks-**Gruppe** hinzufügen und Rechte der Gruppe zuweisen.

### 4c. `subject_claim`-Property für alternative Claims

Standardmäßig identifiziert Databricks den Workload über den `sub`-Claim. Nutzt der IdP `sub` nicht als stabilen Identifier, setze `subject_claim` auf den Claim-Namen des Providers (Beispiel: CircleCI in Abschnitt 3).

## <a id="account-wide">5. Account-weite Token Federation</a>

Account-Admins konfigurieren OAuth Token Federation im Databricks-Account über eine **Account-Federation-Policy**. Diese ermöglicht **allen Benutzern und Service Principals** im Account den API-Zugriff mit IdP-Tokens. Sie legt fest:

- Den **Identity Provider / Issuer**, dessen Tokens Databricks akzeptiert.
- Die **Kriterien zur Abbildung** eines Tokens auf den entsprechenden Databricks-Benutzer oder Service Principal.

**Beispiel** einer Account-Federation-Policy:

- **Issuer:** `https://idp.mycompany.com/oidc`
- **Audiences:** `databricks`
- **Subject claim:** `sub`

Passender JWT-Body zur Authentifizierung als `username@mycompany.com`:

```json
{
  "iss": "https://idp.mycompany.com/oidc",
  "aud": "databricks",
  "sub": "username@mycompany.com"
}
```

## <a id="account-policy">6. Account-Federation-Policy konfigurieren</a>

Konfiguration über Databricks-UI, [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/) oder [Databricks REST API](https://docs.databricks.com/api/account/introduction). **Maximal 20 Account-Federation-Policies pro Account.**

Anzugebende Felder:

- **Issuer-URL:** HTTPS-URL, die den IdP identifiziert (`iss`-Claim).
- **Audiences:** vorgesehener Empfänger (`aud`-Claim). Match bei mindestens einer übereinstimmenden Audience. Default: Databricks-Account-ID.
- **Subject claim:** Token-Claim mit dem Databricks-Benutzernamen des Benutzers, für den das Token ausgestellt wurde. Default: `sub`.
- **Token-Signaturvalidierung (optional):** öffentliche Schlüssel bzw. URL im JWKS-Format (bis 5 Schlüssel; sonst JWKS-URI). Ohne Angabe: Well-Known-Endpoint des Issuers (empfohlen).

> **Wichtig:** Für Account-weite Federation nur IdPs registrieren, die vollständig von deiner Organisation verwaltet und ihr vertraut werden (z. B. der firmeneigene IdP). **Keine** externen IdPs konfigurieren, die du nicht kontrollierst (z. B. von Kunden oder Partnern verwaltete).

### 6a. Über die Databricks-UI

1. Als Account-Admin bei `https://accounts.cloud.databricks.com` anmelden.
2. **Security** öffnen, Tab **Authentication**.
3. Unter **Federation policies** auf **Create policy** klicken.
4. Issuer-URL, Audiences, Subject claim und optionale Token-Signaturvalidierung eingeben.
5. **Create policy** klicken.

> Die Databricks CLI kann nicht im Web-Terminal des Workspaces zum Anlegen einer Federation Policy verwendet werden.

### 6b. Über die Databricks CLI

1. Neueste Version der [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/install) installieren/aktualisieren.
2. Als Account-Admin authentifizieren:

   ```bash
   databricks auth login --host ${ACCOUNT_CONSOLE_URL} --account-id ${ACCOUNT_ID}
   ```

3. Account-Federation-Policy erstellen:

   ```bash
   databricks account federation-policy create --json '{
     "oidc_policy": {
       "issuer": "https://idp.mycompany.com/oidc",
       "audiences": [
         "databricks"
       ],
       "subject_claim": "sub"
     }
   }'
   ```

### 6c. Über die Databricks Account API

```bash
curl --request POST \
  --header "Authorization: Bearer $TOKEN" \
  "${ACCOUNT_CONSOLE_URL}/api/2.0/accounts/${ACCOUNT_ID}/federationPolicies" \
  --data '{
    "oidc_policy": {
      "issuer": "https://idp.mycompany.com/oidc",
      "audiences": [
        "databricks"
      ],
      "subject_claim": "sub"
    }
  }'
```

`ACCOUNT_CONSOLE_URL`, `ACCOUNT_ID` und Bearer-`TOKEN` angeben. Vollständige API-Referenz: **Account Federation Policy API**.

## <a id="beispiele-account">7. Beispiel-Account-Federation-Policies</a>

| Federation Policy | Beispiel-Token (passend) |
|---|---|
| **Issuer:** `https://idp.mycompany.com/oidc`<br>**Audience:** `2ff814a6-3304-4ab8-85cb-cd0e6f879c1d` | `{ "iss": "https://idp.mycompany.com/oidc", "aud": "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d", "sub": "username@mycompany.com" }` |
| **Issuer:** `https://idp.mycompany.com/oidc`<br>**Audience:** `2ff814a6-...`<br>**Subject claim:** `preferred_username` | `{ "iss": "https://idp.mycompany.com/oidc", "aud": ["2ff814a6-...", "other-audience"], "preferred_username": "username@mycompany.com", "sub": "some-other-ignored-value" }` |
| **Issuer:** `https://idp.mycompany.com/oidc`<br>**Audience:** `2ff814a6-...`<br>**JWKS JSON:** `{"keys":[{"kty":"RSA","e":"AQAB","use":"sig","kid":"<key-id>","alg":"RS256","n":"uPUViFv..."}]}` | `{ "iss": "...", "aud": "2ff814a6-...", "sub": "username@mycompany.com" }` (Signatur mit dem öffentlichen Schlüssel aus der Policy geprüft) |
| **Issuer:** `https://idp.mycompany.com/oidc`<br>**Audience:** `2ff814a6-...`<br>**JWKS URI:** `https://idp.mycompany.com/jwks.json` | `{ "iss": "...", "aud": "2ff814a6-...", "sub": "username@mycompany.com" }` (Signatur mit über `jwks_uri` geholtem öffentlichen Schlüssel geprüft) |

## <a id="next">8. Nächste Schritte</a>

Nach dem Konfigurieren einer Federation Policy:

- Den **Identity Provider** so konfigurieren, dass er Tokens ausstellt, die deine Benutzer bei Databricks tauschen können (IdP-Doku beachten). Für gängige IdPs siehe [04 Workload Identity Federation in CI-CD aktivieren.md](04%20Workload%20Identity%20Federation%20in%20CI-CD%20aktivieren.md).
- Einen **JWT deines IdP** zum Zugriff auf die Databricks-API verwenden, indem du ihn zuerst gegen ein Databricks-OAuth-Token tauschst. Das OAuth-Token im `Bearer:`-Header des API-Aufrufs mitgeben. Der JWT muss gültig und mit **RS256 oder ES256** signiert sein. Details: [09 Mit IdP-Token authentifizieren (Token Exchange).md](09%20Mit%20IdP-Token%20authentifizieren%20%28Token%20Exchange%29.md).

## <a id="quelle">9. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/auth/oauth-federation-policy

**Stand:** 2026-08-28.
