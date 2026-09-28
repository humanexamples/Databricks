# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Grobgranulare ACLs auf Tabellenebene reichen oft nicht aus: Häufig soll nur ein Teil der Zeilen sichtbar sein (z. B. nur Daten der eigenen Region) oder eine einzelne Spalte je nach Nutzergruppe unterschiedlich dargestellt werden (z. B. eine Sozialversicherungsnummer nur für Berechtigte im Klartext). Databricks bietet dafür zwei Wege: den klassischen Ansatz über <strong>Dynamic Views</strong> und den moderneren, direkt auf der Tabelle ansetzenden Ansatz mit <strong>Row Filters</strong> und <strong>Column Masks</strong>.</p>

<h2>1. Der klassische Weg: Dynamic Views</h2>
<p>Eine Dynamic View ist eine ganz normale SQL-View, die zusätzlich Funktionen wie <code>session_user()</code> oder <code>is_account_group_member()</code> nutzt, um ihr Ergebnis abhängig vom abfragenden Nutzer zu verändern. (Die ältere Funktion <code>is_member()</code> taucht in älteren Beispielen noch auf, ist aber ein Hive-Metastore-Relikt und sollte für Unity-Catalog-Tabellen nicht mehr verwendet werden &ndash; <code>session_user()</code> ist die aktuell empfohlene Alternative.) Spalten werden dabei per <code>CASE</code>-Ausdruck redigiert, Zeilen per <code>WHERE</code>-Klausel gefiltert.</p>

{code('sql', '''CREATE OR REPLACE VIEW customers_gold_dynamic_view AS
SELECT
  CASE WHEN        -- customer_id nur für Supervisors im Klartext
    is_account_group_member('supervisors') THEN customer_id
    ELSE 9999999
  END AS customer_id,
  state,
  avg(units_purchased) as average_units_purchased,
  loyalty_segment
FROM customers_silver
WHERE
  CASE WHEN         -- Nicht-Supervisors sehen nur loyalty_segment < 3
    is_account_group_member('supervisors') THEN TRUE
    ELSE loyalty_segment < 3
  END
GROUP BY customer_id, state, loyalty_segment
ORDER BY customer_id;''')}

<p>Wichtig zu verstehen: Der Eigentümer der View benötigt selbst keine Rechte auf <code>customers_silver</code>, um die View bereitzustellen &ndash; entscheidend ist, dass der View-Eigentümer Zugriff auf die Basistabelle hat. Andere Nutzer greifen ausschließlich über die View zu und sehen nur das, was die View-Definition zulässt. Der Nachteil dieses Ansatzes: Für jede unterschiedliche Sicht auf dieselben Daten muss eine eigene View angelegt und gepflegt werden, was bei vielen Tabellen schnell unübersichtlich wird.</p>

<h2>2. Der moderne Weg: Row Filters und Column Masks</h2>
<p>Seit 2024 lassen sich Zeilenfilter und Spaltenmaskierungen direkt an die Tabelle selbst anhängen &ndash; ganz ohne zusätzliches View-Objekt. Row Filters und Column Masks werden als SQL-<strong>User-Defined-Functions (UDFs)</strong> definiert (Python- und Scala-UDFs sind ebenfalls möglich, müssen dafür aber in eine SQL-UDF eingebettet werden) und per <code>ALTER TABLE</code> aktiviert.</p>

<figure class="img">
<img src="assets/05/row-filter-column-mask.png">
<figcaption>Row Filters (links) und Column Masks (rechts): jeweils eine UDF definieren und mit SET ROW FILTER bzw. SET MASK an die Tabelle anhängen.</figcaption>
</figure>

<h3>2.1 Row Filter</h3>
<p>Ein Row Filter ist eine UDF, die für jede Zeile <code>TRUE</code> oder <code>FALSE</code> zurückgibt; nur Zeilen mit <code>TRUE</code> werden angezeigt. Jede Tabelle kann höchstens einen Row Filter besitzen, der aber beliebig viele Spalten als Parameter binden darf.</p>

{code('sql', '''-- 1. UDF definieren
CREATE OR REPLACE FUNCTION loyalty_row_filter(loyalty_segment STRING)
RETURNS BOOLEAN
RETURN IF(is_account_group_member('supervisors'), true, loyalty_segment < 3);

-- 2. UDF an die Tabelle binden
ALTER TABLE customers_silver_with_row_filter_and_column_masks
SET ROW FILTER loyalty_row_filter ON (loyalty_segment);

-- 3. Aktivierte Filter prüfen
SELECT *
FROM information_schema.row_filters
WHERE table_name = 'customers_silver_with_row_filter_and_column_masks';''')}

<h3>2.2 Column Mask</h3>
<p>Eine Column Mask ist eine UDF, die bei jeder Abfrage anstelle des Originalwerts ausgewertet wird. Damit lassen sich Werte vollständig redigieren (wie im Beispiel) oder auch nur teilweise unkenntlich machen &ndash; etwa nur die letzten vier Ziffern einer Kontonummer anzeigen.</p>

{code('sql', '''-- 1. UDF definieren
CREATE OR REPLACE FUNCTION redact_customer_id(customer_id BIGINT)
RETURN CASE WHEN is_account_group_member('supervisors')
  THEN customer_id
  ELSE 9999999
END;

-- 2. UDF an eine Spalte binden
ALTER TABLE customers_silver_with_row_filter_and_column_masks
  ALTER COLUMN customer_id
  SET MASK redact_customer_id;

-- 3. Ergebnis: Zeilenfilter und Spaltenmaskierung greifen gemeinsam
SELECT *
FROM customers_silver_with_row_filter_and_column_masks
ORDER BY loyalty_segment DESC
LIMIT 10;
-- customer_id zeigt 9999999, nur loyalty_segment < 3 ist sichtbar''')}

<h2>3. Dynamic Views vs. Row Filters/Column Masks &ndash; Vergleich</h2>
<table>
<tr><th>Kriterium</th><th>Dynamic Views</th><th>Row Filters / Column Masks</th></tr>
<tr><td>Zusätzliches Objekt nötig?</td><td>Ja &ndash; eine View pro Anwendungsfall</td><td>Nein &ndash; wird direkt an die Tabelle angehängt</td></tr>
<tr><td>Pflegeaufwand bei vielen Varianten</td><td>Hoch (viele Views)</td><td>Gering (eine UDF, mehrfach wiederverwendbar)</td></tr>
<tr><td>Gilt automatisch für alle Abfragen der Tabelle</td><td>Nein, nur für Abfragen über die View</td><td>Ja, unabhängig vom Zugriffsweg</td></tr>
<tr><td>Granularität</td><td>Zeilen und Spalten kombinierbar</td><td>Ein Row Filter + beliebig viele Column Masks je Tabelle</td></tr>
</table>

<h2>4. Ausblick: Attribute-Based Access Control (ABAC)</h2>
<p>Sowohl Dynamic Views als auch klassische Row Filters/Column Masks müssen pro Tabelle einzeln eingerichtet werden. Bei hunderten Tabellen mit denselben Schutzanforderungen (z. B. "alle als <code>pii</code> getaggten Spalten maskieren") wird das schnell unpraktikabel. Genau hier setzt <strong>ABAC</strong> an: Statt Regeln an einzelne Objekte zu binden, werden sie an <strong>Tags</strong> gebunden und automatisch auf alle passenden Objekte im gesamten Catalog oder Schema angewendet &ndash; siehe Recherche-Box unten.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Attribute-Based Access Control (ABAC) für Row Filtering und Column Masking ist inzwischen als eigenständiges, tag-basiertes Policy-Modell in Unity Catalog allgemein verfügbar (General Availability), gemeinsam mit Governed Tags und automatisierter Data Classification. Statt UDFs individuell an jede Tabelle zu binden, definiert man eine ABAC-Policy auf Catalog- oder Schema-Ebene, die tag-basierte Bedingungen auswertet (z. B. "Spalten mit Tag <code>pii_category=email</code> maskieren") und automatisch auf alle passenden, auch künftig neu hinzukommenden Objekte angewendet wird. Damit wird ABAC zur empfohlenen Vorgehensweise, sobald konsistente Filter-/Maskierungsregeln über viele Tabellen hinweg gelten sollen &ndash; die klassischen, objektgebundenen Row Filters und Column Masks aus diesem Kapitel bleiben für punktuelle Sonderfälle weiterhin unterstützt.<br>
Quelle: <a href="https://www.databricks.com/blog/abac-row-filtering-and-column-masking-policies-governed-tags-and-data-classification-are-now">ABAC row filtering and column masking policies, governed tags, and data classification are now generally available &ndash; Databricks Blog</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\Databricks Kurs\Databricks-Dokumentation-DE\Section 7 - Governance and Security\02 Row Filters, Column Masks & Dynamic Views.pdf",
    title="Row Filters, Column Masks & Dynamic Views",
    subtitle="Section 7 &middot; Governance and Security &middot; Quelle: Kurs 6, DP 1.1",
    body_html=body,
    build_name="05_02_row_filters_column_masks",
)
print("OK")
