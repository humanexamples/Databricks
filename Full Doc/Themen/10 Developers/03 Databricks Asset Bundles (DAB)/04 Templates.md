# Templates

Standard-Bundle-Templates, wie man eigene Templates erstellt, und wie man sie im Team teilt (Git oder zentrale Workspace-Konfiguration). Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Was Bundle-Templates sind](#was-sind)
2. [Standard-Templates](#standard-templates)
3. [Eigenes Template erstellen: Schritt für Schritt](#eigenes-template)
4. [Template-Schema-Konfiguration](#schema)
5. [Template-Helper und eingebaute Variablen](#helper)
6. [Konfigurationstemplates](#konfig-templates)
7. [Templates testen](#testen)
8. [Eigene Templates teilen](#teilen)
9. [Quelle](#quelle)

---

## <a id="was-sind">1. Was Bundle-Templates sind</a>

Bundle-Templates ermöglichen konsistente und wiederholbare Bundle-Erstellung, indem sie Ordnerstruktur, Build-Schritte, Tasks, Tests und DevOps-Infrastructure-as-Code-Eigenschaften festlegen — sie helfen, „Bundles auf konsistente, wiederholbare Weise zu erstellen."

**Grundsyntax:**

```bash
databricks bundle init [template-name]
databricks bundle init default-python
databricks bundle init /projects/my-custom-bundle-templates/dab-container-template
```

## <a id="standard-templates">2. Standard-Templates</a>

Sieben mitgelieferte Templates:

| Template | Zweck |
|---|---|
| `default-minimal` | leeres Bundle mit nur den essenziellen Dateien und Catalog-Variablen-Konfiguration |
| `default-python` | Python-basiertes Bundle mit Job und ETL-Pipeline; benötigt den `uv`-Paketmanager |
| `default-scala` | Scala-JAR-Kompilierung, konfiguriert für Serverless-Compute-Deployment |
| `default-sql` | SQL-Queries, ausgeführt auf einem SQL-Warehouse über einen konfigurierten Job |
| `dbt-sql` | dbt-core-Integration, kombiniert lokale Entwicklung mit Bundle-Deployment |
| `mlops-stacks` | fortgeschrittenes Full-Stack-Template für MLOps-Stacks-Projekte (siehe [10 MLOps Stacks.md](10%20MLOps%20Stacks.md)) |
| `pydabs` | modifiziertes Python-Template, das Python statt YAML zur Konfiguration nutzt (siehe [03 Python- und Scala-Artefakte.md](03%20Python-%20und%20Scala-Artefakte.md), Abschnitt 4) |

## <a id="eigenes-template">3. Eigenes Template erstellen: Schritt für Schritt</a>

### Schritt 1 — Nutzer-Prompt-Variablen definieren

```bash
mkdir dab-container-template
cd dab-container-template
touch databricks_template_schema.json
```

```json
{
  "properties": {
    "project_name": {
      "type": "string",
      "default": "project_name",
      "description": "Project name",
      "order": 1
    }
  }
}
```

### Schritt 2 — Ordnerstruktur anlegen

```bash
mkdir -p "template/{{.project_name}}"
mkdir -p "template/{{.project_name}}/resources"
mkdir -p "template/{{.project_name}}/src"
```

### Schritt 3 — YAML-Konfigurationstemplates hinzufügen

`template/{{.project_name}}/databricks.yml.tmpl`:

```yaml
# This is a bundle definition for {{.project_name}}.
bundle:
  name: {{.project_name}}
include:
  - resources/*.yml
targets:
  dev:
    mode: development
    default: true
    workspace:
      host: {{workspace_host}}
  prod:
    mode: production
    workspace:
      host: {{workspace_host}}
      root_path: /Workspace/Production/.bundle/${bundle.name}
    {{- if not is_service_principal}}
    run_as:
      user_name: {{user_name}}
    {{end -}}
```

`template/{{.project_name}}/resources/{{.project_name}}_job.yml.tmpl`:

```yaml
resources:
  jobs:
    {{.project_name}}_job:
      name: {{.project_name}}_job
      tasks:
        - task_key: python_task
          job_cluster_key: job_cluster
          spark_python_task:
            python_file: ../src/task.py
      job_clusters:
        - job_cluster_key: job_cluster
          new_cluster:
            docker_image:
              url: databricksruntime/python:10.4-LTS
            node_type_id: i3.xlarge
            spark_version: 13.3.x-scala2.12
```

### Schritt 4 — Referenzierte Dateien hinzufügen

`template/{{.project_name}}/src/task.py`:

```python
print(f'Spark version{spark.version}')
```

### Schritt 5 — Struktur prüfen

```
dab-container-template
├── databricks_template_schema.json
└── template
    └── {{.project_name}}
        ├── databricks.yml.tmpl
        ├── resources
        │   └── {{.project_name}}_job.yml.tmpl
        └── src
            └── task.py
```

### Schritt 6 — Template testen

```bash
databricks bundle init dab-container-template
```

## <a id="schema">4. Template-Schema-Konfiguration</a>

Die Datei `databricks_template_schema.json` definiert Eingabevariablen und Initialisierungsverhalten:

| Feld | Zweck |
|---|---|
| `properties` | definiert die während der Initialisierung abgefragten Eingabevariablen |
| `properties.<var>.default` | Standardwert ohne Nutzereingabe |
| `properties.<var>.description` | Prompt-Text für den Nutzer |
| `properties.<var>.enum` | Liste wählbarer Werte als CLI-Menü |
| `properties.<var>.order` | Ganzzahl zur Steuerung der Prompt-Reihenfolge |
| `properties.<var>.pattern` | Regexp zur Eingabevalidierung |
| `properties.<var>.pattern_match_failure_message` | Fehlermeldung bei Validierungsfehlschlag |
| `properties.<var>.skip_prompt_if` | Prompt bedingt überspringen (basierend auf bestehender Konfiguration) |
| `template_dir` | Pfad zum Template-Verzeichnis bei Multi-Schema-Templates |
| `welcome_message` | Einleitende Nachricht vor den Prompts |
| `success_message` | Nachricht nach erfolgreicher Initialisierung |
| `min_databricks_cli_version` | Mindest-CLI-Versionsanforderung |

**Beispiel:**

```json
{
  "properties": {
    "project_name": {
      "type": "string",
      "default": "basic_bundle",
      "description": "What is the name of the bundle you want to create?",
      "order": 1
    }
  },
  "success_message": "\nYour bundle '{{.project_name}}' has been created."
}
```

## <a id="helper">5. Template-Helper und eingebaute Variablen</a>

| Helper | Beschreibung |
|---|---|
| `{{url}}` | URL-Parsing aus Gos `net/url`-Paket |
| `{{regexp}}` | Regex-Kompilierung aus Gos `regexp`-Paket |
| `{{random_int}}` | nicht-negative Pseudozufallszahl |
| `{{uuid}}` | RFC-4122-konforme 128-Bit-UUID |
| `{{bundle_uuid}}` | stabile eindeutige ID des Bundles über Template-Ausführungen hinweg |
| `{{pair}}` | Key-Value-Paar-Utility zur Map-Erstellung |
| `{{map}}` | konvertiert Paarlisten zu Map-Objekten für Template-Argumente |
| `{{smallest_node_type}}` | gibt den kleinsten verfügbaren Node-Typ zurück |
| `{{path_separator}}` | Betriebssystem-Pfadtrenner (`/` oder `\`) |
| `{{workspace_host}}` | aktuelle Workspace-Host-URL |
| `{{user_name}}` | vollständiger Name des initialisierenden Nutzers |
| `{{short_name}}` | verkürzter Nutzername |
| `{{default_catalog}}` | Standard-Workspace-Catalog (leer, falls keiner vorhanden oder Unity Catalog deaktiviert) |
| `{{is_service_principal}}` | boolescher Wert, ob der Nutzer ein Service Principal ist |
| `{{ skip <glob-pattern> }}` | Dateien/Verzeichnisse, die auf das Glob-Pattern passen, überspringen |

**Eigene Helper** in `library/`-Dateien mit Go-Template-Syntax:

```go
{{ define `cli_version` -}}
    v0.240.0{{- end }}
{{ define `model_name` -}}
    {{ .input_project_name }}-model{{- end }}
```

## <a id="konfig-templates">6. Konfigurationstemplates</a>

Konfigurationstemplates nutzen YAML mit Templating-Syntax, z. B. `databricks.yml.tmpl`:

```yaml
bundle:
  name: {{.project_name}}
include:
  - resources/*.yml
targets:
  dev:
    mode: development
    default: true
    workspace:
      host: {{workspace_host}}
  prod:
    mode: production
    workspace:
      host: {{workspace_host}}
      root_path: /Workspace/Production/.bundle/${bundle.name}
```

## <a id="testen">7. Templates testen</a>

```bash
databricks bundle init basic-bundle-template
```

Bei der Prompt „What is your bundle project name?" den gewünschten Namen eingeben (z. B. `my_test_bundle`) — die generierte Struktur spiegelt die Template-Organisation mit ersetzten Variablen wider.

## <a id="teilen">8. Eigene Templates teilen</a>

### Über Versionskontrolle

Templates in für Nutzer zugänglichen Git-Repositories ablegen. `databricks_template_schema.json` muss im Repository-Root liegen, oder die `--template-dir`-Option nutzen:

```bash
databricks bundle init <git-url> --template-dir <folder-path>
```

### Über Workspace-Konfiguration (Beta)

Workspace-Admins können einen zentralen Template-Ordner konfigurieren:

1. Template in einem GitHub-Repository ablegen.
2. Git-Folder-Verbindung im Workspace konfigurieren.
3. **Settings** > **Development** > **Declarative Automation Bundles** öffnen.
4. Den Ordner mit den Templates wählen (alle eigenen Templates müssen auf Root-Ebene liegen).
5. Berechtigungen für Template-Bearbeitung (`CAN MANAGE`) und Bundle-Erstellung (`CAN VIEW`) konfigurieren.

Erforderliche Ordnerstruktur:

```
folder-for-custom-templates/
├── example-custom-template/
├── custom-template-2/
├── custom-template-3/
└── ...
```

## <a id="quelle">9. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/bundles/template-tutorial
- https://docs.databricks.com/aws/en/dev-tools/bundles/templates

**Stand:** 2026-08-21.
