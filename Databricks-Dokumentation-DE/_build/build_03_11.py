# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Kaum eine Transformation ist im Data-Engineering-Alltag so häufig wie das Zusammenführen zweier Tabellen. Der Exam Guide verlangt konkret die Beherrschung von Inner Join, Left Join, Broadcast Join, Joins über mehrere Schlüssel, Cross Join sowie <code>union</code>/<code>union all</code>. Dieses Kapitel zeigt alle genannten Varianten anhand von zwei einfachen Beispieltabellen &ndash; <code>customers</code> (Kunden) und <code>orders</code> (Bestellungen) &ndash; jeweils in PySpark- und SQL-Syntax.</p>

<p>Als Ausgangsdaten dienen zwei kleine, frei erfundene DataFrames:</p>
{code('python', '''customers = spark.createDataFrame([
    (1, "Anna",   "Berlin"),
    (2, "Ben",    "München"),
    (3, "Clara",  "Hamburg"),
], ["customer_id", "name", "city"])

orders = spark.createDataFrame([
    (100, 1, 49.90),
    (101, 1, 12.50),
    (102, 2, 99.00),
    (103, 4, 20.00),   # customer_id 4 existiert nicht in customers
], ["order_id", "customer_id", "amount"])

customers.createOrReplaceTempView("customers")
orders.createOrReplaceTempView("orders")''')}

<h2>1. Inner Join</h2>
<p>Der <strong>Inner Join</strong> ist der Standardfall: Er liefert ausschließlich Zeilen, für die in <em>beiden</em> DataFrames ein passender Schlüssel existiert. Kunde &bdquo;Clara&ldquo; (ohne Bestellung) und Bestellung 103 (mit unbekanntem <code>customer_id</code> 4) fallen dabei aus dem Ergebnis heraus.</p>
{code('python', '''result = customers.join(orders, on="customer_id", how="inner")
# gleichwertig: how="inner" ist der Standardwert und kann weggelassen werden
result = customers.join(orders, on="customer_id")''')}
{code('sql', '''SELECT c.customer_id, c.name, o.order_id, o.amount
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id;''')}

<h2>2. Left Join (Left Outer Join)</h2>
<p>Ein <strong>Left Join</strong> (auch <code>left_outer</code>) behält alle Zeilen der linken Tabelle bei &ndash; unabhängig davon, ob ein passender Partner in der rechten Tabelle existiert. Fehlt ein Treffer, werden die Spalten der rechten Tabelle mit <code>NULL</code> aufgefüllt. Im Beispiel bleibt Clara im Ergebnis erhalten, ihre Bestellspalten sind jedoch <code>NULL</code>.</p>
{code('python', '''result = customers.join(orders, on="customer_id", how="left")
# alternative Schreibweisen, alle gleichwertig:
customers.join(orders, on="customer_id", how="left_outer")''')}
{code('sql', '''SELECT c.customer_id, c.name, o.order_id, o.amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;''')}
<p>Analog existieren <code>how="right"</code> (Right Outer Join, behält alle Zeilen der rechten Tabelle) und <code>how="outer"</code> bzw. <code>"full"</code> (Full Outer Join, behält Zeilen aus beiden Tabellen und füllt jeweils fehlende Seite mit <code>NULL</code> auf).</p>

<h2>3. Broadcast Join</h2>
<p>Ein <strong>Broadcast Join</strong> ist keine eigene <code>how</code>-Option, sondern ein <em>Optimierungshinweis</em>: Ist eine der beiden Tabellen klein genug, um komplett in den Arbeitsspeicher jedes Executors zu passen (typischerweise eine kleine Dimensionstabelle wie <code>customers</code>), kann sie vollständig an alle Executor verteilt werden. Das erspart den teuren Shuffle der großen Tabelle über das Netzwerk. Spark entscheidet automatisch anhand des Parameters <code>spark.sql.autoBroadcastJoinThreshold</code> (siehe Kapitel 14 dieser Section), ob gebroadcastet wird &ndash; mit dem expliziten Hint <code>broadcast()</code> lässt sich dieses Verhalten aber auch gezielt erzwingen.</p>
{code('python', '''from pyspark.sql.functions import broadcast

result = orders.join(broadcast(customers), on="customer_id", how="inner")''')}
{code('sql', '''SELECT /*+ BROADCAST(c) */ o.order_id, o.amount, c.name
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id;''')}
<p>Der Broadcast-Hint eignet sich vor allem dann, wenn Spark die tatsächliche Größe einer Tabelle nicht korrekt einschätzen kann (z.&nbsp;B. nach mehreren Transformationsschritten) und deshalb von sich aus keinen Broadcast Join wählen würde, obwohl die Tabelle klein genug wäre.</p>

<h2>4. Joins über mehrere Schlüssel</h2>
<p>Sollen zwei Tabellen über <em>mehrere</em> Spalten gleichzeitig verglichen werden (z.&nbsp;B. weil ein einzelner Schlüssel nicht eindeutig ist), gibt es in PySpark zwei gängige Varianten: eine Liste gemeinsamer Spaltennamen oder eine zusammengesetzte Bedingung mit <code>&amp;</code>.</p>
{code('python', '''# Variante A: Liste gemeinsamer Spaltennamen (identisch benannt in beiden DataFrames)
result = df1.join(df2, on=["customer_id", "order_year"], how="inner")

# Variante B: zusammengesetzte Bedingung, auch bei unterschiedlichen Spaltennamen möglich
result = df1.join(
    df2,
    on=(df1.customer_id == df2.cust_id) & (df1.order_year == df2.year),
    how="inner",
)''')}
{code('sql', '''SELECT *
FROM df1
INNER JOIN df2
  ON df1.customer_id = df2.cust_id
 AND df1.order_year = df2.year;''')}
<p>Wichtig bei Variante&nbsp;B: Da die Join-Bedingung hier über einen Spaltenausdruck statt über <code>on="..."</code> mit gemeinsamem Namen erfolgt, tauchen beide Schlüsselspalten (<code>customer_id</code> <em>und</em> <code>cust_id</code>) im Ergebnis auf &ndash; im Gegensatz zu Variante&nbsp;A, bei der die gemeinsame Spalte nur einmal erscheint.</p>

<h2>5. Cross Join</h2>
<p>Ein <strong>Cross Join</strong> (kartesisches Produkt) verknüpft jede Zeile der linken Tabelle mit jeder Zeile der rechten Tabelle &ndash; ganz ohne Join-Bedingung. Die Ergebnisgröße entspricht dem Produkt beider Zeilenzahlen und kann dadurch sehr schnell sehr groß werden. Typischer Anwendungsfall sind Kombinationstabellen, etwa alle möglichen Kombinationen aus Produktfarben und -größen.</p>
{code('python', '''colors = spark.createDataFrame([("rot",), ("blau",)], ["farbe"])
sizes  = spark.createDataFrame([("S",), ("M",), ("L",)], ["groesse"])

kombinationen = colors.crossJoin(sizes)   # Ergebnis: 2 x 3 = 6 Zeilen''')}
{code('sql', '''SELECT farbe, groesse
FROM colors
CROSS JOIN sizes;''')}
<p>Cross Joins sollten mit Bedacht eingesetzt werden: Bei zwei Tabellen mit jeweils einer Million Zeilen entstünde ein Ergebnis mit einer Billion Zeilen. Spark verweigert einen impliziten Cross Join standardmäßig sogar (Fehlermeldung <code>CROSS_JOIN_UNSUPPORTED</code>), wenn <code>join()</code> ohne Bedingung aufgerufen wird &ndash; die explizite Methode <code>crossJoin()</code> bzw. die SQL-Klausel <code>CROSS JOIN</code> muss bewusst gewählt werden.</p>

<h2>6. Union, Union All und UnionByName</h2>
<p>Während Joins Tabellen <em>nebeneinander</em> (spaltenweise) zusammenführen, hängen <code>union</code>-Operationen zwei DataFrames <em>untereinander</em> (zeilenweise) an &ndash; Voraussetzung ist dieselbe Anzahl an Spalten mit kompatiblen Datentypen.</p>
{code('python', '''orders_de = spark.createDataFrame([(200, 1, 30.0)], ["order_id", "customer_id", "amount"])
orders_at = spark.createDataFrame([(300, 2, 45.0)], ["order_id", "customer_id", "amount"])

# union() und unionAll() sind in PySpark identisch (kein automatisches DISTINCT!)
alle_bestellungen = orders_de.union(orders_at)
alle_bestellungen = orders_de.unionAll(orders_at)   # Alias, gleiches Verhalten

# unionByName(): matcht Spalten anhand ihres Namens statt ihrer Position
orders_ch = spark.createDataFrame([(2, 400, 60.0)], ["customer_id", "order_id", "amount"])
alle_bestellungen = orders_de.unionByName(orders_ch)

# unionByName mit allowMissingColumns=True erlaubt sogar unterschiedliche Spaltenmengen
# fehlende Spalten werden in den betroffenen Zeilen automatisch mit NULL aufgefüllt
orders_uk = spark.createDataFrame([(500, 3, 15.0, "GBP")], ["order_id", "customer_id", "amount", "currency"])
alle_bestellungen = orders_de.unionByName(orders_uk, allowMissingColumns=True)''')}
{code('sql', '''SELECT * FROM orders_de
UNION ALL
SELECT * FROM orders_at;

-- SQL UNION (ohne ALL) entfernt zusätzlich Duplikate, entspricht also union().distinct()
SELECT * FROM orders_de
UNION
SELECT * FROM orders_at;''')}
<p><strong>Wichtiger Unterschied zwischen PySpark und SQL:</strong> In der DataFrame-API sind <code>union()</code> und <code>unionAll()</code> identisch und entfernen <em>keine</em> Duplikate. In reinem SQL hingegen entfernt <code>UNION</code> (ohne <code>ALL</code>) Duplikate, während <code>UNION ALL</code> alle Zeilen unverändert übernimmt &ndash; hier lohnt sich also besondere Aufmerksamkeit, da der Name <code>union()</code> in PySpark auf den ersten Blick das SQL-<code>UNION</code>-Verhalten vermuten lässt, tatsächlich aber <code>UNION ALL</code> entspricht. Ein anschließendes <code>.distinct()</code> stellt bei Bedarf das SQL-<code>UNION</code>-Verhalten in PySpark her. <code>union()</code> und <code>unionAll()</code> matchen Spalten zudem rein <strong>positionsbasiert</strong> &ndash; unterscheidet sich die Spaltenreihenfolge zwischen beiden DataFrames, landen Werte unbemerkt in der falschen Spalte. <code>unionByName()</code> vermeidet dieses Risiko, indem es Spalten anhand ihres Namens zuordnet.</p>

<h2>7. Welcher Join-Typ wann?</h2>
<table>
<tr><th>Join-Typ</th><th>Wann sinnvoll</th></tr>
<tr><td>Inner Join</td><td>Nur eindeutig zuordenbare Datensätze aus beiden Tabellen werden benötigt (Standardfall).</td></tr>
<tr><td>Left Join</td><td>Alle Datensätze der &bdquo;Haupttabelle&ldquo; sollen erhalten bleiben, auch ohne Treffer in der Zweittabelle (z.&nbsp;B. alle Kunden, auch ohne Bestellung).</td></tr>
<tr><td>Broadcast Join</td><td>Eine der beiden Tabellen ist klein genug für den Arbeitsspeicher jedes Executors (Dimensionstabelle) &ndash; spart teuren Shuffle.</td></tr>
<tr><td>Mehrfachschlüssel-Join</td><td>Ein einzelner Schlüssel reicht zur eindeutigen Zuordnung nicht aus (z.&nbsp;B. Kombination aus ID und Jahr).</td></tr>
<tr><td>Cross Join</td><td>Bewusst alle Kombinationen zweier (meist kleiner) Mengen erzeugt werden sollen.</td></tr>
<tr><td>Union / Union All</td><td>Zeilen mehrerer strukturgleicher Tabellen sollen untereinandergehängt werden, z.&nbsp;B. regionale Teiltabellen zu einer Gesamttabelle.</td></tr>
</table>

<div class="docbox">
<strong>Ergänzt aus der offiziellen PySpark-Dokumentation:</strong> <code>DataFrame.crossJoin()</code> erzeugt explizit das kartesische Produkt zweier DataFrames ohne Join-Bedingung. <code>functions.broadcast()</code> markiert einen DataFrame als klein genug, um an alle Worker-Knoten verteilt zu werden, und ist damit der explizite Gegenpart zum automatischen Broadcast-Verhalten über <code>spark.sql.autoBroadcastJoinThreshold</code>. <code>DataFrame.unionByName()</code> unterstützt seit Spark&nbsp;3.1 zusätzlich den Parameter <code>allowMissingColumns</code>, der fehlende Spalten in einem der beiden DataFrames automatisch mit <code>NULL</code> auffüllt, statt einen Fehler zu werfen.<br>
Quelle: <a href="https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.crossJoin.html">pyspark.sql.DataFrame.crossJoin &ndash; Apache Spark Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\11 DataFrame-Joins - Inner, Left, Broadcast, Cross und Union.pdf",
    title="DataFrame-Joins: Inner, Left, Broadcast, Cross und Union",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: PySpark-/Databricks-Referenzdokumentation",
    body_html=body,
    build_name="03_11_dataframe_joins",
)
print("OK")
