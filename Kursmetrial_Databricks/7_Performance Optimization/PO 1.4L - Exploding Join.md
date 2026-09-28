

  Exploding Join

In diesem Lab arbeiten wir daran, die Query Performance eines exploding join zwischen 3 Tabellen zu verbessern:
- **transactions**
- **stores**
- **countries**

Wir wollen ein durch den exploding join verursachtes Spill einführen und identifizieren und die Performance des Joins schrittweise verbessern.

```python
# Das Deaktivieren des Disk Cachings verhindert, dass Databricks Cloud-Storage-Dateien 
# nach der ersten Abfrage speichert. Dadurch wird die Wirkung der Optimierungen deutlicher, 
# da sichergestellt wird, dass Dateien bei jeder Abfrage stets aus dem Cloud Storage geladen 
# werden.
# Dieser Befehl funktioniert nicht mit Serverless sondern mit Classic Compute:
spark.conf.set('spark.databricks.io.cache.enabled', False)
```

```python
## 'transactions' Tabelle mit 2.000.000 Zeilen erzeugen:

from pyspark.sql.functions import *

spark.sql('DROP TABLE IF EXISTS transactions')

## Tabelle erstellen
transactions_df = (spark
                   .range(0, 2000000, 1, 32)
                    .select(
                        'id',
                        round(rand() * 10000, 2).alias('amount'),
                        (col('id') % 10).alias('country_id'),
                        (col('id') % 100).alias('store_id')
                    )
                    .write
                    .mode('overwrite')
                    .option("overwriteSchema", "true")
                    .saveAsTable('transactions')
                )
```

```python
## 'countries' Tabelle erzeugen:
spark.sql('DROP TABLE IF EXISTS countries')

## Tabelle erstellen
countries = [(0, "Italy"),(1, "Canada"),(2, "Mexico"),(3, "China"),(4, "Germany"),(5, "UK"),
         (6, "Japan"),(7, "Korea"),(8, "Australia"),(9, "France"),(10, "Spain"),(11, "USA")
            ]
columns = ["id", "name"]

countries_df = (spark
                .createDataFrame(data = countries, schema = columns)
                .write
                .mode('overwrite')
                .saveAsTable("countries")
            )
```

### C3. Die stores-Tabelle erstellen
- Erzeugen Sie die Tabelle **stores**, um sie später mit der Tabelle **transactions** zu joinen.
- Die Tabelle **stores** enthält absichtlich Duplikate des Werts **id**, wodurch ein exploding join mit der Tabelle **transactions** entsteht.
- Beim Joinen der Tabelle **transactions** mit der Tabelle **stores** werden aufgrund der duplizierten **ids** eine Reihe von Zeilen explodieren.

```python
## 'stores' Tabelle erzeugen:
spark.sql('DROP TABLE IF EXISTS stores')

stores_df = (
spark
 .range(0, 9999)
 .select(
   (col('id') % 100).alias('id'), # Duplizierung der ids, um den Join zu explodieren
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
## Deaktivieren Sie in dieser Zelle broadcast joins, um die Performance-Verbesserungen 
## durch das Tuning der Join-Strategie schrittweise zu demonstrieren.

## Deaktiviert den automatischen broadcast join vollständig. Das heißt, Spark wird für Joins niemals einen Datensatz broadcasten, unabhängig von dessen Größe.
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)

# Deaktiviert das broadcast join Feature unter AQE, das heißt, selbst bei Verwendung von adaptive query execution wird Spark nicht versuchen, die kleinere Seite eines Joins zu broadcasten.
spark.conf.set("spark.databricks.adaptive.autoBroadcastJoinThreshold", -1)
```

```python
## Wir werden die Tabelle **transactions** mit den Daten aus **countries** und **stores** joinen und die Aktion auslösen, indem wir das Ergebnis in eine Tabelle namens **transact_countries** schreiben. Dieser Prozess kann ungefähr ~1 Minute dauern.
joined_df_nobroadcast = spark.sql("""
    SELECT 
        transactions.id,
        amount,
        countries.name as country_name,
        employees,
        stores.name as store_name
    FROM
        transactions
    JOIN
        stores
        ON
            transactions.store_id = stores.id
    JOIN
        countries
        ON
            transactions.country_id = countries.id
""")

(joined_df_nobroadcast
 .write
 .mode('overwrite')
 .saveAsTable('transact_countries')
)
```

### D1. TODO: Den Exploding Join betrachten
Öffnen Sie die Spark UI und navigieren Sie zur **Stages**-Seite. Identifizieren Sie die Explosion der Zeilenanzahl im DAG der Spark UI. Um den DAG anzuzeigen, gehen Sie wie folgt vor:

1. Klappen Sie in der obigen Zelle **Spark Jobs** auf.

2. Klicken Sie beim ersten Job mit der rechten Maustaste auf **View** und wählen Sie *Open in a New Tab*. 
- **Wenn der erste Job nicht die korrekten Informationen anzeigt, versuchen Sie es mit dem zweiten.**

**HINWEISE:** In der Vocareum-Lab-Umgebung zeigt das Popup-Fenster einen Fehler an, wenn Sie **View** anklicken, ohne es in einem neuen Tab zu öffnen.

3. Suchen Sie im neuen Fenster oben die Überschrift **Jobs** und klicken Sie auf die Zahl unter **Associated SQL Query**.

4. Hier sollten Sie den gesamten Query Plan sehen. Lesen Sie den DAG-Graphen von unten nach oben, um die Details des Ausführungsplans besser zu verstehen.

![1.4-d1-exploding_join_shuffle_dag.png](./Includes/images/1.4-d1-exploding_join_shuffle_dag.png)

5. Klappen Sie im Query Plan unterhalb der Zeilenanzahl (199.980.000) die Box **PhotonShuffleExchangeSink** auf (der Pfeil im obigen Bild zeigt Ihnen, was aufzuklappen ist). Beachten Sie, dass die **Metrik** für *estimated rows output* nach dem Join der Tabelle **transactions** mit der Tabelle **stores** um das 100-fache explodiert ist, was durch die Duplikate der store-id in der stores-Tabelle verursacht wird.

6. Betrachten Sie an derselben Stelle die **Metrik** **num bytes spilled to disk due to memory pressure total (min, med, max)**. Beachten Sie, dass *927,6 MiB* (Wert kann variieren) auf die Festplatte gespillt wurden.

7. Lassen Sie die Spark UI geöffnet.

### D2. TODO: Das Spill betrachten
Betrachten Sie das Memory Spill in der Spark UI. 

1. Wählen Sie in der Spark UI in der oberen Navigationsleiste **Stages**. Hier sehen Sie alle auf dem Cluster durchgeführten Stages.

2. Finden Sie die Stage mit der größten Menge an **Shuffle Writes** (sollte bei etwa 1335,0 MiB liegen, kann aber variieren) für die Query, deren **Description**-Spalte mit `joined_df_nobroadcast = spark("""SELECT...)` beginnt.

3. Nachdem Sie diese Stage gefunden haben, wählen Sie den Link im Feld **Description**.
![1.4-d2_find_spill.png](./Includes/images/1.4-d2_find_spill.png)

4. Betrachten Sie das Feld **Spill (Disk)** für diese Stage. Beachten Sie, dass diese Query auf die Festplatte gespillt hat.

**HINWEIS:** In Apache Spark wird, wenn mehr Daten vorhanden sind, als im Speicher verarbeitet werden können, ein Teil der zusätzlichen Daten auf die Festplatte ausgelagert. Dies wird als *spilling to disk* bezeichnet, und die 927,9 MiB bedeuten, dass etwa 927,9 Megabyte an Daten auf die Festplatte verschoben werden mussten, um die Verarbeitung fortzusetzen.

![1.4-d2_memory_spill.png](./Includes/images/1.4-d2_memory_spill.png)

5. Betrachten Sie auf derselben Seite die **Locality Level Summary**. Dies bedeutet, dass die Anzahl der Partitionen in dieser Stage 4 beträgt. Überlegen Sie: Ist das eine gute Einstellung?

6. Schließen Sie den Spark-UI-Browser.

## E. Verbesserung: Erhöhen der Anzahl der Shuffle Partitions
Versuchen wir, die Performance dieser Query zu verbessern, indem wir die Anzahl der Shuffle Partitions erhöhen. Dazu ändern Sie die Konfigurationseinstellung **spark.sql.shuffle.partitions** und setzen sie auf **8** Partitionen. 

Dies konfiguriert die Anzahl der Partitionen, die beim Shuffling von Daten für Joins oder Aggregationen verwendet werden.

Weitere Informationen finden Sie in der Dokumentation zu [spark.sql.shuffle.partitions](https://spark.apache.org/docs/latest/sql-performance-tuning.html#adaptive-query-execution).

```python
## Zelle erneut ausführen, um die broadcast join Features zu deaktivieren, falls noch nicht geschehen
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
spark.conf.set("spark.databricks.adaptive.autoBroadcastJoinThreshold", -1)

## Das Spill beheben, indem die Anzahl der Shuffle Partitions auf 8 erhöht wird
## In diesem kleinen Beispiel kein großer Unterschied, aber mit zunehmender Menge gespillter Daten
## kann dies einen großen Unterschied machen
spark.conf.set("spark.sql.shuffle.partitions", 8)
```

```python
# Führen Sie dieselbe Query wie im vorherigen Beispiel aus, diesmal jedoch mit der Anzahl der Shuffle Partitions auf 8 gesetzt. Notieren Sie sich die Zeit, die die Query zur Ausführung benötigt. Dies sollte ungefähr ~50 Sekunden dauern.

joined_df_8_partitions = spark.sql("""
    SELECT 
        transactions.id,
        amount,
        countries.name as country_name,
        employees,
        stores.name as store_name
    FROM
        transactions
    JOIN
        stores
        ON
            transactions.store_id = stores.id
    JOIN
        countries
        ON
            transactions.country_id = countries.id
""")

(joined_df_8_partitions
 .write
 .mode('overwrite')
 .saveAsTable('transact_countries')
)

## shuffle.partitions auf die Standardeinstellung zurücksetzen
spark.conf.unset("spark.sql.shuffle.partitions")
```

### E1. TODO: Das Spill betrachten

Betrachten Sie das Memory Spill in der Spark UI. 

1. Klappen Sie **Spark Jobs** auf, klicken Sie beim ersten Job mit der rechten Maustaste und wählen Sie **Open in a New Tab**.

2. Wählen Sie in der Spark UI in der oberen Navigationsleiste **Stages**.

3. Finden Sie die Stage mit der größten Menge an Shuffle Writes (sollte bei etwa 679,9 MiB liegen, kann aber variieren) für die Query, deren **Description**-Spalte mit `joined_df_8_partitions = spark("""SELECT...)` beginnt.

4. Nachdem Sie diese Stage gefunden haben, wählen Sie den Link im Feld **Description**.

5. Betrachten Sie das Feld **Spill (Disk)**. Beachten Sie, dass diese Stage auf die Festplatte gespillt hat.

**HINWEIS:** In Apache Spark wird, wenn mehr Daten vorhanden sind, als im Speicher verarbeitet werden können, ein Teil der zusätzlichen Daten auf die Festplatte ausgelagert. Dies wird als *spilling to disk* bezeichnet, und die 273,4 MiB bedeuten, dass etwa 273,4 MiB an Daten auf die Festplatte verschoben werden mussten, um die Verarbeitung fortzusetzen.

Durch die Änderung der Anzahl der Partitionen hat sich das Spill verringert.

![1.4-e_memory_spill.png](./Includes/images/1.4-e_memory_spill.png)

6. Betrachten Sie auf derselben Seite die **Locality Level Summary**. Dies bedeutet, dass die Anzahl der Partitionen in dieser Stage 6 beträgt, obwohl wir die Anzahl der Partitionen auf 8 gesetzt haben. Dies liegt daran, dass Spark automatisch entscheidet, kleinere Partitionen während eines Jobs zu größeren zusammenzufassen, was Spark helfen kann, den Job schneller abzuschließen und weniger Speicher zu verwenden. 

Sie können dies deaktivieren, indem Sie die folgende Option setzen: `spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", False)`.

7. Beachten Sie, dass die Menge der gespillten Daten reduziert wurde und die Ausführungszeit der Query etwas schneller ist. 

**HINWEIS:** Die Spill-Metriken von 273 MB gespillter Daten lassen sich im Query Plan im **PhotonShuffleExchangeSink** beobachten, der auf die Join-Operationen folgt, sowie in den Stage-Details der Stage mit der größten Menge an Shuffle Writes.

## F. Verbesserung: Die Reihenfolge des Joins ändern

Führen Sie die untenstehende Zelle aus, um **autoBroadcastJoinThreshold** zu deaktivieren, falls noch nicht geschehen.

```python
## broadcast join Features deaktivieren, falls noch nicht geschehen
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
spark.conf.set("spark.databricks.adaptive.autoBroadcastJoinThreshold", -1)
```

Betrachten wir die unten geänderte Query, die nun die Tabelle **transactions** zunächst mit **countries** joint und anschließend mit der Tabelle **stores**. 

Indem zuerst der kleinere Join ausgeführt wird (und der große exploding join vermieden wird), müssen wir nicht so viele Daten shuffeln wie zuvor, als wir zuerst mit der Tabelle **stores** gejoint haben.

Führen Sie die Zelle aus und notieren Sie die Zeit, die die Query zur Fertigstellung benötigt.

**HINWEIS:** Die Query wurde bereits für Sie angepasst. Führen Sie die Zelle einfach aus.

```python
# Betrachten wir die unten geänderte Query, die nun die Tabelle 'transactions' 
# zunächst mit 'countries' joint und anschließend mit der Tabelle 'stores'. 

# Indem zuerst der kleinere Join ausgeführt wird (und der große exploding join  
# vermieden wird), müssen wir nicht so viele Daten shuffeln wie zuvor, als wir 
# zuerst mit der Tabelle 'stores' gejoint haben.

small_joined_first_df = spark.sql("""
    SELECT 
        transactions.id,
        amount,
        countries.name as country_name,
        employees,
        stores.name as store_name
    FROM
        transactions
    -- Beachten Sie, dass wir zuerst mit countries statt mit stores joinen --
    JOIN
        countries
        ON
            transactions.country_id = countries.id
    -- Anschließend joinen wir die Ergebnisse mit der stores-Tabelle, wodurch der Shuffle des großen exploding join vermieden wird --
    JOIN
        stores
        ON
            transactions.store_id = stores.id
""")

(small_joined_first_df
 .write
 .mode('overwrite')
 .saveAsTable('transact_countries')
)
```

### F1. TODO: Die Shuffles betrachten
Öffnen Sie die Spark UI und navigieren Sie zum Query-DAG. Identifizieren Sie die Explosion der Zeilenanzahl im DAG der Spark UI. Um zu sehen, wie der DAG funktioniert, gehen Sie wie folgt vor:

1. Klappen Sie in der obigen Zelle **Spark Jobs** auf.

2. Klicken Sie beim ersten Job mit der rechten Maustaste auf **View** und wählen Sie *Open in a New Tab*. 

**HINWEIS:** In der Vocareum-Lab-Umgebung zeigt das Popup-Fenster einen Fehler an, wenn Sie **View** anklicken, ohne es in einem neuen Tab zu öffnen.

3. Suchen Sie im neuen Fenster oben die Überschrift **Jobs** und klicken Sie auf die Zahl unter **Associated SQL Query**.

4. Hier sollten Sie den gesamten Query Plan sehen. Lesen Sie den DAG-Graphen von unten nach oben, um die Details des Ausführungsplans besser zu verstehen. 

5. Beachten Sie in der Query-Plan-Ansicht, dass der erste Join zwischen den Tabellen **transactions** und **countries** stattfindet und 2 Millionen Ergebnisse liefert. Anschließend werden die Ergebnisse mit der Tabelle **stores** gejoint, wodurch der exploding join entsteht. Dadurch wird vermieden, dass der große Join zwischen **transactions** und **stores** (~200.000.000 Zeilen) geshuffelt werden muss, wie es bei der ersten Query der Fall war.

![1.4-f_smaller_join_first_dag.png](./Includes/images/1.4-f_smaller_join_first_dag.png)

6. Lassen Sie die Spark UI geöffnet.

### F2. TODO: Das Spill betrachten
Betrachten Sie das Memory Spill in der Spark UI. 

1. Wählen Sie in der Spark UI in der oberen Navigationsleiste **Stages**. Hier sehen Sie alle auf dem Cluster durchgeführten Stages.

2. Finden Sie die Stage mit der größten Menge an **Shuffle Writes** (sollte bei etwa 19,1 MiB liegen, kann aber variieren) für die Query, deren **Description**-Spalte mit `small_joined_first_df = spark("""SELECT...)` beginnt.

3. Nachdem Sie diese Stage gefunden haben, wählen Sie den Link im Feld **Description**.

4. Betrachten Sie das Feld **Spill (Disk)**. Beachten Sie, dass diese Query nicht auf die Festplatte gespillt hat.

![1.4-f2_memory_spill.png](./Includes/images/1.4-f2_memory_spill.png)

5. Schließen Sie den Spark-UI-Browser.

Können Sie in der Spark UI immer noch Spill sehen? Lief diese Query schneller oder langsamer als das vorherige Beispiel?

## G. Verbesserung: Standard-Broadcast-Konfigurationen analysieren und verwenden

Setzen Sie die Konfigurationen **spark.sql.autoBroadcastJoinThreshold** und **spark.databricks.adaptive.autoBroadcastJoinThreshold** mithilfe der Methode `spark.conf.unset()` zurück.

[spark.sql.autoBroadcastJoinThreshold](https://spark.apache.org/docs/latest/sql-performance-tuning.html#automatically-broadcasting-joins) Dokumentation

[spark.databricks.adaptive.autoBroadcastJoinThreshold](https://spark.apache.org/docs/latest/sql-performance-tuning.html#converting-sort-merge-join-to-broadcast-join) Dokumentation

Führen Sie die Zelle aus und betrachten Sie die Ergebnisse. Bestätigen Sie die folgenden Standardwerte für die Konfigurationen:
- *Standardwert von autoBroadcastJoinThreshold: 10.485.760 Bytes*
- *Standardwert von adaptive.autoBroadcastJoinThreshold: 31.457.280 Bytes*

```python
# Standardwerte hier zurücksetzen
spark.conf.unset("spark.sql.autoBroadcastJoinThreshold")
spark.conf.unset("spark.databricks.adaptive.autoBroadcastJoinThreshold")

# Werte anzeigen

# Default value of autoBroadcastJoinThreshold:
print(spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))
# Default value of adaptive.autoBroadcastJoinThreshold:
print(spark.conf.get("spark.databricks.adaptive.autoBroadcastJoinThreshold"))
```

Kostenbasierte Optimierer stützen sich auf Statistikinformationen, um den effizientesten physischen Query Plan mit den geringsten Kosten zu erzeugen. Dazu gehören Entscheidungen über die Join-Strategie und die Reihenfolge der Joins.

Das Ausführen von `ANALYZE` auf den Join-Spalten der drei Tabellen ermöglicht es dem Optimierer, bessere Entscheidungen zu treffen, und alles funktioniert wie von selbst. 

Vervollständigen Sie die untenstehende Zelle, indem Sie die erforderlichen `ANALYZE`-Anweisungen schreiben. 

```python
# Analysiert die transactions-Tabelle und berechnet Statistiken für die Spalten country_id und store_id
sql("ANALYZE TABLE transactions COMPUTE STATISTICS FOR COLUMNS country_id, store_id")

# Analysiert die stores-Tabelle und berechnet Statistiken für die Spalte id
sql("ANALYZE TABLE stores COMPUTE STATISTICS FOR COLUMNS id")

# Analysiert die countries-Tabelle und berechnet Statistiken für die Spalte id
sql("ANALYZE TABLE countries COMPUTE STATISTICS FOR COLUMNS id")
```

Im folgenden Beispiel schreibt ein Entwickler Joins, ohne die optimale Reihenfolge der Joins zu berücksichtigen.

Führen Sie die Query erneut mit der ursprünglichen Query aus, die wir in dieser Demonstration verwendet haben, bei der **transactions** zuerst mit **stores** gejoint wird und die Daten für den großen Shuffle explodieren. 

Wird es funktionieren, wenn wir Spark selbst herausfinden lassen, wie die Daten effizient gejoint werden? 

Notieren Sie sich die für den Join benötigte Zeit.

```python
joined_df_analyze = spark.sql("""
    SELECT 
        transactions.id,
        amount,
        countries.name as country_name,
        employees,
        stores.name as store_name
    FROM
        transactions
    JOIN
        stores
        ON
            transactions.store_id = stores.id
    JOIN
        countries
        ON
            transactions.country_id = countries.id
""")

(joined_df_analyze
 .write
 .mode('overwrite')
 .saveAsTable('transact_countries')
)
```

**HINWEISE:**
- Wir haben die Shuffle-Einstellungen wieder auf die Standardwerte zurückgesetzt. Es ist normalerweise am besten, bei den Standardwerten zu bleiben, da sich diese im Laufe der Zeit tendenziell verbessern. Wenn Sie Konfigurationen fest codieren, verzichten Sie möglicherweise unwissentlich auf zukünftige Performance-Verbesserungen. Es lohnt sich immer, alte Konfigurationen zu überprüfen, um sicherzustellen, dass sie noch benötigt werden. Durch das Bereinigen alter Konfigurationen können Sie erhebliche Performance-Verbesserungen erzielen.

Betrachten Sie die Spark UI. Denken Sie über Folgendes nach:
- Was können Sie im DAG des Query Plans erkennen? 
- Gibt es ein Spill? 
- Sind Zeilen explodiert? 
- Reihenfolge des Joins? 
- Ist der DAG ähnlich wie bei den vorherigen Joins? 
- Wurde die Query schneller ausgeführt? Wie groß waren die Shuffle Writes? 
- Größer oder kleiner als bei den vorherigen Queries?

**Stages**
- Beachten Sie die geringe Menge an Shuffle Writes.
![1.4-g_analyze_stages.png](./Includes/images/1.4-g_analyze_stages.png)

**DAG**
- Betrachten Sie die Unterschiede im DAG.
![1.4_g_dag.png](./Includes/images/1.4_g_dag.png)

## Zusammenfassung der 4 Joins

| Join-Strategie | Ausführungszeit | Memory Spill | Größter Shuffle Write | Anmerkungen |
|---------------|----------------|----------------|----------------|----------------|
|D. Exploding Join| ~60 Sekunden| ~928 MiB |	1334,8 MiB |Zuerst wird die Tabelle **transactions** mit der Tabelle **store** gejoint (exploding join) |
|E. Anzahl der Shuffles erhöhen| ~50 Sekunden | ~273,7 MiB | 680,5 MiB |Derselbe Join wie zuvor, mit 8 Partitionen |
|F. Join-Reihenfolge ändern | ~40 Sekunden| 0 | 19,1 MiB |Die Join-Reihenfolge wird geändert, sodass **transactions** zuerst mit **countries** gejoint wird |
|G. Analyze und Broadcast Join| ~20 Sekunden| 0 | 383,6 KiB |Databricks analysiert und verwendet die Standard-Broadcast-Konfigurationen. Während die Query etwa gleich lange dauerte, wurde der Shuffle drastisch reduziert. |

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Markenzeichen der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
