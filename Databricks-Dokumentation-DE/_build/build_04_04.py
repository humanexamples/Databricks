# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Kapitel 3 dieser Section hat die drei Verletzungsaktionen von Expectations &ndash; <code>WARN</code>, <code>DROP ROW</code> und <code>FAIL UPDATE</code> &ndash; anhand einfacher <code>NOT NULL</code>-Prüfungen eingeführt. In produktiven Pipelines reicht das jedoch selten aus: Ein Feld kann vorhanden und trotzdem inhaltlich falsch sein, Regeln müssen sich über mehrere Tabellen hinweg prüfen lassen, und jede gelöschte Zeile bedeutet einen unwiderruflichen Datenverlust ohne Audit-Spur. Dieses Kapitel zeigt, wie sich Expectations für den produktiven Einsatz härten lassen &ndash; und stellt mit dem <strong>Quarantäne-Muster</strong> eine Alternative zu <code>DROP ROW</code> vor, bei der keine einzige Zeile verloren geht.</p>

<h2>1. Wo einfache NOT-NULL-Prüfungen an ihre Grenzen stoßen</h2>
<p>Eine <code>NOT NULL</code>-Prüfung bestätigt lediglich, dass ein Wert <em>vorhanden</em> ist &ndash; nicht, dass er <em>korrekt</em> ist. Ein <code>discount_pct</code>-Feld mit dem Wert <code>120</code> besteht jede <code>NOT NULL</code>-Prüfung anstandslos, obwohl ein Rabatt von 120&nbsp;% offensichtlich unmöglich ist und nachgelagerte Umsatzberechnungen verfälscht. Ähnliche Lücken entstehen bei numerischen Ausreißern (negative Mengen), zeitlichen Inkonsistenzen (Datumswerte aus der Systemvergangenheit), Wertebereichsverletzungen sowie bei Feldern, die zwar optional sein dürfen, aber &ndash; wenn vorhanden &ndash; bestimmten Regeln genügen müssen. Für all diese Fälle braucht es Ausdrücke, die über eine reine Präsenzprüfung hinausgehen.</p>

<h2>2. Cross-Table-Expectations: Prüfungen über Tabellengrenzen hinweg</h2>
<p>Expectations sind nicht auf Prüfungen innerhalb einer einzelnen Zeile beschränkt. Da eine Expectation letztlich ein SQL-Boolean-Ausdruck ist, lässt sich damit auch das Ergebnis einer Materialized View prüfen, die selbst mehrere Tabellen miteinander vergleicht. Zwei Muster sind besonders verbreitet: die <strong>Row-Count-Validierung</strong>, die nach Joins oder Aggregationen sicherstellt, dass keine Zeilen unbemerkt verloren gegangen sind, und die Prüfung auf <strong>Primärschlüssel-Eindeutigkeit</strong>, die doppelte Schlüssel aufdeckt, bevor sie nachgelagerte Joins verfälschen:</p>

{code('sql', '''-- Row-Count-Validierung: stimmen die Zeilenzahlen zweier Tabellen überein?
CREATE OR REFRESH MATERIALIZED VIEW count_verification (
  CONSTRAINT no_rows_dropped EXPECT (a_count == b_count)
    ON VIOLATION FAIL UPDATE
)
AS SELECT * FROM
  (SELECT COUNT(*) AS a_count FROM table_a),
  (SELECT COUNT(*) AS b_count FROM table_b)

-- Primärschlüssel-Eindeutigkeit: darf jeder Schlüssel nur einmal vorkommen?
CREATE OR REFRESH MATERIALIZED VIEW report_pk_tests (
  CONSTRAINT unique_pk EXPECT (num_entries = 1)
    ON VIOLATION FAIL UPDATE
)
AS SELECT pk, COUNT(*) AS num_entries
FROM report
GROUP BY pk''')}

<p>Ein weiterer wichtiger Punkt bei der Formulierung von Regeln: SQL wertet <code>NULL</code> in einem Vergleich als <em>nicht wahr</em> &ndash; nicht als falsch, aber eben auch nicht als bestanden. Eine naive Bereichsprüfung wie <code>discount_rate &gt;= 0 AND discount_rate &lt;= 100</code> markiert dadurch jeden <code>NULL</code>-Wert fälschlich als Verstoß, etwa wenn nach einer Schema-Erweiterung alle historischen Zeilen für die neue Spalte <code>NULL</code> enthalten. Die Lösung ist eine NULL-tolerante Formulierung mit <code>CASE WHEN</code>, die eine Regel nur dann anwendet, wenn der Wert tatsächlich vorhanden ist:</p>

{code('sql', '''-- NULL-tolerant: prüft nur, wenn ein Wert vorhanden ist
CONSTRAINT valid_discount
EXPECT (
  CASE
    WHEN discount_rate IS NOT NULL
    THEN discount_rate >= 0 AND discount_rate <= 100
    ELSE TRUE   -- NULL wird akzeptiert
  END
)''')}

<h2>3. Robuste Bronze-Schicht: STRING-Ingest plus TRY_CAST</h2>
<p>Die widerstandsfähigste Bronze-Schicht lehnt niemals einen Datensatz wegen eines Typkonflikts ab. Werden alle eingehenden Felder zunächst als <code>STRING</code> gespeichert, akzeptiert die Pipeline, was die Quelle auch immer liefert &ndash; ob Ganzzahl, Dezimalzahl oder inkonsistent formatiert &ndash; und verschiebt die eigentliche Typdurchsetzung in die Silver-Schicht, wo <code>TRY_CAST</code> bei einem fehlgeschlagenen Cast einfach <code>NULL</code> zurückgibt, statt die gesamte Pipeline zu stoppen. Genau dieses Muster verwendet die Demo-Pipeline in der Bronze-Schicht:</p>

{code('sql', '''CREATE OR REFRESH STREAMING TABLE dq_1_bronze.sales_bronze_raw_demo
AS
SELECT
  CAST(subsidiary_id AS STRING) AS subsidiary_id,
  CAST(order_id AS STRING) AS order_id,
  CAST(qty AS STRING) AS qty,
  CAST(unit_price AS STRING) AS unit_price,
  -- Neue Spalten für Schema-Evolution (zunächst NULL)
  CAST(order_status AS STRING) AS order_status,
  CAST(shipping_cost AS STRING) AS shipping_cost,
  -- Rescued-Data-Spalte fängt unerwartete Felder auf
  CAST(_rescued_data AS STRING) AS _rescued_data,
  _metadata.file_name AS source_file,
  _metadata.file_modification_time AS file_mod_time
FROM STREAM read_files(
  '${source}',
  format => 'csv',
  schemaHints => 'order_status STRING, shipping_cost STRING'
);

-- Erst hier, in einer separaten Zwischentabelle, erfolgt die Typisierung
CREATE OR REFRESH STREAMING TABLE dq_1_bronze.sales_bronze_clean_demo
COMMENT "Intermediate table - type casting only, no quality checks"
AS
SELECT
  subsidiary_id,
  order_id,
  TRY_CAST(qty AS INT) AS qty,
  TRY_CAST(unit_price AS DOUBLE) AS unit_price,
  TRY_CAST(shipping_cost AS DOUBLE) AS shipping_cost,
  source_file
FROM STREAM dq_1_bronze.sales_bronze_raw_demo;''')}

<p>Die Option <code>schemaHints</code> kündigt Spalten an, die erst in künftigen Dateien auftauchen werden &ndash; historische Zeilen erhalten dafür einfach <code>NULL</code>. Für alles, was darüber hinausgeht und nicht im deklarierten Schema vorgesehen ist, dient die <code>_rescued_data</code>-Spalte (siehe auch Section 2) als letzte Auffanglinie: Unerwartete Felder werden dort als JSON gesammelt statt stillschweigend verworfen.</p>

<h2>4. Das Quarantäne-Muster: is_quarantined statt DROP ROW</h2>
<p><code>DROP ROW</code> entfernt ungültige Zeilen unwiderruflich &ndash; es gibt keinen Weg zurück. Das <strong>Quarantäne-Muster</strong> vermeidet diesen Datenverlust vollständig: Jede Zeile wird zunächst geschrieben, ein <code>is_quarantined</code>-Flag markiert per <strong>inverser Logik</strong>, ob irgendeine Regel verletzt wurde, und erst nachgelagerte Views trennen saubere von fehlerhaften Datensätzen. Die Kernregel dabei: Die Tabelle, auf der das Flag berechnet wird, darf ausschließlich <code>WARN</code> verwenden &ndash; würde man dort <code>DROP ROW</code> einsetzen, wären die fehlerhaften Zeilen bereits entfernt, bevor das Flag überhaupt berechnet werden könnte.</p>

{code('sql', '''CREATE OR REFRESH STREAMING TABLE dq_2_silver.sales_silver_dq_demo
(
  -- ... Geschäftsspalten ...
  is_quarantined BOOLEAN,
  quarantine_reason STRING,

  -- Expectations nur mit WARN: kein Datensatz wird entfernt,
  -- die Verstöße werden aber im Pipeline-UI sichtbar
  CONSTRAINT check_subsidiary_id  EXPECT (subsidiary_id IS NOT NULL),
  CONSTRAINT check_customer_id    EXPECT (customer_id IS NOT NULL),
  CONSTRAINT valid_discount_range EXPECT (discount_pct IS NULL OR (discount_pct >= 0 AND discount_pct <= 100))
)
COMMENT "Quarantine table with 6 expectations - supports inverse logic pattern"
PARTITIONED BY (is_quarantined);

CREATE FLOW apply_inverse_logic_flow
AS
INSERT INTO dq_2_silver.sales_silver_dq_demo BY NAME
SELECT
  subsidiary_id, order_id, customer_id, discount_pct, -- ... weitere Spalten ...

  -- Inverse Logik: TRUE, sobald IRGENDEINE Regel verletzt ist
  NOT (
    (subsidiary_id IS NOT NULL) AND
    (customer_id IS NOT NULL) AND
    (discount_pct IS NULL OR (discount_pct >= 0 AND discount_pct <= 100))
  ) AS is_quarantined,

  CONCAT_WS('; ',
    CASE WHEN subsidiary_id IS NULL THEN 'Missing subsidiary_id' END,
    CASE WHEN discount_pct IS NOT NULL AND (discount_pct < 0 OR discount_pct > 100)
         THEN 'Invalid discount_pct (must be 0-100)' END
  ) AS quarantine_reason
FROM STREAM dq_1_bronze.sales_bronze_clean_demo;

-- Zwei nachgelagerte Streaming Tables trennen die Wege
CREATE OR REFRESH STREAMING TABLE dq_2_silver.sales_silver_valid_demo
AS SELECT * EXCEPT (is_quarantined, quarantine_reason)
FROM STREAM dq_2_silver.sales_silver_dq_demo
WHERE is_quarantined = FALSE;

CREATE OR REFRESH STREAMING TABLE dq_2_silver.sales_silver_quarantined_demo
AS SELECT *
FROM STREAM dq_2_silver.sales_silver_dq_demo
WHERE is_quarantined = TRUE;''')}

<p>Die Tabelle wird bewusst mit <code>PARTITIONED BY (is_quarantined)</code> angelegt: Da die beiden nachgelagerten Tabellen jeweils exakt nach diesem Flag filtern, profitieren sie von Partition Pruning und lesen nur die für sie relevante Partition, statt die gesamte Tabelle zu scannen. Die eigentliche Gold-Schicht baut anschließend ausschließlich auf der validierten <code>sales_silver_valid_demo</code>-Tabelle auf, während die Quarantäne-Tabelle für Root-Cause-Analysen und eine spätere Nachbearbeitung erhalten bleibt.</p>

<figure class="img">
<img src="assets/04/dq_pipeline_overview.png">
<figcaption>Nach der Typisierung in der Bronze-Schicht durchläuft jede Zeile die Data-Quality-Prüfung; erst danach trennen sich saubere und quarantänierte Datensätze in zwei separate Streaming Tables.</figcaption>
</figure>

<table>
<tr><th></th><th>DROP ROW</th><th>Quarantäne-Muster</th></tr>
<tr><td>Ungültige Zeilen</td><td>Endgültig gelöscht</td><td>In Quarantäne-Tabelle erhalten</td></tr>
<tr><td>Audit-Trail</td><td>Keiner</td><td>Vollständig, abfragbar</td></tr>
<tr><td>Nachbearbeitung</td><td>Nicht möglich</td><td>Regel korrigieren &rarr; erneut einsortieren</td></tr>
<tr><td>Pipeline-Komplexität</td><td>Gering &ndash; eine Tabelle</td><td>Moderat &ndash; eine Basistabelle plus zwei Views</td></tr>
<tr><td>Empfehlung</td><td>Unkritische Streams mit etablierten Regeln</td><td>Produktive Pipelines mit Compliance-/Audit-Anforderungen</td></tr>
</table>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Die Databricks-Dokumentation zu Expectation Patterns bestätigt die hier gezeigten Muster für Cross-Table-Validierung und Row-Count-Prüfungen als offiziell empfohlene Ansätze; das Quarantänieren ungültiger Datensätze über Regeln, die spiegelbildlich zu den definierten Expectations formuliert werden, wird dort explizit als Alternative zum Verwerfen von Daten aufgeführt. Ergänzend gilt: Expectations senden ihre Metriken unabhängig von der gewählten Verletzungsaktion an den Pipeline-Event-Log, sodass sich Datenqualitätstrends auch bei WARN-basierten Regeln über die Zeit auswerten lassen.<br>
Quelle: <a href="https://learn.microsoft.com/en-us/azure/databricks/ldp/expectations">Manage data quality with pipeline expectations &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\09 Erweiterte Datenqualitaetspruefungen und Quarantaene-Muster.pdf",
    title="Erweiterte Datenqualitätsprüfungen & Quarantäne-Muster",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: Kurs 5, Kapitel 7&ndash;8",
    body_html=body,
    build_name="04_04_advanced_dq_quarantine",
)
print("OK")
