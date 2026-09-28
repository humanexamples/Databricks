

  

Bevor Sie Zellen in diesem Notebook ausführen, wählen Sie bitte Ihren Classic Compute-Cluster im Lab aus. 

```python
# Das Deaktivieren des Disk Cachings verhindert, dass Databricks Cloud-Storage-Dateien 
# nach der ersten Abfrage speichert. Dadurch wird die Wirkung der Optimierungen deutlicher, 
# da sichergestellt wird, dass Dateien bei jeder Abfrage stets aus dem Cloud Storage geladen 
# werden.
# Dieser Befehl funktioniert nicht mit Serverless sondern mit Classic Compute:
spark.conf.set('spark.databricks.io.cache.enabled', False)
```

```python
from pyspark.sql.functions import *

# Lassen Sie uns einige fiktive IoT-Daten generieren. Zunächst erzeugen wir 
# nur 2.500 Zeilen.
df = (spark
      .range(0, 2500)
      .select(
          hash('id').alias('id'), # IDs leicht randomisieren
          rand().alias('value'),
          from_unixtime(lit(1701692381 + col('id'))).alias('time') 
      ))

display(df.limit(5))
```

```python
# Jetzt schreiben wir die Daten in eine nach **id** partitionierte Tabelle (2.500 
# unterschiedliche Werte), was dazu führt, dass jede Zeile in einen eigenen Ordner 
# für die jeweilige Partition geschrieben wird
# **HINWEIS:** Die Erstellung der Tabelle mit 2.500 Partitionen dauert etwa 1-2 Minuten.
spark.sql('DROP TABLE IF EXISTS iot_data_partitioned')

(df
 .write
 .mode('overwrite')
 .option("overwriteSchema", "true")
 .partitionBy('id')
 .saveAsTable("iot_data_partitioned")
)
```

```sql
-- Bestätigen Sie Folgendes:
-- In der Spalte **operationParameters** ist die Tabelle nach **id** partitioniert.
-- In der Spalte **operationMetrics** enthält die Tabelle 2.500 Dateien, eine 
-- Parquet-Datei für jede eindeutige partitionierte **id**.
DESCRIBE HISTORY iot_data_partitioned;
```

```python
# Mit der Anweisung `SHOW PARTITIONS` können Sie alle Partitionen einer Tabelle auflisten. 
# Führen Sie den Code aus und sehen Sie sich die Ergebnisse an. Beachten Sie, dass die 
# Tabelle nach **id** partitioniert ist und 2.500 Zeilen enthält.
spark.sql("SHOW PARTITIONS iot_data_partitioned").limit(5).display();

display(spark.sql("SHOW PARTITIONS iot_data_partitioned").count());
```

# Abfrage der Tabelle
```sql
-- Query 1: Filterung nach der partitionierten Spalte. 
-- HINWEIS: (1-2 Sekunden Ausführungszeit)
SELECT * FROM iot_data_partitioned WHERE id = 519220707;
```

| Metric    | Value    | Note    |
|-------------|-------------|-------------|
| cloud storage request count| 1| Bezieht sich auf die Anzahl der Requests, die während der Job-Ausführung an Cloud-Storage-Systeme wie S3, Azure Blob oder Google Cloud Storage gestellt werden. Dies kann mehrere Operationen umfassen, wie das Lesen von Metadaten, den Zugriff auf Verzeichnisse oder das Abrufen der eigentlichen Daten. |
| cloud storage response size| 880.0B| Gibt die Gesamtmenge der Daten an, die während der Ausführung eines Jobs vom Cloud Storage zu Spark übertragen wurden. Es liefert Einblicke in die I/O-Performance sowie mögliche Engpässe beim Datentransfer. |
| files pruned | 2.499 |Gibt die Anzahl der Dateien an, die Spark während der Job-Ausführung übersprungen bzw. ignoriert hat. Insgesamt wurden 2.499 Dateien von Spark aufgrund von Pruning basierend auf der Filterung nach **id** übersprungen. Dies liegt daran, dass die Tabelle nach **id** partitioniert ist.|
| files read | 1 | Gibt die Anzahl der Dateien an, die Spark während der Job-Ausführung tatsächlich gelesen hat. Es wurde nur 1 Datei gelesen, da die Abfrage auf der partitionierten Spalte **id** ausgeführt wurde. Spark muss basierend auf der Abfrage nur die notwendige(n) Partition(en) lesen. |

 



```sql
-- Query 2 - Filterung nach einer nicht partitionierten Spalte 
-- **HINWEIS:** (1-2 Sekunden Ausführungszeit)
SELECT avg(value) 
FROM iot_data_partitioned 
WHERE time >= "2023-12-04 12:19:00" AND
      time <= "2023-12-04 13:01:20";
```

| Metric    | Value    | Note    |
|-------------|-------------|-------------|
| cloud storage request count total (min, med, max)| 2500 (21, 37, 37)| Min, Median und Max stellen die Zusammenfassung der von Tasks bzw. Executors gestellten Requests dar. Die Verteilung ist über die Tasks bzw. Executors hinweg recht gleichmäßig, und es gibt keine große Varianz bei der Anzahl der von jedem Task gestellten Cloud-Storage-Requests. |
| cloud storage response size total (min, med, max) | 2.1 MiB (18.0 KiB, 31.8 KiB, 31.8 KiB)| Gibt die Gesamtmenge der Daten an, die während der Ausführung eines Jobs vom Cloud Storage zu Spark übertragen wurden. Min, Median,Max zeigen ein relativ konsistentes und gleichmäßiges Datentransfermuster über die Tasks hinweg hindeutet. |
| files pruned | 0 |Insgesamt wurden 0 Dateien von Spark aufgrund von Pruning basierend auf den Filtern der Abfrage übersprungen.|
| files read | 2.500 | Während der Ausführung des Spark-Jobs wurden 2.500 Dateien gelesen. Da die Daten nach **id** partitioniert, aber nach der Spalte **time** abgefragt wurden, musste Spark alle Dateien lesen. |

## Behebung des Problems

```python
from pyspark.sql.functions import *

# Jetzt erhöhen wir das Volumen drastisch, indem wir 50.000.000 Zeilen verwenden.
df = (spark
      .range(0,50000000, 1, 32)
      .select(
          hash('id').alias('id'), # IDs leicht randomisieren
          rand().alias('value'),
          from_unixtime(lit(1701692381 + col('id'))).alias('time') 
      )
    )

spark.sql('DROP TABLE IF EXISTS iot_data')

# Jetzt erstellen wir eine Tabelle namens **iot_data**, um die Daten zu erfassen, 
# **diesmal ohne Partitionierung**. Auf diese Weise erreichen wir Folgendes:
# 1. Die Ausführung dauert kürzer, selbst bei größeren Datensätzen, da wir keine hohe Anzahl 
#    an Tabellenpartitionen erstellen.
# 2. Es werden weniger Dateien geschrieben (32 Dateien für 50.000.000 Zeilen gegenüber 2.500 
#    Dateien für 2.500 Zeilen in der partitionierten Tabelle).
# 3. Das Schreiben ist schneller als bei der Partitionierung auf Festplattenebene, da sich 
#    alle Dateien in einem Verzeichnis befinden, anstatt 2.500 Verzeichnisse zu erstellen.
# 4. Abfragen nach einer **id** dauern etwa so lange wie zuvor.
# 5. Filterungen nach der Spalte **time** sind deutlich schneller, da nur ein Verzeichnis 
#    abgefragt werden muss.
(df
 .write
 .option("overwriteSchema", "true")
 .mode('overwrite')
 .saveAsTable("iot_data")
)
```

```sql
-- Bestätigen Sie Folgendes:
-- In der Spalte **operationParameters**, bestätigen Sie, dass die Tabelle nicht 
-- partitioniert ist.
-- In der Spalte **operationMetrics**, bestätigen Sie, dass die Tabelle insgesamt 32 
-- Dateien enthält.
DESCRIBE HISTORY iot_data;
```

## Optimierung validieren
```sql
SELECT * FROM iot_data WHERE id = 519220707
```

| Metric    | Value    | Note    |
|-------------|-------------|-------------|
| cloud storage request count total (min, med, max)| 65 (8, 8, 9)| Vorher: 1      |
| cloud storage response size total (min, med, max)| 216.9 MiB (24.8 MiB, 24.8 MiB, 43.0 MiB)| Vorher: 880.0B |
| files pruned | 0 | Vorher: 2.499  |
| files read | 32| Vorher: 1 |





```sql
%sql
SELECT avg(value) 
FROM iot_data 
WHERE time >= "2023-12-04 12:19:00" AND 
      time <= "2023-12-04 13:01:20";
```

| Metric    | Value    | Note    |
|-------------|-------------|-------------|
| cloud storage request count| 3| Vorher: 2500 (21, 37, 37) |
| cloud storage response size| 	18.4 MiB| Vorher: 2.1 MiB (18.0 KiB, 31.8 KiB, 31.8 KiB) |
| files pruned | 31 | Vorher: 0                                      |
| files read | 1 | Vorher: 2500 |
