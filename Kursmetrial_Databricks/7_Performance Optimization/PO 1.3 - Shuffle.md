

Demo:  Shuffle

Shuffle ist ein Spark-Mechanismus, der Daten so umverteilt, dass sie unterschiedlich über die **Partitionen** gruppiert werden. Dies beinhaltet typischerweise das Kopieren von Daten über Executors und Maschinen hinweg und kann, obwohl manchmal notwendig, eine komplexe und teure Operation sein.

Ein Shuffle bezeichnet den Prozess der Umverteilung von Daten über verschiedene Nodes/Partitionen hinweg. Dies ist notwendig für Operationen wie Joins, bei denen Daten aus zwei oder mehr Datensätzen basierend auf einem Schlüssel kombiniert werden müssen, die relevanten Zeilen sich aber möglicherweise nicht in derselben Partition befinden.

**Broadcast Join** vermeidet das Shuffle.

Auch **Aggregationen** verwenden ein Shuffle.

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
## 'transactions' Tabelle erstellen:

from pyspark.sql.functions import *

## Tabelle löschen, falls sie bereits existiert
spark.sql('DROP TABLE IF EXISTS transactions')

## Spark DataFrame erstellen und als Tabelle speichern
## Die Tabelle wird *150.000.000* Zeilen enthalten.
(spark
 .range(0, 150000000, 1, 32)
 .select(
    'id',
    round(rand() * 10000, 2).alias('amount'),
    (col('id') % 10).alias('country_id'),
    (col('id') % 100).alias('store_id')
 )
 .write
 .mode('overwrite')
 .saveAsTable('transactions')
)
```

```python
## 'stores' Tabelle erstellen:

## Tabelle löschen, falls sie bereits existiert
spark.sql('DROP TABLE IF EXISTS stores')

## Spark DataFrame erstellen
(spark
 .range(0, 99)
 .select(
    'id',
    round(rand() * 100, 0).alias('employees'),
    (col('id') % 10).alias('country_id'),
    expr('uuid()').alias('name')
    )
 .write
 .mode('overwrite')
 .saveAsTable('stores')
)
```

```python
## 'countries-Lookup' Tabelle erstellen:

## Tabelle löschen, falls sie bereits existiert
spark.sql('DROP TABLE IF EXISTS countries')

## Daten erstellen
countries = [(0, "Italy"),(1, "Canada"),(2, "Mexico"),(3, "China"),(4, "Germany"),(5, "UK"),(6, "Japan"),(7, "Korea"),(8, "Australia"),(9, "France"),(10, "Spain"),(11, "USA")]

columns = ["id", "name"]

## Spark DataFrame und countries-Tabelle erstellen
countries_df = (spark
                .createDataFrame(data = countries, schema = columns)
                .write
                .mode('overwrite')
                .saveAsTable("countries")
            )
```

# Joins ohne Broadcast Join

Nun führen wir eine Abfrage aus, die durch das Zusammenführen dreier Tabellen ein Shuffle auslöst, und schreiben die Ergebnisse in eine separate Tabelle.

Diese Optionen legen automatisch fest, wann ein **Broadcast Join** verwendet werden soll, basierend auf der Größe des kleineren DataFrames (bzw. der kleineren Tabelle) im Join.

Führen Sie die untenstehende Zelle aus, um die Standardwerte des Broadcast Joins und der **Adaptive Query Execution (AQE)**-Konfigurationen anzuzeigen. Beachten Sie, dass:
- Der Standardwert für eine Tabelle mit einem Broadcast Join **10.485.760 Bytes** beträgt.
- Falls AQE aktiviert ist, beträgt der Wert für den Broadcast Join **31.457.280 Bytes**.
- AQE ist standardmäßig aktiviert.

```python
# Default value of autoBroadcastJoinThreshold:
print(spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))

# Default value of adaptive.autoBroadcastJoinThreshold:
print(spark.conf.get("spark.databricks.adaptive.autoBroadcastJoinThreshold"))

# Anzeigen, ob AQE aktiviert ist:
print(spark.conf.get("spark.sql.adaptive.enabled"))
```

```python
# In dieser Zelle deaktivieren wir Broadcast Joins explizit, um ein Shuffle zu demonstrieren 
# und Ihnen zu zeigen, wie Sie die Query-Performance untersuchen und verbessern können. 

# Den automatischen Broadcast Join vollständig deaktivieren. Das heißt, Spark wird für Joins 
# niemals ein Dataset broadcasten, unabhängig von dessen Größe.
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)

# Die Broadcast-Join-Funktion unter AQE deaktivieren, sodass Spark auch bei aktivierter Adaptive Query Execution nicht versucht, die kleinere Seite eines Joins zu broadcasten.
spark.conf.set("spark.databricks.adaptive.autoBroadcastJoinThreshold", -1)

# Current value of autoBroadcastJoinThreshold:
print(spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))
# Current value of adaptive.autoBroadcastJoinThreshold:
print(spark.conf.get("spark.databricks.adaptive.autoBroadcastJoinThreshold"))
```

Führen Sie den Join von **transactions**, **stores** und **countries** durch, um eine Tabelle namens **transact_countries** zu erstellen, ohne Broadcast Joins zu verwenden. Beachten Sie, dass die Ausführung dieser Abfrage etwa ~1 Minute dauert.

```python
joined_df_no_broadcast = spark.sql("""
    SELECT 
        transactions.id,
        amount,
        countries.name as country_name,
        employees,
        stores.name as store_name
    FROM
        transactions
    LEFT JOIN
        stores
        ON
            transactions.store_id = stores.id
    LEFT JOIN
        countries
        ON
            transactions.country_id = countries.id
""")

## Eine Tabelle mit den zusammengeführten Daten erstellen
(joined_df_no_broadcast
 .write
 .mode('overwrite')
 .saveAsTable('transact_countries')
)
```

Öffnen Sie die Spark UI auf der Stages-Seite und beachten Sie, dass es zwei große Shuffles von Daten mit **1,4 GB** gab. 

Um den Query-DAG anzuzeigen, führen Sie die folgenden Schritte aus:

1. Erweitern Sie in der obigen Zelle **Spark Jobs**.

2. Klicken Sie im zweiten Job mit der rechten Maustaste auf **View** und wählen Sie *Open in a New Tab*.

**HINWEIS:** In der Vocareum-Lab-Umgebung wird ein Fehler angezeigt, wenn Sie auf **View** klicken, ohne es in einem neuen Tab zu öffnen.

3. Klicken Sie auf den Link **Stages** in der oberen Navigationsleiste. Beachten Sie, dass es in den Stages dieser spezifischen Abfrage sehr große **Shuffle Read**- und **Shuffle Write**-Operationen gab.



4. Wählen Sie als Nächstes in der Tabelle **Completed Stages** den Link (**mapPartitionsInternal at...**) in der Spalte **Description** für die Zeile mit den großen **Shuffle Read**- und **Shuffle Write**-Werten sowie den Link **Jobs** in der oberen Navigationsleiste. Im obigen Bild wäre das beispielsweise Zeile **151**.

5. Wählen Sie dann den Zahlenlink in der Tabelle oben unter **Associated Job ID**. Klicken Sie anschließend auf die Zahl unter **Associated SQL Query**. Dort können Sie den gesamten Query-Plan (DAG) einsehen.

![1.3-non_broadcastjoin_dag.png](./Includes/images/1.3-non_broadcastjoin_dag.png)

6. Führen Sie im Query-Plan die folgenden Schritte aus:

##### 6a. Shuffle Join von transactions und stores

![1.3-shuffle_join_transactions_stores.png](./Includes/images/1.3-shuffle_join_transactions_stores.png)

- Suchen Sie **PhotonScan parquet dbacademy.your-schema-name.transactions (1)**.

- Erweitern Sie oberhalb dieser Tabelle **PhotonShuffleExchangeSink (2)**.

- Beachten Sie, dass das Shuffle für den ersten Join mit der Tabelle **stores** etwa 1,4 GB benötigt.

##### 6b. Shuffle Join des Ergebnisses mit countries

![1.3-shuffle_join_results_countries.png](./Includes/images/1.3-shuffle_join_results_countries.png)

- Suchen Sie **PhotonShuffleExchangeSource** auf der linken Seite oberhalb von **AQEShuffleRead** für das Ergebnis des vorherigen Joins.

- Erweitern Sie **PhotonShuffleExchangeSource**.

- Beachten Sie, dass ein weiteres Shuffle mit etwa 1,4 GB für den Join der Ergebnisse des ersten Joins mit der **countries**-Tabelle durchgeführt wurde.

# Joins mit Broadcast Join

Jetzt setzen wir die Konfiguration jedoch wieder auf den Standardwert zurück, sodass Broadcast Join aktiviert ist, um die Abfragen zu vergleichen. 

Dies funktioniert in diesem Fall, weil mindestens eine der Tabellen in jedem Join relativ klein ist und unter den Schwellenwerten liegt:
- < 10 MB für einen Broadcast Join **ohne** AQE
- < 30 MB für einen Broadcast Join **mit** AQE

```python
# Die Standardkonfigurationen für Broadcast Joins setzen
spark.conf.unset("spark.sql.autoBroadcastJoinThreshold")
spark.conf.unset("spark.databricks.adaptive.autoBroadcastJoinThreshold")

## Die Standardwerte anzeigen
# Current value of autoBroadcastJoinThreshold: 
print(spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))
# Current value of adaptive.autoBroadcastJoinThreshold:
print(spark.conf.get("spark.databricks.adaptive.autoBroadcastJoinThreshold"))
```

Führen Sie die Abfrage aus, um denselben Join wie zuvor durchzuführen. Beachten Sie, dass diese Abfrage in etwa der Hälfte der Zeit des vorherigen Joins ausgeführt wird.

```python
joined_df = spark.sql("""
    SELECT 
        transactions.id,
        amount,
        countries.name as country_name,
        employees,
        stores.name as store_name
    FROM
        transactions
    LEFT JOIN
        stores
        ON
            transactions.store_id = stores.id
    LEFT JOIN
        countries
        ON
            transactions.country_id = countries.id
""")

(joined_df
 .write
 .mode('overwrite')
 .saveAsTable('transact_countries')
)
```

Das ist eine Verbesserung. Wenn Sie erneut auf den **Stages**-Tab der Spark UI schauen, werden Sie feststellen, **dass es keine großen Shuffle Reads mehr gibt**. Nur die kleinen Tabellen wurden geshuffelt, die große Tabelle jedoch nicht, sodass wir das zweimalige Verschieben von 1,4 GB vermieden haben.

Sehen Sie sich die Stages dieser Abfrage an. Beachten Sie, dass die großen Shuffles vermieden wurden, was die Query-Effizienz verbessert.
![1.3-broadcast_join_stages.png](./Includes/images/1.3-broadcast_join_stages.png)

Sie können sich auch den Query-Plan ansehen und erkennen, dass die großen Tabellen nicht geshuffelt wurden.

![1.3-broadcast_join.png](./Includes/images/1.3-broadcast_join.png)

Broadcast Joins können deutlich schneller sein als Shuffle Joins, wenn eine der Tabellen sehr groß und die andere klein ist. Leider funktionieren Broadcast Joins nur, wenn mindestens eine der Tabellen kleiner als 100 MB ist. Beim Zusammenführen größerer Tabellen müssen wir, wenn wir das Shuffle vermeiden möchten, möglicherweise unser Schema überdenken, um den Join von vornherein zu vermeiden.

## E. Aggregationen

Auch Aggregationen verwenden ein Shuffle, dieses ist jedoch oft deutlich günstiger. Die folgende Zelle führt eine Abfrage aus, die dies demonstriert.

```sql
%sql
SELECT 
  country_id, 
  COUNT(*) AS count,
  AVG(amount) AS avg_amount
FROM transactions
GROUP BY country_id
ORDER BY count DESC
```

Das ging schnell! Hier passiert eine ganze Menge. Einer der wichtigsten Punkte ist, dass wir nur die Counts und Summen shuffeln, die zur Berechnung der angeforderten Counts und Averages notwendig sind. Dies führt lediglich zum Shuffeln weniger KB. Nutzen Sie erneut die Spark UI, um dies zu überprüfen.

![1.3_aggregations-ui.png](./Includes/images/1.3-aggregations_ui.png)

Das Shuffle ist also im Vergleich zu den Shuffle Joins, bei denen alle Daten geshuffelt werden müssen, günstig. Hilfreich ist außerdem, dass unsere Ausgabe in diesem Fall im Prinzip 0 ist.
