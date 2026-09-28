# dbt-Platform-Task (Public Preview)

Orchestriert und überwacht bestehende **dbt-Platform**-Jobs direkt aus Databricks heraus: dbt-Jobs auswählen und auslösen, Auto-Retry bei Fehlern konfigurieren, Läufe überwachen.

## dbt Platform Task vs. dbt Task

| Task-Typ | Einsatz |
|---|---|
| **dbt platform task** | orchestriert bestehende dbt-Platform-Jobs über die dbt-Platform-API — zentrale Orchestrierung in Databricks, dbt-Platform-Vorteile (Monitoring, Zeitplanung) bleiben erhalten |
| **dbt task** | führt dbt-Core-Projekte auf einem Databricks-Cluster mit Code aus Git aus — volle Kontrolle über die Ausführungsumgebung |

## Voraussetzungen

- Workspace-Admin muss die Preview aktivieren.
- `CREATE CONNECTION` auf dem Unity-Catalog-Metastore.
- Bestehendes dbt-Projekt mit definiertem Job in der dbt Platform.
- Recht, einen Service-Token in der dbt Platform zu erzeugen (Service-Account-Token statt persönlichem Token empfohlen).

## dbt-Platform-Details beschaffen

- **Account ID:** dbt Platform → Settings → Account Settings → aus der URL `https://cloud.getdbt.com/settings/accounts/{account_id}`.
- **API Key:** Settings → Profile Setting → Your Profile → Access API → API Key.
- **Host-URL:** abhängig von Tenancy — z. B. Multi-Tenant Nordamerika `https://cloud.getdbt.com`, Cell-based Nordamerika `https://12345.us1.dbt.com`.

## dbt-Platform-Connection einrichten

1. Catalog-Icon in der Sidebar.
2. Plus-Icon im Schema-Browser → **Create a connection**.
3. Namen vergeben, Typ **dbt platform** → **Next**.
4. Host-URL eingeben (ohne abschließenden Slash).
5. Account ID und API-Token eingeben.
6. **Create connection**.
7. Optional Privilegien an andere Nutzer/Gruppen vergeben.

## Job mit dbt-Platform-Task erstellen

1. **Jobs & Pipelines** → **Create** → **Job**.
2. **Add another task type** → „dbt platform" suchen und wählen.
3. Task-Namen eingeben.
4. dbt-Platform-Connection wählen.
5. dbt-Platform-Job wählen.
6. Optional Retries, Laufdauer-/Streaming-Backlog-Schwellen, Benachrichtigungen.
7. **Save task**.
8. Optional **Run now** zum Testen.

## Zeitplan/Trigger

Zeitbasiert oder ereignisbasiert konfigurierbar. **Continuous-Trigger werden für dbt-Platform-Jobs nicht unterstützt.**

## Läufe überwachen

**Jobs & Pipelines** → Job öffnen → Lauf in Spalte **Start time** anklicken → **View in dbt** für Details in der dbt Platform.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/dbt-platform
