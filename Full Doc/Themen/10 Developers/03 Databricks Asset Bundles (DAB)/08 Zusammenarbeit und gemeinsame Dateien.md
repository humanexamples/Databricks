# Zusammenarbeit und gemeinsame Dateien

Wie mehrere Bundles gemeinsame Konfiguration und Code teilen, und welche Berechtigungsstufen für Teamzusammenarbeit sinnvoll sind. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Ausgangslage](#ausgangslage)
2. [Empfohlene Repository-Struktur](#repo-struktur)
3. [Konfiguration für Datei-Sharing](#konfiguration)
4. [Bundle-Validierung](#validierung)
5. [Berechtigungen für gemeinsam genutzte Bundles](#berechtigungen)

---

## <a id="ausgangslage">1. Ausgangslage</a>

„Organisationen pflegen oft viele Bundles, und in diesen fortgeschritteneren CI/CD-Szenarien teilen sich diese Bundles gemeinsame Konfiguration und Dateien."

## <a id="repo-struktur">2. Empfohlene Repository-Struktur</a>

Databricks empfiehlt, mehrere Bundle-Quellen in einem einzigen Repository mit einem dedizierten Shared-Ordner zu speichern:

```
databricks-bundle-repo/
├── shared/
│   ├── variables.yml
│   └── shared_library.py
├── job_bundle/
│   ├── databricks.yml
│   ├── resources/
│   ├── src/
│   └── README.md
├── pipeline_bundle/
│   ├── databricks.yml
│   ├── resources/
│   ├── src/
│   └── README.md
```

## <a id="konfiguration">3. Konfiguration für Datei-Sharing</a>

Externe Code-Dateien werden über den `paths`-Key des `sync`-Mappings eingebunden.

**`shared/shared_library.py`:**

```python
def multiply(a: int, b: int) -> int:
    return a * b
```

**`shared/variables.yml`:**

```yaml
variables:
  cluster_id:
    default: 1234-567890-abcde123
```

**`job_bundle/databricks.yml`:**

```yaml
bundle:
  name: job_bundle
sync:
  paths:
    - ../shared
    - ./src
include:
  - resources/*.yml
  - ../shared/*.yml
targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://my-workspace.cloud.databricks.com
  prod:
    mode: production
    workspace:
      host: https://my-workspace.cloud.databricks.com
      root_path: /Workspace/Users/someone@example.com/.bundle/${bundle.name}/${bundle.target}
    permissions:
      - user_name: someone@example.com
        level: CAN_MANAGE
```

**`resources/job_bundle.job.yml`:**

```yaml
resources:
  jobs:
    my_python_job:
      name: my_python_job
      tasks:
        - task_key: python_task
          spark_python_task:
            python_file: src/my_python.py
    my_notebook_job:
      name: my_notebook_job
      tasks:
        - task_key: notebook_task
          existing_cluster_id: ${var.cluster_id}
          notebook_task:
            notebook_path: src/notebook.ipynb
```

**`src/my_python.py`** — Zugriff auf die gemeinsame Bibliothek:

```python
import os
import sys

# Zum Sync-Root-Pfad navigieren.
# Hinweis: erfordert DBR >= 14 oder Serverless.
shared_path = os.getcwd() + "/../../shared"

sys.path.append(shared_path)

from shared_library import multiply

result = multiply(2, 3)
print(result)
```

## <a id="validierung">4. Bundle-Validierung</a>

„Es ist wichtig, die Bundle-Konfiguration stets zu validieren — besonders, wenn Bundles Dateien und Konfiguration teilen." Vor jedem Deployment ausführen:

```bash
databricks bundle validate
```

Der Validierungsprozess stellt sicher, dass Variablen, Dateien und Pfade existieren und korrekt vererbt werden.

## <a id="berechtigungen">5. Berechtigungen für gemeinsam genutzte Bundles</a>

Unterschiedliche Teammitglieder benötigen unterschiedliche Berechtigungsstufen: „Alle Nutzer müssen die Bundles unter Umständen einsehen können, manche müssen Bundle-Änderungen deployen und Ressourcen im Ziel-Development-Workspace ausführen können, einige wenige müssen Bundle-Änderungen deployen und Ressourcen in Production ausführen können, und automatisierte Workflows, die einen Service Principal nutzen, müssen Ressourcen in einem Bundle ausführen können."

```yaml
bundle:
  name: shared_bundle
include:
  - resources/*.yml
permissions:
  - level: CAN_VIEW
    group_name: all_users
  - level: CAN_MANAGE
    group_name: data_engineering_users
  - level: CAN_RUN
    service_principal_name: 123456-abcdef
targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://my-workspace.cloud.databricks.com
  prod:
    mode: production
    workspace:
      host: https://my-workspace.cloud.databricks.com
      root_path: /Workspace/Users/someone@example.com/.bundle/${bundle.name}/${bundle.target}
    permissions:
      - user_name: someone@example.com
        level: CAN_MANAGE
```

Berechtigungsstufen: `CAN_VIEW`, `CAN_MANAGE`, `CAN_RUN` — erlauben feingranulare Zugriffskontrolle über Development- und Production-Umgebungen hinweg.
