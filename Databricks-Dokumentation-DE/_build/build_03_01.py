# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Klassische ETL-Pipelines lesen bei jedem Lauf alle Dateien eines Verzeichnisses neu ein &ndash; das funktioniert für kleine Datenmengen, wird aber mit wachsendem Datenvolumen zunehmend teuer und langsam. <strong>Lakeflow Declarative Pipelines</strong> (kurz: SDP, ehemals <strong>Delta Live Tables</strong>/DLT) lösen dieses Problem, indem Entwickler nur noch <em>deklarieren</em>, welche Tabellen aus welchen Quellen entstehen sollen &ndash; Databricks kümmert sich automatisch um inkrementelle Verarbeitung, Abhängigkeiten und Orchestrierung im Hintergrund.</p>

<h2>1. Warum deklarativ statt prozedural?</h2>
<p>Bei einer klassischen (prozeduralen) Pipeline wird jeder Schritt einzeln als <code>CREATE OR REPLACE TABLE</code> formuliert, wobei jede Anweisung bei jedem Lauf die komplette Quelle neu liest und neu berechnet:</p>

{code('sql', '''-- Klassischer Ansatz: jede Ausfuehrung liest ALLE Dateien neu ein
CREATE OR REPLACE TABLE orders_bronze
AS
SELECT *, current_timestamp() AS processing_time, _metadata.file_name AS source_file
FROM read_files(source_volume_path || "/orders", format => "json");

CREATE OR REPLACE TABLE orders_silver
AS
SELECT order_id, timestamp(order_timestamp) AS order_timestamp, customer_id, notifications
FROM orders_bronze;''')}

<p>Dieser Ansatz funktioniert, wird aber mit wachsender Datenmenge zunehmend ineffizient: Kosten und Laufzeit steigen mit jeder zusätzlichen Datei, unabhängig davon, ob diese neu ist oder nicht. Structured Streaming würde inkrementelle Verarbeitung ermöglichen, bringt dafür aber deutlich mehr Komplexität mit sich (Checkpoints, Trigger-Konfiguration, Zustandsverwaltung). Lakeflow Declarative Pipelines schließt genau diese Lücke: Man beschreibt das <em>gewünschte Ergebnis</em>, nicht den prozeduralen Weg dorthin &ndash; die Plattform übernimmt inkrementelle Ausführung, Abhängigkeitsauflösung und Automatisierung.</p>

<h2>2. Namensänderung: von Delta Live Tables zu Lakeflow Declarative Pipelines</h2>
<p>Wer bereits mit <strong>Delta Live Tables (DLT)</strong> gearbeitet hat, findet die Konzepte hier wieder &ndash; nur mit aktualisierter Terminologie. Die Kernsemantik ist unverändert, alte Syntax bleibt aus Kompatibilitätsgründen nutzbar:</p>
<table>
<tr><th>Veraltet (DLT)</th><th>Aktuell (Lakeflow Declarative Pipelines)</th></tr>
<tr><td><code>CREATE OR REFRESH STREAMING LIVE TABLE</code></td><td><code>CREATE OR REFRESH STREAMING TABLE</code></td></tr>
<tr><td><code>CREATE OR REFRESH LIVE TABLE</code></td><td><code>CREATE OR REFRESH MATERIALIZED VIEW</code></td></tr>
<tr><td><code>CREATE LIVE VIEW</code> / <code>CREATE TEMPORARY LIVE VIEW</code></td><td><code>CREATE VIEW</code> / <code>CREATE TEMPORARY VIEW</code></td></tr>
</table>

<h2>3. Die drei Datensatztypen</h2>
<p>Lakeflow Declarative Pipelines unterscheidet drei Arten von Datensätzen, die jeweils für einen anderen Verarbeitungszweck gedacht sind:</p>

<h3>3.1 Streaming Table (ST)</h3>
<p>Eine <strong>Streaming Table</strong> unterstützt inkrementelle Verarbeitung und liest bei jedem Lauf ausschließlich neue Daten ein. Sie eignet sich für die Bronze- und Silver-Schicht, wo kontinuierlich neue Rohdaten eintreffen.</p>

{code('sql', '''CREATE OR REFRESH STREAMING TABLE orders_bronze
AS
SELECT *
FROM STREAM read_files(
  source_volume_path || '/orders',
  format => 'json'
);''')}

<p>Entscheidend ist das Schlüsselwort <code>STREAM</code> in der <code>FROM</code>-Klausel: Es sorgt dafür, dass Auto Loader nur die seit dem letzten Lauf neu hinzugekommenen Dateien verarbeitet, statt das gesamte Quellverzeichnis erneut zu lesen.</p>

<h3>3.2 Materialized View (MV)</h3>
<p>Eine <strong>Materialized View</strong> berechnet ihre Ergebnisse so, dass sie stets den aktuellen Stand der zugrunde liegenden Daten widerspiegeln &ndash; typischerweise für Aggregationen, Transformationen oder häufig genutzte, vorab berechnete Abfragen in der Gold-Schicht:</p>

{code('sql', '''CREATE OR REFRESH MATERIALIZED VIEW gold_orders_by_date
AS
SELECT date(order_timestamp) AS order_date, count(*) AS total_daily_orders
FROM orders_silver;''')}

<p>Wichtig: Beim Referenzieren einer Streaming Table innerhalb einer Materialized-View-Definition entfällt das <code>STREAM</code>-Schlüsselwort &ndash; die Materialized View verarbeitet grundsätzlich den vollständigen aktuellen Datenbestand der Quelle. Ein kostenbasierter Optimierer entscheidet dabei automatisch, ob ein inkrementelles Refresh oder eine vollständige Neuberechnung günstiger ist.</p>

<h3>3.3 Views (Temporary View und View)</h3>
<p>Views erzeugen keine physisch gespeicherten Daten, sondern rein logische Repräsentationen der zugrunde liegenden SQL-Abfrage. <strong>Temporary Views</strong> existieren nur für die Dauer eines Pipeline-Laufs, während <strong>Views</strong> dauerhaft in Unity Catalog registriert werden:</p>

{code('sql', '''-- Temporaer, nur waehrend des Pipeline-Laufs sichtbar
CREATE TEMPORARY VIEW orders_active AS
SELECT * FROM orders_silver WHERE notifications = 'Y';

-- Dauerhaft in Unity Catalog registriert
CREATE VIEW orders_active_view AS
SELECT * FROM orders_silver WHERE notifications = 'Y';''')}

<h2>4. Automatische Abhängigkeitsauflösung: der Pipeline-Graph</h2>
<p>Eine der wichtigsten Eigenschaften deklarativer Pipelines: Die Reihenfolge, in der Datensätze im Code definiert werden, spielt keine Rolle. Databricks erkennt automatisch, welche Tabelle von welcher anderen abhängt (etwa weil <code>orders_silver</code> auf <code>orders_bronze</code> verweist), und verbindet diese Abhängigkeiten im sogenannten <strong>Pipeline-Graph</strong>. Das erspart manuelles Abhängigkeitsmanagement und macht den Datenfluss auf einen Blick sichtbar.</p>

<figure class="img">
<img src="assets/03/declarative_pipeline_graph.png">
<figcaption>Der Pipeline-Graph verbindet Streaming Tables und Materialized Views automatisch anhand ihrer SQL-Abhängigkeiten.</figcaption>
</figure>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks hat Delta Live Tables (DLT) auf dem Data + AI Summit 2025 offiziell in <strong>Lakeflow Declarative Pipelines</strong> umbenannt und als Teil der breiteren Lakeflow-Familie positioniert (zusammen mit Lakeflow Connect für Ingestion und Lakeflow Jobs für Orchestrierung, der neuen Bezeichnung für die früheren Databricks Workflows). Bestehender DLT-Code funktioniert ohne Migration unverändert weiter. Auf Python-Seite wurde zusätzlich der neue Dekorator <code>@materialized_view</code> eingeführt, ergänzend zum bisherigen <code>@table</code>-Dekorator für Streaming Tables.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ldp/concepts/where-is-dlt">What happened to Delta Live Tables (DLT)? &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\01 Konzepte - Flows, Streaming Tables und Materialized Views.pdf",
    title="Konzepte: Flows, Streaming Tables & Materialized Views",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: Kurs 3, Kapitel 2&ndash;3",
    body_html=body,
    build_name="03_01_konzepte",
)
print("OK")
