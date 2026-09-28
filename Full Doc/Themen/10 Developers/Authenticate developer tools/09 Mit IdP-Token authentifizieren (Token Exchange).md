# Mit einem Identity-Provider-Token authentifizieren (Token Exchange)

Wie ein föderierter Identity-Token (JWT) gegen ein Databricks-OAuth-Token getauscht wird — automatisch über SDK/CLI oder manuell per `curl`. Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Abschnittsübersicht

1. [Ablauf](#ablauf)
2. [Voraussetzungen](#voraussetzungen)
3. [Konfiguration (Umgebungsvariablen / `.databrickscfg`)](#konfig)
4. [Zugriff auf Databricks-APIs](#zugriff)
5. [Benutzerdefinierte Authorization Provider](#custom)
6. [Manueller Token-Austausch](#manuell)
7. [Quelle](#quelle)

---

## <a id="ablauf">1. Ablauf</a>

Databricks unterstützt **OAuth 2.0 Token Exchange**: Benutzer und Workloads „tauschen einen föderierten Identity-Token gegen ein Databricks-OAuth-Token". SDK/CLI übernehmen den Token-Refresh automatisch — keine manuelle Credential-Rotation.

## <a id="voraussetzungen">2. Voraussetzungen</a>

1. Eine **Federation Policy** für den Account oder den Service Principal ist erstellt (siehe [03](03%20Federation%20Policy%20konfigurieren.md)).
2. Ein gültiger **JWT** des IdP, der zur Policy passt (signiert mit **RS256 oder ES256**).

## <a id="konfig">3. Konfiguration</a>

Folgende Werte als Umgebungsvariablen, `.databrickscfg`-Felder oder SDK-Konfiguration setzen:

| Wert | Beschreibung |
|---|---|
| **Databricks host** | `https://accounts.cloud.databricks.com` (Account) oder Workspace-URL |
| **Account ID** | nur bei Account-Konsolen-URL erforderlich |
| **Service principal client ID** | nur bei Workload Identity Federation erforderlich |
| **Auth type** | `env-oidc` (Umgebungsvariable) oder `file-oidc` (Datei) |
| **OIDC token env var** | Name der Variable mit dem Token (Default `DATABRICKS_OIDC_TOKEN`) |
| **OIDC token filepath** | Pfad zur Datei mit dem föderierten Token |

### Umgebungsvariablen

```bash
export DATABRICKS_HOST=<workspace-url-or-account-console-url>
export DATABRICKS_ACCOUNT_ID=<account-id>
export DATABRICKS_CLIENT_ID=<client-id>
export DATABRICKS_AUTH_TYPE=<auth-method>
export DATABRICKS_OIDC_TOKEN_ENV=<token-env-name>
export DATABRICKS_OIDC_TOKEN_FILEPATH=<token-filepath-name>
```

### `.databrickscfg`-Profil

```ini
[<profile-name>]
host = <workspace-url-or-account-console-url>
account_id = <account-id>
client_id = <client-id>
auth_type = <auth-method>
oidc_token_env = <token-env-name>
oidc_token_filepath = <token-filepath-name>
```

## <a id="zugriff">4. Zugriff auf Databricks-APIs</a>

### CLI

```bash
databricks clusters list
```

### Python

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
clusters = w.clusters.list()
```

### Java

```java
import com.databricks.sdk.WorkspaceClient;
WorkspaceClient w = new WorkspaceClient();
List<ClusterDetails> clusters = w.clusters().list();
```

### Go

```go
import "github.com/databricks/databricks-sdk-go"
w := databricks.Must(databricks.NewWorkspaceClient())
clusters := w.Clusters.ListAll(context.Background(), compute.List{})
```

## <a id="custom">5. Benutzerdefinierte Authorization Provider</a>

### AWS-IAM-Workloads (Python)

```python
import boto3
from databricks.sdk import WorkspaceClient
from databricks.sdk import oidc
from databricks.sdk.core import Config, credentials_strategy, oidc_credentials_provider

class AwsStsTokenSource(oidc.IdTokenSource):
    def __init__(self, audience="databricks", region="us-east-1"):
        self._audience = audience
        self._region = region

    def id_token(self) -> oidc.IdToken:
        sts = boto3.client("sts", region_name=self._region)
        resp = sts.get_web_identity_token(
            Audience=[self._audience],
            SigningAlgorithm="RS256",
            DurationSeconds=300,
        )
        return oidc.IdToken(jwt=resp["WebIdentityToken"])

@credentials_strategy("aws-sts-wif", [])
def aws_sts_wif_strategy(cfg: Config):
    return oidc_credentials_provider(cfg, AwsStsTokenSource())

w = WorkspaceClient(
    host="https://my-workspace.cloud.databricks.com",
    client_id="<service-principal-uuid>",
    credentials_strategy=aws_sts_wif_strategy)

clusters = w.clusters.list()
```

> **Hinweis:** 300 Sekunden Token-Lebensdauer empfohlen; Anpassung bis 3600 Sekunden möglich.

### Roher Token-Austausch (Python)

```python
import boto3
import requests

sts = boto3.client("sts", region_name="us-east-1")
resp = sts.get_web_identity_token(
    Audience=["databricks"],
    SigningAlgorithm="RS256",
    DurationSeconds=300,
)
aws_jwt = resp["WebIdentityToken"]

token_resp = requests.post(
    "https://<workspace>.cloud.databricks.com/oidc/v1/token",
    data={
        "client_id": "<service-principal-uuid>",
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": aws_jwt,
        "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "scope": "all-apis",
    },
)
access_token = token_resp.json()["access_token"]
```

### Generische benutzerdefinierte Implementierung (Python)

```python
from databricks.sdk import oidc
from databricks.sdk.core import (Config, CredentialsProvider, credentials_strategy, oidc_credentials_provider)

class MyCustomIdTokenSource(oidc.IdTokenSource):
    def id_token(self) -> oidc.IdToken:
        token = ...
        return oidc.IdToken(jwt=token)

@credentials_strategy("my-custom-oidc", [])
def my_custom_oidc_strategy(cfg: Config) -> CredentialsProvider:
    return oidc_credentials_provider(cfg, MyCustomIdTokenSource())

if __name__ == "__main__":
    cfg = Config(
        host="https://my-workspace.cloud.databricks.com",
        credentials_strategy=my_custom_oidc_strategy
    )
    from databricks.sdk import WorkspaceClient
    w = WorkspaceClient(config=cfg)
```

### Generische benutzerdefinierte Implementierung (Java)

```java
import com.databricks.sdk.WorkspaceClient;
import com.databricks.sdk.core.DatabricksConfig;
import com.databricks.sdk.core.CredentialsProvider;
import com.databricks.sdk.core.oauth.IDTokenSource;
import com.databricks.sdk.core.oauth.IDToken;

public class CustomOIDCExample {
    static class MyCustomIdTokenSource implements IDTokenSource {
        @Override
        public IDToken getIDToken(String audience) {
            String jwt = "...";
            return new IDToken(jwt);
        }
    }

    public static void main(String[] args) {
        CredentialsProvider provider = ...;
        DatabricksConfig cfg = new DatabricksConfig()
            .setHost("https://my-workspace.cloud.databricks.com")
            .setCredentialsProvider(provider);
        WorkspaceClient w = new WorkspaceClient(cfg);
        System.out.println("Databricks client initialized: " + w);
    }
}
```

### Generische benutzerdefinierte Implementierung (Go)

```go
package main

import (
    "context"
    "fmt"
    "github.com/databricks/databricks-sdk-go"
    "github.com/databricks/databricks-sdk-go/config"
    "github.com/databricks/databricks-sdk-go/credentials"
)

type MyCustomIdTokenSource struct{}

func (s *MyCustomIdTokenSource) IDToken(ctx context.Context) (*credentials.IDToken, error) {
    token := "..."
    return &credentials.IDToken{JWT: token}, nil
}

func myCustomOIDCStrategy(cfg *config.Config) (credentials.CredentialsProvider, error) {
    return credentials.NewOIDCCredentialsProvider(cfg, &MyCustomIdTokenSource{}), nil
}

func main() {
    cfg := &config.Config{
        Host: "https://my-workspace.cloud.databricks.com",
    }
    credentials.Register("my-custom-oidc", myCustomOIDCStrategy)
    w, err := databricks.NewWorkspaceClientWithConfig(cfg)
    if err != nil {
        panic(err)
    }
    fmt.Println("Databricks client initialized:", w)
}
```

## <a id="manuell">6. Manueller Token-Austausch</a>

### Föderierten JWT gegen Databricks-OAuth-Token tauschen

**Account-weite Federation Policies:**

```bash
curl --request POST https://<databricks-workspace-host>/oidc/v1/token \
  --data "subject_token=${FEDERATED_JWT_TOKEN}" \
  --data 'subject_token_type=urn:ietf:params:oauth:token-type:jwt' \
  --data 'grant_type=urn:ietf:params:oauth:grant-type:token-exchange' \
  --data 'scope=all-apis'
```

> **Tipp:** Für Account-Ressourcen `https://<databricks-account-host>/oidc/accounts/<account-id>/v1/token` verwenden.

**Service-Principal-Federation-Policies:**

```bash
curl --request POST https://<databricks-workspace-host>/oidc/v1/token \
  --data "client_id=${CLIENT_ID}" \
  --data "subject_token=${FEDERATED_JWT_TOKEN}" \
  --data 'subject_token_type=urn:ietf:params:oauth:token-type:jwt' \
  --data 'grant_type=urn:ietf:params:oauth:grant-type:token-exchange' \
  --data 'scope=all-apis'
```

`CLIENT_ID` = UUID des Service Principals.

### Beispiel-Antwort

```json
{
  "access_token": "eyJraWQ...odi0WFNqQw",
  "scope": "all-apis",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### OAuth-Token zum Aufruf von Databricks-APIs verwenden

```bash
TOKEN='<your-databricks-oauth-token>'
curl --header "Authorization: Bearer $TOKEN" \
  --url https://${DATABRICKS_WORKSPACE_HOSTNAME}/api/2.0/preview/scim/v2/Me
```

### Beispiel-Antwort

```json
{
  "userName": "username@mycompany.com",
  "displayName": "Firstname Lastname"
}
```

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/auth/oauth-federation-exchange
- https://docs.databricks.com/aws/en/dev-tools/sdk-python (`WorkspaceClient`-Grundlagen für die Python-Beispiele oben; vollständige SDK-Referenz siehe [Databricks SDK für Python.md](../07%20Databricks%20SDK%20fuer%20Python.md))

**Stand:** 2026-09-01.
