# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p><strong>Section 2, Kapitel 1</strong> dieser Dokumentation hat CTAS (<code>CREATE TABLE AS SELECT</code>) bereits im Ingestion-Kontext eingeführt &ndash; als Methode, um Rohdaten aus Cloud-Speicher in eine Bronze-Tabelle zu laden. Dieses Kapitel betrachtet CTAS aus einer anderen Perspektive: als allgemeines Werkzeug zum Anlegen von Delta-Tabellen, ergänzt um Table Constraints und das Klonen von Tabellen.</p>

<h2>1. CTAS: Spalten filtern und umbenennen</h2>
<p>Da eine CTAS-Anweisung im Kern eine <code>SELECT</code>-Abfrage ausführt, lassen sich dabei ganz normale Projektionen anwenden &ndash; einzelne Spalten auswählen, weglassen oder umbenennen:</p>
{code('sql', '''CREATE TABLE table_1
AS SELECT col_1, col_3 AS new_col_3 FROM table_2;''')}

<h2>2. Zusätzliche CTAS-Optionen</h2>
<p>Die <code>CREATE TABLE ... AS</code>-Klausel lässt sich um mehrere Optionen erweitern, die auch bei einer klassischen <code>CREATE TABLE</code>-Anweisung verfügbar sind:</p>
{code('sql', '''CREATE TABLE new_table
COMMENT "Contains PII"
PARTITIONED BY (city, birth_date)
LOCATION '/some/path'
AS SELECT id, name, email, birth_date, city FROM users;''')}
<ul>
<li><code>COMMENT</code> &ndash; ein beschreibender Kommentar, der die Tabelle im Katalog leichter auffindbar macht (hier z. B. ein Hinweis auf enthaltene personenbezogene Daten).</li>
<li><code>PARTITIONED BY</code> &ndash; physische Aufteilung der Daten in Unterordner nach einer oder mehreren Spalten (Details und Fallstricke dazu in Section 6, Kapitel 2).</li>
<li><code>LOCATION</code> &ndash; macht aus der neuen Tabelle eine External Table an einem frei gewählten Speicherort (siehe voriges Kapitel dieser Section).</li>
</ul>

<p>Anstelle von <code>PARTITIONED BY</code> lässt sich bei der Tabellenerstellung ebenso die modernere <code>CLUSTER BY</code>-Klausel angeben &ndash; syntaktisch an derselben Stelle, aber ohne die Nachteile klassischer Partitionierung (siehe Section 6, Kapitel 3):</p>
{code('sql', '''-- Explizite Clustering-Spalten
CREATE TABLE new_table (id INT, city STRING, birth_date DATE)
CLUSTER BY (city, birth_date);

-- Databricks waehlt die Clustering-Spalten selbststaendig anhand des Abfrageverhaltens
CREATE TABLE new_table (id INT, city STRING, birth_date DATE)
CLUSTER BY AUTO;''')}
<p><code>CLUSTER BY AUTO</code> setzt allerdings eine <strong>Managed Table</strong> mit aktivierter Predictive Optimization voraus (siehe voriges Kapitel dieser Section) &ndash; bei einer <code>LOCATION</code>-basierten External Table steht diese automatische Variante nicht zur Verfügung. <code>PARTITIONED BY</code>, <code>CLUSTER BY</code> und <code>ZORDER</code> (über <code>OPTIMIZE</code>) schließen sich dabei gegenseitig aus: Für eine Tabelle gilt zu jedem Zeitpunkt nur eines dieser drei Datenlayout-Verfahren.</p>

<h2>3. CREATE TABLE vs. CTAS im Vergleich</h2>
<table>
<tr><th></th><th>CREATE TABLE (klassisch)</th><th>CTAS</th></tr>
<tr><td>Schema</td><td>Manuelle Deklaration erforderlich</td><td>Wird automatisch aus dem Abfrageergebnis abgeleitet &ndash; keine manuelle Deklaration möglich</td></tr>
<tr><td>Zustand nach Erstellung</td><td>Leere Tabelle</td><td>Sofort mit Daten befüllt</td></tr>
<tr><td>Daten laden</td><td>Erfordert einen separaten <code>INSERT INTO</code></td><td>Erfolgt bereits während der Erstellung</td></tr>
</table>
{code('sql', '''-- Klassisch: manuelles Schema, danach leer
CREATE TABLE table_1 (col1 INT, col2 STRING, col3 DOUBLE);

-- CTAS: Schema und Daten kommen aus der Abfrage
CREATE TABLE table_1
AS SELECT col1, col2, col3 FROM table_2;''')}

<h2>4. Table Constraints: NOT NULL und CHECK</h2>
<p>Nach dem Anlegen &ndash; ob klassisch oder per CTAS &ndash; lassen sich einer Tabelle nachträglich Integritätsregeln hinzufügen. Databricks unterstützt dafür zwei Constraint-Typen: <code>NOT NULL</code> und <code>CHECK</code>. <code>CHECK</code>-Constraints funktionieren dabei wie eine gewöhnliche <code>WHERE</code>-Bedingung, die jeder neue Datensatz erfüllen muss:</p>
{code('sql', '''ALTER TABLE orders
ADD CONSTRAINT valid_date CHECK (date > '2020-01-01');''')}
<p>Wichtige Voraussetzung: Bevor ein Constraint hinzugefügt werden kann, dürfen keine bereits vorhandenen Datensätze gegen die neue Regel verstoßen &ndash; Databricks prüft das beim Anlegen des Constraints. Ab diesem Zeitpunkt führt jeder Schreibversuch, der die Regel verletzt, zu einem Fehler und wird abgelehnt.</p>

<h2>5. Informationelle Constraints: PRIMARY KEY und FOREIGN KEY</h2>
<p>Zusätzlich zu <code>NOT NULL</code> und <code>CHECK</code> lassen sich unter Unity Catalog auch <code>PRIMARY KEY</code>- und <code>FOREIGN KEY</code>-Constraints deklarieren &ndash; mit einem entscheidenden Unterschied zu klassischen Datenbanken: Sie sind rein <strong>informationell</strong> und werden von Databricks <strong>nicht erzwungen</strong>.</p>
{code('sql', '''-- Primaerschluessel auf der Zieltabelle
ALTER TABLE customers ADD CONSTRAINT pk_customers PRIMARY KEY (customer_id);

-- Fremdschluessel-Beziehung zwischen zwei Tabellen
ALTER TABLE orders ADD CONSTRAINT fk_orders_customer
  FOREIGN KEY (customer_id) REFERENCES customers (customer_id);''')}
<p>Da Databricks die Eindeutigkeit bzw. referenzielle Integrität <strong>nicht selbst prüft</strong>, liegt es in der eigenen Verantwortung, vor dem Anlegen sicherzustellen, dass die Daten die deklarierte Beziehung tatsächlich einhalten &ndash; ein doppelter <code>customer_id</code>-Wert oder eine Bestellung ohne passenden Kunden führt zu keinem Fehler. Der Nutzen liegt stattdessen darin, dass Databricks diese Information für <strong>Query-Optimierungen</strong> heranziehen kann (z. B. um Joins effizienter zu planen), sowie darin, dass Modellierungs- und BI-Tools die Tabellenbeziehungen automatisch erkennen und visualisieren können. <code>FOREIGN KEY</code>-Constraints werden dabei nur für Unity-Catalog-Tabellen unterstützt, nicht für Tabellen im (legacy) Hive Metastore.</p>

<h2>6. Nur das Schema kopieren: CREATE TABLE LIKE</h2>
<p>Manchmal wird gar keine Datenkopie benötigt, sondern lediglich eine neue, leere Tabelle mit demselben Schema wie eine bestehende &ndash; etwa um eine Staging-Tabelle mit identischer Struktur anzulegen. Dafür eignet sich <code>CREATE TABLE ... LIKE</code>:</p>
{code('sql', '''CREATE TABLE staging_orders LIKE orders;''')}
<p>Im Gegensatz zu <code>DEEP CLONE</code>/<code>SHALLOW CLONE</code> werden dabei zwar Schema, Partitionierung und Spalteneigenschaften übernommen, aber <strong>keinerlei Daten und keine Verweise</strong> auf die Quelldateien oder deren Transaktionslog &ndash; die neue Tabelle ist von Anfang an vollständig leer und eigenständig.</p>

<h2>7. Delta-Tabellen klonen: Deep Clone vs. Shallow Clone</h2>
<p>Um eine Kopie einer Tabelle zu erstellen &ndash; etwa um in einer Testumgebung gefahrlos mit Produktionsdaten zu experimentieren &ndash; bietet Delta Lake zwei Klon-Varianten:</p>
{code('sql', '''-- Deep Clone: kopiert Daten UND Metadaten vollständig
CREATE TABLE table_clone
DEEP CLONE source_table;

-- Shallow Clone: kopiert nur die Transaktionslogs, keine Daten
CREATE TABLE table_clone
SHALLOW CLONE source_table;''')}
<table>
<tr><th>Deep Clone</th><th>Shallow Clone</th></tr>
<tr><td>Kopiert Daten und Metadaten vollständig</td><td>Kopiert nur die Delta-Transaktionslogs, keine Datendateien</td></tr>
<tr><td>Kann bei großen Datenmengen einige Zeit dauern</td><td>Nahezu augenblicklich, da keine Daten bewegt werden</td></tr>
<tr><td>Erneutes Ausführen synchronisiert nachträgliche Änderungen der Quelle inkrementell</td><td>Ideal zum schnellen Testen von Änderungen, ohne die Originaltabelle zu berühren</td></tr>
</table>
<p>In beiden Fällen gilt: Datenänderungen an der geklonten Tabelle wirken sich <strong>nie</strong> auf die Quelltabelle aus &ndash; Klone sind unabhängige Kopien, keine Referenzen.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Ein Shallow Clone verweist zunächst auf dieselben zugrunde liegenden Parquet-Dateien wie die Quelltabelle und lädt keine Daten neu &ndash; deshalb ist zu beachten, dass ein <code>VACUUM</code> auf der <em>Quelltabelle</em> Dateien entfernen kann, auf die ein Shallow Clone noch verweist, was zu Lesefehlern im Klon führen kann. Deep Clones sind davon nicht betroffen, da sie eigenständige Kopien aller Datendateien besitzen.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/delta/clone">Clone a table on Databricks &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 1 - Databricks Intelligence Plattform\06 Delta-Tabellen anlegen - CTAS-Optionen, Constraints und Cloning.pdf",
    title="Delta-Tabellen anlegen: CTAS-Optionen, Constraints und Cloning",
    subtitle="Section 1 &middot; Databricks Intelligence Plattform &middot; Quelle: Udemy-Kursmaterial &bdquo;Set Up Delta Tables&ldquo;, erg&auml;nzt mit Databricks-Dokumentation",
    body_html=body,
    build_name="gap_s1_ctas",
)
print("OK")
