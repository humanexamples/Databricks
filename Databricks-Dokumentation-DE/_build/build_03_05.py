# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Quellsysteme wie Datenbanken oder SaaS-Anwendungen ändern sich fortlaufend: Neue Kunden werden angelegt, Adressen aktualisiert, Konten gelöscht. <strong>Change Data Capture (CDC)</strong> ist die Technik, mit der solche Änderungen nachverfolgt und in eine Zieltabelle im Lakehouse übertragen werden. Dieses Dokument erklärt die Grundidee von CDC, den Unterschied zwischen SCD Type 1 und Type 2, und wie sich CDC mit der deklarativen <code>AUTO CDC INTO</code>-Syntax umsetzen lässt.</p>

<h2>1. Was ist Change Data Capture?</h2>
<p>CDC bezeichnet die Technik, Änderungen (Inserts, Updates, Deletes) in einer Datenquelle zu erfassen und automatisiert auf eine Zieltabelle anzuwenden, um diese kontinuierlich mit dem aktuellen Stand der Quelle synchron zu halten. Eng damit verbunden ist das Konzept der <strong>Slowly Changing Dimensions (SCD)</strong>, das festlegt, <em>wie</em> historische Änderungen in der Zieltabelle behandelt werden. Zwei Varianten sind besonders verbreitet:</p>
<ul>
<li><strong>SCD Type 1</strong> &ndash; überschreibt vorhandene Daten, es wird keine Historie geführt.</li>
<li><strong>SCD Type 2</strong> &ndash; verfolgt historische Änderungen, indem frühere Versionen eines Datensatzes zusätzlich gespeichert werden.</li>
</ul>

<h2>2. SCD Type 1 &ndash; einfach erklärt</h2>
<p>Bei SCD Type 1 wird die Zieltabelle stets mit den aktuellsten Werten überschrieben &ndash; es gibt keine Möglichkeit, frühere Zustände eines Datensatzes nachzuvollziehen. Ein Beispiel anhand einer Kundentabelle mit drei eingehenden Änderungen:</p>
<ul>
<li><strong>Peter</strong> (Kunde 1): Seine Adresse wird auf den neuesten Stand aktualisiert (basierend auf dem Sequenzfeld <code>ProcessDate</code>).</li>
<li><strong>Samarth</strong> (Kunde 2): Sein Konto wurde gelöscht &rarr; seine Zeile wird aus der Zieltabelle entfernt.</li>
<li><strong>Kostas</strong> (Kunde 3): Ein neuer Kunde &rarr; sein Datensatz wird eingefügt.</li>
</ul>
<p>Das Ergebnis ist ein aktueller Schnappschuss aller aktiven Kunden &ndash; ohne jede Historie. Das macht SCD Type 1 zur einfachsten CDC-Strategie und ideal für Anwendungsfälle, bei denen ausschließlich der aktuelle, korrekte Datenstand zählt.</p>

<figure class="img">
<img src="assets/03/scd_type_1_worked_example.png">
<figcaption>SCD Type 1: Updates überschreiben bestehende Zeilen, Deletes entfernen sie, neue Kunden werden eingefügt &ndash; ohne Historie.</figcaption>
</figure>

<h2>3. SCD Type 2 &ndash; kurzer Ausblick</h2>
<p>Im Gegensatz dazu bewahrt SCD Type 2 jede historische Version eines Datensatzes: Statt eine Zeile zu überschreiben, wird eine neue Version eingefügt und die vorherige über Metadatenspalten (<code>__START_AT</code>/<code>__END_AT</code>) als abgelaufen markiert. Aktive Zeilen tragen ein leeres <code>__END_AT</code>, historische und gelöschte Zeilen ein konkretes Datum. Dieses Muster wird in Kapitel 8 dieser Section vertieft; die vorliegenden Grundlagen fokussieren auf SCD Type 1.</p>

<h2>4. AUTO CDC INTO: die deklarative CDC-Syntax</h2>
<p>Lakeflow Declarative Pipelines bietet mit <code>AUTO CDC INTO</code> eine kompakte, deklarative Syntax für CDC-Verarbeitung. Sie ersetzt aufwendige, manuell geschriebene <code>MERGE INTO</code>-Logik durch wenige klar lesbare Klauseln. <strong>Wichtiger Hinweis:</strong> <code>AUTO CDC INTO</code> löst die ältere <code>APPLY CHANGES INTO</code>-API ab &ndash; beide verwenden dieselbe Syntax, <code>APPLY CHANGES INTO</code> bleibt aber weiterhin funktionsfähig.</p>

{code('sql', '''-- Leere Ziel-Streaming-Table anlegen
CREATE OR REFRESH STREAMING TABLE scd_type_1_customers_silver;

-- CDC-Verarbeitung mit SCD Type 1 (Standardverhalten)
CREATE FLOW scd_type_1_flow AS
AUTO CDC INTO scd_type_1_customers_silver
FROM STREAM customers_bronze_clean
KEYS (customer_id)
APPLY AS DELETE WHEN operation = 'delete'
SEQUENCE BY timestamp
COLUMNS * EXCEPT (operation)
STORED AS SCD TYPE 1;''')}

<p>Die einzelnen Klauseln im Überblick:</p>
<ul>
<li><strong>KEYS</strong> &ndash; definiert eine oder mehrere Spalten als eindeutigen Schlüssel, über den Datensätze identifiziert werden.</li>
<li><strong>APPLY AS DELETE WHEN</strong> &ndash; legt fest, unter welcher Bedingung ein eingehender Datensatz als Löschung interpretiert wird.</li>
<li><strong>SEQUENCE BY</strong> &ndash; bestimmt die Spalte, anhand derer verspätet eintreffende Datensätze korrekt in der richtigen Reihenfolge verarbeitet werden.</li>
<li><strong>COLUMNS ... EXCEPT (...)</strong> &ndash; wählt aus, welche Spalten übernommen werden sollen; hier werden alle außer der reinen Steuerspalte <code>operation</code> übernommen.</li>
<li><strong>STORED AS SCD TYPE 1</strong> &ndash; legt die Historisierungsstrategie fest (Type 1 ist zugleich der Standardwert, wenn diese Klausel weggelassen wird).</li>
</ul>
<p><code>AUTO CDC INTO</code> übernimmt dabei automatisch mehrere Garantien: inkrementelle/streamende Verarbeitung der CDC-Daten, korrekte Behandlung verspätet eintreffender Datensätze anhand des Sequenzfelds sowie eine einfache Syntax zum Ausschließen von Spalten über <code>EXCEPT</code>.</p>

<h2>5. Ein Praxisbeispiel mit konkreten Zahlen</h2>
<p>In einem Beispiel-Kundendatensatz enthielt die erste Datei 939 neue Kunden, die vollständig als Inserts in die leere Zieltabelle übernommen wurden. Eine zweite, nachgelagerte Datei mit 23 Änderungen enthielt 12&nbsp;Updates, 1&nbsp;Delete und 10&nbsp;neue Kunden. Nach der Verarbeitung zeigte die Zieltabelle exakt <code>939&nbsp;+&nbsp;10&nbsp;&minus;&nbsp;1&nbsp;=&nbsp;948</code> Zeilen &ndash; die 12 Updates wurden direkt an Ort und Stelle überschrieben, ohne dass die vorherigen Werte irgendwo erhalten blieben. Das ist das charakteristische Verhalten von SCD Type 1: Nur der aktuelle Zustand zählt.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Die vollständige Syntaxreferenz von <code>AUTO CDC INTO</code> umfasst neben den hier gezeigten Klauseln weitere optionale Elemente: <code>IGNORE NULL UPDATES</code> (NULL-Werte in eingehenden Updates ignorieren statt zu übernehmen), <code>APPLY AS TRUNCATE WHEN</code> (nur für SCD Type&nbsp;1 unterstützt, zum Verarbeiten vollständiger Tabellen-Truncate-Operationen der Quelle) sowie <code>TRACK HISTORY ON</code> für granulare Steuerung, welche Spalten bei SCD Type&nbsp;2 historisiert werden. <code>STORED AS SCD TYPE 1</code> ist der Standardwert und muss daher nicht zwingend explizit angegeben werden.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-apply-changes-into">AUTO CDC INTO (pipelines) &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\05 Change Data Capture Grundlagen - AUTO CDC und SCD Type 1.pdf",
    title="Change Data Capture Grundlagen (AUTO CDC, SCD Type 1)",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: Kurs 3, Kapitel 11&ndash;12, 14",
    body_html=body,
    build_name="03_05_cdc_grundlagen",
)
print("OK")
