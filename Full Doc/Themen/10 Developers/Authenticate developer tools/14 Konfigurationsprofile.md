# Databricks-Konfigurationsprofile (`.databrickscfg`)

Konfigurationsprofile speichern Authentifizierungseinstellungen in der `.databrickscfg`-Datei und erlauben den Wechsel zwischen Workspaces, Umgebungen oder Auth-Methoden „ohne den Code zu ändern". Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Abschnittsübersicht

1. [Bestandteile eines Profils](#bestandteile)
2. [Profile erstellen](#erstellen)
3. [Mehrere Profile](#mehrere)
4. [Profile verwenden](#verwenden)
5. [Best Practices](#best-practices)
6. [Profile testen](#testen)
7. [Quelle](#quelle)

---

## <a id="bestandteile">1. Bestandteile eines Profils</a>

- Authentifizierungs-Credentials (Tokens oder Service-Principal-Credentials)
- Die Workspace- oder Account-URL
- Optionale, methodenspezifische Einstellungen

## <a id="erstellen">2. Profile erstellen</a>

### Über die CLI

```bash
databricks auth login --host <workspace-url>
```

### Manuell

1. `.databrickscfg` im Home-Verzeichnis anlegen:
   - Unix/Linux/macOS: `~/.databrickscfg`
   - Windows: `%USERPROFILE%\.databrickscfg`
2. Profil im Format:

```ini
[<profile-name>]
<field-name> = <field-value>
```

### Beispiel: OAuth M2M

```ini
[DEFAULT]
host          = https://<workspace-url>
client_id     = <client-id>
client_secret = <client-secret>
```

## <a id="mehrere">3. Mehrere Profile</a>

```ini
[DEFAULT]
host          = https://production-workspace-url
client_id     = <production-client-id>
client_secret = <production-client-secret>

[DEVELOPMENT]
host          = https://dev-workspace-url
client_id     = <dev-client-id>
client_secret = <dev-client-secret>

[STAGING]
host          = https://staging-workspace-url
client_id     = <staging-client-id>
client_secret = <staging-client-secret>
```

## <a id="verwenden">4. Profile verwenden</a>

**CLI:**

```bash
databricks workspace list --profile DEVELOPMENT
```

**Umgebungsvariable:**

```bash
export DATABRICKS_CONFIG_PROFILE=DEVELOPMENT
databricks workspace list
```

**Python SDK:**

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient(profile="DEVELOPMENT")
```

## <a id="best-practices">5. Best Practices</a>

- `DEFAULT` für den am häufigsten genutzten Workspace verwenden.
- Sprechende Namen vergeben (`PRODUCTION`, `DEVELOPMENT`, `STAGING`).
- Restriktive Dateiberechtigungen setzen.
- Datei per `.gitignore` von der Versionskontrolle ausschließen.
- Für Produktion Service Principals verwenden.
- Credentials regelmäßig rotieren.

## <a id="testen">6. Profile testen</a>

```bash
# Ein bestimmtes Profil inspizieren
databricks auth env --profile DEVELOPMENT

# Alle Profile auflisten
databricks auth profiles
```

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/auth/config-profiles
- https://docs.databricks.com/aws/en/dev-tools/sdk-python (`WorkspaceClient(profile=...)`; vollständige SDK-Referenz siehe [Databricks SDK für Python.md](../07%20Databricks%20SDK%20fuer%20Python.md))

**Stand:** 2026-09-01.
