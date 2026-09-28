# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Neben den Methoden zur Erstbefüllung einer Tabelle (CTAS, COPY INTO, Streaming Tables) gibt es einen sehr häufigen Anwendungsfall: neue oder geänderte Datensätze in eine <strong>bereits bestehende</strong> Delta-Tabelle einzupflegen, ohne Duplikate zu erzeugen oder die gesamte Tabelle neu zu schreiben. Dafür bietet Databricks den <code>MERGE INTO</code>-Befehl.</p>

<h2>1. MERGE INTO: Updates, Inserts und Deletes in einem Schritt</h2>
<p><code>MERGE INTO</code> vergleicht eine Quelltabelle (bzw. das Ergebnis einer Abfrage) mit einer Zieltabelle anhand einer Join-Bedingung und führt je nach Ergebnis unterschiedliche Aktionen aus: Bestehende Zeilen werden aktualisiert (<code>UPDATE</code>), gelöscht (<code>DELETE</code>) oder neue Zeilen eingefügt (<code>INSERT</code>) &ndash; alles als eine einzige, atomare Transaktion. Das macht <code>MERGE INTO</code> zum Standardwerkzeug für inkrementelle Upsert-Logik, etwa beim Zusammenführen von CDC-Änderungen oder beim regelmäßigen Abgleich einer Bronze- mit einer Silver-Tabelle.</p>

{code('sql', '''MERGE INTO main_users_target target
USING update_users_source source
ON target.id = source.id
WHEN MATCHED AND source.status = 'update' THEN
  UPDATE SET
    target.email = source.email,
    target.status = source.status
WHEN MATCHED AND source.status = 'delete' THEN
  DELETE
WHEN NOT MATCHED THEN
  INSERT (id, first_name, email, sign_up_date, status)
  VALUES (source.id, source.first_name, source.email, source.sign_up_date, source.status);''')}

<p>Die Bedingung hinter <code>WHEN MATCHED</code> bzw. <code>WHEN NOT MATCHED</code> kann zusätzliche Filter enthalten (hier: <code>source.status</code>), sodass sich Update-, Delete- und Insert-Fälle in einer einzigen Anweisung fein steuern lassen. Wie jede Delta-Operation wird auch <code>MERGE INTO</code> als neue Version in der Tabellenhistorie protokolliert und kann über <code>DESCRIBE HISTORY</code> sowie <code>SELECT * FROM tabelle VERSION AS OF n</code> (Time Travel) nachvollzogen werden.</p>

<h2>2. Schema-Evolution innerhalb von MERGE INTO</h2>
<p>Enthält die Quelltabelle neue Spalten, die in der Zieltabelle noch nicht existieren, schlägt ein normales <code>MERGE INTO</code> mit einem Schema-Fehler fehl. Für genau diesen Fall bietet Databricks die Erweiterung <code>MERGE WITH SCHEMA EVOLUTION INTO</code>: Sie erlaubt es, neue Spalten aus der Quelle automatisch in die Zieltabelle zu übernehmen, ohne vorher eine Session-Konfiguration setzen zu müssen.</p>

{code('sql', '''-- Ohne Schema-Evolution: schlägt fehl, wenn "new_users_source"
-- eine zusätzliche Spalte "country" enthält, die im Ziel fehlt
MERGE INTO main_users_target target
USING new_users_source source
ON target.id = source.id
WHEN MATCHED AND source.status = 'update' THEN
  UPDATE SET
    target.email = source.email,
    target.status = source.status
WHEN NOT MATCHED AND source.status = 'new' THEN
  INSERT (id, first_name, email, sign_up_date, status, country)
  VALUES (source.id, source.first_name, source.email, source.sign_up_date, source.status, source.country);

-- Mit Schema-Evolution: die neue Spalte "country" wird automatisch
-- zur Zieltabelle hinzugefügt
MERGE WITH SCHEMA EVOLUTION INTO main_users_target target
USING new_users_source source
ON target.id = source.id
WHEN MATCHED AND source.status = 'update' THEN
  UPDATE SET
    target.email = source.email,
    target.status = source.status
WHEN NOT MATCHED AND source.status = 'new' THEN
  INSERT (id, first_name, email, sign_up_date, status, country)
  VALUES (source.id, source.first_name, source.email, source.sign_up_date, source.status, source.country);''')}

<h2>3. Weitere Ingestion-nahe Plattform-Features</h2>
<p>Über die in diesem Themenordner behandelten Ingestion-Methoden hinaus bietet Databricks weitere Funktionen, die bei wachsender Architektur relevant werden können:</p>
<ul>
<li><strong>Lakehouse Federation</strong> &ndash; ermöglicht Abfragen auf externe Datenquellen (z. B. andere Datenbanken) direkt aus Databricks heraus, ohne die Daten vorher physisch zu kopieren.</li>
<li><strong>Delta Sharing &amp; Databricks Marketplace</strong> &ndash; ein offener Standard bzw. ein Marktplatz, um Datensätze sicher mit anderen Organisationen zu teilen oder von dort zu beziehen, ebenfalls ohne unnötige Datenkopien.</li>
<li><strong>Zerobus</strong> &ndash; eine Möglichkeit, Daten sehr niedrig-latent direkt in Databricks-Tabellen zu streamen (z. B. aus IoT- oder Event-Quellen).</li>
</ul>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Für <code>MERGE WITH SCHEMA EVOLUTION INTO</code> empfiehlt Databricks inzwischen ausdrücklich, die Schema-Evolution direkt in der jeweiligen Schreiboperation anzugeben (wie oben gezeigt), statt sie global über eine Session-Konfiguration zu aktivieren &ndash; das macht das Verhalten pro Anweisung nachvollziehbar und vermeidet unbeabsichtigte Schema-Änderungen an anderer Stelle. Die Funktion steht ab Databricks Runtime 15.2 zur Verfügung; Nutzerinnen und Nutzer, die ausschließlich LTS-Versionen einsetzen, benötigen Runtime 15.4 LTS als erste LTS-Version mit dieser Funktion.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/tables/update-schema">Update table schemas with schema evolution &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\Databricks Kurs\Databricks-Dokumentation-DE\Section 2 - Data Ingestion and Loading\05 Daten in bestehende Delta-Tabellen einfuegen (MERGE INTO).pdf",
    title="Daten in bestehende Delta-Tabellen einfügen",
    subtitle="Section 2 &middot; Data Ingestion and Loading &middot; Quelle: Kurs 1, Kapitel 16&ndash;17",
    body_html=body,
    build_name="01_05_merge_into",
)
print("OK")
