# **Databricks Delta Lake und Statistiken**

Für effektives **Data Skipping** und **Z-Ordering** in Delta Lake ist es notwendig, **Statistiken** über Ihre Daten zu sammeln. **Standardmäßig sammelt Databricks Delta Lake Statistiken für die ersten 32 Spalten einer Tabelle** und erfasst dabei Werte wie **Min** und **Max** **für jede Spalte** in den Datei-Metadaten. **Diese Statistiken ermöglichen es Spark, zu erkennen, welche Dateien wahrscheinlich relevante Query-Ergebnisse enthalten**, sodass Dateien übersprungen werden können, die nicht den Filterkriterien entsprechen. 

So können beispielsweise reine Metadaten-Queries, wie das Ermitteln des Maximalwerts einer Spalte, beantwortet werden, ohne dass Datendateien gelesen werden müssen — vorausgesetzt, es sind Statistiken vorhanden. 

Allerdings gibt es einige Einschränkungen. Filter werden in folgender Reihenfolge angewendet: 

- Erstens: **Partition Filters**
- Zweitens: **Data Filters**
- und dann **Pushed Filters**

Aufgrund **möglicher Präzisions- oder Trunkierungsprobleme** führen Statistiken für **Timestamp**- und **String**-Spalten nicht immer zu exakten Übereinstimmungen, sodass gelegentlich auf das Scannen der Dateien zurückgegriffen werden muss. 

Es empfiehlt sich außerdem, **die Erfassung von Statistiken für Spalten mit langen Strings zu vermeiden**, indem man entweder

- sie **außerhalb der ersten 32 Spalten** platziert 
- oder **Konfigurationseinstellungen anpasst, um die Query-Geschwindigkeit** und Systemeffizienz zu erhalten.

- Databricks Delta Lake sammelt Statistiken über die ersten N Spalten
  - `dataSkippingNumIndexedCols = 32`
- Diese Statistiken werden in Queries verwendet:
  - Reine Metadaten-Queries: `select max(col) from table`
- Fragt nur das Delta Log ab, muss die Dateien nicht ansehen, wenn die Spalte über Statistiken verfügt
  - Ermöglicht es, Dateien zu überspringen
- Partition Filters, **Data Filters**, Pushed Filters werden in dieser Reihenfolge angewendet
  - Timestamp- und String-Typen sind nicht immer sehr nützlich
- Präzision/Trunkierung verhindern exakte Übereinstimmungen, manchmal muss auf die Dateien zurückgegriffen werden
- Vermeiden Sie die Erfassung von Statistiken für lange Strings
  - Platzieren Sie sie außerhalb der ersten 32 Spalten oder erfassen Sie Statistiken für weniger Spalten 
- alter table change column col after col32
- `set spark.databricks.delta.properties.defaults.dataSkippingNumIndexedCols = 3`
