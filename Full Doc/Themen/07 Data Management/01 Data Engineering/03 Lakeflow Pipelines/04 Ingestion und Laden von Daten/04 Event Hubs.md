# Azure Event Hubs als Pipeline-Datenquelle — Referenz

Dieses Dokument beschreibt, wie Nachrichten aus Azure Event Hubs in einer Lakeflow-Declarative-Pipeline (LDP) verarbeitet werden. Es vertieft den in `Daten laden.md` Abschnitt 7 verlinkten Kurzabschnitt. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/event-hubs`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte. Die Zielstruktur dieses Projekts verlinkt auf die AWS-Doku-URL (`docs.databricks.com/aws/en/ldp/event-hubs`); der Inhalt ist Azure-spezifisch, aber auch auf der AWS-Domain als Teil der einheitlichen Databricks-Dokumentation gespiegelt.

## Abschnittsübersicht

1. [Grundprinzip: Kafka-kompatible Schnittstelle statt eigenem Connector](#grundprinzip)
2. [Benötigte Event-Hubs-Verbindungswerte](#verbindungswerte)
3. [Policy Key als Databricks Secret hinterlegen](#secret)
4. [Pipeline-Code zum Konsumieren von Events](#pipeline-code)
5. [Pipeline erstellen und Konfiguration parametrisieren](#pipeline-erstellen)
6. [Quellen](#quellen)

---

## <a id="grundprinzip">1. Grundprinzip: Kafka-kompatible Schnittstelle statt eigenem Connector</a>

Nachrichten aus Azure Event Hubs lassen sich in einer Pipeline über die Kafka-kompatible Schnittstelle verarbeiten. Der **Structured-Streaming-Event-Hubs-Connector** kann **nicht** verwendet werden, da diese Bibliothek nicht Teil der Databricks Runtime ist und Lakeflow-Pipelines keine Drittanbieter-JVM-Bibliotheken erlauben.

Azure Event Hubs bietet stattdessen einen zu Apache Kafka kompatiblen Endpunkt, der zusammen mit dem in der Databricks Runtime enthaltenen Structured-Streaming-Kafka-Connector zur Verarbeitung von Event-Hubs-Nachrichten genutzt werden kann.

## <a id="verbindungswerte">2. Benötigte Event-Hubs-Verbindungswerte</a>

Um eine Pipeline mit einer bestehenden Event-Hubs-Instanz zu verbinden und Events aus einem Topic zu konsumieren, werden folgende Verbindungswerte benötigt:

- der Name des Event-Hubs-Namespace,
- der Name der Event-Hub-Instanz innerhalb des Namespace,
- ein Shared-Access-Policy-Name und der zugehörige Policy-Key.

Standardmäßig wird für jeden Event-Hubs-Namespace eine `RootManageSharedAccessKey`-Policy angelegt, die `manage`-, `send`- und `listen`-Berechtigungen besitzt. Liest die Pipeline nur aus Event Hubs, empfiehlt Databricks, eine neue Policy mit ausschließlich `listen`-Berechtigung anzulegen.

**Hinweise laut Doku:**

- Azure Event Hubs bietet sowohl OAuth-2.0- als auch Shared-Access-Signature-(SAS)-Optionen zur Autorisierung. Die Doku-Anleitung nutzt SAS-basierte Authentifizierung.
- Wird der Event-Hubs-Connection-String aus dem Azure-Portal bezogen, enthält er möglicherweise keinen `EntityPath`-Wert. Dieser wird nur für den Structured-Streaming-Event-Hubs-Connector benötigt; bei Nutzung des Structured-Streaming-Kafka-Connectors muss lediglich der Topic-Name angegeben werden.

## <a id="secret">3. Policy Key als Databricks Secret hinterlegen</a>

Da der Policy Key sensible Information ist, empfiehlt Databricks, den Wert nicht im Pipeline-Code hartzukodieren, sondern über Databricks Secrets zu speichern und zu verwalten.

Beispiel über die Databricks CLI zum Anlegen eines Secret Scope und Speichern des Keys:

```bash
databricks --profile <profile-name> secrets create-scope <scope-name>

databricks --profile <profile-name> secrets put-secret <scope-name> <shared-policy-name> --string-value <shared-policy-key>
```

Im Pipeline-Code wird der Key-Wert anschließend über `dbutils.secrets.get()` mit `scope-name` und `shared-policy-name` abgerufen.

## <a id="pipeline-code">4. Pipeline-Code zum Konsumieren von Events</a>

Das folgende Beispiel liest IoT-Events aus einem Topic. Als Best Practice empfiehlt Databricks, Anwendungsvariablen über die Pipeline-Einstellungen zu konfigurieren; der Pipeline-Code liest sie dann über `spark.conf.get()` aus.

```python
from pyspark import pipelines as dp
import pyspark.sql.types as T
from pyspark.sql.functions import *

# Event Hubs configuration
EH_NAMESPACE                    = spark.conf.get("iot.ingestion.eh.namespace")
EH_NAME                         = spark.conf.get("iot.ingestion.eh.name")

EH_CONN_SHARED_ACCESS_KEY_NAME  = spark.conf.get("iot.ingestion.eh.accessKeyName")
SECRET_SCOPE                    = spark.conf.get("io.ingestion.eh.secretsScopeName")
EH_CONN_SHARED_ACCESS_KEY_VALUE = dbutils.secrets.get(scope = SECRET_SCOPE, key = EH_CONN_SHARED_ACCESS_KEY_NAME)

EH_CONN_STR                     = f"Endpoint=sb://{EH_NAMESPACE}.servicebus.windows.net/;SharedAccessKeyName={EH_CONN_SHARED_ACCESS_KEY_NAME};SharedAccessKey={EH_CONN_SHARED_ACCESS_KEY_VALUE}"
# Kafka Consumer configuration

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

# PAYLOAD SCHEMA
payload_ddl = """battery_level BIGINT, c02_level BIGINT, cca2 STRING, cca3 STRING, cn STRING, device_id BIGINT, device_name STRING, humidity BIGINT, ip STRING, latitude DOUBLE, lcd STRING, longitude DOUBLE, scale STRING, temp  BIGINT, timestamp BIGINT"""
payload_schema = T._parse_datatype_string(payload_ddl)

# Basic record parsing and adding ETL audit columns
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
    "pipelines.reset.allowed": "false" # preserves the data in the delta table if you do full refresh
  },
  partition_cols=["eh_enqueued_date"]
)
@dp.expect("valid_topic", "topic IS NOT NULL")
@dp.expect("valid records", "parsed_records IS NOT NULL")
def iot_raw():
  return (
   spark.readStream
    .format("kafka")
    .options(**KAFKA_OPTIONS)
    .load()
    .transform(parse)
  )
```

## <a id="pipeline-erstellen">5. Pipeline erstellen und Konfiguration parametrisieren</a>

Eine neue Pipeline wird mit einer Python-Quelldatei angelegt, in die der obige Code eingefügt wird. Der Code referenziert konfigurierte Parameter — diese lassen sich über die Settings-UI oder direkt über die Settings-JSON angeben.

Die Settings-Datei legt zugleich den Speicherort für ein Azure-Data-Lake-Storage-(ADLS)-Storage-Account fest. Als Best Practice nutzt diese Pipeline nicht den Standard-DBFS-Speicherpfad, sondern ein ADLS-Storage-Account:

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

Platzhalter in diesem Beispiel:

| Platzhalter | Ersetzen durch |
|---|---|
| `<container-name>` | Name des Azure-Storage-Account-Containers |
| `<storage-account-name>` | Name des ADLS-Storage-Accounts |
| `<eh-namespace>` | Name des Event-Hubs-Namespace |
| `<eh-policy-name>` | Secret-Scope-Key für den Event-Hubs-Policy-Key |
| `<eventhub>` | Name der Event-Hubs-Instanz |
| `<secret-scope-name>` | Name des Databricks-Secret-Scopes, der den Event-Hubs-Policy-Key enthält |

---

## <a id="quellen">6. Quellen</a>

- Use Azure Event Hubs as a pipeline data source (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/ldp/event-hubs
- Load data in pipelines (Abschnitt "Load data from Azure Event Hubs", Verweis-Kontext): https://learn.microsoft.com/en-us/azure/databricks/ldp/load

**Stand:** 2026-08-19.
