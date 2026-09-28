# Ihren ersten Structured-Streaming-Workload ausführen — Referenz

Dieses Dokument enthält Code-Beispiele und Erklärungen der grundlegenden Konzepte, die nötig sind, um die ersten Structured-Streaming-Queries auf Databricks auszuführen. Structured Streaming wird für Near-Realtime- und inkrementelle Verarbeitungs-Workloads verwendet. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/tutorial`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte; die Original-GCP-Seite lieferte nur eine gerenderte Kurzfassung.

## Abschnittsübersicht
1. [Einleitung und Empfehlung: Lakeflow-Pipelines](#einleitung)
2. [Auto Loader zum Lesen von Streaming-Daten aus Objektspeicher verwenden](#auto-loader)
3. [Eine Streaming-Transformation durchführen](#transformation)
4. [Ein inkrementelles Batch-Schreiben nach Delta Lake durchführen](#batch-write)
5. [Daten aus Delta Lake lesen, transformieren und nach Delta Lake schreiben](#delta-zu-delta)
6. [Daten aus Kafka lesen, transformieren und nach Kafka schreiben](#kafka)
7. [Quellen](#quellen)

---

## <a id="einleitung">1. Einleitung und Empfehlung: Lakeflow-Pipelines</a>

Structured Streaming ist eine von mehreren Technologien, die Streaming-Tabellen in Lakeflow-Pipelines antreiben. Databricks empfiehlt, für alle neuen ETL-, Ingestion- und Structured-Streaming-Workloads Lakeflow-Pipelines zu verwenden. Siehe [Spark Declarative Pipelines](https://docs.databricks.com/gcp/en/ldp/).

**Hinweis:** Während Lakeflow-Pipelines eine leicht abgewandelte Syntax zur Deklaration von Streaming-Tabellen bereitstellen, gilt die allgemeine Syntax zur Konfiguration von Streaming-Reads und -Transformationen für alle Streaming-Anwendungsfälle auf Databricks. Lakeflow-Pipelines vereinfachen Streaming zudem, indem sie Zustandsinformationen, Metadaten und zahlreiche Konfigurationen selbst verwalten.

## <a id="auto-loader">2. Auto Loader zum Lesen von Streaming-Daten aus Objektspeicher verwenden</a>

Das folgende Beispiel zeigt das Laden von JSON-Daten mit Auto Loader, das `cloudFiles` zur Angabe von Format und Optionen verwendet. Die Option `schemaLocation` aktiviert Schema-Inferenz und -Evolution. Fügen Sie den folgenden Code in eine Databricks-Notebook-Zelle ein und führen Sie die Zelle aus, um ein Streaming-DataFrame namens `raw_df` zu erstellen:

```python
file_path = "/databricks-datasets/structured-streaming/events"
checkpoint_path = "/tmp/ss-tutorial/_checkpoint"

raw_df = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", checkpoint_path)
    .load(file_path)
)
```

Wie bei anderen Read-Operationen auf Databricks lädt die Konfiguration eines Streaming-Reads tatsächlich noch keine Daten. Es muss eine Aktion auf den Daten ausgelöst werden, bevor der Stream beginnt.

**Hinweis:** Der Aufruf von `display()` auf einem Streaming-DataFrame startet einen Streaming-Job. Für die meisten Structured-Streaming-Anwendungsfälle sollte die Aktion, die einen Stream auslöst, das Schreiben von Daten in eine Senke sein. Siehe [Produktionsüberlegungen für Structured Streaming](https://docs.databricks.com/gcp/en/structured-streaming/production).

## <a id="transformation">3. Eine Streaming-Transformation durchführen</a>

Structured Streaming unterstützt die meisten Transformationen, die auf Databricks und in Spark SQL verfügbar sind. Es lassen sich sogar MLflow-Modelle als UDFs laden und als Transformation für Streaming-Vorhersagen einsetzen.

Das folgende Code-Beispiel führt eine einfache Transformation durch, um die eingelesenen JSON-Daten mit zusätzlichen Informationen anhand von Spark-SQL-Funktionen anzureichern:

```python
from pyspark.sql.functions import col, current_timestamp

transformed_df = (raw_df.select(
    "*",
    col("_metadata.file_path").alias("source_file"),
    current_timestamp().alias("processing_time")
    )
)
```

Das resultierende `transformed_df` enthält Query-Anweisungen, um jeden Datensatz beim Eintreffen in der Datenquelle zu laden und zu transformieren.

**Hinweis:** Structured Streaming behandelt Datenquellen als unbeschränkte bzw. unendliche Datasets. Daher werden manche Transformationen in Structured-Streaming-Workloads nicht unterstützt, da sie das Sortieren einer unendlichen Anzahl von Elementen erfordern würden.

Die meisten Aggregationen und viele Joins erfordern das Verwalten von Zustandsinformationen mittels Watermarks, Fenstern und Output-Modus. Siehe [Watermarks anwenden, um Datenverarbeitungsschwellenwerte zu steuern](https://docs.databricks.com/gcp/en/structured-streaming/watermarks).

## <a id="batch-write">4. Ein inkrementelles Batch-Schreiben nach Delta Lake durchführen</a>

Das folgende Beispiel schreibt nach Delta Lake unter Angabe eines Dateipfads und eines Checkpoints.

**Wichtig:** Stellen Sie stets sicher, dass Sie für jeden konfigurierten Streaming-Writer einen eindeutigen Checkpoint-Speicherort angeben. Der Checkpoint liefert die eindeutige Identität für den Stream und verfolgt alle verarbeiteten Datensätze sowie die zugehörigen Zustandsinformationen.

Die Trigger-Einstellung `availableNow` weist Structured Streaming an, alle bislang unverarbeiteten Datensätze aus dem Quell-Dataset zu verarbeiten und sich anschließend zu beenden — der folgende Code kann daher gefahrlos ausgeführt werden, ohne dass ein Stream dauerhaft weiterläuft:

```python
target_path = "/tmp/ss-tutorial/"
checkpoint_path = "/tmp/ss-tutorial/_checkpoint"

transformed_df.writeStream
    .trigger(availableNow=True)
    .option("checkpointLocation", checkpoint_path)
    .option("path", target_path)
    .start()
```

In diesem Beispiel treffen keine neuen Datensätze in der Datenquelle ein, sodass eine wiederholte Ausführung dieses Codes keine neuen Datensätze einliest.

**Warnung:** Die Ausführung von Structured Streaming kann verhindern, dass Auto Termination die Rechenressourcen herunterfährt. Um unerwartete Kosten zu vermeiden, sollten Streaming-Queries stets beendet werden.

## <a id="delta-zu-delta">5. Daten aus Delta Lake lesen, transformieren und nach Delta Lake schreiben</a>

Delta Lake bietet umfangreiche Unterstützung für die Arbeit mit Structured Streaming sowohl als Quelle als auch als Senke. Siehe [Delta-Lake-Tabellen-Streaming-Reads und -Writes](https://docs.databricks.com/gcp/en/structured-streaming/delta-lake).

Das folgende Beispiel zeigt eine Beispielsyntax, um alle neuen Datensätze aus einer Delta-Lake-Tabelle inkrementell zu laden, sie mit einem Snapshot einer weiteren Delta-Lake-Tabelle zu joinen und in eine Delta-Lake-Tabelle zu schreiben:

```python
(spark.readStream
    .table("<table-name1>")
    .join(spark.read.table("<table-name2>"), on="<id>", how="left")
    .writeStream
    .trigger(availableNow=True)
    .option("checkpointLocation", "<checkpoint-path>")
    .toTable("<table-name3>")
)
```

Es müssen die passenden Berechtigungen konfiguriert sein, um Quelltabellen zu lesen sowie in Zieltabellen und den angegebenen Checkpoint-Speicherort zu schreiben. Alle mit spitzen Klammern (`<>`) gekennzeichneten Parameter müssen mit den relevanten Werten für die jeweiligen Datenquellen und -senken ausgefüllt werden.

**Hinweis:** Lakeflow-Pipelines bieten eine vollständig deklarative Syntax zum Erstellen von Delta-Lake-Pipelines und verwalten Eigenschaften wie Trigger und Checkpoints automatisch. Siehe [Spark Declarative Pipelines](https://docs.databricks.com/gcp/en/ldp/).

## <a id="kafka">6. Daten aus Kafka lesen, transformieren und nach Kafka schreiben</a>

Apache Kafka und andere Messaging Busse bieten für große Datasets eine der niedrigsten verfügbaren Latenzen. Databricks kann verwendet werden, um Transformationen auf aus Kafka eingelesene Daten anzuwenden und die Daten anschließend zurück nach Kafka zu schreiben.

**Hinweis:** Das Schreiben von Daten in Cloud-Objektspeicher fügt zusätzlichen Latenz-Overhead hinzu. Wer Daten aus einem Messaging Bus in Delta Lake speichern möchte, aber die niedrigstmögliche Latenz für Streaming-Workloads benötigt, sollte laut Databricks-Empfehlung separate Streaming-Jobs konfigurieren — einen, um Daten in das Lakehouse einzulesen, und einen weiteren für Near-Realtime-Transformationen für nachgelagerte Messaging-Bus-Senken.

Das folgende Code-Beispiel zeigt ein einfaches Muster, um Daten aus Kafka anzureichern, indem sie mit Daten in einer Delta-Lake-Tabelle gejoint und anschließend zurück nach Kafka geschrieben werden:

```python
(spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "<server:ip>")
    .option("subscribe", "<topic>")
    .option("startingOffsets", "latest")
    .load()
    .join(spark.read.table("<table-name>"), on="<id>", how="left")
    .writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "<server:ip>")
    .option("topic", "<topic>")
    .option("checkpointLocation", "<checkpoint-path>")
    .start()
)
```

Es müssen die passenden Berechtigungen für den Zugriff auf den jeweiligen Kafka-Dienst konfiguriert sein. Alle mit spitzen Klammern (`<>`) gekennzeichneten Parameter müssen mit den relevanten Werten für die jeweiligen Datenquellen und -senken ausgefüllt werden. Siehe [Verbindung zu Apache Kafka herstellen](https://docs.databricks.com/gcp/en/connect/streaming/kafka/).

---

## <a id="quellen">7. Quellen</a>

- Run your first Structured Streaming workload (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/tutorial
- Run your first Structured Streaming workload (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/tutorial

**Stand:** 2026-08-22.
