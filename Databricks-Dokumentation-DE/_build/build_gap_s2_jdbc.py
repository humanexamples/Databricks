# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>Nicht jede Datenquelle lässt sich über einen Lakeflow-Connect-Connector oder Auto Loader anbinden. Für klassische relationale Datenbanken (SQL Server, PostgreSQL, MySQL, Oracle, &hellip;) sowie für Systeme, die nur eine REST-API anbieten, ist es üblich, direkt aus einem Notebook heraus per <strong>JDBC/ODBC</strong> bzw. per HTTP-Client Daten zu laden und anschließend in Cloud-Speicher oder direkt in eine Unity-Catalog-verwaltete Tabelle zu schreiben.</p>

<h2>1. Datenbanken per JDBC anbinden</h2>
<p>Spark bringt einen generischen JDBC-Datenquellen-Connector mit. Damit lässt sich eine komplette Tabelle oder das Ergebnis einer beliebigen SQL-Abfrage direkt als DataFrame laden:</p>
{code('python', '''jdbc_url = "jdbc:postgresql://my-db-host:5432/salesdb"

df = (spark.read
      .format("jdbc")
      .option("url", jdbc_url)
      .option("dbtable", "public.orders")
      .option("user", dbutils.secrets.get(scope="db", key="user"))
      .option("password", dbutils.secrets.get(scope="db", key="password"))
      .option("driver", "org.postgresql.Driver")
      .load())

df.write.mode("overwrite").saveAsTable("main.bronze.orders_raw")''')}
<p>Wichtig für produktive Ingestion großer Tabellen: Ohne weitere Optionen liest Spark die gesamte Tabelle über eine einzige Verbindung/Partition &ndash; das skaliert schlecht. Mit <code>partitionColumn</code>, <code>lowerBound</code>, <code>upperBound</code> und <code>numPartitions</code> lässt sich der Lesevorgang auf mehrere parallele JDBC-Verbindungen aufteilen:</p>
{code('python', '''df = (spark.read
      .format("jdbc")
      .option("url", jdbc_url)
      .option("dbtable", "public.orders")
      .option("partitionColumn", "order_id")
      .option("lowerBound", "1")
      .option("upperBound", "1000000")
      .option("numPartitions", "8")
      .load())''')}
<p>Credentials sollten dabei &ndash; wie im Beispiel &ndash; nie im Klartext im Notebook stehen, sondern über <strong>Databricks Secrets</strong> (<code>dbutils.secrets.get(...)</code>) referenziert werden.</p>

<h2>2. ODBC: dieselbe Aufgabe aus der anderen Richtung</h2>
<p>Während JDBC in diesem Szenario verwendet wird, um <em>aus</em> Databricks heraus eine externe Datenbank anzuzapfen, wird der von Databricks bereitgestellte <strong>ODBC-Treiber</strong> meist in die andere Richtung genutzt: Externe BI-Tools (Power BI, Tableau) verbinden sich per ODBC/JDBC <em>zu</em> Databricks, um auf Unity-Catalog-Tabellen zuzugreifen. Für die Prüfung reicht das Verständnis, dass beide Treiber dem gleichen Zweck dienen &ndash; standardisierter Datenbankzugriff &ndash; nur aus jeweils entgegengesetzter Blickrichtung.</p>

<h2>3. REST-APIs aus dem Notebook heraus abfragen</h2>
<p>Für Systeme ohne JDBC-Schnittstelle (z. B. SaaS-Anwendungen mit REST-API) wird die Anfrage typischerweise mit Pythons Standard-HTTP-Bibliotheken direkt im Notebook ausgeführt und das JSON-Ergebnis anschließend in ein Spark-DataFrame überführt:</p>
{code('python', '''import requests

response = requests.get(
    "https://api.example.com/v1/customers",
    headers={"Authorization": f"Bearer {dbutils.secrets.get('api', 'token')}"}
)
response.raise_for_status()
records = response.json()["data"]

# In ein Spark-DataFrame überführen und als Delta-Tabelle schreiben
df = spark.createDataFrame(records)
df.write.mode("append").saveAsTable("main.bronze.customers_api_raw")''')}
<p>Solche REST-Ingestion-Notebooks werden in der Praxis so gut wie nie manuell gestartet, sondern als <strong>Notebook-Task innerhalb eines Lakeflow Jobs</strong> geplant &ndash; z. B. stündlich per Cron-Schedule, damit neue Datensätze regelmäßig automatisiert nachgeladen werden (siehe Section 4 zu Lakeflow Jobs).</p>

<h2>4. Einordnung gegenüber anderen Ingestion-Methoden</h2>
<table>
<tr><th>Methode</th><th>Typischer Anwendungsfall</th></tr>
<tr><td>Lakeflow Connect (Managed Connector)</td><td>Verbreitete Enterprise-/SaaS-Quellen mit vorgefertigtem, wartungsarmem Connector</td></tr>
<tr><td>Auto Loader</td><td>Dateibasierte Quellen in Cloud-Speicher, kontinuierlich wachsend</td></tr>
<tr><td>JDBC/ODBC im Notebook</td><td>Klassische relationale Datenbanken ohne Managed Connector, einmalige oder geplante Batch-Abzüge</td></tr>
<tr><td>REST-Client im Notebook</td><td>SaaS-/Web-APIs ohne Datenbankschnittstelle und ohne verfügbaren Managed Connector</td></tr>
</table>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Databricks stellt sowohl einen offiziellen JDBC- als auch einen ODBC-Treiber bereit, die dem Industriestandard folgen und u. a. auch von BI-Tools zum Zugriff <em>auf</em> Unity-Catalog-Tabellen genutzt werden. Für den ODBC-Treiber ab Version 2.6.17 wird zusätzlich <strong>Cloud Fetch</strong> unterstützt: Große Abfrageergebnisse werden dabei über den ans Databricks-Deployment angebundenen Cloud-Speicher statt über eine einzelne Verbindung übertragen, was den Datendurchsatz bei großen Ergebnismengen deutlich erhöht.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/integrations/jdbc-odbc-bi.html">Databricks ODBC and JDBC Drivers &ndash; Databricks-Dokumentation</a></div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 2 - Data Ingestion and Loading\07 Daten laden via JDBC-ODBC und REST-APIs in Notebooks.pdf",
    title="Daten laden via JDBC/ODBC und REST-APIs in Notebooks",
    subtitle="Section 2 &middot; Data Ingestion and Loading &middot; Quelle: Databricks-Dokumentation (JDBC/ODBC)",
    body_html=body,
    build_name="gap_s2_jdbc",
)
print("OK")
