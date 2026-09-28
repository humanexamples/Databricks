# Sinks in Lakeflow Pipelines

Dieses Dokument fasst die Databricks-Referenzseite "Use sinks in pipelines" zusammen. Verifiziert per `WebFetch` gegen die AWS-Seite (`docs.databricks.com/aws/en/ldp/ldp-sinks`) und wörtlich vollständig extrahiert von der inhaltlich übereinstimmenden Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/ldp-sinks`).

## Abschnittsübersicht

1. [Zweck und Einordnung](#zweck)
2. [Sink-Workflow](#workflow)
3. [Sink erstellen](#sink-erstellen)
4. [Mit einem Append Flow in einen Sink schreiben](#append-flow-schreiben)
5. [Limitierungen](#limitierungen)
6. [Quellen](#quellen)

---

## <a id="zweck">1. Zweck und Einordnung</a>

Die Lakeflow-Pipeline-`sink`-API wird zusammen mit Flows verwendet, um von einer Pipeline transformierte Datensätze in eine externe Daten-Senke ("external data sink") zu schreiben. Externe Daten-Senken umfassen Unity-Catalog-Managed- und -External-Tables sowie Event-Streaming-Dienste wie Apache Kafka oder Azure Event Hubs. Daten-Senken können außerdem verwendet werden, um in benutzerdefinierte Datenquellen zu schreiben, indem Python-Code für diese Datenquelle geschrieben wird.

**Wichtige Hinweise aus der Doku:**

- Die `sink`-API ist nur für Python verfügbar.
- Ein benutzerdefinierter Sink lässt sich außerdem über die ForEachBatch-API erstellen.

## <a id="workflow">2. Sink-Workflow</a>

Während Event-Daten aus einer Streaming-Quelle in die Pipeline aufgenommen werden, werden diese Daten in Transformationen der Pipeline verarbeitet und veredelt. Anschließend wird Append-Flow-Verarbeitung genutzt, um die transformierten Datensätze zu einem Sink zu streamen. Dieser Sink wird über die Funktion `create_sink()` erstellt.

```mermaid
flowchart LR
    Q["Streaming-Quelle"] --> T["Transformationen<br/>in der Pipeline"]
    T --> CS["create_sink(...)"]
    CS --> AF["append_flow oder<br/>update_flow (target=Sink)"]
    AF --> EXT["externes Ziel<br/>Delta außerhalb · Kafka · Event Hubs · Custom"]
```

Das Implementieren eines Sinks besteht aus zwei Schritten:

1. Den Sink erstellen.
2. Einen Append Flow oder Update Flow verwenden, um die vorbereiteten Datensätze in den Sink zu schreiben.

## <a id="sink-erstellen">3. Sink erstellen</a>

Databricks unterstützt mehrere Arten von Ziel-Senken, in die verarbeitete Datensätze aus dem Stream geschrieben werden können:

- Delta-Table-Sinks (einschließlich Unity-Catalog-Managed- und -External-Tables)
- Apache-Kafka-Sinks
- Azure-Event-Hubs-Sinks
- Benutzerdefinierte Sinks in Python, über Python Custom Data Sources

### Delta-Sinks

Delta-Sink per Dateipfad erstellen:

```python
dp.create_sink(
  name = "delta_sink",
  format = "delta",
  options = {"path": "/Volumes/catalog_name/schema_name/volume_name/path/to/data"}
)
```

Delta-Sink per Tabellenname erstellen, mit vollständig qualifiziertem Catalog- und Schema-Pfad:

```python
dp.create_sink(
  name = "delta_sink",
  format = "delta",
  options = { "tableName": "catalog_name.schema_name.table_name" }
)
```

### Kafka- und Azure-Event-Hubs-Sinks

Derselbe Code funktioniert sowohl für Apache-Kafka- als auch für Azure-Event-Hubs-Sinks:

```python
credential_name = "<service-credential>"
eh_namespace_name = "dp-eventhub"
bootstrap_servers = f"{eh_namespace_name}.servicebus.windows.net:9093"
topic_name = "dp-sink"

dp.create_sink(
name = "eh_sink",
format = "kafka",
options = {
    "databricks.serviceCredential": credential_name,
    "kafka.bootstrap.servers": bootstrap_servers,
    "topic": topic_name
  }
)
```

`credential_name` referenziert ein Unity-Catalog-Service-Credential.

### Python Custom Data Sources

Angenommen, es existiert eine als `my_custom_datasource` registrierte Python-Custom-Data-Source:

```python
from pyspark import pipelines as dp

# Assume `my_custom_datasource` is a custom Python streaming
# data source that writes data to your system.

# Create Lakeflow pipelines sink using my_custom_datasource
dp.create_sink(
    name="custom_sink",
    format="my_custom_datasource",
    options={
        <options-needed-for-custom-datasource>
    }
)

# Create append flow to send data to RequestBin
@dp.append_flow(name="flow_to_custom_sink", target="custom_sink")
def flow_to_custom_sink():
    return read_stream("my_source_data")
```

## <a id="append-flow-schreiben">4. Mit einem Append Flow in einen Sink schreiben</a>

Nachdem der Sink erstellt wurde, werden verarbeitete Datensätze hineingeschrieben, indem der Sink als `target`-Wert im `append_flow`-Decorator angegeben wird.

- **Unity-Catalog-Managed- und -External-Tables:** Format `delta` verwenden und Pfad oder Tabellenname in den Options angeben. Die Pipeline muss für die Verwendung von Unity Catalog konfiguriert sein.
- **Apache-Kafka-Topics:** Format `kafka` verwenden und Topic-Name, Verbindungsinformationen und Authentifizierungsinformationen in den Options angeben — dieselben Options, die ein Spark-Structured-Streaming-Kafka-Sink unterstützt.
- **Azure Event Hubs:** Format `kafka` verwenden und Event-Hubs-Name, Verbindungsinformationen und Authentifizierungsinformationen in den Options angeben — dieselben Options, die ein Spark-Structured-Streaming-Event-Hubs-Sink über das Kafka-Interface unterstützt.

### Delta-Sink

```python
@dp.append_flow(name = "delta_sink_flow", target="delta_sink")
def delta_sink_flow():
  return(
  spark.readStream.table("spark_referrers")
  .selectExpr("current_page_id", "referrer", "current_page_title", "click_count")
)
```

### Kafka- und Azure-Event-Hubs-Sinks

```python
@dp.append_flow(name = "kafka_sink_flow", target = "eh_sink")
def kafka_sink_flow():
return (
  spark.readStream.table("spark_referrers")
  .selectExpr("cast(current_page_id as string) as key", "to_json(struct(referrer, current_page_title, click_count)) AS value")
)
```

Der Parameter `value` ist für einen Azure-Event-Hubs-Sink zwingend erforderlich. Zusätzliche Parameter wie `key`, `partition`, `headers` und `topic` sind optional.

## <a id="limitierungen">5. Limitierungen</a>

Wörtlich aus der Doku übernommene Limitierungs-Liste:

- Nur die Python-API wird unterstützt. SQL wird nicht unterstützt.
- Nur Streaming-Queries werden unterstützt. Batch-Queries werden nicht unterstützt.
- Nur `append_flow` und `update_flow` können verwendet werden, um in Sinks zu schreiben. Andere Flows, etwa `create_auto_cdc_flow`, werden nicht unterstützt, und ein Sink kann nicht in einer Pipeline-Dataset-Definition verwendet werden. Folgendes wird beispielsweise **nicht** unterstützt:

    ```python
    @table("from_sink_table")
    def fromSink():
      return read_stream("my_sink")
    ```
- Für Delta-Sinks muss der Tabellenname vollständig qualifiziert sein. Konkret muss der Tabellenname für Unity-Catalog-Managed- und -External-Tables die Form `<catalog>.<schema>.<table>` haben; für den Hive-Metastore muss er die Form `<schema>.<table>` haben.
- Das Ausführen eines Full-Refresh-Updates räumt zuvor berechnete Ergebnisdaten in den Sinks **nicht** auf. Das bedeutet, dass erneut verarbeitete Daten an den Sink angehängt werden und bestehende Daten nicht verändert werden.
- Pipeline-Expectations werden nicht unterstützt (siehe `08 Data Quality (Expectations)/Expectations-Grundlagen.md`, Abschnitt "Limitierungen").
- Serverless Egress Control unterstützt nur Kafka- und Delta-Lake-Sink-Connectors.

---

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/ldp-sinks
- https://learn.microsoft.com/en-us/azure/databricks/ldp/ldp-sinks (wörtliche Vollzitat-Quelle, inhaltlich mit AWS-Seite abgeglichen)
