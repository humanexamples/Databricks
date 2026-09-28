# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Databricks bietet mehrere Compute-Typen mit unterschiedlichen Eigenschaften, Kostenmodellen und Einsatzzwecken an. Die richtige Wahl zu treffen ist eine eigenständige Prüfungskompetenz: Es geht nicht nur darum, dass ein Workload überhaupt läuft, sondern dass er auf der wirtschaftlich und technisch passenden Infrastruktur läuft.</p>

<h2>1. All-Purpose Compute</h2>
<p><strong>All-Purpose-Cluster</strong> sind für interaktive Entwicklung gedacht: mehrere Personen können sich denselben Cluster teilen, um Notebooks zu schreiben, zu explorieren und Ad-hoc-Abfragen auszuführen. Sie bleiben so lange laufen, bis sie manuell gestoppt oder durch eine konfigurierte Inaktivitäts-Timeout-Regel automatisch heruntergefahren werden. Der Kompromiss: Der DBU-Satz (Databricks Unit, die Verrechnungseinheit für Compute) ist hier am höchsten, da neben reiner Rechenleistung auch interaktive Funktionen wie Autovervollständigung, Notebook-Anhänge und gemeinsame Nutzung mitfinanziert werden.</p>

<h2>2. Job Compute</h2>
<p><strong>Job-Cluster</strong> werden ausschließlich für die Ausführung eines geplanten oder ausgelösten Lakeflow Jobs erzeugt und nach Abschluss automatisch wieder terminiert &ndash; es gibt keine Leerlaufzeit, für die bezahlt werden müsste. Der DBU-Satz liegt deutlich unter dem von All-Purpose-Clustern, da keine interaktiven Zusatzfunktionen benötigt werden. Job-Cluster sind damit die wirtschaftlich richtige Wahl für produktive, wiederkehrende ETL-Workloads &ndash; nicht für Entwicklung und Exploration.</p>

<h2>3. SQL-Warehouses</h2>
<p><strong>SQL-Warehouses</strong> sind speziell für SQL-Analytics- und BI-Workloads optimiert (Dashboards, Power BI, Tableau, Ad-hoc-SQL-Abfragen vieler gleichzeitiger Nutzer). Sie unterstützen automatische Skalierung über mehrere Cluster hinweg (Multi-Cluster-Load-Balancing) für hohe Nebenläufigkeit und sind in einer klassischen (provisionierten) sowie einer serverlosen Variante verfügbar.</p>

<h2>4. Serverless Compute</h2>
<p><strong>Serverless Compute</strong> ist inzwischen für alle Compute-Typen verfügbar &ndash; Notebooks, Jobs und SQL-Warehouses. Databricks verwaltet dabei die zugrunde liegende Infrastruktur (Instanztypen, Skalierung, Patches) vollständig selbst; Nutzerinnen und Nutzer zahlen nur für tatsächlich verbrauchte Rechenzeit. Der größte praktische Vorteil ist die Startzeit: Serverless-SQL-Warehouses stehen typischerweise innerhalb weniger Sekunden bereit, während klassische Cluster mehrere Minuten zum Hochfahren benötigen.</p>

{code('python', '''# Compute-Konfiguration ist deklarativ, z. B. innerhalb eines Jobs (Auszug aus resources/job.yml)
# job_clusters:
#   - job_cluster_key: etl_cluster
#     new_cluster:
#       spark_version: "15.4.x-scala2.12"
#       node_type_id: "Standard_DS3_v2"
#       autoscale:
#         min_workers: 2
#         max_workers: 8''')}

<h2>5. Entscheidungskriterien für die Prüfung</h2>
<table>
<tr><th>Anforderung</th><th>Passender Compute-Typ</th></tr>
<tr><td>Mehrere Personen entwickeln/explorieren interaktiv im selben Notebook</td><td>All-Purpose Compute</td></tr>
<tr><td>Geplanter, wiederkehrender ETL-Job, kein interaktiver Zugriff nötig</td><td>Job Compute (klassisch oder serverless)</td></tr>
<tr><td>Viele gleichzeitige BI-/Dashboard-Nutzer mit variabler Last</td><td>SQL-Warehouse mit Autoscaling/Multi-Cluster</td></tr>
<tr><td>Schnelle Startzeit, minimaler Verwaltungsaufwand, variable Auslastung</td><td>Serverless Compute (beliebiger Typ)</td></tr>
<tr><td>Kosten für Leerlaufzeit strikt vermeiden</td><td>Job Compute oder Serverless (kein Dauerbetrieb)</td></tr>
</table>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Der DBU-Satz unterscheidet sich zwischen All-Purpose-, Job- und SQL-Warehouse-Compute teils um mehr als das Dreifache für denselben zugrunde liegenden Instanztyp &ndash; ein häufiger Kostenfehler ist, aus Gewohnheit alle Workloads auf All-Purpose-Clustern laufen zu lassen, obwohl produktive, nicht-interaktive Jobs auf Job-Compute deutlich günstiger wären. Serverless-SQL-Warehouses sind laut Databricks innerhalb weniger Sekunden startklar, was insbesondere bei sporadischer BI-Nutzung Kosten spart, da keine dauerhaft laufende Infrastruktur vorgehalten werden muss.<br>
Quelle: <a href="https://www.databricks.com/product/pricing">Databricks Pricing &amp; DBU-Modell &ndash; Databricks</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 1 - Databricks Intelligence Plattform\02 Compute-Optionen - Cluster-Typen, Kosten und Workload-Auswahl.pdf",
    title="Compute-Optionen: Cluster-Typen, Kosten und Workload-Auswahl",
    subtitle="Section 1 &middot; Databricks Intelligence Plattform &middot; Quelle: Databricks-Dokumentation (Compute &amp; Pricing)",
    body_html=body,
    build_name="gap_s1_compute",
)
print("OK")
