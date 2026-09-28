# Ingestion und Laden von Daten in Pipelines

## 1. Grundprinzip

Jede von Apache Spark auf Databricks unterstützte Quelle ist ladbar; Datasets lassen sich gegen jede Query definieren, die einen Spark-DataFrame liefert (auch Streaming- und Pandas-on-Spark-DataFrames). Empfohlen: **Streaming Tables** — Auto Loader für Dateien, direktes Lesen für Message Busse. SQL- und Python-Quellen lassen sich in einer Pipeline mischen.

| Quelle | Empfohlener Weg |
|---|---|
| Dateien in Cloud-Speicher (S3, ADLS, GCS) | Auto Loader (`cloudFiles`) — inkrementell, Schema-Inferenz/-Evolution |
| DB/SaaS (Salesforce, SQL Server, PostgreSQL, Workday) | Lakeflow-Connect-Connector wenn vorhanden; sonst direkte Ingestion oder API-Antworten als Dateien |
| Message Busse (Kafka, Kinesis, Event Hubs, Pub/Sub) | direkt als Structured-Streaming-Quelle |
| andere Delta-Tabellen/UC-Objekte | direkt referenzieren (UC-Governance/Lineage übernehmen Zugriff) |
| kleine/statische Referenzdaten | Batch-Quelle in Materialized View |
| HTTP/REST ohne Connector | aus Pipeline abrufen oder Antworten als Dateien ablegen |

Vorab klären: **Identität** (Service Principal empfohlen), **Netzwerkpfad** (Storage Credential/External Location/Managed Connectivity), **Änderungs-Semantik** (Updates/Deletes → CDC nötig, sonst Append reicht).

- Ausgabeformat nicht wählbar: jede ST/MV wird als **Delta-Tabelle** gespeichert (ACID, Schema Enforcement/Evolution, Time Travel, UC-Governance/Lineage).
- Rohes Eingabeformat (`cloudFiles.format` / `format =>`): eigene Quelle → Parquet/Avro empfohlen (Schema mitgeführt, bessere Kompression).
- Roher Speicherort: UC-Volume statt ungovernter Bucket-Pfad.
- Zieltabellen: Katalog/Schema + `CLUSTER BY` (Liquid Clustering) für Performance ohne manuelles Partitions-Tuning.

## 2. Laden aus einer bestehenden Tabelle

```python
@dp.table(comment="A table summarizing counts of the top baby names for New York for 2021.")
def top_baby_names_2021():
  return (
    spark.read.table("baby_names_prepared")
      .filter(expr("Year_Of_Birth == 2021"))
      .groupBy("First_Name")
      .agg(sum("Count").alias("Total_Count"))
      .sort(desc("Total_Count"))
  )
```

```sql
CREATE OR REFRESH MATERIALIZED VIEW top_baby_names_2021
COMMENT "A table summarizing counts of the top baby names for New York for 2021."
AS SELECT First_Name, SUM(Count) AS Total_Count
FROM baby_names_prepared
WHERE Year_Of_Birth = 2021
GROUP BY First_Name
ORDER BY Total_Count DESC
-- Ergebnis: je First_Name eine Zeile mit Gesamtcount für 2021, absteigend sortiert
```

## 3. Laden von Dateien aus Cloud-Objektspeicher (Auto Loader)

Empfohlen für inkrementelles, idempotentes Laden stetig wachsender Daten.

```python
@dp.table
def customers():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .load("abfss://myContainer@myStorageAccount.dfs.core.windows.net/analysis/*/*/*.json")
  )
```

```sql
CREATE OR REFRESH STREAMING TABLE sales
  AS SELECT * FROM STREAM read_files(
    'abfss://myContainer@myStorageAccount.dfs.core.windows.net/analysis/*/*/*.json',
    format => "json"
  );
```

CSV aus UC-Volume:

```python
@dp.table
def customers():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "csv")
      .load("/Volumes/my_catalog/retail_org/customers/")
  )
```

```sql
CREATE OR REFRESH STREAMING TABLE customers
AS SELECT * FROM STREAM read_files("/Volumes/my_catalog/retail_org/customers/", format => "csv")
```

- Full Refresh mit File-Notifications-Auto-Loader: Ressourcen müssen manuell bereinigt werden (`CloudFilesResourceManager` in Notebook).
- UC-aktivierte Pipeline + Auto Loader → External Location nötig (konfiguriert + `READ FILES`-Privileg für ausführenden Nutzer).

### `COPY INTO` als batch-orientierte Alternative

Rein batch, **retryable und idempotent** (bereits geladene Dateien werden übersprungen, auch wenn seither geändert):

```sql
COPY INTO target_table [ BY POSITION | ( col_name [ , <col_name> ... ] ) ]
  FROM { source_clause | ( SELECT expression_list FROM source_clause ) }
  FILEFORMAT = data_source
  [ VALIDATE [ ALL | num_rows ROWS ] ]
  [ FILES = ( file_name [, ...] ) | PATTERN = glob_pattern ]
  [ FORMAT_OPTIONS ( { data_source_reader_option = value } [, ...] ) ]
  [ COPY_OPTIONS ( { copy_option = value } [, ...] ) ]
```

```sql
COPY INTO target_table BY POSITION
FROM '/Volumes/my_catalog/retail_org/customers/'
FILEFORMAT = CSV
VALIDATE 15 ROWS
PATTERN = 'data_202*.csv'
FORMAT_OPTIONS ('headers' = 'false')
COPY_OPTIONS ('force' = 'true', 'mergeSchema' = 'true')
-- Ergebnis: 'force'=true deaktiviert Idempotenz für diesen Lauf, mergeSchema=true erlaubt Schema-Evolution
```

Sehr große Verzeichnisse: Auto Loader statt wiederholtem `COPY INTO`.

## 4. Laden aus Message Bussen (Kafka, Pub/Sub, Kinesis, Pulsar)

Für niedrigste Latenz: Streaming Tables mit Continuous-Ausführung + Enhanced Autoscaling.

**Kafka** (`read_kafka`):

```python
@dp.table
def kafka_raw():
  return (
    spark.readStream.format("kafka")
      .option("kafka.bootstrap.servers", "kafka_server:9092")
      .option("subscribe", "topic1")
      .load()
  )
```

```sql
CREATE OR REFRESH STREAMING TABLE kafka_raw AS
  SELECT * FROM STREAM read_kafka(bootstrapServers => 'kafka_server:9092', subscribe => 'topic1');
```

**Google Pub/Sub** (`read_pubsub`):

```sql
CREATE OR REFRESH STREAMING TABLE pubsub_raw
AS SELECT * FROM STREAM read_pubsub(
  subscriptionId => 'my-subscription',
  projectId => 'my-project',
  topicId => 'my-topic',
  clientEmail => secret('pubsub-scope', 'clientEmail'),
  clientId => secret('pubsub-scope', 'clientId'),
  privateKeyId => secret('pubsub-scope', 'privateKeyId'),
  privateKey => secret('pubsub-scope', 'privateKey')
);
```

- Secrets statt Klartext für Auth (empfohlen).
- Weitere SQL-TVFs: `read_kinesis` (Kinesis), `read_pulsar` (Pulsar).

## 5. Laden aus Azure Event Hubs

Structured-Streaming-Event-Hubs-Connector **nicht nutzbar** (keine Drittanbieter-JVM-Libs in Lakeflow-Pipelines) → stattdessen der Kafka-kompatible Endpunkt von Event Hubs + der in DBR enthaltene Kafka-Connector.

**Benötigt:** Namespace-Name, Event-Hub-Instanzname, Shared-Access-Policy-Name + Key. Default je Namespace: `RootManageSharedAccessKey` (manage/send/listen) — bei reinem Lesen empfiehlt Databricks eigene Policy mit nur `listen`. OAuth-2.0 und SAS unterstützt (Referenzbeispiel nutzt SAS). Connection-String aus Portal evtl. ohne `EntityPath` — beim Kafka-Connector genügt der Topic-Name.

```bash
databricks --profile <profile-name> secrets create-scope <scope-name>
databricks --profile <profile-name> secrets put-secret <scope-name> <shared-policy-name> --string-value <shared-policy-key>
```

**Pipeline-Code** (IoT-Events, Config via `spark.conf.get()`):

```python
from pyspark import pipelines as dp
import pyspark.sql.types as T
from pyspark.sql.functions import *

EH_NAMESPACE                    = spark.conf.get("iot.ingestion.eh.namespace")
EH_NAME                         = spark.conf.get("iot.ingestion.eh.name")
EH_CONN_SHARED_ACCESS_KEY_NAME  = spark.conf.get("iot.ingestion.eh.accessKeyName")
SECRET_SCOPE                    = spark.conf.get("io.ingestion.eh.secretsScopeName")
EH_CONN_SHARED_ACCESS_KEY_VALUE = dbutils.secrets.get(scope = SECRET_SCOPE, key = EH_CONN_SHARED_ACCESS_KEY_NAME)
EH_CONN_STR                     = f"Endpoint=sb://{EH_NAMESPACE}.servicebus.windows.net/;SharedAccessKeyName={EH_CONN_SHARED_ACCESS_KEY_NAME};SharedAccessKey={EH_CONN_SHARED_ACCESS_KEY_VALUE}"

KAFKA_OPTIONS = {
  "kafka.bootstrap.servers"  : f"{EH_NAMESPACE}.servicebus.windows.net:9093",
  "subscribe"                : EH_NAME,
  "kafka.sasl.mechanism"     : "PLAIN",
  "kafka.security.protocol"  : "SASL_SSL",
  "kafka.sasl.jaas.config"   : f"kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required username=\"$ConnectionString\" password=\"{EH_CONN_STR}\";",
  "kafka.request.timeout.ms" : spark.conf.get("iot.ingestion.kafka.requestTimeout"),
  "kafka.session.timeout.ms" : spark.conf.get("iot.ingestion.kafka.sessionTimeout"),
  "maxOffsetsPerTrigger"     : spark.conf.get("iot.ingestion.spark.maxOffsetsPerTrigger"),
  "failOnDataLoss"           : spark.conf.get("iot.ingestion.spark.failOnDataLoss"),
  "startingOffsets"          : spark.conf.get("iot.ingestion.spark.startingOffsets")
}

payload_ddl = """battery_level BIGINT, c02_level BIGINT, cca2 STRING, cca3 STRING, cn STRING, device_id BIGINT, device_name STRING, humidity BIGINT, ip STRING, latitude DOUBLE, lcd STRING, longitude DOUBLE, scale STRING, temp  BIGINT, timestamp BIGINT"""
payload_schema = T._parse_datatype_string(payload_ddl)

def parse(df):
  return (df
    .withColumn("records", col("value").cast("string"))
    .withColumn("parsed_records", from_json(col("records"), payload_schema))
    .withColumn("iot_event_timestamp", expr("cast(from_unixtime(parsed_records.timestamp / 1000) as timestamp)"))
    .withColumn("eh_enqueued_timestamp", expr("timestamp"))
    .withColumn("eh_enqueued_date", expr("to_date(timestamp)"))
    .withColumn("etl_processed_timestamp", col("current_timestamp"))
    .withColumn("etl_rec_uuid", expr("uuid()"))
    .drop("records", "value", "key")
  )

@dp.create_table(
  comment="Raw IOT Events",
  table_properties={
    "quality": "bronze",
    "pipelines.reset.allowed": "false"  # preserves data on full refresh
  },
  partition_cols=["eh_enqueued_date"]
)
@dp.expect("valid_topic", "topic IS NOT NULL")
@dp.expect("valid records", "parsed_records IS NOT NULL")
def iot_raw():
  return (
   spark.readStream.format("kafka").options(**KAFKA_OPTIONS).load().transform(parse)
  )
```

Konfigurationswerte über Pipeline-Settings; Best Practice: eigenes ADLS-Storage-Account als `storage`-Pfad statt DBFS-Standard:

```json
{
  "storage": "abfss://<container-name>@<storage-account-name>.dfs.core.windows.net/iot/",
  "configuration": {
    "iot.ingestion.eh.namespace": "<eh-namespace>",
    "iot.ingestion.eh.accessKeyName": "<eh-policy-name>",
    "iot.ingestion.eh.name": "<eventhub>",
    "io.ingestion.eh.secretsScopeName": "<secret-scope-name>",
    "iot.ingestion.spark.maxOffsetsPerTrigger": "50000",
    "iot.ingestion.spark.startingOffsets": "latest",
    "iot.ingestion.spark.failOnDataLoss": "false",
    "iot.ingestion.kafka.requestTimeout": "60000",
    "iot.ingestion.kafka.sessionTimeout": "30000"
  }
}
```

## 6. Laden aus externen Systemen (JDBC, Lakehouse Federation)

Jede von Databricks unterstützte Quelle ladbar. Zusätzlich **Lakehouse Federation** (benötigt DBR ≥ 13.3 LTS → Pipeline auf Preview-Channel). Ohne SQL-Äquivalent: Python nutzen (SQL/Python mischbar):

```python
import dp

@dp.table
def postgres_raw():
  return (
    spark.read.format("postgresql")
      .option("dbtable", table_name)
      .option("host", database_host_url)
      .option("port", 5432)
      .option("database", database_name)
      .option("user", username)
      .option("password", password)
      .load()
  )
```

## 7. API-Ingestion (HTTP/REST ohne Managed Connector)

**Keine eingebaute generische API-Quelle** — Auth/Pagination/Rate Limits selbst handhaben. **Vor Eigenentwicklung prüfen:** Lakeflow-Connect-Connector (Salesforce, Workday, ServiceNow, Google Analytics u. a., wachsend) — übernimmt Auth/Pagination/inkrementelle Extraktion, meist weniger Aufwand.

Voraussetzungen: Pipeline; API-Credentials als Secret (nie im Code); Netzwerkzugriff Compute → API.

| Muster | Einsatz wenn |
|---|---|
| Periodische Abrufe als Materialized View | kleine/mittlere Payloads, einmaliger Abruf pro Lauf |
| Python Data Source API | hochvolumig/streamend, inkrementeller Checkpoint |
| Entkoppelt via Scheduled Job + Auto Loader | API-Eigenheiten isolieren, Exactly-once-Datei-Tracking |

**Muster 1 — Periodische Abrufe als Materialized View** (Funktion läuft bei jedem Update vollständig+idempotent neu; Token als Secret → `spark_conf`: `"api.token": "{{secrets/<scope-name>/<secret-name>}}"`, gelesen via `spark.conf.get("api.token")`):

```python
import requests
from pyspark import pipelines as dp
from pyspark.sql import Row

@dp.materialized_view(name="exchange_rates_bronze", comment="Daily FX rates pulled from a public REST API")
def exchange_rates_bronze():
    resp = requests.get(
        "https://api.example.com/v1/rates",
        params={"base": "USD"},
        headers={"Authorization": f"Bearer {spark.conf.get('api.token')}"},
        timeout=30,
    )
    resp.raise_for_status()
    rates = resp.json()["rates"]
    rows = [Row(currency=k, rate=float(v), as_of_date=resp.json()["date"]) for k, v in rates.items()]
    return spark.createDataFrame(rows)
```

Pagination innerhalb der Funktion:

```python
@dp.materialized_view(name="customers_bronze", comment="Customers pulled from a paginated REST API")
def customers_bronze():
    token = spark.conf.get("api.token")
    rows = []
    url = "https://api.example.com/v1/customers"
    while url:
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        rows.extend(Row(**record) for record in payload["data"])
        url = payload.get("next")
    return spark.createDataFrame(rows)
```

- Retry/Backoff empfohlen. Liest bei jedem Update die vollständige Antwort neu — nur für begrenzte Payloads geeignet.

**Muster 2 — Python Data Source API** (echte Streaming-Semantik, Checkpoint-Fortschritt):

```python
spark.dataSource.register(MyApiDataSource)

from pyspark import pipelines as dp

@dp.table(name="events_bronze")
def events_bronze():
    return spark.readStream.format("my_api_source").load()
```

**Muster 3 — Entkoppelt: Scheduled Job + Auto Loader** (Job landet rohe Antworten als Dateien im UC-Volume, Pipeline holt via Auto Loader — isoliert API-Eigenheiten, liefert Exactly-once-Tracking):

```python
# Notebook/Skript, separat per Lakeflow Jobs geplant
import requests, json, time

token = dbutils.secrets.get(scope="<scope-name>", key="<secret-name>")
volume_path = "/Volumes/main/raw/landing/api_events"

resp = requests.get("https://api.example.com/v1/events", headers={"Authorization": f"Bearer {token}"}, timeout=30)
resp.raise_for_status()
with open(f"{volume_path}/events_{int(time.time())}.json", "w") as f:
    json.dump(resp.json()["data"], f)
```

```python
# In der Pipeline
from pyspark import pipelines as dp

@dp.table(name="api_events_bronze")
def api_events_bronze():
    return (
        spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "json")
            .load("/Volumes/main/raw/landing/api_events")
    )
```

**Best Practices:** Secrets aus Quellcode heraushalten; Antworten früh mit Expectations validieren; Pagination/Rate Limits mit Retry+Backoff handhaben.

## 8. Laden kleiner/statischer Datensätze

```python
@dp.table
def clickstream_raw():
  return (spark.read.format("json").load("/databricks-datasets/wikipedia-datasets/data-001/clickstream/raw-uncompressed-json/2015_2_clickstream.json"))
```

```sql
CREATE OR REFRESH MATERIALIZED VIEW clickstream_raw
AS SELECT * FROM read_files("/databricks-datasets/wikipedia-datasets/data-001/clickstream/raw-uncompressed-json/2015_2_clickstream.json")
```

`read_files` ist über alle SQL-Umgebungen auf Databricks einheitlich verfügbar — empfohlenes Muster für direkten Dateizugriff via SQL in Pipelines.

## 9. Laden über eine Python-Custom-Data-Source

Für eigene Formate oder Wiederverwendung von Python-Code für interne Systeme:

```python
from pyspark import pipelines as dp

# my_custom_datasource unterstützt Batch- und Streaming-Reads und wurde
# via spark.dataSource.register registriert.

@dp.table(name = "read_from_batch")  # erzeugt eine Materialized View
def read_from_batch():
    return spark.read.format("my_custom_datasource").load()

@dp.table(name = "read_from_streaming")  # erzeugt eine Streaming Table
def read_from_streaming():
    return spark.readStream.format("my_custom_datasource").load()
```

## 10. Schema-Änderungen an einer Quell-Streaming-Table ignorieren (`skipChangeCommits`)

Streaming Tables verlangen standardmäßig Append-only-Quellen. Bei Updates/Deletes in der Quelle (z. B. DSGVO-Löschung): Flag `skipChangeCommits` übersteuert dies — Änderungen werden ignoriert. Nur mit `spark.readStream` + `option()`; **nicht** wenn die Quelle Ziel einer `create_auto_cdc_flow()` ist.

```python
@dp.table
def b():
   return spark.readStream.option("skipChangeCommits", "true").table("A")
```

## 11. Speicher-Credentials sicher über Secrets einbinden

Spark-Property im `spark_conf`-Block der Cluster-Konfiguration — Schlüssel mit Präfix `spark.hadoop.`:

```json
{
  "id": "43246596-a63f-11ec-b909-0242ac120002",
  "storage": "abfss://<container-name>@<storage-account-name>.dfs.core.windows.net/<path>",
  "clusters": [
    {
      "spark_conf": {
        "spark.hadoop.fs.azure.account.key.<storage-account-name>.dfs.core.windows.net": "{{secrets/<scope-name>/<secret-name>}}"
      },
      "autoscale": { "min_workers": 1, "max_workers": 5, "mode": "ENHANCED" }
    }
  ],
  "development": true,
  "continuous": false,
  "libraries": [ { "notebook": { "path": "/Users/user@databricks.com/Pipeline Notebooks/pipeline quickstart" } } ],
  "name": "pipeline quickstart using ADLS2"
}
```

```python
from pyspark import pipelines as dp

json_path = "abfss://<container-name>@<storage-account-name>.dfs.core.windows.net/<path-to-input-dataset>"

@dp.create_table(comment="Data ingested from an ADLS2 storage account.")
def read_from_ADLS2():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .load(json_path)
  )
```

Gleiches Verfahren für jedes andere benötigte Secret (z. B. AWS-Keys, Hive-Metastore-Passwort).

## 12. Schema-Inferenz und -Evolution mit `from_json` (Public Preview)

`from_json` parst eine JSON-String-Spalte → Struct. Außerhalb von Pipelines: Schema muss explizit angegeben werden (`schema`-Argument). **Innerhalb einer Pipeline:** automatische Inferenz/Evolution möglich (Auto Loader, Kafka, Kinesis) — erkennt neue Felder (auch verschachtelt), inferiert Typen, erweitert Schema automatisch, behandelt nicht passende Daten automatisch.

**Automatische Inferenz** (`schemaLocationKey` eindeutig pro `from_json`-Ausdruck und Pipeline, Schema auf `NULL`):

```sql
from_json(jsonStr, NULL, map("schemaLocationKey", "<uniqueKey>" [, otherOptions]))
```

```sql
SELECT
  value,
  from_json(value, NULL, map('schemaLocationKey', 'keyX')) parsedX,
  from_json(value, NULL, map('schemaLocationKey', 'keyY')) parsedY
FROM STREAM READ_FILES('/databricks-datasets/nyctaxi/sample/json/', format => 'text')
```

Festes Schema (auch außerhalb von Pipelines): reguläre Syntax `from_json(jsonStr, schema, [, options])`.

- Inferenz aus erstem Batch, indiziert über `schemaLocationKey`. `{"id": 123, "name": "John"}` → `STRUCT<id LONG, name STRING, _rescued_data STRING>`. Top-Level-Array → umschlossen: `STRUCT<value ARRAY<id LONG, name STRING>, _rescued_data STRING>` (per `explode` aufsplittbar).

**Schema Hints** überschreiben inferierte Typen (Semantik wie Auto Loader). Bei Top-Level-Arrays: Präfix `element.`:

```sql
SELECT
from_json(data, NULL, map('schemaLocationKey', 'x', 'schemaHints', 'a STRING')),  -- {"a": 1} -> a als STRING
FROM STREAM READ_FILES(...)
```

**Schema-Evolution** (`schemaEvolutionMode`) — neue Felder werden ans Schema-Ende angehängt, bestehende Typen unverändert, Pipeline startet automatisch mit neuem Schema neu:

| `schemaEvolutionMode` | Verhalten bei neuer Spalte |
|---|---|
| `addNewColumns` (Standard) | Stream schlägt einmalig fehl, Spalte wird hinzugefügt |
| `rescue` | kein Fehlschlag, Schema entwickelt sich nie weiter; neue Spalten in Rescued-Data |
| `failOnNewColumns` | Stream schlägt fehl, startet nicht neu bis `schemaHints`/Daten angepasst |
| `none` | keine Weiterentwicklung, neue Spalten ignoriert (sofern `rescuedDataColumn` nicht gesetzt), kein Fehlschlag |

**Rescued-Data (`_rescued_data`, umbenennbar via `rescuedDataColumn`):** rettet nicht zum Schema passende Spalten (Typkonflikt, fehlend, Groß-/Kleinschreibung). Beschädigte Datensätze: `_corrupt_record` via Schema Hint (umbenennbar via `columnNameOfCorruptRecord`):

```sql
CREATE STREAMING TABLE bronze AS
  SELECT from_json(value, NULL,
      map('schemaLocationKey', 'nycTaxi',
          'schemaHints', '_corrupt_record STRING',
          'columnNameOfCorruptRecord', '_corrupt_record')) jsonCol
  FROM STREAM READ_FILES('/databricks-datasets/nyctaxi/sample/json/', format => 'text')
```

3 Modi für beschädigte Datensätze: `PERMISSIVE` (String ins konfigurierte Feld, fehlerhafte Felder `null`), `DROPMALFORMED` (ignoriert; mit `rescuedDataColumn` führen reine Typkonflikte nicht zum Verwerfen), `FAILFAST` (Exception; mit `rescuedDataColumn` werfen reine Typkonflikte keinen Fehler).

**Referenzierung inferierter Felder:** Referenz vor erstem erfolgreichem Lauf von `from_json` → Feld löst sich nicht auf, Query wird übersprungen → Bronze (parsen)/Silver (referenzieren) trennen:

```sql
CREATE STREAMING TABLE bronze AS
  SELECT from_json(value, NULL, map('schemaLocationKey', 'nycTaxi')) jsonCol
  FROM STREAM READ_FILES('/databricks-datasets/nyctaxi/sample/json/', format => 'text')

CREATE STREAMING TABLE silver AS
  SELECT jsonCol.VendorID, jsonCol.total_amount FROM bronze
```

Referenz in derselben Query kann Analyse fehlschlagen lassen — Abhilfe: Trennung wie oben, oder `schemaHints`:

```sql
CREATE STREAMING TABLE bronze AS
  SELECT from_json(value, NULL, map('schemaLocationKey', 'nycTaxi', 'schemaHints', 'total_amount DOUBLE')) jsonCol
  FROM STREAM READ_FILES('/databricks-datasets/nyctaxi/sample/json/', format => 'text')
  WHERE jsonCol.total_amount > 100.0
```

**`from_json` vs. `parse_json`:** `parse_json` → `VARIANT` (flexibel, kein erzwungenes Schema, in und außerhalb Pipelines). `from_json`+Inferenz/Evolution: **nur in Pipelines**, passt bei erzwungenem Schema, Speicher-/Latenzoptimierung, Fehlschlag bei Typkonflikten, Teilergebnis-Extraktion via `_corrupt_record`. `parse_json`/`VARIANT` passt bei flexiblem/schnell wechselndem Schema, keinem Fehlschlag bei Typkonflikten, Vermeidung der Rescued-Data-Spalte.

> **Wichtig:** Diese `from_json`-Inferenz-/-Evolution-Syntax ist außerhalb von Pipelines nicht nutzbar. Ein Feld lässt sich auf das Schema der Ziel-Streaming-Table beziehen. Festes Schema + Evolution gleichzeitig geht nicht — Schema Hints können aber einzelne/alle inferierten Felder überschreiben. Full Refresh leert die verknüpften Schema-Speicherorte, Schema wird neu inferiert.

---

**Stand:** 2026-09-14.
