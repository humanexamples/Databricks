# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Sobald ein Job, eine Pipeline oder ein Notebook in Databricks über die Oberfläche entwickelt und getestet wurde, stellt sich die Frage, wie diese Ressourcen zuverlässig und wiederholbar in andere Umgebungen &ndash; etwa eine Test- oder Produktionsumgebung &ndash; gebracht werden können. Manuelles Nachbauen per Klick ist fehleranfällig und lässt sich nicht versionieren. Genau hier setzen <strong>Declarative Automation Bundles</strong> an, die in der Databricks-Dokumentation und in älteren Kursmaterialien häufig noch unter ihrem ursprünglichen Namen <strong>Databricks Asset Bundles (DABs)</strong> zu finden sind &ndash; beide Begriffe bezeichnen dasselbe Konzept. Ein Bundle beschreibt Jobs, Pipelines und weitere Ressourcen als Code (YAML) und macht Databricks-Projekte damit zu klassischen Software-Projekten, die sich versionieren, überprüfen (Code-Review) und automatisiert deployen lassen &ndash; die Grundlage für CI/CD in der Data-Engineering-Welt.</p>

<h2>1. Die Datei databricks.yml als Ausgangspunkt</h2>
<p>Jedes Bundle benötigt genau eine Konfigurationsdatei mit dem festen Namen <code>databricks.yml</code> im Wurzelverzeichnis des Projekts. Diese Datei muss mindestens die oberste Zuordnung <code>bundle</code> mit einem Namen enthalten. Für ein neues, noch leeres Bundle sieht die Grundstruktur so aus:</p>

{code('yaml', '''bundle:                   # Required
  name: demo01_bundle     # Required

resources:
  jobs:
    # <-- hier werden Job- und Pipeline-Definitionen ergänzt

targets:
  development:
    # The default target uses \'mode: development\' to create a development copy.
    mode: development
    default: true
    workspace:
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}''')}

<p>Die drei zentralen Top-Level-Zuordnungen sind:</p>
<ul>
<li><strong><code>bundle</code></strong> &ndash; der programmatische (logische) Name des Bundles. Er taucht später im Workspace-Pfad wieder auf, unter dem alle deployten Dateien liegen.</li>
<li><strong><code>resources</code></strong> &ndash; die eigentlichen Databricks-Objekte, die das Bundle verwaltet: Jobs, Lakeflow-Declarative-Pipelines, Modelle usw.</li>
<li><strong><code>targets</code></strong> &ndash; eine oder mehrere Zielumgebungen, in denen das Bundle deployt werden kann. Jedes Target ist eine eigenständige Kombination aus Workspace-Einstellungen, Ressourcen-Overrides und (optional) einem Deployment-Modus.</li>
</ul>
<p>Der <code>mode: development</code>-Modus in einem Target sorgt dafür, dass alle nicht als Datei/Notebook deployten Ressourcen automatisch mit dem Präfix <code>[dev &lt;benutzername&gt;]</code> versehen und mit einem <code>dev</code>-Tag markiert werden &ndash; so lassen sich Entwicklungs-Deployments in der Oberfläche sofort von produktiven Ressourcen unterscheiden. Nur ein Target darf <code>default: true</code> gesetzt haben; das verhindert, dass ein CLI-Aufruf ohne explizites Ziel versehentlich in der Produktion landet.</p>

<h2>2. Von einem bestehenden Job zur YAML-Konfiguration</h2>
<p>Ein gängiger Startpunkt in der Praxis: Man baut den Job zunächst gewohnt über die Oberfläche (Jobs &amp; Pipelines), testet ihn, und lässt sich anschließend die YAML-Definition automatisch generieren. Über das Kontextmenü eines Jobs (die drei Punkte neben &bdquo;Run now&ldquo;) steht die Funktion <strong>View as code</strong> zur Verfügung, die die Job-Konfiguration wahlweise als YAML, Python (SDK oder Bundle-Format) oder JSON ausgibt. Die YAML-Variante lässt sich direkt in die <code>resources</code>-Zuordnung von <code>databricks.yml</code> einfügen. Nach dem Einfügen sind meist noch zwei Anpassungen nötig: Notebook-Pfade auf relative Pfade mit Dateiendung (z.&nbsp;B. <code>./src/create_bronze_table.ipynb</code>) umstellen und dem Job-Schlüssel (dem Bezeichner unter <code>jobs:</code>) einen sprechenden, stabilen Namen geben. So sieht die fertige Konfiguration für einen einfachen zweistufigen Job aus einem der Kursbeispiele aus:</p>

{code('yaml', '''resources:
  jobs:
    demo1_simple_dab_labuser15933383_1784705641:
      name: demo1_simple_dab_labuser15933383_1784705641
      tasks:
        - task_key: create_bronze_table
          notebook_task:
            notebook_path: ./src/create_bronze_table.ipynb
            source: WORKSPACE
        - task_key: create_silver_table
          depends_on:
            - task_key: create_bronze_table
          notebook_task:
            notebook_path: ./src/create_silver_table.ipynb
            source: WORKSPACE
      queue:
        enabled: true
      parameters:
        - name: display_target
          default: development_updating_the_value_test
        - name: catalog_name
          default: labuser15933383_1784705641_1_dev''')}

<p>Die beiden Notebook-Tasks bauen aufeinander auf (<code>depends_on</code>) und erhalten über <code>parameters</code> zur Laufzeit den Zielkatalog sowie einen Anzeigetext mit &ndash; klassische Job-Parameter, wie sie auch außerhalb von Bundles verwendet werden. Die zugehörigen Notebooks lesen diese Werte über <code>dbutils.widgets.get(...)</code> aus, zum Beispiel im Bronze-Layer-Notebook:</p>

{code('python', '''# Databricks notebook source
my_catalog = dbutils.widgets.get(\'catalog_name\')
target = dbutils.widgets.get(\'display_target\')

set_default_catalog = spark.sql(f\'USE CATALOG {my_catalog}\')

# COMMAND ----------

spark.sql(f\'\'\'
CREATE OR REPLACE TABLE {my_catalog}.default.health_bronze_demo_01 AS
SELECT *, _metadata.file_name as file_name, current_timestamp() as load_date
FROM read_files(\'/Volumes/{my_catalog}/default/health/\', format => \'csv\', header => true)
\'\'\')''')}

<figure class="img">
<img src="assets/08/simple-dab-job-run.png">
<figcaption>Ein per Bundle deployter und über die CLI gestarteter Job in der Databricks-Oberfläche &ndash; der Hinweis &bdquo;Connected to Declarative Automation Bundles&ldquo; zeigt, dass der Job aus einem Bundle stammt und nicht mehr manuell über die UI verändert werden sollte.</figcaption>
</figure>

<h2>3. Der CLI-Lifecycle eines Bundles</h2>
<p>Nachdem die CLI installiert und authentifiziert ist (Workspace-URL und Zugangsdaten, z.&nbsp;B. per PAT oder OAuth), wird jedes Bundle-Kommando aus dem Verzeichnis heraus ausgeführt, in dem die <code>databricks.yml</code> liegt &ndash; die CLI nutzt diese Datei automatisch für Authentifizierungsdetails wie Host und Profil. Der typische Lebenszyklus eines Bundles besteht aus vier Schritten:</p>

{code('bash', '''# Version der installierten Databricks CLI prüfen
databricks -v

# Die databricks.yml auf syntaktische und semantische Korrektheit pruefen
databricks bundle validate

# Bundle in die Zielumgebung "development" deployen
databricks bundle deploy -t development

# Den in der YAML definierten Job ausfuehren (Job-Schluessel aus "resources.jobs")
databricks bundle run -t development demo01_simple_dab

# Alle zuvor deployten Ressourcen dieses Bundles endgueltig loeschen
databricks bundle destroy --auto-approve''')}

<table>
<tr><th>Befehl</th><th>Zweck</th></tr>
<tr><td><code>databricks bundle validate</code></td><td>Prüft die Konfiguration gegen das Objektschema, ohne etwas zu deployen &ndash; findet z.&nbsp;B. fehlende Notebook-Pfade oder falsche Einrückungen.</td></tr>
<tr><td><code>databricks bundle deploy -t &lt;target&gt;</code></td><td>Lädt Dateien hoch und legt bzw. aktualisiert die in <code>resources</code> definierten Jobs/Pipelines im angegebenen Ziel-Workspace an.</td></tr>
<tr><td><code>databricks bundle run -t &lt;target&gt; &lt;job-key&gt;</code></td><td>Startet einen deployten Job oder eine Pipeline über ihren YAML-Schlüssel (nicht den Anzeigenamen).</td></tr>
<tr><td><code>databricks bundle destroy [--auto-approve]</code></td><td>Entfernt alle zuvor deployten Ressourcen und Artefakte des Bundles unwiderruflich; ohne die Option wird vorher eine Bestätigung abgefragt.</td></tr>
</table>

<p>Wird eine Änderung an der <code>databricks.yml</code> vorgenommen &ndash; etwa ein neuer Standardwert für einen Job-Parameter &ndash; muss das Bundle erneut deployt werden, damit die Änderung im Workspace wirksam wird; ein einfaches Speichern der Datei genügt nicht. Wichtig ist außerdem der Unterschied zwischen einem <strong>source-linked Deployment</strong> (typisch, wenn direkt aus dem Workspace heraus deployt wird: Der deployte Job verweist auf die bestehenden Workspace-Dateien, es wird keine Kopie angelegt) und einem klassischen Deployment von einer lokalen Maschine oder aus einer CI/CD-Pipeline aus, bei dem die Dateien tatsächlich in den Zielpfad kopiert werden.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Declarative Automation Bundles (früher Databricks Asset Bundles) sind Databricks' empfohlenes Werkzeug, um Software-Engineering-Best-Practices &ndash; Versionskontrolle, Code-Review, Tests und CI/CD &ndash; auf Data- und KI-Projekte anzuwenden. Der übliche Ablauf ist, ein Bundle zunächst in den persönlichen Dev-Workspace eines Entwicklers zu deployen; erst nach erfolgreichem Testen wird dieselbe, unveränderte Bundle-Definition gegen Staging- und anschließend Produktions-Ziele deployt. Die vollständige Liste aller <code>databricks bundle</code>-Unterbefehle sowie sämtlicher gültigen Schlüssel der <code>databricks.yml</code> ist in der Referenzdokumentation gepflegt.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/dev-tools/bundles/reference">Configuration reference &ndash; Databricks-Dokumentation</a> und <a href="https://docs.databricks.com/aws/en/dev-tools/cli/bundle-commands">bundle command group &ndash; Databricks CLI-Referenz</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 5 - Implementing CI-CD\06 Grundlagen - databricks.yml und CLI-Lifecycle.pdf",
    title="Grundlagen: databricks.yml & CLI-Lifecycle",
    subtitle="Section 5 &middot; Implementing CI-CD &middot; Quelle: Kurs 8, Modul 01",
    body_html=body,
    build_name="08_01_grundlagen_databricks_yml",
)
print("OK")
