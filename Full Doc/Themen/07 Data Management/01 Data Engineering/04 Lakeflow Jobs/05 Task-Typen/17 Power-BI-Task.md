# Power-BI-Task (Public Preview)

Orchestriert Power-BI-Semantikmodelle über Databricks Jobs — automatisierte Veröffentlichung nach Microsoft Power BI Online ohne manuellen Eingriff.

## Voraussetzungen

- Power-BI-Connection in Unity Catalog eingerichtet.
- `USE CONNECTION`-Privileg.
- Zugriff auf die benötigten Tabellen und ein SQL-Warehouse (General-Purpose-Compute wird nicht unterstützt).

## Konfiguration

1. Tab **Tasks** → Task hinzufügen.
2. Task-Namen eingeben, Typ **Power BI**.
3. Erforderliche Eigenschaften konfigurieren: SQL-Warehouse, Power-BI-Connection, Workspace, Semantikmodell.
4. Optional erweiterte Einstellungen (Retries, Benachrichtigungen, Schwellen).
5. Task speichern.

## Zentrale Eigenschaften

**SQL-Warehouse:** erforderlich für Refreshes im Import-Modus oder Queries im DirectQuery-Modus.

**Power-BI-Query-Modus:**

| Modus | Verhalten |
|---|---|
| **Import** | Daten werden in Power BI gecacht; Refresh vor Nutzung fragt das SQL-Warehouse ab |
| **DirectQuery** | fragt das SQL-Warehouse bei Erstellen/Laden von Dashboards ab |

**Authentifizierung:** OAuth oder PAT (Personal Access Token) — Credentials ggf. zusätzlich in der Power-BI-UI nach dem Deployment zu konfigurieren.

**Metadatenverwaltung:** Checkbox „Overwrite existing model" propagiert alle Updates; standardmäßig werden nur Metadaten angehängt.

## Credential-Konfiguration über REST-APIs

Zwei Wege: **Microsoft Fabric Connections API** (Cloud-Connections und beide Gateway-Typen) oder **Power BI REST API** (Aktualisierung von Datenquellen-Credentials). Beide benötigen Microsoft-Entra-ID-Access-Tokens und unterstützen Basic Authentication mit Service-Principal-Application-IDs und -Secrets.

## Wichtige Hinweise

Databricks empfiehlt einen Service Principal als Run-As-Identität für optimale Governance. Semantikmodelle während der Task-Ausführung nicht im Power-BI-Service bearbeiten — sonst können Modelle im Status „Pending changes" hängen bleiben.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/powerbi
