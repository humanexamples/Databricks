# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Reale Pipelines bestehen selten nur aus einer einzigen Datenquelle. Häufig müssen mehrere Streams miteinander verknüpft werden &ndash; etwa Bestelldaten mit dazugehörigen Statusänderungen. Dieses Dokument behandelt die in Lakeflow Declarative Pipelines unterstützten <strong>Join-Muster für Streaming-Daten</strong> sowie den Weg von einer Entwicklungspipeline zu einem überwachten, produktiven Deployment.</p>

<h2>1. Drei Join-Muster im Überblick</h2>
<table>
<tr><th>Muster</th><th>Beschreibung</th><th>Beispiel</th></tr>
<tr><td><strong>Stream-Snapshot-Join</strong><br>(Stream-Static-Join)</td><td>Eine Streaming Table wird mit einer statischen Referenztabelle verknüpft; nur die neuen Zeilen des Streams werden verarbeitet, dabei aber gegen den <em>vollständigen</em> aktuellen Stand der statischen Tabelle geprüft.</td><td>Länder-Codes einer Transaktionsstream mit einer statischen Länder-Nachschlagetabelle anreichern</td></tr>
<tr><td><strong>Join zweier Streaming Tables über eine Materialized View</strong></td><td>Beide Seiten ändern sich kontinuierlich; bei jedem Pipeline-Lauf werden alle Zeilen beider Tabellen erneut verknüpft, mit Optimierungen wo möglich.</td><td>Kundenaktivität mit Produktkatalog-Updates zusammenführen</td></tr>
<tr><td><strong>Stream-Stream-Join</strong></td><td>Inkrementeller Join zweier Streams, bei dem nur neu eintreffende Daten aus beiden Seiten verglichen werden; erfordert Windowing/Watermarking und liegt außerhalb des Kursumfangs.</td><td>Clickstream-Daten mit Echtzeit-Ad-Impressions zeitlich korrelieren</td></tr>
</table>

<h2>2. Stream-Snapshot-Join im Detail</h2>
<p>Bei diesem Muster wird jede neu ankommende Zeile der Streaming Table gegen den <em>kompletten</em> Bestand der statischen Tabelle geprüft &ndash; das Ergebnis wird an die Ziel-Streaming-Table angehängt. Da nur eine Seite (der Stream) sich verändert, ist dieser Join effizient und zuverlässig: Die statische Tabelle muss nicht neu verarbeitet werden, nur die eingehenden Stream-Daten werden ausgewertet.</p>

<h2>3. Join zweier Streaming Tables mit einer Materialized View</h2>
<p>Sollen zwei sich kontinuierlich ändernde Streaming Tables verknüpft werden, reicht ein einfacher Stream-Snapshot-Join nicht mehr aus &ndash; hierfür kommt eine <strong>Materialized View</strong> zum Einsatz. Sie führt bei jedem Lauf einen vollständigen Inner Join über beide Quellen aus und nutzt dabei, wo möglich, inkrementelles Refresh, um unnötige Neuberechnung zu vermeiden:</p>

{code('sql', '''-- Zwei Streaming Tables ueber eine Materialized View verknuepfen
CREATE OR REFRESH MATERIALIZED VIEW full_order_info_gold
  COMMENT "Bestellungen verknuepft mit ihrem Status-Verlauf"
  TBLPROPERTIES ("quality" = "gold")
AS
SELECT o.order_id,
       o.order_timestamp,
       s.order_status,
       s.order_status_timestamp
FROM orders_silver o
INNER JOIN status_silver s
  ON o.order_id = s.order_id;

-- Darauf aufbauende, gefilterte Gold-Sichten
CREATE OR REFRESH MATERIALIZED VIEW cancelled_orders_gold
AS
SELECT *, datediff(order_status_timestamp, order_timestamp) AS days_to_cancel
FROM full_order_info_gold
WHERE order_status = 'canceled';''')}

<p>Beachten Sie: Beim Referenzieren der beiden Streaming Tables (<code>orders_silver</code>, <code>status_silver</code>) innerhalb der Materialized-View-Definition entfällt das <code>STREAM</code>-Schlüsselwort &ndash; die View verarbeitet grundsätzlich den kompletten aktuellen Datenbestand beider Quellen.</p>

<figure class="img">
<img src="assets/03/stream_stream_joins.png">
<figcaption>Je nach Kombination aus statischer und streamender Quelle eignet sich ein anderes Join-Muster.</figcaption>
</figure>

<h2>4. Von der Entwicklung in die Produktion</h2>
<p>Der Übergang einer Pipeline in den produktiven Betrieb umfasst vier zentrale operative Aufgaben:</p>
<ul>
<li><strong>Dokumentation</strong> &ndash; <code>COMMENT</code> und <code>TBLPROPERTIES</code> für jeden Datensatz erleichtern das Verständnis in Unity Catalog, etwa <code>"quality" = "bronze"</code> zur Kennzeichnung der Medaillon-Schicht oder <code>"pipelines.reset.allowed" = false</code>, um versehentliche vollständige Refreshes und den damit verbundenen Verlust von Checkpoints zu verhindern.</li>
<li><strong>Scheduling</strong> &ndash; die Pipeline wird entweder im <strong>Triggered-Modus</strong> (läuft nach Zeitplan, verarbeitet inkrementell) oder im <strong>Continuous-Modus</strong> (dauerhaft aktiv) betrieben.</li>
<li><strong>Benachrichtigungen</strong> &ndash; E-Mail-Alarme lassen sich für Start, Erfolg und Fehlschlag konfigurieren.</li>
<li><strong>Monitoring über das Event-Log</strong> &ndash; jeder Lauf schreibt detaillierte Ereignisdaten in eine (standardmäßig versteckte) Delta-Tabelle.</li>
</ul>

{code('sql', '''-- Grundstruktur des Pipeline-Event-Logs abfragen
SELECT id, event_type, details,
       details:flow_progress,
       details:user_action
FROM sdp_1_bronze.event_log_demo10;''')}

<p>Ein besonders nützlicher Anwendungsfall des Event-Logs ist die Analyse von Datenqualitäts-Metriken über mehrere Läufe hinweg: Die JSON-Struktur im Feld <code>details</code> lässt sich mit <code>from_json</code> und <code>explode</code> in tabellarische Form bringen, um pro Constraint bestandene und fehlgeschlagene Datensätze zu aggregieren.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks empfiehlt, Pipeline-Quellcode konsequent zu versionieren und für das Deployment über Umgebungen hinweg <strong>Databricks Asset Bundles</strong> (deklarative YAML-Konfiguration neben dem Quellcode) einzusetzen; über die <code>databricks bundle</code>-CLI lassen sich Pipelines validieren, deployen und ausführen. Beim Stream-Snapshot-Join gilt zudem: Werden Datensätze in der statischen Tabelle nachträglich geändert, nachdem der entsprechende Stream-Datensatz bereits verarbeitet wurde, wirken sich diese Änderungen erst nach einem vollständigen Refresh aus &ndash; nicht automatisch rückwirkend.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ldp/best-practices">Best practices for Lakeflow pipelines &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\04 Streaming Joins und Produktivbetrieb.pdf",
    title="Streaming Joins & Produktivbetrieb",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: Kurs 3, Kapitel 9&ndash;10",
    body_html=body,
    build_name="03_04_streaming_joins",
)
print("OK")
