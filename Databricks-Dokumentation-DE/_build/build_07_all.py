# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

BASE = r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 5 - Implementing CI-CD"

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

# ---------------------------------------------------------------- 07-1
body_1 = f"""
<p>Databricks-Notebooks laden dazu ein, schnell loszulegen &ndash; doch genau das führt oft zu langen, monolithischen Skripten, die Ingestion, Transformation und Business-Logik in einer einzigen Zellenkette vermischen. Solcher Code lässt sich schwer testen, wiederverwenden oder von mehreren Personen gemeinsam pflegen. Software-Engineering-Best-Practices helfen dabei, aus Notebook-Prototypen wartbare, produktionsreife Data-Pipelines zu machen.</p>

<h2>1. Kernprinzipien guter Data-Engineering-Praxis</h2>
<ul>
<li><strong>Lesbarkeit:</strong> klare Namen, konsistente Formatierung, kurze Funktionen &ndash; reduziert Fehler bei späteren Änderungen.</li>
<li><strong>Dokumentation:</strong> Docstrings und Kommentare, die das <em>Warum</em> statt das offensichtliche <em>Was</em> erklären.</li>
<li><strong>Automatisiertes Testen:</strong> Unit- und Integrationstests, die Regressionen frühzeitig aufdecken (siehe Kapitel 3 und 4 dieses Themenordners).</li>
<li><strong>Versionskontrolle &amp; Code-Review:</strong> Änderungen nachvollziehbar machen und vor dem Merge gegenprüfen (siehe Kapitel 5).</li>
<li><strong>Isolierte Umgebungen:</strong> strikte Trennung von Entwicklungs-, Test- und Produktionsdaten (z. B. eigene Unity-Catalog-Kataloge je Umgebung).</li>
</ul>

<h2>2. Vom Monolithen zur modularen Funktion</h2>
<p>Der zentrale Refactoring-Schritt ist, wiederkehrende Logik (Schema-Definitionen, Transformationen, Schreibvorgänge) aus dem Notebook-Ablauf in benannte, einzeln testbare Python-Funktionen auszulagern und in einem gemeinsamen Modul abzulegen. Aus dem folgenden Ausschnitt eines Bronze-Ingestion-Schritts &hellip;</p>

{code('python', '''# Vorher: Schema-Definition direkt im Notebook-Flow
health_csv_schema = StructType([
    StructField("ID", IntegerType(), True),
    StructField("PII", StringType(), True),
    StructField("date", DateType(), True),
    StructField("HighCholest", IntegerType(), True),
    StructField("HighBP", DoubleType(), True),
    StructField("BMI", DoubleType(), True),
    StructField("Age", DoubleType(), True),
    StructField("Education", DoubleType(), True),
    StructField("income", IntegerType(), True)
])''')}

<p>&hellip; wird eine wiederverwendbare, dokumentierte Funktion in einem eigenen Modul <code>src/helpers/project_functions.py</code>:</p>

{code('python', '''from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType
from pyspark.sql.functions import when, col


def get_health_csv_schema():
    """Gibt das Schema für die Health-Data-CSV-Dateien zurück."""
    return StructType([
        StructField("ID", IntegerType(), True),
        StructField("PII", StringType(), True),
        StructField("date", DateType(), True),
        StructField("HighCholest", IntegerType(), True),
        StructField("HighBP", DoubleType(), True),
        StructField("BMI", DoubleType(), True),
        StructField("Age", DoubleType(), True),
        StructField("Education", DoubleType(), True),
        StructField("income", IntegerType(), True)
    ])


def high_cholest_map(col_name: str):
    """Wandelt einen numerischen Cholesterin-Code in ein lesbares Label um."""
    return (
        when(col(col_name) == 0, 'Normal')
        .when(col(col_name) == 1, 'Above Average')
        .when(col(col_name) == 2, 'High')
        .otherwise('Unknown')
    )''')}

<p>Im eigentlichen Notebook bleibt dann nur noch der eigentliche <em>Ablauf</em> übrig &ndash; lesbar als kurze Kette von Funktionsaufrufen:</p>

{code('python', '''from src.helpers.project_functions import get_health_csv_schema, high_cholest_map

health_csv_df = read_health_data(
    csv_path=f"/Volumes/{DA.catalog_name}/default/health",
    schema=get_health_csv_schema()
)
save_df_to_delta(health_csv_df, f"{DA.catalog_name}.default.health_bronze_dev", mode="overwrite")''')}

<p>Der entscheidende Vorteil: Jede einzelne Funktion (Schema-Erzeugung, Mapping-Logik, Schreibvorgang) lässt sich isoliert mit Unit-Tests absichern, ohne dass dafür ein komplettes Notebook oder ein Spark-Cluster mit echten Produktionsdaten ausgeführt werden muss.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks empfiehlt, Python-Code für Data-Engineering-Projekte nicht nur in Notebooks, sondern zusätzlich als reguläre <strong>Workspace-Files</strong> (<code>.py</code>-Module) im Git-Ordner abzulegen. Dadurch lässt sich derselbe Code sowohl per <code>import</code> aus Notebooks als auch direkt von einer lokalen IDE oder einer CI-Pipeline aus testen &ndash; eine Voraussetzung für die in Kapitel 3 behandelten Unit-Tests.</div>
"""

render_pdf(os.path.join(BASE, "01 Software-Engineering-Best-Practices und Code-Modularisierung.pdf"),
    "Software-Engineering-Best-Practices & Code-Modularisierung",
    "Section 5 &middot; Implementing CI-CD &middot; Quelle: Kurs 4, M02 Kapitel 1&ndash;4",
    body_1, "07_01_swe_best_practices")
print("07-1 OK")

# ---------------------------------------------------------------- 07-2
body_2 = f"""
<p>Bevor man Continuous-Integration- und Continuous-Deployment-Praktiken (CI/CD) konkret in Databricks umsetzt, lohnt sich ein Blick auf die dahinterliegenden Konzepte: DevOps, sein datenspezifisches Pendant DataOps, und die Rolle von CI vs. CD innerhalb dieses Lebenszyklus.</p>

<h2>1. Was ist DevOps?</h2>
<p>DevOps ist eine Kultur und eine Sammlung von Praktiken, die Software-Engineering-Best-Practices mit IT-Betrieb (Operations) verbindet, um Software schneller, zuverlässiger und in höherer Qualität auszuliefern. Der klassische DevOps-Lebenszyklus umfasst acht wiederkehrende Phasen: <em>Planen &rarr; Entwickeln (Code) &rarr; Bauen (Build) &rarr; Testen &rarr; Freigeben (Release) &rarr; Deployen &rarr; Betreiben &rarr; Überwachen (Monitor)</em> &ndash; und beginnt danach wieder von vorn.</p>

<h2>2. DataOps = DevOps für die Data-Engineering-Welt</h2>
<p>DataOps überträgt genau diese Prinzipien &ndash; Automatisierung, Zusammenarbeit, kontinuierliche Verbesserung &ndash; auf Datenpipelines: Es automatisiert das Management von Datenpipelines, überwacht deren Qualität und beschleunigt die Auslieferung neuer/geänderter Pipelines in die Produktion. Parallel dazu überträgt <strong>MLOps</strong> dieselben Prinzipien auf den Machine-Learning-Lebenszyklus (Modelltraining, -versionierung, -deployment). Alle drei Disziplinen teilen sich dieselbe Grundidee, unterscheiden sich aber in den konkreten Artefakten, die durch die Pipeline fließen: Code (DevOps), Daten (DataOps) bzw. Modelle (MLOps).</p>

<h2>3. Die Rolle von CI und CD</h2>
<p><strong>Continuous Integration (CI)</strong> bedeutet, dass Codeänderungen mehrerer Mitwirkender regelmäßig in ein zentrales Repository zusammengeführt (gemerged) und dabei automatisiert getestet werden &ndash; Tests, die fehlschlagen, verhindern, dass fehlerhafter Code in den Hauptzweig gelangt. Dabei orientiert man sich häufig an der sogenannten <em>Testpyramide</em>: an der Basis stehen viele schnelle <strong>Unit-Tests</strong> (einzelne Funktionen isoliert), darüber weniger, aber breitere <strong>Integrationstests</strong> (Zusammenspiel mehrerer Komponenten, z. B. einer ganzen Pipeline), an der Spitze wenige <strong>Systemtests</strong> (das Gesamtsystem end-to-end).</p>

<p><strong>Continuous Delivery</strong> automatisiert das Ausrollen geprüfter Änderungen in eine Staging-/Vorproduktionsumgebung, überlässt den finalen Schritt nach Produktion aber einer manuellen Freigabe. <strong>Continuous Deployment</strong> geht einen Schritt weiter: Jede Änderung, die alle Tests besteht, wird automatisch bis in die Produktionsumgebung ausgerollt &ndash; ganz ohne manuellen Eingriff. Welche der beiden Varianten sinnvoll ist, hängt vom Risiko- und Reifegrad des jeweiligen Projekts ab.</p>

<h2>4. Umgebungsisolation als Grundlage</h2>
<p>Damit CI/CD funktioniert, müssen Entwicklungs-, Test- (Stage) und Produktionsumgebung sauber voneinander getrennt sein &ndash; in Databricks typischerweise über separate Unity-Catalog-Kataloge (<code>dev</code>/<code>stage</code>/<code>prod</code>) mit jeweils eigenen Berechtigungen, sodass Entwickler nie versehentlich Produktionsdaten verändern.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Für das Testen von Lakeflow Declarative Pipelines über mehrere Umgebungen hinweg empfiehlt Databricks, gezielt Entwicklungs- und Testdatensätze mit sowohl validen als auch bewusst fehlerhaften Datensätzen anzulegen, um die Pipeline-Logik (inkl. Expectations) gegen realistische Fehlerfälle zu prüfen; jeder Pipeline-Lauf schreibt zudem ein strukturiertes Event-Log (als Delta-Tabelle abfragbar), das sich für automatisierte Prüfungen über dev/stage/prod hinweg auswerten lässt.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ldp/expectations">Manage data quality with pipeline expectations &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(os.path.join(BASE, "02 DevOps-, DataOps- und CI-CD-Grundlagen.pdf"),
    "DevOps-, DataOps- und CI/CD-Grundlagen",
    "Section 5 &middot; Implementing CI-CD &middot; Quelle: Kurs 4, M02 Kapitel 5&ndash;7",
    body_2, "07_02_devops_grundlagen")
print("07-2 OK")

# ---------------------------------------------------------------- 07-3
body_3 = f"""
<p>Unit-Tests prüfen einzelne Funktionen isoliert &ndash; ohne einen kompletten Pipeline-Lauf und ohne echte Produktionsdaten. Für PySpark-Code stellt Apache Spark seit Version 3.5 mit dem Modul <code>pyspark.testing.utils</code> zwei speziell auf DataFrames zugeschnittene Vergleichsfunktionen bereit: <code>assertDataFrameEqual</code> und <code>assertSchemaEqual</code>. In Kombination mit dem Python-Testframework <strong>pytest</strong> lassen sich damit die im vorigen Kapitel modularisierten Funktionen systematisch absichern.</p>

<h2>1. Testaufbau mit einer pytest-Fixture</h2>
<p>Da PySpark-Funktionen eine aktive <code>SparkSession</code> benötigen, wird diese üblicherweise einmal pro Testlauf über eine pytest-<strong>Fixture</strong> bereitgestellt und an alle Testfunktionen weitergereicht:</p>

{code('python', '''import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType, LongType
from pyspark.sql.functions import when, col
from pyspark.testing.utils import assertDataFrameEqual, assertSchemaEqual

from src.helpers import project_functions


@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder.getOrCreate()
    yield spark''')}

<h2>2. Schema-Test mit assertSchemaEqual</h2>
<p>Die Funktion <code>assertSchemaEqual</code> vergleicht ausschließlich das Schema zweier DataFrames (Spaltennamen, Datentypen, Nullable-Flag) &ndash; ideal, um sicherzustellen, dass eine Schema-Definitionsfunktion wie <code>get_health_csv_schema()</code> nach künftigen Änderungen weiterhin das erwartete Format liefert:</p>

{code('python', '''def test_get_health_csv_schema_match():
    expected_schema = StructType([
        StructField("ID", IntegerType(), True),
        StructField("PII", StringType(), True),
        StructField("date", DateType(), True),
        StructField("HighCholest", IntegerType(), True),
        StructField("HighBP", DoubleType(), True),
        StructField("BMI", DoubleType(), True),
        StructField("Age", DoubleType(), True),
        StructField("Education", DoubleType(), True),
        StructField("income", IntegerType(), True)
    ])

    actual_schema = project_functions.get_health_csv_schema()
    assertSchemaEqual(actual_schema, expected_schema)''')}

<h2>3. Datenvergleich mit assertDataFrameEqual</h2>
<p>Um eine Mapping-Funktion wie <code>high_cholest_map</code> zu testen, erzeugt man einen kleinen, handgeschriebenen Beispiel-DataFrame mit bekannten Eingaben, wendet die zu testende Funktion darauf an, und vergleicht das Ergebnis mit einem ebenfalls handgeschriebenen erwarteten DataFrame:</p>

{code('python', '''def test_high_cholest_column_valid_map(spark):
    data = [(0,), (1,), (2,), (3,), (4,), (None,)]
    sample_df = spark.createDataFrame(data, ["value"])

    actual_df = sample_df.withColumn("actual", project_functions.high_cholest_map("value"))

    expected_df = spark.createDataFrame(
        [(0, "Normal"), (1, "Above Average"), (2, "High"),
         (3, "Unknown"), (4, "Unknown"), (None, "Unknown")],
        schema=StructType([
            StructField("value", LongType(), True),
            StructField("actual", StringType(), True)
        ])
    )

    assertDataFrameEqual(actual_df.select(col('actual')), expected_df.select(col('actual')))''')}

<p>Wichtig: Werden diese Tests über die Kommandozeile mit <code>pytest</code> ausgeführt (nicht als Notebook-Zelle), muss der Pfad zum <code>src</code>-Modul im <code>PYTHONPATH</code> verfügbar sein, damit <code>from src.helpers import project_functions</code> funktioniert &ndash; genau dieser Aufruf ist es auch, der später in einer CI-Pipeline automatisiert ausgeführt wird (siehe Kapitel 4).</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation/Apache Spark:</strong> <code>assertDataFrameEqual</code> unterstützt zahlreiche optionale Parameter, um den Vergleich flexibel zu steuern &ndash; u. a. <code>checkRowOrder</code> (Zeilenreihenfolge ignorieren), <code>rtol</code>/<code>atol</code> (Toleranzen für Fließkommazahlen), <code>ignoreColumnOrder</code> und <code>ignoreColumnType</code>. Bei sehr großen DataFrames kann die Funktion laut Databricks-Knowledgebase zu <code>OutOfMemoryError</code> führen, da für den Vergleich Daten auf den Treiber gesammelt werden &ndash; für Unit-Tests sollten daher bewusst kleine, handgeschriebene Beispieldatensätze verwendet werden, wie auch im Kurs gezeigt.<br>
Quelle: <a href="https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.testing.assertDataFrameEqual.html">pyspark.testing.assertDataFrameEqual &ndash; Apache-Spark-Dokumentation</a></div>
"""

render_pdf(os.path.join(BASE, "03 Unit Tests fuer PySpark (pytest, assertDataFrameEqual).pdf"),
    "Unit Tests für PySpark (pytest, assertDataFrameEqual)",
    "Section 5 &middot; Implementing CI-CD &middot; Quelle: Kurs 4, M02 Kapitel 9&ndash;10 + tests/unit_tests/",
    body_3, "07_03_unit_tests")
print("07-3 OK")

# ---------------------------------------------------------------- 07-4
body_4 = f"""
<p>Unit-Tests prüfen einzelne Funktionen isoliert &ndash; sie sagen aber nichts darüber aus, ob eine komplette Pipeline mit ihren echten Ein- und Ausgabedaten korrekt funktioniert. Dafür braucht es <strong>Integrationstests</strong>. Für Lakeflow Declarative Pipelines (SDP) bieten sich zwei komplementäre Ansätze an: Datenqualitäts-Expectations direkt in der Pipeline, und separate Validierungs-Tasks in einem Lakeflow Job.</p>

<h2>1. Integrationstests über SDP-Expectations</h2>
<p>Eine einfache und wirkungsvolle Methode ist, innerhalb der Pipeline selbst eine Materialized View zu definieren, die eine erwartete Kennzahl (z. B. Zeilenanzahl je Umgebung) berechnet und über eine Expectation gegen einen Zielwert prüft. Da sich die erwartete Zeilenanzahl zwischen Entwicklungs- und Staging-Umgebung unterscheidet, wird der Zielwert dynamisch anhand der Pipeline-Konfiguration <code>target</code> ausgewählt:</p>

{code('python', '''from pyspark import pipelines as dp

target = spark.conf.get("target")

# Erwartete Zeilenzahlen je Umgebung (aus dem Kursbeispiel)
target_integration_tests_validation = {
    'development': {'health_bronze': {'total_rows': 7500}, 'health_silver': {'total_rows': 7500}},
    'stage':       {'health_bronze': {'total_rows': 35000}, 'health_silver': {'total_rows': 35000}}
}

if target in ('development', 'stage'):
    total_expected_bronze = target_integration_tests_validation[target]['health_bronze']['total_rows']
    total_expected_silver = target_integration_tests_validation[target]['health_silver']['total_rows']


def test_count_table_total_rows(table_name, total_count, target):
    """Erstellt eine Materialized View, die die Zeilenanzahl einer Tabelle
    gegen den für die aktuelle Umgebung erwarteten Wert prüft."""
    @dp.expect_all_or_fail({"row_count_matches": f"count = {total_count}"})
    @dp.table(name=f"test_{table_name}_row_count")
    def _row_count_check():
        return spark.sql(f"SELECT COUNT(*) AS count FROM {table_name}")''')}

<p>Schlägt die Expectation fehl (z. B. weil nach einer Code-Änderung plötzlich Zeilen verloren gehen), bricht der Pipeline-Lauf ab bzw. wird die Abweichung im Event-Log sichtbar &ndash; je nachdem, welche der drei Expectation-Aktionen (WARN/DROP ROW/FAIL UPDATE) gewählt wurde. In Produktion wird meist bewusst nur ein Teil der Tests ausgeführt (z. B. nur die Gold-Tabellen-Prüfung), um die Laufzeit gering zu halten.</p>

<h2>2. Integrationstests über Lakeflow-Jobs-Tasks</h2>
<p>Alternativ oder ergänzend lässt sich ein mehrstufiger Lakeflow Job aufbauen, dessen Tasks nacheinander ausgeführt werden: zuerst ein Task, der die Unit-Tests via <code>pytest</code> ausführt, danach ein Pipeline-Task für die eigentliche SDP-ETL-Pipeline, und optional ein abschließender Visualisierungs- oder Validierungs-Task. Schlägt ein früherer Task fehl, werden nachfolgende Tasks (dank Task-Abhängigkeiten, siehe Section 4) gar nicht erst gestartet &ndash; fehlerhafter Code gelangt so nicht in die nächste Umgebung.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks empfiehlt, für das Testen von Pipelines gezielt eigene Entwicklungs-/Test-Datasets mit sowohl korrekten als auch bewusst fehlerhaften Datensätzen zu verwenden, um zu prüfen, ob die Pipeline-Logik (inklusive Expectations) Fehlerfälle wie erwartet behandelt. Da jeder Pipeline-Lauf ein strukturiertes Event-Log als Delta-Tabelle schreibt (mit Ausführungsfortschritt, Expectation-Ergebnissen und Datenherkunft), kann dieses Log direkt für automatisierte Integrationstests über dev/stage/prod hinweg abgefragt werden, statt eigene Zähl-Views wie oben von Hand zu pflegen.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ldp/expectations">Manage data quality with pipeline expectations &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(os.path.join(BASE, "04 Integrationstests mit Pipelines und Jobs.pdf"),
    "Integrationstests mit Pipelines und Jobs",
    "Section 5 &middot; Implementing CI-CD &middot; Quelle: Kurs 4, M02 Kapitel 12&ndash;13 + tests/integration_test/",
    body_4, "07_04_integration_tests")
print("07-4 OK")

# ---------------------------------------------------------------- 07-5
body_5 = f"""
<p>Ohne zentrale Versionskontrolle entstehen schnell Entwicklungs-Silos: Mehrere Personen arbeiten an Kopien desselben Notebooks, Änderungen lassen sich nicht mehr nachvollziehen, und es ist unklar, welche Version tatsächlich in Produktion läuft. Git löst dieses Problem durch nachvollziehbare Versionierung, parallele Entwicklung über Branches und einen zentralen Ort (das Remote-Repository, z. B. auf GitHub), auf den sich alle Beteiligten beziehen.</p>

<h2>1. Branching-Strategie: Gitflow</h2>
<p>Eine verbreitete Strategie ist <strong>Gitflow</strong>: Ein stabiler <code>main</code>-Branch spiegelt immer den Produktionsstand wider. Neue Funktionen werden in eigenen <em>Feature-Branches</em> entwickelt, über Pull Requests geprüft und dann in einen Integrations-Branch (oft <code>develop</code>) gemerged; Release- und Hotfix-Branches ermöglichen es, eine Version für die Veröffentlichung vorzubereiten bzw. dringende Produktionsfehler zu beheben, ohne laufende Feature-Entwicklung zu stören.</p>

<h2>2. Databricks Git-Ordner (Git Folders)</h2>
<p>Databricks integriert Git direkt in den Workspace über sogenannte <strong>Git-Ordner</strong> (früher „Repos“): Ein Git-Ordner ist ein Workspace-Verzeichnis, das an ein Remote-Repository gekoppelt ist und Standard-Git-Operationen (Pull, Commit, Push, Branch wechseln) über die Databricks-Oberfläche erlaubt. Typische Arbeitsweise:</p>
<ul>
<li><strong>Admin-Workflow:</strong> Ein Workspace-Administrator legt zentrale Git-Ordner für Produktions-/Test-/Staging-Branches unter einem gemeinsamen Pfad an.</li>
<li><strong>Nutzer-Workflow:</strong> Jede Person klont das Repository in einen eigenen Git-Ordner unter ihrem Benutzerverzeichnis, arbeitet dort auf einem eigenen Branch und pusht Änderungen ins Remote-Repository.</li>
<li><strong>Merge-Workflow:</strong> Nach Review und Merge eines Pull Requests wird der aktualisierte Stand automatisiert (z. B. per CI/CD-Pipeline) in die zentralen Produktions-Git-Ordner übernommen.</li>
</ul>

<h2>3. Authentifizierung mit einem GitHub Personal Access Token (PAT)</h2>
<p>Damit Databricks im Namen einer Person auf ein privates GitHub-Repository zugreifen darf, wird in den Nutzereinstellungen ein <strong>Personal Access Token</strong> (PAT) hinterlegt. Dieses Token wird beim Verknüpfen des Git-Ordners mit dem Repository hinterlegt und ersetzt die klassische Passwort-Authentifizierung.</p>

<h2>4. Automatisierung über die Repos-API</h2>
<p>Für CI/CD-Automatisierung stellt Databricks eine <strong>REST-API für Git-Ordner</strong> bereit: Damit lässt sich z. B. nach einem erfolgreichen Merge eines Pull Requests automatisiert der entsprechende Produktions-Git-Ordner im Workspace auf den neuesten Commit aktualisieren &ndash; ganz ohne manuellen Eingriff einer Person im Workspace.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks beschreibt für CI/CD mit Git-Ordnern konkret drei Abläufe: einen <em>Admin-Flow</em> (zentrale Produktions-/Test-/Staging-Ordner anlegen), einen <em>Nutzer-Flow</em> (persönlicher Git-Ordner unter <code>/Workspace/Users/&lt;email&gt;/</code> mit eigenem Branch) und einen <em>Merge-Flow</em> (nach Merge eines Pull Requests automatisiertes Update der Produktions-Git-Ordner über die Repos-API). Diese Struktur deckt sich mit dem im Kurs vermittelten Modell.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/repos/ci-cd">CI/CD with Databricks Git folders &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(os.path.join(BASE, "05 Versionskontrolle mit Git und Databricks Git-Ordnern.pdf"),
    "Versionskontrolle mit Git & Databricks Git-Ordnern",
    "Section 5 &middot; Implementing CI-CD &middot; Quelle: Kurs 4, M02 Kapitel 14&ndash;15, M03 Kapitel 1",
    body_5, "07_05_git_versionskontrolle")
print("07-5 OK")
