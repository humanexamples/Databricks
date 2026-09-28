# Job-Parameter vs. Bundle-Variablen

Wann Job-Parameter statt Bundle-Variablen verwendet werden sollten, und wie sich beide Mechanismen ergänzen. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Grundunterschied](#grundunterschied)
2. [YAML-Beispiel](#beispiel)
3. [Einschränkung: nicht mit Task-`base_parameters` kombinierbar](#einschraenkung)
4. [Zur Laufzeit überschreiben](#ueberschreiben)
5. [Troubleshooting](#troubleshooting)
6. [Quelle](#quelle)

---

## <a id="grundunterschied">1. Grundunterschied</a>

„Bundle-Variablen werden in der Konfiguration definiert und beim Deployment aufgelöst. Job-Parameter werden aufgelöst, wenn ein Job läuft — Default-Werte lassen sich also überschreiben, ohne neu zu deployen."

| Änderungshäufigkeit | Mechanismus | Anwendungsfall |
|---|---|---|
| pro Umgebung (dev/staging/prod) | Bundle-Variablen (siehe [05 Konfiguration (databricks.yml).md](05%20Konfiguration%20%28databricks.yml%29.md), Abschnitt 5) | Cluster-Größe, Warehouse-ID |
| pro Job-Lauf | Job-Parameter | Verarbeitungsdatum, Quelltabelle |
| pro Task (keine Job-Parameter vorhanden) | Task-`base_parameters` | task-spezifische Dateipfade |

## <a id="beispiel">2. YAML-Beispiel</a>

Vollständiges Beispiel mit umgebungsspezifischen Defaults über eine Bundle-Variable als Parameter-Default:

```yaml
# databricks.yml
variables:
  default_catalog:
    description: Environment-specific catalog
    default: dev_catalog

targets:
  dev:
    variables:
      default_catalog: biz_dev
  prod:
    variables:
      default_catalog: biz_prod

resources:
  jobs:
    etl_pipeline:
      name: etl_pipeline
      parameters:
        - name: catalog
          default: ${var.default_catalog}
        - name: processing_date
          default: '{{job.start_time.iso_date}}'
        - name: mode
          default: incremental
      tasks:
        - task_key: process_data
          notebook_task:
            notebook_path: ./notebooks/process.py
```

## <a id="einschraenkung">3. Einschränkung: nicht mit Task-`base_parameters` kombinierbar</a>

„Die Bundle-Validierung erlaubt nicht, dass Job-Level-`parameters` und Task-Level-`base_parameters` im selben Job verwendet werden." Es muss ein Ansatz gewählt werden:

**Nur Job-Level-Parameter:**

```yaml
resources:
  jobs:
    my_job:
      parameters:
        - name: catalog
          default: dev
        - name: schema
          default: default
      tasks:
        - task_key: task1
          notebook_task:
            notebook_path: ./notebook.py
```

**Nur Task-Level:** `base_parameters` auf einzelnen Tasks nutzen, sofern kein Job-Level-`parameters`-Block existiert.

## <a id="ueberschreiben">4. Zur Laufzeit überschreiben</a>

Drei Wege, Parameter bei der Ausführung zu überschreiben:

**CLI:**

```bash
databricks bundle run my_job -- --catalog=prod --mode=full_refresh
```

**REST API:**

```json
{
  "job_id": 123,
  "job_parameters": {
    "catalog": "prod",
    "mode": "full_refresh"
  }
}
```

**UI:** Job öffnen → **Run now** → Option für abweichende Parameter wählen.

## <a id="troubleshooting">5. Troubleshooting</a>

**Werte ändern sich zur Laufzeit nicht:** „Bundle-Variablen werden zum Deployment-Zeitpunkt aufgelöst. Soll ein Wert zur Laufzeit überschreibbar sein, muss er als Job-Parameter definiert werden, mit der Bundle-Variable als dessen Default."

**Parameter im Notebook nicht verfügbar** — prüfen:

- Parameter existiert im `parameters`-Abschnitt des Jobs.
- Code nutzt `dbutils.widgets.get("name")`.
- Parameternamen stimmen exakt überein (Groß-/Kleinschreibung).
- Das Bundle wurde nach Hinzufügen/Umbenennen der Parameter erneut deployt.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/bundles/job-parameters

**Stand:** 2026-08-26.
