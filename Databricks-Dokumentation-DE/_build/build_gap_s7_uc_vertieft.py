# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Kapitel 1 dieser Section hat das Unity-Catalog-Sicherheitsmodell (ACLs, Tagging, Lineage, System-Tables) vorgestellt, Kapitel 7 die Befehle <code>GRANT</code>/<code>REVOKE</code>/<code>DENY</code> vertieft. Dieses Kapitel ergänzt drei bislang fehlende Bausteine: die <strong>Architektur</strong>-Perspektive (warum Unity Catalog eingeführt wurde), das <strong>Identitätsmodell</strong> (Users, Service Principals, Groups, Identity Federation), sowie das <strong>vollständige Rechtemodell</strong> im Vergleich zum älteren, Hive-Metastore-basierten Berechtigungssystem.</p>

<h2>1. Architektur: Governance vor und nach Unity Catalog</h2>
<p>Vor Unity Catalog verwaltete jeder Databricks-Workspace seine Nutzerverwaltung, seinen Hive Metastore und seine Zugriffskontrollen vollständig <strong>unabhängig</strong> &ndash; Rechte mussten in jedem Workspace einzeln gepflegt werden, auch wenn dieselben Personen und dieselben Daten betroffen waren. Unity Catalog verlagert Nutzerverwaltung, Metastores und Zugriffskontrollen auf die <strong>Account-Ebene</strong> (verwaltet über die Account Console) und macht sie dadurch workspace-übergreifend wiederverwendbar: Ein einziger Unity-Catalog-Metastore lässt sich mehreren Workspaces gleichzeitig zuweisen, sodass diese sich Zugriffskontrollen und Datenzugriff teilen, statt sie zu duplizieren.</p>

<figure class="img">
<img src="assets/s7/uc_architecture_before_after.png">
<figcaption>Vor Unity Catalog verwaltete jeder Workspace Nutzer, Metastore und Zugriffskontrollen unabhängig; Unity Catalog zentralisiert alle drei auf Account-Ebene und teilt sie über Workspaces hinweg.</figcaption>
</figure>

<h2>2. Identitäten: Users, Service Principals, Groups</h2>
<p>Unity Catalog unterscheidet drei Arten von Prinzipalen (siehe auch die <code>GRANT</code>-Beispiele in Kapitel 7):</p>
<ul>
<li><strong>User</strong> &ndash; eine natürliche Person, eindeutig identifiziert über ihre E-Mail-Adresse. Ein User kann zusätzlich die Rolle <strong>Account Administrator</strong> erhalten, um Metastores zu verwalten und Workspaces zuzuweisen.</li>
<li><strong>Service Principal</strong> &ndash; eine Identität für automatisierte Tools und Anwendungen (z. B. eine CI/CD-Pipeline), eindeutig identifiziert über eine Application ID statt einer E-Mail-Adresse. Auch Service Principals können administrative Rechte erhalten, um programmatisch Verwaltungsaufgaben auszuführen.</li>
<li><strong>Group</strong> &ndash; fasst Users und Service Principals zu einer Einheit zusammen und kann selbst weitere Gruppen enthalten (verschachtelte Gruppen, z. B. eine übergeordnete Gruppe &bdquo;employees&ldquo; mit den Untergruppen &bdquo;HR&ldquo; und &bdquo;Finance&ldquo;).</li>
</ul>
<p>Identitäten existieren dabei auf zwei Ebenen: auf <strong>Account-Ebene</strong> (zentral in der Account Console verwaltet) und auf <strong>Workspace-Ebene</strong>. <strong>Identity Federation</strong> erlaubt es, eine Identität einmalig auf Account-Ebene anzulegen und sie anschließend beliebigen Workspaces zuzuweisen &ndash; ohne dass in jedem Workspace eine eigene Kopie derselben Identität manuell gepflegt werden müsste.</p>

<figure class="img">
<img src="assets/s7/uc_identity_federation.png">
<figcaption>Identity Federation: Eine einmal auf Account-Ebene angelegte Identität lässt sich mehreren Workspaces zuweisen, ohne sie dort erneut anzulegen.</figcaption>
</figure>

<h2>3. Weitere Securable Objects: Storage Credential, External Location, Share, Recipient</h2>
<p>Neben der bereits bekannten Objekthierarchie (Metastore &rarr; Catalog &rarr; Schema &rarr; Table/View/Function) verwaltet Unity Catalog zwei weitere Objektkategorien: <strong>Storage Credentials</strong> kapseln die Authentifizierung gegenüber dem zugrunde liegenden Cloud-Speicher und gelten für einen gesamten Speicher-Container; <strong>External Locations</strong> referenzieren darauf aufbauend ein konkretes Verzeichnis innerhalb dieses Containers. Für Delta Sharing kommen zusätzlich <strong>Shares</strong> (eine Sammlung von Tabellen, die mit einem oder mehreren <strong>Recipients</strong> geteilt wird) hinzu.</p>

<h2>4. Das vollständige Privilegien-Modell</h2>
<p>Kapitel 7 hat <code>GRANT</code>/<code>REVOKE</code>/<code>DENY</code> anhand einzelner Beispiele (<code>SELECT</code>, <code>USE SCHEMA</code>, <code>ALL PRIVILEGES</code>) gezeigt. Die vollständige Liste der in Unity Catalog verfügbaren Privilegien:</p>
<table>
<tr><th>Privileg</th><th>Bedeutung</th></tr>
<tr><td><code>CREATE</code></td><td>Ein neues Objekt anlegen (z. B. eine Tabelle in einem Schema)</td></tr>
<tr><td><code>SELECT</code></td><td>Lesezugriff auf ein Objekt</td></tr>
<tr><td><code>MODIFY</code></td><td>Daten in einem Objekt hinzufügen, ändern oder löschen</td></tr>
<tr><td><code>READ FILES</code></td><td>Zugriff auf die zugrunde liegenden Dateien eines Storage-Objekts (Volume, External Location)</td></tr>
<tr><td><code>WRITE FILES</code></td><td>Schreibzugriff auf die zugrunde liegenden Dateien eines Storage-Objekts</td></tr>
<tr><td><code>EXECUTE</code></td><td>Eine benutzerdefinierte Funktion (Function) ausführen</td></tr>
<tr><td><code>USE CATALOG</code> / <code>USE SCHEMA</code></td><td>Voraussetzung, um überhaupt auf Objekte innerhalb des Catalogs bzw. Schemas zugreifen zu können (siehe Kapitel 7)</td></tr>
</table>

<figure class="img">
<img src="assets/s7/uc_security_model_overview.png">
<figcaption>Das Sicherheitsmodell von Unity Catalog verbindet drei Bausteine: Prinzipale (wer), Securable Objects (was) und Privilegien (wie) &ndash; vergeben über GRANT Privilege ON Securable_Object TO Principal.</figcaption>
</figure>

<h2>5. Legacy: weiterhin Zugriff auf den Hive Metastore</h2>
<p>Unity Catalog ist <strong>additiv</strong>: Der bisherige, workspace-lokale Hive Metastore bleibt nach Aktivierung von Unity Catalog vollständig zugänglich &ndash; unabhängig davon, welcher Unity-Catalog-Metastore dem Workspace zugewiesen ist, stellt der feste Catalog-Name <code>hive_metastore</code> weiterhin Zugriff auf die dort verwalteten Datenbanken und Tabellen bereit. Eine harte, erzwungene Migration ist damit nicht nötig &ndash; bestehende Hive-Metastore-Objekte und neue Unity-Catalog-Kataloge (z. B. <code>dev</code>, <code>prod</code>) lassen sich parallel referenzieren.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Vor Unity Catalog nutzte Databricks für Governance ein älteres, Hive-Metastore-basiertes <strong>Table-ACL-Modell</strong> mit einem eigenen, leicht abweichenden Satz an Privilegien: <code>SELECT</code>, <code>MODIFY</code>, <code>CREATE</code>, <code>READ_METADATA</code> (Metadaten eines Objekts einsehen), <code>USAGE</code> (ohne inhaltliche Wirkung, aber Voraussetzung für jede Aktion auf einem Datenbankobjekt) und <code>ALL PRIVILEGES</code>, vergeben ebenfalls über <code>GRANT ... ON ... TO ...</code> auf die Objekttypen <code>CATALOG</code>, <code>SCHEMA</code>, <code>TABLE</code>, <code>VIEW</code>, <code>FUNCTION</code> sowie <code>ANY FILE</code> für Zugriff auf das zugrunde liegende Dateisystem. Wer Rechte vergeben durfte, richtete sich nach der Objekt-Eigentümerschaft (Databricks-Administrator: alle Objekte im Catalog und Dateisystem; Catalog-Owner: alle Objekte im Catalog; Database-Owner: alle Objekte in der Datenbank; Table-Owner: nur die eigene Tabelle). Unity Catalog übernimmt das Grundprinzip (<code>GRANT</code>/<code>REVOKE</code>, Owner-basierte Rechtevergabe), ersetzt aber <code>ANY FILE</code> durch die feingranularen <code>READ FILES</code>/<code>WRITE FILES</code>-Privilegien auf Volumes bzw. External Locations und führt zusätzlich <code>USE CATALOG</code> als neue, durch die dritte Namensebene (Catalog) nötig gewordene Voraussetzung ein &ndash; <code>USAGE</code> und <code>READ_METADATA</code> entfallen dagegen als eigenständige Privilegien.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/data-governance/unity-catalog/">What is Unity Catalog? &ndash; Databricks-Dokumentation</a> &middot; <a href="https://docs.databricks.com/aws/en/admin/users-groups/">Manage users and groups &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 7 - Governance and Security\08 Unity Catalog vertieft - Architektur, Identitaeten und vollstaendiges Rechtemodell.pdf",
    title="Unity Catalog vertieft: Architektur, Identitäten und vollständiges Rechtemodell",
    subtitle="Section 7 &middot; Governance and Security &middot; Quelle: Udemy-Kursmaterial &bdquo;Unity Catalog&ldquo; &amp; &bdquo;Data object privileges&ldquo;, erg&auml;nzt mit Databricks-Dokumentation",
    body_html=body,
    build_name="gap_s7_uc_vertieft",
)
print("OK")
