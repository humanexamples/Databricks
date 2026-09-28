# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Ein Job, der nur manuell gestartet wird, ist für den Produktivbetrieb wenig hilfreich. Damit Datenpipelines zuverlässig und ohne menschliches Zutun laufen, bietet Lakeflow Jobs ein reichhaltiges Set an <strong>Trigger-Typen</strong> sowie Mechanismen, um Tasks zur Laufzeit mit <strong>Parametern</strong> zu versorgen. Dieses Dokument behandelt beides: die Automatisierung der Ausführung und die Konfiguration wiederverwendbarer, flexibler Tasks.</p>

<h2>1. Parameter, Task Values und dynamische Referenzen</h2>
<p>Lakeflow Jobs unterscheidet zwischen mehreren Ebenen der Parametrisierung:</p>
<ul>
<li><strong>Job-Parameter</strong> &ndash; auf Job-Ebene definierte Schlüssel-Wert-Paare, die automatisch an alle Tasks weitergereicht werden. Sie eignen sich, um sinnvolle Standardwerte (z.&nbsp;B. Katalog- oder Schemanamen) zentral festzulegen.</li>
<li><strong>Task-Parameter</strong> &ndash; auf einzelne Tasks beschränkte Schlüssel-Wert-Paare für feingranulare Steuerung. Wichtig: Existiert ein Schlüssel sowohl auf Job- als auch auf Task-Ebene, gewinnt der <strong>Job-Parameter</strong>.</li>
<li><strong>Task Values</strong> &ndash; werden zur Laufzeit berechnet und dienen dem Datenaustausch zwischen Tasks, z.&nbsp;B. um eine Datensatzanzahl oder ein Prüfergebnis an einen nachgelagerten Task weiterzugeben.</li>
<li><strong>Dynamische Wertreferenzen</strong> (<code>{{{{ }}}}</code>-Syntax) &ndash; erlauben den Zugriff auf Laufzeitkontext wie <code>{{{{job.run_id}}}}</code>, <code>{{{{task.name}}}}</code> oder auf Ergebnisse anderer Tasks wie <code>{{{{tasks.data-validation.values.record_count}}}}</code>.</li>
</ul>
<p>In einem Notebook-Task lassen sich Parameter über <code>dbutils.widgets.get(...)</code> abrufen, während Task Values explizit gesetzt und gelesen werden:</p>

{code('python', '''# Einen Task-Parameter im Notebook auslesen
my_catalog = dbutils.widgets.get("catalog")
my_schema  = dbutils.widgets.get("schema")

# Einen berechneten Wert fuer nachgelagerte Tasks bereitstellen
duplicate_exists = df.count() > df.dropDuplicates().count()
dbutils.jobs.taskValues.set(key="has_duplicates", value=duplicate_exists)

# Diesen Wert in einem anderen (downstream) Task auslesen
upstream_flag = dbutils.jobs.taskValues.get(
    taskKey="customers_sales_summary",
    key="has_duplicates"
)''')}

<h2>2. Trigger-Typen im Überblick</h2>
<p>Ein Trigger ist im Kern eine Regel, die automatisch einen Job-Lauf auslöst. Lakeflow Jobs unterstützt vier Kategorien:</p>
<table>
<tr><th>Trigger</th><th>Funktionsweise</th><th>Typischer Einsatzzweck</th></tr>
<tr><td><strong>Scheduled (Zeitgesteuert)</strong></td><td>Einfache UI-Schedules (stündlich/täglich/wöchentlich) oder volle Cron-Syntax für komplexe Zeitpläne</td><td>Tägliche ETL-Läufe, wöchentliche Reports, monatliche Aggregationen</td></tr>
<tr><td><strong>File Arrival</strong></td><td>Überwacht einen Cloud-Speicherort bzw. ein Unity-Catalog-Volume auf neue Dateien</td><td>Partnerdaten-Feeds, unregelmäßig eintreffende Dateien</td></tr>
<tr><td><strong>Table Update</strong></td><td>Löst aus, wenn sich eine oder mehrere überwachte Quelltabellen ändern (bis zu 10 Tabellen, &bdquo;any&ldquo; oder &bdquo;all&ldquo;)</td><td>Ereignisgesteuerte Weiterverarbeitung ohne festen Zeitplan</td></tr>
<tr><td><strong>Continuous</strong></td><td>Startet automatisch einen neuen Lauf, sobald der vorherige beendet ist</td><td>Dauerhaft laufende Streaming-Workloads</td></tr>
</table>
<p>Bei der <strong>Table-Update-Trigger</strong>-Konfiguration lassen sich zusätzlich zwei Feinsteuerungen setzen: <em>Minimum time between triggers</em> verhindert zu häufiges Auslösen bei schnell aufeinanderfolgenden Tabellenänderungen, und <em>Wait after last change</em> verzögert den Start, bis seit der letzten Änderung eine bestimmte Zeit vergangen ist &ndash; nützlich, wenn Daten in mehreren Batches eintreffen und erst nach vollständigem Eintreffen verarbeitet werden sollen.</p>

<h2>3. File-Arrival-Trigger in der Praxis</h2>
<p>Ein File-Arrival-Trigger wird auf ein Unity-Catalog-Volume oder einen Cloud-Speicherpfad gerichtet. Sobald eine neue Datei erscheint, startet der Job automatisch &ndash; standardmäßig prüft Databricks etwa einmal pro Minute auf Änderungen. Wichtig: Nur wirklich <em>neue</em> Dateien lösen einen Lauf aus; das Überschreiben einer Datei mit demselben Namen tut dies nicht. Zudem gilt eine Obergrenze von 1000 Dateien pro Trigger-Auslösung.</p>

{code('sql', '''-- Volume anlegen, das als Ueberwachungsort fuer den File-Arrival-Trigger dient
CREATE VOLUME IF NOT EXISTS trigger_storage_location;

-- Verfuegbare Volumes im aktuellen Schema anzeigen
SHOW VOLUMES;''')}

<figure class="img">
<img src="assets/02/job_schedules_triggers_overview.png">
<figcaption>Lakeflow Jobs unterstützt zeitgesteuerte, ereignisgesteuerte und kontinuierliche Trigger.</figcaption>
</figure>

<h2>4. Benachrichtigungen und Retry-Policies</h2>
<p>Sowohl auf Job- als auch auf Task-Ebene lassen sich <strong>Benachrichtigungen</strong> konfigurieren &ndash; per E-Mail, Microsoft Teams, PagerDuty, Slack oder Webhook. Job-Level-Benachrichtigungen eignen sich für Stakeholder, die nur am Gesamtergebnis interessiert sind; Task-Level-Benachrichtigungen erlauben granularere Alarmierung, etwa sofortige Meldungen bei fehlgeschlagenen Datenqualitätsprüfungen. Neben Erfolg/Fehlschlag lassen sich auch Schwellenwerte für <em>Late Jobs</em> (Laufzeitüberschreitung) oder <em>Streaming Backlog</em> konfigurieren.</p>
<p>Eine durchdachte <strong>Retry-Policy</strong> berücksichtigt die Art des Fehlers (z.&nbsp;B. transiente Netzwerkprobleme vs. Datenqualitätsprobleme), die Auswirkung wiederholter Ausführung auf Cluster-Ressourcen sowie geschäftliche SLA-Vorgaben, die das Zeitfenster für Wiederholungen begrenzen können.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Neben den vier hier vorgestellten Trigger-Typen weist die aktuelle Dokumentation darauf hin, dass für optimale Performance und Skalierbarkeit &bdquo;File Events&ldquo; auf dem externen Speicherort aktiviert werden sollten, auf dem die überwachten Tabellen liegen &ndash; dies verbessert sowohl Table-Update-Trigger als auch den zugrunde liegenden Auto Loader. Die End-to-End-Latenz liegt bei Table-Update- und File-Arrival-Triggern typischerweise bei ein bis zwei Minuten zzgl. der Zeit für Cluster-/Compute-Start.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/jobs/trigger-table-update">Trigger jobs when source tables are updated &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 4 - Working with Lakeflow Jobs\02 Jobs erstellen, planen und automatisieren.pdf",
    title="Jobs erstellen, planen und automatisieren (Scheduling & Trigger)",
    subtitle="Section 4 &middot; Working with Lakeflow Jobs &middot; Quelle: Kurs 2, Kapitel 6&ndash;7",
    body_html=body,
    build_name="02_02_scheduling_trigger",
)
print("OK")
