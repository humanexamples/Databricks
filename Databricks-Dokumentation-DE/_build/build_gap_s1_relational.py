# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Das Überblick-Kapitel dieser Section hat bereits die moderne Unity-Catalog-Hierarchie vorgestellt (Metastore &rarr; Catalog &rarr; Schema &rarr; Table/Volume). Historisch &ndash; und noch immer relevant, wenn man versteht, worauf Unity Catalog eigentlich aufsetzt &ndash; verwaltet Databricks diese Objekte über den sogenannten <strong>Hive Metastore</strong>. Dieses Kapitel erklärt die relationalen Grundbausteine (Datenbanken, Tabellen) auf dieser fundamentalen Ebene und zeigt, wie das <code>LOCATION</code>-Schlüsselwort den physischen Speicherort beeinflusst.</p>

<h2>1. Datenbanken = Schemas im Hive Metastore</h2>
<p>In Databricks ist eine <strong>Datenbank</strong> technisch identisch mit einem <strong>Schema</strong> im Hive Metastore &ndash; beide Befehle erzeugen exakt dasselbe Objekt:</p>
{code('sql', '''CREATE DATABASE db_name;
-- vollkommen gleichwertig:
CREATE SCHEMA db_name;''')}
<p>Der <strong>Hive Metastore</strong> ist ein zentrales Metadaten-Repository: Er speichert nicht die Daten selbst, sondern Informationen darüber &ndash; welche Datenbanken und Tabellen es gibt, deren Schema (Spaltennamen und -typen), das Speicherformat und vor allem, <em>wo</em> die zugehörigen Daten physisch liegen. Jeder Databricks-Workspace verfügt über einen zentralen Hive Metastore, auf den alle Cluster zugreifen.</p>

<h2>2. Der Standard-Speicherort: dbfs:/user/hive/warehouse</h2>
<p>Ohne weitere Angaben landen neue Tabellen in der vorhandenen Standarddatenbank <code>default</code>, und ihre Daten werden physisch unter dem Hive-Standardverzeichnis <code>dbfs:/user/hive/warehouse</code> abgelegt. Legt man eine neue, eigene Datenbank an, entsteht dafür automatisch ein Unterordner mit der Endung <code>.db</code> (zur Unterscheidung von reinen Tabellenordnern) &ndash; ebenfalls unterhalb des Standardverzeichnisses:</p>
{code('sql', '''CREATE SCHEMA db_x;

USE db_x;
CREATE TABLE table1 (...);
CREATE TABLE table2 (...);
-- Metadaten: Hive Metastore, Eintrag "db_x"
-- Daten: dbfs:/user/hive/warehouse/db_x.db/table1, .../table2''')}

<figure class="img">
<img src="assets/s1/hive_metastore_schema.png">
<figcaption>Datenbanken werden im Hive Metastore als Metadaten-Einträge geführt; ihre Tabellendaten liegen standardmäßig als .db-Unterordner unter dbfs:/user/hive/warehouse.</figcaption>
</figure>

<h2>3. Eigene Speicherorte mit LOCATION</h2>
<p>Eine Datenbank muss nicht zwingend unter dem Hive-Standardverzeichnis liegen. Mit dem <code>LOCATION</code>-Schlüsselwort lässt sich beim Anlegen ein beliebiger, davon unabhängiger Pfad vorgeben:</p>
{code('sql', '''CREATE SCHEMA db_y
LOCATION 'dbfs:/custom/path/db_y.db';

USE db_y;
CREATE TABLE table1 (...);
-- Metadaten weiterhin im Hive Metastore
-- Daten diesmal unter dbfs:/custom/path/db_y.db/table1''')}
<p>Wichtig: Die <strong>Metadaten</strong> landen in beiden Fällen gleichermaßen im zentralen Hive Metastore &ndash; unabhängig von <code>LOCATION</code> betrifft dieses Schlüsselwort ausschließlich den physischen Ablageort der <em>Daten</em>.</p>

<h2>4. Managed vs. External Tables</h2>
<p>Dasselbe Prinzip lässt sich auch auf einzelne Tabellen anwenden &ndash; unabhängig davon, wo die umgebende Datenbank selbst liegt:</p>
<table>
<tr><th></th><th>Managed Table</th><th>External Table</th></tr>
<tr><td>Erzeugung</td><td><code>CREATE TABLE table_name (...)</code> &ndash; ohne LOCATION, im Datenbankverzeichnis</td><td><code>CREATE TABLE table_name (...) LOCATION 'pfad'</code> &ndash; außerhalb des Datenbankverzeichnisses</td></tr>
<tr><td>Verantwortung</td><td>Hive/Unity Catalog verwaltet Metadaten <strong>und</strong> Daten</td><td>Hive/Unity Catalog verwaltet <strong>nur</strong> die Metadaten</td></tr>
<tr><td>Verhalten bei <code>DROP TABLE</code></td><td>Datendateien werden mitgelöscht</td><td>Datendateien bleiben erhalten</td></tr>
<tr><td>Automatische Optimierung</td><td>Predictive Optimization (automatisches <code>OPTIMIZE</code>/<code>VACUUM</code>) sowie Automatic Liquid Clustering (<code>CLUSTER BY AUTO</code>) verfügbar</td><td>Nicht verfügbar &ndash; Optimierung muss manuell angestoßen werden</td></tr>
</table>

<figure class="img">
<img src="assets/s1/managed_vs_external.png">
<figcaption>Managed Tables liegen im Datenbankverzeichnis und werden bei DROP TABLE vollständig gelöscht; External Tables verweisen per LOCATION auf einen unabhängigen Pfad.</figcaption>
</figure>

<p>Ein oft übersehener, aber praktisch wichtiger Unterschied betrifft die automatische Wartung: <strong>Predictive Optimization</strong> &ndash; also das automatische Ausführen von <code>OPTIMIZE</code> und <code>VACUUM</code> im Hintergrund, ohne eigene Wartungsjobs planen zu müssen &ndash; sowie <strong>Automatic Liquid Clustering</strong> (<code>CLUSTER BY AUTO</code>, siehe Section 6) setzen beide eine <strong>Unity-Catalog-Managed-Table</strong> voraus. External Tables sind davon grundsätzlich ausgeschlossen, da Unity Catalog dort nur die Metadaten, nicht aber die zugrunde liegenden Dateien verwaltet und entsprechend keine automatisierten Schreiboperationen auf ihnen ausführen kann. Das ist ein weiteres gutes Argument, im Zweifel Managed statt External Tables zu verwenden.</p>

<p>Eine External Table lässt sich dabei in jeder beliebigen Datenbank anlegen &ndash; auch in einer, die selbst unter einem eigenen <code>LOCATION</code>-Pfad liegt. Die Tabellendefinition erscheint stets im Hive Metastore unterhalb der gewählten Datenbank, während die Daten unabhängig davon exakt dort landen, wo <code>LOCATION</code> es vorgibt:</p>
{code('sql', '''USE db_x;
CREATE TABLE table3
LOCATION 'dbfs:/some/path_2/x_table3';
-- Metadaten: Hive Metastore, unter db_x gelistet
-- Daten: dbfs:/some/path_2/x_table3 (voellig unabhaengig vom db_x-Verzeichnis)''')}

<h2>5. Metadaten per SQL abfragen: INFORMATION_SCHEMA</h2>
<p>Der Hive Metastore bzw. sein Unity-Catalog-Nachfolger speichert also Metadaten &ndash; aber wie fragt man diese Metadaten selbst per SQL ab, statt sie nur über die grafische Oberfläche zu durchsuchen? Jeder Unity-Catalog-Katalog enthält dafür automatisch ein <strong>INFORMATION_SCHEMA</strong>: eine schreibgeschützte Sammlung von Systemtabellen bzw. -Views, die genau diese Metadaten &ndash; Kataloge, Schemas, Tabellen, Spalten, Berechtigungen und mehr &ndash; als ganz normal abfragbare Tabellen bereitstellt:</p>
{code('sql', '''-- Alle Tabellen in einem bestimmten Schema auflisten
SELECT table_catalog, table_schema, table_name, table_type
FROM main.information_schema.tables
WHERE table_schema = 'default';

-- Spalten und Datentypen einer bestimmten Tabelle nachschlagen
SELECT column_name, data_type, is_nullable
FROM main.information_schema.columns
WHERE table_catalog = 'main' AND table_schema = 'default' AND table_name = 'orders';''')}
<p>Ein wichtiges Detail dabei: <code>INFORMATION_SCHEMA</code> ist <strong>rechte-bewusst</strong> &ndash; jede Abfrage liefert ausschließlich die Objekte zurück, auf die die aktuell angemeldete Person tatsächlich Zugriffsrechte besitzt. Das macht es zum idealen Werkzeug, um programmatisch (z. B. aus einem Governance-Dashboard heraus) zu prüfen, welche Tabellen und Spalten überhaupt existieren, ohne dafür erhöhte Rechte zu benötigen.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Mit Unity Catalog wird das Grundkonzept um eine zusätzliche Hierarchieebene erweitert (<code>catalog.schema.table</code> statt nur <code>schema.table</code>) und der Hive Metastore durch den zentralen, kontenweiten Unity-Catalog-Metastore abgelöst &ndash; das Grundprinzip von Managed vs. External Tables sowie die Bedeutung von <code>LOCATION</code> bleiben dabei inhaltlich unverändert. Für <code>INFORMATION_SCHEMA</code>-Abfragen empfiehlt Databricks, stets selektive Filter wie <code>WHERE table_catalog = '...' AND table_schema = '...'</code> zu setzen, um Timeouts bei sehr vielen Objekten zu vermeiden; außerdem werden alle Bezeichner (außer Spalten- und Tag-Namen) intern kleingeschrieben gespeichert, weshalb Vergleiche direkt in Kleinschreibung erfolgen sollten statt über <code>LOWER()</code>/<code>UPPER()</code>-Funktionen. Details zu den Zugriffsrechten (GRANT/REVOKE/DENY) und zur gezielten Konvertierung zwischen Managed und External unter Unity Catalog behandelt <strong>Section 7</strong> dieser Dokumentation.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/tables/types">Unity Catalog table types</a> &middot; <a href="https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-information-schema">Information schema &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 1 - Databricks Intelligence Plattform\05 Relationale Entitaeten - Datenbanken, Tabellen und der Hive Metastore.pdf",
    title="Relationale Entitäten: Datenbanken, Tabellen und der Hive Metastore",
    subtitle="Section 1 &middot; Databricks Intelligence Plattform &middot; Quelle: Udemy-Kursmaterial &bdquo;Relational Entities&ldquo;, erg&auml;nzt mit Databricks-Dokumentation",
    body_html=body,
    build_name="gap_s1_relational",
)
print("OK")
