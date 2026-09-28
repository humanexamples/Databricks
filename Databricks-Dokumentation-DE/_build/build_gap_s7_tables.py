# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Ein früheres Kapitel dieser Section hat den konzeptionellen Unterschied zwischen Managed und External Tables bereits eingeführt. Für die Prüfung ist zusätzlich das praktische Handwerkszeug wichtig: die konkreten SQL-Befehle, um beide Tabellentypen anzulegen, zu ändern, zu löschen und ineinander umzuwandeln.</p>

<h2>1. Managed Tables anlegen, ändern, löschen</h2>
<p>Wird beim Anlegen einer Tabelle kein <code>LOCATION</code> angegeben, entsteht automatisch eine <strong>Managed Table</strong>: Unity Catalog verwaltet sowohl die Metadaten als auch den zugrunde liegenden Speicherort innerhalb des von Databricks verwalteten Cloud-Speichers.</p>
{code('sql', '''-- Managed Table anlegen (kein LOCATION angegeben)
CREATE TABLE main.sales.orders (
  order_id BIGINT,
  customer_id BIGINT,
  order_date DATE,
  amount DOUBLE
);

-- Ändern: Spalte hinzufügen bzw. umbenennen
ALTER TABLE main.sales.orders ADD COLUMN currency STRING;
ALTER TABLE main.sales.orders RENAME COLUMN amount TO order_amount;

-- Löschen: entfernt Metadaten UND die zugrunde liegenden Daten
DROP TABLE main.sales.orders;''')}

<h2>2. External Tables anlegen, ändern, löschen</h2>
<p>Eine <strong>External Table</strong> entsteht, sobald beim Anlegen ein expliziter <code>LOCATION</code>-Pfad in einem extern registrierten Storage-Bereich (Unity-Catalog-<em>External Location</em>) angegeben wird. Unity Catalog verwaltet dann nur die Metadaten &ndash; die Daten selbst bleiben unter der vollen Kontrolle des zugrunde liegenden Cloud-Speichers.</p>
{code('sql', '''-- External Table anlegen (mit explizitem LOCATION)
CREATE TABLE main.sales.orders_ext (
  order_id BIGINT,
  customer_id BIGINT,
  order_date DATE,
  amount DOUBLE
)
LOCATION 's3://my-company-data/sales/orders_ext/';

-- Löschen: entfernt NUR die Metadaten, die Daten unter dem LOCATION-Pfad bleiben erhalten
DROP TABLE main.sales.orders_ext;''')}
<p>Genau dieser Unterschied beim <code>DROP TABLE</code>-Verhalten ist einer der am häufigsten geprüften Punkte: Bei Managed Tables verschwinden mit dem <code>DROP</code> auch die Daten unwiderruflich, bei External Tables bleiben sie bestehen und könnten &ndash; sofern noch bekannt &ndash; erneut über <code>CREATE TABLE ... LOCATION</code> eingebunden werden.</p>

<h2>3. Zwischen Managed und External konvertieren</h2>
<p>Seit neueren Databricks-Runtime-Versionen lässt sich eine bestehende External Table direkt in eine Managed Table umwandeln, ohne die Daten manuell kopieren zu müssen:</p>
{code('sql', '''-- External Table nachträglich in eine Managed Table umwandeln
ALTER TABLE main.sales.orders_ext SET MANAGED;''')}
<p>Dabei bleiben Tabellenname, Berechtigungen, abhängige Views und die vollständige Tabellenhistorie (Time Travel) erhalten &ndash; die Konvertierung ist zudem so konzipiert, dass sie parallel zu laufenden Lese-/Schreibzugriffen mit minimaler Unterbrechung durchgeführt werden kann. Eine Rückkonvertierung von Managed zu External ist bewusst nicht als einfacher Befehl vorgesehen, da damit die Verantwortung für die physische Datenverwaltung wieder aus Unity Catalog herausgegeben würde.</p>

<h2>4. Entscheidungshilfe</h2>
<table>
<tr><th>Kriterium</th><th>Managed Table</th><th>External Table</th></tr>
<tr><td>Wer verwaltet die Daten?</td><td>Databricks/Unity Catalog</td><td>Bestehender Cloud-Speicher, außerhalb von Databricks kontrolliert</td></tr>
<tr><td>Verhalten bei <code>DROP TABLE</code></td><td>Daten werden mitgelöscht</td><td>Nur Metadaten werden entfernt</td></tr>
<tr><td>Empfohlen für</td><td>Neue Tabellen (Standard- und Empfehlungsfall)</td><td>Bestehende Daten, die auch von Systemen außerhalb Databricks gelesen werden</td></tr>
<tr><td>Unterstützte Formate</td><td>Delta Lake, Apache Iceberg</td><td>Delta, CSV, JSON, Avro, Parquet, ORC, Text</td></tr>
</table>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Managed Tables gelten laut Databricks als Standard- und empfohlener Tabellentyp für Delta Lake und Apache Iceberg, da Unity Catalog dabei sämtliche Lese-, Schreib-, Speicher- und Optimierungsverantwortung übernimmt (inkl. automatischem <code>OPTIMIZE</code>/<code>VACUUM</code> über Predictive Optimization, siehe Section 6). Die Konvertierung per <code>ALTER TABLE ... SET MANAGED</code> unterstützt außerdem ein Rollback: Eine bereits konvertierte Managed Table kann bei Bedarf wieder in eine External Table zurückversetzt werden.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/tables/convert-to-managed">Convert external or foreign Delta Lake tables to Unity Catalog managed tables &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 7 - Governance and Security\06 Managed vs. External Tables - Erstellen, Aendern, Loeschen, Konvertieren.pdf",
    title="Managed vs. External Tables: Erstellen, Ändern, Löschen, Konvertieren",
    subtitle="Section 7 &middot; Governance and Security &middot; Quelle: Databricks-Dokumentation (Unity Catalog Tables)",
    body_html=body,
    build_name="gap_s7_tables",
)
print("OK")
