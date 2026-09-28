# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Drei der häufigsten Ursachen für langsame oder sogar abstürzende Spark-Jobs sind <strong>Data Skew</strong> (ungleich verteilte Daten), <strong>Shuffle</strong> (Datenumverteilung über das Netzwerk) und <strong>Spill</strong> (Auslagern von Arbeitsspeicher auf die Festplatte). Alle drei Phänomene hängen eng zusammen: Skew verstärkt Shuffle-Probleme, und beide können zu Spill führen. Dieses Kapitel erklärt, wie die drei Effekte entstehen, wie man sie im Spark UI erkennt und mit welchen Maßnahmen man ihnen begegnet.</p>

<h2>1. Data Skew: Wenn eine Partition alle anderen überragt</h2>
<p>Beim initialen Einlesen werden Daten typischerweise in 128&nbsp;MB große Partitionen aufgeteilt und gleichmäßig verteilt. Sobald jedoch transformiert wird &ndash; etwa durch eine Aggregation nach einer Schlüsselspalte &ndash; kann eine Partition erheblich mehr Datensätze enthalten als eine andere. Ein einfaches Beispiel: Werden Transaktionsdaten nach Stadt aggregiert und eine Stadt hat doppelt so viele Einwohner wie die übrigen, landet in ihrer Partition auch doppelt so viel Datenvolumen. Ein geringer Grad an Skew ist meist unproblematisch, starker Skew führt jedoch zu Spill oder sogar zu schwer diagnostizierbaren <strong>Out-of-Memory-Fehlern</strong>.</p>
<p>Die Konsequenz von Skew: Da eine Stage erst abgeschlossen ist, wenn die <em>langsamste</em> Task fertig ist, bestimmt die am stärksten überladene Partition die Gesamtlaufzeit der gesamten Stage &ndash; und unter Umständen reicht der verfügbare Arbeitsspeicher für diese eine Partition nicht mehr aus.</p>

<figure class="img">
<img src="assets/06/aqe-skew.png">
<figcaption>Adaptive Query Execution erkennt überproportional große Partitionen zur Laufzeit und teilt sie automatisch in kleinere, gleichmäßiger verteilte Stücke auf.</figcaption>
</figure>

<h3>Skew beheben: vier gestufte Strategien</h3>
<ol>
<li><strong>Skew-Werte herausfiltern</strong> &ndash; Ist der Skew auf einen bestimmten (häufig: <code>NULL</code>-)Wert zurückzuführen, etwa bei einem Join über eine Spalte mit vielen Nullwerten, löst ein einfacher Filter das Problem oft vollständig.</li>
<li><strong>Skew-Hints</strong> &ndash; Sind Tabelle, Spalte und idealerweise auch die betroffenen Werte bekannt, kann Spark über einen expliziten Hint mitgeteilt werden, dass hier Skew vorliegt, damit Spark das Problem gezielt behandeln kann.</li>
<li><strong>AQE-Skew-Optimierung</strong> &ndash; Seit Spark&nbsp;3.0 löst die Adaptive Query Execution Skew standardmäßig automatisch: Eine Partition gilt als &bdquo;skewed&ldquo;, wenn sie mindestens 256&nbsp;MB groß und mindestens fünfmal größer als die durchschnittliche Partitionsgröße ist. Diese Schwellenwerte lassen sich konfigurieren. Bei mehr als 2.000 Shuffle-Partitionen kann AQE Skew allerdings nicht mehr zuverlässig erkennen, da Spark dann nur noch Durchschnittswerte statt exakter Shuffle-Block-Größen verfolgt &ndash; hier hilft entweder eine Reduzierung der Shuffle-Partitionen unter 2.000 oder eine Anpassung der entsprechenden Spark-Konfiguration.</li>
<li><strong>Salting</strong> &ndash; Führt keine der vorherigen Maßnahmen zum Erfolg, bleibt als letztes Mittel das Salting: Den Werten der Skew-Spalte werden zufällige Suffixe angehängt, um eine große, ungleich verteilte Partition künstlich in mehrere kleinere, gleichmäßig verteilte Partitionen aufzuteilen.</li>
</ol>

<h2>2. Shuffle: Datenumverteilung über das Netzwerk</h2>
<p>Ein <strong>Shuffle</strong> tritt immer dann auf, wenn Daten am Ende einer Stage neu über das Netzwerk verteilt werden müssen, damit die nächste Stage darauf aufbauen kann &ndash; klassischerweise bei Operationen wie <code>join()</code>, <code>distinct()</code>, <code>groupBy()</code>, <code>orderBy()</code> oder bestimmten Aktionen wie <code>count()</code>. Solche Operationen werden als <strong>Wide Transformations</strong> bezeichnet, weil sie zwei Stages benötigen: In der ersten Stage (Map) wird vorbereitet, welche Daten wohin verschoben werden müssen; anschließend erfolgt der eigentliche Shuffle über das Netzwerk; in der zweiten Stage (Reduce) werden die neu angeordneten Daten weiterverarbeitet. Operationen ohne Shuffle heißen entsprechend <strong>Narrow Transformations</strong> und benötigen nur eine einzige Stage.</p>

<h3>Shuffle-Strategien bei Joins</h3>
<p>Welche konkrete Join-Strategie Spark wählt, hat großen Einfluss auf die Menge an Shuffle-Daten:</p>
<ul>
<li><strong>Broadcast Hash Join</strong> &ndash; Die kleinere Tabelle wird vollständig an alle Executor verteilt, wodurch ein teurer Shuffle der großen Tabelle entfällt. Ideal, wenn eine der beiden Tabellen klein genug in den Speicher passt.</li>
<li><strong>Shuffle Hash Join</strong> &ndash; Standard-Join-Strategie bei Databricks Photon.</li>
<li><strong>Sort-Merge Join</strong> &ndash; Standard-Join-Strategie im Open-Source-Spark ohne Photon.</li>
</ul>

<h3>Shuffle reduzieren: Empfehlungen</h3>
<ul>
<li>Wenige, dafür größere virtuelle Maschinen (mehr Cores) verwenden &ndash; die Kosten für Festplatten-I/O bleiben zwar bestehen, das Netzwerk-I/O sinkt jedoch.</li>
<li>Auf AQE und Dynamic Partition Pruning (DPP) verlassen, statt Datensätze manuell zu denormalisieren &ndash; beide Techniken machen viele frühere Denormalisierungs-Workarounds überflüssig.</li>
<li>Die zu shuffelnde Datenmenge reduzieren: unnötige Spalten frühzeitig entfernen, nicht benötigte Datensätze vorab herausfiltern.</li>
<li><strong>Bucketing</strong> nur mit Bedacht einsetzen &ndash; es eliminiert zwar den Sortierschritt im Sort-Merge-Join durch vorsortierte Partitionen, ist aber aufwendig korrekt umzusetzen und lohnt sich in der Regel erst ab Datenmengen von mehreren Terabyte.</li>
</ul>

<h2>3. Spill: Wenn der Arbeitsspeicher nicht ausreicht</h2>
<p><strong>Spill</strong> beschreibt, was passiert, wenn eine Datenmenge nicht mehr vollständig in den verfügbaren Arbeitsspeicher (RAM) passt: Ein Teil der Daten wird auf die Festplatte ausgelagert und bei Bedarf später wieder zurückgelesen. Da Festplattenzugriffe deutlich langsamer sind als Arbeitsspeicherzugriffe, verlangsamt Spill die Verarbeitung erheblich &ndash; findet dieser Auslagerungsprozess gar nicht erst statt und reicht der Speicher trotzdem nicht aus, kommt es zu einem Out-of-Memory-Fehler, der den gesamten Job zum Absturz bringt.</p>

<h3>Typische Ursachen für Spill</h3>
<ul>
<li><code>spark.sql.files.maxPartitionBytes</code> zu hoch eingestellt (Standardwert: 128&nbsp;MB) &ndash; führt zu überdimensionierten Partitionen.</li>
<li><code>explode()</code> selbst kleiner Arrays, wodurch deutlich mehr Zeilen entstehen als vorher vorhanden waren.</li>
<li><code>join()</code> oder <code>crossJoin()</code> zweier Tabellen, die eine große Zahl neuer Zeilen erzeugen &ndash; insbesondere bei Cross-Joins oder Joins auf Skew-Schlüsseln.</li>
<li><code>groupBy()</code> auf Spalten mit niedriger Kardinalität, <code>countDistinct()</code> oder <code>collect_set()</code>.</li>
<li><code>spark.sql.shuffle.partitions</code> zu niedrig gesetzt oder falsche Verwendung von <code>repartition()</code>.</li>
</ul>

<h3>Spill im Spark UI erkennen</h3>
<p>Spill wird ausschließlich auf der Detailseite einer einzelnen Stage angezeigt (in den zusammengefassten Metriken, den nach Executor aggregierten Metriken oder in der Tasks-Tabelle) bzw. in den entsprechenden Query-Details. Das macht Spill leicht zu übersehen &ndash; die Spalten für &bdquo;Spill (Memory)&ldquo; und &bdquo;Spill (Disk)&ldquo; erscheinen im UI überhaupt nur, wenn tatsächlich Spill vorliegt. Sind diese Spalten sichtbar, ist das bereits ein eindeutiges Warnsignal. Der Wert &bdquo;Spill (Disk)&ldquo; ist dabei stets kleiner als &bdquo;Spill (Memory)&ldquo;, da die Daten beim Schreiben auf die Festplatte automatisch komprimiert werden.</p>

<h3>Spill vermeiden: Gegenmaßnahmen</h3>
<ul>
<li>Cluster mit mehr RAM pro Core bereitstellen.</li>
<li>Data Skew beheben (siehe oben) &ndash; oft ist Skew die eigentliche Ursache eines Spill-Problems.</li>
<li>Größe der Spark-Partitionen gezielt steuern.</li>
<li>Teure Operationen wie <code>explode()</code> möglichst vermeiden.</li>
<li>Datenmenge frühzeitig reduzieren, wo immer möglich.</li>
</ul>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks empfiehlt, Skew-Probleme grundsätzlich <em>vor</em> Spill-Problemen zu beheben, da Skew häufig die eigentliche Ursache eines Spills ist. Als schnelle Diagnose gilt: Ist die maximale Task-Dauer einer Stage mehr als 50&nbsp;% höher als die Dauer des 75.&nbsp;Perzentils, liegt vermutlich Skew vor. Die &bdquo;Skew and Spill&ldquo;-Seite des Spark-UI-Guides beschreibt detailliert, welche Metriken auf der Stage-Detailseite zu prüfen sind.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/optimizations/spark-ui-guide/long-spark-stage-page">Skew and spill &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 6 - Troubleshooting, Monitoring and Optimization\04 Skew, Shuffle und Spill erkennen und beheben.pdf",
    title="Skew, Shuffle und Spill erkennen und beheben",
    subtitle="Section 6 &middot; Troubleshooting, Monitoring and Optimization &middot; Quelle: Kurs 7, Kapitel 3.1&ndash;3.3",
    body_html=body,
    build_name="06_04_skew_shuffle_spill",
)
print("OK")
