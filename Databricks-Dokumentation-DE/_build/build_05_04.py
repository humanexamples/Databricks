# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Structured Streaming geht grundsätzlich davon aus, dass Quelltabellen nur angehängt (append-only) werden &ndash; Updates und Deletes an bereits gelesenen Daten passen nicht in dieses Modell. Genau hier setzt <strong>Change Data Feed (CDF)</strong> an: CDF verfolgt Zeilen-Änderungen zwischen Versionen einer Delta-Tabelle und macht Inserts, Updates und Deletes als eigenen, inkrementell lesbaren Datenstrom verfügbar. Für Datenschutz-Anwendungsfälle ist das unverzichtbar &ndash; insbesondere um Löschanfragen ("Recht auf Vergessenwerden") zuverlässig von einer Quelltabelle in alle nachgelagerten Tabellen zu propagieren.</p>

<h2>1. Change Data Feed aktivieren</h2>
<p>CDF ist standardmäßig <strong>nicht</strong> aktiviert und muss explizit eingeschaltet werden &ndash; entweder für einzelne Tabellen per <code>ALTER TABLE</code> oder global für alle künftig neu erstellten Tabellen.</p>

{code('sql', '''-- Fuer eine bestehende Tabelle aktivieren
ALTER TABLE silver_users
SET TBLPROPERTIES (delta.enableChangeDataFeed = true);

-- Aktivierung pruefen
DESCRIBE TABLE EXTENDED silver_users;
-- ... [delta.enableChangeDataFeed=true] sollte unter Table Properties erscheinen''')}

{code('python', '''# Global fuer alle neuen Tabellen der Session aktivieren
spark.conf.set("spark.databricks.delta.properties.defaults.enableChangeDataFeed", True)''')}

<p>Sobald CDF aktiv ist, enthält jede Abfrage der Änderungshistorie drei zusätzliche Metadatenspalten:</p>
<table>
<tr><th>Spalte</th><th>Typ</th><th>Bedeutung</th></tr>
<tr><td><code>_change_type</code></td><td>String</td><td><code>insert</code>, <code>delete</code>, <code>update_preimage</code>, <code>update_postimage</code></td></tr>
<tr><td><code>_commit_version</code></td><td>Long</td><td>Delta-Log-Version, in der die Änderung committet wurde</td></tr>
<tr><td><code>_commit_timestamp</code></td><td>Timestamp</td><td>Zeitpunkt des Commits</td></tr>
</table>
<p>Bei Updates erscheinen für jede geänderte Zeile zwei Einträge: <code>update_preimage</code> zeigt den Zustand vor, <code>update_postimage</code> den Zustand nach der Änderung.</p>

<figure class="img">
<img src="assets/05/cdf-output-example.png">
<figcaption>Change Data Feed am Beispiel: aus dem Vergleich zweier Tabellenversionen entsteht eine Ausgabe mit Change Type, Zeitstempel und Version je betroffener Zeile.</figcaption>
</figure>

<h2>2. Änderungen lesen: Streaming oder table_changes()</h2>
<p>Es gibt zwei Wege, CDF zu konsumieren. Für kontinuierliche Verarbeitung eignet sich ein Stream mit der Option <code>readChangeFeed</code> und <code>startingVersion</code>:</p>

{code('python', '''cdf_df = (spark.read
               .format("delta")
               .option("readChangeFeed", "true")
               .option("startingVersion", 2)   # ab welcher Version gelesen werden soll
               .table("silver_users"))

display(cdf_df)''')}

<p>Für punktuelle Batch-Abfragen &ndash; etwa "was hat sich seit dem letzten Lauf geändert?" &ndash; eignet sich die SQL-Tabellenfunktion <code>table_changes(table_str, start [, end])</code>, die einen Ausschnitt der Änderungshistorie als normale Tabelle zurückgibt:</p>

{code('sql', '''-- Alle in der letzten Version eingefuegten Zeilen
SELECT *
FROM table_changes("silver_users", latest_version)
WHERE _change_type = "insert"
ORDER BY _commit_version;

-- Alle geloeschten Zeilen seit Version 4
SELECT *
FROM table_changes("silver_users", 4)
WHERE _change_type = "delete";''')}

<h2>3. Löschungen propagieren: das Muster für DSGVO-Löschanfragen</h2>
<p>Löschanfragen werden aus gutem Grund meist <strong>nicht</strong> in der regulären ETL-Pipeline mitverarbeitet, sondern in einem eigenen, auditierbaren Prozess. Ein typisches Muster: Eine Compliance-Tabelle <code>delete_requests</code> hält offene Löschanfragen mit Frist (<code>deadline</code>) und Status fest. Nach dem eigentlichen <code>DELETE</code> auf der Quelltabelle wird der Change Data Feed genutzt, um exakt dieselben Datensätze automatisiert in alle nachgelagerten (Gold-)Tabellen zu propagieren:</p>

{code('sql', '''-- 1. Loeschung auf der Quelltabelle ausfuehren
DELETE FROM silver_users
WHERE mrn IN (SELECT mrn FROM delete_requests);
-- Delta erzeugt eine neue Tabellenversion mit Operation "DELETE"''')}

{code('python', '''# 2. CDF-Stream ab der Delete-Version inkrementell lesen
deleteDF = (spark.readStream
                 .format("delta")
                 .option("readChangeFeed", "true")
                 .option("startingVersion", 4)     # Version des DELETE-Commits
                 .table("silver_users"))

# 3. Fuer jeden Mikro-Batch: Loeschung in die Gold-Tabelle propagieren
#    und den Anfrage-Status als "erledigt" markieren
def process_deletes(microBatchDF, batchId):
    microBatchDF.createOrReplaceTempView("deletes")

    spark.sql("""
        MERGE INTO gold_users u
        USING deletes d
        ON u.mrn = d.mrn
        WHEN MATCHED
            THEN DELETE
    """)

    spark.sql("""
        MERGE INTO delete_requests dr
        USING deletes d
        ON d.mrn = dr.mrn
        WHEN MATCHED
          THEN UPDATE SET status = "deleted"
    """)

query = (deleteDF.writeStream
                 .foreachBatch(process_deletes)
                 .outputMode("update")
                 .option("checkpointLocation", f"{checkpoint_path}/deletes")
                 .trigger(availableNow=True)
                 .start())

query.awaitTermination()''')}

<p>Der Clou an diesem Muster: Die <code>mrn</code>-Spalte (natürlicher Schlüssel bzw. Pseudonym) verbindet die Löschanfrage über den CDF-Stream mit beliebig vielen nachgelagerten Tabellen &ndash; das Prinzip lässt sich problemlos auf zusätzliche Ziel-Tabellen ausweiten, indem die <code>process_deletes</code>-Funktion um weitere <code>MERGE INTO</code>-Statements ergänzt wird. Delta Lake erlaubt zudem, jedem Commit eine frei wählbare <strong>Commit-Message</strong> mitzugeben (z. B. über die Option <code>userMetadata</code> beim Schreiben), was den gesamten Löschvorgang zusätzlich in der Tabellenhistorie auditierbar macht.</p>

<p>Ein wichtiger Vorbehalt: Nach diesem Vorgang ist die Löschung zwar in der aktuellen Tabellenversion vollzogen, ältere Versionen der Tabelle (Time Travel) und die CDF-Historie enthalten die gelöschten Zeilen aber weiterhin. Wie diese Daten auch physisch entfernt werden, behandelt Kapitel 05-5 zu <code>VACUUM</code>.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> <code>table_changes</code> gibt alle Spalten der Ausgangstabelle zurück, ergänzt um die Commit-Version und den Commit-Zeitstempel der jeweiligen Änderung. Neben dem hier gezeigten Compliance-Anwendungsfall wird die Funktion offiziell auch für inkrementelle ETL-Pipelines empfohlen, die nur seit dem letzten Lauf geänderte Zeilen weiterverarbeiten sollen, für Audit-Trails zur Nachverfolgung von Datenänderungen sowie für Datenreplikations-Workloads, die Änderungen an nachgelagerte Systeme, Caches oder externe Ziele synchronisieren.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/sql/language-manual/functions/table_changes">table_changes table-valued function &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\Databricks Kurs\Databricks-Dokumentation-DE\Section 7 - Governance and Security\04 Change Data Feed - Aenderungen nachverfolgen & propagieren.pdf",
    title="Change Data Feed: Änderungen nachverfolgen & propagieren",
    subtitle="Section 7 &middot; Governance and Security &middot; Quelle: Kurs 6, DP 1.3 &amp; DP 1.4L",
    body_html=body,
    build_name="05_04_change_data_feed",
)
print("OK")
