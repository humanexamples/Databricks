# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Section 2 hat Auto Loader bereits im Kontext der Datei-Ingestion mit <code>spark.readStream</code> gezeigt, und Kapitel 1 dieser Section erwähnt Streaming Tables als Gold-Layer-Objekt. Dieses Kapitel liefert das fehlende Bindeglied dazwischen: die <strong>generische Spark-Structured-Streaming-API</strong> selbst &ndash; DataStreamReader und DataStreamWriter &ndash; unabhängig davon, ob die Quelle eine Datei, ein Delta-Table oder ein Message-Bus ist.</p>

<h2>1. Was ist ein Datenstrom?</h2>
<p>Ein <strong>Datenstrom</strong> ist jede Datenquelle, die kontinuierlich wächst &ndash; etwa neue JSON-Dateien, die in Cloud-Speicher landen, per CDC erfasste Datenbankänderungen, oder Ereignisse in einer Pub/Sub-Warteschlange wie Kafka. Um solche Quellen zu verarbeiten, gibt es grundsätzlich zwei Ansätze: den kompletten Datensatz bei jeder Aktualisierung neu zu verarbeiten, oder gezielt nur die seit dem letzten Lauf neu hinzugekommenen Daten zu erfassen. <strong>Spark Structured Streaming</strong> ist die Engine, die den zweiten, effizienteren Ansatz umsetzt.</p>

<figure class="img">
<img src="assets/s3/streaming_source_sink.png">
<figcaption>Spark Structured Streaming liest kontinuierlich aus einer unendlichen Datenquelle und schreibt das Ergebnis inkrementell in eine dauerhafte Senke (Sink).</figcaption>
</figure>

<h2>2. Das Konzept der unbounded Table</h2>
<p>Der zentrale Kunstgriff von Structured Streaming: Ein kontinuierlich wachsender Datenstrom wird intern wie eine ganz normale, aber <strong>unbegrenzte Tabelle</strong> (&bdquo;unbounded table&ldquo;) behandelt. Jede neue Dateneinheit im Stream entspricht schlicht einer neuen Zeile, die dieser Tabelle angehängt wird. Dadurch lassen sich auf einem Streaming-DataFrame nahezu dieselben Transformationen anwenden wie auf einem gewöhnlichen, statischen DataFrame.</p>

<figure class="img">
<img src="assets/s3/streaming_unbounded_table.png">
<figcaption>Jede neue Dateneinheit im Eingabe-Stream wird als neue Zeile in eine gedanklich unbegrenzte Tabelle eingefügt.</figcaption>
</figure>

<h2>3. DataStreamReader und DataStreamWriter</h2>
<p>Delta-Tabellen lassen sich direkt als Streaming-Quelle verwenden: <code>spark.readStream</code> liest dabei nicht nur die bereits vorhandenen, sondern auch alle künftig hinzukommenden Zeilen der Quelltabelle. Das Ergebnis ist ein Streaming-DataFrame, das sich mit <code>writeStream</code> in eine Zieltabelle schreiben lässt:</p>
{code('python', '''streamDF = spark.readStream.table("Input_Table")

streamDF.writeStream \\
    .trigger(processingTime="2 minutes") \\
    .outputMode("append") \\
    .option("checkpointLocation", "/path") \\
    .table("Output_Table")''')}

<figure class="img">
<img src="assets/s3/streaming_input_output_table.png">
<figcaption>spark.readStream liest kontinuierlich aus der Eingabetabelle; writeStream schreibt das transformierte Ergebnis in festgelegten Intervallen in die Ausgabetabelle.</figcaption>
</figure>

<h2>4. Trigger-Intervalle: wann wird verarbeitet?</h2>
<p>Die <code>trigger</code>-Methode legt fest, <em>wann</em> Structured Streaming nach neuen Daten sucht und diese verarbeitet:</p>
<table>
<tr><th>Trigger</th><th>Aufruf</th><th>Verhalten</th></tr>
<tr><td>Nicht angegeben</td><td>&ndash;</td><td>Standard: alle 500&nbsp;ms prüfen (Micro-Batch)</td></tr>
<tr><td>Fixes Intervall</td><td><code>.trigger(processingTime="5 minutes")</code></td><td>Verarbeitung in Micro-Batches im angegebenen Intervall</td></tr>
<tr><td>Getriggerter Batch</td><td><code>.trigger(availableNow=True)</code></td><td>Verarbeitet alle verfügbaren Daten (in mehreren Micro-Batches) und stoppt danach von selbst</td></tr>
</table>
<p>Beide getriggerten Varianten eignen sich für inkrementelle Batch-Verarbeitung (siehe Section 2, Kapitel 8): Der Stream läuft, verarbeitet alle aktuell vorhandenen neuen Daten und beendet sich danach automatisch, statt dauerhaft weiterzulaufen.</p>

<h2>5. Output-Modi: wie wird geschrieben?</h2>
<table>
<tr><th>Modus</th><th>Aufruf</th><th>Verhalten</th></tr>
<tr><td><strong>Append</strong> (Standard)</td><td><code>.outputMode("append")</code></td><td>Nur neu hinzugekommene Zeilen werden inkrementell an die Zieltabelle angehängt</td></tr>
<tr><td><strong>Complete</strong></td><td><code>.outputMode("complete")</code></td><td>Die Zieltabelle wird bei jedem Batch komplett neu berechnet und überschrieben</td></tr>
</table>

<h2>6. Checkpointing: der Fortschritt eines Streams</h2>
<p>Über die Option <code>checkpointLocation</code> speichert Databricks den aktuellen Zustand eines Streaming-Jobs im Cloud-Speicher. Dieser Checkpoint erlaubt es der Engine, den Verarbeitungsfortschritt nachzuvollziehen &ndash; und nach einem Ausfall genau dort fortzusetzen, wo der Stream aufgehört hat. Wichtig für die Praxis: <strong>Ein Checkpoint kann nicht zwischen mehreren Streams geteilt werden</strong> &ndash; jeder einzelne Schreibvorgang (<code>writeStream</code>) benötigt einen eigenen, exklusiven Checkpoint-Pfad.</p>

<h2>7. Garantien: Fehlertoleranz und Exactly-Once</h2>
<p>Structured Streaming bietet zwei zentrale Garantien:</p>
<ul>
<li><strong>Fehlertoleranz</strong> &ndash; dank Checkpointing in Kombination mit <em>Write-Ahead-Logs</em>, die den verarbeiteten Offset-Bereich jedes Trigger-Intervalls festhalten, kann der Stream nach einem Ausfall exakt dort fortsetzen, wo er unterbrochen wurde.</li>
<li><strong>Exactly-Once-Verarbeitung</strong> &ndash; da Streaming-Senken als <em>idempotent</em> konzipiert sind, führt ein mehrfaches Schreiben derselben, anhand des Offsets identifizierten Daten nicht zu Duplikaten im Ziel.</li>
</ul>
<p>Beide Garantien setzen voraus, dass die Quelle <strong>wiederholbar</strong> ist (z. B. Cloud-Objektspeicher oder ein Pub/Sub-Dienst mit Offset-Verwaltung) &ndash; erst das Zusammenspiel aus wiederholbarer Quelle und idempotenter Senke ermöglicht echte Exactly-Once-Semantik über beliebige Fehlerfälle hinweg.</p>

<h2>8. Nicht unterstützte Operationen</h2>
<p>Auf einem Streaming-DataFrame lassen sich zwar die meisten Operationen genauso anwenden wie auf einem statischen DataFrame &ndash; einige Ausnahmen bestehen jedoch: <strong>Sortierung</strong> und <strong>Deduplizierung</strong> (siehe Section 3, Kapitel 13 zur Deduplizierung auf statischen DataFrames) sind auf einem unbegrenzten Datenstrom entweder zu aufwendig oder logisch nicht direkt möglich, da der vollständige Datensatz nie gleichzeitig vorliegt. Für solche Anwendungsfälle bietet Spark fortgeschrittene Methoden wie <strong>Windowing</strong> und <strong>Watermarking</strong> an, die zeitlich begrenzte Ausschnitte des Streams betrachten.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> <code>trigger(once=True)</code> gilt seit Databricks Runtime 11.3 LTS als <strong>deprecated</strong> &ndash; Databricks empfiehlt für sämtliche inkrementelle Batch-Workloads stattdessen durchgängig <code>trigger(availableNow=True)</code>, das inhaltlich denselben Zweck erfüllt (alle verfügbaren Daten verarbeiten, dann stoppen), dabei aber die Datenmenge in mehrere, besser steuerbare Micro-Batches aufteilen kann statt alles in einem einzigen Batch zu verarbeiten. Die Option <code>checkpointLocation</code> ist bei Verwendung von <code>trigger(availableNow=True)</code> zwingend erforderlich, damit jeder Lauf nachvollziehen kann, wo der vorherige Lauf aufgehört hat.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/structured-streaming/triggers">Configure Structured Streaming trigger intervals &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\16 Spark Structured Streaming - DataStreamReader und DataStreamWriter.pdf",
    title="Spark Structured Streaming: DataStreamReader und DataStreamWriter",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: Udemy-Kursmaterial &bdquo;Structured Streaming&ldquo;, erg&auml;nzt mit Databricks-Dokumentation",
    body_html=body,
    build_name="gap_s3_structuredstreaming",
)
print("OK")
