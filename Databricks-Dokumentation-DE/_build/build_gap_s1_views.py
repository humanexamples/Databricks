# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Neben Tabellen und Volumes kennt Databricks ein drittes relationales Objekt: die <strong>View</strong>. Eine View ist eine <strong>virtuelle Tabelle ohne eigene physische Daten</strong> &ndash; sie ist im Kern nichts anderes als eine gespeicherte SQL-Abfrage gegen bestehende Tabellen, die bei jeder Nutzung der View erneut ausgeführt wird.</p>

<h2>1. Views als gespeicherte Abfrage</h2>
<p>Eine View kombiniert und filtert Spalten aus einer oder mehreren zugrunde liegenden Tabellen zu einem neuen, logischen Ergebnis:</p>
{code('sql', '''CREATE VIEW view_x
AS SELECT A1, A4, B2, B3
FROM table_1
INNER JOIN table_2 ...;''')}

<figure class="img">
<img src="assets/s1/view_diagram.png">
<figcaption>Eine View führt bei jeder Abfrage die zugrunde liegende SQL-Anweisung erneut gegen die Quelltabellen aus, statt eigene Daten zu speichern.</figcaption>
</figure>

<p>Nach der Erstellung lässt sich eine View genauso abfragen wie eine gewöhnliche Tabelle &ndash; per <code>SELECT</code>. Da bei jeder Abfrage die hinterlegte Query erneut gegen die aktuellen Daten der Basistabellen ausgeführt wird, spiegelt eine View immer den aktuellen Stand wider, ohne dass eigene Daten synchronisiert werden müssten.</p>

<h2>2. Drei Sichtbarkeits-Varianten</h2>
<p>Databricks unterscheidet drei Arten von Views, die sich in ihrer Lebensdauer und Sichtbarkeit unterscheiden:</p>
<table>
<tr><th></th><th>(Stored) View</th><th>Temporary View</th><th>Global Temporary View</th></tr>
<tr><td>Sichtbarkeit</td><td>Über beliebig viele Sessions hinweg</td><td>Nur innerhalb der aktuellen Spark-Session</td><td>Über alle Sessions hinweg, solange derselbe Cluster läuft</td></tr>
<tr><td>Persistenz</td><td>In der Datenbank gespeichert</td><td>Nicht gespeichert</td><td>Nicht gespeichert</td></tr>
<tr><td>Entfernt durch</td><td>Nur explizit per <code>DROP VIEW</code></td><td>Automatisch beim Ende der Session</td><td>Automatisch beim Neustart des Clusters</td></tr>
<tr><td>Syntax</td><td><code>CREATE VIEW</code></td><td><code>CREATE TEMP VIEW</code></td><td><code>CREATE GLOBAL TEMP VIEW</code></td></tr>
</table>

<h3>2.1 (Stored) Views</h3>
<p>Wie Tabellen werden Stored Views dauerhaft in der Datenbank abgelegt &ndash; gespeichert wird dabei allerdings nur die Definition (die SQL-Abfrage), nicht die Daten selbst:</p>
{code('sql', '''CREATE VIEW view_name AS query;
DROP VIEW view_name;''')}

<h3>2.2 Temporary Views</h3>
<p>Eine Temporary View ist an die aktuelle <strong>Spark-Session</strong> gebunden und existiert nur so lange, wie diese Session läuft:</p>
{code('sql', '''CREATE TEMP VIEW view_name AS query;''')}
<p>Für die Prüfung relevant ist die Frage, <em>wann</em> in Databricks überhaupt eine neue Spark-Session entsteht &ndash; denn genau dann verschwinden alle bis dahin angelegten Temporary Views:</p>
<ul>
<li>beim Öffnen eines neuen Notebooks,</li>
<li>beim Trennen und erneuten Verbinden (Detach/Reattach) eines Notebooks mit einem Cluster,</li>
<li>nach der Installation eines Python-Pakets (da dies einen Neustart des Python-Interpreters auslöst),</li>
<li>sowie nach einem Neustart des Clusters selbst.</li>
</ul>

<h3>2.3 Global Temporary Views</h3>
<p>Eine Global Temporary View verhält sich ähnlich wie eine Temporary View, ist aber nicht an eine einzelne Session, sondern an den gesamten <strong>Cluster</strong> gebunden: Solange der Cluster läuft, kann jedes daran angehängte Notebook &ndash; unabhängig von seiner eigenen Session &ndash; auf sie zugreifen. Global Temporary Views werden dafür automatisch in einer eigenen, clusterweiten Datenbank namens <code>global_temp</code> abgelegt:</p>
{code('sql', '''CREATE GLOBAL TEMP VIEW view_name AS query;

-- Zugriff erfordert den Datenbank-Qualifizierer "global_temp"
SELECT * FROM global_temp.view_name;''')}

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Unity Catalog unterstützt zusätzlich zu den hier beschriebenen Grundtypen auch <strong>dynamische Views</strong>, bei denen die Sichtbarkeit einzelner Zeilen oder Spalten von Funktionen wie <code>current_user()</code> oder <code>is_account_group_member()</code> abhängt &ndash; ein älterer Ansatz für zeilen-/spaltenbasierte Zugriffskontrolle, der inzwischen weitgehend durch die in Section 7 behandelten Row Filters und Column Masks abgelöst wurde, syntaktisch aber weiterhin unterstützt wird.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/views/">Views &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 1 - Databricks Intelligence Plattform\07 Views - Stored, Temporary und Global Temporary Views.pdf",
    title="Views: Stored, Temporary und Global Temporary Views",
    subtitle="Section 1 &middot; Databricks Intelligence Plattform &middot; Quelle: Udemy-Kursmaterial &bdquo;Views&ldquo;, erg&auml;nzt mit Databricks-Dokumentation",
    body_html=body,
    build_name="gap_s1_views",
)
print("OK")
