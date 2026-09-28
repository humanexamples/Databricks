# Tutorials: Jobs, Pipelines, Apps

Vollständige Schritt-für-Schritt-Anleitungen für die drei zentralen Bundle-Tutorials (Job, Pipeline, App) sowie eine Übersicht aller verfügbaren Tutorials. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Von der UI zum Bundle: Job als YAML exportieren](#von-ui-zum-bundle)
2. [Übersicht aller Tutorials](#uebersicht-tutorials)
3. [Tutorial: Job mit Bundle](#job-tutorial)
4. [Tutorial: Pipeline mit Bundle](#pipeline-tutorial)
5. [Tutorial: Databricks App mit Bundle](#app-tutorial)
6. [Quelle](#quelle)

---

## <a id="von-ui-zum-bundle">Von der UI zum Bundle: Job als YAML exportieren</a>

**Nicht-Databricks-Quelle: privates Kursmaterial** (`Kursmetrial_Databricks/4_DevOps Essentials for Data Engineering/Course Notebooks/M03 - CD/_Abschnitte/02 Demo - Deploying the Databricks Assets/B. Create the Job with Notebooks, Python Files and a SPD Pipeline.md`). Neben den offiziellen Tutorials zeigt der Kurs einen praktischen Brückenweg, um einen in der UI (oder per SDK) erstellten Job in eine Bundle-Ressourcendefinition zu überführen, ohne die Job-Konfiguration manuell von Hand nachzubauen:

1. Einen Job zunächst über die UI oder das Databricks SDK erstellen und in **Jobs & Pipelines** öffnen.
2. Im Kebab-Menü (drei Punkte neben **Run now**) **View as code** wählen und den Tab **JSON** öffnen — liefert die vollständige Job-Definition für die REST-API bzw. das SDK.
3. Alternativ im selben Kebab-Menü **Edit as YAML** wählen — liefert dieselbe Job-Definition als YAML, direkt im Format einer Bundle-Ressource (`resources.jobs.<job_key>`).
4. Diese YAML-Ausgabe lässt sich per Copy-Paste in eine Bundle-Ressourcendatei übernehmen (z. B. `resources/<job_name>.job.yml`, per `include` in `databricks.yml` eingebunden — siehe [05 Konfiguration (databricks.yml).md](05%20Konfiguration%20%28databricks.yml%29.md)) und ist damit sofort mit `databricks bundle validate`/`deploy` nutzbar.

Dieser Weg ergänzt `databricks bundle generate` (siehe [09 Manuelle Bundle-Erstellung und Ressourcen-Migration.md](09%20Manuelle%20Bundle-Erstellung%20und%20Ressourcen-Migration.md)): Während `bundle generate` eine bestehende Ressource direkt aus dem Workspace in Bundle-Dateien exportiert, eignet sich **View as Code** insbesondere während der iterativen Entwicklung in der UI, um schnell eine Momentaufnahme der aktuellen Konfiguration als YAML zu erhalten.

---

## <a id="uebersicht-tutorials">1. Übersicht aller Tutorials</a>

1. **Develop a job with Declarative Automation Bundles** — Bundle zur programmatischen Verwaltung eines Jobs über das Standard-Python-Template erstellen (inkl. Notebook und Job-Definition), dann validieren, deployen, ausführen.
2. **Develop pipelines with Declarative Automation Bundles** — Bundle für Pipeline-Verwaltung über das Python-Template mit Beispiel-Pipeline-Code sowie Definitionen für Pipeline und Ausführungs-Job.
3. **Build a Python wheel file** — Python-Wheel als Teil eines Bundle-Projekts bauen, deployen und ausführen (siehe [03 Python- und Scala-Artefakte.md](03%20Python-%20und%20Scala-Artefakte.md)).
4. **Build a Scala JAR** — Scala-JAR als Teil eines Bundle-Projekts bauen, deployen und ausführen (siehe [03 Python- und Scala-Artefakte.md](03%20Python-%20und%20Scala-Artefakte.md)).
5. **Manage Databricks apps** — Databricks App lokal entwickeln, dann bundle-basiertes Deployment in den Workspace konfigurieren.
6. **Declarative Automation Bundles for MLOps Stacks** — MLOps-Stacks-Bundle nach produktionsreifen Best Practices erstellen (siehe [10 MLOps Stacks.md](10%20MLOps%20Stacks.md)).
7. **Create a bundle manually** — Bundle ohne Template von Grund auf bauen (siehe [09 Manuelle Bundle-Erstellung und Ressourcen-Migration.md](09%20Manuelle%20Bundle-Erstellung%20und%20Ressourcen-Migration.md)).
8. **Create a custom bundle template** — eigene Templates für Jobs mit spezifischen Python-Tasks auf Docker-Container-Images entwickeln (siehe [04 Templates.md](04%20Templates.md)).

## <a id="job-tutorial">2. Tutorial: Job mit Bundle</a>

**Voraussetzungen:** Databricks CLI ≥ 0.218.0; `uv`-Tool für Tests/Dependency-Installation; Workspace-Dateien im Remote-Workspace aktiviert; bestehender Catalog für Tabellenerstellung.

### Schritt 1 — Authentifizierung

```bash
databricks auth login --host <workspace-url>
```

Vorgeschlagenen Profilnamen übernehmen oder anpassen. Token-Info prüfen: `databricks auth token --host <workspace-url>` bzw. `databricks auth token -p <profile-name>`.

### Schritt 2 — Bundle initialisieren

```bash
databricks bundle init
```

Prompt-Antworten: Template `default-python` (Enter); Projektname `my_project` (oder eigener); „Include a job that runs a notebook" → `yes`; „Include an ETL pipeline" → `no`; „Include a stub Python package" → `no`; „Use serverless" → `yes`; Default-Catalog eintragen; „Use personal schema per user" → `yes`.

### Schritt 3 — Bundle-Struktur

- `databricks.yml` — Bundle-Name, Dateireferenzen, Catalog-/Schema-Variablen, Ziel-Workspace-Einstellungen.
- `resources/sample_job.job.yml` — Job-Einstellungen inkl. Standard-Notebook-Task-Konfiguration.
- `src/sample_notebook.ipynb` — liest Beispieltabellen.
- `tests/` — Beispiel-Unit-Tests.
- `README.md`.

### Schritt 4 — Validieren

```bash
databricks bundle validate
```

### Schritt 5 — Deployen

```bash
databricks bundle deploy --target dev
```

Verifikation: Workspace-Sidebar → **Users > `<username>` > .bundle > `<project-name>` > dev > files > src** (Notebook vorhanden); **Jobs & Pipelines** mit Filtern **Jobs**/**Owned by me** → **[dev `<username>`] `sample_job`** → Tab **Tasks** zeigt einen `notebook_task`.

### Schritt 6 — Ausführen

```bash
databricks bundle run --target dev sample_job
```

Die zurückgegebene **Run URL** im Browser öffnen, um den Fortschritt zu verfolgen.

### Schritt 7 — Tests ausführen

```bash
uv run pytest
```

### Schritt 8 — Aufräumen

```bash
databricks bundle destroy --target dev
```

Bei der Bestätigungsabfrage `y` eingeben.

## <a id="pipeline-tutorial">3. Tutorial: Pipeline mit Bundle</a>

**Voraussetzungen:** Databricks CLI ≥ 0.283.0 (`databricks -v`); `uv`; Workspace-Dateien aktiviert; bestehender Unity-Catalog-Catalog für Pipeline-Tabellen; optional das PyPI-Modul `databricks-dlt` für lokale Entwicklungsunterstützung.

### Schritt 1 — Authentifizierung

```bash
databricks auth login --host <workspace-url>
databricks auth token --host <workspace-url>
```

### Schritt 2 — Bundle erstellen

```bash
databricks pipelines init
```

Prompts: Projektname (Standard `my_pipeline_project`); bestehender Catalog-Name; „Personal schema per user" → `yes`; Sprache → `python`.

### Schritt 3 — Bundle-Struktur

```
my_pipeline_project
├── databricks.yml
├── pyproject.toml
├── README.md
├── resources
│   ├── my_pipeline_project_etl.pipeline.yml
│   └── sample_job.job.yml
└── src
    └── my_pipeline_project_etl
        ├── explorations
        │   └── sample_exploration.ipynb
        ├── README.md
        └── transformations
            ├── sample_trips_my_pipeline_project.py
            └── sample_zones_my_pipeline_project.py
```

### Schritt 4 — Validieren

```bash
databricks bundle validate
```

### Schritt 5 — Deployen

```bash
databricks bundle deploy --target dev
# oder:
databricks pipelines deploy --target dev
```

Verifikation: **Workspace > Users > `<username>` > `.bundle`**, dann **Jobs & Pipelines** für die erstellte Pipeline prüfen.

### Schritt 6 — Pipeline ausführen

```bash
databricks pipelines run my_pipeline_project_etl --target dev
```

Die zurückgegebene **Update URL** im Browser öffnen.

### Schritt 7 — Logs und Historie

```bash
databricks pipelines history my_pipeline_project_etl
databricks pipelines logs my_pipeline_project_etl
```

### Schritt 8 — Aufräumen

```bash
databricks pipelines destroy --target dev
```

## <a id="app-tutorial">4. Tutorial: Databricks App mit Bundle</a>

„Databricks Apps erlaubt es, sichere Daten- und KI-Anwendungen auf der Databricks-Plattform zu erstellen, die sich leicht teilen lassen."

**Voraussetzungen:** Databricks-Workspace und lokale Entwicklungsumgebung gemäß App-Spezifikationen; Databricks CLI ≥ 0.250.0.

### App lokal erstellen — drei Optionen

**Option 1 — von Grund auf:** Quickstart-Tutorials für unterstützte Frameworks (Dash, Flask, Gradio, Shiny, Streamlit) befolgen; `app.yaml` im Projekt-Root mit Ausführungsbefehl ergänzen (Streamlit: `command: ['streamlit', 'run', 'app.py']`; Dash: `command: ['python', 'app.py']`).

**Option 2 — bestehende Workspace-App synchronisieren:**

```bash
mkdir hello-world-app
cd hello-world-app
databricks workspace export-dir /Workspace/Users/someone@example.com/databricks_apps/[app-path] .
```

**Option 3 — GitHub-Templates:**

```bash
git clone https://github.com/databricks/app-templates
```

**Bestehende App zum Bundle hinzufügen:**

```bash
databricks bundle generate app --existing-app-name hello-world-app
databricks bundle bind
```

### Lokale Entwicklung und Debugging

```bash
databricks apps run-local --prepare-environment --debug
```

Zugriff über `http://localhost:8001`. Debugging über den VS-Code-Python-Debugger mit Remote Attach (Proxy standardmäßig auf Port 5678).

### Bundle-Konfiguration und Deployment

```yaml
bundle:
  name: hello_world_bundle

resources:
  apps:
    hello_world_app:
      name: 'hello-world-app'
      source_code_path: .
      description: 'A Databricks app'

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://myworkspace.cloud.databricks.com

  prod:
    mode: production
    workspace:
      host: https://myworkspace.cloud.databricks.com
      root_path: /Workspace/Users/someone@example.com/.bundle/${bundle.name}/${bundle.target}
    permissions:
      - user_name: someone@example.com
        level: CAN_MANAGE
```

```bash
databricks bundle validate
databricks bundle deploy
databricks apps deploy
databricks bundle summary
```

### Berechtigungen und Testen

```yaml
resources:
  apps:
    hello_world_app:
      name: 'hello-world-app'
      source_code_path: .
      description: 'A Databricks app'
      permissions:
        - level: CAN_USE
          group_name: users
```

```bash
databricks bundle run hello_world_app
```

### Produktions-Deployment: Service-Principal-Grant

**Option A — direkter Schema-Grant:**

```yaml
resources:
  apps:
    hello_world_app:
      name: 'hello-world-app'
      source_code_path: .
      description: 'A Databricks app'
  schemas:
    my_schema:
      name: my_schema
      grants:
        - principal: '${resources.apps.hello_world_app.service_principal_client_id}'
          privileges:
            - CREATE_TABLE
      catalog_name: main
```

**Option B — Job-basierter Grant** (`grant_notebook.ipynb`):

```python
app_service_principal = dbutils.widgets.get("app_service_principal")
spark.sql(f"GRANT ALL PRIVILEGES ON SCHEMA <schema-name> TO `{app_service_principal}`")
```

```yaml
resources:
  jobs:
    grant_job:
      name: 'grant-job'
      parameters:
        - name: app_service_principal
          default: '${resources.apps.hello_world_app.service_principal_client_id}'
      tasks:
        - task_key: setup_grants
          notebook_task:
            notebook_path: ./grant_notebook.ipynb
```

**Produktions-Deployment:**

```bash
databricks bundle deploy -t prod
databricks bundle run grant_job -t prod
databricks bundle run hello_world_app -t prod
```

**Bundle-Init-Template für eine Streamlit-App:**

```bash
databricks bundle init https://github.com/databricks/bundle-examples --template-dir contrib/templates/streamlit-app
```

## <a id="quelle">5. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/bundles/tutorials
- https://docs.databricks.com/aws/en/dev-tools/bundles/jobs-tutorial
- https://docs.databricks.com/aws/en/dev-tools/bundles/pipelines-tutorial
- https://docs.databricks.com/aws/en/dev-tools/bundles/apps-tutorial

**Stand:** 2026-08-21.
