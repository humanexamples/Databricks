# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Change Data Capture (CDC) bezeichnet die Technik, Änderungen an einer Quelle &ndash; neue, geänderte oder gelöschte Datensätze &ndash; zu erkennen und in eine Zieltabelle zu übertragen, sodass diese jederzeit den aktuellen Stand der Quelle widerspiegelt. Wie mit diesen Änderungen historisch umgegangen wird, beschreiben die sogenannten <strong>Slowly Changing Dimensions</strong> (SCD). Kapitel 5 dieser Section hat bereits SCD Type 1 mit <code>AUTO CDC INTO</code> eingeführt; dieses Kapitel vertieft den Unterschied zu <strong>SCD Type 2</strong>, bei der die vollständige Änderungshistorie erhalten bleibt, und zeigt die dafür nötige Syntax anhand einer echten Kundendaten-Pipeline.</p>

<h2>1. SCD Type 1 vs. SCD Type 2 im Vergleich</h2>
<p>Bei <strong>SCD Type 1</strong> wird eine geänderte Zeile in der Zieltabelle einfach überschrieben &ndash; es existiert zu jedem Zeitpunkt nur die aktuelle Version eines Datensatzes, frühere Zustände gehen verloren. Das ist speicherschonend und einfach, eignet sich aber nicht, wenn die Historie einer Änderung selbst von Interesse ist. <strong>SCD Type 2</strong> hingegen bewahrt bei jeder Änderung die vorherige Version als abgeschlossenen historischen Datensatz und fügt eine neue Zeile mit den aktuellen Werten hinzu. Löschungen werden dabei nicht physisch entfernt, sondern als &bdquo;Soft Delete&ldquo; markiert: Die Zeile bleibt bestehen, wird aber als inaktiv gekennzeichnet.</p>

<table>
<tr><th></th><th>SCD Type 1</th><th>SCD Type 2</th></tr>
<tr><td>Update-Verhalten</td><td>Bestehende Zeile wird überschrieben</td><td>Alte Zeile wird abgeschlossen, neue Zeile wird eingefügt</td></tr>
<tr><td>Historie</td><td>Nicht vorhanden</td><td>Vollständig nachvollziehbar</td></tr>
<tr><td>Löschungen</td><td>Zeile wird entfernt</td><td>Zeile bleibt erhalten, wird als inaktiv markiert</td></tr>
<tr><td>Speicherbedarf</td><td>Gering</td><td>Wächst mit jeder Änderung</td></tr>
<tr><td>Typischer Einsatz</td><td>Nur aktueller Stand relevant</td><td>Audit-Trails, Point-in-Time-Analysen, Compliance</td></tr>
</table>

<h2>2. AUTO CDC INTO: Syntax für SCD Type 2</h2>
<p>Für beide SCD-Varianten stellt Apache Spark Declarative Pipelines denselben deklarativen Befehl bereit: <code>AUTO CDC INTO</code> (früher <code>APPLY CHANGES INTO</code> genannt &ndash; Syntax und Funktionsweise sind identisch geblieben, nur der Name wurde aktualisiert). Anstelle einer selbst geschriebenen <code>MERGE INTO</code>-Logik übernimmt die Pipeline automatisch die korrekte Reihenfolge der Ereignisse, das Auflösen von Updates gegen Inserts sowie &ndash; bei SCD Type 2 &ndash; das Schließen und Neuanlegen von Zeilen. Der Unterschied zu SCD Type 1 liegt allein in der Klausel <code>STORED AS SCD TYPE 2</code> am Ende der Anweisung.</p>

<p>Die vollständige Pipeline aus der Demo gliedert sich in drei Schritte: Zunächst wird die Bronze-Tabelle per Auto Loader aus JSON-Dateien befüllt, anschließend eine bereinigte Zwischentabelle mit Expectations erzeugt, und erst danach greift <code>AUTO CDC INTO</code> auf dieser bereinigten Quelle:</p>

{code('sql', '''-- Schritt 1: Rohdaten inkrementell einlesen
CREATE OR REFRESH STREAMING TABLE sdp_cdc_1_bronze.customers_bronze_raw_demo
  COMMENT "Raw data from customers CDC feed"
AS
SELECT
  *,
  current_timestamp() processing_time,
  _metadata.file_name as source_file
FROM STREAM read_files(
  "${source}",
  format => "json");

-- Schritt 2: Typumwandlung und Data-Quality-Regeln auf Bronze-Ebene
CREATE STREAMING TABLE sdp_cdc_1_bronze.customers_bronze_clean_demo
  (
    CONSTRAINT valid_id EXPECT (customer_id IS NOT NULL)
      ON VIOLATION FAIL UPDATE,
    CONSTRAINT valid_operation EXPECT (operation IS NOT NULL)
      ON VIOLATION DROP ROW,
    CONSTRAINT valid_email EXPECT (
      rlike(email, '^([a-zA-Z0-9_\\\\-\\\\.]+)@([a-zA-Z0-9_\\\\-\\\\.]+)\\\\.([a-zA-Z]{2,5})$')
      OR operation = "DELETE")
      ON VIOLATION DROP ROW
  )
  COMMENT "Clean raw bronze data and apply quality constraints"
AS
SELECT
  *,
  CAST(from_unixtime(timestamp) AS timestamp) AS timestamp_datetime
FROM STREAM sdp_cdc_1_bronze.customers_bronze_raw_demo;

-- Schritt 3: SCD Type 2 mit AUTO CDC INTO
CREATE OR REFRESH STREAMING TABLE sdp_cdc_2_silver.customers_silver_scd2_demo
  COMMENT 'SCD Type 2 Historical Customer Data';

CREATE FLOW customers_scd_type_2_flow AS
AUTO CDC INTO sdp_cdc_2_silver.customers_silver_scd2_demo
FROM STREAM sdp_cdc_1_bronze.customers_bronze_clean_demo
  KEYS (customer_id)
  APPLY AS DELETE WHEN operation = "DELETE"
  SEQUENCE BY timestamp_datetime
  COLUMNS * EXCEPT (timestamp, _rescued_data, operation)
  STORED AS SCD TYPE 2;''')}

<p>Die einzelnen Klauseln übernehmen klar getrennte Aufgaben: <code>KEYS (customer_id)</code> legt fest, anhand welcher Spalte(n) Datensätze aus Quelle und Ziel einander zugeordnet werden &ndash; auch zusammengesetzte Schlüssel aus mehreren Spalten sind möglich. <code>APPLY AS DELETE WHEN operation = "DELETE"</code> definiert, welche eingehenden Zeilen als Löschvorgang statt als Update behandelt werden. <code>SEQUENCE BY timestamp_datetime</code> stellt sicher, dass Änderungen unabhängig von ihrer Ankunftsreihenfolge in der korrekt chronologischen Reihenfolge angewendet werden &ndash; entscheidend bei verspätet eintreffenden Ereignissen. <code>COLUMNS * EXCEPT (...)</code> schließt rein technische Spalten aus der Zieltabelle aus, und <code>STORED AS SCD TYPE 2</code> aktiviert schließlich die Historisierung.</p>

<h2>3. Die Metadatenspalten __START_AT und __END_AT</h2>
<p>Bei SCD Type 2 ergänzt <code>AUTO CDC INTO</code> die Zieltabelle automatisch um zwei Metadatenspalten: <code>__START_AT</code> hält fest, ab welchem Sequenzwert eine Zeile gültig war, <code>__END_AT</code> markiert das Ende dieser Gültigkeit. Ein <code>NULL</code>-Wert in <code>__END_AT</code> kennzeichnet die aktuell gültige Version eines Datensatzes; ein gesetzter Wert zeigt eine historische, nicht mehr aktive Zeile an. Bei einer Löschung wird kein neuer Datensatz angelegt &ndash; stattdessen erhält die zuletzt aktive Zeile lediglich ein <code>__END_AT</code>, während der ursprüngliche Inhalt erhalten bleibt.</p>

<figure class="img">
<img src="assets/04/scd_type2_example.png">
<figcaption>Für Kunde Peter existieren nach mehreren Adressänderungen zwei Zeilen: die historische mit gesetztem __END_AT und die aktuelle mit __END_AT = NULL. Der gelöschte Kunde Samarth bleibt als inaktive Zeile erhalten.</figcaption>
</figure>

<p>Auf dieser Grundlage lassen sich in der Gold-Schicht gezielt unterschiedliche Sichten bilden. Die folgenden zwei Materialized Views aus der Demo-Pipeline zeigen das Muster: eine View mit ausschließlich aktuell aktiven Kunden, sowie eine zweite View, die per <code>MAX_BY</code> gezielt die zuletzt aktive Version aller inzwischen gelöschten Kunden zusammenstellt:</p>

{code('sql', '''-- Aktuell aktive Kunden: __END_AT ist NULL
CREATE OR REFRESH MATERIALIZED VIEW sdp_cdc_3_gold.current_customers_gold_demo
COMMENT "Current updated list of active customers"
AS
SELECT
  * EXCEPT (processing_time),
  current_timestamp() updated_at
FROM sdp_cdc_2_silver.customers_silver_scd2_demo
WHERE `__END_AT` IS NULL;

-- Gelöschte Kunden: letzte bekannte Version je Kunde, __END_AT vorhanden
CREATE OR REFRESH MATERIALIZED VIEW sdp_cdc_3_gold.removed_customers_gold_demo AS
SELECT
  customer_id,
  MAX_BY(name, __START_AT)       AS name,
  MAX_BY(address, __START_AT)    AS address,
  MAX_BY(__START_AT, __START_AT) AS __START_AT,
  MAX_BY(__END_AT, __START_AT)   AS __END_AT
FROM sdp_cdc_2_silver.customers_silver_scd2_demo
GROUP BY customer_id
HAVING MAX_BY(__END_AT, __START_AT) IS NOT NULL;''')}

<p>Damit lässt sich mit vergleichsweise wenig Code eine vollständig historisierte Kundendimension abbilden &ndash; inklusive sauberer Trennung von aktivem Bestand und Löschhistorie, ohne dass eine einzige Zeile manueller <code>MERGE</code>-Logik geschrieben werden musste.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Die aktuelle Syntaxreferenz zu <code>AUTO CDC INTO</code> führt neben <code>STORED AS SCD TYPE 1</code> und <code>SCD TYPE 2</code> inzwischen auch die Option <code>BITEMPORAL</code> sowie zusätzliche Klauseln wie <code>IGNORE NULL UPDATES</code>, <code>APPLY AS TRUNCATE WHEN</code> und <code>TRACK HISTORY ON</code> für eine noch feinere Steuerung, welche Spalten überhaupt eine Historisierung auslösen. Für SCD-Type-2-Zieltabellen gilt außerdem: Werden <code>__START_AT</code> und <code>__END_AT</code> beim expliziten Anlegen des Tabellenschemas mit angegeben, müssen sie denselben Datentyp wie die <code>SEQUENCE BY</code>-Spalte besitzen.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-apply-changes-into">AUTO CDC INTO (pipelines) &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\08 CDC vertieft - SCD Type 1 vs Type 2 mit AUTO CDC INTO.pdf",
    title="CDC vertieft: SCD Type 1 vs. Type 2 mit AUTO CDC INTO",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: Kurs 5, Kapitel 5&ndash;6",
    body_html=body,
    build_name="04_03_cdc_scd_type2",
)
print("OK")
