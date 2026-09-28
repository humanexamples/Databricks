# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Die vorherigen Kapitel dieses Themenordners haben die technischen Bausteine behandelt &ndash; ACLs, Row Filters, Pseudonymisierung, Change Data Feed. Dieses Kapitel führt zusammen, welche regulatorischen Anforderungen dahinterstehen und worauf beim tatsächlichen, physischen Löschen von Daten in einem Lakehouse besonders zu achten ist. Denn ein <code>DELETE</code>-Statement allein reicht bei personenbezogenen Daten oft nicht aus, um eine Löschanfrage rechtlich vollständig zu erfüllen.</p>

<h2>1. DSGVO und CCPA: die wichtigsten Eckpunkte</h2>
<p>Die europäische <strong>DSGVO</strong> (Datenschutz-Grundverordnung) und der kalifornische <strong>CCPA</strong> (California Consumer Privacy Act) sind die beiden einflussreichsten Datenschutzregelwerke, an denen sich international tätige Unternehmen orientieren. Beide verlangen im Kern, dass Unternehmen personenbezogene Daten zu einer Person identifizieren und auf Anfrage exportieren, korrigieren oder löschen können &ndash; und das innerhalb klar definierter Fristen.</p>

<figure class="img">
<img src="assets/05/gdpr-ccpa-overview.png">
<figcaption>DSGVO (EU) und CCPA (Kalifornien) verlangen im Kern dieselben drei Nutzerrechte: Auskunft, Berichtigung und Löschung &ndash; jeweils fristgebunden.</figcaption>
</figure>

<table>
<tr><th>Regelwerk</th><th>Bearbeitungsfrist</th><th>Sanktionen bei Verstoß</th></tr>
<tr><td>DSGVO (EU)</td><td>i. d. R. 30 Tage</td><td>bis zu 4 % des Jahresumsatzes oder 20 Mio. &euro; (was höher ist)</td></tr>
<tr><td>CCPA (Kalifornien)</td><td>Eingangsbestätigung innerhalb 10 Werktagen, Bearbeitung innerhalb 45 Tagen</td><td>bis zu 2.500 $ je Verstoß, 750 $ je Verbraucher und Vorfall</td></tr>
</table>

<p>Da sich die Detailanforderungen beider Regelwerke unterscheiden, viele Unternehmen aber sowohl in der EU als auch in Kalifornien tätig sind, empfiehlt sich eine einzige, konservative Policy, die beide Anforderungen gleichzeitig erfüllt. Delta Lake und die Lakehouse-Architektur helfen dabei strukturell: Durch ACID-Transaktionsgarantien und Schema-Durchsetzung wird verhindert, dass PII unbemerkt durch Schema-Abweichungen oder fehlgeschlagene Jobs im System verstreut bleibt, und Änderungen an Tabellenhistorie und Change Data Feed (siehe Kapitel 05-4) schaffen die Nachvollziehbarkeit, die Audits verlangen.</p>

<h2>2. Warum DELETE allein nicht reicht: Delta-Historie und Time Travel</h2>
<p>Delta Lake löscht Zeilen nicht, indem vorhandene Dateien verändert werden &ndash; stattdessen werden neue Datendateien ohne die gelöschten Zeilen geschrieben, während die <strong>alten Dateien und Tabellenversionen zunächst erhalten bleiben</strong>. Das ist die Grundlage für Time Travel und Rollbacks, hat aber eine wichtige Konsequenz für Löschanfragen: Nach einem <code>DELETE</code> sind die betroffenen Zeilen zwar aus der aktuellen Version verschwunden, in älteren Versionen der Tabelle aber weiterhin abrufbar.</p>

{code('sql', '''-- Aktuelle Version: geloeschte Nutzer sind nicht mehr enthalten
SELECT count(*) AS TotalRows FROM gold_users;
-- z.B. 3.387 Zeilen

-- Aeltere Version (vor dem DELETE): geloeschte Nutzer sind weiterhin sichtbar!
SELECT count(*) AS TotalRows FROM gold_users VERSION AS OF 0;
-- z.B. 3.407 Zeilen -- inklusive der 20 "geloeschten" Nutzer''')}

<p>Für eine DSGVO-konforme Löschung reicht ein <code>DELETE</code> also nicht aus &ndash; die alten Dateiversionen müssen zusätzlich <strong>physisch</strong> entfernt werden.</p>

<h2>3. VACUUM: das tatsächliche physische Löschen</h2>
<p>Der Befehl <code>VACUUM</code> entfernt Datendateien, die von keiner aktuell referenzierten Tabellenversion mehr benötigt werden und älter sind als die konfigurierte Aufbewahrungsfrist (Standard: 7 Tage). Erst nach einem erfolgreichen <code>VACUUM</code> sind die Rohdaten wirklich aus dem Cloud-Speicher entfernt.</p>

{code('sql', '''-- Standard-VACUUM: entfernt Dateien aelter als 7 Tage (Default-Schutzschwelle)
VACUUM gold_users;

-- Fuer eine sofortige, vollstaendige Loeschung (z.B. akute DSGVO-Anfrage):
-- 1. Sicherheitscheck der 7-Tage-Mindestfrist deaktivieren
SET spark.databricks.delta.retentionDurationCheck.enabled = false;

-- 2. Trockenlauf: welche Dateien wuerden geloescht? (nichts wird tatsaechlich entfernt)
VACUUM gold_users RETAIN 0 HOURS DRY RUN;

-- 3. Tatsaechliches, sofortiges physisches Loeschen
VACUUM gold_users RETAIN 0 HOURS;''')}

<p>Wichtig: Auch der <strong>Change Data Feed</strong> folgt derselben Aufbewahrungsfrist wie die Tabellenhistorie &ndash; erst mit <code>VACUUM</code> werden auch die zugehörigen CDF-Änderungsdateien entfernt. Wer also über CDF Löschungen propagiert (Kapitel 05-4), muss zusätzlich sicherstellen, dass die Quelltabelle regelmäßig vacuumed wird, damit gelöschte PII nicht dauerhaft in alten CDF-Dateien liegen bleibt. Aus Effizienzgründen empfiehlt es sich außerdem, Löschungen möglichst an Partitionsgrenzen auszurichten &ndash; dann können ganze Partitionen entfernt werden, statt einzelne Zeilen aus großen Dateien neu zu schreiben.</p>

<h2>4. Sonderfall: Deletion Vectors</h2>
<p>Bei Tabellen mit aktivierten <strong>Deletion Vectors</strong> (einer Performance-Optimierung, die gelöschte Zeilen zunächst nur markiert statt Dateien sofort neu zu schreiben) reicht <code>VACUUM</code> allein nicht aus, um wirklich alle referenzierten Datensätze physisch zu entfernen. Zusätzlich ist ein <code>REORG TABLE ... APPLY (PURGE)</code> nötig, das die markierten Zeilen endgültig aus den zugrunde liegenden Dateien entfernt, bevor die alten Dateiversionen per <code>VACUUM</code> gelöscht werden können.</p>

{code('sql', '''REORG TABLE gold_users APPLY (PURGE);
VACUUM gold_users RETAIN 0 HOURS;''')}

<h2>5. Einschränkungen bei DML auf Streaming Tables und Materialized Views</h2>
<p>Nicht jedes Zielobjekt in einer deklarativen Pipeline lässt sich beliebig per <code>DELETE</code>/<code>UPDATE</code> bearbeiten:</p>
<ul>
<li><strong>Streaming Tables</strong> gehen von append-only-Quellen aus; direkte, manuelle <code>DELETE</code>/<code>UPDATE</code>-Statements sind mit dem inkrementellen Verarbeitungsmodell nur eingeschränkt vereinbar. Für strukturierte Änderungspropagierung wird stattdessen <code>AUTO CDC INTO</code> (vormals <code>APPLY CHANGES INTO</code>) verwendet. Für das dauerhafte, gezielte Löschen einzelner Nutzer aus einer Streaming Table lässt sich in Lakeflow Declarative Pipelines eine konfigurierbare Aufbewahrungsfrist bzw. ein Pipeline-Reset einsetzen, um die Tabelle kontrolliert neu aufzubauen.</li>
<li><strong>Materialized Views</strong> lassen grundsätzlich <strong>kein</strong> direktes <code>INSERT</code>, <code>UPDATE</code> oder <code>DELETE</code> zu &ndash; ihr Inhalt ist stets das Ergebnis der letzten <code>REFRESH</code>-Berechnung. Eine Löschung in einer darunterliegenden Quelltabelle wird erst nach dem nächsten (vollständigen oder inkrementellen) Refresh der Materialized View sichtbar.</li>
</ul>
<p>Für produktive GDPR-Workflows bedeutet das: Löschungen werden auf der (Streaming-)Bronze- oder Silver-Ebene angestoßen und über CDF in nachgelagerte Tabellen propagiert (siehe Kapitel 05-4); Materialized Views in der Gold-Schicht aktualisieren sich dabei automatisch über ihren nächsten Refresh-Zyklus mit.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks bestätigt explizit, dass Delta Lake standardmäßig gelöschte Datensätze für 30 Tage in der Tabellenhistorie vorhält (nutzbar für Time Travel und Rollbacks), und dass erst ein <code>VACUUM</code>-Lauf diese physisch aus dem Cloud-Speicher entfernt &ndash; ein Standard-<code>VACUUM</code> reduziert dabei die Time-Travel-Fähigkeit auf die konfigurierte Aufbewahrungsfrist (Default 7 Tage, konfigurierbar). Für Tabellen mit aktivierten Deletion Vectors wird zusätzlich <code>REORG TABLE ... APPLY (PURGE)</code> benötigt, um bereits als gelöscht markierte Datensätze endgültig aus den zugrunde liegenden Dateien zu entfernen, bevor VACUUM sie physisch löschen kann.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/security/privacy/gdpr-delta">Prepare your data for GDPR compliance &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 7 - Governance and Security\05 Compliance - DSGVO,CCPA & Datenloeschung.pdf",
    title="Compliance: DSGVO/CCPA & Datenlöschung",
    subtitle="Section 7 &middot; Governance and Security &middot; Quelle: Kurs 6, Regulatory Compliance &amp; DP 1.3",
    body_html=body,
    build_name="05_05_compliance_dsgvo_ccpa",
)
print("OK")
