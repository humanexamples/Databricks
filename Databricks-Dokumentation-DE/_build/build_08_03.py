# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Kapitel 1&ndash;5 dieser Section haben gezeigt, wie sich PySpark-Code in wiederverwendbare Funktionen zerlegen lässt und wie Unit- sowie Integrationstests dafür sorgen, dass eine Data-Pipeline zuverlässig funktioniert. Declarative Automation Bundles sind das Werkzeug, das diese Bausteine zu einer durchgängigen <strong>CI/CD-Pipeline</strong> zusammenfügt: ein einziges Bundle, das Unit-Tests, eine Lakeflow-Declarative-Pipeline mit eingebauten Integrationstests und eine Visualisierung als einen zusammenhängenden Workflow definiert &ndash; und das identisch über drei Umgebungen (<code>development</code>, <code>stage</code>, <code>production</code>) hinweg promotet wird.</p>

<h2>1. Projektstruktur eines produktionsreifen Bundles</h2>
<p>Während die einfachen Beispiele aus den vorherigen Kapiteln nur einen Job enthielten, zeigt das <em>Full Project</em>-Beispiel aus Modul 06, wie ein realistisches Data-Engineering-Projekt aufgebaut ist:</p>
<table>
<tr><th>Ordner/Datei</th><th>Inhalt</th></tr>
<tr><td><code>databricks.yml</code></td><td>Bundle-Name, <code>include</code>-Liste, drei Targets (development/stage/production)</td></tr>
<tr><td><code>resources/variables.yml</code></td><td>Alle Bundle-Variablen zentral an einer Stelle (Benutzername, E-Mail, Cluster-Lookup, Katalognamen je Umgebung)</td></tr>
<tr><td><code>resources/job/dabs_workflow.job.yml</code></td><td>Der Workflow: drei Tasks (Unit-Tests, Pipeline, Visualisierung)</td></tr>
<tr><td><code>resources/pipeline/health_etl_pipeline.pipeline.yml</code></td><td>Konfiguration der Lakeflow Declarative Pipeline (ehem. Delta Live Tables)</td></tr>
<tr><td><code>src/dlt_pipelines/</code></td><td>Die eigentlichen ETL-Notebooks der Pipeline (Bronze/Silver/Gold)</td></tr>
<tr><td><code>src/helpers/project_functions.py</code></td><td>Wiederverwendbare, testbare Transformationsfunktionen</td></tr>
<tr><td><code>tests/unit_tests/</code></td><td>pytest-Unit-Tests für die Helper-Funktionen</td></tr>
<tr><td><code>tests/integration_test/</code></td><td>Integrationstests als DLT-Expectations innerhalb der Pipeline</td></tr>
</table>

<h2>2. databricks.yml: drei Targets, ein Bundle</h2>
<p>Die Hauptdatei bindet alle Ressourcen-Dateien über <code>include</code> ein und definiert für jedes der drei Targets die abweichenden Werte &ndash; in <code>development</code> und <code>stage</code> laufen die Tasks noch auf einem festen Lab-Cluster, in <code>production</code> dagegen auf Serverless-Compute:</p>

{code('yaml', '''bundle:
  name: health_etl_bundle

include:
  - "./resources/variables.yml"
  - "./resources/pipeline/health_etl_pipeline.pipeline.yml"
  - "./resources/job/dabs_workflow.job.yml"

targets:

  development:
    mode: development
    default: true
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

  stage:
    mode: development
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

  production:
    mode: production
    workspace:
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}
    variables:
      target_catalog: ${var.catalog_prod}
      raw_data_path: /Volumes/${var.catalog_prod}/default/health''')}

<p>Bemerkenswert: <code>stage</code> nutzt technisch denselben <code>mode: development</code> wie die Entwicklungsumgebung (kein produktiver Namens-Präfix nötig, da es noch keine echten Endnutzer gibt), bekommt aber bereits die größere <code>stage</code>-Datenmenge und einen eigenen Katalog zugewiesen &ndash; ein typisches Muster, um eine Vorproduktions-Stufe realistisch zu testen, bevor produktive Daten involviert sind.</p>

<h2>3. Der Workflow: Unit-Tests, Pipeline und Visualisierung als ein Job</h2>
<p>Der Job in <code>resources/job/dabs_workflow.job.yml</code> verkettet drei Tasks unterschiedlichen Typs zu einem Workflow: einen Notebook-Task, der pytest-Unit-Tests ausführt, einen Pipeline-Task, der die Lakeflow-Pipeline anstößt, und einen abschließenden Notebook-Task für die Visualisierung:</p>

{code('yaml', '''resources:
  jobs:
    health_etl_workflow:
      name: health_etl_workflow_${bundle.target}
      description: Final Workflow SDK
      email_notifications:
        on_failure:
          - ${var.my_email}
      tasks:
        - task_key: Unit_Tests
          notebook_task:
            notebook_path: ../../run_unit_tests.ipynb
            source: WORKSPACE
          description: Execute unit tests for project.
        - task_key: Visualization
          depends_on:
            - task_key: Health_ETL
          notebook_task:
            notebook_path: ../../src/Final Visualization.ipynb
            base_parameters:
              catalog_name: ${var.target_catalog}
            source: WORKSPACE
          description: Final visualization for project.
        - task_key: Health_ETL
          depends_on:
            - task_key: Unit_Tests
          pipeline_task:
            pipeline_id: ${resources.pipelines.health_etl_pipeline.id}
            full_refresh: true
          description: Spark Declarative Pipeline

      parameters:
        - name: target
          default: ${bundle.target}
        - name: catalog_name
          default: ${var.target_catalog}''')}

<p>Zwei Dinge sind hier lehrreich. Erstens: Die Task-Reihenfolge im YAML (<code>Unit_Tests</code>, <code>Visualization</code>, <code>Health_ETL</code>) muss nicht der Ausführungsreihenfolge entsprechen &ndash; ausschlaggebend ist ausschließlich <code>depends_on</code>. Zweitens: <code>pipeline_task</code> referenziert die Pipeline nicht über einen festen Namen, sondern über <code>${{resources.pipelines.health_etl_pipeline.id}}</code> &ndash; eine Bundle-interne Referenz, die die CLI beim Deployment automatisch auf die tatsächliche, generierte Pipeline-ID auflöst. Die Pipeline selbst wird in einer eigenen Datei definiert und bindet die ETL-Notebooks sowie die Integrationstests als Bibliotheken ein:</p>

{code('yaml', '''resources:
  pipelines:
    health_etl_pipeline:
      name: health_etl_pipeline_${bundle.target}
      libraries:
        - glob:
            include: ../../src/dlt_pipelines/gold_tables_dlt.sql
        - glob:
            include: ../../src/dlt_pipelines/ingest-bronze-silver_dlt.py
        - glob:
            include: ../../tests/integration_test/integration_tests_dlt
      schema: ${var.schema}
      photon: true
      catalog: ${var.target_catalog}
      serverless: true
      root_path: ../../src/dlt_pipelines
      configuration:
        target: ${bundle.target}
        raw_data_path: ${var.raw_data_path}''')}

<h2>4. Unit-Tests im Bundle-Kontext</h2>
<p>Die pytest-Mechanik selbst (<code>assertDataFrameEqual</code>, die Session-Fixture, der Test gegen <code>project_functions.high_cholest_map</code>) wurde bereits in Kapitel 3 dieser Section ausführlich gezeigt und wird hier unverändert wiederverwendet &ndash; neu ist nur, <em>wo</em> dieser Test im Bundle liegt und wie er ausgeführt wird: Die Testdatei liegt unter <code>tests/unit_tests/</code>, und der Workflow-Task <code>Unit_Tests</code> führt sie über das Notebook <code>run_unit_tests.ipynb</code> aus (siehe <code>notebook_task</code> in Kapitel 3 oben) &ndash; nicht direkt per <code>pytest</code>-Kommandozeilenaufruf.</p>

<h2>5. Integrationstests im Bundle-Kontext</h2>
<p>Auch die Integrationstest-Mechanik selbst (Expectation gegen eine erwartete Zeilenanzahl je Umgebung) entspricht dem in Kapitel 4 dieser Section gezeigten Muster. Neu und bundle-spezifisch ist die <strong>Ziel-abhängige Test-Auswahl über <code>target</code></strong>: In <code>development</code> und <code>stage</code> laufen die Prüfungen auf Bronze, Silver <em>und</em> Gold, in <code>production</code> dagegen bewusst nur die Prüfung der Gold-Tabelle &ndash; da dort die absolute Zeilenzahl täglich wächst und ein fester Sollwert keinen Sinn ergäbe:</p>

{code('python', '''# Je nach Zielumgebung unterschiedliche Tests ausfuehren
if target in (\'development\', \'stage\'):
    test_count_table_total_rows(\'health_bronze\', total_expected_bronze, target)
    test_count_table_total_rows(\'health_silver\', total_expected_silver, target)
    test_gold_table_columns()
elif target == \'production\':
    test_gold_table_columns()   # In Produktion nur die Gold-Tabelle pruefen''')}

<h2>6. Promotion über drei Umgebungen</h2>
<p>Der eigentliche CI/CD-Ablauf besteht darin, exakt dieselben Befehle nacheinander gegen alle drei Targets auszuführen &ndash; nichts an der Bundle-Definition ändert sich zwischen den Umgebungen, nur die Zielangabe <code>-t</code>:</p>

{code('bash', '''# 1. Entwicklung: Unit-Tests + ETL + Integrationstests auf 7.500 Beispielzeilen
databricks bundle validate -t development
databricks bundle deploy -t development
databricks bundle run health_etl_workflow

# 2. Staging: dieselbe Definition, jetzt gegen 35.000 Zeilen Stage-Daten
databricks bundle validate -t stage
databricks bundle deploy -t stage
databricks bundle run health_etl_workflow -t stage

# 3. Produktion: volle Datenmenge, Serverless-Compute statt Lab-Cluster
databricks bundle validate -t production
databricks bundle deploy -t production
databricks bundle run health_etl_workflow -t production

# Variablen lassen sich bei Bedarf auch direkt ueberschreiben, ohne die YAML zu aendern
databricks bundle validate --var="target_catalog=labuser123_2_stage" -t stage

# Aufraeumen: alle drei Umgebungen entfernen
databricks bundle destroy -t development --auto-approve
databricks bundle destroy -t stage --auto-approve
databricks bundle destroy -t production --auto-approve''')}

<figure class="img">
<img src="assets/08/cicd-dev-job-run.png">
<figcaption>Erfolgreicher Lauf des dreistufigen Workflows (Unit_Tests &rarr; Health_ETL &rarr; Visualization) im development-Target &ndash; alle Tasks grün, Job-Parameter zeigen den Dev-Katalog.</figcaption>
</figure>

<p>In einer echten CI/CD-Pipeline (z.&nbsp;B. GitHub Actions) werden diese Befehle nicht manuell aus einem Notebook heraus gestartet, sondern automatisiert bei jedem Push bzw. Merge ausgeführt: ein Validate-Lauf bei jedem Pull Request, ein Deploy-nach-Development bei jedem Merge in einen Feature-Branch, und ein Deploy-nach-Production erst nach manueller Freigabe. Für die Authentifizierung wird dabei statt eines persönlichen Zugangs in der Regel ein <strong>Service Principal</strong> verwendet (siehe <code>run_as</code>-Einstellung in der Bundle-Konfiguration).</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks empfiehlt für produktive CI/CD-Pipelines mit Asset Bundles die <strong>Workload Identity Federation</strong> zur Authentifizierung gegenüber dem Workspace, da sie ohne dauerhaft gespeicherte Secrets auskommt und damit sicherer ist als klassische Personal-Access-Tokens. In der Praxis hat sich bewährt, GitHub-Actions-Workflows nach Zweck zu trennen (z.&nbsp;B. eigene Workflow-Dateien für Validierung, Dev-Deployment und Prod-Deployment), damit nicht jede Codeänderung versehentlich einen Produktions-Deploy auslöst. Ziel bleibt, dieselbe Bundle-Definition unverändert von der Entwicklungs- bis zur Produktionsumgebung zu bewegen und Konfigurationsabweichungen (&bdquo;Drift&ldquo;) zwischen den Stufen zu minimieren.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/dev-tools/ci-cd/best-practices">Best practices and recommended CI/CD workflows on Databricks &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 5 - Implementing CI-CD\08 CI-CD mit Asset Bundles - Tests und Pipelines kombiniert.pdf",
    title="CI/CD mit Asset Bundles (Tests + Pipelines kombiniert)",
    subtitle="Section 5 &middot; Implementing CI-CD &middot; Quelle: Kurs 8, Modul 06",
    body_html=body,
    build_name="08_03_cicd_asset_bundles",
)
print("OK")
