# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Das vorangegangene Kapitel dieser Section hat Delta Lake bereits als Speicherschicht der Databricks-Plattform eingeführt. Dieses Kapitel öffnet die Motorhaube und erklärt den zentralen Mechanismus, der Delta Lake seine Zuverlässigkeit verleiht: das <strong>Transaktionsprotokoll</strong> (Delta Log).</p>

<h2>1. Delta Lake: Was es ist &ndash; und was nicht</h2>
<p>Delta Lake ist ein <strong>quelloffenes Speicher-Framework</strong>, keine proprietäre Technologie. Es ist eine <strong>Speicherschicht</strong>, kein eigenes Dateiformat und kein Speichermedium &ndash; darunter liegen weiterhin gewöhnliche Parquet-Dateien. Und es ist auch kein Data Warehouse oder Datenbankdienst, sondern das Fundament, auf dem sich eine <strong>Lakehouse-Architektur</strong> erst aufbauen lässt. Technisch ist Delta Lake eine Komponente, die als Teil des Databricks Runtime auf dem Cluster läuft: Erstellt man eine Delta-Tabelle, landen die eigentlichen Daten als eine oder mehrere Parquet-Dateien im Speicher &ndash; zusätzlich schreibt Delta Lake aber ein Transaktionsprotokoll mit.</p>

<figure class="img">
<img src="assets/s1/delta_lake_architecture.png">
<figcaption>Delta Lake läuft als Komponente des Databricks Runtime auf dem Cluster; im Speicher liegen sowohl die Datendateien als auch das Transaktionsprotokoll.</figcaption>
</figure>

<h2>2. Das Transaktionsprotokoll: Single Source of Truth</h2>
<p>Der <strong>Delta Log</strong> ist eine geordnete Aufzeichnung jeder einzelnen Transaktion, die jemals auf einer Tabelle ausgeführt wurde &ndash; abgelegt als fortlaufend nummerierte JSON-Dateien im Unterordner <code>_delta_log</code>. Jede committete Transaktion hält fest: welche Operation ausgeführt wurde (z. B. Insert oder Update), welche Bedingungen/Filter dabei galten, und welche Datendateien dadurch hinzugekommen oder entfernt wurden. Jede Leseanfrage an eine Delta-Tabelle prüft zuerst dieses Protokoll, um die aktuell gültige Version der Daten zu ermitteln &ndash; die Datendateien selbst werden nie direkt und ungeprüft gelesen.</p>

<h2>3. Wie Schreib- und Lesevorgänge zusammenspielen</h2>
<p>Vier Szenarien zeigen, warum dieser Mechanismus so robust ist:</p>
<ul>
<li><strong>Normaler Schreib-/Lesevorgang:</strong> Ein Schreibprozess legt Datendateien an und trägt anschließend einen neuen Log-Eintrag ein. Ein Leseprozess liest zuerst den Log und weiß dadurch genau, welche Dateien zur aktuellen Tabellenversion gehören.</li>
<li><strong>Update (Copy-on-Write):</strong> Delta Lake ändert eine bestehende Datei nie direkt. Stattdessen wird eine Kopie mit den aktualisierten Werten als neue Datei angelegt, und der neue Log-Eintrag vermerkt, dass die alte Datei nicht mehr Teil der aktuellen Version ist &ndash; sie wird nicht sofort gelöscht, sondern bleibt bis zu einem späteren <code>VACUUM</code> (siehe nächstes Kapitel) physisch bestehen.</li>
<li><strong>Gleichzeitige Schreib- und Lesevorgänge:</strong> Solange ein Schreibvorgang noch nicht committet (also noch kein neuer Log-Eintrag existiert), sieht ein parallel laufender Lesevorgang ausschließlich den zuletzt vollständig committeten Stand &ndash; nie einen unvollständigen Zwischenzustand.</li>
<li><strong>Fehlgeschlagene Schreibvorgänge:</strong> Bricht ein Schreibvorgang mit einem Fehler ab, wird schlicht kein neuer Log-Eintrag geschrieben. Eine dabei bereits teilweise geschriebene, unvollständige Datei bleibt zwar im Speicher liegen, wird aber von keinem Log-Eintrag referenziert und daher von keinem Leseprozess jemals gelesen.</li>
</ul>

<figure class="img">
<img src="assets/s1/delta_lake_updates.png">
<figcaption>Ein Update kopiert die betroffene Datei statt sie zu überschreiben (Copy-on-Write) und aktualisiert erst danach das Transaktionsprotokoll.</figcaption>
</figure>

<h2>4. Die Vorteile im Überblick</h2>
<ul>
<li><strong>ACID-Transaktionen</strong> auch auf reinem Objektspeicher (S3, ADLS, GCS), der von sich aus keine Transaktionsgarantien bietet.</li>
<li><strong>Skalierbare Metadatenverwaltung</strong> &ndash; auch bei Tabellen mit Milliarden Zeilen und Zehntausenden Dateien bleibt das Protokoll effizient abfragbar.</li>
<li><strong>Vollständiger Audit-Trail</strong> aller Änderungen, da jede Transaktion protokolliert wird (Basis für Time Travel, siehe nächstes Kapitel).</li>
<li>Aufbau auf <strong>offenen Standardformaten</strong> &ndash; Parquet für Daten, JSON für das Protokoll &ndash; statt auf einem proprietären Binärformat.</li>
</ul>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Um das wiederholte Auflisten aller JSON-Dateien bei sehr langer Historie zu vermeiden, schreibt Delta Lake automatisch alle 10 Commits eine binäre <strong>Checkpoint-Datei</strong> (Parquet-Format), die den kompletten Tabellenzustand zu diesem Zeitpunkt zusammenfasst &ndash; ein Leseprozess muss dann nur noch den letzten Checkpoint plus die seither hinzugekommenen JSON-Dateien auswerten, statt das gesamte Protokoll von Anfang an durchzugehen.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/delta/history">Work with Delta Lake table history &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 1 - Databricks Intelligence Plattform\03 Delta Lake - Transaktionsprotokoll und ACID-Garantien.pdf",
    title="Delta Lake: Transaktionsprotokoll und ACID-Garantien",
    subtitle="Section 1 &middot; Databricks Intelligence Plattform &middot; Quelle: Udemy-Kursmaterial &bdquo;Delta Lake&ldquo;, erg&auml;nzt mit Databricks-Dokumentation",
    body_html=body,
    build_name="gap_s1_deltalog",
)
print("OK")
