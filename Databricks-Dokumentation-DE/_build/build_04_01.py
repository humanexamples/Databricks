# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Bisher kannte man aus den Grundlagen einer Lakeflow Declarative Pipeline vor allem den einfachen Fall: Eine Streaming Table oder Materialized View wird mit genau einer <code>SELECT</code>-Abfrage aus genau einer Quelle befüllt. Sobald mehrere Quellen in ein gemeinsames Ziel einfließen sollen &ndash; etwa Bestelldaten dreier Tochtergesellschaften, die jeweils in unterschiedlichen Formaten abgelegt werden &ndash; reicht dieses einfache Modell nicht mehr aus. Genau hier setzt das Konzept des <strong>Flows</strong> an, das in fortgeschrittenen Pipelines zum zentralen Baustein wird.</p>

<h2>1. Flow = Query + Target</h2>
<p>Ein <strong>Flow</strong> ist die kleinste Ausführungseinheit einer Deklarativen Pipeline. Er besteht immer aus zwei Teilen: einer <strong>Query</strong> (der SQL- oder DataFrame-Logik, die bestimmt, welche Daten gelesen und wie sie transformiert werden) und einem <strong>Target</strong> (der Streaming Table oder Materialized View, in die das Ergebnis geschrieben wird). Jeder Flow verwaltet dabei seinen eigenen <strong>Checkpoint</strong>, über den der Fortschritt der inkrementellen Verarbeitung nachverfolgt wird. Wird ein Flow umbenannt, verliert er seinen Checkpoint und beginnt beim nächsten Lauf wieder von vorne &ndash; ein Detail, das bei Refactorings leicht übersehen wird, aber in der Produktion teuer werden kann.</p>

<p>Meistens entsteht ein Flow implizit, sobald eine Streaming Table oder Materialized View definiert wird &ndash; man spricht dann von einem <strong>Default Flow</strong>, der automatisch den Namen seiner Zieltabelle erbt. Wird hingegen zusätzlicher Schreibzugriff auf eine bereits bestehende Tabelle benötigt, etwa weil eine zweite Quelle angebunden werden soll, definiert man einen <strong>expliziten Flow</strong> separat mit <code>CREATE FLOW</code>. Beide Varianten laufen unabhängig voneinander: Ein langsamer oder fehlgeschlagener Flow beeinflusst die übrigen Flows im selben Pipeline-Lauf nicht.</p>

{code('sql', '''-- Default Flow: Tabelle und Flow entstehen in einem Schritt
CREATE OR REFRESH STREAMING TABLE target_table
AS SELECT * FROM STREAM source_table;

-- Expliziter Flow: Tabelle wird separat definiert,
-- der Flow schreibt anschließend gezielt hinein
CREATE OR REFRESH STREAMING TABLE target_table;

CREATE FLOW my_flow
AS INSERT INTO target_table BY NAME
SELECT * FROM STREAM source_table;''')}

<h2>2. Das Multi-Flow-Muster: mehrere Quellen, ein Ziel</h2>
<p>Sollen mehrere Datenquellen in dieselbe Tabelle einfließen, lassen sich beliebig viele explizite Flows auf dasselbe Target richten. Jeder Flow liest unabhängig von seiner eigenen Quelle, verarbeitet die Daten und hängt sie an die gemeinsame Zieltabelle an. Das folgende Beispiel aus der Demo-Pipeline zeigt drei Tochtergesellschaften (Bright Home, Lumina Sports, Northstar Outfitters), die jeweils eigene CSV- bzw. JSON-Dateien liefern, aber gemeinsam in eine einzige Bronze-Tabelle einfließen:</p>

{code('sql', '''CREATE OR REPLACE STREAMING TABLE multi_flow_1_bronze.orders_bronze_flows_demo
(
  subsidiary_id   STRING,
  order_id        STRING,
  order_timestamp STRING,
  customer_id     STRING,
  region          STRING,
  country         STRING,
  city            STRING,
  channel         STRING,
  sku             STRING,
  category        STRING,
  qty             STRING,
  unit_price      STRING,
  discount_pct    STRING,
  coupon_code     STRING,
  total_amount    STRING,
  order_date      STRING,
  source_file     STRING,
  file_mod_time   TIMESTAMP
)
COMMENT "Creates a single bronze streaming table with orders from all subsidiaries using multiple flows."
TBLPROPERTIES (
  'pipelines.reset.allowed' = false
);

-- Flow 1: liest CSV-Dateien der Bright-Home-Volume
CREATE FLOW bright_home_orders_flow
AS INSERT INTO multi_flow_1_bronze.orders_bronze_flows_demo BY NAME
SELECT
  CAST(subsidiary_id AS STRING) AS subsidiary_id,
  CAST(order_id AS STRING) AS order_id,
  -- ... weitere Spalten, alle als STRING gecastet ...
  _metadata.file_name AS source_file,
  _metadata.file_modification_time AS file_mod_time
FROM STREAM read_files(
    '${bright_home_orders_source}',
    format => 'csv',
    header => true
);

-- Flow 2: liest CSV-Dateien der Lumina-Sports-Volume (identisches Zielschema)
CREATE FLOW lumina_sports_orders_flow
AS INSERT INTO multi_flow_1_bronze.orders_bronze_flows_demo BY NAME
SELECT ... FROM STREAM read_files('${lumina_sports_orders_source}', format => 'csv', header => true);

-- Flow 3: liest JSON-Dateien der Northstar-Outfitters-Volume
CREATE FLOW northstar_outfitters_orders_flow
AS INSERT INTO multi_flow_1_bronze.orders_bronze_flows_demo BY NAME
SELECT ... FROM STREAM read_files('${northstar_outfitters_orders_source}', format => 'json');''')}

<p>Bemerkenswert ist die Tabelleneigenschaft <code>'pipelines.reset.allowed' = false</code>: Sie verhindert, dass ein versehentlicher Full Refresh die gesamte Bronze-Tabelle löscht &ndash; wichtig, weil hier Daten aus drei unabhängigen Quellen zusammenlaufen, die im Zweifel einzeln neu geladen werden müssten. Alle drei Flows casten sämtliche Geschäftsspalten konsequent auf <code>STRING</code>, damit unterschiedliche Quellformate keine Typkonflikte erzeugen &ndash; die eigentliche Typisierung erfolgt erst später in der Silver-Schicht.</p>

<figure class="img">
<img src="assets/04/multi_flow_pipeline_overview.png">
<figcaption>Drei unabhängige Flows schreiben aus unterschiedlichen Quell-Volumes in dieselbe Bronze-Tabelle; erst danach folgen Liquid Clustering in der Silver-Schicht und aggregierende Gold-Materialized-Views.</figcaption>
</figure>

<h2>3. Warum Multi-Flow und nicht UNION?</h2>
<p>Eine naheliegende Alternative wäre, die drei Quellen einfach per <code>UNION ALL</code> innerhalb einer einzigen Streaming-Table-Definition zusammenzuführen. Für inkrementelle Pipelines bringt das jedoch entscheidende Nachteile mit sich: Alle Quellen teilen sich dann einen einzigen Checkpoint, sodass das Hinzufügen einer vierten Tochtergesellschaft einen kompletten Full Refresh der gesamten Tabelle erzwingt. Zudem kann ein Fehler in einer Quelle den gesamten Ladevorgang blockieren, und die Nachverfolgung, welche Zeile aus welcher Quelle stammt, wird unübersichtlich. Das Multi-Flow-Muster löst all diese Probleme: Jeder Flow besitzt einen eigenen Checkpoint, neue Quellen lassen sich ohne Neuverarbeitung der Historie ergänzen, und Fehler bleiben auf den jeweiligen Flow beschränkt. Aus diesem Grund gilt Multi-Flow bei mehreren Quellen mit identischem Zielschema als die empfohlene Vorgehensweise gegenüber <code>UNION</code>.</p>

<p>Eine wichtige Einschränkung dabei: <strong>Data-Quality-Expectations</strong> (siehe Kapitel 3 und Kapitel 9 dieser Section) lassen sich nicht auf einzelnen Flows definieren, sondern ausschließlich auf der Zieltabelle selbst. Dadurch gelten dieselben Qualitätsregeln automatisch für alle Flows, die in diese Tabelle schreiben &ndash; unabhängig davon, aus welcher Quelle die jeweilige Zeile stammt.</p>

<h2>4. Liquid Clustering im Pipeline-Kontext</h2>
<p>Nachdem die Bronze-Tabelle die Rohdaten aus allen Flows vereint, folgt in der Silver-Schicht typischerweise eine Bereinigung samt Typisierung. An dieser Stelle lohnt sich häufig auch die Aktivierung von <strong>Liquid Clustering</strong> &ndash; dem modernen Nachfolger von Hive-Partitionierung und Z-Ordering, der in Section 6 (Troubleshooting, Monitoring and Optimization) ausführlich behandelt wird. Im Pipeline-Kontext genügt die Klausel <code>CLUSTER BY AUTO</code> direkt in der Tabellendefinition, damit Databricks anhand der tatsächlichen Abfragemuster selbstständig geeignete Clustering-Spalten wählt und die Datenlayout-Optimierung inkrementell im Hintergrund ausführt &ndash; ganz ohne manuelles <code>OPTIMIZE</code>.</p>

{code('sql', '''CREATE OR REFRESH STREAMING TABLE multi_flow_2_silver.orders_silver_flows_demo
(
  subsidiary_id   STRING,
  order_id        STRING,
  order_timestamp TIMESTAMP,
  order_date      DATE,
  -- ... weitere Spalten ...
  CONSTRAINT qty_valid          EXPECT (qty >= 0) ON VIOLATION DROP ROW,
  CONSTRAINT total_amount_valid EXPECT (total_amount >= 0) ON VIOLATION DROP ROW,
  CONSTRAINT timestamp_not_null EXPECT (order_timestamp IS NOT NULL) ON VIOLATION FAIL UPDATE
)
COMMENT 'Clean and standardize data from the multiple-flow bronze table'

-- Liquid Clustering: Databricks wählt die Clustering-Spalten selbst
CLUSTER BY AUTO

AS
SELECT
  subsidiary_id,
  order_id,
  TRY_CAST(order_timestamp AS TIMESTAMP) AS order_timestamp,
  TRY_CAST(order_date      AS DATE)      AS order_date,
  -- ... TRY_CAST für alle numerischen Spalten ...
FROM STREAM multi_flow_1_bronze.orders_bronze_flows_demo;''')}

<p>Alternativ lassen sich mit <code>CLUSTER BY (spalte1, spalte2)</code> auch explizite Clustering-Schlüssel angeben, wenn die typischen Filterspalten bereits bekannt sind &ndash; etwa <code>region</code> und <code>order_date</code> bei regelmäßigen Auswertungen nach Zeitraum und Vertriebsregion. Ein Hybrid ist ebenfalls möglich: explizite Spalten als Startpunkt, während <code>clusterByAuto</code> zusätzlich aktiviert bleibt, damit sich das Layout mit der Zeit weiterentwickelt.</p>

<table>
<tr><th>Ansatz</th><th>Wann sinnvoll</th></tr>
<tr><td><code>CLUSTER BY AUTO</code></td><td>Neue Tabellen oder unklare Abfragemuster &ndash; Databricks lernt aus der Query-Historie</td></tr>
<tr><td><code>CLUSTER BY (spalten)</code></td><td>Bekannte, stabile Filterspalten &ndash; volle Kontrolle über das Datenlayout</td></tr>
<tr><td>Hive-Partitionierung (Legacy)</td><td>Nur noch für Sonderfälle wie DSGVO-Löschungen relevant, siehe Section 6</td></tr>
</table>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Automatic Liquid Clustering wird inzwischen sowohl für Materialized Views als auch für Streaming Tables in Lakeflow Declarative Pipelines unterstützt. Databricks analysiert dabei die tatsächliche Abfrage-Historie einer Tabelle, um passende Clustering-Spalten vorzuschlagen, passt die Auswahl bei sich ändernden Zugriffsmustern automatisch an und ändert die Schlüssel nur dann, wenn der erwartete Performance-Gewinn die Kosten der Neusortierung übersteigt. Voraussetzung für die automatische Schlüsselwahl ist, dass Predictive Optimization für die Tabelle aktiviert ist; Clustering-Vorgänge laufen dabei grundsätzlich asynchron im Hintergrund.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/tables/clustering">Use liquid clustering for tables &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\06 Multi-Flow-Pipelines und Liquid Clustering.pdf",
    title="Multi-Flow-Pipelines & Liquid Clustering",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: Kurs 5, Kapitel 1&ndash;2",
    body_html=body,
    build_name="04_01_multi_flow_liquid_clustering",
)
print("OK")
