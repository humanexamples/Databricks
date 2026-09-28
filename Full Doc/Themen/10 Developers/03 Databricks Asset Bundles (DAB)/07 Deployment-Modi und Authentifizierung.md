# Deployment-Modi und Authentifizierung

Die Modi `development` und `production` samt ihrer Standardverhalten, benutzerdefinierte Presets, sowie attended (User-to-Machine) und unattended (Machine-to-Machine) Authentifizierung für Bundles. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Development-Modus](#development)
2. [Production-Modus](#production)
3. [Benutzerdefinierte Presets](#presets)
4. [Attended-Authentifizierung (User-to-Machine)](#attended)
5. [Unattended-Authentifizierung (Machine-to-Machine)](#unattended)
6. [Authentifizierungstypen im Überblick](#auth-typen)
7. [Quelle](#quelle)

---

## <a id="development">1. Development-Modus</a>

Deployment-Modi sind vollständig optional — Bundles funktionieren auch ohne Modus-Konfiguration.

```yaml
targets:
  dev:
    mode: development
```

**Verhaltensweisen:**

1. **Ressourcen-Benennung/-Tagging:** stellt Nicht-Datei-/Notebook-Ressourcen den Präfix `[dev ${workspace.current_user.short_name}]` voran; taggt deployte Jobs und Pipelines mit `dev`.
2. **Pipeline-Management:** markiert deployte Lakeflow-Pipelines als `development: true`.
3. **Cluster-Override:** aktiviert das Flag `--cluster-id <cluster-id>` bzw. das `cluster_id`-Mapping, um bestehende Cluster-Definitionen zu überschreiben.
4. **Zeitplan-/Trigger-Pausierung:** pausiert alle Zeitpläne und Trigger auf Jobs und Quality Monitors (pro Ressource überschreibbar via `pause_status: UNPAUSED`).
5. **Nebenläufige Läufe:** aktiviert parallele Job-Ausführung für schnellere Iteration (pro Job deaktivierbar via `max_concurrent_runs: 1`).
6. **Deployment-Lock:** deaktiviert das Deployment-Lock für schnellere Iteration (wieder aktivierbar via `bundle.deployment.lock.enabled: true`).

## <a id="production">2. Production-Modus</a>

```yaml
targets:
  prod:
    mode: production
```

**Verhaltensweisen:**

1. **Pipeline-Validierung:** „validiert, dass alle zugehörigen deployten Lakeflow-Pipelines als `development: false` markiert sind."
2. **Git-Branch-Validierung:** validiert, dass der aktuelle Git-Branch dem Target entspricht (optionale Konfiguration):
   ```yaml
   git:
     branch: main
   ```
   Überschreibbar über das `--force`-Flag beim Deployment.
3. **Service-Principal-Empfehlung:** die Doku empfiehlt Service Principals für Produktions-Deployments (durchsetzbar via `run_as`).
4. **Pfad-/Berechtigungsvalidierung** (ohne Service Principal): validiert, dass `artifact_path`, `file_path`, `root_path` oder `state_path` nicht auf spezifische Nutzer überschrieben sind; validiert, dass `run_as` und `permissions` angegeben sind.
5. **Cluster-Override-Einschränkung:** untersagt Cluster-Definitions-Overrides (anders als im Development-Modus).
6. **Empfehlung für unveränderliche Ordner:** die Doku empfiehlt Deployment in unveränderliche, schreibgeschützte Ordner, um Änderungen durch Nicht-Admin-Nutzer zu verhindern.

## <a id="presets">3. Benutzerdefinierte Presets</a>

Presets erlauben die Anpassung von Target-Verhalten. „Sofern für ein Preset keine Ausnahme angegeben ist, überschreiben Presets — falls sowohl `mode` als auch `presets` gesetzt sind — das Standardverhalten des Modus."

```yaml
targets:
  dev:
    presets:
      name_prefix: 'testing_'
      pipelines_development: true
      trigger_pause_status: PAUSED
      jobs_max_concurrent_runs: 10
      tags:
        department: finance
```

**Override-Hierarchie:** Einstellungen einzelner Ressourcen überschreiben Presets, Presets überschreiben Modus-Standardwerte.

## <a id="attended">4. Attended-Authentifizierung (User-to-Machine)</a>

**Empfohlener Ansatz:** OAuth User-to-Machine (U2M).

„Attended-Authentifizierungs-Szenarien (User-to-Machine) sind manuelle Workflows — z. B. die Nutzung des Webbrowsers auf der lokalen Maschine, um sich beim Ziel-Workspace anzumelden, wenn die Databricks CLI dazu auffordert."

**Alternative:** Personal Access Tokens, an Nutzerkonten gebunden.

**Speicherung:** Databricks-Konfigurationsprofile auf der lokalen Entwicklungsmaschine erlauben schnellen Wechsel zwischen mehreren Workspace-Kontexten. Nutzer geben Profile über `--profile`/`-p` bei Bundle-Befehlen (validate, deploy, run, destroy) an.

**Wichtig:** Das `DEFAULT`-Konfigurationsprofil wird automatisch aktiv, wenn kein Profil explizit angegeben ist.

## <a id="unattended">5. Unattended-Authentifizierung (Machine-to-Machine)</a>

**Bevorzugte Reihenfolge:**

1. OAuth Machine-to-Machine (M2M) für Service Principals.
2. Personal-Access-Token-Authentifizierung für Service-Principal-gebundene Tokens.

**Speicherung:** Umgebungsvariablen, da CI/CD-Systeme darauf optimiert sind.

**Multi-Workspace-Empfehlung:** Für Projekte mit mehreren zusammenhängenden Workspaces (Development, Staging, Production) einen einzelnen Service Principal mit Zugriff auf alle Umgebungen nutzen — ermöglicht konsistente Umgebungsvariablen über das gesamte Projekt.

**Setup-Voraussetzung:** die Databricks CLI auf den zugehörigen Compute-Ressourcen vor dem Deployment installieren.

## <a id="auth-typen">6. Authentifizierungstypen im Überblick</a>

- **OAuth M2M:** erfordert die Service-Principal-Autorisierungsdokumentation; Umgebungsvariablen im Abschnitt zu Workspace-Ebenen-Operationen spezifiziert.
- **OAuth U2M:** Konfiguration über die CLI generiert automatisch ein Konfigurationsprofil für attended Szenarien.
- **Personal Access Tokens (Legacy):** Profilerstellung in der CLI-Dokumentation beschrieben; Umgebungsvariablen im Abschnitt zu Workspace-Ebenen-Operationen.

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/bundles/deployment-modes
- https://docs.databricks.com/aws/en/dev-tools/bundles/authentication

**Stand:** 2026-08-21.
