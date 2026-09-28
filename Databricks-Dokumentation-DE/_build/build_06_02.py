# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Wie schnell eine Abfrage auf einer Delta-Tabelle läuft, hängt maßgeblich davon ab, wie die zugrunde liegenden Dateien physisch organisiert sind. Dieses Kapitel behandelt drei klassische Techniken zur Optimierung des <strong>Datenlayouts</strong>: Data Skipping, Z-Ordering und Partitionierung &ndash; sowie die Statistiken im Transaktionsprotokoll, auf denen sie beruhen. Sie bilden die konzeptionelle Grundlage für Liquid Clustering, das in Kapitel 06-3 behandelt wird und diese Techniken bei neuen Tabellen inzwischen weitgehend ablöst.</p>

<h2>1. Data Skipping: Dateien ungelesen überspringen</h2>
<p><strong>Data Skipping</strong> ist eine Optimierung, bei der Spark Dateien (oder Teile davon) gar nicht erst öffnet, wenn feststeht, dass sie keine für die Abfrage relevanten Daten enthalten können. Möglich wird das durch Statistiken, die Delta Lake beim Schreiben pro Datei sammelt &ndash; typischerweise Minimum- und Maximum-Werte, Null-Zähler und Zeilenzahlen je Spalte. Diese Statistiken liegen nicht in den Dateien selbst, sondern im <strong>Transaktionsprotokoll</strong> (Delta Log). Enthält eine Abfrage einen Filter wie <code>WHERE datum = '2026-07-01'</code>, prüft Spark zunächst die Metadaten: Überschneidet sich der Min/Max-Bereich einer Datei nicht mit dem gesuchten Wert, wird die Datei komplett übersprungen &ndash; ganz ohne Festplattenzugriff.</p>

{code('sql', '''-- Minimal- und Maximalwerte je Datei ermitteln (illustriert das Prinzip hinter Data Skipping)
SELECT
    input_file_name() AS file_name,
    min(col) AS col_min,
    max(col) AS col_max
FROM table
GROUP BY input_file_name();''')}

<p>Der Nutzen ist unmittelbar einleuchtend: weniger I/O bedeutet schnellere Abfragen, insbesondere bei großen Tabellen mit vielen Dateien. Data Skipping funktioniert am besten, wenn die Daten physisch nach den Spalten geclustert sind, auf die häufig gefiltert wird &ndash; genau hier setzen Z-Ordering und Partitionierung an.</p>

<h2>2. Statistiken im Transaktionsprotokoll</h2>
<p>Damit Data Skipping und Z-Ordering überhaupt funktionieren, muss Delta Lake zunächst Statistiken sammeln. Standardmäßig erfasst Databricks Delta Lake Min/Max-Werte für die <strong>ersten 32 Spalten</strong> einer Tabelle (Konfigurationsparameter <code>dataSkippingNumIndexedCols</code>). Manche Abfragen &ndash; etwa <code>SELECT max(col) FROM table</code> &ndash; lassen sich sogar rein aus den Metadaten beantworten, ganz ohne dass eine einzige Datenzeile gelesen werden muss.</p>
<p>Beim Filtern wendet Spark die verschiedenen Filterarten in einer festen Reihenfolge an: zuerst Partitionsfilter, dann Datenfilter (Data Skipping), zuletzt Pushed Filters. Zwei Einschränkungen sind zu beachten:</p>
<ul>
<li>Bei <strong>Timestamp-</strong> und <strong>String</strong>-Spalten können Präzisions- oder Trunkierungseffekte dazu führen, dass die Statistiken keine exakten Treffer liefern &ndash; Spark muss dann teilweise doch auf einen vollständigen Dateiscan zurückfallen.</li>
<li>Für Spalten mit sehr langen Strings sollten keine Statistiken gesammelt werden, da sie den Metadaten-Overhead unnötig aufblähen. Entweder werden solche Spalten hinter die ersten 32 Spalten verschoben (<code>ALTER TABLE ... CHANGE COLUMN ... AFTER col32</code>), oder die Anzahl indizierter Spalten wird direkt reduziert:</li>
</ul>

{code('sql', '''SET spark.databricks.delta.properties.defaults.dataSkippingNumIndexedCols = 3;''')}

<h2>3. Z-Ordering: Ähnliche Werte physisch zusammen ablegen</h2>
<p><strong>Z-Ordering</strong> organisiert die Daten einer Tabelle anhand einer oder mehrerer Spalten so, dass ähnliche Werte in denselben Dateien landen. Dabei wird jede Datei anschließend mit ihren Min/Max-Werten für die Z-Order-Spalte(n) im Dateifußbereich (z.&nbsp;B. bei Parquet) versehen. Filtert eine Abfrage nun auf die Z-Order-Spalte, kann Spark anhand dieser Statistiken gezielt genau die eine relevante Datei öffnen, statt mehrere Dateien &ldquo;auf Verdacht&rdquo; zu lesen. Der Effekt ist besonders stark bei Spalten mit vielen unterschiedlichen Werten (hoher Kardinalität).</p>
<p>Databricks empfiehlt inzwischen grundsätzlich <strong>Liquid Clustering</strong> anstelle von Z-Ordering für neue Tabellen (siehe Kapitel 06-3) &ndash; Z-Ordering bleibt aber weiterhin unterstützt und in bestehenden Umgebungen relevant.</p>

<h2>4. Partitionierung: Nutzen und Risiken</h2>
<p>Partitionierung ist die klassischste Layout-Technik: Daten werden anhand einer Spalte in physisch getrennte Verzeichnisse aufgeteilt, sodass Spark ganze Partitionen überspringen kann, statt einzelne Dateien zu prüfen. Databricks rät jedoch generell von Partitionierung ab, da sie in der Praxis häufig falsch eingesetzt wird &ndash; typische Folgen sind eine <strong>Explosion kleiner Dateien</strong> oder ungleichmäßig verteilte Daten (Data Skew).</p>

<figure class="img">
<img src="assets/06/over-partitioning.png">
<figcaption>Über-Partitionierung: eine zu granulare Partitionierungsspalte erzeugt viele winzige Dateien pro Partition &ndash; das erhöht den Metadaten-Overhead und verlangsamt Lesezugriffe.</figcaption>
</figure>

<p>Trotzdem gibt es sinnvolle Anwendungsfälle für Partitionierung:</p>
<ul>
<li><strong>Isolation von Daten getrennter Schemata</strong> (Multiplexing mehrerer Quellen in einer Tabelle).</li>
<li><strong>DSGVO/CCPA-Löschanfragen</strong>, bei denen typischerweise eine ganze Partition gelöscht werden soll (z.&nbsp;B. alle Daten eines bestimmten Tages).</li>
<li><strong>SCD Type 2</strong>, wo eine physische Trennung zwischen aktuellen und historischen Datensätzen die Performance verbessert.</li>
</ul>
<p>Wird Partitionierung eingesetzt, gelten folgende Faustregeln: eine Spalte mit <strong>niedriger Kardinalität</strong> wählen, um nicht zu viele winzige Dateien zu erzeugen; jede Partition sollte zwischen 1&nbsp;GB und 1&nbsp;TB groß sein; besonders sinnvoll ist Partitionierung erst bei Tabellen, die auf über 1&nbsp;TB anwachsen; üblicherweise wird nach einem Datum partitioniert. Z-Ordering lässt sich zusätzlich mit Partitionierung kombinieren, um Abfragen zu beschleunigen, die häufig auf eine zweite Spalte in der <code>WHERE</code>-Klausel filtern.</p>

{code('python', '''# Beispiel: Tabelle nach einer Spalte partitionieren
(df
 .write
 .mode('overwrite')
 .option("overwriteSchema", "true")
 .partitionBy('id')   # Partitionierung nach id
 .saveAsTable("iot_data_partitioned")
)''')}

<p>Mit <code>DESCRIBE HISTORY</code> lässt sich die entstandene Partitionierung nachvollziehen &ndash; im <code>operationParameters</code>-Feld erscheint die gewählte Partitionierungsspalte, im <code>operationMetrics</code>-Feld die tatsächliche Anzahl erzeugter Dateien (bei zu hoher Kardinalität der Partitionierungsspalte kann diese Zahl schnell in die Tausende gehen, wie im obigen Beispiel mit <code>id</code> als Partitionierungsspalte). Mit <code>SHOW PARTITIONS &lt;tabelle&gt;</code> lassen sich zudem alle vorhandenen Partitionen einer Tabelle auflisten.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Die aktuelle Databricks-Dokumentation empfiehlt, für neue Tabellen standardmäßig <strong>Liquid Clustering</strong> zu verwenden und explizite Partitionierung nur noch für die oben genannten Spezialfälle (Compliance-Löschungen, sehr große Tabellen mit stabilen Zugriffsmustern) einzusetzen. Wird dennoch partitioniert, sollte die Partitionierungsspalte niedrige Kardinalität besitzen und regelmäßig mit <code>OPTIMIZE</code> kombiniert werden, um Small-File-Probleme zu vermeiden.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/tables/partitions">When to partition tables on Databricks &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 6 - Troubleshooting, Monitoring and Optimization\02 Datenlayout - Data Skipping, Z-Ordering, Partitionierung.pdf",
    title="Datenlayout: Data Skipping, Z-Ordering, Partitionierung",
    subtitle="Section 6 &middot; Troubleshooting, Monitoring and Optimization &middot; Quelle: Kurs 7, Kapitel 2.2.1&ndash;2.2.4",
    body_html=body,
    build_name="06_02_datenlayout",
)
print("OK")
