# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Nicht jeder Workflow lässt sich als starre Abfolge von Tasks abbilden. Manchmal soll ein Task nur laufen, wenn ein bestimmtes Ergebnis vorliegt; manchmal muss dieselbe Logik auf eine unbekannte Anzahl von Eingabewerten angewendet werden. Für solche Fälle bietet Lakeflow Jobs drei fortgeschrittene Task-Muster: <strong>Run-if-Abhängigkeiten</strong>, <strong>If/Else-Tasks</strong> und <strong>For-Each-Tasks</strong>. Zusammen erlauben sie dynamische Workflows, die auf Laufzeitbedingungen reagieren, statt starr vorgegeben zu sein.</p>

<h2>1. Run-if-Abhängigkeiten (Run If Conditions)</h2>
<p>Standardmäßig wartet ein Task, bis alle vorgelagerten Tasks erfolgreich abgeschlossen sind (&bdquo;All succeeded&ldquo;). Für robustere Workflows lässt sich diese Bedingung jedoch feiner steuern:</p>
<ul>
<li><strong>All succeeded</strong> &ndash; alle Vorgänger-Tasks müssen erfolgreich sein (Standardverhalten).</li>
<li><strong>At least one succeeded</strong> &ndash; sinnvoll bei redundanten Datenquellen oder Verarbeitungspfaden; der Workflow läuft weiter, sobald mindestens ein Vorgänger erfolgreich war.</li>
<li><strong>None failed</strong> &ndash; erlaubt Ausführung auch dann, wenn Vorgänger-Tasks übersprungen wurden, solange keiner davon explizit fehlgeschlagen ist.</li>
<li><strong>All done</strong> &ndash; läuft, sobald alle Vorgänger-Tasks abgeschlossen sind, unabhängig von deren Ergebnis.</li>
<li><strong>At least one failed</strong> &ndash; läuft, sobald mindestens ein Vorgänger fehlgeschlagen ist &ndash; nützlich etwa für Aufräum- oder Benachrichtigungs-Tasks.</li>
<li><strong>All failed</strong> &ndash; läuft nur, wenn alle Vorgänger-Tasks fehlgeschlagen sind.</li>
</ul>
<p>Das sind die sechs festen, in der UI/API vorgegebenen Optionen &ndash; eine frei definierbare, benutzerdefinierte Bedingung gibt es nicht.</p>
<p>Diese Bedingungen erhöhen die Ausfallsicherheit eines Workflows deutlich: Ist ein Task etwa so konfiguriert, dass er läuft, sobald mindestens einer von zwei Vorgängern erfolgreich war, kann er trotzdem starten, wenn einer der beiden Vorgänger fehlschlägt. Das verhindert Kaskadenausfälle und spiegelt reale Geschäftsprozesse wider, bei denen es oft mehrere gültige Wege zum Ziel gibt.</p>

<figure class="img">
<img src="assets/02/run_if_dag_visualization.png">
<figcaption>Unterschiedliche Run-if-Bedingungen werden im Job-DAG durch verschiedene Linienstile visualisiert.</figcaption>
</figure>

<h2>2. If/Else-Tasks</h2>
<p>Während Run-if-Bedingungen nur den <em>Status</em> vorheriger Tasks berücksichtigen, ermöglichen <strong>If/Else-Tasks</strong> echte boolesche Logik basierend auf Daten, Parametern oder berechneten Kennzahlen. Unterstützt werden die Operatoren <code>==</code>, <code>!=</code>, <code>&gt;</code>, <code>&gt;=</code>, <code>&lt;</code> und <code>&lt;=</code>. Typische Anwendungsfälle sind Datenqualitäts-Gates (Verzweigung je nach Datensatzanzahl oder Null-Anteil), unterschiedliche Verarbeitungsstrategien je nach Datenvolumen oder umgebungsabhängige Logik (Dev/Stage/Prod). Jeder der beiden Zweige &ndash; <strong>True</strong> und <strong>False</strong> &ndash; kann beliebig viele eigene Folge-Tasks enthalten.</p>
<p>Ein konkretes Beispiel aus der Praxis: Ein vorgelagerter Task prüft eine Tabelle auf doppelte Datensätze und speichert das Ergebnis als Task Value.</p>

{code('python', '''# Im vorgelagerten Task: Duplikate pruefen und Ergebnis als Task Value speichern
df = spark.sql("SELECT * FROM customers_sales_silver")
duplicate_exists = df.count() > df.dropDuplicates().count()
dbutils.jobs.taskValues.set(key="has_duplicates", value=duplicate_exists)''')}

<p>Der If/Else-Task greift anschließend über eine dynamische Wertreferenz auf dieses Ergebnis zu und prüft die Bedingung <code>tasks.customers_sales_summary.values.has_duplicates == true</code>. Ist die Bedingung wahr, läuft der Zweig, der Duplikate bereinigt; andernfalls läuft direkt die Transformation ohne Bereinigungsschritt.</p>

<h2>3. For-Each-Tasks: iterative Verarbeitung</h2>
<p>Ein <strong>For-Each-Task</strong> wiederholt dieselbe Logik für jedes Element einer Eingabeliste &ndash; etwa für jeden Bundesstaat, jede Kundengruppe oder jede zu verarbeitende Datei. Er besteht aus zwei Bausteinen:</p>
<ul>
<li><strong>Der For-Each-Container</strong> &ndash; verwaltet die Iterationslogik, die Eingabeliste (<code>Inputs</code>) und die Nebenläufigkeit (<code>Concurrency</code>), also wie viele Iterationen parallel laufen dürfen.</li>
<li><strong>Der verschachtelte (nested) Task</strong> &ndash; die eigentliche Arbeit, die pro Iteration ausgeführt wird. Er kann ein beliebiger Task-Typ sein (Notebook, SQL, Python) und erhält das jeweilige Listenelement über die Referenz <code>{{{{input}}}}</code>.</li>
</ul>
<p>Downstream-Tasks hängen dabei nur vom gesamten For-Each-Container ab, nicht von jeder einzelnen Iteration &ndash; das hält den DAG übersichtlich, auch wenn im Hintergrund Dutzende Iterationen laufen. Ein Beispiel: Aus einer Tabelle mit Bestelldaten sollen separate Auswertungstabellen für die Bundesstaaten Kalifornien, New York und Virginia erzeugt werden, jeweils mit demselben Notebook, aber unterschiedlichem Parameterwert:</p>

{code('python', '''# Konfiguration des For-Each-Containers (vereinfachtes Beispiel)
# Inputs:      ["CA", "NY", "VA"]
# Nested Task: Notebook "9.5 - For Each: Customer orders State"
# Parameter:   state = {{input}}   -> wird pro Iteration automatisch befuellt''')}

<figure class="img">
<img src="assets/02/for_each_task_loop_diagram.png">
<figcaption>Der For-Each-Task durchläuft eine Eingabeliste und führt für jedes Element den verschachtelten Task aus.</figcaption>
</figure>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks führt diese drei Muster unter dem Oberbegriff &bdquo;Control the flow of tasks&ldquo; zusammen. Run-if-Bedingungen sind dabei <strong>kein eigener Task-Typ</strong>, sondern eine Einstellung an der Abhängigkeit (&bdquo;Depends on&ldquo;) eines Tasks zu seinen Vorgängern; If/Else-Tasks werden dagegen über einen eigenständigen Task-Typ mit boolescher Ausdrucksauswertung konfiguriert. Für For-Each-Tasks unterstützt die aktuelle API mehrere Methoden zur Parameterübergabe an den verschachtelten Task, nicht nur die einfache <code>{{{{input}}}}</code>-Referenz.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/jobs/control-flow">Control the flow of tasks within Lakeflow Jobs &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\Databricks Kurs\Databricks-Dokumentation-DE\Section 4 - Working with Lakeflow Jobs\03 Bedingte und iterative Tasks.pdf",
    title="Bedingte und iterative Tasks (Run If, For Each)",
    subtitle="Section 4 &middot; Working with Lakeflow Jobs &middot; Quelle: Kurs 2, Kapitel 8&ndash;10",
    body_html=body,
    build_name="02_03_bedingte_iterative_tasks",
)
print("OK")
