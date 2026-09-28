

Databricks empfiehlt, wann immer möglich native Funktionen zu verwenden. UDFs sind zwar eine großartige Möglichkeit, die Funktionalität von Spark SQL zu erweitern, ihre Verwendung erfordert jedoch die **Übertragung von Daten zwischen Python und Spark**, was wiederum eine **Serialisierung** erfordert. **Dies verlangsamt Abfragen erheblich.**

Manchmal sind UDFs jedoch notwendig. **Sie können ein besonders leistungsfähiges Werkzeug für ML- oder NLP-Anwendungsfälle sein, für die es möglicherweise keine native Spark-Entsprechung gibt.**

Zwei Arten von Python-UDFs: 

- Rechenintensive Python-UDF
- Parallelisierung einer Python-UDF durch Repartitionierung



```python
# Das Deaktivieren des Disk Cachings verhindert, dass Databricks Cloud-Storage-Dateien 
# nach der ersten Abfrage speichert. Dadurch wird die Wirkung der Optimierungen deutlicher, 
# da sichergestellt wird, dass Dateien bei jeder Abfrage stets aus dem Cloud Storage geladen 
# werden.

# Dieser Befehl funktioniert nicht mit Serverless sondern mit Classic Compute:
spark.conf.set('spark.databricks.io.cache.enabled', False)
```

```python
#'device_data' Tabelle mit Telemetriedaten, die Temperaturmesswerte erzeugen.

from pyspark.sql.functions import *

spark.sql('DROP TABLE IF EXISTS device_data')

df = (spark
      .range(0, 60, 1, 1)
      .select(
          'id',
          (col('id') % 1000).alias('device_id'),
          (rand() * 100).alias('temperature_F')
      )
      .write
      .saveAsTable('device_data')
)
```



```python
# Rechenintensive Python-UDF: Zu Experimentierzwecken implementieren wir eine Funktion, die 
# Fahrenheit in Celsius umrechnet. Beachten Sie, dass wir eine Verzögerung von einer Sekunde 
# einfügen, um einen rechenintensiven Vorgang innerhalb unserer UDF zu simulieren. Probieren 
# wir es aus.

from pyspark.sql.functions import *
from pyspark.sql.types import *
import time

## Python-UDF erstellen
@udf("double")
def F_to_Celsius(f):
    # Rechzeitsimulation: 1 Sekunde pro Zeile
    time.sleep(1)
    return (f - 32) * (5/9)

spark.sql('DROP TABLE IF EXISTS celsius')

celsius_df = (spark
              .table('device_data')
              # .repartition(4) # Repartitionierung mit 4 Kerne in Ihrem Cluster
              .withColumn("celsius", F_to_Celsius(col('temperature_F')))
            )

## Tabelle erstellen
(celsius_df
 .write
 .mode('overwrite')
 .saveAsTable('celsius')
)
```

Führen Sie den Code aus, um zu sehen, wie viele Partitionen für die Abfrage verwendet wurden. Beachten Sie, dass nur **1 Partition** verwendet wurde, da die UDF die Möglichkeiten der parallelen Verarbeitung von Spark nicht nutzt, was die Abfrage verlangsamt.

```python
print(f'Total number of cores across all executors in the cluster: {spark.sparkContext.defaultParallelism}')
print(f'The number of partitions in the underlying RDD of a dataframe: {celsius_df.rdd.getNumPartitions()}')
```

Erklären Sie den Spark-Ausführungsplan. Beachten Sie, dass die Phase **BatchEvalPython** darauf hinweist, dass eine Python-UDF verwendet wird.

```python
celsius_df.explain()
```

#### Zusammenfassung
Das dauerte etwa eine Minute, was überraschend ist, da wir etwa 60 Sekunden Rechenzeit haben, die auf mehrere Kerne verteilt werden. Sollte es nicht deutlich weniger Zeit in Anspruch nehmen?

Die Antwort auf diese Frage lautet: Ja, es sollte weniger Zeit in Anspruch nehmen. Das Problem hier ist, dass Spark nicht weiß, dass die Berechnungen aufwendig sind, sodass die Arbeit nicht in Tasks aufgeteilt wurde, die parallel ausgeführt werden können. Wir können dies daran erkennen, dass während der Ausführung der Zelle nur eine einzige Aufgabe abgearbeitet wird, sowie durch einen Blick in die Spark UI.

### D2. Parallelisierung einer Python-UDF durch Repartitionierung

**Repartitionierung** ist in diesem Fall die Lösung. *Wir* wissen, dass diese Berechnung aufwendig ist und alle 4 Kerne nutzen sollte, daher können wir das DataFrame explizit repartitionieren:

```python
# Repartitionierung entsprechend der Anzahl der Kerne in Ihrem Cluster
num_cores = 4

@udf("double")
def F_to_Celsius(f):
    # Nehmen wir an, dass eine ausgefeilte Berechnung eine Sekunde pro Zeile benötigt
    time.sleep(1)
    return (f - 32) * (5/9)

spark.sql('DROP TABLE IF EXISTS celsius')

celsius_df_cores = (spark.table('device_data')
                    .repartition(num_cores) # <-- HIER
                    .withColumn("celsius", F_to_Celsius(col('temperature_F')))
             )

(celsius_df_cores
 .write
 .mode('overwrite')
 .saveAsTable('celsius')
)
```

Führen Sie den Code aus, um zu sehen, wie viele Partitionen für die Abfrage verwendet werden. Beachten Sie, dass 4 Partitionen (Tasks) verwendet werden, um den Code parallel auszuführen.

```python
print(f'Total number of cores across all executors in the cluster: {spark.sparkContext.defaultParallelism}')
print(f'The number of partitions in the underlying RDD of a dataframe: {celsius_df_cores.rdd.getNumPartitions()}')
```

#### Zusammenfassung
Der repartition-Befehl ist eine empfohlene Best Practice, um sicherzustellen, dass Ihre UDF parallel und verteilt ausgeführt wird.

## E. SQL-UDFs

Die Möglichkeit, benutzerdefinierte Funktionen in Python und Scala zu erstellen, ist praktisch, da sie es Ihnen erlaubt, die Funktionalität in der Sprache Ihrer Wahl zu erweitern. Im Hinblick auf die Optimierung ist es jedoch wichtig zu wissen, dass SQL in der Regel die beste Wahl ist, und zwar aus mehreren Gründen:
- SQL-UDFs erfordern weniger Datenserialisierung
- Der Catalyst-Optimizer kann innerhalb von SQL-UDFs arbeiten

Lassen Sie uns dies nun in der Praxis sehen, indem wir die Performance einer SQL-UDF mit ihrem Python-Pendant vergleichen.

Definieren wir zunächst die zuvor verwendete Python-UDF neu, diesmal ohne die Verzögerung, damit wir die reine Performance vergleichen können.

Nun führen wir den entsprechenden Vorgang mithilfe einer SQL-UDF durch.

```sql
%sql

-- Dieselbe Funktion erstellen
DROP FUNCTION IF EXISTS farh_to_cels;

CREATE FUNCTION farh_to_cels (farh DOUBLE)
  RETURNS DOUBLE RETURN ((farh - 32) * 5/9);

-- Die Funktion verwenden, um die Tabelle zu erstellen
DROP TABLE IF EXISTS celsius_sql;

CREATE OR REPLACE TABLE celsius_sql AS
SELECT farh_to_cels(temperature_F) as Farh_to_cels_convert 
FROM device_data;

-- Die Daten anzeigen
SELECT * 
FROM celsius_sql LIMIT 10;
```

Erklären Sie den Abfrageplan mit der SQL-UDF. Beachten Sie, dass die SQL-UDF vollständig von Photon unterstützt wird und leistungsfähiger ist.

```sql
%sql
EXPLAIN 
SELECT farh_to_cels(temperature_F) as Farh_to_cels_convert 
FROM device_data
```

## Zusammenfassung

Die tatsächlichen Zeiten hängen von einer Reihe von Faktoren ab, im Durchschnitt schneidet die SQL-UDF jedoch besser ab als ihr Python-Pendant — oft sogar deutlich besser. Der Grund dafür ist, dass SQL-UDFs die integrierten APIs und Funktionen von Spark nutzen, anstatt sich auf externe Abhängigkeiten oder Python-UDFs zu verlassen.

Wenn Sie eine UDF in Ihrem Spark-Job verwenden, führt eine Umgestaltung Ihres Codes zur Nutzung nativer Spark-APIs oder -Funktionen, wo immer möglich, zu den besten Leistungs- und Effizienzgewinnen.

Wenn Sie aufgrund starker Abhängigkeiten von externen Bibliotheken UDFs verwenden müssen, sollten Sie Ihren Code parallelisieren und Ihr DataFrame entsprechend der Anzahl der CPU-Kerne in Ihrem Cluster repartitionieren, um den bestmöglichen Grad an Parallelisierung zu erreichen.

Ziehen Sie bei der Verwendung von Python-UDFs in Betracht, stattdessen mit **Apache Arrow** optimierte Python-UDFs zu verwenden, da diese den Datenaustausch zwischen der Spark-Runtime und dem UDF-Prozess effizienter gestalten. [Erfahren Sie mehr über Arrow-optimierte Python-UDFs](https://www.databricks.com/blog/arrow-optimized-python-udfs-apache-sparktm-35).

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
