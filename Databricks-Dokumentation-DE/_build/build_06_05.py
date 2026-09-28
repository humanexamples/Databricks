# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Spark SQL- und DataFrame-Operationen sind hochgradig optimiert &ndash; sobald jedoch eine eigene <strong>User-Defined Function (UDF)</strong> ins Spiel kommt, insbesondere in Python, kann die Performance drastisch einbrechen. Dieses Kapitel erklärt, warum das so ist (Stichwort: Serialisierung), welche Alternativen es gibt und wann UDFs überhaupt sinnvoll sind.</p>

<h2>1. Warum Serialisierung ein Performance-Thema ist</h2>
<p>Damit eine benutzerdefinierte Funktion überhaupt auf einem verteilten Cluster ausgeführt werden kann, muss sie <strong>serialisiert</strong> und an jeden Executor im Cluster verteilt werden. Zusätzlich müssen die Parameter und der Rückgabewert der Funktion bei <em>jedem einzelnen Funktionsaufruf</em> &ndash; also für jede Zeile der verarbeiteten Daten &ndash; konvertiert werden. Dieser Overhead entsteht bei UDFs in jeder unterstützten Sprache, fällt bei <strong>Python-UDFs</strong> aber am stärksten ins Gewicht:</p>
<ul>
<li>Der Python-Code muss zunächst gepickelt werden (in ein für Python geeignetes Serialisierungsformat gebracht werden).</li>
<li>Spark muss in <em>jedem</em> Executor einen eigenen Python-Interpreter starten und am Leben erhalten.</li>
<li>Jede einzelne Zeile muss zwischen der JVM (in der die DataFrame-Engine läuft) und dem Python-Prozess hin- und herkonvertiert werden &ndash; dieser Overhead summiert sich bei großen Datenmengen erheblich.</li>
</ul>

<figure class="img">
<img src="assets/06/python-udf.png">
<figcaption>Der Datenaustausch zwischen der JVM und dem Python-Interpreter bei klassischen Python-UDFs verursacht pro Zeile zusätzlichen Serialisierungs-Overhead.</figcaption>
</figure>

<h2>2. UDFs als Optimierungsbarriere für Catalyst</h2>
<p>Ein zweiter, oft unterschätzter Nachteil: Der Catalyst-Optimizer (siehe Kapitel 06-1) kann den Code <em>vor</em> und <em>nach</em> einer UDF zwar weiterhin optimieren, den Inhalt der UDF selbst jedoch nicht &ndash; sie bleibt für Catalyst eine &bdquo;Black Box&ldquo;. Damit wird eine UDF innerhalb einer Transformationskette zu einer <strong>Analysebarriere</strong>, die verhindert, dass Catalyst übergreifende Optimierungen über den gesamten Ausführungsplan hinweg vornehmen kann.</p>

<h2>3. Empfehlungen</h2>
<ol>
<li><strong>UDFs möglichst ganz vermeiden.</strong> In den allermeisten Fällen lässt sich dieselbe Transformation mit den eingebauten, kontinuierlich optimierten und von der Community weiterentwickelten Spark-SQL-Funktionen (Higher-Order Functions) abbilden. Es lohnt sich, aktiv nach einer eingebauten Alternative zu suchen, bevor eine eigene UDF geschrieben wird.</li>
<li><strong>Wenn Python-UDFs unumgänglich sind</strong> (häufig der Fall bei Data-Scientist-Workloads mit bestehendem Python-Code), sollten <strong>Vektorisierte UDFs</strong> (Pandas UDFs) oder die neueren <strong>Apache-Arrow-optimierten Python-UDFs</strong> verwendet werden statt klassischer, zeilenweiser Python-UDFs. Beide arbeiten spaltenweise (vektorisiert) statt zeilenweise und reduzieren den Serialisierungs-Overhead erheblich.</li>
<li><strong>Bei Scala-UDFs</strong> sollten stattdessen Typed Transformations bevorzugt werden.</li>
<li><strong>Bestehende Business-Logik nicht künstlich über UDFs integrieren.</strong> Es lohnt sich fast immer, vorhandene Geschäftslogik direkt in nativen Spark-Code zu portieren, statt sie unverändert in eine UDF zu kapseln.</li>
</ol>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Klassische, zeilenweise Python-UDFs sind mit Abstand am langsamsten. Pandas-UDFs (vektorisiert, über Apache Arrow) können gegenüber zeilenweisen UDFs eine bis zu 100-fache Beschleunigung erzielen. Die neueren, nativen <strong>Arrow-optimierten Python-UDFs</strong> gehen noch einen Schritt weiter: Sie arbeiten direkt auf dem Arrow-Format, ohne den Umweg über Pandas- oder NumPy-Objekte, und sind dadurch nochmals rund 10&nbsp;% schneller sowie rund 40&nbsp;% speichersparender als klassische Pandas-UDFs. Selbst reguläre (nicht-vektorisierte) Python-UDFs profitieren spürbar von Arrow-Optimierung: Sie laufen dann rund 1,6-mal schneller als klassisch gepickelte UDFs, bei verketteten UDF-Aufrufen sogar bis zu 1,9-mal schneller. Aktiviert wird die Arrow-Optimierung für UDFs Session-weit über den Konfigurationsparameter <code>spark.sql.execution.pythonUDF.arrow.enabled</code>.<br>
Quelle: <a href="https://www.databricks.com/blog/introducing-arrow-udfs-pyspark-faster-leaner-replacement-pandas-udfs">Introducing Arrow UDFs in PySpark &ndash; Databricks-Blog</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 6 - Troubleshooting, Monitoring and Optimization\05 Serialisierung und UDF-Performance.pdf",
    title="Serialisierung und UDF-Performance",
    subtitle="Section 6 &middot; Troubleshooting, Monitoring and Optimization &middot; Quelle: Kurs 7, Kapitel 3.4",
    body_html=body,
    build_name="06_05_serialisierung_udf",
)
print("OK")
