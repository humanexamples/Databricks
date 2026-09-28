# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Dieses Dokument bildet den Einstieg in die gesamte Dokumentationsreihe. Es beantwortet drei Fragen: Was ist die Databricks-Plattform eigentlich, wie organisiert sie Daten intern (Medallion-Architektur und Unity Catalog), und wie hängen die sechs folgenden Sections mit dem Databricks-Produkt <strong>Lakeflow</strong> zusammen. Wer diese Landkarte im Kopf hat, kann die Detail-PDFs der übrigen Sections deutlich leichter einordnen.</p>

<h2>1. Die Databricks Data Intelligence Platform</h2>
<p>Databricks ist im Kern eine <strong>Lakehouse-Plattform</strong>: Sie kombiniert die Kostenvorteile und Flexibilität eines Data Lakes (offene Dateiformate, beliebig skalierbarer Cloud-Speicher) mit den Verlässlichkeitsgarantien eines klassischen Data Warehouse (Transaktionssicherheit, Schema-Durchsetzung, schnelle SQL-Abfragen). Möglich wird das durch <strong>Delta Lake</strong>, ein offenes Tabellenformat, das auf Parquet-Dateien aufsetzt und zusätzlich ein JSON-basiertes Transaktionsprotokoll (den <em>Delta Log</em>) mitführt. Dieses Protokoll verleiht sogenannten <strong>Delta-Tabellen</strong> Eigenschaften, die man sonst nur aus Datenbanken kennt:</p>
<ul>
<li><strong>ACID-Transaktionen</strong> &ndash; mehrere Nutzer können gleichzeitig lesen und schreiben, ohne dass sich Änderungen gegenseitig zerstören.</li>
<li><strong>DML-Unterstützung</strong> &ndash; <code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code> und <code>MERGE</code> funktionieren wie in einer relationalen Datenbank.</li>
<li><strong>Time Travel</strong> &ndash; frühere Tabellenversionen lassen sich abfragen oder wiederherstellen.</li>
<li><strong>Schema-Enforcement &amp; -Evolution</strong> &ndash; das Schema wird beim Schreiben geprüft, kann bei Bedarf aber kontrolliert erweitert werden.</li>
</ul>
<p>Auf dieser Speicherschicht setzt Databricks zwei weitere Säulen auf: <strong>Unity Catalog</strong> für die einheitliche Governance (siehe Kapitel 3 sowie Section 7) und <strong>Lakeflow</strong> für Ingestion, Transformation und Orchestrierung (siehe Kapitel 4 sowie Sections 2&ndash;4). Als Verarbeitungs-Engine kommt durchgängig Apache Spark inklusive Structured Streaming zum Einsatz, beschleunigt durch die proprietäre <strong>Photon</strong>-Engine &ndash; Details dazu in Section 6.</p>

<figure class="img">
<img src="assets/00/lakeflow-overview.png">
<figcaption>Die Databricks Data Intelligence Platform: optimierter Speicher (Delta Lake/Parquet/Iceberg), einheitliche Governance (Unity Catalog) und Lakeflow als Klammer um Connect, Pipelines und Jobs.</figcaption>
</figure>

<h2>2. Medallion-Architektur: Bronze, Silver, Gold</h2>
<p>Daten werden in Databricks typischerweise nicht in einem Schritt von der Rohquelle zur fertigen Kennzahl verarbeitet, sondern durchlaufen mehrere aufeinander aufbauende Qualitätsstufen &ndash; die sogenannte <strong>Medallion-Architektur</strong>, gelegentlich auch als <strong>Multi-Hop-Architektur</strong> bezeichnet, da die Daten schrittweise mehrere &bdquo;Hops&ldquo; (Stufen) durchlaufen:</p>
<ul>
<li><strong>Bronze</strong> &ndash; Rohdaten, so wie sie aus der Quelle kommen (Dateien, Datenbank-Exporte, API-Antworten). Es findet kaum Transformation statt, damit die Ursprungsdaten jederzeit nachvollziehbar bleiben.</li>
<li><strong>Silver</strong> &ndash; bereinigte, validierte und angereicherte Daten. Duplikate werden entfernt, Typen korrigiert, Tabellen aus mehreren Quellen zusammengeführt.</li>
<li><strong>Gold</strong> &ndash; aggregierte, geschäftsfertige Daten, meist bereits auf die Anforderungen von BI-Dashboards, Machine-Learning-Modellen oder operativen Anwendungen zugeschnitten.</li>
</ul>
<p>Jede Stufe kann sowohl aus Batch- als auch aus Streaming-Quellen gespeist werden; der zentrale Vorteil ist, dass Datenqualität und Nutzbarkeit mit jeder Stufe steigen, während gleichzeitig die Rohdaten der Bronze-Schicht als Fallback erhalten bleiben. Die wichtigsten Vorteile dieses Musters im Überblick:</p>
<ul>
<li><strong>Einfaches, verständliches Datenmodell</strong> &ndash; drei klar abgegrenzte Stufen statt einer unübersichtlichen Vielzahl von Ad-hoc-Transformationen.</li>
<li><strong>Inkrementelles ETL</strong> &ndash; jede Stufe verarbeitet nur die seit dem letzten Lauf neu hinzugekommenen Daten, statt bei jedem Durchlauf alles neu zu berechnen.</li>
<li><strong>Batch und Streaming in derselben Pipeline kombinierbar</strong> &ndash; jede einzelne Stufe lässt sich unabhängig als Batch- oder Streaming-Job konfigurieren.</li>
<li><strong>Tabellen jederzeit aus den Rohdaten rekonstruierbar</strong> &ndash; da Bronze die unveränderten Ursprungsdaten dauerhaft aufbewahrt, lassen sich Silver und Gold bei Bedarf (z. B. nach einem Fehler in der Transformationslogik) komplett neu aus Bronze berechnen.</li>
</ul>

<figure class="img">
<img src="assets/00/medallion-architecture.png">
<figcaption>Bronze &rarr; Silver &rarr; Gold: Rohdaten werden schrittweise bereinigt, angereichert und für Reporting, ML/KI und Streaming-Analysen aufbereitet.</figcaption>
</figure>

<h2>3. Unity Catalog: die Governance-Ebene</h2>
<p><strong>Unity Catalog</strong> ist die zentrale Verwaltungsschicht für alle Daten- und KI-Objekte im Workspace &ndash; unabhängig davon, ob es sich um Tabellen, Dateien, Machine-Learning-Modelle oder Dashboards handelt. Er stellt Zugriffskontrolle, Auditing, Data Lineage, Datenqualitäts-Monitoring und Discoverability über beliebig viele Workspaces hinweg bereit. Die Objekte sind hierarchisch organisiert:</p>
<table>
<tr><th>Ebene</th><th>Bedeutung</th></tr>
<tr><td><strong>Metastore</strong></td><td>Oberste Ebene pro Cloud-Region; enthält die Metadaten aller Catalogs. In der Regel ein Metastore pro Organisation/Region.</td></tr>
<tr><td><strong>Catalog</strong></td><td>Oberste Organisationseinheit für Daten, z. B. getrennt nach Umgebung (<code>dev</code>, <code>prod</code>) oder Geschäftsbereich.</td></tr>
<tr><td><strong>Schema (Database)</strong></td><td>Gruppiert zusammengehörige Tabellen, Views und Volumes innerhalb eines Catalogs, ähnlich einem Datenbankschema.</td></tr>
<tr><td><strong>Table / View</strong></td><td>Die eigentlichen strukturierten Daten &ndash; als Managed Table (Databricks verwaltet Daten und Metadaten) oder External Table (nur Metadaten werden verwaltet).</td></tr>
<tr><td><strong>Volume</strong></td><td>Governed Zugriff auf nicht-tabellarische Dateien (z. B. Rohdateien vor der Ingestion, Bilder, Modell-Artefakte).</td></tr>
</table>
<p>Der vollqualifizierte Name eines Objekts folgt entsprechend dem Muster <code>catalog.schema.table</code>, z. B. <code>prod.sales.orders_gold</code>. Zugriffsrechte werden über Standard-SQL-Befehle wie <code>GRANT SELECT ON TABLE ... TO ...</code> vergeben und lassen sich bis auf Zeilen- und Spaltenebene verfeinern (siehe Section 7 &ndash; Governance and Security).</p>

<h2>4. Lakeflow: die Landkarte für Ingestion, Transformation und Orchestrierung</h2>
<p><strong>Lakeflow</strong> ist die Sammelbezeichnung für Databricks' integrierte Data-Engineering-Werkzeuge. Es besteht aus drei (inzwischen vier) Kernkomponenten, die inhaltlich genau den ersten Themenordnern dieser Dokumentationsreihe entsprechen:</p>
<ul>
<li><strong>Lakeflow Connect</strong> &ndash; effiziente Ingestion-Connectoren, mit denen Daten aus Cloud-Speicher, Datenbanken, SaaS-Anwendungen (z. B. Salesforce, SharePoint) und Message-Bussen (z. B. Kafka) in die Lakehouse-Plattform gelangen. Batch, inkrementelles Batch und Streaming werden dabei einheitlich unterstützt.</li>
<li><strong>Lakeflow Pipelines</strong> (früher <em>Delta Live Tables</em>, technisch als <em>Spark Declarative Pipelines</em> bezeichnet) &ndash; ein deklaratives Framework für Batch- und Streaming-ETL in SQL und Python. Statt einzelne Verarbeitungsschritte manuell zu orchestrieren, beschreibt man nur das gewünschte Ergebnis (Streaming Tables, Materialized Views); Databricks kümmert sich um Ausführungsreihenfolge, Fehlerbehandlung und inkrementelle Aktualisierung.</li>
<li><strong>Lakeflow Jobs</strong> &ndash; die Orchestrierungsschicht, mit der beliebige Workloads (Notebooks, SQL-Abfragen, Pipelines, ML-Trainings) zu Workflows mit Abhängigkeiten, Zeitplänen und Benachrichtigungen kombiniert werden &ndash; als native Alternative zu externen Tools wie Apache Airflow.</li>
<li><strong>Lakeflow Designer</strong> &ndash; eine neuere, no-code/low-code Oberfläche, mit der auch Analysten ohne Programmierkenntnisse per Drag-and-drop und natürlichsprachlichen Prompts produktionsreife ETL-Pipelines erstellen können.</li>
</ul>

<h3>So sind die Sections dieser Dokumentation aufgebaut</h3>
<table>
<tr><th>Section</th><th>Thema</th><th>Lakeflow-/Plattform-Bezug</th></tr>
<tr><td>1</td><td>Databricks Intelligence Plattform</td><td>Dieses Dokument &ndash; Lakehouse-Grundlagen, Medallion-Architektur, Unity Catalog, Lakeflow-Landkarte</td></tr>
<tr><td>2</td><td>Data Ingestion and Loading</td><td>Connect &ndash; Batch-/Streaming-Ingestion, Metadaten, Enterprise-Connectoren, MERGE INTO</td></tr>
<tr><td>3</td><td>Data Transformation and Modelling</td><td>Pipelines &ndash; Streaming Tables, Materialized Views, Expectations, Multi-Flow, Liquid Clustering, Delta Sinks, CDC (SCD Type 1 &amp; 2)</td></tr>
<tr><td>4</td><td>Working with Lakeflow Jobs</td><td>Jobs &ndash; Tasks, Scheduling, bedingte/iterative Tasks, Monitoring, Best Practices</td></tr>
<tr><td>5</td><td>Implementing CI/CD</td><td>Software Engineering &amp; Deployment &ndash; Modularisierung, Unit-/Integrationstests, Git, Asset Bundles, Multi-Environment-Deployments</td></tr>
<tr><td>6</td><td>Troubleshooting, Monitoring and Optimization</td><td>Spark-Engine &ndash; AQE, Data Skipping, Liquid Clustering, Skew/Shuffle/Spill, Cluster-Auswahl/Photon</td></tr>
<tr><td>7</td><td>Governance and Security</td><td>Unity Catalog &ndash; ACLs, Row Filters/Column Masks, PII-Schutz, CDF, DSGVO/CCPA</td></tr>
</table>
<p>Kurz gesagt: Section 2&ndash;4 behandeln die drei klassischen Lakeflow-Komponenten (Connect, Pipelines, Jobs), Section 6&ndash;7 vertiefen die darunterliegenden Plattformdienste (Performance, Governance), und Section 5 zeigt, wie man all das softwaretechnisch sauber entwickelt, testet und produktiv ausrollt &ndash; von der ersten Unit-Test-Zeile bis zum automatisierten Asset-Bundle-Deployment.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Seit 2025 zählt neben Connect, Pipelines und Jobs auch <strong>Lakeflow Designer</strong> offiziell zu Lakeflow &ndash; eine visuelle, KI-gestützte No-Code-Oberfläche, mit der auch Fachanwender ohne Python-/SQL-Kenntnisse Pipelines per Drag-and-drop und natürlichsprachlichen Prompts bauen können. Der frühere Produktname &bdquo;Delta Live Tables&ldquo; wurde vollständig durch <strong>Lakeflow Pipelines</strong> (technisch: Spark Declarative Pipelines) ersetzt; die zugrunde liegenden Konzepte (Streaming Tables, Materialized Views, Expectations) sind unverändert geblieben.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/data-engineering">Data engineering with Databricks &ndash; Databricks-Dokumentation</a>, <a href="https://www.databricks.com/blog/introducing-databricks-lakeflow">Introducing Databricks Lakeflow &ndash; Databricks Blog</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 1 - Databricks Intelligence Plattform\01 Databricks Data-Engineering-Plattform und Lakeflow im Ueberblick.pdf",
    title="Databricks Data-Engineering-Plattform & Lakeflow im Überblick",
    subtitle="Section 1 &middot; Databricks Intelligence Plattform &middot; Quelle: Kurs 1 &amp; Kurs 2, jeweils Lektion 1",
    body_html=body,
    build_name="00_01_ueberblick",
)
print("OK")
