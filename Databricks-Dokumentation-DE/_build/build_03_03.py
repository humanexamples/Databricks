# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Fehlerhafte oder unerwartete Daten schleichen sich in fast jede Pipeline ein &ndash; ein leeres Pflichtfeld, ein ungültiger Statuscode, ein Datum in der Zukunft. Lakeflow Declarative Pipelines bietet mit <strong>Expectations</strong> ein eingebautes Werkzeug, um solche Datenqualitätsregeln direkt im Pipeline-Code zu definieren und automatisch durchzusetzen &ndash; ganz ohne separates Validierungs-Framework.</p>

<h2>1. Was sind Expectations?</h2>
<p>Eine <strong>Expectation</strong> ist eine SQL-Bedingung, die für jede Zeile geprüft wird, während sie die Pipeline durchläuft. Wird die Bedingung erfüllt, läuft die Verarbeitung normal weiter. Wird sie verletzt, entscheidet die konfigurierte <strong>Verletzungsaktion</strong> darüber, was mit der betroffenen Zeile geschieht. Definiert werden Expectations über die <code>CONSTRAINT ... EXPECT (...)</code>-Syntax direkt in der Tabellendefinition.</p>

<h2>2. Die drei Verletzungsaktionen</h2>
<table>
<tr><th>Aktion</th><th>Verhalten bei Verletzung</th><th>Typischer Einsatz</th></tr>
<tr><td><strong>WARN</strong> (Standard)</td><td>Verstoß wird protokolliert, die Zeile bleibt aber im Ergebnis erhalten, Pipeline läuft normal weiter</td><td>Nicht-kritische Qualitätsüberwachung, ohne den Betrieb zu unterbrechen</td></tr>
<tr><td><strong>DROP ROW</strong></td><td>Die betroffene Zeile wird verworfen, die Anzahl wird protokolliert, restliche Verarbeitung läuft weiter</td><td>Fehlerhafte Daten sollen ausgeschlossen werden, ohne den Lauf zu stoppen</td></tr>
<tr><td><strong>FAIL UPDATE</strong></td><td>Der betroffene Flow wird sofort gestoppt; manuelles Eingreifen erforderlich, andere Flows bleiben unberührt</td><td>Kritische Datenprobleme, die zwingend behoben werden müssen, bevor es weitergeht</td></tr>
</table>
<p>Mehrere Constraints können gleichzeitig auf einer Tabelle definiert werden und werden unabhängig voneinander ausgewertet &ndash; so lässt sich eine feingranulare, mehrschichtige Qualitätskontrolle über alle relevanten Spalten hinweg aufbauen.</p>

<h2>3. Syntaxbeispiel: alle drei Aktionen kombiniert</h2>
<p>Das folgende Beispiel zeigt, wie sich alle drei Verletzungsaktionen gemeinsam auf einer Silver-Tabelle einsetzen lassen &ndash; jede Spalte erhält dabei die für sie passende Strenge:</p>

{code('sql', '''CREATE OR REFRESH STREAMING TABLE orders_silver (
  CONSTRAINT valid_notifications EXPECT (notifications IN ('Y', 'N')),
  CONSTRAINT valid_date EXPECT (order_timestamp > '2021-12-26') ON VIOLATION DROP ROW,
  CONSTRAINT valid_id EXPECT (customer_id IS NOT NULL) ON VIOLATION FAIL UPDATE
)
AS
SELECT order_id,
       timestamp(order_timestamp) AS order_timestamp,
       customer_id,
       notifications
FROM STREAM orders_bronze;''')}

<p>In diesem Beispiel wird <code>valid_notifications</code> ohne explizite <code>ON VIOLATION</code>-Angabe definiert &ndash; das entspricht automatisch dem Standardverhalten <strong>WARN</strong>. Bei einem echten Testlauf mit Beispieldaten ergab sich folgendes Bild: Von 174 eingelesenen Zeilen wurden 26 wegen eines ungültigen Datums verworfen (<code>DROP ROW</code>) und 39 lösten eine Warnung wegen eines ungültigen Notifications-Werts aus (<code>WARN</code>, Zeile bleibt erhalten) &ndash; am Ende standen 148 Zeilen in der Zieltabelle.</p>

<h2>4. Wie Expectations im Pipeline-Ablauf wirken</h2>
<p>Der Ablauf pro Zeile lässt sich in zwei Schritten zusammenfassen: Eine Zeile tritt in die Pipeline ein und wird gegen alle definierten Expectations geprüft. Besteht sie alle Prüfungen, wird sie normal weiterverarbeitet. Schlägt eine Prüfung fehl, greift die für diesen Constraint konfigurierte Aktion &ndash; unabhängig davon, was mit anderen Zeilen oder anderen Flows in derselben Pipeline passiert.</p>

<figure class="img">
<img src="assets/03/actions_overview.png">
<figcaption>Jede Zeile wird gegen alle definierten Expectations geprüft; die konfigurierte Aktion bestimmt das weitere Vorgehen bei einer Verletzung.</figcaption>
</figure>

<h2>5. Metriken auswerten</h2>
<p>Nach einem Pipeline-Lauf lassen sich die Ergebnisse jeder Expectation im Editor direkt einsehen &ndash; etwa über die <strong>Table metrics</strong> eines Datensatzes: Anzahl der Ausgabezeilen, wie viele Expectations erfüllt bzw. verletzt wurden, sowie eine Aufschlüsselung nach Constraint mit Ausfallquote. Für eine langfristige Auswertung über mehrere Läufe hinweg (z.&nbsp;B. um Qualitätstrends zu erkennen) empfiehlt sich das Abfragen des <strong>Pipeline-Event-Logs</strong>, das strukturierte Datenqualitäts-Metriken pro Lauf enthält.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Die aktuelle Databricks-Dokumentation verwendet für die programmatische Python-API leicht andere Bezeichner als die hier gezeigte SQL-Syntax: <code>expect</code> entspricht der WARN-Aktion (Zeile bleibt erhalten, Metriken werden erfasst), während <code>expect_or_drop</code> der DROP-ROW-Aktion entspricht und verhindert, dass ungültige Zeilen weiterverarbeitet werden. Das Pipeline-Event-Log gilt als zentrales Beobachtbarkeits-Werkzeug: Jeder Lauf schreibt strukturierte Datensätze zu Ausführungsfortschritt, Datenqualitätsergebnissen, Daten-Lineage und Fehlerdetails &ndash; das <code>details</code>-Feld enthält dabei unter anderem eine JSON-Struktur mit Bestanden-/Fehlgeschlagen-Zählern pro Constraint, die sich für Trendanalysen und Alarmierung eignet.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ldp/expectations">Manage data quality with pipeline expectations &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\03 Datenqualitaet mit Expectations.pdf",
    title="Datenqualität mit Expectations",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: Kurs 3, Kapitel 6&ndash;8",
    body_html=body,
    build_name="03_03_expectations",
)
print("OK")
