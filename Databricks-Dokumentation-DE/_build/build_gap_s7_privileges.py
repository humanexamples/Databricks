# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Ein früheres Kapitel dieser Section hat das Unity-Catalog-Sicherheitsmodell im Überblick vorgestellt. Dieses Kapitel vertieft das praktische Handwerkszeug für die Zugriffssteuerung: die Befehle <code>GRANT</code>, <code>REVOKE</code> und <code>DENY</code>, die Prinzipale, an die Rechte vergeben werden, und wie sich Rechte über die Objekthierarchie hinweg vererben.</p>

<h2>1. Securable Objects und die Objekthierarchie</h2>
<p>Jedes Objekt, auf das sich in Unity Catalog Rechte vergeben lassen, wird als <strong>Securable Object</strong> bezeichnet: der Metastore selbst, Catalogs, Schemas, Tables, Views, Volumes, Functions und weitere. Catalogs und Schemas gelten dabei zusätzlich als <strong>Container-Objekte</strong>: Rechte, die auf einem Container gewährt werden, wirken sich &ndash; über Vererbung &ndash; automatisch auch auf dessen Kinder-Objekte aus. Ein <code>USE CATALOG</code>-Recht auf Catalog-Ebene ist beispielsweise Voraussetzung dafür, überhaupt auf Schemas und Tabellen darunter zugreifen zu können.</p>

<h2>2. GRANT: Rechte vergeben</h2>
<p>Rechte werden nicht an einzelne Personen, sondern an <strong>Prinzipale</strong> vergeben: einzelne Nutzerkonten, Gruppen oder Service Principals (für automatisierte Zugriffe, z. B. aus einer CI/CD-Pipeline).</p>
{code('sql', '''-- Leserecht auf eine einzelne Tabelle für eine Gruppe
GRANT SELECT ON TABLE main.sales.orders TO `data-analysts`;

-- Nutzungsrecht auf Schema-Ebene (Voraussetzung, um Objekte darunter überhaupt zu sehen)
GRANT USE SCHEMA ON SCHEMA main.sales TO `data-analysts`;

-- Alle Rechte auf ein Schema an einen Service Principal (z. B. für eine CI/CD-Pipeline)
GRANT ALL PRIVILEGES ON SCHEMA main.sales TO `svc-cicd-pipeline`;''')}
<p><code>ALL PRIVILEGES</code> ist dabei ein Sonderfall: Es fasst sämtliche für das jeweilige Objekt verfügbaren Einzelrechte zusammen, statt sie einzeln aufzählen zu müssen. Jedes Objekt hat außerdem einen <strong>Owner</strong>, der automatisch über alle Rechte auf diesem Objekt verfügt &ndash; einschließlich des Rechts, selbst weitere Rechte an andere Prinzipale zu vergeben.</p>

<h2>3. REVOKE: Rechte entziehen</h2>
<p><code>REVOKE</code> nimmt ein zuvor gewährtes Recht wieder zurück. Wichtig für die Prüfung: Der Befehl schlägt nicht fehl, selbst wenn das angegebene Recht nie explizit gewährt wurde &ndash; er ist also gefahrlos wiederholbar.</p>
{code('sql', '''REVOKE SELECT ON TABLE main.sales.orders FROM `data-analysts`;''')}

<h2>4. DENY: explizite Zugriffssperre</h2>
<p>Während <code>REVOKE</code> lediglich eine zuvor erteilte Erlaubnis entfernt, setzt <code>DENY</code> eine <strong>explizite Sperre</strong>, die selbst dann greift, wenn derselbe Prinzipal das Recht über einen anderen Weg (z. B. Gruppenmitgliedschaft oder Vererbung von einem übergeordneten Container) eigentlich hätte. Ein <code>DENY</code> hat also grundsätzlich Vorrang vor jedem <code>GRANT</code> &ndash; dieses Zusammenspiel wird in der Prüfung gerne anhand von Szenarien mit widersprüchlichen Rechten abgefragt.</p>
{code('sql', '''-- Auch wenn die Gruppe "data-analysts" über GRANT Zugriff auf das Schema hat,
-- wird dieser einzelnen Nutzerin der Zugriff auf genau diese Tabelle explizit verwehrt.
DENY SELECT ON TABLE main.sales.customer_pii TO `anna.example@firma.de`;''')}

<h2>5. Auflösungsreihenfolge bei widersprüchlichen Rechten</h2>
<table>
<tr><th>Situation</th><th>Ergebnis</th></tr>
<tr><td>Kein GRANT vorhanden</td><td>Zugriff verweigert (Standard: alles ist zunächst gesperrt)</td></tr>
<tr><td>GRANT vorhanden, kein DENY</td><td>Zugriff erlaubt</td></tr>
<tr><td>GRANT und gleichzeitig DENY vorhanden (z. B. über verschiedene Gruppen)</td><td>Zugriff verweigert &ndash; DENY gewinnt immer</td></tr>
<tr><td>REVOKE nach einem GRANT</td><td>Zugriff verweigert (wie im Ausgangszustand ohne GRANT)</td></tr>
</table>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks weist ausdrücklich darauf hin, dass jedes Securable Object einen Owner besitzt, der implizit über sämtliche Rechte auf diesem Objekt verfügt &ndash; inklusive der Möglichkeit, Rechte an weitere Prinzipale zu delegieren. Container-Objekte (Metastore, Catalog, Schema) spielen im Berechtigungsmodell eine besondere Rolle, da auf ihnen gewährte Rechte automatisch an alle enthaltenen Kinder-Objekte vererbt werden &ndash; ein zentraler Baustein, um große Objektmengen effizient zu verwalten, ohne jedes einzelne Objekt separat berechtigen zu müssen.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/">Manage privileges in Unity Catalog &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 7 - Governance and Security\07 Zugriffskontrolle vertieft - GRANT, REVOKE, DENY und Rechte-Hierarchie.pdf",
    title="Zugriffskontrolle vertieft: GRANT, REVOKE, DENY und die Rechte-Hierarchie",
    subtitle="Section 7 &middot; Governance and Security &middot; Quelle: Databricks-Dokumentation (Unity Catalog Privileges)",
    body_html=body,
    build_name="gap_s7_privileges",
)
print("OK")
