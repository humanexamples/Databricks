# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Neben der korrekten Formulierung von Joins, Filtern und Aggregationen (Kapitel 11&ndash;13 dieser Section) verlangt der Exam Guide auch ein grundlegendes Verständnis der wichtigsten Spark-Tuning-Parameter: <code>spark.sql.shuffle.partitions</code>, <code>spark.default.parallelism</code>, die Speicherparameter <code>spark.executor.memory</code>/<code>spark.driver.memory</code> sowie <code>spark.sql.autoBroadcastJoinThreshold</code>. Dieses Kapitel erklärt jeden Parameter, nennt typische Werte und zeigt, wie sich eine Konfigurationsänderung anschließend &bdquo;vermessen&ldquo; lässt.</p>

<h2>1. spark.sql.shuffle.partitions</h2>
<p>Dieser Parameter legt fest, in wie viele Partitionen Daten bei einem Shuffle (also bei Wide Transformations wie <code>join()</code>, <code>groupBy()</code> oder <code>distinct()</code>) aufgeteilt werden. Der Standardwert beträgt <strong>200</strong> &ndash; ein Wert, der historisch für mittelgroße On-Premises-Cluster gewählt wurde und für viele moderne Workloads nicht mehr optimal ist. Zu viele Shuffle-Partitionen bei kleinen Datenmengen erzeugen unnötigen Overhead durch viele kleine Tasks; zu wenige Partitionen bei großen Datenmengen führen zu übergroßen Partitionen und damit potenziell zu Spill oder Out-of-Memory-Fehlern.</p>
{code('python', '''# aktuellen Wert auslesen
print(spark.conf.get("spark.sql.shuffle.partitions"))   # Standard: 200

# Wert anpassen, z.B. für einen kleineren Cluster mit wenigen Cores
spark.conf.set("spark.sql.shuffle.partitions", 32)''')}
{code('sql', '''SET spark.sql.shuffle.partitions = 32;''')}
<p>Auf Databricks übernimmt <strong>Adaptive Query Execution (AQE)</strong> seit Spark&nbsp;3.0 einen Großteil dieser Feinabstimmung automatisch: <code>spark.sql.shuffle.partitions</code> wird dabei zur Laufzeit dynamisch angepasst (Coalescing kleiner Partitionen), sodass eine manuelle Anpassung in den meisten Fällen gar nicht mehr notwendig ist. Für Workloads ohne AQE bzw. zum grundlegenden Verständnis bleibt der Parameter dennoch relevant.</p>

<h2>2. spark.default.parallelism</h2>
<p>Während <code>spark.sql.shuffle.partitions</code> ausschließlich für DataFrame-/SQL-Shuffles gilt, steuert <code>spark.default.parallelism</code> die Standard-Parallelität von <strong>RDD</strong>-Operationen (etwa <code>parallelize()</code> oder RDD-Joins/-Aggregationen) sowie den Default für Operationen ohne explizite Partitionsangabe. Der Standardwert richtet sich nach der Cluster-Größe: bei lokalem Modus nach der Anzahl der Cores der Maschine, im Cluster-Modus nach der Gesamtzahl aller verfügbaren Executor-Cores.</p>
{code('python', '''print(spark.sparkContext.defaultParallelism)   # z.B. 8 auf einer 8-Core-Maschine
spark.conf.set("spark.default.parallelism", 100)''')}
<p>In der täglichen Arbeit mit DataFrames (statt RDDs) spielt <code>spark.default.parallelism</code> eine untergeordnete Rolle gegenüber <code>spark.sql.shuffle.partitions</code> &ndash; für das Verständnis der Beziehung zwischen Cluster-Größe und Standard-Parallelität ist der Parameter dennoch Teil des Grundwissens.</p>

<h2>3. Speicherparameter: spark.executor.memory und spark.driver.memory</h2>
<p><code>spark.executor.memory</code> legt fest, wie viel Arbeitsspeicher jedem einzelnen Executor-Prozess für die Ausführung von Tasks zur Verfügung steht; <code>spark.driver.memory</code> entsprechend für den Treiberprozess, der u.&nbsp;a. den Ausführungsplan koordiniert und Ergebnisse von <code>collect()</code>-Aufrufen empfängt. Auf Databricks werden diese Werte in der Regel automatisch anhand des gewählten Cluster-/Instanztyps gesetzt, lassen sich bei Bedarf aber über die Cluster-Konfiguration (Spark-Config) oder programmatisch überschreiben.</p>
{code('python', '''# Hinweis: Speicherparameter müssen i.d.R. beim Start der Spark-Session/des Clusters
# gesetzt werden, da Executoren bereits mit einer festen Speichergrenze starten.
spark.conf.set("spark.executor.memory", "8g")
spark.conf.set("spark.driver.memory", "4g")''')}
<p>Ein zu knapp bemessenes <code>spark.executor.memory</code> äußert sich typischerweise in vermehrtem Spill (Daten werden auf Festplatte ausgelagert) oder in Out-of-Memory-Fehlern einzelner Tasks; ein zu knapp bemessenes <code>spark.driver.memory</code> macht sich vor allem bei großen <code>collect()</code>-Aufrufen oder komplexen Ausführungsplänen mit vielen Partitionen bemerkbar.</p>

<h2>4. spark.sql.autoBroadcastJoinThreshold</h2>
<p>Dieser Parameter bestimmt, ab welcher geschätzten Tabellengröße Spark bei einem Join <em>automatisch</em> einen Broadcast Join wählt (siehe Kapitel 11 zu Join-Typen), statt einen teuren Shuffle beider Tabellen durchzuführen. Der Standardwert beträgt <strong>10&nbsp;MB (10485760 Bytes)</strong>. Wird der Wert auf <code>-1</code> gesetzt, deaktiviert dies den automatischen Broadcast vollständig.</p>
{code('python', '''print(spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))   # Standard: 10485760 (10 MB)

# Schwellenwert erhöhen, z.B. auf 100 MB, wenn genügend Executor-Speicher vorhanden ist
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 100 * 1024 * 1024)

# automatischen Broadcast vollständig deaktivieren
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)''')}
{code('sql', '''SET spark.sql.autoBroadcastJoinThreshold = 104857600;  -- 100 MB''')}
<p>Ein höherer Schwellenwert kann bei Joins mit mittelgroßen Dimensionstabellen sinnvoll sein, erhöht aber auch das Risiko von Speicherproblemen auf den Executoren, falls die geschätzte Tabellengröße die tatsächliche unterschätzt (etwa nach komplexen vorgelagerten Transformationen).</p>

<h2>5. Eine Änderung &bdquo;re-messen&ldquo;: Vorgehen in der Praxis</h2>
<p>Der Exam Guide verlangt ausdrücklich, eine Parameteränderung anschließend hinsichtlich ihrer Wirkung zu überprüfen. In einem Databricks-Notebook bieten sich dafür zwei ergänzende Methoden an:</p>
<ol>
<li><strong>Zeitmessung mit <code>%timeit</code>:</strong> In einer Python-Notebookzelle lässt sich ein Transformationsschritt (inkl. einer abschließenden Aktion wie <code>count()</code>, da Spark sonst lazy bleibt) mehrfach automatisiert ausführen und die durchschnittliche Laufzeit ausgeben.</li>
<li><strong>Vergleich in der Spark-UI:</strong> Über den Reiter &bdquo;SQL / DataFrame&ldquo; lässt sich für jede Ausführung die Gesamtlaufzeit sowie &ndash; über die Stage-Detailseiten &ndash; Kennzahlen wie Shuffle Read/Write-Volumen und Spill einsehen und zwischen &bdquo;vorher&ldquo; und &bdquo;nachher&ldquo; vergleichen.</li>
</ol>
{code('python', '''# Beispiel: Auswirkung einer geänderten Shuffle-Partitionsanzahl messen
spark.conf.set("spark.sql.shuffle.partitions", 200)
%timeit grosse_tabelle.groupBy("kategorie").count().collect()

spark.conf.set("spark.sql.shuffle.partitions", 16)
%timeit grosse_tabelle.groupBy("kategorie").count().collect()

# %timeit fuehrt die Zelle standardmaessig mehrfach aus und meldet Mittelwert
# und Standardabweichung der Laufzeit -- so laesst sich der Effekt der
# Konfigurationsaenderung direkt quantitativ vergleichen.''')}
<p>Wichtig für belastbare Messungen: Zwischen den beiden Messungen sollte möglichst nur der zu testende Parameter verändert werden, und Caching-Effekte (etwa bereits im Speicher gehaltene Zwischenergebnisse) sollten berücksichtigt bzw. durch mehrfache Wiederholung ausgeglichen werden. Bei kleinen Testdatenmengen &ndash; wie sie in Übungsumgebungen üblich sind &ndash; fallen Unterschiede durch Tuning-Parameter oft nur gering aus; die eigentliche Wirkung zeigt sich meist erst bei produktionsnahen Datenmengen.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Spark-Dokumentation:</strong> Der &bdquo;Performance Tuning&ldquo;-Leitfaden von Apache Spark bestätigt für <code>spark.sql.shuffle.partitions</code> den Standardwert von 200 sowie den Hinweis, dass dieser Wert bei aktivierter Adaptive Query Execution (<code>spark.sql.adaptive.enabled</code>) zur Laufzeit automatisch angepasst wird. Für <code>spark.sql.autoBroadcastJoinThreshold</code> nennt die Dokumentation den Standardwert 10&nbsp;MB und weist ausdrücklich darauf hin, dass der Wert <code>-1</code> den automatischen Broadcast vollständig deaktiviert; aktuell werden zudem nur Tabellen unterstützt, für die <code>ANALYZE TABLE ... COMPUTE STATISTICS</code> ausgeführt wurde oder deren Größe der Dateistatistik entnommen werden kann.<br>
Quelle: <a href="https://spark.apache.org/docs/latest/sql-performance-tuning.html">Performance Tuning &ndash; Apache Spark Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\14 Performance-Tuning-Parameter fuer Transformationen.pdf",
    title="Performance-Tuning-Parameter für Transformationen",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: PySpark-/Databricks-Referenzdokumentation",
    body_html=body,
    build_name="03_14_performance_tuning_parameter",
)
print("OK")
