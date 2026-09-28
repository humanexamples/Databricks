# -*- coding: utf-8 -*-
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import render_pdf

def code(lang, text):
    return f'<pre class="code {lang}">{html.escape(text.strip())}</pre>'

body = f"""
<p>In vielen Unternehmen laufen unterschiedliche Ereignistypen &ndash; Marketing-Events, Logistik-Meldungen, Store-Vorgänge &ndash; über ein und denselben technischen Kanal, etwa ein einzelnes Kafka-Topic oder einen gemeinsamen Cloud-Speicherpfad. Ohne besondere Vorkehrung müsste für jeden Ereignistyp eine eigene Ingestion-Pipeline mit eigenem Checkpoint gebaut werden &ndash; bei fünf Ereignistypen also fünf parallele, weitgehend redundante Pipelines. Das <strong>Multiplex-Muster</strong> löst dieses Problem, indem es die Quelle nur einmal liest und die Daten erst anschließend nach Typ auffächert. Dieses Kapitel behandelt außerdem zwei eng verwandte fortgeschrittene Techniken: <strong>Delta Sinks</strong> für Schreibzugriffe außerhalb der von der Pipeline verwalteten Tabellen, und <strong>Delta UniForm</strong> für den lesenden Zugriff aus Iceberg-kompatiblen Tools wie Snowflake oder Trino.</p>

<h2>1. Das Multiplex-Muster: einmal einlesen, nach Typ verzweigen</h2>
<p>Der Kerngedanke ist einfach: Zunächst werden <strong>alle</strong> Ereignistypen in eine gemeinsame Bronze-Tabelle eingelesen, ohne sie zu unterscheiden. Ein Typ-Feld im Nachrichtenkörper (z. B. <code>event_group</code> oder <code>topic</code>) identifiziert anschließend, zu welcher Fachdomäne ein Datensatz gehört. Erst in einem zweiten Schritt werden die Daten anhand dieses Feldes in domänenspezifische Zwischentabellen aufgeteilt (&bdquo;Fan-out&ldquo;). Der entscheidende Vorteil: Es existiert nur <strong>ein</strong> Checkpoint und nur <strong>ein</strong> Lesevorgang auf die Quelle, unabhängig davon, wie viele Domänen am Ende bedient werden. Ändert sich etwas an der Quelle &ndash; ein neues Feld, ein geänderter Pfad &ndash; muss diese Änderung nur an einer Stelle nachgezogen werden.</p>

<p>Im Beispiel aus der Demo-Pipeline liegen Business-Events als JSON-Payload in einer Kafka-ähnlichen Quelle vor. Die Bronze-Tabelle liest den rohen Payload zunächst als <code>VARIANT</code>-Typ ein &ndash; ein semi-strukturierter Datentyp, der beliebig verschachtelte JSON-Strukturen ohne vorheriges Schema aufnehmen kann:</p>

{code('sql', '''CREATE OR REFRESH STREAMING TABLE multiplex_1_bronze.bronze_demo
TBLPROPERTIES (
  'pipelines.reset.allowed' = false,
  'delta.feature.variantType-preview' = 'supported'
)
AS
SELECT
  CAST(key AS STRING) AS event_id,
  PARSE_JSON(CAST(value AS STRING)) AS event_data_variant,
  CAST(topic AS STRING) AS event_group,
  CAST(partition AS STRING) AS partition,
  CAST(offset AS STRING) AS offset,
  _metadata.file_name AS source_file,
  _metadata.file_modification_time AS file_mod_time
FROM STREAM read_files('${business_events_source}');

-- Fan-out: eine Zwischentabelle je Fachdomäne, gefiltert nach event_group
CREATE OR REFRESH STREAMING TABLE multiplex_1_bronze.marketing_intermediate
TBLPROPERTIES ('delta.feature.variantType-preview' = 'supported')
AS SELECT
  event_id,
  event_data_variant,
  event_group,
  event_data_variant:event_id::STRING     AS extracted_event_id,
  event_data_variant:timestamp::TIMESTAMP AS timestamp,
  event_data_variant:campaign_id::STRING  AS campaign_id,
  event_data_variant:impressions::LONG    AS impressions,
  event_data_variant:clicks::LONG         AS clicks,
  event_data_variant:spend_usd::DOUBLE    AS spend_usd,
  source_file, file_mod_time
FROM STREAM multiplex_1_bronze.bronze_demo
WHERE event_group = 'business_events_marketing';''')}

<p>Analog dazu entstehen <code>logistics_intermediate</code> und <code>store_ops_intermediate</code> als weitere Zwischentabellen, jeweils mit einer eigenen <code>WHERE event_group = ...</code>-Bedingung und ihren spezifischen, aus dem VARIANT extrahierten Feldern. Der Doppelpunkt-Operator (<code>event_data_variant:feld</code>) navigiert dabei durch die JSON-Struktur, und der <code>::</code>-Operator castet das Ergebnis auf den passenden Zieltyp. Auf diesen Zwischentabellen bauen anschließend die eigentlichen Silver-Tabellen der jeweiligen Fachdomäne auf, etwa mit berechneten Kennzahlen wie <code>click_through_rate</code> im Marketing-Zweig.</p>

<figure class="img">
<img src="assets/04/multiplex_pipeline_overview.png">
<figcaption>Eine gemeinsame Bronze-Tabelle wird nach Ereignistyp in drei Zwischentabellen aufgefächert; ein Zweig fließt zusätzlich über einen Delta Sink an ein externes System.</figcaption>
</figure>

<h2>2. Delta Sinks: Schreiben außerhalb der Pipeline</h2>
<p>Standardmäßig verwaltet eine Deklarative Pipeline jede Streaming Table und jede Materialized View selbst &ndash; inklusive Lineage-Tracking und Expectations. Ein <strong>Sink</strong> durchbricht dieses Prinzip bewusst: Er erlaubt es, Streaming-Daten aus der Pipeline heraus in eine <strong>externe</strong> Delta-Tabelle, ein Kafka-Topic oder einen Azure-Event-Hub zu schreiben &ndash; also in ein Ziel, das außerhalb des von der Pipeline verwalteten Bereichs liegt. Das ist etwa für Reverse-ETL-Szenarien relevant, bei denen verarbeitete Daten wieder an operative Systeme zurückgespielt werden sollen, oder wenn eine Tabelle Eigenschaften benötigt, die auf Pipeline-verwalteten Tabellen nicht gesetzt werden können &ndash; wie im nächsten Abschnitt beschrieben.</p>

<p>Sinks stehen ausschließlich über die Python-API zur Verfügung; eine SQL-Entsprechung existiert nicht. Die Definition erfolgt zweistufig: Zunächst wird der Sink mit <code>dp.create_sink()</code> registriert, anschließend schreibt eine mit <code>@dp.append_flow</code> dekorierte Funktion kontinuierlich neue Datensätze hinein. Checkpointing übernimmt <code>append_flow</code> automatisch; es werden pro Lauf ausschließlich neue Datensätze angehängt, nie überschrieben.</p>

{code('python', '''from pyspark import pipelines as dp

my_catalog = spark.conf.get("my_catalog")

dp.create_sink(
  name = "delta_sink_logistics",
  format = "delta",
  options = { "tableName": f"{my_catalog}.multiplex_3_gold.logistics_delta_sink" }
)

@dp.append_flow(name = "delta_sink_logistics_flow", target="delta_sink_logistics")
def delta_sink_logistics_flow():
  return(
  spark.readStream.table("multiplex_2_silver.logistics_silver_demo")
)''')}

<h2>3. Delta UniForm: Iceberg-Lesezugriff ohne Datenkopie</h2>
<p>Viele moderne Datenarchitekturen setzen nicht ausschließlich auf Databricks &ndash; Tools wie Snowflake, Trino oder Apache Athena sprechen nativ das <strong>Apache-Iceberg</strong>-Tabellenformat, nicht Delta Lake. Statt die Daten dafür in ein zweites Format zu kopieren und zwei Kopien synchron zu halten, erzeugt <strong>Delta UniForm</strong> zusätzlich zum Delta-Transaktionslog automatisch Iceberg-Metadaten für dieselben Parquet-Dateien. Es entsteht ein physischer Datenbestand mit zwei logischen Sichten: Databricks-Clients lesen weiterhin über das Delta-Protokoll, externe Iceberg-Clients greifen über den Iceberg-REST-Katalog auf dieselben Dateien zu. Die Iceberg-Metadaten werden dabei asynchron nach jedem Delta-Commit aktualisiert, sodass reguläre Schreibvorgänge nicht verlangsamt werden.</p>

<p>Wichtig für den Pipeline-Kontext: <strong>Pipeline-verwaltete Streaming Tables und Materialized Views unterstützen UniForm nicht direkt</strong> &ndash; die dafür nötige Tabelleneigenschaft <code>delta.universalFormat.enabledFormats</code> lässt sich auf ihnen nicht setzen. Genau hier schließt sich der Kreis zu den Delta Sinks aus dem vorherigen Abschnitt: Die Pipeline schreibt ihre Ergebnisse über einen Sink in eine gewöhnliche externe Delta-Tabelle, und erst auf dieser lassen sich die für UniForm nötigen Eigenschaften setzen.</p>

<table>
<tr><th>Schritt</th><th>Tabelleneigenschaft</th><th>Zweck</th></tr>
<tr><td>1</td><td><code>delta.enableDeletionVectors = false</code></td><td>Iceberg v2 kennt keine Soft-Delete-Markierungen &ndash; Deletion Vectors müssen deaktiviert sein</td></tr>
<tr><td>2</td><td><code>delta.columnMapping.mode = name</code></td><td>Konsistente Spaltenkennungen zwischen Delta- und Iceberg-Schema</td></tr>
<tr><td>3</td><td><code>delta.enableIcebergCompatV2 = true</code></td><td>Aktiviert das mit Iceberg v2 kompatible Delta-Schreibprotokoll</td></tr>
<tr><td>4</td><td><code>delta.universalFormat.enabledFormats = iceberg</code></td><td>Stößt die asynchrone Generierung der Iceberg-Metadaten an</td></tr>
</table>

<p>Diese Eigenschaften müssen einmalig gesetzt werden, bevor die erste Zeile geschrieben wird. Externe Tools erhalten den Zugriff dabei governt über Unity Catalog, das gleichzeitig als Iceberg-REST-Katalog fungiert &ndash; ohne zusätzliche Infrastruktur. Zu beachten ist, dass Schreibzugriffe weiterhin ausschließlich über Delta erfolgen dürfen: Iceberg-Clients können UniForm-Tabellen nur lesen, nicht beschreiben.</p>

<div class="docbox">
<strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> Bei aktivierter Kompatibilität über <code>enableIcebergCompatV2</code> werden Deletion Vectors für Iceberg-v2-Lesezugriffe grundsätzlich nicht unterstützt &ndash; sie müssen vor der Aktivierung deaktiviert bzw. per <code>REORG</code>-Befehl aus bestehenden Tabellen entfernt werden. Seit Kurzem unterstützt Apache Iceberg v3 Deletion Vectors auch bei aktiviertem UniForm; wer diese Kombination benötigt, kann eine Tabelle stattdessen auf <code>delta.enableIcebergCompatV3 = true</code> heben. Für Sinks gilt zudem: <code>append_flow</code> ist der einzige unterstützte Flow-Typ, Pipeline-Expectations werden auf Sinks nicht angewendet, und es werden ausschließlich Streaming-Queries unterstützt, keine Batch-Abfragen.<br>
Quelle: <a href="https://docs.databricks.com/aws/en/delta/uniform">Read Delta Lake tables with Iceberg clients using UniForm</a> &middot; <a href="https://docs.databricks.com/aws/en/ldp/concepts/sinks">Sinks in Lakeflow Spark Declarative Pipelines</a> &ndash; Databricks-Dokumentation</div>
"""

render_pdf(
    out_pdf=r"C:\Temp\a - Kopie\Databricks-Dokumentation-DE\Section 3 - Data Transformation and Modelling\07 Multiplex Streaming, Delta Sinks und Iceberg-UniForm.pdf",
    title="Multiplex Streaming, Delta Sinks & Iceberg/UniForm",
    subtitle="Section 3 &middot; Data Transformation and Modelling &middot; Quelle: Kurs 5, Kapitel 3&ndash;4",
    body_html=body,
    build_name="04_02_multiplex_sinks_uniform",
)
print("OK")
