# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Z-Ordering und Partitionierung (Kapitel 06-2) haben einen gemeinsamen Nachteil: Sie erfordern manuelle Entscheidungen &ndash; welche Spalte, welche Kardinalität, wann neu optimieren &ndash; und reagieren schlecht auf sich ändernde Abfragemuster. <strong>Liquid Clustering</strong> ist Databricks' Antwort darauf: eine Technik, die Partitionierung und Z-Ordering ersetzen soll, indem sie sich automatisch und fortlaufend an die tatsächlichen Daten und Abfragen anpasst.</p>

<h2>1. Warum &bdquo;liquid&ldquo;? Das Grundprinzip</h2>
<p>Anders als bei starren Partitionsgrenzen zielt Liquid Clustering darauf ab, eine <strong>konsistente Zieldateigröße</strong> zu erreichen. Statt Daten in feste Partitionen zu zwingen, entscheidet Databricks intelligent, welche Wertebereiche zu welchen Dateien zusammengefasst werden, damit die Dateigrößen über die gesamte Tabelle hinweg möglichst gleichmäßig bleiben. Dazu speichert Liquid Clustering zusätzliche Metadaten, mit deren Hilfe neu geschriebene Daten direkt beim Schreiben (&bdquo;Clustering on Write&ldquo;) in die bestehende Clusterstruktur eingeordnet werden.</p>

<figure class="img">
<img src="assets/06/liquid-clustering.png">
<figcaption>Liquid Clustering passt die Dateiaufteilung flexibel an die Daten an, statt sie in starre Partitionsgrenzen zu zwingen.</figcaption>
</figure>

<h2>2. Vorteile gegenüber Partitionierung und Z-Ordering</h2>
<ul>
<li><strong>Beste Performance ohne Tuning</strong> &ndash; Clustering erfolgt automatisch beim Schreiben, ganz ohne manuelle Konfiguration.</li>
<li><strong>Konsistentes Data Skipping</strong> &ndash; unempfindlich gegenüber Data Skew, da keine starren Partitionsgrenzen existieren, die zu ungleich großen Dateien führen können.</li>
<li><strong>Minimale Schreibverstärkung bei der Wartung</strong> &ndash; echtes <em>inkrementelles</em> <code>OPTIMIZE</code>: Nur die noch nicht optimal geclusterten Bereiche werden neu geschrieben, nicht die gesamte Tabelle.</li>
<li><strong>Row-Level Concurrency</strong> &ndash; vereinfacht die Logik für nebenläufige Schreibvorgänge mehrerer gleichzeitiger Writer.</li>
<li><strong>Weniger kognitive Last</strong> &ndash; es muss nicht mehr abgewogen werden, ob eine Spalte für Partitionierung geeignete (niedrige) Kardinalität besitzt; Liquid Clustering funktioniert unabhängig von der Kardinalität der Clustering-Spalten gut.</li>
</ul>

<h2>3. Liquid Clustering einrichten</h2>
<p>Anstelle von <code>PARTITIONED BY</code> oder eines nachträglichen <code>ZORDER BY</code> wird beim Anlegen einer Tabelle <code>CLUSTER BY</code> mit den gewünschten Clustering-Spalten angegeben. Alternativ lässt sich mit <code>CLUSTER BY AUTO</code> die Auswahl der Clustering-Spalten vollständig Databricks überlassen (siehe <em>Predictive Optimization</em> unten).</p>

{code('sql', '''-- Tabelle mit Liquid Clustering anlegen
CREATE TABLE events (
  event_id   BIGINT,
  event_time TIMESTAMP,
  user_id    STRING,
  event_type STRING
)
CLUSTER BY (event_type, user_id);

-- Clustering-Keys nachträglich ändern -- ohne vollständige Neuschreibung der Tabelle
ALTER TABLE events CLUSTER BY (event_type);

-- Clustering periodisch anwenden (inkrementell, nur unclustered Daten werden bearbeitet)
OPTIMIZE events;''')}

<h2>4. Tabellenstatistiken für den Cost-Based Optimizer</h2>
<p>Unabhängig vom gewählten Layout-Verfahren lohnt es sich, regelmäßig aktuelle Tabellenstatistiken zu berechnen. Sie helfen der Adaptive Query Execution (Kapitel 06-1) unter anderem dabei, die passende Join-Strategie zu wählen, die richtige Build-Seite bei einem Hash-Join zu bestimmen und die Join-Reihenfolge bei Multi-Way-Joins zu kalibrieren.</p>

{code('sql', '''ANALYZE TABLE mytable COMPUTE STATISTICS FOR ALL COLUMNS;''')}

<h2>5. Predictive Optimization: automatische Wartung</h2>
<p><strong>Predictive Optimization</strong> geht noch einen Schritt weiter als Liquid Clustering selbst: Sie übernimmt die routinemäßige Wartung von Delta-Tabellen vollautomatisch. Auf Basis der beobachteten Workload-Muster entscheidet Databricks im Hintergrund, wann <code>OPTIMIZE</code> (Dateigrößen optimieren) und <code>VACUUM</code> (nicht mehr benötigte Datendateien entfernen und so Speicherkosten senken) ausgeführt werden sollten &ndash; ganz ohne dass diese Jobs manuell geplant oder überwacht werden müssen. Wenn <code>CLUSTER BY AUTO</code> verwendet wird, wählt Predictive Optimization zusätzlich selbstständig die effektivsten Clustering-Spalten anhand des tatsächlichen Abfrageverhaltens aus und passt diese Wahl an, sobald sich die Zugriffsmuster ändern. Die Wartungsjobs laufen dabei auf Serverless-Compute, sodass auch hierfür keine eigene Cluster-Verwaltung nötig ist.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Mit <strong>Automatic Liquid Clustering</strong> analysiert Predictive Optimization die historische Abfrage-Workload einer Tabelle und wählt darauf aufbauend automatisch die Clustering-Keys, die den größten Nutzen beim Data Skipping bringen &ndash; Clustering-Keys werden dabei nur dann geändert, wenn die geschätzte Ersparnis durch besseres Data Skipping die Kosten der Neu-Clusterung übersteigt. Predictive Optimization ist für alle nach dem 11.&nbsp;November 2024 angelegten Accounts standardmäßig aktiviert; für bestehende Accounts erfolgt ein schrittweiser Rollout. Liquid Clustering ist zudem nicht mit Z-Ordering auf derselben Tabelle kompatibel.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/tables/clustering">Use liquid clustering for tables &ndash; Databricks-Dokumentation</a> &middot; <a href="https://docs.databricks.com/aws/en/optimizations/predictive-optimization">Predictive optimization for Unity Catalog managed tables</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 6 - Troubleshooting, Monitoring and Optimization\03 Liquid Clustering und Predictive Optimization.pdf",
    title="Liquid Clustering und Predictive Optimization",
    subtitle="Section 6 &middot; Troubleshooting, Monitoring and Optimization &middot; Quelle: Kurs 7, Kapitel 2.2.5",
    body_html=body,
    build_name="06_03_liquid_clustering",
)
print("OK")
