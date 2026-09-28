# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Neben dem Zusammenführen mehrerer Tabellen gehört das gezielte Verändern einer einzelnen Tabelle zum Kernhandwerk jeder PySpark-Transformation: Spalten hinzufügen oder entfernen, umbenennen, aufteilen, Zeilen filtern und verschachtelte Arrays auf einzelne Zeilen &bdquo;auffalten&ldquo;. Der Exam Guide fasst dies unter dem Ziel &bdquo;Manipulate columns, rows, and table structures&ldquo; zusammen. Als Grundlage dient eine kleine, frei erfundene Bestelltabelle:</p>

{code('python', '''bestellungen = spark.createDataFrame([
    (1, "Max Mustermann", "Kaffee,Zucker,Milch", 24.90, "2024-05-01"),
    (2, "Erika Beispiel",  "Tee,Kekse",           11.50, "2024-05-03"),
    (3, "Jan Schmidt",     "Kaffee",               8.90, "2024-05-04"),
], ["order_id", "customer_name", "items_raw", "amount", "order_date"])

bestellungen.createOrReplaceTempView("bestellungen")''')}

<h2>1. Spalten hinzufügen: withColumn()</h2>
<p><code>withColumn(name, expr)</code> fügt einer bestehenden Tabelle eine neue Spalte hinzu oder überschreibt eine vorhandene Spalte gleichen Namens. Das zugrunde liegende DataFrame bleibt dabei unverändert (Spark-DataFrames sind unveränderlich, <em>immutable</em>) &ndash; <code>withColumn</code> gibt stets ein <em>neues</em> DataFrame zurück.</p>
{code('python', '''from pyspark.sql.functions import col, round as spark_round

bestellungen_erw = bestellungen.withColumn(
    "amount_mit_steuer", spark_round(col("amount") * 1.19, 2)
)''')}
{code('sql', '''SELECT *, ROUND(amount * 1.19, 2) AS amount_mit_steuer
FROM bestellungen;''')}
<p>Sollen mehrere Spalten gleichzeitig ergänzt werden, existiert seit Spark&nbsp;3.3 zusätzlich <code>withColumns()</code>, das ein Dictionary aus Spaltenname und Ausdruck entgegennimmt, statt <code>withColumn</code> mehrfach hintereinander aufzurufen.</p>

<h2>2. Spalten entfernen: drop()</h2>
<p><code>drop()</code> entfernt eine oder mehrere Spalten aus dem DataFrame. Da hier keine Bedingung geprüft wird, ist die Methode deutlich unkomplizierter als etwa ein Filter.</p>
{code('python', '''bestellungen_ohne_rohspalte = bestellungen.drop("items_raw")
# mehrere Spalten gleichzeitig entfernen:
bestellungen.drop("items_raw", "order_date")''')}
{code('sql', '''SELECT order_id, customer_name, amount, order_date
FROM bestellungen;
-- Alternativ dauerhaft am Tabellenschema:
ALTER TABLE bestellungen DROP COLUMN items_raw;''')}

<h2>3. Spalten umbenennen: withColumnRenamed()</h2>
{code('python', '''bestellungen_umbenannt = bestellungen.withColumnRenamed("customer_name", "kunde")
# mehrere Umbenennungen verketten:
bestellungen.withColumnRenamed("customer_name", "kunde").withColumnRenamed("amount", "betrag")''')}
{code('sql', '''SELECT customer_name AS kunde, amount AS betrag
FROM bestellungen;
-- Alternativ dauerhaft am Tabellenschema:
ALTER TABLE bestellungen RENAME COLUMN customer_name TO kunde;''')}

<h2>4. Spalten aufteilen: split()</h2>
<p>Die Funktion <code>split(spalte, muster)</code> zerlegt eine String-Spalte anhand eines regulären Ausdrucks in ein <strong>Array</strong> von Teilstrings. Im Beispiel wird zum einen die kommaseparierte Artikel-Spalte <code>items_raw</code> in ein Array überführt, zum anderen der volle Kundenname anhand des Leerzeichens in Vor- und Nachname aufgeteilt.</p>
{code('python', '''from pyspark.sql.functions import split

bestellungen_split = (
    bestellungen
    .withColumn("items", split(col("items_raw"), ","))
    .withColumn("vorname", split(col("customer_name"), " ").getItem(0))
    .withColumn("nachname", split(col("customer_name"), " ").getItem(1))
)''')}
{code('sql', '''SELECT
  order_id,
  split(items_raw, ',')            AS items,
  split(customer_name, ' ')[0]     AS vorname,
  split(customer_name, ' ')[1]     AS nachname
FROM bestellungen;''')}

<h2>5. Zeilen filtern: filter() / where()</h2>
<p><code>filter()</code> und <code>where()</code> sind in PySpark vollständig gleichwertige Aliase &ndash; welche Variante gewählt wird, ist reine Geschmackssache bzw. Lesbarkeitsfrage (viele SQL-Entwickler bevorzugen <code>where()</code>).</p>
{code('python', '''bestellungen.filter(col("amount") > 10)
bestellungen.where(col("amount") > 10)               # identisch zu filter()
bestellungen.filter("amount > 10 AND order_date >= '2024-05-03'")  # als SQL-String-Ausdruck''')}
{code('sql', '''SELECT * FROM bestellungen
WHERE amount > 10 AND order_date >= '2024-05-03';''')}

<h2>6. Arrays auffalten: explode()</h2>
<p><code>explode()</code> wandelt eine Array-Spalte in mehrere Zeilen um: Für jedes Element des Arrays entsteht eine eigene Ausgabezeile, während alle übrigen Spalten unverändert dupliziert werden. Das ist besonders nützlich, um aus der zuvor per <code>split()</code> erzeugten <code>items</code>-Spalte eine Zeile <em>pro Artikel</em> zu machen.</p>
{code('python', '''from pyspark.sql.functions import explode

artikel_zeilen = bestellungen_split.withColumn("item", explode(col("items")))
# Ergebnis: aus 3 Bestellungen mit insgesamt 4 Artikeln (Bestellung 1 hat 3 Artikel,
# Bestellung 2 hat 2, Bestellung 3 hat 1) werden 6 Zeilen, jeweils ein Artikel pro Zeile.''')}
{code('sql', '''SELECT order_id, customer_name, item
FROM bestellungen_split
LATERAL VIEW explode(items) AS item;

-- Alternative moderne Schreibweise ohne LATERAL VIEW:
SELECT order_id, customer_name, explode(items) AS item
FROM bestellungen_split;''')}
<p>Enthält die Array-Spalte in manchen Zeilen <code>NULL</code> oder ein leeres Array, gehen diese Zeilen bei <code>explode()</code> vollständig verloren, da es kein Element zum Auffalten gibt. Soll die Ursprungszeile in diesem Fall dennoch (mit <code>NULL</code> in der neuen Spalte) erhalten bleiben, hilft die Variante <code>explode_outer()</code> mit identischer Syntax.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen PySpark-Dokumentation:</strong> <code>pyspark.sql.functions.explode()</code> gibt laut Referenz &bdquo;a new row for each element in the given array or map&ldquo; zurück; für leere oder <code>NULL</code>-wertige Arrays/Maps wird standardmäßig keine Zeile erzeugt &ndash; hierfür ist explizit <code>explode_outer()</code> vorgesehen. Seit Spark&nbsp;3.3 ergänzt <code>DataFrame.withColumns()</code> die Einzelspalten-Methode <code>withColumn()</code> um die Möglichkeit, mehrere neue oder ersetzte Spalten in einem Aufruf über ein Dictionary zu definieren.<br>
Quelle: <a href="https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.explode.html">pyspark.sql.functions.explode &ndash; Apache Spark Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\12 Spalten, Zeilen und Tabellenstrukturen bearbeiten.pdf",
    title="Spalten, Zeilen und Tabellenstrukturen bearbeiten",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: PySpark-/Databricks-Referenzdokumentation",
    body_html=body,
    build_name="03_12_spalten_zeilen_bearbeiten",
)
print("OK")
