# 1_Classroom Setup

In diesem Lab arbeiten wir daran, die Query-Performance eines exploding joins zwischen 3 Tabellen zu verbessern:

- **transactions**
- **stores**
- **countries**

Wir wollen den durch den exploding join verursachten Spill herbeiführen und identifizieren und die Performance des joins schrittweise verbessern.

#### Hinweise zum Lab

Um erfolgreich einen exploding join zu erzeugen, der auf die Festplatte spillt, mussten wir gezielt die folgenden Optimierungen deaktivieren:

- Predictive Optimization ([AWS](https://docs.databricks.com/aws/en/optimizations/predictive-optimization) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/optimizations/predictive-optimization) | [GCP](https://docs.databricks.com/gcp/en/optimizations/predictive-optimization)) für von Unity Catalog verwaltete Tabellen im **lab**-Schema.
- Broadcast joins, um die Performance-Verbesserungen durch die Anpassung der join-Strategie schrittweise zu demonstrieren.

Führen Sie die folgende Zelle aus, um Ihre Arbeitsumgebung für diesen Kurs zu konfigurieren. Dadurch wird außerdem Ihr perf_opt_lab-Catalog auf Ihren eindeutigen **labuser**-Catalog gesetzt und das Standardschema auf **perf_opt_lab**. Alle Tabellen werden von diesem Ort gelesen und dorthin geschrieben.

------

```python
%run ./Includes/Classroom-Setup-4L
```

**Ausgabe:**

Course Catalog:	   labuser15922011_1784595191
Ihr Schema:	       perf_opt_lab
Airline Data Catalog:    dbacademy_flightdata
Airline Schema:	     flightdata

------

