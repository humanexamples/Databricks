# 1_1_Classroom Setup

# [Video Tutorial](https://customer-academy.databricks.com/learn/courses/2958/databricks-performance-optimization/lessons/25476/demo-file-explosion)

**File Explosion:** Viele Data Engineers partitionieren ihre Tabellen auf eine Weise, die erhebliche Performance-Probleme verursachen kann, ohne die künftige Query-Performance zu verbessern. Dies wird als "**Over Partitioning**" bezeichnet. In diesem Demo sehen wir uns an, wie sich das in der Praxis auswirkt.

##### Nützliche Referenzen

- Partitioning Recommendations: [AWS](https://docs.databricks.com/aws/en/tables/partitions) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/tables/partitions) | [GCP](https://docs.databricks.com/gcp/en/tables/partitions)
- CREATE TABLE Syntax: [AWS](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-using) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/sql-ref-syntax-ddl-create-table-using) | [GCP](https://docs.databricks.com/gcp/en/sql/language-manual/sql-ref-syntax-ddl-create-table-using)
- About ZORDER: [AWS](https://docs.databricks.com/aws/en/delta/data-skipping) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/delta/data-skipping) | [GCP](https://docs.databricks.com/gcp/en/delta/data-skipping)
- About Liquid Clustering: [AWS](https://docs.databricks.com/aws/en/delta/clustering) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/delta/clustering) | [GCP](https://docs.databricks.com/gcp/en/delta/clustering)
- 

### Demo-Zusammenfassung

Bei der Tabelle **iot_data** werden wir die Tabelle beim Speichern nicht partitionieren. In diesem Beispiel überlassen wir den Speichervorgang Spark. Obwohl der Datensatz deutlich größer ist als die partitionierte Tabelle aus dem ersten Beispiel, optimiert Spark, wie die Daten gespeichert werden. Es werden 32 Dateien für die Tabelle erzeugt, wobei jede Datei eine ausgewogene Anzahl an Zeilen enthält. So wird das "Small File"-Problem vermieden, das bei der partitionierten Tabelle im vorherigen Beispiel auftrat.

Führen Sie die folgende Zelle aus, um Ihre Arbeitsumgebung für diesen Kurs zu konfigurieren. Dadurch wird außerdem Ihr perf_opt-Katalog auf Ihren eindeutigen **labuser**-Katalog gesetzt und das Standardschema auf **perf_opt**. Alle Tabellen werden an diesem Ort gelesen und geschrieben.

```python
%run ./Includes/Classroom-Setup-1

# Output:
# Course Catalog:	labuser15922011_1784595191
# Your Schema:	    perf_opt
```

```sql
SELECT current_catalog(), current_schema()

# Output:
# catalog: labuser15922011_1784595191   schema: perf_opt
```