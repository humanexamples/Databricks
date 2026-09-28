Was ein **Declarative Automation Bundle (DAB)** ist, wie es über die Databricks CLI funktioniert und wo Bundles verwendet werden. Sie betrachten die standardmäßige Bundle-Projektstruktur, die Konfigurationsdatei `databricks.yml` mit ihren Top-Level-Mappings und die drei CLI-Befehle zum Validieren, Deployen und Ausführen eines Bundles. Diese Grundlagen werden in jedem folgenden Demo und Lab verwendet.

## B. Einfache Projektstruktur

```
my_project/
 ├─ resources/
 ├─ src/
 ├─ tests/
 └─ databricks.yml
```

- **resources/** – Zusätzliche YAML-Konfigurationsdateien für Ihre Declarative Automation Bundles
- **src/** – Enthält die **Quelldateien (Notebooks, Python-Dateien usw.)**, die für die Datenpipeline benötigt werden
- **tests/** – Enthält **Unit- und Integrationstests** für die Datenpipeline
- **databricks.yml** – ERFORDERLICHE Bundle-Konfigurationsdatei, die:
  - im **YAML-Format** ausgedrückt sein muss
  - mindestens das **Top-Level-`bundle`-Mapping** enthalten muss
  - mindestens eine (und nur eine) Bundle-Konfigurationsdatei namens **databricks.yml** enthalten muss

Die Top-Level-Mappings der Konfigurationsdatei `databricks.yml` sind linksbündige Schlüssel. Dieses Beispiel verwendet **bundle**, **resources** und **targets**; weitere Mappings sind für fortgeschrittenere Konfiguration verfügbar.

Zu den Top-Level-Mappings gehören: `bundle`, `resources`, `targets`, `variables`, `workspace`, `permissions`, `artifacts`, `include`, `sync`.

- **bundle** – Identität des Bundles; deklariert den erforderlichen Bundle-Namen.
- **resources** – die Databricks-Objekte, die das Bundle verwaltet (Jobs, Pipelines, MLflow …), definiert mit REST-API-Parametern.
- **targets** – Umgebungen und ihre Konfigurations-Overrides (dev, production …).

```yaml
bundle:
  name: demo01_bundle

resources:
  jobs:
    l1_simple_dab:
      name: my_job_name_l1_simple_dab
      tasks:
        - task_key: create_bronze_table
          notebook_task:
            notebook_path: ./src/create_bronze_table.py
            source: WORKSPACE
. . .
targets:
  development:
    mode: development
    default: true
    workspace:
      host: https://dev.cloud.databricks.com/
  production:
    mode: production
    workspace:
      host: https://prod.cloud.databricks.com/
```

### C2. Die Mappings `bundle` und `resources`

Das **bundle**-Mapping deklariert einen erforderlichen Bundle-Namen (und kann weitere optionale Konfigurationen tragen). Das **resources**-Mapping definiert die vom Bundle verwendeten Databricks-Ressourcen mithilfe der entsprechenden Databricks-REST-API-Parameter.

- **bundle name** – das Top-Level-`bundle`-Mapping deklariert einen erforderlichen Bundle-Namen und kann weitere optionale Konfigurationen nutzen.
- **resources** – definiert die vom Bundle verwendeten Databricks-Ressourcen – Lakeflow Jobs, Spark Declarative Pipelines, MLflow und mehr – mithilfe der entsprechenden Databricks-REST-API.
- **Job Key** – der Name des Ressourcen-Mappings (Job Key); muss eindeutig sein.
- **Job Name** – das `name`-Mapping setzt den tatsächlichen im Workspace erstellten Job-Namen.
- **tasks · notebook** – jeder Task verwendet `notebook_path` (ein relativer Pfad mit der korrekten Erweiterung), um das auszuführende Notebook anzugeben.

```yaml
bundle:
  name: demo01_bundle

resources:
  jobs:
    l1_simple_dab:
      name: my_job_name_l1_simple_dab
      tasks:
        - task_key: create_bronze_table
          notebook_task:
            notebook_path: ./src/create_bronze_table.py
            source: WORKSPACE
```

> **Hinweis:** Seit dem 20. Dezember 2024 ist das Standardformat für neue Notebooks das `.ipynb`-Format. Stellen Sie sicher, dass Sie die korrekte Notebook-Erweiterung angeben.

> **Zusätzliche Notizen (Sprechernotizen):**
>
> - Eine Bundle-Konfigurationsdatei darf nur ein Top-Level-`bundle`-Mapping enthalten, das den gesamten Inhalt des Bundles mit einem Namen verknüpft. Zusätzlich können Sie bei Bedarf weitere Databricks-Workspace-Einstellungen wie `cluster_id`, `compute_id`, `git` und einige andere aufnehmen. Die zusätzlichen Mappings unter dem Top-Level-Mapping müssen eingerückt sein.
> - Das `resources`-Mapping gibt Informationen über die vom Bundle verwendeten Databricks-Ressourcen an, etwa Lakeflow Jobs, Spark Declarative Pipelines, MLflow und mehr. Die Ressourcen werden mit den entsprechenden Databricks-REST-API-Parametern definiert.
> - Jedes Ressourcentyp-Mapping enthält eine oder mehrere einzelne Ressourcendeklarationen, jede mit eindeutigem Namen. In diesem Beispiel hat der Job den Ressourcen-Mapping-Namen (Job Key) `l1_simple_dab`. Das erstellt über das `name`-Mapping einen Job namens `my_job_name_l1_simple_dab`, und dieser Job enthält einen oder mehrere Tasks, angegeben mit den entsprechenden REST-API-Parametern.
> - Innerhalb des `tasks`-Mappings ist der Task `create_bronze_table` benannt und verwendet den `notebook_path`-Schlüssel, um das zu verwendende Notebook anzugeben. Verwenden Sie hier einen relativen Pfad des Notebooks innerhalb Ihres Projekts, mit der korrekten Erweiterung.
> - Beachten Sie, dass seit dem 20. Dezember 2024 das Standardformat für neue Notebooks das `.ipynb`-Format ist. Wenn Sie nicht die korrekte Notebook-Erweiterung angeben, wird ein Fehler zurückgegeben. In diesem Beispiel verwendet das Notebook die traditionelle `.py`-Erweiterung.

### C3. Das `targets`-Mapping

Das **targets**-Mapping setzt spezifische Umgebungen und ihre Konfigurations-Overrides, einschließlich Modus-Typen, einer Standard-Zielumgebung und verschiedener anderer Konfigurationen und Overrides. Dieses Beispiel umfasst zwei Umgebungen, **development** und **production**, jede mit einer eindeutigen Konfiguration.

- **targets** – setzt spezifische Umgebungen und ihre Konfigurations-Overrides.
- **development** – `mode: development` und `default: true` (das Standardziel, wenn keines angegeben wird) – mit eigenem Workspace-Host.
- **production** – `mode: production` mit dem Produktions-Workspace-Host.

```yaml
targets:
  development:
    mode: development
    default: true
    workspace:
      host: https://dev.cloud.databricks.com/
  production:
    mode: production
    workspace:
      host: https://prod.cloud.databricks.com/
```

> **Zusätzliche Notizen (Sprechernotizen):**
>
> - Das Top-Level-Mapping `targets` setzt spezifische Umgebungen und Umgebungskonfigurationen, darunter: den Umgebungs-Modus-Typ (z. B. development oder production); die Standard-Zielumgebung, die auf die Entwicklungsumgebung gesetzt sein sollte (das sichert, dass ohne Angabe von Deploy-Ziel standardmäßig development verwendet wird); und verschiedene andere Konfigurationen und Konfigurations-Overrides für dieses spezifische Target.
> - In diesem Beispiel gibt es zwei Zielumgebungen: development und production, jede mit eindeutigen Konfigurationen und Overrides.
> - Für development geben wir die Mappings `mode: development` und `default: true` an, mit einer spezifischen Development-Workspace-URL.
> - Für production verwenden wir `mode: production` und geben die Production-Workspace-URL an.

## D. Validieren, Deployen und Ausführen mit der CLI

### D1. Ihr DAB validieren, deployen und ausführen

Sobald Ihre `databricks.yml` bereit ist, führen drei Databricks-CLI-Befehle das Bundle von der Prüfung bis zur Ausführung:

**1. `databricks bundle validate`**
Gibt **Warnungen** zurück, wenn unbekannte Ressourceneigenschaften in Bundle-Konfigurationsdateien gefunden werden.

**2. `databricks bundle deploy -t development`**
Gibt an, in welche Umgebung Ihr Bundle **deployed** werden soll. In diesem Beispiel wird das Bundle in die **development**-Umgebung deployed.

**3. `databricks bundle run -t development l1_simple_dab`**
Gibt an, Ihr Bundle in der Umgebung auszuführen. Sie müssen den **Job-Key-Namen** angeben, um den Bundle-Job auszuführen.

```yaml
bundle:
  name: demo01_bundle

resources:
  jobs:
    l1_simple_dab:
      name: my_job_name_l1_simple_dab
      tasks:
        - task_key: create_bronze_table
          notebook_task:
            notebook_path: ./src/create_bronze_table.py
            source: WORKSPACE
. . .
targets:
  development:
    mode: development
    default: true
    workspace:
      host: https://dev.cloud.databricks.com/
```

> **Zusätzliche Notizen (Sprechernotizen):**
>
> - Zuerst validieren Sie Ihr Bundle mit dem CLI-Befehl `databricks bundle validate`.
> - Dann deployen Sie das Bundle in Ihren Databricks-Workspace. Verwenden Sie dazu den Befehl `databricks bundle deploy`, das Flag `-t` für Target, und geben Sie die Umgebung an, in die deployed werden soll. In diesem Beispiel deployen wir in die development-Umgebung. Standardmäßig ist development als Standardziel gesetzt, also geht es ohne Angabe an development. Es ist jedoch Best Practice, explizit zu sein.
> - Sobald das Bundle in Databricks deployed ist, möchten Sie es typischerweise ausführen. Verwenden Sie den Befehl `databricks bundle run`, das Flag `-t` für development und den Key, der den auszuführenden Job angibt. Hier ist der Key `l1_simple_dab`.
> - Und das war's! Wir haben behandelt, wie man ein einfaches Declarative Automation Bundle erstellt, validiert, deployt und ausführt.

## E. Fazit

- Ein **DAB** beschreibt ein Databricks-Projekt (Code, Ressourcen, Konfiguration) in YAML und wird von der Databricks CLI gesteuert, nützlich in Entwicklung und CI/CD.
- Ein Bundle-Projekt folgt einer Standardstruktur: `databricks.yml`, `resources/`, `src/` und `tests/`.
- Die Top-Level-Mappings von `databricks.yml`, besonders **bundle**, **resources** und **targets**, definieren das Bundle.
- Drei CLI-Befehle – **validate**, **deploy** und **run** – führen ein Bundle von der Prüfung bis zur Ausführung.

### Nächste Schritte

Im nächsten Demo deployen Sie ein einfaches DAB und sehen diese Befehle in Aktion.

---

&copy; 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
