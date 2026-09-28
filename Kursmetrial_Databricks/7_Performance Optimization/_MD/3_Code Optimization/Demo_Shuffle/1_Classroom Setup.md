# 1_Classroom Setup

# [Video Tutorial](https://customer-academy.databricks.com/learn/courses/2958/databricks-performance-optimization/lessons/25481/demo-shuffle)

Shuffle ist ein Spark-Mechanismus, der Daten so umverteilt, dass sie unterschiedlich auf die Partitions verteilt sind. Dies erfordert in der Regel das Kopieren von Daten über Executors und Maschinen hinweg und kann, obwohl manchmal notwendig, eine komplexe und teure Operation sein.

In dieser Demo sehen wir Shuffle in Aktion. Führen Sie die nächste Zelle aus, um die Lektion einzurichten.

Führen Sie die folgende Zelle aus, um Ihre Arbeitsumgebung für diesen Kurs zu konfigurieren. Dadurch wird auch Ihr perf_opt-Katalog auf Ihren eindeutigen **labuser**-Katalog und das Standard-Schema auf **perf_opt** gesetzt. Alle Tabellen werden an diesem Ort gelesen und geschrieben.

```python
%run ./Includes/Classroom-Setup-3
```

**Output:**

Course Catalog:	     labuser15922011_1784595191
Ihr Schema:	        perf_opt
Airline Data Catalog:     dbacademy_flightdata
Airline Schema:	     flightdata

------

Lassen Sie uns den aktuellen Catalog und das aktuelle Schema überprüfen

```sql
SELECT current_catalog(), current_schema()
-- Output:
-- catalog: labuser15922011_1784595191  schema: perf_opt
```

