# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Alle bisherigen Beispiele in diesem Themenordner wurden aus einem Databricks-Notebook heraus per <code>%sh</code>-Zelle bedient &ndash; praktisch für Schulungszwecke, aber nicht der Arbeitsweise, die die meisten Data-Engineering-Teams im Alltag nutzen. In der Praxis wird der Code eines Bundles lokal in einer richtigen Entwicklungsumgebung geschrieben, versioniert und von dort aus deployt. Die <strong>Databricks-Erweiterung für Visual Studio Code</strong> bringt dafür Syntaxhervorhebung, Schema-Validierung, Autovervollständigung für <code>databricks.yml</code> sowie Deploy- und Run-Buttons direkt in den Editor &ndash; ohne dass man dafür ständig zwischen Browser-Tabs und Terminal wechseln muss.</p>

<h2>1. Authentifizierung: Workspace-URL und Personal Access Token</h2>
<p>Bevor VS Code mit einem Databricks-Workspace kommunizieren kann, benötigt die Erweiterung zwei Angaben: die Workspace-URL und einen gültigen Berechtigungsnachweis. Für den Einstieg wird meist ein <strong>Personal Access Token (PAT)</strong> verwendet. Die Workspace-URL lässt sich z.&nbsp;B. direkt aus einer laufenden Spark-Session auslesen:</p>

{code('python', '''lab_databricks_url = f\'{spark.conf.get("spark.databricks.workspaceUrl")}/\'
print(lab_databricks_url)''')}

<p>Ein PAT wird in der Databricks-Oberfläche über <strong>Einstellungen &rarr; Developer &rarr; Access tokens &rarr; Manage &rarr; Generate new token</strong> erzeugt. Wichtig dabei: Der Token wird nur einmal im Klartext angezeigt &ndash; wird er nicht sofort kopiert und sicher hinterlegt (z.&nbsp;B. in einem Passwort-Manager, keinesfalls im Klartext ins Repository committen), muss ein neuer erzeugt werden. Für den produktiven Einsatz gilt: PATs sollten möglichst eng auf die benötigten API-Bereiche eingeschränkt und regelmäßig rotiert werden; das Scope &bdquo;alle APIs&ldquo; ist ausschließlich für Trainings- bzw. Testzwecke gedacht.</p>
<p>Sobald Workspace-URL und PAT vorliegen, öffnet man in VS Code die Befehlspalette und authentifiziert die Erweiterung gegen den Workspace. Alternativ &ndash; und für Teams empfehlenswert &ndash; lässt sich die CLI auch mit einem bestehenden <strong>Konfigurationsprofil</strong> (<code>~/.databrickscfg</code>) oder mit OAuth-basiertem Login verbinden, sodass kein Token im Klartext gepflegt werden muss.</p>

<h2>2. Bundles direkt im Editor bearbeiten</h2>
<p>Sobald ein Ordner mit einer <code>databricks.yml</code> in VS Code geöffnet ist, erkennt die Erweiterung das Projekt automatisch als Bundle. Beim Bearbeiten der YAML-Dateien bietet sie:</p>
<ul>
<li><strong>Schema-Validierung in Echtzeit</strong> &ndash; ungültige Schlüssel oder falsch platzierte Zuordnungen werden direkt im Editor als Fehler markiert, ohne dass man erst <code>databricks bundle validate</code> über die CLI ausführen muss.</li>
<li><strong>Autovervollständigung</strong> für gültige Konfigurationsschlüssel (<code>bundle</code>, <code>resources</code>, <code>targets</code>, <code>variables</code> &hellip;) sowie für Referenzen auf andere Ressourcen im selben Bundle.</li>
<li><strong>Autovervollständigung für Databricks-Globals</strong> in Python-Notebooks/-Skripten (z.&nbsp;B. <code>spark</code>, <code>dbutils</code>): Über die Befehlspalette lässt sich mit &bdquo;Databricks: Configure autocomplete for Databricks globals&ldquo; automatisch PySpark installieren und eine passende <code>__builtins__.pyi</code>-Datei fürs Projekt anlegen.</li>
</ul>

<h2>3. Der Bundle Resource Explorer: Deploy und Run per Klick</h2>
<p>Zentrales Werkzeug der Erweiterung ist der <strong>Bundle Resource Explorer</strong>, eine eigene Seitenleiste in VS Code. Er liest die in <code>databricks.yml</code> (und den über <code>include</code> eingebundenen Dateien) definierten Ressourcen aus und stellt sie als Baumstruktur dar &ndash; Jobs, Pipelines und weitere Objekte lassen sich darüber:</p>
<ul>
<li>mit einem Klick deployen, ohne den Terminalbefehl manuell zu tippen,</li>
<li>direkt aus dem Editor heraus starten und deren Run-Status verfolgen,</li>
<li>bei Pipelines partiell validieren und aktualisieren, inklusive Einsicht in Pipeline-Ereignisse und Diagnosen,</li>
<li>mit einem Klick im tatsächlichen, remote Databricks-Workspace öffnen, um dort z.&nbsp;B. den Job-Verlauf einzusehen.</li>
</ul>
<p>Alle CLI-Befehle, die in den vorherigen Kapiteln über <code>%sh</code>-Zellen ausgeführt wurden, funktionieren selbstverständlich unverändert auch im integrierten Terminal von VS Code &ndash; der Bundle Resource Explorer ist lediglich eine grafische Abkürzung für dieselben Operationen:</p>

{code('bash', '''# Diese Befehle funktionieren identisch im VS-Code-Terminal wie zuvor im Notebook
databricks bundle validate -t development
databricks bundle deploy -t development
databricks bundle run -t development demo03_job
databricks bundle destroy --auto-approve''')}

<h2>4. Warum lokal statt im Notebook entwickeln?</h2>
<p>Der Wechsel von notebookbasierter Bundle-Arbeit zu einem lokalen Editor bringt vor allem für größere Projekte handfeste Vorteile:</p>
<table>
<tr><th>Aspekt</th><th>Im Databricks-Notebook (%sh)</th><th>In VS Code mit Databricks-Erweiterung</th></tr>
<tr><td>YAML-Fehler erkennen</td><td>erst beim Ausführen von <code>bundle validate</code></td><td>sofort während des Tippens (Schema-Validierung)</td></tr>
<tr><td>Versionskontrolle</td><td>Umweg über Databricks Git Folders</td><td>natives lokales Git, gewohnter PR-Workflow</td></tr>
<tr><td>Deploy/Run auslösen</td><td>CLI-Befehl in Notebookzelle</td><td>Klick im Bundle Resource Explorer oder Terminalbefehl</td></tr>
<tr><td>Code-Vervollständigung</td><td>Notebook-eigene Autovervollständigung</td><td>volle IDE-Funktionalität inkl. Databricks-Globals</td></tr>
<tr><td>Lokale Tests</td><td>eingeschränkt möglich</td><td>pytest & Debugger direkt im Editor nutzbar</td></tr>
</table>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Die Databricks-Erweiterung für Visual Studio Code ermöglicht es laut Dokumentation, Declarative Automation Bundles direkt zu definieren, zu deployen und auszuführen, um damit CI/CD-Best-Practices auf Lakeflow Jobs, Lakeflow Spark Declarative Pipelines und MLOps Stacks anzuwenden. Der <strong>Bundle Resource Explorer</strong> nutzt dabei die Ressourcendefinitionen aus der Bundle-Konfiguration, um Ressourcen anzuzeigen, mit einem Klick in den Workspace zu deployen und von dort direkt zu den entsprechenden Objekten im Workspace zu navigieren. Für die Erst-Einrichtung der Autovervollständigung für Databricks-spezifische Python-Objekte (<code>spark</code>, <code>dbutils</code> &hellip;) steht der Befehlspalette-Eintrag &bdquo;Databricks: Configure autocomplete for Databricks globals&ldquo; zur Verfügung.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/dev-tools/vscode-ext/bundles">Declarative Automation Bundles extension features &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 5 - Implementing CI-CD\09 Asset Bundles in VS Code.pdf",
    title="Asset Bundles in VS Code",
    subtitle="Section 5 &middot; Implementing CI-CD &middot; Quelle: Kurs 8, Modul 08 (Bonus)",
    body_html=body,
    build_name="08_04_vscode",
)
print("OK")
