# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Kapitel 2 dieser Section hat die vier Compute-Typen (All-Purpose, Job, SQL-Warehouse, Serverless) und ihre Kostenlogik bereits vorgestellt, Section 6 Kapitel 6 die Spot-Instance-Konfiguration. Dieses Kapitel ergänzt zwei praktische Bausteine der Cluster-Konfiguration, die dort noch nicht behandelt wurden: die Wahl des richtigen <strong>Instance-Typs</strong> je nach Workload und <strong>Instance Pools</strong> zur Beschleunigung des Cluster-Starts.</p>

<h2>1. Classic vs. Serverless: die zwei Grundkategorien</h2>
<p>Sämtliche Compute-Typen aus Kapitel 2 lassen sich einer von zwei übergeordneten Kategorien zuordnen: <strong>Classic Compute</strong> (All-Purpose, Job, Pools, SQL-Warehouses &ndash; die Infrastruktur wird vom Cloud-Anbieter bereitgestellt und ist konfigurierbar) und <strong>Serverless Compute</strong> (Notebooks, Jobs, Pipelines, SQL-Warehouses &ndash; Databricks verwaltet die Infrastruktur vollständig selbst).</p>

<figure class="img">
<img src="assets/s1/compute_classic_vs_serverless.png">
<figcaption>Databricks Compute gliedert sich in Classic Compute (konfigurierbare Cloud-Infrastruktur) und Serverless Compute (vollständig von Databricks verwaltet).</figcaption>
</figure>

<h2>2. Instance Family: die passende VM-Kategorie wählen</h2>
<p>Bei Classic Compute lässt sich die zugrunde liegende virtuelle Maschine gezielt nach Workload-Typ auswählen. Die falsche Wahl kostet entweder unnötig Geld (überdimensioniert) oder Performance (unterdimensioniert):</p>
<table>
<tr><th>VM-Kategorie</th><th>Geeignet für</th></tr>
<tr><td><strong>Memory Optimized</strong></td><td>Umfangreiches Shuffling/Spilling, Spark-Caching, speicherintensive ML-Workloads</td></tr>
<tr><td><strong>Compute Optimized</strong></td><td>Structured-Streaming-Jobs, ELT mit vollständigem Scan ohne Datenwiederverwendung, <code>OPTIMIZE</code>/<code>ZORDER</code></td></tr>
<tr><td><strong>Storage Optimized</strong></td><td>Delta-Caching, Ad-hoc-/interaktive Analysen, ML/DL-Workloads mit Daten-Caching</td></tr>
<tr><td><strong>GPU Optimized</strong></td><td>ML/DL-Workloads mit außergewöhnlich hohem Speicherbedarf</td></tr>
<tr><td><strong>General Purpose</strong></td><td>Keine speziellen Anforderungen; <code>VACUUM</code></td></tr>
</table>

<figure class="img">
<img src="assets/s1/instance_family_workload_types.png">
<figcaption>Die Wahl der VM-Kategorie richtet sich nach dem Workload-Typ: Memory-, Compute-, Storage- oder GPU-optimiert, oder General Purpose ohne besondere Anforderungen.</figcaption>
</figure>

<p>Spot-Instances als weiteres Mittel zur Kostensenkung &ndash; inklusive der bewährten Driver-on-Demand/Worker-als-Spot-Konfiguration und konkreter Ersparnis-/Ausfallraten je Instanztyp &ndash; behandelt bereits Section 6, Kapitel 6 ausführlich.</p>

<h2>3. Instance Pools: schnellerer Cluster-Start</h2>
<p>Ein <strong>Instance Pool</strong> ist eine Menge bereits laufender, ungenutzter virtueller Maschinen, die auf ihren Einsatz warten. Wird ein neuer Cluster (oder eine Autoscaling-Erweiterung) aus einem Pool heraus erstellt, entfällt die sonst übliche VM-Boot-Zeit &ndash; Cluster-Start und Autoscaling werden dadurch spürbar beschleunigt. Wichtig für die Kostenkalkulation: Databricks selbst berechnet für ungenutzte Instanzen im Pool <strong>keine</strong> DBU-Gebühr, der Cloud-Anbieter stellt diese Instanzen aber weiterhin in Rechnung, da sie technisch im eigenen Cloud-Konto laufen.</p>

<h2>4. Pro vs. Serverless SQL-Warehouse</h2>
<p>Ergänzend zur Übersicht aus Kapitel 2: Bei <strong>klassischen (Pro) SQL-Warehouses</strong> greift man konkret dann, wenn entweder in der gewählten Cloud-Region <strong>kein Serverless-Warehouse verfügbar</strong> ist, oder wenn ein <strong>benutzerdefiniertes Netzwerk-Setup</strong> benötigt wird &ndash; etwa um aus dem SQL-Warehouse heraus Datenbanken oder Event-Busse im eigenen Cloud-Netzwerk oder On-Premises anzubinden. Serverless-Warehouses bleiben für die meisten Fälle (ETL, BI, explorative Analysen) die einfachere und schneller startende Wahl.</p>

<figure class="img">
<img src="assets/s1/pricing_serverless_vs_classic.png">
<figcaption>Kostenvergleich: Serverless Compute bündelt DBU- und Infrastrukturkosten in einem einzigen Posten; bei Classic Compute kommen Cloud-Anbieter-Instanzkosten und ggf. operative Kosten für die manuelle Cluster-Verwaltung hinzu.</figcaption>
</figure>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks empfiehlt, die Instance-Family-Auswahl regelmäßig anhand des Spark-UI (insbesondere Shuffle-Read/-Write und Spill-Metriken) zu überprüfen und bei Bedarf anzupassen, statt sie einmalig festzulegen &ndash; Workload-Charakteristika ändern sich mit wachsendem Datenvolumen. Für Instance Pools gilt zudem: Ein Pool kann eine minimale Anzahl an Idle-Instanzen sowie eine maximale Gesamtkapazität festlegen; Instanzen oberhalb des Minimums werden nach einer konfigurierbaren Leerlaufzeit automatisch beendet, um unnötige Cloud-Kosten zu vermeiden.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/compute/pools">Pool configuration reference &ndash; Databricks-Dokumentation</a> &middot; <a href="https://docs.databricks.com/aws/en/compute/configure">Compute configuration reference &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 1 - Databricks Intelligence Plattform\08 Compute vertieft - Instance-Typen, Pools und Spot-Instances.pdf",
    title="Compute vertieft: Instance-Typen, Pools und Spot-Instances",
    subtitle="Section 1 &middot; Databricks Intelligence Plattform &middot; Quelle: Udemy-Kursmaterial &bdquo;Cluster Best Practices&ldquo;, erg&auml;nzt mit Databricks-Dokumentation",
    body_html=body,
    build_name="gap_s1_compute_vertieft",
)
print("OK")
