# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Um Spark-Anwendungen auf Databricks gezielt zu optimieren, hilft es, zunächst zu verstehen, wie Spark eine Anfrage überhaupt ausführt. Dieses Kapitel erklärt die grundlegende Ausführungshierarchie (Jobs, Stages, Tasks), die Rollen von Driver und Executor im Cluster sowie die <strong>Adaptive Query Execution (AQE)</strong> &ndash; eine der wichtigsten Optimierungstechniken moderner Spark-Versionen, die viele manuelle Tuning-Schritte überflüssig macht.</p>

<h2>1. Wie Spark eine Anwendung ausführt: Jobs, Stages, Tasks</h2>
<p>Der Grund, warum Spark große Datenmengen so schnell verarbeiten kann, ist <strong>Parallelität</strong>: Eine Berechnung wird in kleine Einheiten zerlegt, die gleichzeitig auf vielen Maschinen laufen. Spark strukturiert diese Parallelität in drei Ebenen:</p>
<ul>
<li><strong>Job</strong> &ndash; Jede ausgelöste Aktion (Action, z.&nbsp;B. <code>write</code>, <code>count</code>, <code>display</code>) startet einen Job. Ein Job ist die größte Ausführungseinheit.</li>
<li><strong>Stage</strong> &ndash; Ein Job wird in eine geordnete Abfolge von Stages zerlegt. Eine neue Stage beginnt immer dann, wenn Daten neu über das Netzwerk verteilt werden müssen (siehe Shuffle, Kapitel 06-4).</li>
<li><strong>Task</strong> &ndash; Die kleinste Ausführungseinheit. Der Driver erzeugt für jede Datenpartition eine Task, die von einem Executor-Kern abgearbeitet wird.</li>
</ul>

<h2>2. Die Spark-Architektur: Driver, Worker, Executor, Cores</h2>
<p>Ein Databricks-Cluster besteht aus virtuellen Maschinen, über die eine Berechnung verteilt wird. Typischerweise gibt es einen <strong>Driver</strong> und mehrere <strong>Worker-Knoten</strong> (Databricks bietet zusätzlich einen Single-Node-Modus für Entwicklung/Tests kleiner Workloads an).</p>
<ul>
<li><strong>Driver</strong> &ndash; Die Maschine, auf der die Anwendung läuft. Er hält den Zustand der Spark-Anwendung, reagiert auf das Nutzerprogramm und ist verantwortlich für Analyse, Verteilung und Planung der Arbeit auf die Executor. Pro Cluster gibt es immer nur <em>einen</em> Driver, unabhängig von der Anzahl der Executor.</li>
<li><strong>Worker-Knoten</strong> &ndash; Hostet den Executor-Prozess mit einer festen Anzahl an Executors.</li>
<li><strong>Executor</strong> &ndash; Jeder Executor hält einen Teil der zu verarbeitenden Daten &ndash; eine sogenannte <strong>Spark-Partition</strong> (nicht zu verwechseln mit einer Festplattenpartition!). Executor führen die vom Driver zugewiesene Arbeit aus und melden den Berechnungsstatus zurück an den Driver.</li>
<li><strong>Cores</strong> (auch Slots oder Threads genannt) &ndash; Spark parallelisiert auf zwei Ebenen: zum einen wird die Arbeit auf mehrere Executor verteilt, zum anderen besitzt jeder Executor mehrere Slots, denen jeweils eine Task zugewiesen werden kann.</li>
</ul>

<figure class="img">
<img src="assets/06/spark-architecture.png">
<figcaption>Grundstruktur eines Spark-Clusters: Der Driver verteilt Arbeit an die Executor, die wiederum über mehrere Cores parallel Tasks abarbeiten.</figcaption>
</figure>

<h2>3. Catalyst-Optimizer: Logischer und physischer Plan</h2>
<p>Bevor eine DataFrame- oder SQL-Operation tatsächlich ausgeführt wird, durchläuft sie Sparks <strong>Catalyst-Optimizer</strong>. Dieser übersetzt die Abfolge der Transformationen zunächst in einen <em>logischen Plan</em>, wendet Optimierungsregeln und Kostenmodelle an und erzeugt daraus einen <em>physischen Plan</em>, der festlegt, wie die Berechnung konkret als RDD-Transformationen und -Aktionen auf dem Cluster ausgeführt wird. Dieser mehrstufige Optimierungsprozess ist einer der Hauptgründe, warum DataFrame- und SQL-Operationen in aller Regel deutlich performanter sind als handgeschriebene RDD-Transformationen oder Single-Threaded-Python/Pandas-Code, der gar nicht erst von Catalyst optimiert werden kann.</p>

<h2>4. Adaptive Query Execution (AQE)</h2>
<p>Ein statischer Ausführungsplan hat einen Nachteil: Er basiert auf Schätzungen, die vor der eigentlichen Ausführung getroffen werden und sich als ungenau herausstellen können. <strong>Adaptive Query Execution</strong> (seit Spark&nbsp;3.0 verfügbar, seit Spark&nbsp;3.2 standardmäßig aktiviert) löst dieses Problem, indem Spark den Ausführungsplan <em>während</em> der Laufzeit anhand tatsächlich beobachteter Statistiken neu optimiert. Nach jedem Shuffle- oder Broadcast-Austausch (einer sogenannten Query-Stage) liegen genaue Zahlen vor, auf deren Basis Spark bessere Entscheidungen treffen kann als jede Vorab-Schätzung.</p>
<p>AQE umfasst im Kern drei Optimierungen:</p>
<ul>
<li><strong>Dynamischer Wechsel der Join-Strategie</strong> &ndash; Stellt sich zur Laufzeit heraus, dass eine Tabelle klein genug ist, wechselt Spark automatisch von einem teuren Sort-Merge-Join zu einem günstigeren Broadcast-Hash-Join.</li>
<li><strong>Dynamisches Zusammenlegen von Shuffle-Partitionen</strong> &ndash; Viele kleine, nach einem Shuffle entstandene Partitionen werden automatisch zu größeren, effizienteren Partitionen zusammengefasst.</li>
<li><strong>Dynamische Optimierung von Skew-Joins</strong> &ndash; Überproportional große Partitionen (Data Skew) werden automatisch aufgeteilt, sodass die Arbeit gleichmäßiger auf die Cores verteilt wird (siehe Kapitel 06-4).</li>
</ul>

<h2>5. DataFrame/SQL statt RDD: Praktische Empfehlungen</h2>
<p>Aus dem Zusammenspiel von Catalyst und AQE ergeben sich klare Code-Empfehlungen für den produktiven Einsatz:</p>
<ol>
<li>DataFrames oder Spark SQL statt der niedrigeren RDD-API verwenden &ndash; nur so profitiert der Code vollständig von Catalyst und AQE.</li>
<li>In Produktions-Jobs unnötige Aktionen vermeiden, die zusätzliche Berechnungen auslösen (z.&nbsp;B. <code>count()</code>, <code>display()</code>, <code>collect()</code>), sofern sie nicht zwingend erforderlich sind.</li>
<li>Operationen vermeiden, die die gesamte Berechnung auf den Driver zwingen, etwa Single-Threaded-Pandas-Code. Stattdessen die <strong>Pandas API on Spark</strong> nutzen, die pandas-ähnliche Syntax auf verteilte Ausführung über alle Cores abbildet.</li>
</ol>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> AQE ist heute standardmäßig aktiviert und umfasst neben den drei klassischen Optimierungen (Join-Strategie, Partition-Coalescing, Skew-Handling) inzwischen auch Optimierungen, die früher manuelle Hints erforderten. Seit Databricks Runtime&nbsp;13.1 profitieren im Rahmen von Project Lightspeed auch strukturierte Streaming-Queries mit <code>foreachBatch</code>-Sink von den dynamischen AQE-Neuoptimierungen. Die aktuelle Referenz listet die konkreten Konfigurationsparameter (z.&nbsp;B. Schwellenwerte für Skew-Erkennung) im Detail auf.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/optimizations/aqe">Adaptive query execution &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 6 - Troubleshooting, Monitoring and Optimization\01 Spark-Architektur und Adaptive Query Execution.pdf",
    title="Spark-Architektur und Adaptive Query Execution",
    subtitle="Section 6 &middot; Troubleshooting, Monitoring and Optimization &middot; Quelle: Kurs 7, Kapitel 1",
    body_html=body,
    build_name="06_01_spark_architektur_aqe",
)
print("OK")
