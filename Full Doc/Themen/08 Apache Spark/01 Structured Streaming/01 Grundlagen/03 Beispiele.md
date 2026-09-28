# Structured-Streaming-Muster — Referenz

Dieses Dokument enthält Notebooks und Code-Beispiele für gängige Muster bei der Arbeit mit Structured Streaming auf Databricks. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/examples`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte; die Original-GCP-Seite lieferte nur eine gerenderte Kurzfassung.

## Abschnittsübersicht
1. [Erste Schritte mit Structured Streaming](#erste-schritte)
2. [Nach Cassandra schreiben als Senke für Structured Streaming in Python](#cassandra)
3. [Nach Azure Synapse Analytics schreiben mit foreachBatch() in Python](#synapse)
4. [Nach Amazon DynamoDB schreiben mit foreach() in Scala und Python](#dynamodb)
5. [MERGE in Delta Lake über foreachBatch (Upserts aus einem Stream)](#merge-delta)
6. [Stream-Stream-Joins](#stream-stream-joins)
7. [Quellen](#quellen)

---

## <a id="erste-schritte">1. Erste Schritte mit Structured Streaming</a>

Wer ganz neu bei Structured Streaming ist, sollte zunächst [Ihren ersten Structured-Streaming-Workload ausführen](https://docs.databricks.com/gcp/en/structured-streaming/tutorial) lesen (siehe auch `Tutorial.md` in diesem Ordner).

## <a id="cassandra">2. Nach Cassandra schreiben als Senke für Structured Streaming in Python</a>

[Apache Cassandra](https://cassandra.apache.org/) ist eine verteilte, latenzarme, skalierbare, hochverfügbare OLTP-Datenbank.

Structured Streaming arbeitet mit Cassandra über den [Spark Cassandra Connector](https://github.com/datastax/spark-cassandra-connector) zusammen. Dieser Connector unterstützt sowohl die RDD- als auch die DataFrame-API und bietet native Unterstützung für das Schreiben von Streaming-Daten.

**Wichtig:** Es muss die passende Version des [spark-cassandra-connector-assembly](https://mvnrepository.com/artifact/com.datastax.spark/spark-cassandra-connector-assembly) verwendet werden.

Das folgende Beispiel stellt eine Verbindung zu einem oder mehreren Hosts in einem Cassandra-Datenbank-Cluster her. Zudem werden Verbindungskonfigurationen wie der Checkpoint-Speicherort sowie die konkreten Keyspace- und Tabellennamen angegeben:

```python
spark.conf.set("spark.cassandra.connection.host", "host1,host2")

df.writeStream \
  .format("org.apache.spark.sql.cassandra") \
  .outputMode("append") \
  .option("checkpointLocation", "/path/to/checkpoint") \
  .option("keyspace", "keyspace_name") \
  .option("table", "table_name") \
  .start()
```

## <a id="synapse">3. Nach Azure Synapse Analytics schreiben mit foreachBatch() in Python</a>

`streamingDF.writeStream.foreachBatch()` erlaubt es, bestehende Batch-Datenschreiber wiederzuverwenden, um das Ergebnis einer Streaming-Query nach Azure Synapse Analytics zu schreiben. Siehe die [foreachBatch-Dokumentation](https://docs.databricks.com/gcp/en/structured-streaming/foreach) für Details.

Um dieses Beispiel auszuführen, wird der Azure-Synapse-Analytics-Connector benötigt. Details zum Azure-Synapse-Analytics-Connector finden sich unter [Daten in Azure Synapse Analytics abfragen](https://docs.databricks.com/gcp/en/archive/connectors/synapse-analytics).

```python
from pyspark.sql.functions import *
from pyspark.sql import *

def writeToSQLWarehouse(df, epochId):
  df.write \
    .format("com.databricks.spark.sqldw") \
    .mode('overwrite') \
    .option("url", "jdbc:sqlserver://<the-rest-of-the-connection-string>") \
    .option("forward_spark_azure_storage_credentials", "true") \
    .option("dbtable", "my_table_in_dw_copy") \
    .option("tempdir", "wasbs://<your-container-name>@<your-storage-account-name>.blob.core.windows.net/<your-directory-name>") \
    .save()

spark.conf.set("spark.sql.shuffle.partitions", "1")

query = (
  spark.readStream.format("rate").load()
    .selectExpr("value % 10 as key")
    .groupBy("key")
    .count()
    .toDF("key", "count")
    .writeStream
    .foreachBatch(writeToSQLWarehouse)
    .outputMode("update")
    .start()
    )
```

## <a id="dynamodb">4. Nach Amazon DynamoDB schreiben mit foreach() in Scala und Python</a>

> Aus der AWS-Doku ergänzt; dieser Abschnitt fehlt in der GCP- und Azure-Fassung.

`streamingDF.writeStream.foreach()` schreibt die Ausgabe einer Streaming-Query an beliebige Ziele.

### Python

Das Beispiel nutzt `streamingDataFrame.writeStream.foreach()`, um nach DynamoDB zu schreiben. Im ersten Schritt wird die DynamoDB-boto-Ressource geholt. Das Beispiel verwendet `access_key` und `secret_key`; **Databricks empfiehlt stattdessen Instance Profiles** (siehe „Tutorial: Configure S3 access with an instance profile“).

**Schritt 1:** Hilfsmethoden, um eine DynamoDB-Tabelle für das Beispiel anzulegen:

```python
table_name = "PythonForeachTest"

def get_dynamodb():
  import boto3

  access_key = "<access key>"
  secret_key = "<secret key>"
  region = "<region name>"
  return boto3.resource('dynamodb',
                 aws_access_key_id=access_key,
                 aws_secret_access_key=secret_key,
                 region_name=region)

def createTableIfNotExists():
    '''
    Create a DynamoDB table if it does not exist.
    This must be run on the Spark driver, and not inside foreach.
    '''
    dynamodb = get_dynamodb()

    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    if table_name not in existing_tables:
      print("Creating table %s" % table_name)
      table = dynamodb.create_table(
          TableName=table_name,
          KeySchema=[ { 'AttributeName': 'key', 'KeyType': 'HASH' } ],
          AttributeDefinitions=[ { 'AttributeName': 'key', 'AttributeType': 'S' } ],
          ProvisionedThroughput = { 'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5 }
      )

      print("Waiting for table to be ready")

table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
```

**Schritt 2:** Klassen und Methoden definieren, die nach DynamoDB schreiben, und sie aus `foreach` aufrufen. Dafür gibt es zwei Wege:

- **Funktion:** der einfache Weg, schreibt eine Zeile pro Aufruf. Allerdings wird der Client bzw. die Verbindung **bei jedem Aufruf** neu initialisiert.

```python
def sendToDynamoDB_simple(row):
  '''
  Function to send a row to DynamoDB.
  When used with `foreach`, this method is going to be called in the executor
  with the generated output rows.
  '''
  # Create client object in the executor,
  # do not use client objects created in the driver
  dynamodb = get_dynamodb()

  dynamodb.Table(table_name).put_item(
      Item = { 'key': str(row['key']), 'count': row['count'] })
```

- **Klasse mit `open`, `process` und `close`:** effizienter, weil ein Client bzw. eine Verbindung einmal initialisiert wird und mehrere Zeilen schreiben kann.

```python
class SendToDynamoDB_ForeachWriter:
  '''
  Class to send a set of rows to DynamoDB.
  When used with `foreach`, copies of this class is going to be used to write
  multiple rows in the executor. See the python docs for `DataStreamWriter.foreach`
  for more details.
  '''

  def open(self, partition_id, epoch_id):
    # This is called first when preparing to send multiple rows.
    # Put all the initialization code inside open() so that a fresh
    # copy of this class is initialized in the executor where open()
    # will be called.
    self.dynamodb = get_dynamodb()
    return True

  def process(self, row):
    # This is called for each row after open() has been called.
    # This implementation sends one row at a time.
    # For further enhancements, contact the Spark+DynamoDB connector
    # team: https://github.com/audienceproject/spark-dynamodb
    self.dynamodb.Table(table_name).put_item(
        Item = { 'key': str(row['key']), 'count': row['count'] })

  def close(self, err):
    # This is called after all the rows have been processed.
    if err:
      raise err
```

**Schritt 3:** `foreach` in der Streaming-Query mit der Funktion oder dem Objekt aufrufen:

```python
from pyspark.sql.functions import *

spark.conf.set("spark.sql.shuffle.partitions", "1")

query = (
  spark.readStream.format("rate").load()
    .selectExpr("value % 10 as key")
    .groupBy("key")
    .count()
    .toDF("key", "count")
    .writeStream
    .foreach(SendToDynamoDB_ForeachWriter())
    #.foreach(sendToDynamoDB_simple)  // alternative, use one or the other
    .outputMode("update")
    .start()
)
```

### Scala

Das Beispiel nutzt `streamingDataFrame.writeStream.foreach()` in Scala. Voraussetzung: eine DynamoDB-Tabelle mit einem einzelnen String-Key namens `"value"`.

**Schritt 1:** Eine Implementierung des Interface `ForeachWriter` definieren, die den Schreibvorgang ausführt:

```scala
import org.apache.spark.sql.{ForeachWriter, Row}
import com.amazonaws.AmazonServiceException
import com.amazonaws.auth._
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder
import com.amazonaws.services.dynamodbv2.model.AttributeValue
import com.amazonaws.services.dynamodbv2.model.ResourceNotFoundException
import java.util.ArrayList

import scala.collection.JavaConverters._

class DynamoDbWriter extends ForeachWriter[Row] {
  private val tableName = "<table name>"
  private val accessKey = "<aws access key>"
  private val secretKey = "<aws secret key>"
  private val regionName = "<region>"

  // This will lazily be initialized only when open() is called
  lazy val ddb = AmazonDynamoDBClientBuilder.standard()
    .withCredentials(new AWSStaticCredentialsProvider(new BasicAWSCredentials(accessKey, secretKey)))
    .withRegion(regionName)
    .build()

  //
  // This is called first when preparing to send multiple rows.
  // Put all the initialization code inside open() so that a fresh
  // copy of this class is initialized in the executor where open()
  // will be called.
  //
  def open(partitionId: Long, epochId: Long) = {
    ddb  // force the initialization of the client
    true
  }

  //
  // This is called for each row after open() has been called.
  // This implementation sends one row at a time.
  // A more efficient implementation can be to send batches of rows at a time.
  //
  def process(row: Row) = {
    val rowAsMap = row.getValuesMap(row.schema.fieldNames)
    val dynamoItem = rowAsMap.mapValues {
      v: Any => new AttributeValue(v.toString)
    }.asJava

    ddb.putItem(tableName, dynamoItem)
  }

  //
  // This is called after all the rows have been processed.
  //
  def close(errorOrNull: Throwable) = {
    ddb.shutdown()
  }
}
```

**Schritt 2:** Mit dem `DynamoDbWriter` einen Rate-Stream nach DynamoDB schreiben:

```scala
spark.readStream
  .format("rate")
  .load()
  .select("value")
  .writeStream
  .foreach(new DynamoDbWriter)
  .start()
```

---

## <a id="merge-delta">5. MERGE in Delta Lake über foreachBatch (Upserts aus einem Stream)</a>

Ein reguläres `MERGE` wird von Structured Streaming nicht direkt unterstützt, da Streaming-Writer keine beliebige Upsert-Logik ausführen können. Über `foreachBatch()` lässt sich `MERGE` dennoch pro Mikro-Batch anwenden — nützlich für:

- effizientere Schreibvorgänge über `update`-Output-Mode statt vollständiger Neuschreibung im `complete`-Modus,
- fortlaufendes Anwenden eines Change-Streams per Merge-Query,
- automatische Deduplizierung während der Stream-Verarbeitung über insert-only Merge-Operationen.

**Variante 1 — SQL-`MERGE` via Temp View (Python):**

```python
def upsertToDelta(microBatchOutputDF, batchId):
  microBatchOutputDF.createOrReplaceTempView("updates")
  microBatchOutputDF.sparkSession.sql("""
    MERGE INTO aggregates t
    USING updates s
    ON s.key = t.key
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
  """)

(streamingAggregatesDF.writeStream
  .foreachBatch(upsertToDelta)
  .outputMode("update")
  .start())
```

**Variante 2 — Delta-API (`DeltaTable.merge`, Python):**

```python
from delta.tables import *
deltaTable = DeltaTable.forName(spark, "table_name")

def upsertToDelta(microBatchOutputDF, batchId):
  (deltaTable.alias("t").merge(
      microBatchOutputDF.alias("s"), "s.key = t.key")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute())

(streamingAggregatesDF.writeStream
  .foreachBatch(upsertToDelta)
  .outputMode("update")
  .start())
```

Beide Varianten funktionieren analog in Scala (`microBatchOutputDF: DataFrame, batchId: Long`, `deltaTable.as("t")` statt `.alias("t")`).

### Idempotente Schreibvorgänge: `txnAppId` und `txnVersion`

Schreibt `foreachBatch` auf mehrere Senken, sollte jeder einzelne Schreibvorgang idempotent sein — nach einem Abbruch kann derselbe Batch erneut angewendet werden, ohne Duplikate zu erzeugen. Dafür bietet der `DataFrameWriter` zwei Optionen:

- **`txnAppId`**: eindeutige Kennung, z. B. die StreamingQuery-ID oder ein selbst vergebener String.
- **`txnVersion`**: ein monoton steigender Zähler als Transaktionsversion (typischerweise die `batchId`).

Delta Lake nutzt beide Parameter, um doppelte Schreibvorgänge zu erkennen und zu unterdrücken.

```python
app_id = ...  # eindeutige Anwendungskennung

def writeToDeltaLakeTableIdempotent(batch_df, batch_id):
  batch_df.write.format(...).option("txnVersion", batch_id).option("txnAppId", app_id).save(...)  # Ziel 1
  batch_df.write.format(...).option("txnVersion", batch_id).option("txnAppId", app_id).save(...)  # Ziel 2

streamingDF.writeStream.foreachBatch(writeToDeltaLakeTableIdempotent).start()
```

### Wichtige Hinweise

- **Idempotenz ist Pflicht:** Das `MERGE`-Statement in `foreachBatch` muss idempotent sein, da Neustarts denselben Batch erneut anwenden können.
- **Checkpoint-Wechsel:** Wird der Streaming-Checkpoint gelöscht und die Query mit neuem Checkpoint neu gestartet, muss eine andere `txnAppId` vergeben werden — ein neuer Checkpoint beginnt wieder bei Batch-ID 0, und Delta nutzt Batch-ID plus `txnAppId` als eindeutigen Bezeichner.
- **Verzerrte Metriken:** Da `merge` Daten wiederholt liest, können die Input-Data-Rate-Metriken ein Vielfaches der tatsächlichen Rate anzeigen. Abhilfe: den Batch-DataFrame vor dem Merge cachen und danach wieder uncachen.
- **Alternative Architektur:** Bei mehreren Senken empfiehlt Databricks eher einen separaten Streaming-Write pro Senke statt mehrerer Schreibvorgänge innerhalb eines `foreachBatch` — Letzteres serialisiert die Schreibvorgänge und reduziert dadurch Parallelisierung sowie Latenz.

Quelle: https://docs.databricks.com/aws/en/structured-streaming/delta-lake#merge-in-streaming

## <a id="stream-stream-joins">6. Stream-Stream-Joins</a>

Die folgenden zwei Notebooks zeigen, wie sich Stream-Stream-Joins in Python und Scala verwenden lassen.

**Stream-Stream-Joins Python-Notebook:** [Notebook abrufen](https://docs.databricks.com/notebooks/source/stream-stream-joins-python.html)

**Stream-Stream-Joins Scala-Notebook:** [Notebook abrufen](https://docs.databricks.com/notebooks/source/stream-stream-joins-scala.html)

---

## <a id="quellen">7. Quellen</a>

- Structured Streaming patterns / examples (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/examples
- Structured Streaming patterns on Azure Databricks (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/examples
- Structured Streaming und Delta Lake, Abschnitt „Perform MERGE outside foreachBatch" / „merge-in-streaming": https://docs.databricks.com/aws/en/structured-streaming/delta-lake#merge-in-streaming

**Stand:** 2026-08-22; Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
