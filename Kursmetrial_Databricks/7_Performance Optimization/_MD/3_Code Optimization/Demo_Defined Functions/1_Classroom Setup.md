# 1_Classroom Setup

# [Video Tutorial](https://customer-academy.databricks.com/learn/courses/2958/databricks-performance-optimization/lessons/25497/demo-user-defined-functions)

Databricks empfiehlt, wann immer möglich native Funktionen zu verwenden. UDFs sind zwar eine großartige Möglichkeit, die Funktionalität von Spark SQL zu erweitern, ihre Verwendung erfordert jedoch die Übertragung von Daten zwischen Python und Spark, was wiederum **Serialisierung erfordert**. **Dies verlangsamt Queries drastisch.**

Manchmal sind UDFs jedoch notwendig. Sie können ein **besonders leistungsfähiges Werkzeug für ML- oder NLP-Anwendungsfälle sein, für die es möglicherweise kein natives Spark-Äquivalent gibt.**

Führen Sie die folgende Zelle aus, um Ihre Arbeitsumgebung für diesen Kurs zu konfigurieren. Dadurch wird außerdem Ihr perf_opt-Catalog auf Ihren eindeutigen **labuser**-Catalog gesetzt und das Standard-Schema auf **perf_opt**. Alle Tabellen werden aus diesem Speicherort gelesen und dorthin geschrieben.

```python
%run ./Includes/Classroom-Setup-5
```

**Output:**

Course Catalog:    labuser15922011_1784595191
Ihr Schema:	perf_opt

Lassen Sie uns den aktuellen Catalog und das aktuelle Schema überprüfen

```sql
SELECT current_catalog(), current_schema()

# Output:
# catalog: labuser15922011_1784595191
# schema: perf_opt
```

