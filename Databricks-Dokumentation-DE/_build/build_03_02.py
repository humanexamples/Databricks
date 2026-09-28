# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Um eine Lakeflow Declarative Pipeline zu entwickeln, kommt der neue <strong>Lakeflow Pipelines Editor</strong> (Multi-File-Editor) zum Einsatz. Er bündelt Codebearbeitung, Pipeline-Einstellungen, Graph-Visualisierung und Ausführungsdetails in einer einzigen Oberfläche &ndash; statt, wie früher üblich, ein einzelnes großes Notebook zu pflegen, wird das Pipeline-Projekt als Satz einzelner Dateien organisiert.</p>

<h2>1. Der Multi-File-Editor</h2>
<p>Statt eines einzelnen monolithischen Notebooks besteht ein modernes Pipeline-Projekt aus mehreren <code>.sql</code>- oder <code>.py</code>-Dateien (Notebooks werden weiterhin unterstützt, sind aber nicht mehr die empfohlene Struktur). Diese Dateien sind im <strong>Pipeline-Assets-Browser</strong> sichtbar und lassen sich einzeln bearbeiten, während Code in einer Datei problemlos auf Tabellen oder Views verweisen kann, die in einer anderen Datei definiert wurden. Der Editor bietet außerdem:</p>
<ul>
<li>Eine interaktive <strong>Pipeline-Graph</strong>-Ansicht mit Datensatz-Abhängigkeiten und aktuellem Status.</li>
<li><strong>Datenvorschauen</strong> für Streaming Tables und Materialized Views direkt im Editor.</li>
<li><strong>Ausführungseinblicke</strong> (Execution Insights) und die Möglichkeit einer selektiven Ausführung einzelner Teile der Pipeline.</li>
<li>Integrierte <strong>Git</strong>-Anbindung für Versionskontrolle.</li>
</ul>
<p>Ein Pipeline-Projekt lässt sich sowohl über den Dateibrowser (<strong>Create &rarr; ETL Pipeline</strong>) als auch direkt über die zentrale <strong>Jobs &amp; Pipelines</strong>-Ansicht anlegen.</p>

<figure class="img">
<img src="assets/03/lakeflow-pipeline-editor.png">
<figcaption>Der Lakeflow Pipelines Editor vereint Code, Pipeline-Graph und Ausführungsdetails in einer Oberfläche.</figcaption>
</figure>

<h2>2. Typische Ordnerstruktur eines Pipeline-Projekts</h2>
<p>Ein Pipeline-Projekt organisiert seinen Code üblicherweise in mehreren Unterordnern, wobei genau festgelegt werden kann, welche davon tatsächlich zur Pipeline gehören:</p>
<table>
<tr><th>Ordner</th><th>Zweck</th></tr>
<tr><td><code>exploration</code></td><td>Explorative Notebooks &ndash; typischerweise <strong>bewusst von der Pipeline ausgeschlossen</strong></td></tr>
<tr><td><code>orders</code> (Beispiel)</td><td>Enthält den eigentlichen Pipeline-Code, z.&nbsp;B. <code>orders_pipeline.sql</code></td></tr>
<tr><td><code>python_excluded</code> (Beispiel)</td><td>Alternative Implementierung, z.&nbsp;B. in Python statt SQL, ebenfalls ausgeschlossen</td></tr>
</table>
<p>Über einen Rechtsklick auf einen Ordner lässt sich die Option <strong>Include folder as pipeline source code</strong> umschalten &ndash; so bestimmt man präzise, welche Dateien tatsächlich als Pipeline ausgeführt werden und welche (z.&nbsp;B. Explorationen) außen vor bleiben.</p>

<h2>3. Wichtige Pipeline-Einstellungen</h2>
<p>Über das Zahnrad-Symbol im Editor öffnet sich das Einstellungsfenster der Pipeline mit folgenden zentralen Bereichen:</p>
<ul>
<li><strong>Compute</strong> &ndash; Serverless (empfohlen) oder klassische, fest dimensionierte Cluster.</li>
<li><strong>Code Assets</strong> &ndash; das Root-Verzeichnis der Pipeline (&bdquo;Pipeline Root Folder&ldquo;, kann ein Git-Ordner sein) sowie die konkreten Quellcode-Pfade, die tatsächlich ausgeführt werden.</li>
<li><strong>Default location for data assets</strong> &ndash; Standard-Katalog und -Schema, in die neue Tabellen geschrieben werden (kann pro Datensatz überschrieben werden).</li>
<li><strong>Konfigurationsparameter</strong> &ndash; Schlüssel-Wert-Paare, die im Code referenziert werden können, um z.&nbsp;B. Pfade nicht hart zu codieren.</li>
<li><strong>Erweiterte Einstellungen</strong> &ndash; u.&nbsp;a. der <em>Channel</em> (Runtime-Version, meist &bdquo;Current&ldquo;) und optionale Event-Logs für Audit-Zwecke.</li>
</ul>

<h2>4. Eine einfache Pipeline aufbauen: Bronze, Silver, Gold</h2>
<p>Das folgende Beispiel zeigt eine vollständige, dreistufige Pipeline im Medaillon-Muster: eine Streaming Table für die Rohdatenaufnahme, eine weitere Streaming Table für die Bereinigung und eine Materialized View für die Aggregation.</p>

{code('sql', '''-- A. Bronze - Rohdatenaufnahme (Streaming Table)
CREATE OR REFRESH STREAMING TABLE orders_bronze
AS
SELECT *,
       current_timestamp() AS processing_time,
       _metadata.file_name AS source_file
FROM STREAM read_files(
  source_volume_path || '/orders',
  format => 'json'
);

-- B. Silver - Bereinigt & typisiert (Streaming Table)
CREATE OR REFRESH STREAMING TABLE orders_silver
AS
SELECT order_id,
       timestamp(order_timestamp) AS order_timestamp,
       customer_id,
       notifications
FROM STREAM orders_bronze;

-- C. Gold - Aggregation (Materialized View)
CREATE OR REFRESH MATERIALIZED VIEW gold_orders_by_date
AS
SELECT date(order_timestamp) AS order_date,
       count(*) AS total_daily_orders
FROM orders_silver
GROUP BY date(order_timestamp);''')}

<p>Bronze und Silver verwenden <code>STREAMING TABLE</code>, weil sie inkrementell verarbeiten sollen; Gold nutzt bewusst eine <code>MATERIALIZED VIEW</code>, da <code>GROUP BY</code>-Aggregationen nicht rein inkrementell berechnet werden können &ndash; Databricks optimiert die Neuberechnung dort, wo möglich, automatisch.</p>

<h2>5. Dry Run, Ausführung und Historie</h2>
<p>Vor der eigentlichen Ausführung lässt sich per <strong>Dry Run</strong> prüfen, ob der Pipeline-Code syntaktisch korrekt ist &ndash; ohne dass dabei Tabellen tatsächlich erstellt oder aktualisiert werden. Beim regulären Run bietet die Oberfläche zwei Modi:</p>
<table>
<tr><th>Update-Typ</th><th>Materialized View</th><th>Streaming Table</th></tr>
<tr><td><strong>Run pipeline</strong> (Refresh)</td><td>Aktualisiert Ergebnisse für die aktuelle Abfrage; inkrementell, sofern kosteneffizienter</td><td>Verarbeitet nur neue Datensätze über Flows</td></tr>
<tr><td><strong>Run pipeline with full table refresh</strong></td><td>Vollständige Neuberechnung</td><td>Leert Daten und Checkpoints, verarbeitet alle Quelldaten neu</td></tr>
</table>
<p>Jeder inkrementelle Lauf lässt sich über <code>DESCRIBE HISTORY</code> nachvollziehen: In der Spalte <code>operation</code> erscheint bei Streaming Tables <code>STREAMING UPDATE</code> statt eines klassischen <code>WRITE</code> oder <code>MERGE</code>, und <code>operationMetrics</code> zeigt exakt, wie viele Zeilen im jeweiligen Lauf neu hinzugekommen sind &ndash; ein direkter Beleg dafür, dass wirklich nur die neuen Daten verarbeitet wurden.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Der Lakeflow Pipelines Editor wurde auf dem Data + AI Summit 2025 vorgestellt und ersetzt die frühere notebookzentrierte Entwicklungsweise. Laut aktueller Dokumentation liegen Quelldateien standardmäßig im Ordner <code>transformations</code> des Pipeline-Assets-Browsers und können Python- (<code>.py</code>) oder SQL-Dateien (<code>.sql</code>) sein &ndash; auch eine Mischung beider Sprachen innerhalb eines Projekts ist möglich, wobei Code in einer Datei problemlos auf Tabellen verweisen kann, die in einer anderen Datei definiert sind.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ldp/multi-file-editor">Develop and debug ETL pipelines with the Lakeflow Pipelines Editor &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\02 Pipelines entwickeln - Pipeline-Editor und Einstellungen.pdf",
    title="Pipelines entwickeln (Pipeline-Editor, Einstellungen)",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: Kurs 3, Kapitel 4&ndash;5",
    body_html=body,
    build_name="03_02_pipeline_editor",
)
print("OK")
