# Workload Identity Federation für AWS-IAM-Workloads aktivieren

Konfiguration von OAuth Token Federation (OIDC) für Workloads, die mit einer AWS-IAM-Rolle laufen (Lambda, EC2, ECS, EKS). Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Anwendungsfälle

- **Lambda-Funktionen**, die Databricks-APIs aufrufen (Jobs auslösen, SQL-Warehouses abfragen).
- **EC2-/ECS-basierte ETL-Pipelines**, die sich ohne Secrets bei Databricks authentifizieren.
- **EKS-basierte ML-Workloads**, die auf Model-Serving-Endpoints zugreifen.
- **Cross-Account-Muster**: Workloads in einem AWS-Account föderieren in einen Databricks-Account, der von einem anderen Team verwaltet wird.
- **Sicherheitsverbesserung**: Eliminierung langlebiger Databricks-PATs oder Secrets aus dem AWS Secrets Manager.

---

## AWS-Voraussetzungen

### Schritt 1: AWS IAM Outbound Identity Federation aktivieren

```python
import boto3
boto3.client('iam').enable_outbound_web_identity_federation()
```

Alternativ in der IAM-Konsole unter **Account Settings** > **Enable "Outbound web identity federation"**.

### Schritt 2: Berechtigung `sts:GetWebIdentityToken` gewähren

Der IAM-Rolle des Workloads die Berechtigung `sts:GetWebIdentityToken` geben:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["sts:GetWebIdentityToken"],
      "Resource": "*",
      "Condition": {
        "ForAllValues:StringEquals": {
          "sts:IdentityTokenAudience": "databricks"
        },
        "NumericLessThanEquals": {
          "sts:DurationSeconds": 300
        }
      }
    }
  ]
}
```

> **Hinweis:** „Die Audience-Bedingung stellt sicher, dass die Rolle nur Tokens für Databricks anfordern kann. Die Duration-Bedingung begrenzt die Token-Lebensdauer auf 300 Sekunden." Die Dauer kann je nach Anforderung bis 3600 Sekunden erhöht werden; kürzere Lebensdauern sind empfohlen.

### Schritt 3: Account-spezifische Issuer-URL notieren

```python
import boto3
info = boto3.client('iam').get_outbound_web_identity_federation_info()
print(info['IssuerUrl'])  # https://<uuid>.tokens.sts.global.api.aws
```

---

## Federation Policy erstellen

> **Wichtig:** Databricks-Federation-Policies werden auf **Account-Ebene** erstellt (nicht Workspace-Ebene). Der Databricks-CLI-Host muss auf `https://accounts.cloud.databricks.com` gesetzt sein, und der Benutzer muss **Account-Admin** sein.

Issuer = account-spezifische Issuer-URL aus Schritt 3:

```bash
databricks account service-principal-federation-policy create ${SP_ID} --json '{
  "oidc_policy": {
    "issuer": "https://<uuid>.tokens.sts.global.api.aws",
    "audiences": ["databricks"],
    "subject": "arn:aws:iam::<account-id>:role/<workload-role-name>"
  }
}'
```

---

## Bei Databricks authentifizieren

Beispiel mit dem `IdTokenSource`-Muster des Databricks SDK for Python: es holt ein AWS-STS-Token und tauscht es gegen ein Databricks-OAuth-Token.

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

# Keine Secrets nötig
clusters = w.clusters.list()
```

> **Hinweis:** 300 Sekunden Token-Lebensdauer empfohlen; Anpassung bis 3600 Sekunden je nach Bedarf möglich.

Ein Beispiel für den **manuellen** Token-Austausch: siehe [09 Mit IdP-Token authentifizieren (Token Exchange).md](09%20Mit%20IdP-Token%20authentifizieren%20%28Token%20Exchange%29.md).

---

## AWS-Referenzen

- Enabling AWS IAM Outbound Identity Federation — `https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_oidc_outbound.html`
- `GetWebIdentityToken` API Reference — `https://docs.aws.amazon.com/STS/latest/APIReference/API_GetWebIdentityToken.html`
- AWS-Blog: *Simplify access to external services using AWS IAM Outbound Identity Federation*

## Quelle

- https://docs.databricks.com/aws/en/dev-tools/auth/provider-aws-iam
- https://docs.databricks.com/aws/en/dev-tools/sdk-python (`WorkspaceClient`/`IdTokenSource`-Grundlagen; vollständige SDK-Referenz siehe [Databricks SDK für Python.md](../07%20Databricks%20SDK%20fuer%20Python.md))

**Stand:** 2026-09-01.
