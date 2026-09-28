# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Bevor Daten in Databricks analysiert, transformiert oder in Pipelines verarbeitet werden können, müssen sie zunächst aus einer Quelle &ndash; etwa Cloud-Speicher, Datenbanken oder SaaS-Anwendungen &ndash; in eine Delta-Tabelle geladen werden. Dieser Vorgang wird als <strong>Ingestion</strong> (Datenaufnahme) bezeichnet und ist der erste Schritt der sogenannten <em>Medallion-Architektur</em> (Bronze &rarr; Silver &rarr; Gold). Databricks bietet dafür mehrere Methoden an, die sich vor allem darin unterscheiden, ob Daten <strong>einmalig/batchweise</strong> oder <strong>inkrementell/kontinuierlich</strong> geladen werden sollen.</p>

<figure class="img">
<img src="assets/01/cloud-storage.png">
<figcaption>Rohdaten liegen typischerweise als Dateien (CSV, JSON, Parquet, &hellip;) in einem Cloud-Speicher oder einem Unity-Catalog-Volume.</figcaption>
</figure>

<h2>1. Einmalige Batch-Ingestion mit CTAS und read_files()</h2>
<p>Die einfachste Methode ist die <code>CREATE TABLE AS</code>-Anweisung (kurz <strong>CTAS</strong>) in Kombination mit der Tabellenfunktion <code>read_files()</code>. Damit lässt sich eine Delta-Tabelle in einem einzigen Schritt anlegen und mit dem Ergebnis einer Abfrage befüllen. Die Funktion <code>read_files()</code> erkennt das Dateiformat automatisch, leitet das Schema aus Metadaten ab (bei Parquet sehr zuverlässig, da das Schema in der Datei eingebettet ist) und bietet zusätzliche Optionen wie <code>schemaHints</code> für Sonderfälle.</p>

{code('sql', '''-- Vorschau der Rohdaten direkt aus dem Volume abfragen
SELECT *
FROM read_files(
  '/Volumes/dbacademy_ecommerce/v01/raw/users-historical',
  format => 'parquet'
)
LIMIT 10;

-- Delta-Tabelle mit CTAS erzeugen und befüllen
CREATE TABLE historical_users_bronze_ctas_rf
SELECT *
FROM read_files(
        '/Volumes/dbacademy_ecommerce/v01/raw/users-historical',
        format => 'parquet'
      );''')}

<p>Mit <code>DESCRIBE TABLE EXTENDED</code> lässt sich anschließend prüfen, dass es sich um eine <strong>Managed Table</strong> handelt: Databricks verwaltet dabei sowohl die Metadaten als auch die zugrunde liegenden Daten. Wird eine solche Tabelle gelöscht, werden auch die Daten entfernt &ndash; im Gegensatz zu <strong>External Tables</strong>, bei denen Databricks nur die Metadaten verwaltet und die Daten unabhängig von der Tabelle bestehen bleiben.</p>

<h2>2. Inkrementelle Batch-Ingestion mit COPY INTO</h2>
<p><code>COPY INTO</code> ist ein SQL-Befehl, der Daten aus einem Dateipfad in eine bestehende Delta-Tabelle lädt. Der wichtigste Unterschied zu CTAS: <code>COPY INTO</code> ist <strong>idempotent</strong> &ndash; bereits geladene Dateien werden bei einem erneuten Aufruf automatisch übersprungen. Damit eignet sich der Befehl gut für wiederkehrende, geplante Batch-Jobs, die neu hinzugekommene Dateien laden sollen, ohne den gesamten Datenbestand neu einzulesen.</p>

{code('sql', '''-- Tabelle mit COPY_OPTIONS für automatische Schema-Evolution befüllen
CREATE TABLE historical_users_bronze_ci_no_schema;

COPY INTO historical_users_bronze_ci_no_schema
  FROM '/Volumes/dbacademy_ecommerce/v01/raw/users-historical'
  FILEFORMAT = parquet
  COPY_OPTIONS ('mergeSchema' = 'true');

-- Erneuter Aufruf: bereits geladene Dateien werden übersprungen
-- (num_affected_rows = 0, da keine neuen Dateien vorhanden sind)
COPY INTO historical_users_bronze_ci_no_schema
  FROM '/Volumes/dbacademy_ecommerce/v01/raw/users-historical'
  FILEFORMAT = parquet
  COPY_OPTIONS ('mergeSchema' = 'true');''')}

<p>Ohne die Option <code>mergeSchema&nbsp;=&nbsp;true</code> schlägt <code>COPY INTO</code> fehl, sobald die Quelldateien mehr Spalten enthalten als die Zieltabelle (Fehler <code>COPY_INTO_SCHEMA_MISMATCH_WITH_TARGET_TABLE</code>). Die Option erlaubt es, das Tabellenschema automatisch um neue Spalten zu erweitern.</p>

<h2>3. Kontinuierliche Ingestion mit Streaming Tables und Auto Loader</h2>
<p>Für Quellen, die fortlaufend neue Dateien erhalten (z. B. Log-Dateien, Exporte aus vorgelagerten Systemen), empfiehlt Databricks <strong>Streaming Tables</strong> in Kombination mit <strong>Auto&nbsp;Loader</strong>. Auto Loader überwacht ein Verzeichnis effizient auf neue Dateien und verarbeitet nur die seit dem letzten Lauf hinzugekommenen Daten &ndash; ohne das gesamte Verzeichnis erneut auflisten zu müssen. In SQL wird Auto Loader über <code>STREAM read_files(...)</code> innerhalb einer <code>CREATE OR REFRESH STREAMING TABLE</code>-Anweisung aktiviert.</p>

{code('sql', '''CREATE OR REFRESH STREAMING TABLE sql_csv_autoloader
SCHEDULE EVERY 1 WEEK        -- automatische, periodische Aktualisierung (optional)
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/dbacademy/<schema>/csv_files_autoloader_source',
  format => 'CSV',
  sep => '|',
  header => true
);

-- Tabelle manuell aktualisieren (neue Dateien seit dem letzten Lauf laden)
REFRESH STREAMING TABLE sql_csv_autoloader;

-- Verlauf der Aktualisierungen einsehen
DESCRIBE HISTORY sql_csv_autoloader;''')}

<p>Jeder <code>REFRESH</code>-Vorgang wird als eigene Version in der Tabellenhistorie protokolliert, sodass sich jederzeit nachvollziehen lässt, wann welche Datenmenge geladen wurde.</p>

<h2>4. Welche Methode wählen?</h2>
<table>
<tr><th>Methode</th><th>Ladeart</th><th>Typischer Einsatzzweck</th></tr>
<tr><td>CTAS + <code>read_files()</code></td><td>Einmalig (voller Snapshot)</td><td>Erstbefüllung, Prototyping, Ad-hoc-Analysen</td></tr>
<tr><td><code>COPY INTO</code></td><td>Inkrementell, idempotent</td><td>Wiederkehrende Batch-Jobs auf mittelgroßen Dateimengen</td></tr>
<tr><td>Streaming Table + Auto Loader</td><td>Inkrementell/kontinuierlich, skaliert auf sehr viele Dateien</td><td>Produktive Bronze-Schicht, wachsende/laufend eintreffende Datenmengen</td></tr>
</table>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Für die meisten neuen Ingestion-Anwendungsfälle empfiehlt Databricks inzwischen grundsätzlich <strong>Streaming Tables</strong> als bevorzugten Ansatz, auch für Daten aus Cloud-Speicher oder Message-Bussen wie Kafka &ndash; <code>read_files()</code> ist dabei die SQL-Funktion, über die Auto Loader innerhalb einer Streaming-Table-Definition angesprochen wird. CTAS und <code>COPY INTO</code> bleiben unterstützt und sinnvoll für einmalige bzw. einfache wiederkehrende Batch-Ladevorgänge, gelten aber nicht mehr als Standardempfehlung für neue produktive Pipelines. Für komplexere Quellen (SaaS-Anwendungen, Datenbanken) bietet Databricks zusätzlich <strong>Lakeflow Connect</strong> mit vorgefertigten, verwalteten Connectoren an (siehe Kapitel 4 dieses Themenordners).<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ldp/load">Load data in pipelines &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 2 - Data Ingestion and Loading\01 Ingestion-Methoden im Ueberblick.pdf",
    title="Ingestion-Methoden im Überblick",
    subtitle="Section 2 &middot; Data Ingestion and Loading &middot; Quelle: Kurs 1, Kapitel 3&ndash;5, 17",
    body_html=body,
    build_name="01_01_ingestion_ueberblick",
)
print("OK")
