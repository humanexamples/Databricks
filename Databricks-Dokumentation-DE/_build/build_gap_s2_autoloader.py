# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Ein früheres Kapitel dieser Section hat Auto Loader bereits im Zusammenspiel mit Streaming Tables eingeführt. Für die Prüfung sind darüber hinaus drei Details entscheidend: wie Auto Loader neue Dateien überhaupt <em>erkennt</em> (zwei unterschiedliche Betriebsmodi), wie er auf <em>Schema-Abweichungen</em> reagiert (Enforcement vs. Evolution), und wie sich das Verhalten gezielt konfigurieren lässt.</p>

<h2>1. Zwei Erkennungsmodi: Directory Listing vs. File Notification</h2>
<p>Auto Loader muss bei jedem Lauf herausfinden, welche Dateien im Quellverzeichnis neu hinzugekommen sind. Dafür stehen zwei Modi zur Verfügung:</p>
<ul>
<li><strong>Directory Listing</strong> (Standard) &ndash; Auto Loader listet das Quellverzeichnis inkrementell auf und vergleicht das Ergebnis mit einem intern geführten Zustand bereits verarbeiteter Dateien. Vorteil: funktioniert ohne jede Zusatzkonfiguration. Nachteil: bei sehr vielen Dateien/Unterverzeichnissen wird das Auflisten selbst zum Flaschenhals.</li>
<li><strong>File Notification</strong> &ndash; Auto Loader abonniert stattdessen Ereignis-Benachrichtigungen des Cloud-Speichers (z. B. AWS S3-Events über SQS, Azure Event Grid mit Queue, GCP Pub/Sub) und erfährt so sofort und ohne Auflisten, wenn eine neue Datei ankommt. Das ist schneller und günstiger bei sehr großen, tief verschachtelten oder häufig wachsenden Verzeichnissen, erfordert aber die Einrichtung der entsprechenden Cloud-Infrastruktur (Event-Quelle, Warteschlange).</li>
</ul>
{code('python', '''(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.useNotifications", "true")   # File-Notification-Modus aktivieren
  .option("cloudFiles.queueUrl", "<sqs-queue-url>")  # nur bei AWS/SQS nötig
  .load("/Volumes/catalog/schema/raw_events"))''')}

<h2>2. Schema Enforcement: Abweichungen werden nicht stillschweigend ignoriert</h2>
<p>Sobald Auto Loader ein Schema kennt (aus einem inferierten oder explizit angegebenen Schema), wird jede eingehende Datei dagegen geprüft. Enthält eine Datei unerwartete zusätzliche Spalten, landen diese &ndash; statt verworfen zu werden &ndash; automatisch in der <code>_rescued_data</code>-Spalte als JSON-String. Damit geht bei einer Schema-Abweichung nie Information verloren, ohne dass der Ingest-Prozess deswegen abbricht.</p>

<h2>3. Schema Evolution: Wie Auto Loader auf neue Spalten reagiert</h2>
<p>Über die Option <code>cloudFiles.schemaEvolutionMode</code> lässt sich steuern, was passieren soll, wenn Auto Loader eine neue Spalte entdeckt, die im bisherigen Schema noch nicht vorkam:</p>
<table>
<tr><th>Modus</th><th>Verhalten bei neuer Spalte</th></tr>
<tr><td><code>addNewColumns</code> (Standard)</td><td>Der Stream wird gestoppt, das Schema um die neue Spalte erweitert, der Stream muss neu gestartet werden.</td></tr>
<tr><td><code>rescue</code></td><td>Neue Spalten werden nicht ins Schema aufgenommen, sondern landen dauerhaft in <code>_rescued_data</code>.</td></tr>
<tr><td><code>failOnNewColumns</code></td><td>Der Stream schlägt fehl und muss mit einem manuell aktualisierten Schema neu gestartet werden.</td></tr>
<tr><td><code>none</code></td><td>Neue Spalten werden ignoriert (landen nicht einmal in <code>_rescued_data</code>) &ndash; nur sinnvoll, wenn ein explizites Schema samt <code>schemaHints</code> vorgegeben wird.</td></tr>
</table>
{code('python', '''(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_schema/orders")
  .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
  .option("cloudFiles.schemaHints", "order_id INT, amount DOUBLE")
  .load("/Volumes/catalog/schema/raw/orders"))''')}
<p>Die Option <code>cloudFiles.schemaLocation</code> ist dabei Pflicht, sobald Auto Loader das Schema selbst ableiten oder weiterentwickeln soll &ndash; dort wird das aktuell erkannte Schema zwischen den Läufen persistiert.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks empfiehlt File-Notification-Modus für die meisten produktiven Workloads mit großen, wachsenden Datenmengen, da er schneller und kosteneffizienter skaliert als Directory Listing &ndash; Directory Listing bleibt aber der Standard, da er ohne jede Cloud-Infrastruktur-Einrichtung sofort funktioniert. Zusätzlich unterstützt Auto Loader seit neuerem automatische Typ-Erweiterung (<code>addNewColumnsWithTypeWidening</code>): Ändert sich z. B. eine Spalte von <code>int</code> zu <code>long</code>, wird der Datentyp automatisch erweitert, ohne dass bestehende Daten neu geschrieben werden müssen.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema">Configure schema inference and evolution in Auto Loader &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 2 - Data Ingestion and Loading\06 Auto Loader vertieft - Schema Enforcement, Evolution und Erkennungsmodi.pdf",
    title="Auto Loader vertieft: Schema Enforcement, Schema Evolution und Erkennungsmodi",
    subtitle="Section 2 &middot; Data Ingestion and Loading &middot; Quelle: Databricks-Dokumentation (Auto Loader)",
    body_html=body,
    build_name="gap_s2_autoloader",
)
print("OK")
