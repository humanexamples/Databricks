# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Weil jede Änderung an einer Delta-Tabelle im Transaktionsprotokoll festgehalten wird (siehe vorheriges Kapitel), lässt sich der komplette Verlauf einer Tabelle nachvollziehen &ndash; und sogar rückgängig machen. Dieses Kapitel behandelt die drei praktischen Werkzeuge dafür: <strong>Time Travel</strong>, <strong>RESTORE TABLE</strong> und <strong>VACUUM</strong>.</p>

<h2>1. Die Tabellenhistorie einsehen</h2>
<p>Mit <code>DESCRIBE HISTORY</code> lässt sich der vollständige Audit-Trail einer Tabelle abfragen &ndash; jede Version mit Zeitstempel, ausführender Person, Operation und betroffenen Dateien:</p>
{code('sql', '''DESCRIBE HISTORY my_table;''')}

<h2>2. Time Travel: ältere Versionen abfragen</h2>
<p>Auf Basis dieser Historie lässt sich jede frühere Version einer Tabelle gezielt abfragen &ndash; entweder über einen Zeitstempel oder über die fortlaufende Versionsnummer:</p>
{code('sql', '''-- Per Zeitstempel
SELECT * FROM my_table TIMESTAMP AS OF "2019-01-01";

-- Per Versionsnummer (zwei gleichwertige Schreibweisen)
SELECT * FROM my_table VERSION AS OF 36;
SELECT * FROM my_table@v36;''')}
<p>Das ist besonders nützlich, um den Zustand einer Tabelle vor einer bestimmten Änderung zu vergleichen oder nachträglich zu prüfen, welche Werte zu einem früheren Zeitpunkt tatsächlich vorlagen.</p>

<h2>3. Fehler rückgängig machen: RESTORE TABLE</h2>
<p>Hat z. B. ein fehlerhafter Pipeline-Lauf versehentlich Datensätze gelöscht oder überschrieben, lässt sich die gesamte Tabelle mit einem einzigen Befehl auf einen früheren, bekannt guten Zustand zurücksetzen:</p>
{code('sql', '''RESTORE TABLE my_table TO TIMESTAMP AS OF "2019-01-01";
RESTORE TABLE my_table TO VERSION AS OF 36;''')}
<p><code>RESTORE</code> ist dabei selbst nur eine weitere Transaktion: Es werden keine Dateien rückwirkend verändert, sondern anhand des Protokolls ermittelt, welche Dateien zur Zielversion gehörten, und diese Information als neuer, aktueller Log-Eintrag festgeschrieben &ndash; entsprechend schnell ist der Vorgang auch bei großen Tabellen.</p>

<h2>4. Dateien kompaktieren und indizieren (Kurzüberblick)</h2>
<p>Delta Lake kann viele kleine Dateien mit dem <code>OPTIMIZE</code>-Befehl zu größeren, effizienter lesbaren Dateien zusammenfassen (Compaction) und optional zusätzlich per <code>ZORDER BY</code> nach einer Spalte co-lokalisieren, um Data-Skipping-Algorithmen zu beschleunigen:</p>
{code('sql', '''OPTIMIZE my_table;
OPTIMIZE my_table ZORDER BY id;''')}
<p>Die Details zu Z-Ordering, Partitionierung und dem moderneren Liquid Clustering &ndash; inklusive der jeweiligen Vor- und Nachteile &ndash; behandelt <strong>Section 6, Kapitel 2&ndash;3</strong> dieser Dokumentation ausführlich.</p>

<h2>5. Aufräumen: VACUUM</h2>
<p>Da Delta Lake bei Updates und Löschungen alte Dateien nicht sofort physisch entfernt (siehe Copy-on-Write im vorigen Kapitel), sammeln sich mit der Zeit nicht mehr benötigte Dateien an &ndash; sowohl aus nicht mehr referenzierten alten Tabellenversionen als auch aus fehlgeschlagenen, unvollständigen Schreibvorgängen. Der <code>VACUUM</code>-Befehl entfernt genau diese verwaisten Dateien:</p>
{code('sql', '''-- Alle Dateien entfernen, die aelter als die Aufbewahrungsfrist sind (Standard: 7 Tage)
VACUUM my_table;

-- Explizite Aufbewahrungsfrist in Stunden angeben
VACUUM my_table RETAIN 168 HOURS;''')}
<p>Die Standard-Aufbewahrungsfrist beträgt <strong>7 Tage</strong> &ndash; das ist bewusst so gewählt, damit noch laufende, länger dauernde Lesevorgänge nicht plötzlich auf gelöschte Dateien verweisen. Der entscheidende Merksatz für die Prüfung: <strong>Nach einem VACUUM ist Time Travel für Versionen älter als die Aufbewahrungsfrist nicht mehr möglich</strong> &ndash; die zugehörigen physischen Dateien existieren schlicht nicht mehr, unabhängig davon, was das Transaktionsprotokoll noch darüber weiß.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Die Aufbewahrungsfrist für <code>VACUUM</code> wird technisch über die Tabelleneigenschaft <code>delta.deletedFileRetentionDuration</code> gesteuert (Standardwert 7 Tage); Databricks rät ausdrücklich davon ab, diesen Wert zu unterschreiten. Getrennt davon regelt <code>delta.logRetentionDuration</code> (Standard 30 Tage), wie lange die JSON-Protokolldateien selbst aufbewahrt werden. Für <code>RESTORE TABLE</code> gilt: Die Wiederherstellung funktioniert nur, solange die zugehörigen Datendateien noch nicht durch ein <code>VACUUM</code> gelöscht wurden.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/delta/vacuum">Remove unused data files with vacuum &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 1 - Databricks Intelligence Plattform\04 Time Travel und VACUUM bei Delta Lake.pdf",
    title="Time Travel und VACUUM bei Delta Lake",
    subtitle="Section 1 &middot; Databricks Intelligence Plattform &middot; Quelle: Udemy-Kursmaterial &bdquo;Advanced Delta Lake Features&ldquo;, erg&auml;nzt mit Databricks-Dokumentation",
    body_html=body,
    build_name="gap_s1_timetravel",
)
print("OK")
