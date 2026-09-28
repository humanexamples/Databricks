

Demo: Arbeiten wir mit **Liquid Clustering**, einer Delta Lake Optimierungsfunktion, die **Table Partitioning** und **ZORDER** ersetzt, um Entscheidungen zum Data Layout zu vereinfachen und die Query Performance zu optimieren. Sie bietet die Flexibilität, Clustering Keys neu zu definieren, ohne die Daten neu schreiben zu müssen. 

Databricks empfiehlt Liquid Clustering für alle neuen Delta-Tabellen. Szenarien, die von Clustering profitieren: 

* Tabellen, die häufig nach Spalten mit hoher Kardinalität gefiltert werden.
* Tabellen mit einer deutlichen Schiefe (Skew) in der Datenverteilung.
* Tabellen, die schnell wachsen und Wartungs- sowie Tuning-Aufwand erfordern.
* Tabellen mit Anforderungen an gleichzeitige Schreibvorgänge (Concurrent Writes).
* Tabellen mit Zugriffsmustern, die sich im Laufe der Zeit ändern.
* Tabellen, bei denen ein typischer Partition Key die Tabelle mit zu vielen oder zu wenigen Partitionen hinterlassen würde.

**HINWEIS:** Diese Queries auf der ZORDERED-Tabelle sind bereits ohne Verwendung von Clustering recht schnell, wenn man bedenkt, dass wir einen kleinen Cluster verwenden und die Tabellen nicht extrem groß sind. Es gibt jedoch noch Raum für Verbesserungen.

In diesem Lab verwenden wir Flugdaten von Fluggesellschaften, die auf drei verschiedene Arten gespeichert wurden. Jede Tabelle enthält exakt die gleichen Daten (Die Anzahl der Zeilen in jeder Tabelle *1.235.347.780*):

- **flights**: **OPTIMIZED mit einem ZORDER** auf **FlightNum**.
- **flights_cluster_id**: **Liquid clustered** anhand der Spalte **id**.
- **flights_cluster_id_flightnum**: **Liquid clustered** nach zwei Spalten (**id** und **FlightNum**).

Bevor Sie Zellen in diesem Notebook ausführen, wählen Sie bitte Ihren Classic Compute Cluster im Lab aus. 

```python
# Das Deaktivieren des Disk Cachings verhindert, dass Databricks Cloud-Storage-Dateien 
# nach der ersten Abfrage speichert. Dadurch wird die Wirkung der Optimierungen deutlicher, 
# da sichergestellt wird, dass Dateien bei jeder Abfrage stets aus dem Cloud Storage geladen 
# werden.
# Dieser Befehl funktioniert nicht mit Serverless sondern mit Classic Compute:
spark.conf.set('spark.databricks.io.cache.enabled', False)
```

```sql
-- Finden Sie in der Spalte **operation** die Version (Zeile) der Delta-Tabelle, 
-- die *OPTIMIZED* wurde.

-- Beachten Sie in der Spalte **operationParameters**, dass die Tabelle **flights** mit 
-- einem ZORDER auf der Spalte **FlightNum** optimiert wurde. Z-Ordering ist eine Technik, 
-- mit der zusammengehörige Informationen in derselben Gruppe von Dateien kolokiert werden.

-- Beobachten Sie in der Spalte **operationMetrics**, dass die OPTIMIZED-Anweisung 
-- (*numRemovedFiles*) *160* Dateien entfernt und (*numAddedFiles*) *31* Dateien 
-- hinzugefügt hat, um die Speicherung der Tabelle zu optimieren.
DESCRIBE HISTORY flights;
```

```sql
-- Beachten Sie Folgendes:

-- Wenn wir nach der geclusterten Spalte (**id**) abfragen, sehen wir eine Verbesserung 
-- der Query Performance.
-- Wir sehen keine Verschlechterung der Performance bei Queries auf nicht geclusterte 
-- Spalten.  

-- 1. Führen Sie die folgende Zelle aus, um die History der Tabelle **flights_cluster_id** 
-- anzuzeigen. Beobachten Sie in der Ausgabe Folgendes:

-- Beachten Sie in der Spalte **operationParameters**, dass die Tabelle 
-- **flights_cluster_id** mit einem *clusterBy* auf der Spalte **ID** optimiert wurde.

-- Beachten Sie in der Spalte **operationMetrics**, dass die geclusterte Tabelle mit *128* 
-- Dateien erstellt wurde.
DESCRIBE HISTORY flights_cluster_id;

-- Beachten Sie Folgendes:
-- Die Tabelle enthält dieselben 6 Spalten.
-- Unter *Clustering Information* sehen wir, dass die Tabelle nach **id** geclustert ist.
-- Am Ende der Ergebnisse enthalten die **Table Properties** verschiedene Eigenschaften 
-- für Liquid Clustering.
DESCRIBE TABLE EXTENDED flights_cluster_id;
```

```sql
-- Beachten Sie Folgendes:

-- Wir haben weiterhin keine Verschlechterung bei nicht geclusterten Spalten. Hätten wir stattdessen `PARTITION BY` verwendet, um nach **FlightNum** und **id** zu partitionieren, würden wir eine massive Verlangsamung bei jeder Query feststellen, die nicht auf diese Spalten abzielt, und Schreibvorgänge wären bei diesem Datenvolumen unzumutbar langsam.
-- Nun sind Queries auf **FlightNum** verbessert.
-- Queries auf **id** sind jetzt etwas langsamer, wir können jedoch im DAG nachvollziehen, warum.

-----------------

-- Beachten Sie, dass wir mehr Dateien lesen mussten, um diesen Request zu erfüllen. Das Clustering nach mehreren Spalten ist mit (geringen) Kosten verbunden, wählen Sie die Spalten also mit Bedacht.

-- 1. Führen Sie die folgende Zelle aus, um die History der Tabelle **flights_cluster_id_flightnum** anzuzeigen. Beobachten Sie in der Ausgabe Folgendes:

-- Beachten Sie in der Spalte **operationParameters**, dass die Tabelle **flights_cluster_id_flightnum** mit einem *clusterBy* auf den Spalten **id** und **FlightNum** optimiert wurde.

-- Beachten Sie in der Spalte **operationMetrics**, dass die geclusterte Tabelle mit *144* Dateien erstellt wurde.
DESCRIBE HISTORY flights_cluster_id_flightnum;


-- Beachten Sie Folgendes:

-- Unter *Clustering Information* sehen wir, dass die Tabelle nach **id** und 
-- **FlightNum** geclustert ist.
-- Am Ende der Ergebnisse enthalten die **Table Properties** verschiedene Eigenschaften 
-- für Liquid Clustering.
DESCRIBE TABLE EXTENDED flights_cluster_id_flightnum;
```

------

```sql
SELECT AVG(try_cast(ArrDelay AS DOUBLE)) FROM flights 
                                         FROM flights_cluster_id 
                                         FROM flights_cluster_id_flightnum 
WHERE UniqueCarrier = 'TW';
```

**Value - ZORDER (flights):** Diese Tabelle wurde nach **FlightNum** Z-geordnet, aber nach der Spalte **UniqueCarrier** abgefragt. Spark muss alle Dateien lesen, um die Tabelle zu filtern und eine einzelne Zeile zurückzugeben. Im Durchschnitt dauert diese Query etwa **~10 Sekunden** bis zum Abschluss.

**Value - Liquid Clustering(flights_cluster_id):** Diese Tabelle wurde nach **id** geclustert und nach der Spalte **UniqueCarrier** abgefragt, wobei die Ausführung etwa ~10 Sekunden dauerte. Die Ausführungszeit und die Cloud Storage Response Size sind der Query auf der optimierten Tabelle **flights** mit einem ZORDER auf **FlightNum** sehr ähnlich.

**Liquid Clustering(flights_cluster_id_flightnum):** Diese Tabelle wurde nach **id** und **FlightNum** geclustert und nach der Spalte **UniqueCarrier** abgefragt. Diese Query sollte in etwa ~10 Sekunden laufen. Ähnlich wie die beiden anderen Queries, die auf der Spalte **UniqueCarrier** ausgeführt wurden.



**HINWEISE:** Für die Spalte **UniqueCarrier** wurde keine Speicheroptimierung festgelegt, sodass für jede Tabelle bei der Query alle Dateien gelesen wurden. Jede Query hatte ähnliche Cloud Storage Response Sizes und Ausführungszeiten.


| Metric    | ZORDER<br/>(flights) | Liquid Clustering<br/>(clusterid) | Liquid Clustering<br/>(flights_cluster_id_flightnum) |
|-------------|-------------|-------------|-------------|
| Ausführungszeit (sec.) | 10,30 | 10,91 | 10,88 |
| cloud storage request count total (min, med, max)| 149 (3, 3, 18)| 316 (4, 8, 12) | 376 (3, 10, 14) |
| cloud storage response size total (min, med, max)|1116.5 MiB (336.6 KiB, 45.7 MiB, 50.7 MiB)| 1047.8 MiB (601.0 KiB, 27.5 MiB, 47.2 MiB) | 997.6 MiB (988.3 KiB, 27.0 MiB, 43.7 MiB) |
| files pruned | 0 | 0 | 0 |
| files read | 31| 128 | 144 |





------

```sql
SELECT AVG(try_cast(ArrDelay AS DOUBLE)) FROM flights
                                         FROM flights_cluster_id 
                                         FROM flights_cluster_id_flightnum
WHERE FlightNum = 1890
```

**Value - ZORDER (flights):** Diese Tabelle wurde nach **FlightNum** Z-geordnet und nach der Spalte **FlightNum** abgefragt. In diesem Szenario waren die Dateien nach **FlightNum** organisiert und wurden auch nach **FlightNum** abgefragt, sodass die Query effizient die benötigten Dateien lesen konnte. Im Durchschnitt dauert diese Query etwa **~2 Sekunden** bis zum Abschluss.

**Value - Liquid Clustering(flights_cluster_id):** Diese Tabelle wurde nach **id** geclustert und nach der Spalte **FlightNum** abgefragt, wobei die Ausführung etwa ~10 Sekunden dauerte. Diese Query benötigte etwas länger zur Ausführung, und die Cloud Storage Response Size war deutlich größer als bei der Query auf der optimierten Tabelle **flights** mit einem ZORDER auf **FlightNum**.

**Liquid Clustering(flights_cluster_id_flightnum):** Diese Tabelle wurde nach **FlightNum** und **id** geclustert und nach der Spalte **FlightNum** abgefragt. Dadurch kann Spark optimieren, wie es die Daten liest. Diese Query sollte in rund ~2 Sekunden ausgeführt werden, ähnlich wie bei der Tabelle **flights** mit einem ZORDER auf **FlightNum**.



**HINWEISE:** Beachten Sie, dass bei den Tabellen, bei denen **FlightNum** in eine Speicheroptimierungstechnik einbezogen wurde, viele Dateien geprunt wurden, was die Effizienz erhöhte und die Ausführungszeiten verkürzte. Die Tabelle, die nur nach **id** geclustert war, lief langsamer, und die Cloud Storage Response Size war deutlich größer.

| Metric    | ZORDER<br/>(flights) | Liquid Clustering<br/>(clusterid) | Liquid Clustering<br/>(clusterid_flightnum) |
|-------------|-------------|-------------|-------------|
| Ausführungszeit (sec.) | 2,455 | 6,20 | 2,48 |
| cloud storage request count total (min, med, max)| 6 (3, 3, 3)| 275 (4, 12, 15) | 32 (4, 6, 6) |
| cloud storage response size total (min, med, max)|53.5 MiB (26.3 MiB, 27.2 MiB, 27.2 MiB)| 1871.3 MiB (22.8 MiB, 85.3 MiB, 94.2 MiB) | 146.3 MiB (21.9 MiB, 24.9 MiB, 27.6 MiB) |
| files pruned | 30 | 0 | 132 |
| files read | 1| 128 | 12 |



------

```sql
SELECT * FROM flights 
         FROM flights_cluster_id
         FROM flights_cluster_id_flightnum
WHERE id = 1125281431554;
```

**Value - ZORDER (flights):** Diese Tabelle wurde nach **FlightNum** Z-geordnet und nach der Spalte **id** abgefragt. Die Spalte **id** ist eine Spalte mit hoher Kardinalität (Hohe Kardinalität = sehr viele unterschiedliche Werte), was dazu führt, dass die Query:

- eine sehr große Cloud Storage Response Size aufweist.
- jede Datei liest.
- rund **~28 Sekunden** läuft.

**Value - Liquid Clustering(flights_cluster_id):** Diese Tabelle wurde nach **id** geclustert und nach der Spalte **id** abgefragt. Dadurch kann Spark die Daten optimal lesen und die Ausführung in rund **~2 Sekunden** abschließen, im Vergleich zu ~28 Sekunden bei der Tabelle **flights**, die einen ZORDER auf **FlightNum** enthielt und optimiert wurde. Die Cloud Storage Response Size war ebenfalls deutlich kleiner als 4,7 GiB.

**Liquid Clustering(flights_cluster_id_flightnum):** Diese Tabelle wurde nach **FlightNum** und **id** geclustert und nach der Spalte **id** abgefragt. Dadurch kann Spark optimieren, wie es die Daten liest. Diese Query sollte in **rund 2 Sekunden** ausgeführt werden, deutlich schneller als bei der Tabelle **flights** mit einem ZORDER auf **FlightNum** bei derselben Query (~28 Sekunden).

**Liquid Clustering(flights_cluster_id_flightnum):** Diese Tabelle wurde nach **FlightNum** und **id** geclustert und über die Spalte **id** abgefragt. So kann Spark optimieren, wie die Daten gelesen werden. Diese Abfrage sollte in etwa 2 Sekunden laufen – deutlich schneller als die Tabelle **flights** mit ZORDER auf **FlightNum** bei derselben Abfrage (~28 Sekunden).



**HINWEISE:** Beachten Sie, dass bei den Tabellen, bei denen **id** in eine Speicheroptimierungstechnik einbezogen wurde (beide liquid geclusterten Tabellen), viele Dateien geprunt wurden, was die Effizienz erhöhte — selbst bei der Tabelle, die sowohl nach **id** als auch nach **FlightNum** geclustert ist. Sie können außerdem sehen, dass die Cloud Storage Response Size bei jeder der geclusterten Tabellen deutlich kleiner war als bei der nach **FlightNum** Z-geordneten Tabelle. Beachten Sie außerdem, dass die Z-geordnete Tabelle extrem lange zur Ausführung benötigte und die Cloud Storage Response Size beim Abfragen der Spalte **id** in der Tabelle **flights** deutlich größer war.


| Metric    | ZORDER<br/>(flights) | Liquid Clustering<br/>(clusterid) | Liquid Clustering<br/>(flights_cluster_id_flightnum) |
|-------------|-------------|-------------|-------------|
| Ausführungszeit (sec.) | 23,04 | 3,14 | 4,19 |
| cloud storage request count total (min, med, max)| 267 (1, 4, 14)| 4 | 29 (2, 6, 6) |
| cloud storage response size total (min, med, max) | 4.7 GiB (256.0 KiB, 72.5 MiB, 101.1 MiB) | 54.5 MiB | 370.9 MiB (27.3 MiB, 68.5 MiB, 71.5 MiB) |
| files pruned | 0 | 127 | 134 |
| files read | 31| 1 | 10 |





------

## Automatic Liquid Clustering (GA seit Juni 2025)

![LQ Auto](./Includes/images/Liquid-Clusters-OG.png)

In den obigen Demos haben Sie die Clustering Keys manuell ausgewählt. **Automatic Liquid Clustering** nimmt Ihnen diese Entscheidung ab — Databricks analysiert Ihre Workload und wählt die optimalen Keys für Sie aus.

Angetrieben von **Predictive Optimization** funktioniert dies, indem Query-Prädikate (`WHERE`-Klauseln und `JOIN`-Filter) überwacht werden, modelliert wird, welche Clustering Keys die gescannte Datenmenge am stärksten reduzieren würden, und Änderungen nur dann angewendet werden, wenn der prognostizierte Performance-Gewinn die Kosten des Clusterings übersteigt. Dies läuft asynchron ab und **passt sich im Laufe der Zeit an**, wenn sich die Query-Muster ändern.

Databricks empfiehlt dies für **alle von Unity Catalog verwalteten Tabellen** — insbesondere dann, wenn Sie unsicher sind, nach welchen Spalten geclustert werden soll, sich Query-Muster weiterentwickeln oder Sie einen freihändigen Ansatz über viele Tabellen hinweg wünschen. Es erfordert **DBR 15.4 LTS oder höher**, **von Unity Catalog verwaltete Delta-Tabellen** sowie **aktivierte Predictive Optimization** auf Katalog- oder Schemaebene.

#### Automatic Liquid Clustering aktivieren

Verwenden Sie `CLUSTER BY AUTO` beim Erstellen einer neuen Tabelle oder beim Ändern einer vorhandenen Tabelle. Führen Sie `DESCRIBE TABLE EXTENDED` aus, um zu bestätigen, dass es aktiviert ist — achten Sie in den Table Properties auf `clusterByAuto = true`.

```python
## Using my_catalog
spark.sql(f"USE CATALOG {my_catalog}")

## Using schema
spark.sql(f"USE SCHEMA {schema}")
```

```sql
-- Auf einer neuen Tabelle aktivieren
CREATE OR REPLACE TABLE auto_clustered_example (
  id BIGINT,
  transaction_date DATE,
  customer_id STRING,
  amount DOUBLE,
  region STRING
) CLUSTER BY AUTO;

-- Oder auf einer bestehenden, nicht partitionierten / liquid-geclusterten Tabelle aktivieren
-- ALTER TABLE my_existing_table CLUSTER BY AUTO;
```

```sql
-- Überprüfen: nach "clusterByAuto = true" suchen und clusteringColumns auf die ausgewählten Keys prüfen
DESCRIBE TABLE EXTENDED auto_clustered_example;
```

**Warum Sie möglicherweise nicht sofort ausgewählte Clustering Keys sehen:**

Nachdem Sie `CLUSTER BY AUTO` aktiviert haben, werden Clustering Keys **nicht** sofort angezeigt. Predictive Optimization muss zunächst **ausreichend Query-History** zu der Tabelle sammeln — es werden historische Scan-Statistiken der Queries analysiert, um zu ermitteln, welche Spalten sich für Clustering lohnen. Die Auswahl der Keys erfolgt als Hintergrund-Wartungsvorgang nach einem eigenen Zeitplan, nicht zum Zeitpunkt der Query-Ausführung.

Es kann sein, dass keine Keys ausgewählt werden, wenn die Tabelle zu klein ist, zu wenige Queries darauf laufen, wiederkehrende Filtermuster fehlen oder die Kosten-Nutzen-Analyse ergibt, dass Clustering keinen nennenswerten Vorteil bringen würde. In einer Live-Unterrichtsumgebung bedeutet dies, dass das Feld `clusteringColumns` in `DESCRIBE TABLE EXTENDED` während der Demo wahrscheinlich leer bleibt. Dies ist erwartetes Verhalten — Automatic Liquid Clustering ist für Produktions-Workloads konzipiert, die über Tage und Wochen laufen, nicht für kurzlebige Demo-Tabellen.



