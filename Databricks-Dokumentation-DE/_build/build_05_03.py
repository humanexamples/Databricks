# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Bevor personenbezogene Daten (PII) analysiert, für Machine Learning genutzt oder an nachgelagerte Teams weitergegeben werden, sollten sie entweder <strong>pseudonymisiert</strong> oder <strong>anonymisiert</strong> werden. Wichtig vorab: Mit ausreichend Zeit und Zusatzdaten lässt sich praktisch jeder Datensatz re-identifizieren &ndash; beide Techniken reduzieren also das Risiko, beseitigen es aber nicht vollständig. Der grundlegende Unterschied liegt darin, <em>was</em> geschützt wird und <em>ob</em> der Vorgang umkehrbar ist.</p>

<figure class="img">
<img src="assets/05/pseudo-vs-anonym.png">
<figcaption>Pseudonymisierung schützt einzelne Datensätze und bleibt reversibel; Anonymisierung schützt den gesamten Datensatz und ist irreversibel.</figcaption>
</figure>

<h2>1. Pseudonymisierung: reversibel, auf Record-Ebene</h2>
<p>Bei der Pseudonymisierung wird ein personenbezogenes Merkmal (z. B. eine <code>user_id</code>) durch einen künstlichen Bezeichner ersetzt. Der Clou: Über eine gesicherte Zuordnungstabelle oder eine deterministische Funktion lässt sich der Original-Wert bei Bedarf wiederherstellen. Rechtlich wichtig: <strong>Pseudonymisierte Daten gelten nach DSGVO weiterhin als personenbezogene Daten</strong> &ndash; die Pseudonymisierung ersetzt keine Löschpflicht, sie schützt lediglich vor unautorisiertem Zugriff auf den Klartext. Zwei Verfahren kommen zum Einsatz: Hashing und Tokenisierung.</p>

<h3>1.1 Hashing mit Salt</h3>
<p>Eine Hash-Funktion erzeugt aus einem Eingabewert eine Zeichenkette fester Länge. Da Hash-Funktionen deterministisch sind, könnte derselbe Eingabewert (z. B. eine bekannte User-ID) durch simples Ausprobieren zurückgerechnet werden. Um das zu erschweren, wird vor dem Hashing ein zufälliger, geheimer Wert &ndash; das <strong>Salt</strong> &ndash; angehängt. In produktiven Pipelines sollte dieses Salt nicht im Klartext im Code stehen, sondern über die <strong>Databricks Secrets API</strong> (<code>dbutils.secrets.get(...)</code>) verwaltet werden, sodass nur berechtigte Jobs und Nutzer darauf zugreifen können. Das folgende Beispiel stammt aus der echten Pipeline <code>DP 1.2.1 - Pseudonymized PII Lookup Table</code>:</p>

{code('python', '''from pyspark import pipelines as dp
import pyspark.sql.functions as F

# In dieser Demo als Klartext-Variable; produktiv ueber
# dbutils.secrets.get(scope="pii", key="hash_salt") aus einem Secret Scope laden
salt = "BEANS"

# Funktion zum Pseudonymisieren per Salted Hashing
def salted_hash(id):
    return F.sha2(F.concat(id, F.lit(salt)), 256)

# Pseudonymisierte Lookup-Tabelle: alt_id ersetzt user_id in allen Downstream-Tabellen
@dp.table
def user_lookup_hashed():
    return (dp
            .read_stream("registered_users")
            .select(
                  salted_hash(F.col("user_id")).alias("alt_id"),
                  "device_id", "mac_address", "user_id")
           )''')}

<p>Nur die schmale <code>user_lookup_hashed</code>-Tabelle enthält später noch die Verbindung zwischen <code>alt_id</code> und der echten <code>user_id</code>; alle anderen Pipelines arbeiten ausschließlich mit der pseudonymisierten <code>alt_id</code>. Wird der Zugriff auf diese eine Lookup-Tabelle konsequent eingeschränkt, lässt sich die Re-Identifikation im gesamten übrigen System wirksam verhindern.</p>

<h3>1.2 Tokenisierung</h3>
<p>Bei der Tokenisierung wird jedem eindeutigen Wert ein zufälliges Token (meist eine UUID) zugewiesen und die Zuordnung in einem separaten, gesicherten <strong>Token-Vault</strong> gespeichert. Tokenisierung ist beim Schreiben langsamer als Hashing, da ein Join gegen die Vault-Tabelle nötig ist &ndash; beim Lesen dafür effizient, da nur der Token weitergereicht wird.</p>

{code('python', '''# Vault-Tabelle: pro eindeutigem user_id ein zufaelliges Token
@dp.table
def registered_users_tokens():
    return (dp
            .readStream("registered_users")
            .select("user_id")
            .distinct()
            .withColumn("token", F.expr("uuid()"))
        )

# Pseudonymisierte Lookup-Tabelle: user_id wird durch Token (alt_id) ersetzt
@dp.table
def user_lookup_tokenized():
    return (dp
            .read_stream("registered_users")
            .join(dp.read("registered_users_tokens"), "user_id", "left")
            .drop("user_id")
            .withColumnRenamed("token", "alt_id")
           )''')}

<h2>2. Anonymisierung: irreversibel, auf Datensatz-Ebene</h2>
<p>Anonymisierung verändert personenbezogene Daten so, dass eine Person <strong>weder direkt noch indirekt</strong> identifiziert werden kann &ndash; und das absichtlich unumkehrbar. Anders als Pseudonymisierung schützt sie meist den gesamten Datensatz statt einzelner Datensätze und eignet sich besonders für Business-Intelligence-Anwendungsfälle, bei denen Trends und Aggregationen wichtiger sind als Einzelwerte. In der Praxis kombiniert man meist mehrere Techniken.</p>

<h3>2.1 Suppression (Unterdrückung)</h3>
<p>Bedingte Filter und dynamische Zugriffskontrollen (siehe Kapitel 05-2 zu Row Filters/Dynamic Views) entfernen ganze Spalten oder Zeilen aus dem Ergebnis, ohne die Auswertungsfähigkeit für Aggregationen einzuschränken. Auch Gruppen mit sehr niedriger Datensatzanzahl (z. B. "nur ein Kunde in dieser Postleitzahl") sollten gefiltert werden, da solche Kleinstgruppen re-identifizierbar sind.</p>

<h3>2.2 Generalisierung (Binning, Kategorisierung, Kürzung, Rundung)</h3>
<p>Generalisierung nimmt Daten gezielt Präzision, ohne sie ganz zu entfernen: Städte werden zu Bundesländern zusammengefasst (kategoriale Generalisierung), exakte Werte werden in Bänder/Bins gruppiert, IP-Adressen werden auf ein <code>/24</code>-Subnetz gekürzt (letztes Byte auf 0 gesetzt), und Zahlen werden gerundet. Das folgende Beispiel aus der Pipeline <code>DP 1.2.2 - Anonymized Users Age</code> zeigt <strong>Binning</strong>: Statt eines exakten Geburtsdatums wird nur noch eine Altersspanne gespeichert.</p>

{code('python', '''def age_bins(dob_col):
    age_col = F.floor(F.months_between(F.current_date(), dob_col) / 12).alias("age")
    return (
        F.when((age_col < 18), "under 18")
        .when((age_col >= 18) & (age_col < 25), "18-25")
        .when((age_col >= 25) & (age_col < 35), "25-35")
        .when((age_col >= 35) & (age_col < 45), "35-45")
        .when((age_col >= 45) & (age_col < 55), "45-55")
        .when((age_col >= 55) & (age_col < 65), "55-65")
        .when((age_col >= 65) & (age_col < 75), "65-75")
        .when((age_col >= 75) & (age_col < 85), "75-85")
        .when((age_col >= 85) & (age_col < 95), "85-95")
        .when((age_col >= 95), "95+")
        .otherwise("invalid age")
        .alias("age")
    )

@dp.table
def user_age_bins():
    return (
        dp.read("users_bronze")
        .select("user_id", age_bins(F.col("dob")), "gender", "city", "state")
    )''')}

<p>Aus dem exakten Geburtsdatum &ndash; einem eindeutigen, hoch identifizierenden Merkmal &ndash; wird so eine von zehn groben Alterskategorien. Auswertungen wie "Wie verteilen sich Nutzer über Altersgruppen?" bleiben möglich, eine Re-Identifikation einzelner Personen über das Geburtsdatum ist jedoch ausgeschlossen.</p>

<h2>3. Welche Technik wann?</h2>
<table>
<tr><th>Technik</th><th>Schutzgrad</th><th>Reversibel?</th><th>Typischer Einsatzzweck</th></tr>
<tr><td>Data Masking</td><td>Niedrig&ndash;Mittel</td><td>Teilweise</td><td>Operative Nutzbarkeit bei reduziertem Risiko erhalten</td></tr>
<tr><td>Pseudonymisierung (allgemein)</td><td>Niedrig&ndash;Mittel</td><td>Ja</td><td>Längsschnittstudien, bei denen Personen wiedererkennbar bleiben müssen</td></tr>
<tr><td>Hashing (mit Salt)</td><td>Mittel&ndash;Hoch</td><td>Praktisch nein (ohne Salt)</td><td>Sichere, verknüpfbare Kennungen, z. B. Passwort-Speicherung</td></tr>
<tr><td>Column Encryption</td><td>Hoch</td><td>Ja (mit Schlüssel)</td><td>Besonders sensible Einzelspalten</td></tr>
<tr><td>Tokenisierung</td><td>Hoch</td><td>Ja (über Vault)</td><td>Zahlungsdaten, Kreditkartentransaktionen</td></tr>
</table>

<p>Als Faustregel gilt: <strong>keine PII zu speichern ist immer besser, als PII zu schützen</strong>. Wo PII unvermeidbar ist, gilt die Rangfolge <em>Anonymisierung &gt; Pseudonymisierung &gt; Klartext</em>. Zusätzlich lohnt es sich, immer zu bedenken, wie sich mehrere eigentlich harmlose Datensätze kombinieren lassen, um eine Person doch wieder zu identifizieren &ndash; und PII-verarbeitende Umgebungen konsequent von anderen Workloads zu isolieren.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation und Praxisquellen:</strong> Für Salt- und Verschlüsselungsschlüssel empfiehlt sich statt eines klassischen Databricks Secret Scope zunehmend die Anbindung eines externen Schlüsselverwaltungsdienstes (z. B. Azure Key Vault) über ein Unity-Catalog-<strong>Service Credential</strong> &ndash; das zentralisiert die Schlüsselverwaltung zusätzlich zur Governance über Unity Catalog und reduziert das Risiko, dass Salts versehentlich mehrfach oder inkonsistent verwaltet werden. Als organisatorische Best Practice wird zudem empfohlen, PII-Spalten systematisch über Schema-Inspektion und automatisiertes Data-Profiling zu identifizieren, statt sich auf manuelle Dokumentation zu verlassen.<br>
Quelle: <a href="https://medium.com/databricks-platform-sme/best-practices-for-handling-pii-data-6281be8c15ae">Best Practices for handling PII data &ndash; Databricks Platform SME (Medium)</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 7 - Governance and Security\03 PII-Schutz - Pseudonymisierung & Anonymisierung.pdf",
    title="PII-Schutz: Pseudonymisierung & Anonymisierung",
    subtitle="Section 7 &middot; Governance and Security &middot; Quelle: Kurs 6, DP 1.2",
    body_html=body,
    build_name="05_03_pii_pseudonymisierung_anonymisierung",
)
print("OK")
