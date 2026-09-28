# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Kapitel 1 dieser Section hat <code>COPY INTO</code> und Auto Loader bereits im Überblick vorgestellt, Kapitel 6 die Schema-Mechanik von Auto Loader vertieft. Dieses Kapitel ergänzt die fehlende <strong>Entscheidungsgrundlage</strong>: konkrete Größenordnungen, ab wann welches Werkzeug sinnvoll ist, sowie eine bislang nicht gezeigte <code>COPY INTO</code>-Syntaxvariante mit <code>FORMAT_OPTIONS</code>.</p>

<h2>1. COPY INTO mit FORMAT_OPTIONS</h2>
<p>Neben <code>COPY_OPTIONS</code> (steuert das Verhalten des Ladevorgangs selbst, z. B. <code>mergeSchema</code>) unterstützt <code>COPY INTO</code> zusätzlich die Klausel <code>FORMAT_OPTIONS</code>, mit der sich Eigenschaften des <strong>Quelldateiformats</strong> festlegen lassen &ndash; etwa Trennzeichen oder ob die erste Zeile eine Kopfzeile ist:</p>
{code('sql', '''COPY INTO my_table
  FROM '/path/to/files'
  FILEFORMAT = CSV
  FORMAT_OPTIONS ('delimiter' = '|', 'header' = 'true')
  COPY_OPTIONS ('mergeSchema' = 'true');''')}

<figure class="img">
<img src="assets/s2/copy_into_format_options_example.png">
<figcaption>COPY INTO mit FORMAT_OPTIONS: steuert, wie die CSV-Quelldateien selbst gelesen werden (hier Pipe-Trennzeichen und Kopfzeile), unabhängig von COPY_OPTIONS für den Ladevorgang.</figcaption>
</figure>

<h2>2. Entscheidungskriterium: Dateianzahl</h2>
<p>Bei der Wahl zwischen <code>COPY INTO</code> und Auto Loader gibt Databricks eine konkrete Faustregel für die erwartete <strong>Größenordnung</strong> der eingehenden Dateien vor:</p>
<table>
<tr><th></th><th>COPY INTO</th><th>Auto Loader</th></tr>
<tr><td>Empfohlen ab</td><td>Dateien im Bereich von <strong>Tausenden</strong></td><td>Dateien im Bereich von <strong>Millionen oder mehr</strong></td></tr>
<tr><td>Verarbeitungskapazität</td><td>Weniger effizient bei sehr großer Skalierung</td><td>Kann laut Databricks auf <strong>Milliarden von Dateien</strong> skalieren, mit nahezu Echtzeit-Ingestion von <strong>Millionen Dateien pro Stunde</strong></td></tr>
<tr><td>Verarbeitungsmodus</td><td>Ein Batch pro Aufruf</td><td>Teilt die Verarbeitung automatisch in mehrere Micro-Batches auf, dadurch effizienter bei Skalierung</td></tr>
</table>
<p>Databricks empfiehlt Auto Loader entsprechend generell als <strong>Best Practice</strong> für die Ingestion aus Cloud-Objektspeicher, sobald mit wachsenden oder sehr großen Dateimengen zu rechnen ist &ndash; <code>COPY INTO</code> bleibt vor allem für überschaubare, wiederkehrende Batch-Ladevorgänge geeignet (siehe auch die Priorisierungsregel in Kapitel 8 dieser Section).</p>

<figure class="img">
<img src="assets/s2/copy_into_vs_autoloader.png">
<figcaption>Faustregel zur Werkzeugwahl: COPY INTO für Dateimengen im Tausenderbereich, Auto Loader ab Millionen von Dateien und für nahezu Echtzeit-Ingestion.</figcaption>
</figure>

<h2>3. Warum Auto Loader bei Skalierung effizienter ist</h2>
<p>Die Checkpointing-, Fehlertoleranz- und Exactly-Once-Mechanik von Auto Loader wurde bereits generisch in Section 3 (Kapitel zu Spark Structured Streaming) erklärt &ndash; sie gilt unverändert auch hier, da Auto Loader intern auf Structured Streaming aufbaut. Der Effizienzvorteil bei großen Dateimengen entsteht dadurch, dass Auto Loader neue Dateien nicht bei jedem Lauf vollständig aus dem Zielverzeichnis neu auflisten muss (siehe Erkennungsmodi in Kapitel 6), sondern den bereits verarbeiteten Zustand fortlaufend fortschreibt &ndash; <code>COPY INTO</code> muss dagegen bei jedem Aufruf den gesamten Quellpfad neu abgleichen, was mit wachsender Dateizahl zunehmend ins Gewicht fällt.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks führt als weiteres Abgrenzungskriterium an, dass <code>COPY INTO</code> sich für Datenquellen mit insgesamt wenigen Millionen Dateien eignet, während Auto Loader zusätzlich Vorteile bei der Dateierkennung (Directory Listing vs. File Notification, siehe Kapitel 6) und bei komplexen, sich häufig ändernden Verzeichnisstrukturen bietet. Beide Befehle sind zueinander nicht redundant: In produktiven Pipelines wird gelegentlich mit <code>COPY INTO</code> ein einmaliger historischer Backfill durchgeführt, während der laufende Betrieb anschließend auf Auto Loader umgestellt wird.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/">COPY INTO &ndash; Databricks-Dokumentation</a> &middot; <a href="https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/">What is Auto Loader? &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 2 - Data Ingestion and Loading\09 COPY INTO vs. Auto Loader - Entscheidungskriterien und Syntaxdetails.pdf",
    title="COPY INTO vs. Auto Loader: Entscheidungskriterien und Syntaxdetails",
    subtitle="Section 2 &middot; Data Ingestion and Loading &middot; Quelle: Udemy-Kursmaterial &bdquo;Incremental Data Ingestion from Files&ldquo;, erg&auml;nzt mit Databricks-Dokumentation",
    body_html=body,
    build_name="gap_s2_copyinto_vs_autoloader",
)
print("OK")
