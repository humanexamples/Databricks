# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Auch der am besten gestaltete Workflow wird irgendwann einmal fehlschlagen &ndash; sei es wegen eines Konfigurationsfehlers, einer defekten Quelldatei oder eines vorübergehenden Ressourcenengpasses. Entscheidend ist nicht, Fehler vollständig zu vermeiden, sondern effizient auf sie reagieren zu können. Lakeflow Jobs bietet dafür die Funktion <strong>Repair and Rerun</strong> sowie umfangreiche Monitoring-Werkzeuge über System-Tabellen und die Spark-UI.</p>

<h2>1. Repair and Rerun: gezielte Fehlerbehebung</h2>
<p>Statt bei einem Fehlschlag den gesamten Job von vorne zu starten, erlaubt <strong>Repair Run</strong> die selektive Wiederholung: Nur die fehlgeschlagenen Tasks &ndash; und alle davon abhängigen Tasks &ndash; werden erneut ausgeführt. Das spart erheblich Zeit und Rechenkosten, besonders bei umfangreichen, mehrstufigen Workflows. Zusätzlich lassen sich beim Reparaturlauf <strong>Parameter überschreiben</strong>, sodass sich typische Fehlerursachen direkt beheben lassen:</p>
<ul>
<li><strong>Konfigurationsfehler</strong> &ndash; falsche Parameterwerte korrigieren</li>
<li><strong>Ressourcenengpässe</strong> &ndash; mehr Arbeitsspeicher oder Compute für den betroffenen Task bereitstellen</li>
<li><strong>Code-Fehler</strong> &ndash; nach einer Korrektur im Notebook nur die betroffenen Tasks neu laufen lassen</li>
<li><strong>Datenqualitätsprobleme</strong> &ndash; Verarbeitungslogik anpassen und gezielt erneut ausführen</li>
</ul>
<p>Wichtig zu verstehen: Das Reparieren eines Laufs behebt nicht automatisch die <em>Job-Definition</em> selbst. Wurde beispielsweise ein falscher Parameterwert übergeben und im Reparaturlauf manuell korrigiert, muss diese Korrektur zusätzlich dauerhaft in der Job-Konfiguration nachgezogen werden, damit künftige reguläre Läufe nicht erneut fehlschlagen.</p>

<h2>2. Repair and Rerun in der Praxis</h2>
<p>Ein typischer Ablauf: Ein Task schlägt fehl, weil im Code eine falsche Spaltenbezeichnung referenziert wird. Die Fehlerbehebung erfolgt in wenigen Schritten:</p>
<ol>
<li>Im fehlgeschlagenen Lauf auf <strong>Repair run</strong> klicken.</li>
<li>Den Fehler im zugrunde liegenden Notebook identifizieren und korrigieren (z.&nbsp;B. falschen Spaltennamen anpassen).</li>
<li>Zur Job-Übersicht zurückkehren und erneut <strong>Repair run</strong> wählen &ndash; Databricks markiert automatisch den fehlgeschlagenen Task sowie alle abhängigen Tasks zur Wiederholung.</li>
<li>Optional weitere Tasks für die Wiederholung an- oder abwählen.</li>
</ol>
<p>Die Farbkodierung im DAG hilft bei der schnellen Einschätzung eines Laufs:</p>
<table>
<tr><th>Farbe</th><th>Bedeutung</th></tr>
<tr><td>Grau</td><td>Task noch nicht gestartet</td></tr>
<tr><td>Grün, gestreift</td><td>Task läuft aktuell</td></tr>
<tr><td>Grün, durchgehend</td><td>Task erfolgreich abgeschlossen</td></tr>
<tr><td>Rot, dunkel</td><td>Task fehlgeschlagen</td></tr>
<tr><td>Rot, hell</td><td>Task übersprungen, da ein vorgelagerter Task fehlgeschlagen ist</td></tr>
</table>

<figure class="img">
<img src="assets/02/repair_rerun_workflow.png">
<figcaption>Repair and Rerun führt gezielt nur fehlgeschlagene Tasks und deren Abhängigkeiten erneut aus.</figcaption>
</figure>

<h2>3. Monitoring mit system.lakeflow</h2>
<p>Für tiefergehende Analysen über einzelne Läufe hinaus bietet Databricks den System-Katalog <strong>system.lakeflow</strong>. Er protokolliert automatisch sämtliche Job-Aktivität über alle Workspaces einer Region hinweg und stellt unter anderem folgende Tabellen bereit:</p>
<ul>
<li><code>jobs</code> &ndash; grundlegende Job-Metadaten und Konfiguration</li>
<li><code>job_tasks</code> &ndash; Task-Definitionen und -Konfigurationen</li>
<li><code>job_run_timeline</code> &ndash; vollständige Ausführungshistorie jedes Job-Laufs</li>
<li><code>job_task_run_timeline</code> &ndash; detaillierte Ausführungshistorie einzelner Tasks</li>
<li><code>pipelines</code> &ndash; Informationen zu Lakeflow-Declarative-Pipelines-Läufen</li>
</ul>
<p>Die Timeline-Tabellen zerlegen lang laufende Jobs mittels <code>period_start_time</code> und <code>period_end_time</code> in Stundenabschnitte, was präzise Laufzeitanalysen, Nebenläufigkeits-Tracking und SLA-Messungen ermöglicht &ndash; auch für komplexe, lange laufende Workflows. Damit lassen sich Kostenanalysen, Performance-Trends und Ressourcenauslastung systematisch auswerten:</p>

{code('sql', '''-- Verfuegbare Tabellen im system.lakeflow-Schema anzeigen
SHOW TABLES IN system.lakeflow;

-- Jobs mit ihrer Task-Ausfuehrungshistorie verknuepfen
SELECT jobs.workspace_id,
       jobs.name AS job_name,
       jobs.job_id,
       timeline.run_id,
       timeline.period_start_time,
       timeline.period_end_time,
       timeline.task_key,
       timeline.result_state
FROM system.lakeflow.jobs AS jobs
INNER JOIN system.lakeflow.job_task_run_timeline AS timeline
  ON jobs.job_id = timeline.job_id
WHERE lower(jobs.name) LIKE 'demo_12_retail_job_%'
ORDER BY timeline.period_start_time;''')}

<h2>4. Performance-Analyse mit der Spark-UI</h2>
<p>Für die Detailanalyse einzelner Task-Läufe liefert die <strong>Spark-UI</strong> zusätzliche Einblicke: Die Ausführungs-Timeline zeigt Task-Dauer, Überlappungen und Engpässe auf einen Blick; ein Klick auf einzelne Stages offenbart Ausführungspläne, Optimierungsentscheidungen, Dateizugriffsmuster und Partitionsinformationen. Typische Warnsignale sind eine hohe <em>Planning Time</em> (deutet auf Optimierungsbedarf bei Partitionierung oder Metadaten hin) und eine hohe <em>Execution Time</em> (deutet auf Join-Optimierung, Broadcast-Strategien oder Skew-Behandlung hin).</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Die aktuelle Dokumentation unterscheidet klar zwischen &bdquo;Restart&ldquo; (kompletter Neustart des gesamten Jobs) und &bdquo;Repair Run&ldquo; (gezielte Wiederholung nur der fehlgeschlagenen und abhängigen Tasks). Wichtige Einschränkung: Repair Run ist nur für Jobs mit mindestens zwei Tasks verfügbar; bei einem einzelnen Task muss der Job komplett über &bdquo;Run now&ldquo; neu gestartet werden. Zudem macht Lakeflow Jobs Tasks nicht automatisch idempotent &ndash; hat ein Task vor seinem Fehlschlag bereits einen Teil seiner Ausgabe geschrieben, kann eine Wiederholung zu doppelten Daten führen. Dies sollte bei der Pipeline-Gestaltung (z.&nbsp;B. durch idempotente MERGE-Logik) berücksichtigt werden.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/jobs/repair-job-failures">Troubleshoot and repair job failures &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 4 - Working with Lakeflow Jobs\04 Monitoring, Fehlerbehandlung und Repair.pdf",
    title="Monitoring, Fehlerbehandlung und Repair",
    subtitle="Section 4 &middot; Working with Lakeflow Jobs &middot; Quelle: Kurs 2, Kapitel 11&ndash;12",
    body_html=body,
    build_name="02_04_monitoring_repair",
)
print("OK")
