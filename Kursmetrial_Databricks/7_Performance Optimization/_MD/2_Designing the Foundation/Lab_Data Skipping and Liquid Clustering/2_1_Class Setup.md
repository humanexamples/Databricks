# Lab: Data Skipping und Liquid Clustering

In diesem Demo arbeiten wir mit Liquid Clustering, einer Delta Lake-Optimierungsfunktion, die Table Partitioning und ZORDER ersetzt, um Entscheidungen zum Daten-Layout zu vereinfachen und die Query-Performance zu optimieren. Sie bietet die Flexibilität, Clustering-Keys neu zu definieren, ohne die Daten neu schreiben zu müssen. Weitere Informationen finden Sie in der [Dokumentation](https://docs.databricks.com/en/delta/clustering.html).

#### Lernziele
**Am Ende dieses Labs können Sie:**

* Spark Caching deaktivieren, um die Auswirkungen von Liquid Clustering zu beobachten.
* Datensätze zählen und Daten in den Flights-Tabellen erkunden.
* Queries auf einer nicht geclusterten Tabelle ausführen und deren Performance mithilfe der Spark UI analysieren.
* Queries auf Tabellen ausführen und vergleichen, die nach unterschiedlichen Spalten geclustert sind (**id** und **id** + **FlightNum**).
* Die Query-Performance mithilfe der Spark UI untersuchen, um die Vorteile von Liquid Clustering zu verstehen.

# 2_1_Class Setup

In diesem Demo arbeiten wir mit **Liquid Clustering**, einer Delta Lake-Optimierungsfunktion, die **Table Partitioning und ZORDER ersetzt**, um Entscheidungen zum Daten-Layout zu vereinfachen und die Query-Performance zu optimieren. Sie bietet die Flexibilität, Clustering-Keys neu zu definieren, ohne die Daten neu schreiben zu müssen. Weitere Informationen finden Sie in der [Dokumentation](https://docs.databricks.com/en/delta/clustering.html).

Führen Sie die folgende Zelle aus, um Ihre Arbeitsumgebung für diesen Kurs zu konfigurieren. Dadurch wird außerdem Ihr perf_opt_lab-Katalog auf Ihren individuellen **labuser**-Katalog gesetzt und das Standardschema auf **perf_opt**. Alle Tabellen werden an diesem Speicherort gelesen und dorthin geschrieben.

```python
%run ./Includes/Classroom-Setup-2L
```

**Output:**

Course Catalog:           labuser15922011_1784595191
Ihr Schema:	      perf_opt_lab
Airline Data Catalog:   dbacademy_flightdata
Airline Schema:	   flightdata

------

Legen Sie **dbacademy_flightdata** als Standardkatalog und **v01** als Schema fest. Für die Demonstration verwenden wir die schreibgeschützten Tabellen an diesem Speicherort.

**HINWEIS:** Diese Tabellen werden über den Databricks Marketplace bereitgestellt, zur Verfügung gestellt von **Databricks**. Der Name des Shares lautet **Airline Performance Data**.

```sql
USE CATALOG dbacademy_flightdata;
USE SCHEMA v01;

SELECT current_catalog(), current_schema()

-- Output:
-- catalog: dbacademy_flightdata   schema: v01
```

