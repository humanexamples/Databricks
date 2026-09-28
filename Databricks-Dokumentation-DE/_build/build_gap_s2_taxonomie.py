# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Die vorangegangenen Kapitel dieser Section haben einzelne Ingestion-Techniken im Detail behandelt &ndash; CTAS, COPY INTO, Auto Loader (Kapitel 1 &amp; 6) sowie Managed Connectors und Partner Connect (Kapitel 4). Dieses Kapitel liefert die <strong>übergeordnete Landkarte</strong> dazu: die offizielle Einteilung in <strong>vier Konnektortypen</strong> und <strong>drei Ingestion-Modi</strong>, wie sie auch im Exam Guide verwendet wird &ndash; inklusive einer Entscheidungsregel, wann welcher Konnektortyp sinnvoll ist.</p>

<h2>1. Vier Konnektortypen von Lakeflow Connect</h2>
<p>Lakeflow Connect gliedert sämtliche Ingestion-Wege in vier Kategorien, jede für einen anderen Anwendungsfall optimiert:</p>
<table>
<tr><th>Konnektortyp</th><th>Charakteristik</th><th>Details in</th></tr>
<tr><td><strong>Managed Connectors</strong></td><td>Out-of-the-box, low-code/no-code, für konkrete Enterprise-Quellen (Salesforce, Workday, SQL Server, &hellip;)</td><td>Kapitel 4 dieser Section</td></tr>
<tr><td><strong>Standard Connectors</strong></td><td>Anpassbar, erfordern eigenen Python-/SQL-Code (Auto Loader, COPY INTO, CTAS, Structured Streaming)</td><td>Kapitel 1 &amp; 6 dieser Section</td></tr>
<tr><td><strong>Partner Connect</strong></td><td>Drittanbieter-Dienste (z. B. Fivetran, Qlik, Informatica) für Quellen ohne eigenen Managed Connector</td><td>Kapitel 4 dieser Section</td></tr>
<tr><td><strong>Manual File Upload</strong></td><td>Lokale Dateien direkt über die Databricks-Oberfläche hochladen</td><td>siehe Abschnitt 3 unten (neu)</td></tr>
</table>

<figure class="img">
<img src="assets/s2/connector_types.png">
<figcaption>Lakeflow Connect bietet vier Konnektortypen, jeweils optimiert für unterschiedliche Quellkategorien und Ingestion-Muster.</figcaption>
</figure>

<h2>2. Drei Ingestion-Modi im Überblick</h2>
<p>Unabhängig vom gewählten Konnektortyp lässt sich jede Ingestion einem von drei Mustern zuordnen &ndash; eine Unterscheidung, die im Exam Guide explizit als &bdquo;batch, streaming, and incremental loading&ldquo; benannt wird:</p>

<h3>2.1 Batch</h3>
<p>Daten werden als abgeschlossene Charge geladen, oft zeitgesteuert &ndash; bei jedem Lauf wird der <strong>gesamte</strong> Datensatz aus der Quelle erneut verarbeitet.</p>
{code('sql', '''-- SQL: CREATE TABLE AS SELECT (CTAS)
CREATE TABLE bronze_orders AS SELECT * FROM read_files('/Volumes/.../orders', format => 'csv');''')}
{code('python', '''# Python: einmaliges Batch-Read
df = spark.read.load("/Volumes/.../orders")''')}

<figure class="img">
<img src="assets/s2/ingestion_batch.png">
<figcaption>Batch-Ingestion: Bei jedem Lauf wird der komplette Datenbestand der Quelle erneut in die Zieltabelle geladen.</figcaption>
</figure>

<h3>2.2 Incremental Batch</h3>
<p>Nur <strong>neu hinzugekommene</strong> Datensätze werden geladen, bereits verarbeitete Dateien automatisch übersprungen &ndash; schneller und ressourcenschonender als klassisches Batch.</p>
{code('sql', '''-- SQL: COPY INTO (idempotent)
COPY INTO bronze_orders FROM '/Volumes/.../orders' FILEFORMAT = CSV;''')}
{code('python', '''# Python: Spark Structured Streaming im Trigger-Modus (einmalig ausfuehren, dann stoppen)
(spark.readStream.format("cloudFiles").option("cloudFiles.format", "csv")
      .load("/Volumes/.../orders")
      .writeStream.trigger(availableNow=True)
      .toTable("bronze_orders"))''')}
<p>In Lakeflow Declarative Pipelines (SDP) entspricht dies einer Streaming Table im <strong>getriggerten Pipeline-Modus</strong> (die Pipeline läuft, verarbeitet neue Daten und stoppt wieder, statt dauerhaft zu laufen).</p>

<figure class="img">
<img src="assets/s2/ingestion_incremental_batch.png">
<figcaption>Incremental Batch: Nur die seit dem letzten Lauf neu hinzugekommenen Datensätze werden geladen, bereits verarbeitete Daten bleiben unangetastet.</figcaption>
</figure>

<h3>2.3 Streaming</h3>
<p>Daten werden <strong>kontinuierlich</strong> in sehr kurzen, häufigen Intervallen (Sekunden bis Minuten) als Micro-Batches verarbeitet &ndash; ideal für Quellen wie Apache Kafka oder Amazon Kinesis, bei denen nahezu Echtzeit-Aktualität gefragt ist.</p>
{code('python', '''# Python: Spark Structured Streaming im kontinuierlichen Modus (laeuft dauerhaft)
(spark.readStream.format("cloudFiles").option("cloudFiles.format", "json")
      .load("/Volumes/.../events")
      .writeStream.toTable("bronze_events"))''')}
<p>In SDP entspricht dies einer Streaming Table im <strong>kontinuierlichen Pipeline-Modus</strong>.</p>

<figure class="img">
<img src="assets/s2/ingestion_streaming.png">
<figcaption>Streaming-Ingestion: Daten werden fortlaufend in kleinen Micro-Batches verarbeitet, sodass sie nahezu in Echtzeit abfragbar sind.</figcaption>
</figure>

<h2>3. Manual File Upload</h2>
<p>Für einmalige, kleine Datenmengen &ndash; etwa eine lokale CSV-Datei zum Ausprobieren &ndash; lässt sich eine Datei auch ganz ohne Code direkt über die Databricks-Oberfläche hochladen. Dabei stehen zwei Ziele zur Wahl: die Datei kann direkt in eine neue <strong>Delta-Tabelle</strong> importiert werden, oder unverändert in ein <strong>Unity-Catalog-Volume</strong> abgelegt werden, um sie von dort aus z. B. per <code>read_files()</code> weiterzuverarbeiten.</p>

<h2>4. Welchen Konnektortyp wählen? Die Prioritätsregel</h2>
<p>Bei mehreren infrage kommenden Optionen empfiehlt Databricks, sich <strong>von der am stärksten verwalteten Ebene abwärts</strong> vorzuarbeiten und erst dann eine Ebene tiefer zu gehen, wenn die aktuelle Ebene die Anforderungen nicht erfüllt oder die Datenquelle nicht unterstützt:</p>
<ol>
<li><strong>Managed Connector</strong> prüfen &ndash; existiert einer für die konkrete Quelle (Salesforce, SQL Server, &hellip;)? Wenn ja, verwenden.</li>
<li><strong>Standard Connector</strong> (Auto Loader für Dateien, Structured Streaming für Kafka/Kinesis) &ndash; wenn kein Managed Connector existiert, aber die Quelle Cloud-Speicher oder ein Message-Bus ist.</li>
<li><strong>Partner Connect</strong> &ndash; wenn weder Managed noch Standard Connector die Quelle abdecken, aber ein Technologiepartner (z. B. Fivetran) dies leistet.</li>
</ol>
<p><code>COPY INTO</code> bleibt dabei als einfacher, transaktionaler Batch-Befehl vor allem für Ad-hoc-Backfills und klar abgegrenzte historische Ladevorgänge sinnvoll, während <code>CREATE STREAMING TABLE</code> mit <code>read_files()</code> für SQL-Nutzer inzwischen als die skalierbarere, empfohlene Alternative für inkrementelle Ingestion gilt.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks fasst Lakeflow Connect als dreistufiges Modell zusammen: vollständig verwaltete Connectors (Managed), Standard-Connectors für Cloud-Speicher und Message-Busse (mit Auto Loader als zentralem Baustein für Datei-Ingestion), und Partner-Lösungen als dritte Ebene. Die Empfehlung lautet ausdrücklich, zunächst die am stärksten verwaltete Ebene zu prüfen und erst bei Nichteignung eine Ebene tiefer zu gehen &ndash; genau die Priorisierungslogik, die auch der Exam Guide unter &bdquo;Prioritize between Auto Loader, Lakeflow Connect (...), and other ingestion methods&ldquo; abfragt.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ingestion/overview">What is Lakeflow Connect? &ndash; Databricks-Dokumentation</a> &middot; <a href="https://docs.databricks.com/aws/en/ldp/load">Load data in pipelines &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 2 - Data Ingestion and Loading\08 Konnektortypen und Ingestion-Modi im Ueberblick.pdf",
    title="Konnektortypen und Ingestion-Modi im Überblick",
    subtitle="Section 2 &middot; Data Ingestion and Loading &middot; Quelle: Udemy-Kursmaterial &bdquo;Lakeflow Connect&ldquo;, erg&auml;nzt mit Databricks-Dokumentation",
    body_html=body,
    build_name="gap_s2_taxonomie",
)
print("OK")
