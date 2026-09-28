# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Unity Catalog ist die zentrale Governance-Schicht der Databricks-Plattform: Statt Berechtigungen getrennt auf Dateisystem-, Metastore- und Data-Warehouse-Ebene zu pflegen, verwaltet Unity Catalog Zugriffsrechte, Herkunftsnachweise (Lineage) und Metadaten für alle Daten- und KI-Objekte an einer einzigen Stelle. Das erleichtert nicht nur den Alltag, sondern ist auch die Grundlage dafür, Compliance-Anforderungen wie DSGVO oder CCPA überhaupt nachweisbar umzusetzen &ndash; wer wann worauf zugegriffen hat, lässt sich lückenlos dokumentieren.</p>

<h2>1. Die Objekthierarchie: Metastore &rarr; Catalog &rarr; Schema &rarr; Table/Volume</h2>
<p>Unity Catalog organisiert alle Datenobjekte in einem konsistenten Drei-Ebenen-Namespace. Ganz oben steht der <strong>Metastore</strong> &ndash; pro Cloud-Region wird typischerweise genau einer angelegt und mehreren Workspaces zugewiesen. Darunter folgen <strong>Catalogs</strong>, die als primäre Einheit der Datenisolation dienen und oft Organisationseinheiten oder Umgebungen (z. B. <code>dev</code>/<code>prod</code>) abbilden. Jeder Catalog enthält <strong>Schemas</strong> (vergleichbar mit Datenbanken), und darin liegen schließlich die eigentlichen Objekte: <strong>Tables</strong>, <strong>Views</strong>, <strong>Volumes</strong> (für unstrukturierte Dateien), <strong>Models</strong> und <strong>Functions</strong>. Eine Tabelle wird dadurch immer über den vollen Pfad <code>catalog.schema.tabelle</code> referenziert.</p>

<figure class="img">
<img src="assets/05/uc-hierarchy.png">
<figcaption>Die Objekthierarchie in Unity Catalog: Metastore, Catalog, Schema und die darunterliegenden Objekttypen.</figcaption>
</figure>

<p>Storage-Speicherorte lassen sich auf Metastore-, Catalog- oder sogar Schema-Ebene festlegen, sodass Unternehmen bestimmte Datenkategorien gezielt in eigenen Cloud-Speicherorten isolieren können &ndash; etwa um regulatorische Vorgaben zur Datenresidenz zu erfüllen. Volumes verdienen besondere Erwähnung: Sie verwalten rohe, nicht-tabellarische Dateien (Konfigurationen, Checkpoints, Bilder) und ersetzen damit den älteren, unkontrollierten Zugriff über DBFS.</p>

<h2>2. Das ACL-Modell: wer darf was womit</h2>
<p>Der Zugriff auf jedes Objekt wird über <strong>Access Control Lists (ACLs)</strong> gesteuert, die sich in drei Fragen zusammenfassen lassen: <strong>Wer</strong> (das Principal &ndash; ein User, ein Service Principal oder, empfohlen, eine Gruppe), <strong>was</strong> (das Securable Object, z. B. eine Tabelle oder ein Schema) und <strong>wie</strong> (das Privilege, z. B. <code>SELECT</code>, <code>MODIFY</code>, <code>USE CATALOG</code>). Rechte werden über <code>GRANT</code> vergeben und über <code>REVOKE</code> wieder entzogen.</p>

<p>Unity Catalog unterstützt dabei zwei grundsätzliche Strategien. Bei der <strong>vererbten Vergabe</strong> setzt man Rechte auf einer hohen Ebene (z. B. dem Catalog), und alle darunterliegenden Schemas und Tabellen &ndash; auch künftig neu erstellte &ndash; erben diese Rechte automatisch. Das ist bequem, birgt aber das Risiko, versehentlich zu viel freizugeben. Die Alternative ist die <strong>explizite Vergabe</strong> auf einzelne Objekte: aufwendiger in der Pflege, dafür präzise und sicher.</p>

{code('sql', '''-- Vererbte Rechte: alle Konten-Nutzer dürfen im gesamten Catalog lesen
GRANT USE CATALOG, USE SCHEMA, SELECT ON CATALOG kunden_catalog TO `account users`;

-- Explizite Rechte: nur Zugriff auf ein einzelnes Schema und eine einzelne View
GRANT USE SCHEMA ON SCHEMA kunden_catalog.pii_data TO `account users`;
GRANT SELECT ON VIEW kunden_catalog.pii_data.customers_gold_view TO `account users`;

-- Rechte wieder entziehen
REVOKE USAGE ON SCHEMA pii_data FROM `account users`;
REVOKE SELECT ON VIEW pii_data.customers_gold_view FROM `account users`;

-- Vergebene Rechte prüfen
SHOW GRANTS ON SCHEMA pii_data;
SHOW GRANTS ON VIEW pii_data.customers_gold_view;''')}

<p>Ein wichtiges Detail für den Aufbau sicherer Datenprodukte: Wenn eine <strong>View</strong> auf einer zugrunde liegenden Tabelle basiert, benötigen Nutzer der View keinen direkten Zugriff auf die Basistabelle &ndash; entscheidend ist, dass der <strong>Eigentümer der View</strong> über die nötigen Rechte auf die Basistabelle verfügt. Damit lässt sich eine Gold-View gezielt freigeben, während die zugrunde liegende Silver-Tabelle mit den vollständigen Rohdaten geschützt bleibt.</p>

<h2>3. Tagging: Metadaten für Klassifizierung und Compliance</h2>
<p>Tags sind Schlüssel-Wert-Paare, die sich auf nahezu jedes Unity-Catalog-Objekt anwenden lassen &ndash; auf Catalogs, Schemas, Tabellen und sogar auf einzelne Spalten. Sie werden vor allem für Datenklassifizierung (z. B. Markierung von DSGVO-relevanten Spalten), Suche und Lifecycle-Management eingesetzt. Pro Objekt sind bis zu 20 Tags möglich.</p>

{code('sql', '''-- Tabellen-Tags setzen
ALTER TABLE customers_silver
SET TAGS (
  'quality' = 'silver',
  'domain'  = 'customer'
);

-- Spalten-Tag zur Compliance-Kennzeichnung
ALTER TABLE customers_silver
  ALTER COLUMN customer_id SET TAGS ("compliance" = "GDPR");''')}

<h2>4. Discoverability: Daten wiederfinden</h2>
<p>Da alle Metadaten zentral vorliegen, kann die Databricks-Suche direkt nach Tags filtern &ndash; etwa über die Syntax <code>domain:customer</code> in der Suchleiste. Ergebnisse werden dabei automatisch anhand der Berechtigungen des suchenden Nutzers gefiltert: Wer keinen Zugriff auf ein Objekt hat, sieht es auch in der Suche nicht. Alternativ lassen sich Tags direkt per SQL über die <code>INFORMATION_SCHEMA</code> abfragen:</p>

{code('sql', '''SELECT *
FROM INFORMATION_SCHEMA.TABLE_TAGS
WHERE TABLE_NAME = 'customers_silver';

-- Analog verfügbar für weitere Objekttypen:
-- INFORMATION_SCHEMA.CATALOG_TAGS, SCHEMA_TAGS, COLUMN_TAGS, VOLUME_TAGS''')}

<h2>5. Data Lineage</h2>
<p>Unity Catalog erfasst automatisch die Herkunft und den Fluss von Daten &ndash; ganz ohne zusätzliche Konfiguration. Im Lineage-Tab von Catalog Explorer lässt sich für jedes Objekt sowohl <strong>Upstream</strong> (woher stammen die Daten, welche Quellen wurden verwendet) als auch <strong>Downstream</strong> (welche Tabellen, Dashboards oder Jobs verwenden dieses Objekt) einsehen. Lineage wird nicht nur für Tabellen und Spalten getrackt, sondern auch für Notebooks, Lakeflow Jobs, Dashboards und Dateien. Das ist essenziell für Impact-Analysen: Bevor eine Spalte gelöscht oder umbenannt wird, lässt sich sofort erkennen, welche nachgelagerten Reports oder Pipelines davon betroffen wären.</p>

<h2>6. System-Tables: Audit, Zugriff und Kosten in SQL abfragbar</h2>
<p>Unity Catalog stellt umfangreiche <strong>System-Tables</strong> im Catalog <code>system</code> bereit, mit denen sich der Zustand des gesamten Lakehouse per SQL analysieren lässt &ndash; ideal, um Audit-Anfragen oder Compliance-Nachweise zu beantworten.</p>

<table>
<tr><th>System-Table</th><th>Typische Fragestellung</th></tr>
<tr><td><code>system.information_schema.tables</code></td><td>Welche Tabellen existieren in einem Catalog? Wer hat sie zuletzt geändert?</td></tr>
<tr><td><code>system.information_schema.table_privileges</code></td><td>Wer hat welche Rechte auf eine bestimmte Tabelle?</td></tr>
<tr><td><code>system.billing.usage</code></td><td>Wie viele DBUs wurden von welchem Nutzer/Job verbraucht?</td></tr>
<tr><td><code>system.access.audit</code></td><td>Wer hat wann auf welches Objekt zugegriffen oder es gelöscht?</td></tr>
<tr><td><code>system.access.table_lineage</code></td><td>Welche Tabellen wurden aus welcher Quelltabelle erzeugt?</td></tr>
</table>

{code('sql', '''-- Wer hat zuletzt Zugriff auf eine sensible Tabelle bekommen?
SELECT grantee, table_name, privilege_type
FROM system.information_schema.table_privileges
WHERE table_name = 'customers_silver';

-- Wer hat eine Tabelle gelöscht? (Audit Log)
SELECT user_identity.email, event_time
FROM system.access.audit
WHERE request_params.full_name_arg = 'kunden_catalog.pii_data.customers_silver'
  AND service_name = 'unityCatalog'
  AND action_name  = 'deleteTable';''')}

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Die <code>system.access.audit</code>-Tabelle bildet den Audit Log als abfragbare Tabelle ab und beantwortet detailliert, wer wann auf welches Objekt zugegriffen hat (Logins, Datenzugriffe, Start/Stopp von Compute-Ressourcen). Damit Audit-Logs überhaupt in den System-Tables erscheinen, müssen sie zunächst auf Account-Ebene aktiviert und konfiguriert werden. Die Einträge werden im JSON-Format erfasst und standardmäßig <strong>90 Tage</strong> aufbewahrt &ndash; für eine dauerhafte Aufbewahrung (z. B. für mehrjährige Compliance-Nachweise) sollten Audit-Daten regelmäßig in eine eigene, langfristig aufbewahrte Tabelle exportiert werden.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/data-governance/unity-catalog/audit">Audit Unity Catalog events &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 7 - Governance and Security\01 Unity-Catalog-Sicherheitsmodell (ACLs, Lineage, Discoverability).pdf",
    title="Unity-Catalog-Sicherheitsmodell (ACLs, Lineage, Discoverability)",
    subtitle="Section 7 &middot; Governance and Security &middot; Quelle: Kurs 6, DP 1.1",
    body_html=body,
    build_name="05_01_unity_catalog_sicherheitsmodell",
)
print("OK")
