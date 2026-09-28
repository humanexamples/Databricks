# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Ein Job, der im Test funktioniert, ist noch kein produktionsreifer Workflow. Der Übergang von der Entwicklung in den produktiven Betrieb erfordert Entscheidungen zu Compute-Strategie, Kostenmodell, Versionskontrolle und Architektur. Dieses Dokument fasst die wichtigsten Best Practices für den Betrieb von Lakeflow Jobs in Produktionsumgebungen zusammen &ndash; inklusive modularer Orchestrierung, bei der ein Job andere Jobs oder Pipelines aufruft.</p>

<h2>1. Die richtige Compute-Wahl für Produktion</h2>
<p>Für den produktiven Einsatz sind drei Compute-Kategorien relevant, die sich deutlich in Kosten- und Betriebscharakteristik unterscheiden:</p>
<table>
<tr><th>Compute-Typ</th><th>Vorteile</th><th>Nachteile</th></tr>
<tr><td><strong>Interactive Clusters</strong></td><td>Sofort verfügbar, gut für Exploration</td><td>Läuft auch im Leerlauf weiter &rarr; unnötige Kosten; nicht für Produktion empfohlen</td></tr>
<tr><td><strong>Job Clusters</strong></td><td>Terminiert automatisch nach Jobende &rarr; deutlich günstiger, dedizierte Ressourcen pro Job</td><td>Cloud-seitige Startzeit verzögert den Beginn der Verarbeitung</td></tr>
<tr><td><strong>Serverless</strong></td><td>Kein Cluster-Management, schnellerer Start, automatische Skalierung, einheitlicher Preis inkl. Infrastruktur</td><td>Weniger granulare Infrastruktur-Kontrolle</td></tr>
</table>
<p>Für die meisten produktiven Workloads gilt Serverless heute als bevorzugte Empfehlung, da es operative Komplexität reduziert: Statt separate Kosten für Databricks-Units (DBUs) und Cloud-Infrastruktur (VMs, Netzwerk, Sicherheitsdienste) zu verwalten, entsteht ein einheitlicher DBU-Preis. Klassische Job-Cluster bleiben dennoch eine solide, kosteneffiziente Wahl, insbesondere wenn feingranulare Cluster-Konfiguration benötigt wird.</p>

<h2>2. Modulare Orchestrierung: der Run-Job-Task</h2>
<p>Große, monolithische Workflows mit hunderten Tasks werden schnell unübersichtlich und schwer wartbar. Die Lösung: den Workflow in <strong>logische, fachliche Einheiten</strong> zerlegen statt in rein technische Bausteine. Jede Einheit wird als eigener Job modelliert; ein übergeordneter <strong>Parent-Job</strong> orchestriert die <strong>Child-Jobs</strong> über den speziellen Task-Typ <strong>Run Job</strong>. Das bringt mehrere Vorteile:</p>
<ul>
<li><strong>Wartbarkeit</strong> &ndash; kleinere Jobs sind leichter zu verstehen, anzupassen und zu debuggen.</li>
<li><strong>Wiederverwendbarkeit</strong> &ndash; ein Child-Job lässt sich in mehreren übergeordneten Workflows einsetzen.</li>
<li><strong>Teamzusammenarbeit</strong> &ndash; unterschiedliche Teams können unterschiedliche Module eigenverantwortlich betreuen, während der Gesamt-Workflow konsistent bleibt.</li>
<li><strong>Testbarkeit</strong> &ndash; einzelne Module lassen sich isoliert testen, was Qualität erhöht und Deployment-Risiko senkt.</li>
</ul>

<figure class="img">
<img src="assets/02/modular_design.png">
<figcaption>Ein übergeordneter Job ruft über Run-Job-Tasks mehrere unabhängige, wiederverwendbare Child-Jobs auf.</figcaption>
</figure>

<p>Praktisch wird dazu zunächst ein eigenständiger Job (z.&nbsp;B. für einen bestimmten Verarbeitungsschritt) erstellt. Im übergeordneten Master-Job wird anschließend ein Task vom Typ <strong>Run Job</strong> hinzugefügt, der auf diesen eigenständigen Job verweist. Über <strong>Depends on</strong> und <strong>Run if dependencies</strong> lässt sich der Run-Job-Task genauso in den DAG einbetten wie jeder andere Task-Typ &ndash; inklusive Parameterübergabe und Repair-Run-Unterstützung im Fehlerfall.</p>

<h2>3. Jobs und Git: versionskontrollierte Produktion</h2>
<p>Für produktive Jobs empfiehlt sich, den Quellcode direkt aus einem Git-Repository auszuführen, statt Notebooks manuell im Workspace zu pflegen. Das bringt mehrere Vorteile mit sich:</p>
<ul>
<li><strong>Änderungsmanagement</strong> &ndash; unbeabsichtigte Änderungen an Produktions-Jobs werden verhindert, da alles über kontrollierte Versionsverwaltung läuft.</li>
<li><strong>Single Source of Truth</strong> &ndash; es ist jederzeit klar, welche Codeversion produktiv läuft, da stets aus einem bestimmten Branch oder Tag ausgeführt wird.</li>
<li><strong>CI/CD-Integration</strong> &ndash; automatisierte Test- und Deployment-Pipelines können Änderungen validieren, bevor sie produktiv werden.</li>
<li><strong>Breite Plattform-Unterstützung</strong> &ndash; GitHub, GitLab, AWS CodeCommit und weitere Anbieter werden unterstützt.</li>
</ul>
<p>Die Konfiguration erfolgt in zwei Schritten: Zunächst wird für den Task als Quelle ein Git-Provider mit Repository, Branch/Tag und Zugangsdaten hinterlegt; anschließend wird der Pfad zum Hauptnotebook relativ zum Repository-Root angegeben. Für Produktionsumgebungen empfiehlt sich die Nutzung fester Branches oder Tags statt sich ständig ändernder Hauptbranches, kombiniert mit Code-Review-Prozessen vor dem Merge in den Produktions-Branch.</p>

<h2>4. Zusammengefasste Best Practices</h2>
<table>
<tr><th>Bereich</th><th>Empfehlung</th></tr>
<tr><td>Compute &amp; Kosten</td><td>Job-Cluster oder Serverless statt Interactive Clusters; Photon aktivieren; Cluster über Tasks hinweg wiederverwenden, wo möglich</td></tr>
<tr><td>Orchestrierung</td><td>Komplexe Pipelines modular über Run-Job-Tasks aufteilen; Multi-Task-Jobs für parallele Verarbeitung nutzen; Jobs unter 1000 Tasks halten</td></tr>
<tr><td>Monitoring &amp; Governance</td><td>Service Principals statt persönlicher Konten für Job-Ownership verwenden; umfassende Benachrichtigungen konfigurieren; Repair &amp; Rerun zur Kostenoptimierung im Fehlerfall nutzen</td></tr>
<tr><td>Wiederverwendbarkeit</td><td>Tasks konsequent parametrisieren, statt Werte hart zu codieren</td></tr>
</table>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Aktuelle Best-Practice-Empfehlungen von Databricks bestätigen, dass der Wechsel von interaktiven Clustern zu Job-Compute typischerweise erhebliche Einsparungen ermöglicht (häufig im Bereich von 40&ndash;60&nbsp;%), und dass Serverless durch verbrauchsbasierte Abrechnung ohne Vorab-Provisionierung oft die niedrigsten Gesamtbetriebskosten (TCO) für elastische oder schwer vorhersehbare Workloads erzielt. Ergänzend empfohlen: Autoscaling und Auto-Termination konsequent aktivieren, DBU-Verbrauch regelmäßig überprüfen und Jobs mit Kostenstellen-Tags versehen, um Kosten verursachergerecht zuzuordnen.<br>
Quelle: <a href="https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/best-practices">Best practices for serverless compute &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 4 - Working with Lakeflow Jobs\05 Lakeflow Jobs in Produktion - Best Practices und modulare Orchestrierung.pdf",
    title="Lakeflow Jobs in Produktion: Best Practices & modulare Orchestrierung",
    subtitle="Section 4 &middot; Working with Lakeflow Jobs &middot; Quelle: Kurs 2, Kapitel 13, 15",
    body_html=body,
    build_name="02_05_best_practices",
)
print("OK")
