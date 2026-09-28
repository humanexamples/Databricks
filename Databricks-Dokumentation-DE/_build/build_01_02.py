# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Beim Laden von Rohdaten in eine Bronze-Tabelle reicht es selten, nur die fachlichen Spalten der Quelle zu übernehmen. Zwei Ergänzungen haben sich in der Praxis als Standard etabliert: <strong>Metadaten-Spalten</strong>, die dokumentieren, woher und wann eine Zeile stammt, und die <strong>Rescued-Data-Spalte</strong>, die verhindert, dass unerwartete oder fehlerhafte Werte beim Laden stillschweigend verloren gehen. Beide Mechanismen lassen sich mit denselben Ingestion-Werkzeugen nutzen, die bereits aus der CTAS-/<code>read_files()</code>-Ingestion bekannt sind.</p>

<h2>1. Metadaten-Spalten beim Ingest ergänzen</h2>
<p>Jede Datei, die über <code>read_files()</code>, <code>spark.read</code> oder Auto Loader eingelesen wird, besitzt eine versteckte Spalte namens <code>_metadata</code>. Sie steht für alle unterstützten Dateiformate zur Verfügung, muss aber explizit in der Leseabfrage ausgewählt werden. Die wichtigsten Felder sind <code>_metadata.file_name</code> (Name der Quelldatei) und <code>_metadata.file_modification_time</code> (letzter Änderungszeitpunkt der Datei). Ergänzt um <code>current_timestamp()</code> für den Ingestion-Zeitpunkt selbst, lässt sich damit für jede Zeile lückenlos nachvollziehen, aus welcher Datei sie stammt und wann sie geladen wurde &ndash; wichtig für Auditing, Data Lineage und die Fehlersuche, wenn sich später herausstellt, dass eine bestimmte Quelldatei fehlerhafte Daten enthielt.</p>

<figure class="img">
<img src="assets/01/common-file-metadata-fields.png">
<figcaption>Die beiden am häufigsten genutzten Felder der versteckten <code>_metadata</code>-Spalte: Dateiname und letzter Änderungszeitpunkt.</figcaption>
</figure>

<p>In der Praxis werden diese Felder direkt in die CTAS-Abfrage eingebaut, mit der die Bronze-Tabelle erzeugt wird. Das folgende Beispiel liest historische Nutzerdaten aus Parquet-Dateien, wandelt einen Unix-Zeitstempel in ein lesbares Datum um und ergänzt drei Metadaten-Spalten:</p>

{code('sql', '''DROP TABLE IF EXISTS historical_users_bronze;

CREATE TABLE historical_users_bronze AS
SELECT
  *,
  cast(from_unixtime(user_first_touch_timestamp / 1000000) AS DATE) AS first_touch_date,
  _metadata.file_modification_time AS file_modification_time,   -- letzte Änderung der Quelldatei
  _metadata.file_name              AS source_file,               -- Name der Quelldatei
  current_timestamp()              AS ingestion_time              -- Zeitpunkt des Ladevorgangs
FROM read_files(
  "/Volumes/dbacademy_ecommerce/v01/raw/users-historical",
  format => "parquet"
);

-- Beispiel-Auswertung: Zeilenanzahl je Quelldatei
SELECT source_file, count(*) AS total
FROM historical_users_bronze
GROUP BY source_file
ORDER BY source_file;''')}

<p>Dieselbe Logik lässt sich äquivalent in PySpark formulieren, etwa wenn die Ingestion Teil eines größeren Python-Skripts ist:</p>

{code('python', '''from pyspark.sql.functions import col, from_unixtime, current_timestamp
from pyspark.sql.types import DateType

df = spark.read.format("parquet").load("/Volumes/dbacademy_ecommerce/v01/raw/users-historical")

df_with_metadata = (
    df.withColumn("first_touch_date", from_unixtime(col("user_first_touch_timestamp") / 1_000_000).cast(DateType()))
      .withColumn("file_modification_time", col("_metadata.file_modification_time"))
      .withColumn("source_file", col("_metadata.file_name"))
      .withColumn("ingestion_time", current_timestamp())
)

df_with_metadata.write.format("delta").mode("overwrite").saveAsTable("historical_users_bronze_python_metadata")''')}

<h2>2. Die Rescued-Data-Spalte: Schema-Abweichungen abfangen statt verlieren</h2>
<p>Nicht jede Zeile einer Quelldatei passt exakt zum erwarteten Schema der Zieltabelle. Ohne Gegenmaßnahme würde ein Wert, der nicht in den erwarteten Datentyp konvertiert werden kann, beim Laden entweder den ganzen Job abbrechen lassen oder &ndash; schlimmer &ndash; stillschweigend als <code>NULL</code> verschwinden. Genau hier setzt die <strong>Rescued-Data-Spalte</strong> (<code>_rescued_data</code>) an: <code>read_files()</code>, <code>spark.read</code> und Auto Loader legen sie automatisch an, sobald Werte nicht zum Schema passen, und speichern die nicht einlesbaren Originalwerte als JSON-formatierten String &ndash; inklusive Dateipfad der Quelle. Passt eine Zeile vollständig zum Schema, bleibt <code>_rescued_data</code> für diese Zeile <code>NULL</code>.</p>

<figure class="img">
<img src="assets/01/rescued-data-example.png">
<figcaption>Der Wert &bdquo;$100&ldquo; kann nicht als BIGINT gelesen werden und landet deshalb als JSON-String in der Spalte <code>_rescued_data</code>, statt die Zeile zu verwerfen.</figcaption>
</figure>

<p>Typische Auslöser für gerettete Werte sind fehlende Spalten im Schema, Typ-Konflikte (z. B. Text statt Zahl) oder Groß-/Kleinschreibungs-Konflikte bei Spaltennamen. Besonders häufig tritt das bei CSV-Dateien auf, weil CSV im Gegensatz zu Parquet kein eingebettetes Schema mitbringt. Im folgenden Beispiel enthält eine CSV-Zeile den Wert <code>aaa</code> in einer eigentlich numerischen Spalte; mit einem explizit definierten Schema und aktivierter Rescued-Data-Spalte wird die fehlerhafte Zeile nicht verworfen, sondern gezielt sichtbar gemacht:</p>

{code('sql', '''SELECT *
FROM read_files(
  '/Volumes/dbacademy/ops/labuser/csv_demo_files/malformed_example_1_data.csv',
  format => "csv",
  sep => "|",
  header => true,
  schema => \'\'\'
      order_id INT,
      email STRING,
      transactions_timestamp BIGINT\'\'\',
  rescuedDataColumn => "_rescued_data"
);''')}

<p>Fehlt in einer CSV-Datei sogar der Spaltenname selbst (z. B. durch einen fehlerhaften Header), wird die betroffene Spalte unter dem generischen Schlüssel <code>_c0</code> im JSON der Rescued-Data-Spalte abgelegt. Mit der <code>:</code>-Pfadsyntax lässt sich der Wert anschließend gezielt extrahieren und in eine reguläre Spalte überführen:</p>

{code('sql', '''SELECT
  cast(_rescued_data:_c0 AS BIGINT) AS order_id,
  *
FROM read_files(
  '/Volumes/dbacademy/ops/labuser/csv_demo_files/malformed_example_2_data.csv',
  format => "csv",
  sep => "|",
  header => true
);''')}

<p>Im PySpark-Äquivalent wird die Rescued-Data-Spalte über die Option <code>rescuedDataColumn</code> aktiviert:</p>

{code('python', '''df = (spark.read
      .option("header", True)
      .option("sep", "|")
      .option("rescuedDataColumn", "_rescued_data")
      .csv("/Volumes/dbacademy_ecommerce/v01/raw/sales-csv"))''')}

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Die Rescued-Data-Spalte ist eng mit dem Konzept der <strong>Schema Evolution</strong> verzahnt, insbesondere bei Auto Loader: Wird der Schema-Evolution-Modus auf <code>rescue</code> gesetzt, werden nicht nur fehlende oder falsch typisierte Spalten, sondern auch erkannte Typänderungen zunächst in <code>_rescued_data</code> abgelegt, statt das Zielschema sofort automatisch zu erweitern. In den Modi <code>DROPMALFORMED</code> bzw. <code>FAILFAST</code> führen Typkonflikte durch die aktivierte Rescued-Data-Spalte nicht mehr zum Verwerfen der Zeile bzw. zum Abbruch des Jobs &ndash; nur noch tatsächlich korrupte, nicht parsebare Datensätze (z. B. unvollständiges JSON) lösen weiterhin einen Fehler aus.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema">Configure schema inference and evolution in Auto Loader &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 2 - Data Ingestion and Loading\02 Metadaten-Spalten und Rescued-Data-Spalte.pdf",
    title="Metadaten-Spalten & die Rescued-Data-Spalte",
    subtitle="Section 2 &middot; Data Ingestion and Loading &middot; Quelle: Kurs 1, Kapitel 6&ndash;9",
    body_html=body,
    build_name="01_02_metadaten",
)
print("OK")
