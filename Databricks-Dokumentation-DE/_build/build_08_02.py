# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Ein Bundle, das nur eine einzige Zielumgebung kennt, deckt selten die Realität ab: Meist soll derselbe Job in einer kleinen, günstigen Entwicklungsumgebung getestet werden, bevor er unverändert gegen die vollständigen Produktionsdaten läuft &ndash; ohne die Job-Definition zweimal pflegen zu müssen. Declarative Automation Bundles lösen das über drei Mechanismen, die zusammenspielen: mehrere Einträge in der <code>targets</code>-Zuordnung, wiederverwendbare <strong>Bundle-Variablen</strong> und die <code>include</code>-Zuordnung, mit der sich Ressourcen-Definitionen in eigene YAML-Dateien auslagern lassen.</p>

<h2>1. Ressourcen modularisieren mit include</h2>
<p>Statt die komplette Job-Definition direkt in <code>databricks.yml</code> zu schreiben, lagert man sie &ndash; sobald ein Projekt wächst &ndash; in eine eigene Datei im <code>resources</code>-Ordner aus und bindet sie über <code>include</code> ein. Das hält die Hauptdatei übersichtlich und erlaubt es, mehrere Personen parallel an unterschiedlichen Ressourcen zu arbeiten:</p>

{code('yaml', '''include:
  - "./resources/demo_03_job.job.yml"       # Full Job Configuration within the resources folder''')}

{code('yaml', '''# resources/demo_03_job.job.yml
resources:
  jobs:
    demo03_job:
      name: ${bundle.target}_demo3_dab_${workspace.current_user.userName}
      tasks:
        - task_key: create_bronze_table
          notebook_task:
            notebook_path: ../src/create_bronze_table.ipynb
            source: WORKSPACE
        - task_key: create_silver_table
          depends_on:
            - task_key: create_bronze_table
          notebook_task:
            notebook_path: ../src/create_silver_table.ipynb
            source: WORKSPACE
      parameters:
      - name: display_target
        default: ${bundle.target}
      - name: catalog_name
        default: ${var.target_catalog}''')}

<p>Auffällig ist, dass weder Jobname noch Katalog fest verdrahtet sind, sondern über Platzhalter (<code>${{...}}</code>) referenziert werden. <code>${{bundle.target}}</code> wird automatisch durch den Namen des aktuell deployten Targets ersetzt (z.&nbsp;B. <code>development</code> oder <code>production</code>); <code>${{var.target_catalog}}</code> verweist auf eine selbst definierte Bundle-Variable.</p>

<h2>2. Bundle-Variablen und Lookup-Variablen</h2>
<p>Variablen werden zentral in der Top-Level-Zuordnung <code>variables</code> deklariert und können sich gegenseitig referenzieren, sodass sich z.&nbsp;B. aus einem Benutzernamen automatisch mehrere Katalognamen ableiten lassen:</p>

{code('yaml', '''variables:
  my_lab_user_name:
    description: Add your lab user name
    default: ${{workspace.current_user.short_name}}      # dynamisch der eigene Benutzername

  catalog_dev:
    description: Development catalog for the project. Append _1_dev to the user name.
    default: ${{var.my_lab_user_name}}_1_dev

  catalog_prod:
    description: Production catalog for the project. Append _3_prod to the user name.
    default: ${{var.my_lab_user_name}}_3_prod

  target_catalog:
    description: Target catalog to use for deployment - default is \'dev\'.
    default: ${{var.catalog_dev}}

  raw_data_path:
    description: Path to source CSV files to ingest (dev/stage/prod) - default is \'dev\'.
    default: /Volumes/${{var.target_catalog}}/default/health

  ## Lookup-Variable: ermittelt die Cluster-ID anhand des Cluster-Namens
  my_cluster_id:
    description: Get the lab cluster ID using a lookup variable.
    lookup:
      cluster: labuser15933383_1784728005'''.replace('{{','{').replace('}}','}'))}

<p>Der letzte Eintrag zeigt eine <strong>Lookup-Variable</strong>: Statt einen festen Wert einzutragen, sucht die CLI beim Deployment ein bestehendes Objekt (hier: einen Cluster) über seinen Namen und löst die Variable automatisch zu dessen ID auf. Lookups funktionieren für zahlreiche Objekttypen, u.&nbsp;a. <code>cluster</code>, <code>job</code>, <code>pipeline</code>, <code>warehouse</code>, <code>metastore</code> und <code>service_principal</code> &ndash; nützlich überall dort, wo eine Konfiguration auf eine ID verweisen muss, die je nach Workspace unterschiedlich ist.</p>

<h2>3. Targets: pro Umgebung unterschiedliche Werte</h2>
<p>Erst in der <code>targets</code>-Zuordnung bekommen die Variablen ihre konkreten, umgebungsspezifischen Werte. Jedes Target kann Werte aus <code>variables</code> überschreiben und sogar einzelne Task-Eigenschaften (z.&nbsp;B. das Rechencluster) direkt in der <code>resources</code>-Struktur überschreiben:</p>

{code('yaml', '''targets:

  development:
    mode: development
    default: true
    workspace:
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

    # Kleines Lab-Cluster fuer die Entwicklungsumgebung verwenden
    resources:
      jobs:
        demo03_job:
          tasks:
            - task_key: create_bronze_table
              existing_cluster_id: ${var.my_cluster_id}
            - task_key: create_silver_table
              existing_cluster_id: ${var.my_cluster_id}

  production:
    mode: production
    workspace:
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

    ## Im Produktions-Target auf den Produktionskatalog umschalten
    variables:
        target_catalog: ${var.catalog_prod}''')}

<p>Im Beispiel bekommt nur die Entwicklungsumgebung ein fest zugewiesenes (kleines) Cluster &ndash; sinnvoll, weil die Entwicklungsdaten klein und statisch sind. Für <code>production</code> wird keine Compute-Vorgabe überschrieben, sodass der Job auf Serverless-Compute läuft, das sich automatisch an wachsende Datenmengen anpasst. Die Variable <code>target_catalog</code> zeigt standardmäßig auf den Dev-Katalog (<code>${{var.catalog_dev}}</code>); nur im <code>production</code>-Target wird sie explizit auf <code>${{var.catalog_prod}}</code> umgebogen &ndash; die Job-Definition selbst bleibt dabei komplett unverändert.</p>

<figure class="img">
<img src="assets/08/multi-env-dev-deployment.png">
<figcaption>Derselbe Job, deployt im development-Target: Der Job-Name trägt automatisch das Präfix [dev &lt;benutzername&gt;], und beide Tasks laufen auf dem fest zugewiesenen Lab-Cluster.</figcaption>
</figure>
<figure class="img">
<img src="assets/08/multi-env-prod-deployment.png">
<figcaption>Dasselbe Bundle im production-Target deployt: Job-Parameter und Katalog wurden automatisch auf die Produktionswerte umgeschaltet.</figcaption>
</figure>

<h2>4. Bundle validieren, deployen und pro Ziel ausführen</h2>
<p>Mit <code>--output json</code> lässt sich die vollständig aufgelöste Konfiguration (alle Variablen bereits ersetzt) prüfen, bevor tatsächlich deployt wird &ndash; hilfreich, um Substitutionsfehler frühzeitig zu erkennen:</p>

{code('bash', '''# Aufgeloeste Konfiguration im development-Target als JSON anzeigen
databricks bundle validate --output json

# In die Entwicklungsumgebung deployen und den Job dort ausfuehren
databricks bundle deploy -t development
databricks bundle run -t development demo03_job

# Dieselbe, unveraenderte Bundle-Definition in die Produktion deployen
databricks bundle deploy -t production
databricks bundle run -t production demo03_job

# Variablen bei Bedarf gezielt von der Kommandozeile ueberschreiben
databricks bundle deploy --var="target_catalog=labuser123_3_prod" -t production

# Beide Umgebungen wieder aufraeumen
databricks bundle destroy --auto-approve
databricks bundle destroy -t production --auto-approve''')}

<table>
<tr><th>Quelle des Variablenwerts</th><th>Priorität</th></tr>
<tr><td><code>--var</code>-Option beim CLI-Aufruf</td><td>höchste Priorität</td></tr>
<tr><td>Umgebungsvariable <code>BUNDLE_VAR_&lt;name&gt;</code></td><td>2</td></tr>
<tr><td>Datei <code>variable-overrides.json</code></td><td>3</td></tr>
<tr><td><code>variables</code>-Zuordnung innerhalb eines Targets</td><td>4</td></tr>
<tr><td>Standardwert (<code>default</code>) in der Top-Level-<code>variables</code>-Zuordnung</td><td>niedrigste Priorität</td></tr>
</table>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Targets sind laut Databricks der einfachste Weg, Umgebungsunterschiede abzubilden, ohne das Bundle zu duplizieren &ndash; typischerweise ändert ein Target nur den Ziel-Workspace, die Namensgebung der Ressourcen und eine kleine Menge an Laufzeitvariablen wie Katalog, Schema oder Service Principal, während alles andere beim Übergang von Dev zu Prod identisch bleibt. Für Lookup-Variablen gilt: Ist ein Lookup definiert, wird stets die aktuell aufgelöste ID des benannten Objekts verwendet, unabhängig vom Zielworkspace. Bei der Variablenauflösung gewinnt immer die erste gefundene Quelle in der oben gezeigten Prioritätsreihenfolge.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/dev-tools/bundles/variables">Substitutions and variables in Declarative Automation Bundles &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 5 - Implementing CI-CD\07 Multi-Environment-Deployments - Targets und Variablen.pdf",
    title="Multi-Environment-Deployments (Targets & Variablen)",
    subtitle="Section 5 &middot; Implementing CI-CD &middot; Quelle: Kurs 8, Modul 03",
    body_html=body,
    build_name="08_02_multi_environment",
)
print("OK")
