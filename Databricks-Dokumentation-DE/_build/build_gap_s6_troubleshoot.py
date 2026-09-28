# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Die vorangegangenen Kapitel dieser Section haben sich mit Performance-Problemen befasst, die auftreten, <em>während</em> ein Job läuft (Skew, Shuffle, Spill). Genauso wichtig für die Prüfung ist die zweite Kategorie von Problemen: Ein Cluster startet gar nicht erst richtig, oder er stürzt kurz nach dem Start ab &ndash; oft aus ganz anderen Gründen als reiner Datenmenge.</p>

<h2>1. Cluster-Startfehler diagnostizieren</h2>
<p>Wenn ein Cluster nicht in den Status <em>Running</em> gelangt, lohnt sich zuerst ein Blick auf die Fehlerkategorie, die Databricks im Cluster-Event-Log meldet:</p>
<ul>
<li><strong>Timeout beim Hochfahren</strong> &ndash; der Treiberknoten meldet sich nicht innerhalb des konfigurierten Zeitfensters zurück. Häufige Ursache: Init-Skripte oder das Herunterladen zusätzlicher Bibliotheken/Treiber (z. B. Hive-Metastore-JARs) dauert zu lange.</li>
<li><strong>Cloud-Provider-Limits</strong> &ndash; das Kontingent an verfügbaren Instanzen/vCPUs in der Region ist erschöpft, oder die angeforderte Instanzfamilie ist in der Verfügbarkeitszone gerade nicht verfügbar (häufig bei Spot-Instances).</li>
<li><strong>Init-Skript-Fehler</strong> &ndash; ein global oder clusterspezifisch hinterlegtes Init-Skript bricht mit einem Fehler ab (z. B. fehlende Datei, Berechtigungsproblem, defekter Download-Link) und verhindert dadurch den kompletten Start.</li>
<li><strong>Nicht erreichbarer Treiber</strong> &ndash; Netzwerk-/Firewall-Konfiguration verhindert die Kommunikation zwischen Control Plane und Compute Plane (häufig bei benutzerdefinierten VPC-/VNet-Einstellungen).</li>
</ul>
<p>Der erste Diagnoseschritt ist immer derselbe: das <strong>Cluster-Event-Log</strong> (Reiter &bdquo;Event Log&ldquo; in der Cluster-Detailansicht) sowie die <strong>Treiber-Logs</strong> (<code>stderr</code>/<code>stdout</code> unter &bdquo;Driver Logs&ldquo;) öffnen &ndash; dort steht in der Regel die konkrete Fehlermeldung, nicht nur der allgemeine Status &bdquo;Terminated&ldquo;.</p>

<h2>2. Bibliothekskonflikte erkennen und beheben</h2>
<p>Wird eine Bibliothek clusterweit installiert (z. B. über die UI, eine <code>requirements.txt</code> oder ein Init-Skript) und ist mit einer bereits im Databricks Runtime enthaltenen Version inkompatibel, kann das den Treiber bereits beim Start zum Absturz bringen &ndash; typisches Beispiel sind Binärkonflikte zwischen einer manuell installierten NumPy/Pandas-Version und den C-Erweiterungen, die fest im Runtime-Image verankert sind.</p>
{code('python', '''# Systematisches Vorgehen bei Verdacht auf Bibliothekskonflikt:
# 1. Cluster OHNE automatische Bibliotheksinstallation starten -> startet er normal?
# 2. Falls ja: Bibliotheken einzeln nacheinander hinzufügen, nach jedem Schritt neu starten
# 3. Sobald der Fehler wieder auftritt, ist die zuletzt hinzugefügte Bibliothek die Ursache
# 4. Lösung meist: exakte, im Runtime mitgelieferte Version verwenden statt "neueste" Version''')}
<p>Bei clusterweit über ein Init-Skript installierten Bibliotheken lohnt sich zusätzlich ein Blick in die Treiber-Logs auf Meldungen wie <code>ImportError</code> oder <code>version conflict</code> direkt nach dem Start &ndash; diese verraten meist exakt, welche zwei Paketversionen kollidieren.</p>

<h2>3. Out-of-Memory-Fehler diagnostizieren</h2>
<p>Ein <strong>OOM-Fehler</strong> (Out of Memory) kann sowohl den Treiber als auch einzelne Executor betreffen &ndash; die Ursache und die Abhilfe unterscheiden sich:</p>
<table>
<tr><th>Symptom</th><th>Typische Ursache</th><th>Abhilfe</th></tr>
<tr><td>Driver OOM</td><td><code>collect()</code>, <code>toPandas()</code> oder große Broadcast-Variablen holen zu viele Daten auf den Treiberknoten</td><td>Aggregation/Filterung vor dem Sammeln, größeren Treiber wählen, Broadcast-Threshold senken</td></tr>
<tr><td>Executor OOM</td><td>Data Skew, zu wenige Shuffle-Partitionen, teure Operationen wie <code>explode()</code> oder <code>collect_set()</code></td><td>siehe Kapitel zu Skew/Shuffle/Spill dieser Section; mehr RAM pro Core bereitstellen</td></tr>
<tr><td>Wiederholte OOM-Kills während des Cluster-Starts</td><td>Zu kleine Instanztypen für die installierten Bibliotheken/Init-Skripte selbst (z. B. speicherintensive ML-Bibliotheken)</td><td>größeren Treiber-/Worker-Instanztyp wählen</td></tr>
</table>
<p>Die Spark-UI-Reiter <strong>Executors</strong> (Speicherauslastung je Executor) und <strong>Stages</strong> (Spill-Metriken, siehe vorheriges Kapitel) sind auch hier die erste Anlaufstelle, bevor die Cluster-Größe vorschnell erhöht wird &ndash; oft liegt die eigentliche Ursache im Code oder im Datenlayout, nicht in zu wenig Hardware.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks nennt als häufigste Ursachen für gescheiterte Cluster-Starts Timeouts, fehlerhafte globale oder clusterspezifische Init-Skripte, zu viele gleichzeitig installierte Bibliotheken, Cloud-Provider-Limits sowie nicht erreichbare Instanzen. Als erster Diagnoseschritt wird empfohlen, den Cluster testweise komplett ohne automatische Bibliotheksinstallation zu starten, um festzustellen, ob überhaupt ein Bibliothekskonflikt vorliegt, bevor einzelne Bibliotheken schrittweise wieder ergänzt werden.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/compute/troubleshooting/">Troubleshoot compute issues &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 6 - Troubleshooting, Monitoring and Optimization\07 Cluster-Startprobleme, Bibliothekskonflikte und Out-of-Memory-Diagnose.pdf",
    title="Cluster-Startprobleme, Bibliothekskonflikte und Out-of-Memory-Diagnose",
    subtitle="Section 6 &middot; Troubleshooting, Monitoring and Optimization &middot; Quelle: Databricks-Dokumentation (Compute Troubleshooting)",
    body_html=body,
    build_name="gap_s6_troubleshoot",
)
print("OK")
