# Daten laden — Referenz

Dieses Dokument fasst zusammen, wie Daten aus beliebigen Quellen in Lakeflow-Declarative-Pipelines (LDP) geladen werden. Es ist die Einstiegsseite der offiziellen Doku-Sektion "Load data in pipelines" und verlinkt auf die spezialisierteren Unterseiten `API-Ingestion.md`, `Schema Evolution aus JSON.md` und `Event Hubs.md` (alle in diesem Ordner). Jede faktische Aussage wurde per `WebFetch` gegen die offizielle Databricks-Online-Dokumentation verifiziert — primär über die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/load`), die im Gegensatz zur AWS-Seite eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte. Auffällige Einzelaussagen wurden zusätzlich gegen die AWS-Seite (`docs.databricks.com/aws/en/ldp/load`) gegengeprüft.

## Abschnittsübersicht

1. [Einleitung und Grundprinzip](#einleitung)
2. [Datenquellen identifizieren und den passenden Anbindungsweg wählen](#quellen-identifizieren)
3. [Dateiformat und Speicher-Layer wählen](#format-layer)
4. [Laden aus einer bestehenden Tabelle](#aus-tabelle)
5. [Laden von Dateien aus Cloud-Objektspeicher (Auto Loader)](#cloud-storage)
6. [Laden aus einem Message Bus (Kafka, Pub/Sub, Kinesis, Pulsar)](#message-bus)
7. [Laden aus Azure Event Hubs](#event-hubs)
8. [Laden aus externen Systemen (JDBC, Lakehouse Federation)](#externe-systeme)
9. [Laden kleiner/statischer Datensätze](#kleine-datensaetze)
10. [Laden über eine Python-Custom-Data-Source](#custom-data-source)
11. [Streaming Table so konfigurieren, dass sie Änderungen an einer Quell-Streaming-Table ignoriert](#skip-change-commits)
12. [Speicher-Credentials sicher über Secrets einbinden](#secrets)
13. [Quellen](#quellen)

---

## <a id="einleitung">1. Einleitung und Grundprinzip</a>

Daten lassen sich aus jeder von Apache Spark auf Databricks unterstützten Datenquelle in Pipelines laden. Datasets (Tabellen und Views) lassen sich gegen jede Query definieren, die einen Spark-DataFrame zurückgibt — einschließlich Streaming-DataFrames und Pandas-on-Spark-DataFrames.

Für Ingestion-Aufgaben empfiehlt Databricks für die meisten Anwendungsfälle Streaming Tables. Streaming Tables eignen sich für die Ingestion aus Cloud-Objektspeicher via Auto Loader oder aus Message Bussen wie Kafka.

Nicht alle Datenquellen verfügen über SQL-Unterstützung für die Ingestion. SQL- und Python-Quellen lassen sich jedoch innerhalb derselben Pipeline mischen, um Python dort einzusetzen, wo es nötig ist.

## <a id="quellen-identifizieren">2. Datenquellen identifizieren und den passenden Anbindungsweg wählen</a>

Bevor Pipeline-Code geschrieben wird, empfiehlt die Doku, jede Datenquelle zu inventarisieren: wie sie ihre Daten bereitstellt (Dateien, eine Datenbank, ein SaaS-System, eine API oder ein Stream), wie häufig sie sich ändert, und welche Credentials/Netzwerkzugriffe benötigt werden. Die Anbindungsmethode bestimmt oft, ob eine Quelle naturgemäß Batch oder Streaming ist — das früh richtig zu klären vermeidet späteren Mehraufwand.

Die Doku ordnet jede Quelle einem von sechs Anbindungswegen zu:

| Quelle | Empfohlener Anbindungsweg |
|---|---|
| Dateien in Cloud-Objektspeicher (S3, ADLS, GCS) | Der häufigste Startpunkt. Auto Loader (`cloudFiles`-Format) verwenden — übernimmt inkrementelle Erkennung, Schema-Inferenz und Schema-Evolution. |
| Datenbanken und SaaS-Anwendungen (Salesforce, SQL Server, PostgreSQL, Workday) | Einen Lakeflow-Connect-Managed-Connector verwenden, sofern für die Quelle vorhanden — konfigurationsgetrieben, übernimmt Authentifizierung und inkrementelle/CDC-Extraktion. Ohne passenden Connector: direkte Ingestion oder Ablage der API-Antworten als Dateien (siehe `API-Ingestion.md`). |
| Message Busse (Kafka, Kinesis, Azure Event Hubs, Pub/Sub) | Direkt als Structured-Streaming-Quelle lesen, da native Streaming-Quellen. |
| Andere Delta-Tabellen oder Unity-Catalog-Objekte (auch aus anderen Pipelines/Jobs) | Direkt referenzieren, Unity-Catalog-Governance und -Lineage übernehmen Zugriff/Auffindbarkeit. |
| Kleine oder statische Referenzdaten (Lookup-Dateien, selten wechselnde CSVs) | Als Batch-Quelle in einer Materialized View laden — kein Vorteil durch Streaming bei kaum wechselnden Daten. |
| Beliebige HTTP-/REST-API ohne Managed Connector | Aus der Pipeline heraus abrufen oder Antworten zunächst als Dateien ablegen (siehe `API-Ingestion.md`). |

Für jede Quelle sollten laut Doku vorab geklärt werden:

- **Identität:** Als was die Pipeline läuft. Pipelines können als Service Principal laufen — das sollte vorab eingerichtet werden, um nicht von einem persönlichen Account abhängig zu sein.
- **Netzwerkpfad:** Welche Konnektivität die Quelle benötigt (Storage Credential, External Location, Lakeflow-Connect-Managed-Connectivity).
- **Änderungs-Semantik:** Wie die Quelle Updates/Deletes signalisiert, falls überhaupt — bestimmt, ob CDC benötigt wird oder die Quelle als Append-only behandelt werden kann.

## <a id="format-layer">3. Dateiformat und Speicher-Layer wählen</a>

Pipelines treffen die meisten dieser Entscheidungen automatisch: Jede von einer Pipeline erzeugte Streaming Table und Materialized View wird standardmäßig als Delta-Tabelle gespeichert — mit ACID-Transaktionen, Schema-Enforcement und -Evolution, Time Travel sowie Unity-Catalog-Governance und -Lineage auf jedem Dataset. Das Ausgabeformat ist damit nicht wählbar. Die eigentlichen Entscheidungen betreffen die zwei Ränder der Pipeline:

- **Rohes Eingabeformat:** Was auch immer die Quelle liefert (CSV, JSON, Parquet, ...). Auto Loader und `read_files()` unterstützen diese direkt, angegeben über `cloudFiles.format` (Python) bzw. das `format =>`-Argument (SQL). Kontrolliert man die Quelle selbst, empfiehlt Databricks Parquet oder Avro, da diese Formate Schema mitführen und besser komprimieren, was Ingestion und Schema-Inferenz beschleunigt.
- **Roher Speicherort:** Für Dateien wird empfohlen, in einem Unity-Catalog-Volume statt einem ungovernten Bucket-Pfad zu landen, damit Lineage und Zugriffskontrolle bis zur Landing Zone reichen.

Für die von der Pipeline erzeugten Tabellen bleiben Zielkatalog/-schema (Governance-Grenze, Auffindbarkeit) sowie das physische Layout großer Tabellen als Entscheidung — `CLUSTER BY` (Liquid Clustering) wird empfohlen, um Query-Performance beim Wachstum ohne manuelles Partitions-Tuning zu erhalten.

## <a id="aus-tabelle">4. Laden aus einer bestehenden Tabelle</a>

Daten aus jeder existierenden Tabelle in Databricks lassen sich laden, transformieren via Query oder direkt für die Weiterverarbeitung übernehmen.

```python
@dp.table(
  comment="A table summarizing counts of the top baby names for New York for 2021."
)
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
AS SELECT
  First_Name,
  SUM(Count) AS Total_Count
FROM baby_names_prepared
WHERE Year_Of_Birth = 2021
GROUP BY First_Name
ORDER BY Total_Count DESC
```

## <a id="cloud-storage">5. Laden von Dateien aus Cloud-Objektspeicher (Auto Loader)</a>

Databricks empfiehlt Auto Loader in Pipelines für die meisten Ingestion-Aufgaben aus Cloud-Objektspeicher oder aus Dateien in einem Unity-Catalog-Volume. Auto Loader und Pipelines sind darauf ausgelegt, stetig wachsende Daten beim Eintreffen im Cloud-Speicher inkrementell und idempotent zu laden.

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
  AS SELECT *
  FROM STREAM read_files(
    'abfss://myContainer@myStorageAccount.dfs.core.windows.net/analysis/*/*/*.json',
    format => "json"
  );
```

Beispiel mit CSV-Dateien aus einem Unity-Catalog-Volume:

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
AS SELECT * FROM STREAM read_files(
  "/Volumes/my_catalog/retail_org/customers/",
  format => "csv"
)
```

**Hinweise laut Doku:**

- Wird Auto Loader mit File Notifications verwendet und ein Full Refresh der Pipeline/Streaming Table durchgeführt, müssen Ressourcen manuell bereinigt werden (`CloudFilesResourceManager` in einem Notebook).
- Zum Laden von Dateien mit Auto Loader in einer Unity-Catalog-aktivierten Pipeline müssen External Locations verwendet werden.

### Authentifizierung gegen Cloud-Speicher

Auto Loader nutzt Unity-Catalog-External-Locations zur Authentifizierung gegen Cloud-Speicher. Für den zu lesenden Speicherpfad muss eine External Location konfiguriert und dem ausführenden Nutzer das Privileg `READ FILES` gewährt sein. Für ADLS wird eine External Location konfiguriert, die auf ein Storage Credential zurückgreift, das einen Storage-Container referenziert.

## <a id="message-bus">6. Laden aus einem Message Bus (Kafka, Pub/Sub, Kinesis, Pulsar)</a>

Databricks empfiehlt für die effizienteste Ingestion mit niedriger Latenz aus Message Bussen Streaming Tables mit kontinuierlicher Ausführung ("continuous execution") und Enhanced Autoscaling.

**Kafka**, über die SQL-Funktion `read_kafka`:

```python
from pyspark import pipelines as dp

@dp.table
def kafka_raw():
  return (
    spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", "kafka_server:9092")
      .option("subscribe", "topic1")
      .load()
  )
```

```sql
CREATE OR REFRESH STREAMING TABLE kafka_raw AS
  SELECT *
  FROM STREAM read_kafka(
    bootstrapServers => 'kafka_server:9092',
    subscribe => 'topic1'
  );
```

**Google Pub/Sub**, über `read_pubsub`:

```python
@dp.table
def pubsub_raw():
  auth_options = {
    "clientId": client_id,
    "clientEmail": client_email,
    "privateKey": private_key,
    "privateKeyId": private_key_id
  }
  return (
    spark.readStream
      .format("pubsub")
      .option("subscriptionId", "my-subscription")
      .option("topicId", "my-topic")
      .option("projectId", "my-project")
      .options(auth_options)
      .load()
  )
```

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

Databricks empfiehlt ausdrücklich, Secrets für Authentifizierungsoptionen zu verwenden statt Klartextwerte.

Für weitere Message-Bus-Quellen verweist die Doku auf die SQL-Tabellenfunktionen `read_kinesis` (Kinesis) und `read_pulsar` (Pulsar).

## <a id="event-hubs">7. Laden aus Azure Event Hubs</a>

Azure Event Hubs bietet eine zu Apache Kafka kompatible Schnittstelle. Der in der Pipeline-Runtime enthaltene Structured-Streaming-Kafka-Connector kann zum Laden von Nachrichten aus Azure Event Hubs verwendet werden. Details dazu — inklusive vollständigem Praxisbeispiel mit IoT-Events — siehe `Event Hubs.md` in diesem Ordner.

## <a id="externe-systeme">8. Laden aus externen Systemen (JDBC, Lakehouse Federation)</a>

Pipelines unterstützen das Laden aus jeder von Databricks unterstützten Datenquelle. Zusätzlich lassen sich externe Daten über Lakehouse Federation laden — dafür wird Databricks Runtime 13.3 LTS oder höher benötigt, weshalb die Pipeline auf den Preview-Channel konfiguriert werden muss.

Manche Datenquellen verfügen über kein SQL-Äquivalent. Lässt sich Lakehouse Federation für eine solche Quelle nicht einsetzen, kann Python zur Ingestion verwendet werden — Python- und SQL-Quelldateien lassen sich in derselben Pipeline mischen. Beispiel für eine Materialized View, die den aktuellen Stand einer entfernten PostgreSQL-Tabelle abbildet:

```python
import dp

@dp.table
def postgres_raw():
  return (
    spark.read
      .format("postgresql")
      .option("dbtable", table_name)
      .option("host", database_host_url)
      .option("port", 5432)
      .option("database", database_name)
      .option("user", username)
      .option("password", password)
      .load()
  )
```

## <a id="kleine-datensaetze">9. Laden kleiner/statischer Datensätze</a>

Kleine oder statische Datensätze lassen sich über die reguläre Apache-Spark-Lade-Syntax laden — Pipelines unterstützen alle von Apache Spark auf Databricks unterstützten Dateiformate.

```python
@dp.table
def clickstream_raw():
  return (spark.read.format("json").load("/databricks-datasets/wikipedia-datasets/data-001/clickstream/raw-uncompressed-json/2015_2_clickstream.json"))
```

```sql
CREATE OR REFRESH MATERIALIZED VIEW clickstream_raw
AS SELECT * FROM read_files(
  "/databricks-datasets/wikipedia-datasets/data-001/clickstream/raw-uncompressed-json/2015_2_clickstream.json"
)
```

**Hinweis laut Doku:** Die SQL-Funktion `read_files` ist über alle SQL-Umgebungen auf Databricks hinweg einheitlich verfügbar und das empfohlene Muster für direkten Dateizugriff via SQL in Pipelines.

## <a id="custom-data-source">10. Laden über eine Python-Custom-Data-Source</a>

Python-Custom-Data-Sources erlauben das Laden von Daten in benutzerdefinierten Formaten — eigener Code zum Lesen/Schreiben einer spezifischen externen Datenquelle oder Wiederverwendung bestehenden Python-Codes für interne Systeme.

Das folgende Beispiel registriert eine Custom Data Source mit dem Formatnamen `my_custom_datasource` und liest daraus sowohl im Batch- als auch im Streaming-Modus:

```python
from pyspark import pipelines as dp

# Assume `my_custom_datasource` is a custom Python custom data
# source that supports both batch and streaming reads, and has
# been registered using `spark.dataSource.register`.

# This creates a materialized view
@dp.table(name = "read_from_batch")
def read_from_batch():
    return spark.read.format("my_custom_datasource").load()

# This creates a streaming table
@dp.table(name = "read_from_streaming")
def read_from_streaming():
    return spark.readStream.format("my_custom_datasource").load()
```

## <a id="skip-change-commits">11. Streaming Table so konfigurieren, dass sie Änderungen an einer Quell-Streaming-Table ignoriert</a>

Streaming Tables verlangen standardmäßig Append-only-Quellen. Erfordert die Quell-Streaming-Table Updates oder Deletes (z. B. für DSGVO-"Recht auf Vergessenwerden"-Verarbeitung), lässt sich dieses Verhalten über das Flag `skipChangeCommits` übersteuern — Änderungen werden dann ignoriert. Das Flag funktioniert nur mit `spark.readStream` über die `option()`-Funktion und kann nicht verwendet werden, wenn die Quell-Streaming-Table Ziel einer `create_auto_cdc_flow()`-Funktion ist (siehe `../05 CDC/CDC-Grundlagen.md`).

```python
@dp.table
def b():
   return spark.readStream.option("skipChangeCommits", "true").table("A")
```

## <a id="secrets">12. Speicher-Credentials sicher über Secrets einbinden</a>

Databricks Secrets lassen sich verwenden, um Credentials wie Access Keys oder Passwörter zu speichern. Zur Konfiguration in der Pipeline wird eine Spark-Property in der Cluster-Konfiguration der Pipeline-Einstellungen gesetzt.

**Wichtiger Hinweis:** Dem `spark_conf`-Konfigurationsschlüssel, der den Secret-Wert setzt, muss das Präfix `spark.hadoop.` vorangestellt werden.

```json
{
  "id": "43246596-a63f-11ec-b909-0242ac120002",
  "storage": "abfss://<container-name>@<storage-account-name>.dfs.core.windows.net/<path>",
  "clusters": [
    {
      "spark_conf": {
        "spark.hadoop.fs.azure.account.key.<storage-account-name>.dfs.core.windows.net": "{{secrets/<scope-name>/<secret-name>}}"
      },
      "autoscale": {
        "min_workers": 1,
        "max_workers": 5,
        "mode": "ENHANCED"
      }
    }
  ],
  "development": true,
  "continuous": false,
  "libraries": [
    {
      "notebook": {
        "path": "/Users/user@databricks.com/Pipeline Notebooks/pipeline quickstart"
      }
    }
  ],
  "name": "pipeline quickstart using ADLS2"
}
```

```python
from pyspark import pipelines as dp

json_path = "abfss://<container-name>@<storage-account-name>.dfs.core.windows.net/<path-to-input-dataset>"
@dp.create_table(
  comment="Data ingested from an ADLS2 storage account."
)
def read_from_ADLS2():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .load(json_path)
  )
```

Dasselbe Verfahren lässt sich für jedes andere von der Pipeline benötigte Secret verwenden, etwa AWS-Keys für S3-Zugriff oder das Passwort für einen Apache-Hive-Metastore.

---

## <a id="quellen">13. Quellen</a>

- Load data in pipelines (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/ldp/load
- Load data in pipelines (AWS): https://docs.databricks.com/aws/en/ldp/load
- Verwandte Dateien in diesem Projekt: Ordner `Lakeflow Connect/Lakeflow Connect Standard Connectors/Working with Files/06 Auto Loader/` und `_fileIngestionScenarios.md` (vertiefte Auto-Loader-Referenz und Ingestion-Szenarien-Taxonomie)

**Stand:** 2026-08-19.

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### `COPY INTO` — Datei-basiertes Laden ohne Streaming (`delta-copy-into`)

Neben Auto Loader (Abschnitt 5) beschreibt das SQL Language Manual mit `COPY INTO` einen zweiten, rein batch-orientierten Weg, um Dateien aus einem Speicherort in eine bestehende Delta-Tabelle zu laden. Der Befehl ist laut Doku **retryable und idempotent**: Dateien, die bereits geladen wurden, werden übersprungen — selbst wenn sie sich seither geändert haben.

Formale Syntax:

```sql
COPY INTO target_table [ BY POSITION | ( col_name [ , <col_name> ... ] ) ]
  FROM { source_clause | ( SELECT expression_list FROM source_clause ) }
  FILEFORMAT = data_source
  [ VALIDATE [ ALL | num_rows ROWS ] ]
  [ FILES = ( file_name [, ...] ) | PATTERN = glob_pattern ]
  [ FORMAT_OPTIONS ( { data_source_reader_option = value } [, ...] ) ]
  [ COPY_OPTIONS ( { copy_option = value } [, ...] ) ]
```

Praxisnahe Anwendung dieser Syntax — Laden headerloser CSV-Dateien per `PATTERN`-Glob, mit vorheriger Validierung der ersten 15 Zeilen und erzwungenem erneutem Laden bereits verarbeiteter Dateien:

```sql
COPY INTO target_table BY POSITION
FROM '/Volumes/my_catalog/retail_org/customers/'
FILEFORMAT = CSV
VALIDATE 15 ROWS
PATTERN = 'data_202*.csv'
FORMAT_OPTIONS ('headers' = 'false')
COPY_OPTIONS ('force' = 'true', 'mergeSchema' = 'true')
```

**Einordnung gegenüber Auto Loader:** `COPY_OPTIONS ('force' = 'true')` deaktiviert die Idempotenz gezielt für einen einzelnen Lauf; `mergeSchema = true` erlaubt Schema-Evolution beim Laden. Die Doku empfiehlt für sehr große Verzeichnisse mit vielen Dateien statt wiederholter `COPY INTO`-Aufrufe weiterhin Auto Loader.

**Quelle:** https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into
