# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Bevor Rohdaten transformiert oder in eine Delta-Tabelle geladen werden, lassen sie sich oft schon direkt am Speicherort per SQL abfragen &ndash; ganz ohne vorherige Ingestion. Dieses Kapitel zeigt diese leichtgewichtigen Techniken sowie eine wichtige Einschränkung, die dabei entstehen kann, und wie man sie auflöst.</p>

<h2>1. Dateien direkt abfragen</h2>
<p>Mit einer einfachen <code>SELECT</code>-Anweisung lässt sich der Inhalt von Dateien abfragen, ohne vorher eine Tabelle anzulegen. Dabei wird statt eines Tabellennamens das Dateiformat gefolgt vom Pfad in Backticks angegeben (keine einfachen Anführungszeichen!):</p>
{code('sql', '''SELECT * FROM json.`/Volumes/main/default/raw/file_name.json`;''')}
<p>Diese direkte Abfrage funktioniert gut bei <strong>selbstbeschreibenden</strong> Formaten wie JSON oder Parquet, die ihr Schema in der Datei selbst mitführen. Bei <strong>nicht selbstbeschreibenden</strong> Formaten wie CSV oder TSV liefert sie dagegen kaum brauchbare Ergebnisse, da Spaltennamen und -typen fehlen. Der Pfad kann dabei auf drei Arten angegeben werden:</p>
<ul>
<li>eine <strong>einzelne Datei</strong> (z. B. <code>file_2022.json</code>),</li>
<li><strong>mehrere Dateien</strong> über ein Wildcard-Muster (z. B. <code>file_*.json</code>),</li>
<li>ein kompletter <strong>Verzeichnispfad</strong> (z. B. <code>/path/dir</code>) &ndash; vorausgesetzt, alle enthaltenen Dateien teilen sich dasselbe Format und Schema.</li>
</ul>

<figure class="img">
<img src="assets/s3/querying_files_directly.png">
<figcaption>Direkte Dateiabfragen funktionieren zuverlässig bei selbstbeschreibenden Formaten wie JSON/Parquet und lassen sich auf eine einzelne Datei, mehrere Dateien per Wildcard oder ein ganzes Verzeichnis anwenden.</figcaption>
</figure>

<h2>2. Rohdaten als Text oder Binärdaten extrahieren</h2>
<p>Manchmal soll eine Datei bewusst <em>nicht</em> automatisch interpretiert werden &ndash; etwa wenn die Eingabedaten fehlerhaft sein könnten und stattdessen mit eigener Parsing-Logik behandelt werden sollen. Für textbasierte Formate (JSON, CSV, TSV, TXT) liefert das Format <code>text</code> jede Zeile als rohen String:</p>
{code('sql', '''SELECT * FROM text.`/Volumes/main/default/raw/file_name.csv`;''')}
<p>Für Bilder oder andere unstrukturierte Binärdaten liefert <code>binaryFile</code> stattdessen den rohen Byte-Inhalt jeder Datei:</p>
{code('sql', '''SELECT * FROM binaryFile.`/Volumes/main/default/raw/images`;''')}

<h2>3. Mit CTAS eine Tabelle direkt aus Dateien registrieren</h2>
<p>Um aus einer direkten Dateiabfrage eine persistente Delta-Tabelle zu machen, genügt eine CTAS-Anweisung (siehe auch Section 1, Kapitel 6, und Section 2, Kapitel 1):</p>
{code('sql', '''CREATE TABLE bronze_table
AS SELECT * FROM parquet.`/Volumes/main/default/raw/orders`;''')}
<p>Wie bereits bekannt, leitet CTAS das Schema automatisch aus dem Abfrageergebnis ab und unterstützt <strong>keine</strong> manuelle Schema-Deklaration <strong>und keine zusätzlichen Datei-Optionen</strong> (z. B. Trennzeichen oder Encoding bei CSV). Damit eignet sich dieser Weg vor allem für Quellen mit sauber definiertem Schema wie Parquet &ndash; nicht aber für CSV-Dateien, die meist zusätzliche Optionen benötigen.</p>

<h2>4. Externe Tabellen mit CREATE TABLE ... USING ... OPTIONS</h2>
<p>Werden zusätzliche Optionen benötigt (z. B. ein CSV-Trennzeichen), kommt die klassische <code>CREATE TABLE</code>-Anweisung mit dem Schlüsselwort <code>USING</code> zum Einsatz:</p>
{code('sql', '''CREATE TABLE users_csv (
  id INT, name STRING, email STRING
)
USING CSV
OPTIONS (header = "true", delimiter = ";")
LOCATION "/Volumes/main/default/raw/users";''')}
<p>Auf demselben Weg lässt sich auch eine externe SQL-Datenbank über eine JDBC-Verbindung anbinden (siehe auch Section 2, Kapitel 7 für die Python-Variante mit <code>spark.read.format("jdbc")</code>):</p>
{code('sql', '''CREATE TABLE customers_ext (
  id INT, name STRING, email STRING
)
USING JDBC
OPTIONS (
  url = "jdbc:postgresql://hostname:5432/salesdb",
  dbtable = "public.customers",
  user = "app_user",
  password = secret("db-scope", "db-password")
);''')}
<p>Entscheidend: Mit <code>USING</code> entsteht immer eine <strong>External Table</strong> (siehe Section 1, Kapitel 5) &ndash; und zwar eine, die <strong>kein Delta-Format</strong> hat! Es findet beim Erstellen keine Datenbewegung statt; die Tabelle verweist lediglich auf die Dateien bzw. die Datenbank am angegebenen Ort, in deren ursprünglichem Format.</p>

<h2>5. Die Einschränkung: keine Delta-Garantien &ndash; und die Lösung</h2>
<p>Da eine solche Tabelle kein Delta-Format hat, gelten die vertrauten Delta-Lake-Vorteile hier <strong>nicht</strong>: kein Time Travel, keine Garantie, stets die aktuellste Version zu lesen, und bei einer sehr großen, direkt angebundenen Datenbanktabelle drohen zudem Performance-Probleme, da jede Abfrage erneut gegen die externe Quelle ausgeführt wird.</p>
<p>Die Lösung: Statt die externe Quelle dauerhaft als Tabelle zu registrieren, bindet man sie zunächst nur als <strong>Temporary View</strong> ein (siehe Section 1, Kapitel 7) und wandelt diese anschließend per CTAS in eine waschechte, materialisierte Delta-Tabelle um:</p>
{code('sql', '''-- Schritt 1: externe Quelle nur als Temp View einbinden
CREATE TEMP VIEW customers_ext_vw (id INT, name STRING, email STRING)
USING JDBC
OPTIONS (
  url = "jdbc:postgresql://hostname:5432/salesdb",
  dbtable = "public.customers",
  user = "app_user",
  password = secret("db-scope", "db-password")
);

-- Schritt 2: Daten einmalig extrahieren und als Delta-Tabelle materialisieren
CREATE TABLE customers_bronze
AS SELECT * FROM customers_ext_vw;''')}
<p>Bemerkenswert dabei: CTAS ist nicht auf Dateien beschränkt &ndash; als Quelle für den <code>SELECT</code>-Teil kann ebenso gut eine View, eine bestehende Tabelle oder jedes andere abfragbare Objekt dienen. Nach diesem zweistufigen Vorgehen liegen die Daten als vollwertige Delta-Tabelle vor, mit allen gewohnten Garantien.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Für neue Projekte empfiehlt Databricks inzwischen ausdrücklich, anstelle von direkten Dateiabfragen oder <code>CREATE TABLE ... USING</code> die in Section 2 behandelte Funktion <code>read_files()</code> zu verwenden &ndash; sie deckt dieselben Formate ab (inkl. <code>text</code> und <code>binaryFile</code>), erlaubt aber zusätzlich Schema-Angaben und Datei-Optionen direkt in der Abfrage, was mit reinem <code>file_format.path</code>-Zugriff nicht möglich ist. Für Zugangsdaten in der <code>OPTIONS</code>-Klausel (wie im JDBC-Beispiel) rät Databricks statt Klartext-Passwörtern zur <code>secret()</code>-Funktion, die einen in einem Secret Scope hinterlegten Wert referenziert.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files">read_files table-valued function</a> &middot; <a href="https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-using">CREATE TABLE [USING] &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\15 Dateien direkt abfragen und externe Tabellen registrieren.pdf",
    title="Dateien direkt abfragen und externe Tabellen registrieren",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: Udemy-Kursmaterial &bdquo;Querying Files&ldquo;, erg&auml;nzt mit Databricks-Dokumentation",
    body_html=body,
    build_name="gap_s3_queryfiles",
)
print("OK")
