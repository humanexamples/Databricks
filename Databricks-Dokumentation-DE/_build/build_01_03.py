# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>CSV und JSON sind die beiden häufigsten Rohdatenformate beim Einstieg in die Bronze-Schicht. Beide werden über dieselbe Funktion &ndash; <code>read_files()</code> &ndash; eingelesen, unterscheiden sich aber deutlich in ihren Eigenheiten: CSV ist flach und trennzeichenbasiert, bringt aber kein eingebettetes Schema mit; JSON ist von Natur aus verschachtelt und erfordert eigene Techniken, um aus <em>semi-strukturierten</em> Daten <em>strukturierte</em> Spalten zu machen.</p>

<h2>1. CSV-Dateien korrekt einlesen</h2>
<p>CSV-Dateien (Comma-Separated Values) speichern Daten zeilenweise als Text, wobei Werte durch ein Trennzeichen &ndash; meist Komma, häufig aber auch Semikolon, Tabulator oder Pipe (<code>|</code>) &ndash; getrennt sind. Ruft man <code>read_files()</code> ohne weitere Optionen auf, geht die Funktion von den Standardeinstellungen aus (Komma als Trennzeichen, keine Kopfzeile) &ndash; bei abweichend formatierten Dateien liefert das dann falsch aufgeteilte oder falsch benannte Spalten. Deshalb müssen die tatsächlichen Formateigenschaften der Quelle explizit als Optionen übergeben werden:</p>

{code('sql', '''-- Ohne Optionen: Spalten werden nicht korrekt erkannt
SELECT *
FROM read_files(
  "/Volumes/dbacademy_ecommerce/v01/raw/sales-csv",
  format => "csv"
)
LIMIT 5;

-- Mit den passenden Optionen für diese Quelle
SELECT *
FROM read_files(
  "/Volumes/dbacademy_ecommerce/v01/raw/sales-csv",
  format => "csv",
  sep    => "|",     -- Spaltentrennzeichen (Standard: ",")
  header => true      -- erste Zeile enthält die Spaltennamen
)
LIMIT 5;''')}

<p>Wichtige weitere Optionen von <code>read_files()</code> für CSV sind u. a. <code>encoding</code> (Zeichensatz der Datei, z. B. <code>UTF-8</code> oder <code>ISO-8859-1</code>), <code>quote</code> und <code>escape</code> (Behandlung von in Werten enthaltenen Trennzeichen) sowie <code>schema</code>, um die automatische Schema-Ableitung zu umgehen. Letzteres lohnt sich fast immer im produktiven Einsatz: Ohne explizites Schema muss Databricks zunächst einen repräsentativen Teil aller Dateien lesen, um ein gemeinsames Schema zu bestimmen &ndash; das kostet Zeit und kann bei uneinheitlichen Quelldateien zu unerwarteten Typen führen. Ein festes Schema ist außerdem Voraussetzung dafür, dass Schema-Abweichungen zuverlässig in der <code>_rescued_data</code>-Spalte landen (siehe vorheriges Kapitel dieses Themenordners):</p>

{code('sql', '''SELECT *
FROM read_files(
  '/Volumes/dbacademy/ops/labuser/csv_demo_files/malformed_example_1_data.csv',
  format => "csv",
  sep    => "|",
  header => true,
  schema => \'\'\'
      order_id INT,
      email STRING,
      transactions_timestamp BIGINT\'\'\',
  rescuedDataColumn => "_rescued_data"
);''')}

<h2>2. JSON: von der verschachtelten Struktur zur Spalte</h2>
<p>JSON-Daten bestehen aus Objekten in geschweiften Klammern mit Schlüssel-Wert-Paaren; Werte können wiederum Zeichenketten, Zahlen, boolesche Werte, verschachtelte Objekte oder Arrays sein. Genau diese Verschachtelung macht JSON flexibel, aber auch komplexer zu verarbeiten als ein flaches CSV. Databricks bietet für JSON-formatierte Spalten drei grundsätzliche Ansätze:</p>
<table>
<tr><th>Ansatz</th><th>Eigenschaft</th></tr>
<tr><td><strong>STRING</strong></td><td>JSON bleibt als reiner Text gespeichert; flexibel, aber langsam bei Abfragen, kein erzwungenes Schema.</td></tr>
<tr><td><strong>STRUCT</strong></td><td>JSON wird anhand eines definierten Schemas in typisierte, verschachtelte Spalten geparst; erzwingt Konsistenz und ist deutlich performanter.</td></tr>
<tr><td><strong>VARIANT</strong></td><td>Neuerer, offener Datentyp für semi-strukturierte Daten; kombiniert die Flexibilität von STRING mit einer Performance nahe an STRUCT, ohne starres Schema vorauszusetzen.</td></tr>
</table>

<h3>2.1 JSON-Werte direkt aus einer STRING-Spalte extrahieren</h3>
<p>Mit der Doppelpunkt-Syntax <code>spalte:feld</code> lassen sich einzelne Felder direkt aus einer JSON-formatierten Textspalte auslesen &ndash; auch verschachtelt, mit Punkt- oder Klammer-Notation. Das ist der einfachste Einstieg, eignet sich aber vor allem für Ad-hoc-Abfragen, nicht für performancekritische, wiederkehrende Verarbeitung:</p>

{code('sql', '''SELECT
  decoded_value,
  decoded_value:device,
  decoded_value:traffic_source,
  decoded_value:geo,     -- enthält selbst wieder einen JSON-String
  decoded_value:items    -- enthält ein verschachteltes Array von JSON-Objekten
FROM kafka_events_bronze_decoded
LIMIT 5;''')}

<h3>2.2 JSON in eine typisierte STRUCT-Spalte umwandeln</h3>
<p>Für wiederkehrende, performancekritische Verarbeitung empfiehlt sich die Umwandlung in eine <code>STRUCT</code>-Spalte. Der Weg dahin führt über zwei Funktionen: <code>schema_of_json()</code> leitet aus einem Beispiel-String automatisch das passende Schema ab, <code>from_json()</code> wendet dieses Schema anschließend auf die gesamte Spalte an und erzeugt eine typisierte STRUCT-Spalte mit verschachtelten Feldern und Arrays:</p>

{code('sql', '''-- Schritt 1: Schema aus einem Beispielwert ableiten
SELECT schema_of_json(
  '{"device":"Linux","ecommerce":{"purchase_revenue_in_usd":1075.5},"geo":{"city":"Houston","state":"TX"}}'
) AS schema;

-- Schritt 2: Schema mit from_json() anwenden
CREATE OR REPLACE TABLE kafka_events_bronze_struct AS
SELECT
  * EXCEPT (decoded_value),
  from_json(
    decoded_value,
    'STRUCT<device: STRING, ecommerce: STRUCT<purchase_revenue_in_usd: DOUBLE, total_item_quantity: BIGINT>,
             geo: STRUCT<city: STRING, state: STRING>,
             items: ARRAY<STRUCT<item_id: STRING, item_name: STRING, price_in_usd: DOUBLE, quantity: BIGINT>>,
             traffic_source: STRING, user_id: STRING>'
  ) AS value
FROM kafka_events_bronze_decoded;

-- Zugriff auf Felder, verschachtelte Felder und Arrays per Punktnotation
SELECT
  value.device                    AS device,
  value.geo.city                  AS city,
  value.items,
  array_size(value.items)         AS anzahl_items
FROM kafka_events_bronze_struct;''')}

<p>Enthält eine Zeile ein Array mit mehreren Elementen (z. B. mehrere gekaufte Artikel pro Bestellung), lässt sich dieses Array mit <code>explode()</code> in einzelne Zeilen auflösen &ndash; eine Zeile pro Array-Element. Ist der Array-Wert <code>NULL</code>, erzeugt <code>explode()</code> dafür keine Zeile; soll trotzdem eine Zeile mit <code>NULL</code>-Werten erhalten bleiben, verwendet man stattdessen <code>explode_outer()</code>.</p>

{code('sql', '''SELECT
  decoded_key,
  array_size(value.items) AS anzahl_items,
  explode(value.items)    AS einzelnes_item
FROM kafka_events_bronze_struct;''')}

<h3>2.3 Sonderfall: Base64-kodierte Felder (z. B. Kafka-Events)</h3>
<p>Bei Ereignisdaten aus Message-Bussen wie Kafka sind Schlüssel- und Wertfelder häufig Base64-kodiert, um Sonderzeichen und Formatierung beim Transport nicht zu beschädigen. Vor dem eigentlichen JSON-Parsing muss dieser Wert daher zunächst dekodiert werden &ndash; mit <code>unbase64()</code> in einen Binärwert und anschließend mit <code>CAST</code> in einen lesbaren String:</p>

{code('sql', '''CREATE OR REPLACE TABLE kafka_events_bronze_decoded AS
SELECT
  cast(unbase64(key)   AS STRING) AS decoded_key,
  offset, partition, timestamp, topic,
  cast(unbase64(value) AS STRING) AS decoded_value   -- jetzt ein lesbarer JSON-String
FROM kafka_events_bronze_raw;''')}

<h3>2.4 Ausblick: der VARIANT-Datentyp</h3>
<p>Als dritte, neuere Alternative bietet Databricks den offenen <strong>VARIANT</strong>-Datentyp an. Er speichert beliebig strukturierte semi-strukturierte Daten ohne starres Schema, bietet dabei aber ein deutlich besseres Abfrageverhalten als eine reine STRING-Spalte. Mit <code>parse_json()</code> wird eine JSON-Spalte in VARIANT umgewandelt, der Zugriff erfolgt anschließend wie gewohnt über die Doppelpunkt-Syntax:</p>

{code('sql', '''CREATE OR REPLACE TABLE kafka_events_bronze_variant AS
SELECT
  decoded_key, offset, partition, timestamp, topic,
  parse_json(decoded_value) AS json_variant_value
FROM kafka_events_bronze_decoded;

SELECT
  json_variant_value:device :: STRING,
  json_variant_value:items
FROM kafka_events_bronze_variant;''')}

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> <code>read_files()</code> ist die empfohlene, formatunabhängige Tabellenfunktion zum Einlesen von CSV, JSON, XML, TEXT, PARQUET, AVRO, ORC und Binärdateien; die konkreten Optionsnamen für jedes Format (z. B. <code>sep</code>, <code>header</code>, <code>encoding</code>, <code>quote</code>, <code>escape</code> bei CSV, <code>multiLine</code> bei JSON) entsprechen dabei den bekannten <code>DataFrameReader</code>-Optionen von Apache Spark. Der VARIANT-Datentyp, der in diesem Kurs noch als Public Preview beschrieben wird, ist inzwischen für die meisten Compute-Typen allgemein verfügbar (GA) und gilt bei neuen JSON-lastigen Ingestion-Pipelines zunehmend als bevorzugte Alternative zu manuell definierten STRUCT-Schemas, insbesondere wenn sich die Struktur der Quelldaten häufig ändert.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files">read_files table-valued function &ndash; Databricks-Dokumentation</a>, <a href="https://docs.databricks.com/aws/en/query/formats/json">Read and write JSON files &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 2 - Data Ingestion and Loading\03 Strukturierte und halbstrukturierte Daten laden (CSV, JSON).pdf",
    title="Strukturierte & halbstrukturierte Daten laden (CSV, JSON)",
    subtitle="Section 2 &middot; Data Ingestion and Loading &middot; Quelle: Kurs 1, Kapitel 10&ndash;13",
    body_html=body,
    build_name="01_03_csv_json",
)
print("OK")
