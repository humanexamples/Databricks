# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Selbst der bestoptimierte Code läuft nur so gut wie die Infrastruktur, auf der er ausgeführt wird. Dieses abschließende Kapitel des Themenordners behandelt die Wahl des richtigen Compute-Typs, die Photon-Engine, Spot-Instances zur Kostensenkung, Autoscaling sowie Serverless Compute &ndash; und ordnet ein, wie sich die Empfehlungen aus den vorherigen Kapiteln (Datenlayout, Skew/Shuffle/Spill) dazu verhalten.</p>

<h2>1. Die drei Compute-Typen in Databricks</h2>
<ul>
<li><strong>All-Purpose Compute</strong> &ndash; für interaktive Workloads, einschließlich Streaming während der Entwicklung. Unterstützt Autoscaling, um bei Bedarf Kapazität hinzuzufügen und Wartezeiten zu verkürzen. Da Autoscaling zusätzliche Angriffsflächen schaffen kann, sollten Sicherheitsaspekte bei der Konfiguration berücksichtigt werden.</li>
<li><strong>Jobs Compute</strong> &ndash; läuft auf ephemeren Clustern, die eigens für den Job erstellt werden und nach Abschluss automatisch terminieren. Wird vorab geplant oder per API gestartet, ist Single-User-fähig, eignet sich gut für Isolation und Debugging, ist für produktive und wiederkehrende Workloads gedacht und in der Regel günstiger als All-Purpose Compute.</li>
<li><strong>SQL Warehouse</strong> &ndash; für Ad-hoc-SQL-Analysen und BI-Serving mit hoher Nebenläufigkeit konzipiert, mit Photon standardmäßig eingebaut. Empfohlen wird ein gemeinsames Warehouse für allgemeine Ad-hoc-Analysen sowie isolierte Warehouses für spezifische Workloads; Serverless-Warehouses bieten sofortigen Start und niedrigere Gesamtbetriebskosten.</li>
</ul>

<h2>2. Photon: die vektorisierte Ausführungs-Engine</h2>
<p><strong>Photon</strong> ist Databricks' nativ in C++ implementierte, vektorisierte Query-Engine, die SQL- und DataFrame-Workloads erheblich beschleunigt. Sie wird ohne Codeänderungen genutzt &ndash; unabhängig davon, ob mit SQL, Python, Scala oder R gearbeitet wird &ndash; und deckt Exploration, ETL, große wie kleine Datenmengen, Low-Latency- und High-Concurrency-Szenarien sowie Batch- und Streaming-Workloads über eine einheitliche Engine und ein einheitliches API-Set ab. Nach Angaben von Databricks erreicht Photon bei SQL-Workloads (TPC-DS-Benchmark) ein bis zu 5-fach besseres Preis-Leistungs-Verhältnis gegenüber anderen Cloud-Data-Warehouses.</p>

<h2>3. Spot-Instances: Kosten senken, aber richtig</h2>
<p><strong>Spot-Instances</strong> sind vom Cloud-Anbieter zu vergünstigten Preisen angebotene, derzeit ungenutzte Rechenkapazitäten &ndash; mit dem Risiko, dass der Anbieter sie bei steigender Nachfrage kurzfristig zurückfordert. Für unkritische, Ad-hoc- oder geteilte Cluster eignen sie sich hervorragend zur Kostensenkung. Eine bewährte Konfiguration: den <strong>Driver auf On-Demand</strong> laufen lassen (er sollte niemals als Spot-Instance konfiguriert werden), während die <strong>Worker als Spot-Instances</strong> laufen &ndash; werden diese vom Anbieter zurückgefordert, bleibt der Job dank des stabilen Drivers zumindest kontrolliert am Leben. Für Workloads mit strengen SLAs empfiehlt sich zusätzlich ein automatischer <strong>Fallback auf On-Demand-Instanzen</strong>, falls keine Spot-Kapazität verfügbar ist.</p>
<table>
<tr><th>SLA-Anforderung</th><th>Empfehlung</th></tr>
<tr><td>Unkritische Jobs</td><td>Driver On-Demand, Worker als Spot-Instances</td></tr>
<tr><td>Workloads mit strengen SLAs</td><td>Spot-Instances mit Fallback auf On-Demand</td></tr>
</table>
<p>Wichtig: Die Ersparnis und Ausfallrate unterscheiden sich stark je Instanztyp, Region und aktueller Marktlage &ndash; ein pauschaler Vergleich oder feste Prozentwerte lohnen sich nicht, da sich diese laufend ändern. Vor einer produktiven Spot-Konfiguration empfiehlt es sich, die aktuelle Ersparnis und Unterbrechungshäufigkeit für den konkreten Instanztyp und die konkrete Region direkt beim Cloud-Anbieter nachzuschlagen.</p>

<h2>4. Autoscaling</h2>
<p>Autoscaling passt die Clustergröße automatisch an die aktuelle Auslastung an: Bei steigender Nachfrage werden zusätzliche Worker-Knoten hinzugefügt, bei sinkender Nachfrage wird der Cluster wieder verkleinert, was Kosten gegenüber einer statisch dimensionierten Größe spart. Für Entwicklung und Ad-hoc-Analysen empfiehlt sich meist eine großzügige Obergrenze; für produktive Batch-Jobs mit vorhersehbarem Datenvolumen reicht häufig eine feste Clustergröße mit einer Obergrenze für gelegentliche Lastspitzen. Autoscaling wird auch für Streaming-Workloads und Spark Declarative Pipelines unterstützt.</p>
<table>
<tr><th>Einsatzzweck</th><th>Autoscaling-Empfehlung</th></tr>
<tr><td>Ad-hoc-Nutzung / Business-Analysen</td><td>Große Spannweite</td></tr>
<tr><td>Produktive Batch-Jobs</td><td>Meist nicht nötig, ggf. Puffer nach oben</td></tr>
<tr><td>Streaming</td><td>In Spark Declarative Pipelines verfügbar</td></tr>
</table>

<h2>5. Cluster-Optimierungsempfehlungen im Überblick</h2>
<ol>
<li><strong>Data-Science- und Data-Engineering-Entwicklung:</strong> All-Purpose Compute mit Autoscale und Auto-Stop, Entwicklung und Tests auf einem Datenausschnitt.</li>
<li><strong>Ingestion- und ETL-Jobs:</strong> Jobs Compute, dimensioniert nach den SLA-Anforderungen des Jobs.</li>
<li><strong>Ad-hoc-SQL-Analysen:</strong> (Serverless-)SQL-Warehouse mit Autoscale und Auto-Stop.</li>
<li><strong>BI-Reporting:</strong> isoliertes SQL-Warehouse, dimensioniert nach den SLAs des BI-Teams.</li>
<li><strong>Allgemeine Best Practices:</strong> Spot-Instances für Worker aktivieren, aktuelle LTS-Runtime nutzen, Photon einsetzen, mit der aktuellen VM-Generation und General-Purpose-Instanztypen beginnen, bevor speicher- oder rechenoptimierte Typen getestet werden.</li>
</ol>

<h2>6. Serverless Compute: die Infrastrukturebene abgeben</h2>
<p>Klassisches Compute erfordert manuelle Entscheidungen zu Instanztypen, Autoscaling-Grenzen, Spot-Konfiguration und Photon. <strong>Serverless Compute</strong> stellt diese Fragen anders: Was, wenn nichts davon manuell verwaltet werden muss? Serverless basiert auf drei Kernversprechen &ndash; höhere Produktivität durch sofortigen Kaltstart und Autoscaling innerhalb von Sekunden, kein manuelles Pool- oder Kapazitätsmanagement mehr, sowie niedrigere Gesamtbetriebskosten, da ausschließlich tatsächlich genutzte Rechenzeit bezahlt wird. Serverless ist inzwischen für alle drei Compute-Typen &ndash; All-Purpose Compute, Jobs Compute und SQL Warehouses &ndash; generell verfügbar (GA), nicht mehr nur als Preview.</p>

<figure class="img">
<img src="assets/06/serverless-compute.png">
<figcaption>Serverless Compute übernimmt Provisionierung, Instanzwahl, Autoscaling und Cluster-Teardown automatisch &ndash; Startzeiten sinken von 5&ndash;12 Minuten auf etwa 15&ndash;30 Sekunden.</figcaption>
</figure>

<p>Ein wichtiger Vorbehalt: Serverless übernimmt die <strong>Infrastrukturebene</strong>, nicht aber die <strong>Optimierungsebene</strong>. Enthält der Code exzessive Shuffles, ist er auch auf Serverless-Compute langsam. Ist das Datenlayout schlecht &ndash; viele kleine Dateien, kein Liquid Clustering, kein Data Skipping &ndash; behebt Serverless dieses Problem nicht automatisch. Photon treibt weiterhin die zugrunde liegende Query-Engine an. Kurz gesagt: Databricks übernimmt die Infrastruktur, Entwicklerinnen und Entwickler bleiben weiterhin für Code und Datenlayout verantwortlich &ndash; alle in diesem Themenordner behandelten Optimierungstechniken (Datenlayout, Liquid Clustering, Skew/Shuffle/Spill-Vermeidung) gelten auf Serverless Compute unverändert weiter.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Photon ist auf Serverless Compute, SQL-Warehouses und Serverless-Lakeflow-Pipelines aktiviert; auf Serverless-Umgebungen wird Photon jedoch gezielt nur dann eingesetzt, wenn der jeweilige Workload tatsächlich davon profitiert. Aktuelle Erweiterungen der Photon-Engine reduzieren zudem den Speicherverbrauch bei sehr breiten Tabellenschemata deutlich, was frühere Out-of-Memory-Probleme in solchen Szenarien entschärft.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/compute/photon">What is Photon? &ndash; Databricks-Dokumentation</a> &middot; <a href="https://docs.databricks.com/aws/en/release-notes/serverless/">Serverless compute release notes</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\Databricks Kurs\Databricks-Dokumentation-DE\Section 6 - Troubleshooting, Monitoring and Optimization\06 Cluster-Auswahl - Photon, Spot-Instanzen und Serverless Compute.pdf",
    title="Cluster-Auswahl: Photon, Spot-Instanzen und Serverless Compute",
    subtitle="Section 6 &middot; Troubleshooting, Monitoring and Optimization &middot; Quelle: Kurs 7, Kapitel 4",
    body_html=body,
    build_name="06_06_cluster_auswahl",
)
print("OK")
