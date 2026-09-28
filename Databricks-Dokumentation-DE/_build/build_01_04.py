# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Cloud-Speicher-Dateien wie CSV, JSON oder Parquet sind nur ein Teil der Realität in Unternehmen: Ein großer Anteil der geschäftskritischen Daten liegt in Datenbanken (SQL Server, PostgreSQL, MySQL, &hellip;) oder in SaaS-Anwendungen (Salesforce, Workday, ServiceNow, SharePoint, &hellip;). Für diese Quellen wäre selbst geschriebener Ingestion-Code aufwändig zu pflegen &ndash; er müsste sich um Authentifizierung, inkrementelles Nachladen, API-Limits und Schema-Änderungen der Quelle selbst kümmern. Genau hier setzen die <strong>Managed Connectors</strong> von Lakeflow Connect an.</p>

<h2>1. Managed Connectors: vorgefertigte Ingestion für Enterprise-Quellen</h2>
<p>Managed Connectors sind fest in Databricks integrierte, von Databricks selbst betriebene Konnektoren für konkrete Enterprise-Datenquellen. Anders als die in den vorherigen Kapiteln behandelten <em>Standard Connectors</em> (die generisch auf Cloud-Speicher oder Kafka via <code>read_files()</code> zugreifen) sind Managed Connectors auf eine bestimmte Quelle spezialisiert &ndash; z. B. Salesforce, Workday, SQL Server, PostgreSQL, ServiceNow, SharePoint oder Google Analytics. Sie lassen sich per Point-and-Click-Oberfläche oder API einrichten und übernehmen Authentifizierung, inkrementelle Synchronisation und Skalierung vollständig verwaltet.</p>

<figure class="img">
<img src="assets/01/managed-connectors-data-sources.png">
<figcaption>Managed Connectors bündeln den Zugriff auf verbreitete Enterprise-Quellen (Workday, Salesforce, PostgreSQL, SQL Server, Dynamics 365, ServiceNow, SharePoint, u. v. m.) über eine einheitliche, verwaltete Schnittstelle.</figcaption>
</figure>

<h2>2. Zwei Architekturen je nach Quelltyp</h2>
<p>Intern unterscheidet Lakeflow Connect zwischen zwei Architektur-Mustern, je nachdem ob die Quelle öffentlich über eine API erreichbar ist (SaaS) oder in einem privaten Netzwerk liegt (Datenbank):</p>

<h3>2.1 SaaS-Ingestion (z. B. Salesforce, Workday)</h3>
<p>Bei SaaS-Anwendungen ist die Datenquelle über eine öffentlich erreichbare API oder einen OLAP-Endpunkt ansprechbar. Eine serverlose, deklarative Pipeline holt sich die Zugangsdaten aus Unity Catalog, ruft die API der Quelle auf und schreibt das Ergebnis direkt in eine Streaming-Delta-Tabelle. Sämtliche Datenbewegung findet dabei in der sogenannten <em>Data Plane</em> statt; die <em>Control Plane</em> von Databricks wird nur für Einrichtung und Monitoring genutzt.</p>

<h3>2.2 Datenbank-Ingestion (z. B. SQL Server, PostgreSQL)</h3>
<p>Datenbanken liegen häufig hinter einer Firewall oder sind nicht öffentlich erreichbar &ndash; deshalb kommt hier ein zusätzlicher Baustein zum Einsatz: die <strong>Ingestion Gateway</strong>. Sie läuft als eigene Pipeline auf klassischem Compute (nicht serverlos) direkt im Netzwerk der Quelle, verbindet sich mit der Datenbank und extrahiert Metadaten, Snapshots und Change-Logs. Diese Zwischenergebnisse werden in einem Unity-Catalog-Volume zwischengespeichert, bevor eine zweite, serverlose Pipeline die Daten final in Streaming-Delta-Tabellen überführt.</p>

<figure class="img">
<img src="assets/01/database-ingestion-architecture.png">
<figcaption>Datenbank-Ingestion mit Lakeflow Connect: Die Ingestion Gateway verbindet sich mit der Datenbank und legt Zwischenergebnisse in einem Unity-Catalog-Volume ab; eine serverlose Pipeline übernimmt anschließend die Ingestion in Streaming-Delta-Tabellen.</figcaption>
</figure>

<p>Der Grund für diesen zweistufigen Aufbau ist vor allem Netzwerk- und Lastmanagement: Die Gateway kann innerhalb des privaten Netzwerks der Kundenumgebung betrieben werden (falls kein Private Link zur Verfügung steht), und sie bündelt die Verbindungslast zur Quelldatenbank, statt für jede nachgelagerte Pipeline eine eigene Direktverbindung aufzubauen. Bei SaaS-Quellen entfällt dieses Problem, da die Last dort typischerweise über API-Limits des Anbieters selbst geregelt wird.</p>

<h2>3. Partner Connect: wenn kein Managed Connector existiert</h2>
<p>Nicht für jede denkbare Quelle gibt es (noch) einen nativen Managed Connector. Für diesen Fall bietet Databricks <strong>Partner Connect</strong> an: Direkt aus der Databricks-Oberfläche lassen sich Testkonten bei ausgewählten Technologiepartnern (u. a. Fivetran, Informatica, Qlik, Rivery, Alteryx, Prophecy) anlegen und mit dem eigenen Workspace verbinden. Das ermöglicht es, Partnerlösungen mit den eigenen Daten im Lakehouse auszuprobieren, bevor man sich für eine dauerhafte Integration entscheidet. Databricks betont ausdrücklich, dass diese Partneroptionen auch dann bestehen bleiben, wenn später ein nativer Managed Connector für dieselbe Quelle verfügbar wird &ndash; es geht um Wahlfreiheit, nicht um Ablösung.</p>

<h2>4. Ausblick: weitere Integrationsfunktionen</h2>
<p>Über die eigentliche Ingestion hinaus bietet Databricks noch weitere Bausteine für Datenintegration und -austausch, die in diesem Kurs nur gestreift werden:</p>
<ul>
<li><strong>Lakehouse Federation</strong> &ndash; externe Datenquellen (z. B. andere Datenbanken) direkt per Abfrage anzapfen, ohne die Daten vorher zu kopieren; nützlich für Ad-hoc-Reporting, Proof-of-Concepts oder während einer schrittweisen Migration.</li>
<li><strong>Zerobus</strong> &ndash; eine Lakeflow-Connect-API, mit der Anwendungen Ereignisdaten (IoT, Clickstreams, Telemetrie) direkt und mit sehr hohem Durchsatz nahezu in Echtzeit in die Lakehouse schreiben können.</li>
<li><strong>Delta Sharing</strong> &ndash; ein offenes Protokoll zum sicheren Teilen von Daten über Plattform-, Cloud- und Regionsgrenzen hinweg, ohne die Daten physisch zu duplizieren.</li>
<li><strong>Databricks Marketplace</strong> &ndash; ein auf Delta Sharing basierender offener Marktplatz für Datensätze, Notebooks, Dashboards, ML-Modelle und Solution Accelerators, über den sich kuratierte Datenprodukte externer Anbieter mit wenigen Klicks in den eigenen Katalog holen lassen.</li>
</ul>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Die Liste der Managed Connectors wächst kontinuierlich und umfasst inzwischen mehr als 30 SaaS-Anwendungen und Datenbanken. Bereits allgemein verfügbar (GA) sind unter anderem die Connectoren für <strong>Salesforce</strong>, <strong>Workday</strong> und <strong>SQL Server</strong>; über Change Data Capture werden zudem Datenbanken wie <strong>PostgreSQL</strong> und <strong>MySQL</strong> unterstützt. Neuere Ergänzungen betreffen unter anderem <strong>Dynamics 365</strong>, <strong>Google Ads</strong>, <strong>Meta Ads</strong>, <strong>Confluence</strong>, <strong>Jira</strong>, <strong>ServiceNow</strong>, <strong>SharePoint</strong> und <strong>Google Drive</strong>. Da sich der Reifegrad (Public Preview vs. General Availability) einzelner Connectoren laufend ändert, lohnt sich vor einem produktiven Einsatz stets ein Blick in die aktuelle Konnektor-Übersicht.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/">Managed connectors in Lakeflow Connect &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 2 - Data Ingestion and Loading\04 Enterprise-Datenintegration mit Lakeflow Connect.pdf",
    title="Enterprise-Datenintegration mit Lakeflow Connect",
    subtitle="Section 2 &middot; Data Ingestion and Loading &middot; Quelle: Kurs 1, Kapitel 14&ndash;16",
    body_html=body,
    build_name="01_04_enterprise",
)
print("OK")
