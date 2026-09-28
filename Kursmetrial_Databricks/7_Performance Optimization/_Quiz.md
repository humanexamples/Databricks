# Quiz

1. **Welche Optimierungsstrategie sollte zuerst neu bewertet werden, wenn ein Shuffle durch eine Join-Operation verursacht wird?**

   - Eine UDF verwenden

   - Die Parallelität erhöhen

   - Den gesamten Cluster-Arbeitsspeicher verringern

   - Die Join-Reihenfolge ändern ✅

2. **Welche zentralen Informationen erfasst Data Skipping auf Dateiebene?**

   - Zeilenanzahl der Datei

   - Minimale und maximale Spaltenstatistiken ✅

   - Erstellungsdatum der Datei

   - Zugriffssteuerungslisten der Datei

3. **Bei welcher Art von Operation in Spark tritt Shuffling als notwendiger Nebeneffekt auf?**

   - Spaltenauswahl

   - Wide Transformations ✅

   - Filteroperationen

   - Narrow Transformations

4. **Liquid Clustering verringert den gedanklichen Aufwand, da man sich nicht mehr kümmern muss um:**

   - Parallelität auf Zeilenebene
   - Syntax der Clustering-Schlüssel
   - Zieldateigröße
   - Kardinalität ✅??

5. **Gegen welches große Problem ist Liquid Clustering im Gegensatz zur klassischen Partitionierung immun?**

   - Entstehung kleiner Dateien
   - Joins mit hoher Kardinalität
   - Data Skew ✅
   - Write Amplification

6. **Welche Spark-Funktion mildert Data Skew automatisch, indem große Partitionen aufgeteilt werden?**

   - Partition Filtering
   - Adaptive Query Execution ✅
   - Broadcast Hash Join
   - Cost-Based Optimizer

7. **Predictive Optimization unterstützt Wartungsoperationen wie OPTIMIZE und welchen weiteren Befehl?**

   - DESCRIBE
   - ZORDER
   - REFRESH
   - VACUUM ✅

8. **Was ist der Hauptvorteil, das Spark-Caching beim Testen von Performance-Optimierungen zu deaktivieren?**

   - Es stellt sicher, dass Dateien für jede Abfrage immer aus dem Cloud-Speicher gelesen werden ✅
   - Es ermöglicht Broadcast Joins
   - Es erhöht die Speichernutzung
   - Es beschleunigt Abfragen

9. **Was sollte bei den Cluster-Workern optimiert werden, um die Netzwerk-I/O während eines Shuffles zu verringern?**

   - Weniger, dafür größere Worker verwenden ✅
   - Kleinere Worker verwenden
   - Dedizierte Driver-Knoten verwenden
   - Mehr Worker verwenden

10. **Was ist die wichtigste Folge von starkem Data Skew in einem verteilten System?**

- Höherer Serialisierungsaufwand
- Mehr Arbeit wird von einem einzigen Executor erledigt ✅
- Das Delta Log kann nicht gelesen werden
- Probleme mit der Datenkonsistenz

11. **Welcher Faktor wirkt sich direkt auf die Performance aus, weil Worker mehr Daten abrufen müssen?**

- Anzahl gelesener Bytes ✅
- Parallelität
- Komplexität der Abfrage
- CPU-Frequenz

12. **Bei welcher Transformation werden Daten über verschiedene Partitionen hinweg kombiniert, sodass ein Shuffle erforderlich ist?**

- filter()
- select()
- groupBy() ✅
- limit()

13. **Welche Komponente übernimmt die übergreifende Koordination einer Spark-Anwendung?**

- Driver ✅
- Worker-Knoten
- Stage
- Executor

14. **Welche SQL-Warehouse-Option ist serverless und bietet einen sofortigen Start bei niedrigeren Gesamtbetriebskosten (TCO)?**

- Serverless SQL Warehouse ✅
- Isolated SQL Warehouse
- Standard SQL Warehouse
- Pro SQL Warehouse

15. **Welcher Filtertyp wird in der Reihenfolge des Data Skipping am frühesten angewendet?**

- Column Masks
- Partition Filters ✅
- Data Filters
- Pushed Filters

16. **Welche Konfigurationseinstellung erhöht bei einem zu hohen Wert die Wahrscheinlichkeit eines Spills?**

- spark.shuffle.service.enabled
- spark.sql.shuffle.partitions
- spark.driver.memory
- spark.sql.files.maxPartitionBytes ✅

17. **Welcher Begriff beschreibt in Spark das Verschieben von Daten vom RAM auf die Festplatte und wieder zurück in den RAM?**

- Spill ✅
- Garbage Collection
- Serialisierung
- Shuffling

18. **Wie geht Databricks bei Schreibvorgängen in der Regel mit dem Problem kleiner Dateien um?**

- spark.sql.shuffle.partitions erhöhen
- Kleine Dateien mit Auto-Optimize automatisch komprimieren ✅
- Den Data Skew verringern
- Manuelle Komprimierung der Dateien

19. **Welche Compute-Option von Databricks ist speziell darauf ausgelegt, den Infrastrukturbedarf von Workloads automatisch zu verwalten?**

- Serverless Compute ✅
- All-Purpose Compute
- Instance Pools
- Job Compute

20. **Welche teure Operation sollte vermieden werden, um das Spill-Risiko zu minimieren?**

- explode() ✅
- limit()
- select()
- filter()
