# Python- und Scala-Artefakte

Python-Wheel und Scala-JAR mit Bundles bauen (Template-basiert sowie mit Poetry/Setuptools), sowie Python als Konfigurationssprache für Bundles (PyDABs) anstelle von YAML. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Python-Wheel: Template-basiertes Setup](#wheel-template)
2. [Python-Wheel: Poetry und Setuptools](#wheel-alternativ)
3. [Scala-JAR bauen](#scala-jar)
4. [Python als Bundle-Konfigurationssprache (PyDABs)](#pydabs)
5. [Quelle](#quelle)

---

## <a id="wheel-template">1. Python-Wheel: Template-basiertes Setup</a>

**Voraussetzungen:** Databricks CLI ≥ 0.218.0, konfigurierte Authentifizierung; `uv`-Tool; Workspace-Dateien aktiviert; bestehender Unity-Catalog-Catalog.

### Schritt 1 — Bundle erstellen

```bash
databricks bundle init
```

Auswahl: Template `default-python`; Projektname `my_project` oder eigener; „Notebook inclusion" → `no`; „ETL pipeline" → `no`; „Python package stub" → `yes`; „Serverless compute" → `yes`; Catalog wählen; „Personal schema per user" → `yes`.

### Schritt 2 — Struktur

`databricks.yml` (Bundle-Konfiguration inkl. Build-Einstellungen und Catalog-/Schema-Variablen); `resources/sample_job.job.yml` (Python-Wheel-Job-Spezifikation); `src/` (Quelldateien für den Wheel-Build); `tests/`; `README.md`.

**Hinweis für Databricks-Runtime-12.2-LTS-Kompatibilität**, in `databricks.yml` ergänzen:

```yaml
experimental:
  python_wheel_wrapper: true
```

### Schritt 3 — Validieren

```bash
databricks bundle validate
```

### Schritt 4 — Deployen

```bash
databricks bundle deploy --target dev
```

Verifikation: `Workspace > Users > [username] > .bundle > [project-name] > dev > artifacts > .internal > [whl-file-name].whl`.

### Schritt 5 — Job ausführen

```bash
databricks bundle run --target dev sample_job
```

## <a id="wheel-alternativ">2. Python-Wheel: Poetry und Setuptools</a>

Gemeinsame Dateistruktur:

```
├── src
│   └── my_package
│       ├── __init__.py
│       ├── main.py
│       └── my_module.py
└── pyproject.toml   (Poetry) bzw. setup.py (Setuptools)
```

### Poetry-Konfiguration

**`pyproject.toml`:**

```toml
[tool.poetry]
name = "my_package"
version = "0.0.1"
description = "<package-description>"
authors = ["<author> <email@organization>"]

[tool.poetry.dependencies]
python = "^3.10"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.scripts]
main = "my_package.main:main"
```

**Bundle-Konfiguration:**

```yaml
bundle:
  name: my-wheel-bundle

artifacts:
  default:
    type: whl
    build: poetry build
    path: .

resources:
  jobs:
    wheel-job:
      name: wheel-job
      tasks:
        - task_key: wheel-task
          new_cluster:
            spark_version: 13.3.x-scala2.12
            node_type_id: i3.xlarge
            data_security_mode: USER_ISOLATION
            num_workers: 1
          python_wheel_task:
            entry_point: main
            package_name: my_package
          libraries:
            - whl: ./dist/*.whl

targets:
  dev:
    workspace:
      host: <workspace-url>
```

### Setuptools-Konfiguration

**`setup.py`:**

```python
from setuptools import setup, find_packages

setup(
  name = "my_package",
  version = "0.0.1",
  author = "<author-name>",
  url = "https://<organization-url>",
  author_email = "<email@organization>",
  description = "<package-description>",
  packages=find_packages(where='./src'),
  package_dir={'': 'src'},
  entry_points={
    "packages": [
      "main=my_package.main:main"
    ]
  },
  install_requires=[
    "setuptools"
  ]
)
```

Voraussetzungen installieren: `pip3 install --upgrade wheel setuptools`.

`.gitignore`-Einträge: `.databricksdist`, `.databricksbuilddist`, `src/my_package/my_package.egg-info`.

**Bundle-Konfiguration:**

```yaml
bundle:
  name: my-wheel-bundle

artifacts:
  default:
    type: whl
    build: python3 setup.py bdist_wheel
    path: .

resources:
  jobs:
    wheel-job:
      name: wheel-job
      tasks:
        - task_key: wheel-task
          new_cluster:
            spark_version: 13.3.x-scala2.12
            node_type_id: i3.xlarge
            data_security_mode: USER_ISOLATION
            num_workers: 1
          python_wheel_task:
            entry_point: main
            package_name: my_package
          libraries:
            - whl: ./dist/*.whl

targets:
  dev:
    workspace:
      host: <workspace-url>
```

**Bereits gebaute Wheels:** das `artifacts`-Mapping weglassen, falls das Wheel bereits existiert — die CLI deployt dann die in `libraries` angegebenen bestehenden Dateien.

## <a id="scala-jar">3. Scala-JAR bauen</a>

**Workspace-Voraussetzungen:** aktivierter Unity Catalog; ein Unity-Catalog-Volume für Build-Artefakte mit Upload-Berechtigung; aktiviertes Serverless Compute; unterstützte Region.

**Lokale Entwicklungsumgebung:** JDK 17; IntelliJ IDEA; sbt; Databricks CLI ≥ 0.218.0 mit konfiguriertem `DEFAULT`-Profil.

### Schritt 1 — Bundle erstellen

```bash
databricks bundle init default-scala
```

Prompts: Projektname `my_scala_project`; Volumes-Zielpfad (z. B. `/Volumes/my-catalog/my-schema/bundle-volumes`). Das Template generiert automatisch JAR-Builder, Volume-Uploader und eine für Serverless Compute konfigurierte Spark-Job-Definition.

### Schritt 2 — VM-Optionen konfigurieren

In IntelliJ: Projektverzeichnis mit `build.sbt` importieren; Java 17 unter **File** > **Project Structure** > **SDKs** konfigurieren; `src/main/scala/com/examples/Main.scala` öffnen; in der Run-Konfiguration von `Main` folgende VM-Option ergänzen:

```
--add-opens=java.base/java.nio=ALL-UNNAMED
```

**Alternative (VS Code)** — `build.sbt` anpassen:

```sbt
fork := true
javaOptions += "--add-opens=java.base/java.nio=ALL-UNNAMED"
```

Dann `sbt run` ausführen.

### Schritt 3 — Struktur

`databricks.yml` (Bundle-Identifikator, referenziert Job-Konfigurationen); `resources/my_scala_project.job.yml` (JAR-Task und Cluster-Parameter); `src/` (Scala-Quellcode); `build.sbt` (Kompilierungs-/Abhängigkeitskonfiguration); `README.md`.

### Schritt 4 — Validieren

```bash
databricks bundle validate
```

Bestätigt u. a., dass das angegebene Volume existiert.

### Schritt 5 — Deployen

```bash
databricks bundle deploy -t dev
```

Verifikation: JAR im Catalog Explorer unter `/my_scala_project/dev/<user-name>/.internal/`; Job unter **Jobs & Pipelines** (Filter **Jobs**/**Owned by me**) als **[dev `<username>`] `my_scala_project`**.

### Schritt 6 — Ausführen

```bash
databricks bundle run -t dev my_scala_project
```

Die zurückgegebene **Run URL** öffnen; nach erfolgreichem Task (grüne Titelleiste) auf **main_task** klicken, um die Ausgabe einzusehen.

## <a id="pydabs">4. Python als Bundle-Konfigurationssprache (PyDABs)</a>

Python-Support erweitert Bundles um: Ressourcen-Definition in Python-Code (koexistiert mit YAML-Definitionen); dynamische Ressourcenerzeugung während des Deployments anhand von Metadaten; Modifikation bestehender YAML- oder Python-Ressourcen (auch zur Laufzeit über bedingte Tasks oder `for_each_task`).

**Voraussetzungen:** Databricks CLI ≥ 0.275.0; Authentifizierung via `databricks configure`; `uv` (oder `venv`) für virtuelle Umgebungen.

**Projekt initialisieren:**

```bash
databricks bundle init pydabs
```

Generiert eine Beispiel-Job-Struktur in `resources/my_pydabs_project.py` — entweder als Dictionary (`Job.from_dict()`) oder als typisierte Dataclass-Syntax.

**Konfigurationsstruktur** (`databricks.yml`):

```yaml
python:
  venv_path: .venv
  resources:
    - 'resources:load_resources'
```

`resources/__init__.py` enthält die `load_resources`-Funktion, die die Databricks CLI beim Deployment aufruft.

**Deployment:**

```bash
databricks bundle deploy --target dev
databricks bundle summary --target dev
databricks bundle run [job_name]
```

**Bestehende Jobs konvertieren:** über „View as code" im Kebab-Menü des Jobs → Python und Declarative Automation Bundles wählen → generierten Code in den `resources`-Ordner des Bundles kopieren.

**Programmatische Ressourcenerzeugung** (Iteration über Konfigurationsdaten):

```python
def create_job(country: str):
    return Job.from_dict({
        "name": f"my_job_{country}",
        "tasks": [...]
    })

def load_resources(bundle: Bundle) -> Resources:
    resources = load_resources_from_current_package_module()
    for country in ["US", "NL"]:
        resources.add_resource(f"my_job_{country}", create_job(country))
    return resources
```

**Variablenzugriff** über den `@variables`-Decorator:

```python
from databricks.bundles.core import Bundle, Variable, variables

@variables
class Variables:
    warehouse_id: Variable[str]

def load_resources(bundle: Bundle) -> Resources:
    warehouse_id = bundle.resolve_variable(Variables.warehouse_id)
```

Alternativ per Substitutionssyntax: `"${var.warehouse_id}"`.

**Ressourcen-Mutation** über Mutator-Funktionen:

```python
from databricks.bundles.core import job_mutator

@job_mutator
def add_email_notifications(bundle: Bundle, job: Job) -> Job:
    if job.email_notifications:
        return job
    email_notifications = JobEmailNotifications.from_dict({
        "on_failure": ["${workspace.current_user.userName}"],
    })
    return replace(job, email_notifications=email_notifications)
```

Konfiguration in `databricks.yml`: `python: mutators: - 'mutators:add_email_notifications'`.

**Referenzdokumentation:** vollständige API-Doku im [databricks-bundles PyPI-Paket](https://pypi.org/project/databricks-bundles) und unter `https://databricks.github.io/cli/python/`.

## <a id="quelle">5. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/bundles/python-wheel
- https://docs.databricks.com/aws/en/dev-tools/bundles/scala-jar
- https://docs.databricks.com/aws/en/dev-tools/bundles/python/

**Stand:** 2026-08-21.
