![DB Academy](../Includes/images/common/db-academy.png)

# [Video-Tutorial](https://customer-academy.databricks.com/learn/courses/3724/automated-deployment-with-declarative-automation-bundles/lessons/33992/demo-continuous-integration-and-continuous-deployment-with-dabs)

# 06 - Kontinuierliche Integration und kontinuierliche Bereitstellung (CI/CD) mit Declarative Automation Bundles (DABs)

## Überblick

In dieser Demonstration bauen Sie auf allem auf, was Sie bisher über DABs gelernt haben, und wenden es auf einen CI/CD-Workflow mit drei Umgebungen (`development`, `stage`, `production`) an.

Das Bundle stellt einen Workflow bereit, der **Unit-Tests**, eine **Lakeflow Spark Declarative Pipeline (SDP)** für ETL- und Integrationstests sowie ein **Visualisierungs-Notebook** ausführt. Jedes Target überschreibt den Catalog, den Rohdatenpfad und (für dev/stage) die Compute-Ressource, während Production auf Serverless läuft.

## Lernziele

Am Ende dieser Demonstration können Sie:

1. **Ein Multi-File-Bundle lesen und nachvollziehen**, das Ressourcen in YAML-Dateien pro Asset aufteilt und eine dedizierte `variables.yml` verwendet.
2. **Bundle-Variablen setzen** (einschließlich einer `lookup`-Variable, die einen Cluster-Namen in eine Cluster-ID auflöst).
3. **Unit-Tests, eine Lakeflow Spark Declarative Pipeline und eine Visualisierung** als einen einzigen Workflow deployen und ausführen.
4. **Dasselbe Bundle über die Targets `development`, `stage` und `production` hinweg befördern (promoten)** mit Target-spezifischen Überschreibungen für Catalog, Rohdatenpfad und Compute.
5. **Variablen über die CLI überschreiben** mit `databricks bundle <command> --var="<name>=<value>" -t <target>`.

## ERFORDERLICH - WÄHLEN SIE EINE COMPUTE-UMGEBUNG

**Wählen Sie All-Purpose Compute**

Dieses Notebook erfordert **All-Purpose Compute** (Dedicated). Serverless wird für dieses Notebook nicht unterstützt.

Führen Sie die folgenden Schritte aus, um einen All-Purpose-Compute-Cluster anzuhängen:

1. Navigieren Sie oben rechts in diesem Notebook und klicken Sie auf das Dropdown-Menü, um Ihren `labuser_USERNAME`-Cluster auszuwählen.
- Standardmäßig verwendet das Notebook möglicherweise **Serverless**.

2. Wenn Ihr Cluster verfügbar ist, wählen Sie ihn aus und fahren Sie mit der nächsten Zelle fort. Wenn der Cluster nicht angezeigt wird:

- Wählen Sie im Dropdown-Menü **More** aus.

- Wählen Sie im Popup **Attach to an existing compute resource** das erste Dropdown-Menü aus. Dort sehen Sie einen eindeutigen Cluster-Namen. Bitte wählen Sie diesen Cluster aus.

⚠️ **HINWEIS:** Wenn der Cluster den Status **terminated** anzeigt (roter Punkt in der Cluster-Auswahl), muss er gestartet werden, bevor Sie ihn anhängen können. Klicken Sie auf den Cluster und dann auf **Start** und warten Sie einige Minuten, bis Sie einen grünen Punkt sehen.

## ERFORDERLICH - DATEN-SETUP

**Daten-Setup**

Denken Sie daran, dass Ihre Umgebung mit dem Notebook **0 - REQUIRED - Course Setup and Authentication** eingerichtet wurde.

Wenn Sie Ihr Lab beenden oder Ihre Lab-Sitzung abläuft, wird Ihre Umgebung zurückgesetzt. Sie müssen das Notebook **0 - REQUIRED - Course Setup and Authentication** erneut ausführen, um die Catalogs und Daten für Ihre Umgebung neu zu erstellen.

## A. Classroom-Setup

Führen Sie die folgende Zelle aus, um Ihre Arbeitsumgebung für diesen Kurs zu konfigurieren.

**HINWEIS:** Das `DA`-Objekt wird nur in Databricks Academy-Kursen verwendet und ist außerhalb dieser Kurse nicht verfügbar. Es referenziert dynamisch die Informationen, die zur Durchführung des Kurses benötigt werden.

```text
%run ../Includes/Classroom-Setup-06
```

Führen Sie die folgende Zelle aus, um zu bestätigen, dass die Databricks CLI funktioniert.

```bash
%sh
databricks catalogs list
```

## B. Vorkonfigurierte YAML-Dateien untersuchen

Unser Ziel ist es, unser Projekt für unsere CI/CD-Pipeline in den Umgebungen `dev`, `stage` und `prod` zu deployen.

In diesem Beispiel ist das Projekt ein einfacher Workflow, der Unit-Tests, eine Lakeflow Spark Declarative Pipeline und eine Notebook-Visualisierung enthält.

![Workflow](./images/06_Final_Workflow_Desc.png)

**
Voraussetzungen
**

Dieser fortgeschrittene Kurs setzt Vorkenntnisse in wesentlichen DevOps-Konzepten voraus, wie Code-Modularisierung, benutzerdefinierte Python-Funktionen, Unit-Testing mit pytest und Integrationstests mit Spark Declarative Pipelines.

Eine Auffrischung dieser Themen finden Sie im Databricks-Kurs **DevOps Essentials for Data Engineering**. Wir streifen hier jedes dieser Themen, der Fokus dieses Kurses liegt jedoch auf dem Deployment mit Declarative Automation Bundles.

Lassen Sie uns unseren Projektordner mit dem Namen **Full Project** erkunden. Dieser Ordner enthält alle unsere zu deployenden Databricks-Ressourcen.

Im Stammordner (Root-Ordner) finden Sie Folgendes:

  - **src/**
  - **resources/**
  - **databricks.yml**
  - **tests/**

1. Öffnen Sie in einem neuen Tab die Datei **databricks.yml**.

- Sie beginnt mit der Definition des Bundle-Namens unter dem Mapping `bundle`.
- **health_etl_bundle**

- Sie definiert die einzubindenden Ressourcen unter dem Mapping `include`.
- Alle YAML-Konfigurationsdateien für die Ressourcen befinden sich im Ordner **resources/**.

- Unter dem übergeordneten Mapping `targets` sehen Sie drei definierte Targets mit jeweils unterschiedlichen Konfigurationsdetails: `development`, `stage` und `production`.
- Alle drei Targets haben einen `root_path`.
- Alle drei Targets verfügen über spezifische Konfigurationen.
- Die Targets `stage` und `production` verfügen über zusätzliche Variablen, die wir konfigurieren müssen, wie `target_catalog` und `raw_data_path`, um die richtigen Daten anzugeben.

2. Öffnen Sie im neuen Tab **resources/**.

- Klicken Sie auf die YAML-Datei mit dem Namen **variables.yml**.
- Sie enthält vordefinierte Variablen für die Ressourcen, die beim Deployen des Bundles bereitgestellt werden.
- Dazu gehören unter anderem der Job-Name, Notebook-Pfade und Parameter, die an die Notebooks übergeben werden.

- Sie finden zwei Ordner für eine Job- und eine SDP-Ressource:
- **job/**
- Die Datei **dabs_workflow.job.yml** (im Ordner **job/**) beschreibt die Tasks, die erstellt werden.
- Beachten Sie, dass es 3 Tasks gibt: **Unit_Tests**, **Visualization** und **Health_ETL**.
- Obwohl **Health_ETL** nach **Visualization** aufgeführt ist, hängt es von **Unit_Tests** ab.
- Die Reihenfolge der Tasks spielt keine Rolle, da der Schlüssel `depends_on` die Abhängigkeiten konfiguriert.

- **pipeline/**
- Die Datei **health_etl_pipeline.pipeline.yml** (im Ordner **pipeline/**) beschreibt die Konfiguration der Spark Declarative Pipeline.

3. Navigieren Sie im neuen Tab zurück zu **src/** im Stammordner.

Dieser Ordner enthält weitere Ordner und Notebooks, die von den YAML-Dateien aufgerufen werden, die Sie in den vorherigen Schritten untersucht haben. Diese Notebooks sind als Teil des Workflows, den wir im Folgenden deployen, miteinander verkettet.

- **dlt_pipelines/**: enthält zwei Spark Declarative Pipeline-Notebooks:
- **gold_tables_dlt**
- **ingests-bronze-silver_dlt**
- Sie können diese Notebooks untersuchen, um deren Rolle im **Health_ETL**-Workflow zu verstehen.

- **Final Visualization**: Dieses Notebook ist die letzte Task in unserem Workflow.
- Es erstellt ein gestapeltes Balkendiagramm der Cholesterinverteilung nach Altersgruppe.

- **helpers/**: enthält eine `.py`-Datei mit benutzerdefinierten Python-Methoden für die Transformation der Daten in der Pipeline.

## C. YAML-Konfigurationsdateien erkunden und aktualisieren
Wir aktualisieren unsere YAML-Dateien, um besser zu verstehen, wie auf die Assets und Variablen verwiesen wird, die zur Konfiguration des Bundles benötigt werden, bevor wir es mit der Databricks CLI validieren.

### C1. Die databricks.yml-Konfiguration erkunden

Denken Sie daran: Um eine Variable namens `my_variable` in einem Bundle zu verwenden, referenzieren Sie sie mit `${var.my_variable}`.

#### Anweisungen

1. Navigieren Sie zum Ordner mit dem Namen **Full Project**.

2. Klicken Sie auf die Datei **databricks.yml** und erkunden Sie die Bundle-Konfiguration.

3. Suchen Sie das Mapping **targets**.
   - Jedes Target ist eine eindeutige Sammlung von Artefakten, Databricks-Workspace-Einstellungen sowie Job- oder Pipeline-Details.
   - Das Mapping targets besteht aus einem oder mehreren Target-Mappings, die jeweils einen eindeutigen programmatischen (oder logischen) Namen haben müssen.

4. Suchen Sie das Target **development** und untersuchen Sie die Konfiguration. Beachten Sie Folgendes:
   - Der Wert für `default` ist auf `True` gesetzt.
   - Der Wert für `existing_cluster_id` verwendet die Variable `cluster_id`.
   - Die **Tasks** sind so konfiguriert, dass sie unseren Lab-Compute-Cluster verwenden.

5. Suchen Sie das Target **stage** und untersuchen Sie die Konfiguration. Beachten Sie Folgendes:
   - Die Variable `target_catalog` verwendet die Variable `catalog_stage`.
   - Die Variable `raw_data_path` verwendet das Volume `health` in `catalog_stage`.
   - Die **Tasks** sind so konfiguriert, dass sie unseren Lab-Compute-Cluster verwenden.

6. Suchen Sie das Target **production** und untersuchen Sie die Konfiguration. Beachten Sie Folgendes:
   - Die Variable `target_catalog` verwendet die Variable `catalog_prod`.
   - Die Variable `raw_data_path` verwendet das Volume `health` in `catalog_prod`.
   - Für den Job ist kein Compute-Cluster angegeben. Die Standard-Compute-Ressource verwendet in Production Serverless.

```python
print(f'Your user name: {my_catalog}')
```

### C2. `variables.yml` aktualisieren

Als Nächstes aktualisieren wir die Datei **variables.yml**.

#### Anweisungen

1. Navigieren Sie zum Ordner **resources/**.

2. Klicken Sie auf die Datei **variables.yml**.

3. Tragen Sie die folgenden Angaben für die Variablen ein:

   - **TO DO**: `username`: Fügen Sie hier Ihren Benutzernamen ein. Ihren Benutzernamen finden Sie in der Zelle oben.
- Verwenden Sie `${workspace.current_user.short_name}`

   - **TO DO**: `my_email`: Geben Sie hier Ihre E-Mail-Adresse ein. Diese wird verwendet, um Benachrichtigungen zu senden.
- Verwenden Sie Ihre E-Mail-Adresse.

   - **AUFGABE**: `cluster_id`:
- Verwenden Sie die Funktion `lookup` mit Ihrem Benutzernamen, um den Wert der Cluster-ID zu ermitteln.
- Fügen Sie den Wert aus der Zelle oben für die lookup-Cluster-ID-Variable ein.

**
Informationen
**

- Die Datei **variables_solution.yml** enthält eine Beispiellösung, falls Sie Hilfe benötigen.

- In der Databricks Academy-Lab-Umgebung stimmen alle Catalogs, Cluster und Benutzernamen standardmäßig überein und enthalten keine Leerzeichen.

## D. Visualisierung der Assets des Declarative Automation Bundles

Hier betrachten wir, wie wir unsere YAML-Dateien manuell aktualisieren können, um uns mit dem Setup vertraut zu machen.

Da wir ein vorkonfiguriertes Bundle verwenden, lohnt es sich, die Struktur der Dateien zu betrachten, mit denen wir arbeiten werden. Im Folgenden sehen Sie ein Diagramm, das darstellt, wie die Variablen für den Development-Catalog verwendet werden.

![Full Pipeline](./images/06_img1.png)

## E. Notebook-Ausführung

Nachdem wir nun mit den verschiedenen Ordnern und Dateien vertraut sind, aus denen unser Bundle besteht, stellen wir sicher, dass die CLI installiert ist, indem wir uns authentifizieren.

### E1. Development-Bundle

So sieht die Konfiguration unseres Target-Mappings für development in der Datei databricks.yml aus.
```YAML
targets:

  development:
    mode: development
    default: true
    # In Development verwenden wir für unsere Tasks Classic Compute 
    resources:
      jobs:
        health_etl_workflow:    
          name: health_etl_workflow_${bundle.target} 
          tasks:
            - task_key: Unit_Tests
              existing_cluster_id: ${var.cluster_id}
            - task_key: Visualization
              existing_cluster_id: ${var.cluster_id}
    workspace:
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}
...
```

**HINWEIS:** Denken Sie daran, dass wir bei den Target-Umgebungen **development** und **stage** auf Task-Ebene eine Mischung aus Serverless und Classic Compute verwenden.

1. Um das Bundle zu validieren, führen Sie die folgende Zelle aus.

Dies verwendet alle Standardwerte aus **variables.yml** (siehe Diagramm oben).

**Development validieren**

```bash
%sh 
cd "Full Project" 
pwd;
databricks bundle validate -t development
```

**
Fehlerbehebung
**

Wenn nach der Validierung Ihres Bundles der folgende Fehler angezeigt wird, könnte das Format Ihres Notebooks fehlerhaft sein.

`Error: notebook xxx.ipynb not found`. 

Überprüfen Sie das Format Ihres Notebooks und passen Sie es entsprechend an.

2. Nachdem das Target development erfolgreich validiert wurde, deployen Sie das Bundle in die Development-Umgebung.

**In Development deployen**

```bash
%sh
cd "Full Project" 
databricks bundle deploy -t development
```

3. Navigieren Sie in einem neuen Tab zu **Jobs & Pipelines** und sehen Sie sich Ihren deployten Job an.
- Lassen Sie diesen Tab geöffnet.

#### Checkpoint
![Dev CICD Pipeline](../Includes/images/cicd-pipeline/dev-deployed-job.png)

4. Um das Bundle über die Databricks CLI auszuführen, führen Sie die folgende Zelle aus. Beachten Sie, dass der Job in **Jobs and Pipelines** als **[dev ] health_etl_workflow_** angezeigt wird.

Dies wird verständlich, wenn Sie sich die Struktur der Datei **dabs_workflow.job.yml** im Ordner **resources/** noch einmal ansehen:

```yaml
    resources:
      jobs:
        health_etl_workflow:                          # <--- Job-Schlüssel (von `bundle run` verwendet)
          name: health_etl_workflow_${bundle.target}  # <--- Job-Name (in der UI angezeigt)
          description: Final Workflow SDK
    ```

**Bundle in Development ausführen**

```bash
%sh
cd "Full Project" 
databricks bundle run health_etl_workflow 
```

5. Navigieren Sie zurück zu Ihrem Job und sehen Sie sich den erfolgreichen Lauf in development an.

#### Checkpoint - Dev-Lauf
![Dev CICD Pipeline](../Includes/images/cicd-pipeline/dev-job-run.png)

**
Zusammenfassung - Development
**

Während der Job läuft, untersuchen Sie die Tasks bei Verwendung des Targets `development`.

  Beachten Sie Folgendes:
- Die Unit-Tests waren erfolgreich.
- Die Lakeflow Spark Declarative Pipeline sowie die ETL- und Integrationstests waren bei einer kleinen Stichprobe von 7.500 Zeilen Dev-Daten erfolgreich.
- Die Visualisierung wurde anhand der kleinen Stichprobe von 7.500 Zeilen Dev-Daten erstellt.

### E2. Staging-Bundle

So sieht die Konfiguration unseres Mappings `targets` für `stage` in **databricks.yml** aus:

```yaml
  ...

  stage:
    mode: development
      # In Stage verwenden wir für unsere Tasks Classic Compute
    resources:
      jobs:
        health_etl_workflow:
          name: health_etl_workflow_${bundle.target}
          tasks:
            - task_key: Unit_Tests
              existing_cluster_id: ${var.cluster_id}
            - task_key: Visualization
              existing_cluster_id: ${var.cluster_id}
    workspace:
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}
    variables:
      target_catalog: ${var.catalog_stage}
      raw_data_path: /Volumes/${var.catalog_stage}/default/health
```

Stellen Sie sich vor, Sie haben Ihren Code überprüft, die Testabdeckung analysiert und so weiter, und sind nun bereit, in einer Staging-Umgebung zu deployen und zu testen.

DABs vereinfacht dies, indem nur einige wenige Parameterwerte angepasst werden. Führen Sie die folgenden Zellen aus, um mit `stage` als Target zu validieren, zu deployen und auszuführen.

Da `target_catalog` und `raw_data_path` in diesem Beispiel Standardwerte haben, überschreiben wir diese beim Deployen in andere Targets wie `stage` innerhalb des Mappings `targets`. Dadurch liest der Job Daten aus dem Staging-Catalog.

**
Bonus: Variablen überschreiben
**

Sie können Variablenwerte auch direkt über die Databricks CLI überschreiben. Zum Beispiel: `databricks bundle validate --var="target_catalog=<username>_2_stage" -t stage`. Beachten Sie, dass dies lediglich denselben Job reproduziert, den Sie gerade ausgeführt haben.

**Staging validieren**

```bash
%sh
cd "Full Project" 
databricks bundle validate -t stage
```

**In Staging deployen**

```bash
%sh
cd "Full Project" 
databricks bundle deploy -t stage
```

**Bundle in Staging ausführen**

```bash
%sh
cd "Full Project" 
databricks bundle run health_etl_workflow -t stage
```

#### Checkpoint - Stage-Lauf
![Stage CICD Pipeline](../Includes/images/cicd-pipeline/stage-job-run.png)

**
Zusammenfassung - Stage
**

Während der Job läuft, öffnen Sie den gestageten Job (**[dev labuser_UNIQUE_ID] health_etl_workflow_stage**) und untersuchen Sie die Tasks bei Verwendung des Targets `stage`.

  Beachten Sie Folgendes:
- Die Unit-Tests waren erfolgreich.
- Die Lakeflow Spark Declarative Pipeline sowie die ETL- und Integrationstests waren bei einer Stichprobe von 35.000 Zeilen Stage-Daten erfolgreich.
- Die Visualisierung wurde anhand der Stichprobe von 35.000 Zeilen Stage-Daten erstellt.

### E3. Production
So sieht die Konfiguration unseres Target-Mappings für production in der Datei **databricks.yml** aus.
```YAML
  production:
    mode: production
    workspace:
      # host: Host kann geändert werden, wenn nach Workspace isoliert wird
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}
    variables:
      target_catalog: ${var.catalog_prod}
      raw_data_path: /Volumes/${var.catalog_prod}/default/health
```

Hier wiederholen wir dieselben Bash-Befehle mit `%sh`.

Beachten Sie jedoch, dass die gesamte Production-Compute auf **Serverless statt Classic Compute** läuft, da wir die Standard-Compute nicht überschreiben.

Sie können dies überprüfen, indem Sie den Job deployen und die Tasks untersuchen.

**Production validieren**

```bash
%sh
cd "Full Project" 
databricks bundle validate -t production
```

**In Production deployen**

```bash
%sh
cd "Full Project" 
databricks bundle deploy -t production
```

**Bundle in Production ausführen**

```bash
%sh
cd "Full Project" 
databricks bundle run health_etl_workflow -t production
```

#### Checkpoint - Production-Lauf
![Prod CICD Pipeline](../Includes/images/cicd-pipeline/prod-job-run.png)

## F. Alle Bundles löschen

Nachdem wir das Bundle für alle drei Targets validiert, deployt und ausgeführt haben, räumen wir auf, indem wir jedes einzelne löschen. Die folgende Zelle löscht `development`, `stage` und `production` nacheinander.

```bash
%sh
cd "Full Project";
databricks bundle destroy -t development --auto-approve;
databricks bundle destroy -t stage --auto-approve;
databricks bundle destroy -t production --auto-approve;
```

## Fazit

In dieser Demonstration haben Sie einen End-to-End-CI/CD-Workflow durchlaufen, bei dem ein einzelnes Bundle über drei Targets hinweg befördert (promotet) wurde:

1. Ein reales Bundle untersucht, das Ressourcen in YAML-Dateien pro Asset (`job/`, `pipeline/`) sowie eine dedizierte `variables.yml` aufteilt.
2. Die Variablen `username`, `my_email` und `cluster_id` (lookup) gesetzt, damit das Bundle für Ihr Lab korrekt aufgelöst wird.
3. Den Workflow für das Target `development` validiert, deployt und ausgeführt (7.500 Zeilen auf Classic Compute).
4. Dasselbe Bundle durch Überschreiben von `target_catalog` und `raw_data_path` auf das Target `stage` befördert (35.000 Zeilen auf Classic Compute).
5. Dasselbe Bundle auf das Target `production` befördert (vollständiger Datensatz auf Serverless Compute).
6. Aufgeräumt, indem alle drei Targets mit `databricks bundle destroy --auto-approve` pro Target gelöscht wurden.

## Nächste Schritte

![ci_cd](./images/ci_cd_overview.png)

Überlegen Sie, wie Sie DABs nutzen können, um die Entwicklung durch die programmatische Verwaltung Ihrer Workflows zu beschleunigen. Mit DABs können Sie Ihre verschiedenen Assets und Artefakte für CI/CD-Workflows konsistent und wiederholbar erstellen, verwalten und deployen.

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
