# Credentials Utility (`dbutils.credentials`)

Befehle zum Interagieren mit Credentials innerhalb von Notebooks — insbesondere zum Wechseln der beim S3-Zugriff angenommenen IAM-Rolle. Teil der [Databricks Utils](00%20Uebersicht.md)-Reihe.

## Verfügbarkeit

Nur auf Clustern mit aktiviertem **Credential Passthrough** verfügbar.

## Befehle

| Befehl | Signatur | Beschreibung |
|---|---|---|
| `assumeRole` | `assumeRole(role: String): boolean` | setzt den IAM-Rollen-ARN, der bei der S3-Authentifizierung angenommen wird |
| `getServiceCredentialsProvider` | `getServiceCredentialsProvider(credentialName: String): Object` | liefert einen Service-Credentials-Provider für das angegebene Service Credential — Rückgabetyp cloud-spezifisch; **nicht in R verfügbar** |
| `showCurrentRole` | `showCurrentRole: List` | listet die aktuell gesetzte(n) IAM-Rolle(n) |
| `showRoles` | `showRoles: List` | listet alle möglichen, annehmbaren IAM-Rollen |

## Beispiele

```python
dbutils.credentials.assumeRole("arn:aws:iam::123456789012:roles/my-role")
# Out[1]: True

dbutils.credentials.showCurrentRole()
# Out[1]: ['arn:aws:iam::123456789012:role/my-role-a']

dbutils.credentials.showRoles()
# Out[1]: ['arn:aws:iam::123456789012:role/my-role-a', 'arn:aws:iam::123456789012:role/my-role-b']
```

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/databricks-utils#credentials-utility-dbutilscredentials

**Stand:** 2026-08-26.
