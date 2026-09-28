# Streaming-Daten abfragen

Databricks unterstützt Streaming-Datenabfragen über Structured Streaming in Python und Scala, mit eingeschränkter SQL-Unterstützung. SQL-Unterstützung für interaktive Abfragen auf Streaming-Daten ist auf Notebooks beschränkt, die auf All-Purpose Compute laufen.

Für Produktivumgebungen gilt: Streaming-Queries sollten nur ausgelöst werden, indem sie in eine Zieltabelle oder ein externes System geschrieben werden – nicht über Memory-Sinks zur reinen Inspektion.

## Unterstützte Quellen

Unterstützte Streaming-Quellen sind u. a. Kafka, Kinesis, Pub/Sub und Pulsar. Bei Delta-Lake-Tabellen erwarten Streaming-Queries standardmäßig, dass die Quelltabellen nur angehängte Datensätze enthalten.

## Von Kafka lesen

```python
display(spark.readStream.format("kafka").option("kafka.bootstrap.servers", "<server:ip>").option("subscribe", "<topic>").option("startingOffsets", "latest").load())
```

```sql
%sql
SELECT * FROM STREAM read_kafka(bootstrapServers => '<server:ip>', subscribe => '<topic>', startingOffsets => 'latest');
```

## Eine Tabelle als Streaming-Read abfragen

```python
display(spark.readStream.table("table_name"))
```

```sql
%sql
SELECT * FROM STREAM table_name
```

## Daten im Cloud Object Storage mit Auto Loader abfragen (Beispiel JSON)

```python
display(spark.readStream.format("cloudFiles").option("cloudFiles.format", "json").load("/Volumes/catalog/schema/volumes/path/to/files"))
```

```sql
%sql
SELECT * FROM STREAM read_files('/Volumes/catalog/schema/volumes/path/to/files', format => 'json')
```

---
**Quelle:** https://docs.databricks.com/aws/en/query/streaming  
**Stand:** 2026-08-07
