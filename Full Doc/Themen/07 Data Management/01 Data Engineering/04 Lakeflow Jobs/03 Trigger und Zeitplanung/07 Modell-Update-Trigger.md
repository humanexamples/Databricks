# Jobs bei Modell-Updates auslösen (Beta)

Model-Update-Trigger lösen einen Job aus, wenn sich Modelle in Unity Catalog ändern — ohne Cron-Zeitpläne oder dauerhafte Cluster zur Überwachung.

## Anwendungsfälle

- **Data Scientists:** Validierungs-, Test- oder Promotion-Jobs automatisch auslösen, wenn Modellversionen bereit werden oder Aliase gesetzt werden.
- **Administratoren:** alle Modelle eines Metastore oder Schemas überwachen, um jede Neuerstellung automatisch zu auditieren.

## Scope und Bedingung

**Scope:**

| Scope | Bedeutung |
|---|---|
| Model | ein einzelnes registriertes Modell |
| Schema | alle Modelle in einem Schema |
| Metastore | alle Modelle im Metastore (Metastore-Admin-Rechte erforderlich) |

**Bedingung:**

- **Model is created** — neues registriertes Modell im Scope
- **Model version is ready** — neue Modellversion wird bereit
- **Model alias is set** — angegebener Alias wird gesetzt (bis zu 10 Aliase pro Trigger)

## Batching

Der Trigger pollt ca. einmal pro Minute; erkannte Änderungen werden pro Intervall gebündelt und als Parameter an den Job übergeben. Ein Batch darf das 10.000-Zeichen-Limit für Job-Parameterwerte nicht überschreiten. Richtwerte (kurze Namen): 212 Updates/Lauf bei „Model is created", 163 bei „Model version is ready", 117 bei „Model alias is set" — bei längeren Namen entsprechend weniger.

## Hoher Event-Durchsatz

Treffen Updates schneller ein, als ein Lauf verarbeiten kann, und läuft der Trigger etwa eine Stunde durchgehend in jedem Poll-Intervall, schlägt er fehl und stoppt automatisch. Erholung: Update-Rate reduzieren (engerer Scope oder mehrere Trigger) oder Trigger pausieren/fortsetzen.

**Empfehlungen bei hohem Volumen:** Schema-/Model-Scope statt Metastore-Scope, Überwachung auf mehrere Trigger/Jobs aufteilen, ausgelöste Jobs schlank halten und For-Each-Tasks zur Verarbeitung nutzen.

## Voraussetzungen

- Unity Catalog im Workspace aktiviert.
- `EXECUTE`-Privileg auf Ziel-Modell/-Schema.
- Für Metastore-Scope: Metastore-Admin mit `EXECUTE` auf allen aktuellen und künftigen Catalogs.

## Trigger hinzufügen

1. **Jobs & Pipelines** → Job auswählen.
2. **Add trigger**.
3. Trigger-Typ **Model update**.
4. Scope (Model/Schema/Metastore) und Ziel wählen.
5. Bedingung wählen (ggf. bis zu 10 Aliase angeben).
6. Optional: **Minimum time between triggers** / **Wait after last change** (Sekunden).
7. **Test trigger**.
8. **Save**.

Nach dem Speichern dauert die Initialisierung ca. eine Minute („The trigger will be evaluated soon").

## Job-Parameter

`{{job.trigger.model.updates}}` liefert eine JSON-Liste gebündelter Updates:

```json
[{ "full_name": "model.full.name1", "version": 123, "alias_name": "prod" }]
```

`full_name` ist immer gesetzt; `version` bei „Model version is ready" und „Model alias is set"; `alias_name` nur bei „Model alias is set".

**Beispiel — Verarbeitung im Notebook:**

```python
import json
json_list = dbutils.widgets.get("events")
data = json.loads(json_list)
for item in data:
    print(f"Full Name: {item['full_name']}, Version: {item.get('version')}, Alias Name: {item.get('alias_name')}")
```

## Mit einem For-Each-Task verarbeiten

Ein **For-each**-Task führt einen verschachtelten Task einmal je Listenelement aus — als Input `{{job.trigger.model.updates}}` konfigurieren; jedes Update steht dem verschachtelten Task als Widget-Parameter zur Verfügung.

```python
full_name = dbutils.widgets.get("full_name")
version = dbutils.widgets.get("version")
alias_name = dbutils.widgets.get("alias_name")
print(f"Full Name: {full_name}, Version: {version}, Alias Name: {alias_name}")
```

## Über die Jobs API konfigurieren

```json
{
  "job_id": 574587036927544,
  "new_settings": {
    "trigger": {
      "pause_status": "UNPAUSED",
      "model": {
        "securable_name": "main.default",
        "condition": "MODEL_ALIAS_SET",
        "aliases": ["alias1", "alias2"],
        "min_time_between_triggers_seconds": 3600,
        "wait_after_last_change_seconds": 120
      }
    },
    "parameters": [
      {
        "default": "{{job.trigger.model.updates}}",
        "name": "events"
      }
    ]
  }
}
```

`securable_name` (Schema/Modell, leer = ganzer Metastore), `condition` (`MODEL_CREATED`, `MODEL_VERSION_READY`, `MODEL_ALIAS_SET`), `aliases` (nur für `MODEL_ALIAS_SET`).

## Einschränkungen

- Maximal 100 Model-Update-Trigger pro Workspace.
- Ein Job-Lauf trägt Updates bis zum 10.000-Zeichen-Limit (typischerweise 100+ Updates).
- Maximal 10 Aliase pro Trigger.
- Trigger schlägt nach ca. einer Stunde durchgehenden Pollings ohne manuelle Erholung fehl.
- Metastore-Scope erfordert Metastore-Admin-Status und `EXECUTE` auf allen Catalogs.

## Model-Update-Trigger vs. Deployment Jobs

Model-Update-Trigger nutzen für: Modellerstellung/Alias-Änderungen überwachen, breiteren Scope (Schema/Metastore) als einzelne Modelle, viele Modelle mit einem Trigger statt Job-pro-Modell. Deployment Jobs nutzen für: enge UI-Kopplung und Aktivitätsprotokolle zu Modellversion-Erstellung und Job-Lauf-Beziehungen.

## Quelle

- https://docs.databricks.com/aws/en/jobs/model-update-triggers
