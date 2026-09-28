# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Rohdaten enthalten in der Praxis fast immer Duplikate &ndash; sei es durch doppelte Quellsystem-Exporte, wiederholte Streaming-Ereignisse oder fehlerhafte Uploads. Der Exam Guide verlangt sowohl die Beherrschung von Deduplizierungs-Operationen als auch der klassischen Aggregationsfunktionen (<code>count</code>, <code>approx_count_distinct</code>, Mittelwert, <code>summary</code>). Als Beispieldaten dient eine kleine Kundentabelle mit absichtlich eingebauten Duplikaten:</p>

{code('python', '''kunden = spark.createDataFrame([
    (1, "Anna",  "Berlin",  "anna@mail.de"),
    (2, "Ben",   "München", "ben@mail.de"),
    (2, "Ben",   "München", "ben@mail.de"),   # exaktes Duplikat von Zeile 2
    (3, "Clara", "Hamburg", "clara@mail.de"),
    (3, "Clara", "Hamburg", "clara2@mail.de"), # gleiche ID, andere E-Mail
], ["customer_id", "name", "city", "email"])

kunden.createOrReplaceTempView("kunden")''')}

<h2>1. Deduplizierung: distinct() und dropDuplicates()</h2>
<p><code>distinct()</code> entfernt Zeilen, die in <em>allen</em> Spalten exakt übereinstimmen. Im Beispiel wird dadurch nur die exakte Kopie von Ben (Zeile 3) entfernt &ndash; die beiden Clara-Zeilen unterscheiden sich in der E-Mail-Adresse und bleiben daher beide erhalten.</p>
{code('python', '''kunden_distinct = kunden.distinct()   # 4 statt 5 Zeilen''')}
{code('sql', '''SELECT DISTINCT * FROM kunden;''')}

<p><code>dropDuplicates()</code> (ohne Argumente identisch zu <code>distinct()</code>) erlaubt zusätzlich, Duplikate nur anhand einer <em>Teilmenge</em> von Spalten zu bestimmen. Im Beispiel werden nun beide Clara-Zeilen als Duplikate behandelt, da nur <code>customer_id</code> verglichen wird &ndash; welche der beiden Varianten (mit welcher E-Mail-Adresse) behalten wird, ist dabei nicht deterministisch garantiert.</p>
{code('python', '''kunden_ohne_duplikate = kunden.dropDuplicates(["customer_id"])   # 3 Zeilen: 1, 2, 3
kunden_exakt = kunden.dropDuplicates()  # ohne Spaltenliste: identisch zu distinct()''')}
{code('sql', '''SELECT customer_id, FIRST(name) AS name, FIRST(city) AS city, FIRST(email) AS email
FROM kunden
GROUP BY customer_id;
-- SQL kennt keine direkte Entsprechung zu dropDuplicates(subset); GROUP BY mit
-- Aggregatfunktionen wie FIRST()/MAX() bildet das Verhalten nach.''')}

<h2>2. Zählen: count() und approx_count_distinct()</h2>
<p><code>count()</code> als Aktion auf einem DataFrame liefert die exakte Zeilenzahl; als Aggregatfunktion innerhalb von <code>agg()</code> oder <code>groupBy().agg()</code> zählt sie Werte pro Gruppe. Für die Anzahl <em>unterschiedlicher</em> Werte einer Spalte gibt es zwei Optionen: das exakte, aber bei großen Datenmengen teure <code>countDistinct()</code> sowie das deutlich günstigere, approximative <code>approx_count_distinct()</code> (basierend auf dem HyperLogLog++-Algorithmus).</p>
{code('python', '''from pyspark.sql.functions import count, countDistinct, approx_count_distinct

kunden.count()                                              # exakte Gesamtzeilenzahl (5)
kunden.select(countDistinct("customer_id")).show()           # exakt: 3
kunden.select(approx_count_distinct("customer_id")).show()   # approximativ, mit Standardfehler 5%

# Standardfehler (rsd) explizit einstellen, z.B. für höhere Genauigkeit auf Kosten der Performance:
kunden.select(approx_count_distinct("customer_id", 0.01)).show()''')}
{code('sql', '''SELECT
  COUNT(*)                          AS anzahl_zeilen,
  COUNT(DISTINCT customer_id)       AS exakte_anzahl_kunden,
  APPROX_COUNT_DISTINCT(customer_id) AS approx_anzahl_kunden
FROM kunden;''')}
<p><code>approx_count_distinct()</code> lohnt sich vor allem bei sehr großen Tabellen mit Millionen unterschiedlicher Werte (z.&nbsp;B. eindeutige Besucher-IDs auf einer Webseite): Der exakte <code>COUNT(DISTINCT ...)</code> erzwingt einen vollständigen Shuffle aller Werte, während die approximative Variante mit konstantem, deutlich geringerem Speicherbedarf auskommt &ndash; auf Kosten einer kleinen, konfigurierbaren Fehlertoleranz.</p>

<h2>3. Aggregationen: Mittelwert, groupBy().agg() und Summary</h2>
<p>Für Kennzahlen pro Gruppe wird typischerweise <code>groupBy()</code> mit anschließendem <code>agg()</code> kombiniert. Die Funktionen <code>avg()</code> und <code>mean()</code> sind dabei reine Aliase und vollständig austauschbar. Als zweites Beispiel dient eine kleine Bestelltabelle:</p>
{code('python', '''bestellungen = spark.createDataFrame([
    (1, "Anna",  49.90),
    (2, "Anna",  12.50),
    (3, "Ben",   99.00),
    (4, "Clara", 20.00),
    (5, "Clara", 35.00),
], ["order_id", "customer_name", "amount"])
bestellungen.createOrReplaceTempView("bestellungen")''')}
{code('python', '''from pyspark.sql.functions import avg, mean, min as spark_min, max as spark_max

kunden.groupBy("city").agg(
    count("*").alias("anzahl_kunden"),
    approx_count_distinct("customer_id").alias("anzahl_eindeutig"),
).show()

bestellungen.groupBy("customer_name").agg(
    avg("amount").alias("durchschnittsbetrag"),   # avg() und mean() sind identisch
    spark_min("amount").alias("min_betrag"),
    spark_max("amount").alias("max_betrag"),
).show()''')}
{code('sql', '''SELECT city, COUNT(*) AS anzahl_kunden, APPROX_COUNT_DISTINCT(customer_id) AS anzahl_eindeutig
FROM kunden
GROUP BY city;

SELECT customer_name, AVG(amount) AS durchschnittsbetrag, MIN(amount) AS min_betrag, MAX(amount) AS max_betrag
FROM bestellungen
GROUP BY customer_name;''')}

<p>Für eine schnelle, explorative Übersicht über eine gesamte Tabelle eignen sich <code>describe()</code> und das umfangreichere <code>summary()</code>. <code>describe()</code> liefert je numerischer/String-Spalte <code>count</code>, <code>mean</code>, <code>stddev</code>, <code>min</code> und <code>max</code>. <code>summary()</code> erweitert dies standardmäßig um Perzentile (25&nbsp;%, 50&nbsp;%/Median, 75&nbsp;%) und lässt sich über ein optionales Argument auf genau die gewünschten Statistiken einschränken.</p>
{code('python', '''kunden.describe().show()
bestellungen.summary().show()
# nur bestimmte Statistiken berechnen (spart Rechenzeit auf großen Tabellen):
bestellungen.summary("count", "min", "25%", "75%", "max").show()''')}

<div class="docbox">
<strong>Ergänzt aus der offiziellen PySpark-Dokumentation:</strong> <code>approx_count_distinct(col, rsd=0.05)</code> berechnet die approximative Anzahl unterschiedlicher Elemente einer Spalte über den HyperLogLog++-Algorithmus; der Parameter <code>rsd</code> steuert dabei den relativen Standardfehler &ndash; laut Dokumentation gilt: Ist <code>rsd &lt; 0.01</code>, ist es effizienter, stattdessen <code>count_distinct()</code> (exakt) zu verwenden, da der Aufwand für sehr geringe Fehlertoleranzen den Vorteil der Approximation aufhebt. <code>dropDuplicates()</code> ohne Spaltenliste verhält sich laut Referenz identisch zu <code>distinct()</code>; mit Spaltenliste werden nur die angegebenen Spalten zur Duplikaterkennung herangezogen, wobei welche der doppelten Zeilen behalten wird, nicht deterministisch festgelegt ist.<br>
Quelle: <a href="https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.approx_count_distinct.html">pyspark.sql.functions.approx_count_distinct &ndash; Apache Spark Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\13 Deduplizierung und Aggregationen.pdf",
    title="Deduplizierung und Aggregationen",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: PySpark-/Databricks-Referenzdokumentation",
    body_html=body,
    build_name="03_13_dedup_aggregationen",
)
print("OK")
