# Mit Databricks Personal Access Tokens authentifizieren (Legacy)

Personal Access Tokens (PATs) ermöglichen die Authentifizierung auf **Workspace-Ebene**. Databricks empfiehlt stattdessen **OAuth**. Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Abschnittsübersicht

1. [Überblick und Einschränkungen](#ueberblick)
2. [PATs für Workspace-Benutzer erstellen](#user-pat)
3. [PATs für Service Principals erstellen](#sp-pat)
4. [PAT-Authentifizierung durchführen](#durchfuehren)
5. [PATs über die REST-API ausstellen](#rest-api)
6. [Weitere Hinweise](#hinweise)
7. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick und Einschränkungen</a>

„Databricks Personal Access Tokens (PATs) erlauben die Authentifizierung gegenüber Ressourcen und APIs auf Workspace-Ebene."

- Jeder PAT gilt für **genau einen Workspace**.
- Bis zu **600 PATs pro Workspace und Benutzer**.
- Databricks widerruft **ungenutzte PATs automatisch nach 90 Tagen**.
- PATs können **keine** Account-Level-Funktionalität automatisieren.

> „Databricks empfiehlt OAuth statt PATs für die Authentifizierung von Benutzerkonten, da OAuth stärkere Sicherheit bietet."

## <a id="user-pat">2. PATs für Workspace-Benutzer erstellen</a>

1. Benutzernamen in der oberen Leiste anklicken → **Settings**.
2. **Developer** anklicken.
3. Neben **Access tokens** auf **Manage** klicken.
4. **Generate new token** klicken.
5. Einen identifizierenden Namen eingeben.
6. Lebensdauer in Tagen festlegen.
7. Scope-Typ wählen:
   - **BI Tools** — für Tableau- oder Power-BI-Verbindungen.
   - **Other APIs** — für manuelle Scope-Auswahl.
8. Optional **Auto-scope tokens** aktivieren (automatische Scope-Anpassung).
9. **Generate** klicken.
10. Token an einen sicheren Ort kopieren, dann **Done** klicken.

> **Wichtig:** Tokens sicher speichern und nicht teilen. Verlorene Tokens müssen neu erstellt werden.

### Scoped Personal Access Tokens

Scoped Tokens beschränken Berechtigungen auf bestimmte API-Operationen. Beim Erstellen können API-Scopes wie `sql`, `unity-catalog` oder `scim` zugewiesen werden.

> **Warnung:** „Tokens mit dem Scope `authentication` können neue Tokens mit jedem beliebigen Scope erstellen. Diesen Scope nur Tokens gewähren, die andere Tokens verwalten müssen."

### Auto-scoping

Auto-scoping verengt Token-Berechtigungen automatisch auf tatsächlich genutzte APIs:

- Beobachtet die API-Nutzung über **30 Tage**.
- Wendet abgeleitete Scopes auf neue langlebige Tokens (30+ Tage) oder bestehende all-APIs-Tokens an.
- Sendet **7 Tage vor Durchsetzung** Erinnerungs-E-Mails.

Zum Deaktivieren die Scopes manuell setzen (UI oder API):

```bash
PATCH /api/2.0/token/{token_id_sha256}
```

Sind Scopes einmal manuell gesetzt, ist Auto-scoping für dieses Token dauerhaft deaktiviert.

## <a id="sp-pat">3. PATs für Service Principals erstellen</a>

### Schritt 1: Ersten PAT für den Service Principal erstellen (als Workspace-Admin)

1. Databricks-CLI-Authentifizierung einrichten.
2. Application-ID des Service Principals ermitteln:
   - Benutzername → **Settings**.
   - Unter **Workspace admin** → **Identity and access** → neben **Service principals** auf **Manage**.
   - Service-Principal-Namen anklicken.
   - Auf dem Tab **Configurations** die **Application Id** notieren.
3. Befehl ausführen:

```bash
databricks token-management create-obo-token \
  <application-id> \
  --lifetime-seconds <lifetime-seconds> \
  -p <profile-name>
```

Platzhalter:
- `<application-id>` — Application-ID des Service Principals.
- `<lifetime-seconds>` — Lebensdauer (z. B. `86400` = 1 Tag; Default = Workspace-Maximum, typischerweise 730 Tage).
- `<profile-name>` — Konfigurationsprofil (Default `DEFAULT`).

4. Den `token_value` aus der Antwort kopieren und sicher speichern.

### Schritt 2: Weitere PATs für den Service Principal erstellen

Mit dem bestehenden PAT weitere Tokens erzeugen:

```bash
databricks tokens create \
  --lifetime-seconds <lifetime-seconds> \
  -p <profile-name>
```

`token_value` aus der Antwort kopieren und sicher speichern.

## <a id="durchfuehren">4. PAT-Authentifizierung durchführen</a>

### Umgebungsvariablen

```bash
DATABRICKS_HOST=https://dbc-a1b2345c-d6e7.cloud.databricks.com
DATABRICKS_TOKEN=<token-string>
```

### Konfigurationsprofil

`.databrickscfg` erstellen/aktualisieren:

```ini
[<some-unique-configuration-profile-name>]
host  = <workspace-url>
token = <token>
```

### Databricks CLI

> **Hinweis:** Der folgende Befehl überschreibt ein bestehendes `DEFAULT`-Profil. Bestehende Profile prüfen mit `databricks auth env --profile DEFAULT`.

```bash
databricks configure --profile DEFAULT
```

Bei den Prompts eingeben:
- **Databricks Host:** Workspace-URL (z. B. `https://dbc-a1b2345c-d6e7.cloud.databricks.com`).
- **Personal Access Token:** dein Workspace-PAT.

### Databricks Connect

Unterstützt:
- Python: Databricks Connect für Databricks Runtime 13.3 LTS und höher.
- Scala: Databricks Connect für Databricks Runtime 13.3 LTS und höher.

Konfiguration über die CLI wie oben, danach optional:

```bash
databricks configure \
  --configure-cluster \
  --profile DEFAULT
```

Bei den Prompts: Host, PAT und Ziel-Cluster aus der Liste auswählen.

## <a id="rest-api">5. PATs über die REST-API ausstellen</a>

### Token erstellen (`/api/2.0/token/create`)

```bash
curl -X POST https://<databricks-instance>/api/2.0/token/create \
  -H "Authorization: Bearer <your-existing-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
  "lifetime_seconds": <lifetime-seconds>,
  "scopes": [
    "sql",
    "authentication"
  ],
  "autoscope_enabled": true
}'
```

**Erfolgreiche Antwort:**

```json
{
  "token_value": "<your-newly-issued-pat>",
  "token_info": {
    "token_id": "<token-id>",
    "creation_time": <creation-timestamp>,
    "expiry_time": <expiry-timestamp>,
    "comment": "<comment>",
    "scopes": ["authentication", "sql"],
    "last_accessed_time": 0
  }
}
```

### Neues Token verwenden

**Bash:**

```bash
curl -X GET "https://<databricks-instance>/api/2.0/<path-to-endpoint>" \
  -H "Authorization: Bearer <your-new-pat>"
```

**Python:**

```python
import requests

headers = {
    'Authorization': 'Bearer <your-new-pat>'
}

# Beispiel für eine HTTP-GET-Operation.
response = requests.get('https://<databricks-instance>/api/2.0/<path-to-endpoint>', headers=headers)
```

### Token-Scopes aktualisieren (`/api/2.0/token/<token_id>`)

Das aufrufende Token muss den Scope `authentication` haben:

```bash
curl -X PATCH https://<databricks-instance>/api/2.0/token/<token_id> \
  -H "Authorization: Bearer <your-existing-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
  "token": {
    "scopes": ["sql", "unity-catalog"]
  },
  "update_mask": "scopes"
}'
```

> **Hinweis:** Scope-Änderungen können bis zu zehn Minuten zur Verbreitung brauchen.

Alle verfügbaren Scopes anzeigen:

```
GET /api/2.0/token-scopes
```

## <a id="hinweise">6. Weitere Hinweise</a>

- Wenn du keine Tokens erstellen/verwenden kannst, hat der Workspace-Admin die Token-Authentifizierung evtl. deaktiviert oder dir die Berechtigung nicht erteilt.
- Für Account-Level-Automatisierung stattdessen **OAuth-Tokens** für Account-Admins oder Service Principals verwenden.
- Siehe auch: *Enable or disable personal access token authentication for the workspace* und *Personal access token permissions* (Databricks-Doku, Bereich Administration/Security).

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/auth/pat

**Stand:** 2026-08-28.
