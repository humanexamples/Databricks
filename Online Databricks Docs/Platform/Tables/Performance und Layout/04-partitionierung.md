# Wann sollte man Tabellen partitionieren?

Die meisten Tabellen brauchen keine Partitionierung. Databricks empfiehlt stattdessen Liquid Clustering für fast alle Fälle.

> **Hinweis:** Databricks empfiehlt Liquid Clustering für alle Managed Tables. Bei Managed Tables mit Apache Iceberg unterstützt Unity Catalog nur Liquid Clustering. `PARTITION BY`-Spalten werden dabei als Clustering-Keys interpretiert. Siehe „Partitionierte Tabelle zu Liquid Clustering konvertieren".

Die meisten Tabellen mit weniger als 100 TB Daten brauchen keine Partitionierung. Databricks nutzt standardmäßig Delta Lake für alle Tabellen. Unpartitionierte Tabellen werden automatisch nach Ingestion-Zeit geclustert. Dadurch erhält man partitionsähnliche Performance ohne manuelles Tuning. Eine eigene Partitionierungsstrategie lohnt sich nur, wenn sie diese Standardeinstellung übertrifft.

## Eigene Partitionierungsstrategien

Erfahrene Nutzer von Apache Spark und Delta Lake können eine Partitionierungsstrategie finden, die besser ist als das Standard-Ingestion-Time-Clustering.

> **Warnung:** Eine ungeeignete Partitionierungsstrategie kann die Abfrageperformance verschlechtern. Um das zu korrigieren, ist oft ein vollständiges Neuschreiben der Daten nötig. Das kann bei großen Tabellen sehr teuer und langsam sein.

Bevor man eigene Partitionierungsstrategien einsetzt, empfiehlt Databricks Liquid Clustering für alle Tabellen und Predictive Optimization für Unity-Catalog-Managed-Tables.

Um eine bestehende partitionierte Delta-Lake-Tabelle zu Liquid Clustering zu konvertieren, nutzt man `ALTER TABLE ... REPLACE PARTITIONED BY WITH CLUSTER BY`. Liquid Clustering funktioniert sowohl für Spalten mit niedriger als auch mit hoher Kardinalität. Es vermeidet die festen Partitionsgrenzen und das Problem vieler kleiner Dateien, das bei statischer Partitionierung häufig auftritt.

## Unterstützte Datentypen für Partitionsspalten

Partitionierung unterstützt folgende Datentypen für Partitionsspalten:

- Date
- Timestamp
- TimestampNTZ
- Interval
- String
- Binary
- Boolean
- Integer, Long, Short, Byte
- Float, Double, Decimal

Partitionsspalten müssen Top-Level-Spalten sein. Folgende Typen sind als Partitionsspalte nicht möglich:

- Komplexe Typen wie `StructType`, `MapType`, `ArrayType` oder `VariantType`
- Struct-Felder wie `struct_col.field`. Delta Lake behandelt ein Struct-Feld in `PARTITIONED BY` als Ausdruck, nicht als Spaltenreferenz.

Um eine Tabelle nach einem Struct-Feld zu organisieren, nutzt man stattdessen Liquid Clustering. Es erkennt ein Struct-Feld als Clustering-Key. Liquid Clustering ist der einzige Weg, um Data Skipping auf einem Struct-Feld zu nutzen, ohne es vorher in eine Top-Level-Spalte zu extrahieren.

## Mindestgrößen-Empfehlungen

Partitionierung unterhalb dieser Mindestgrößen verschlechtert die Abfrageperformance eher, als dass sie sie verbessert. Folgende Punkte sollte man bei der Entscheidung berücksichtigen:

- Für Tabellen:
  - Unter 1 TB Daten: nicht partitionieren.
  - Zwischen 1 TB und 100 TB Daten: Liquid Clustering statt Partitionierung nutzen. Partitionierung verschlechtert hier die Performance häufiger, als dass sie hilft.
  - Ab 100 TB Daten: Partitionierung kann die Performance verbessern. Databricks empfiehlt aber, zuerst Liquid Clustering auszuprobieren und die Verbesserung zu prüfen.
- Für Partitionen: Jede Partition sollte mindestens 1 GB Daten enthalten. Tabellen mit wenigen, großen Partitionen performen meist besser als Tabellen mit vielen kleinen Partitionen.

## Ingestion Time Clustering nutzen

Mit Delta Lake nutzen unpartitionierte Tabellen automatisch Ingestion Time Clustering. Das bringt ähnliche Performance-Vorteile wie eine Partitionierungsstrategie mit Datumsfeldern, ganz ohne manuelles Optimieren oder Tuning.

> **Hinweis:** Um Ingestion Time Clustering bei vielen `UPDATE`- oder `MERGE`-Anweisungen auf einer Tabelle zu erhalten, empfiehlt Databricks Liquid Clustering auf einer Spalte, die der Ingestion-Reihenfolge entspricht, zum Beispiel ein Event-Timestamp oder ein Erstellungsdatum.

## Kompatibilität zwischen Delta Lake und Parquet bei der Partitionierung

Delta Lake nutzt Parquet zur Datenspeicherung. Manche partitionierten Delta-Lake-Tabellen haben ein Datenlayout, das dem von Parquet-Tabellen mit Apache Spark ähnelt. Apache Spark nutzt Hive-Style-Partitionierung beim Speichern von Daten im Parquet-Format. Hive-Style-Partitionierung ist kein Teil des Delta-Lake-Protokolls. Workloads sollten sich beim Zugriff auf Delta-Lake-Tabellen nicht auf diese Partitionierungsstrategie verlassen.

Databricks empfiehlt, mit Delta Lake gespeicherte Daten nur über offiziell unterstützte Clients und APIs zu nutzen. Viele Delta-Lake-Features brechen mit Annahmen über das Datenlayout, die bei Parquet, Hive oder früheren Delta-Lake-Protokollversionen galten.

> **Hinweis:** Wenn Column Mapping für eine Delta-Lake-Tabelle aktiviert ist, ersetzen zufällige Präfixe die Spaltennamen in den Partitionsverzeichnissen der Hive-Style-Partitionierung.

## Delta-Lake-Partitionierung im Vergleich zu anderen Data Lakes

Partitionierungstechniken, die in anderen Open-Source-Technologien wie Apache Spark, Parquet, Hive und Hadoop nützlich sind, gelten nicht immer für Databricks. Falls man eine Tabelle trotzdem partitioniert, sollte man Folgendes beachten:

- Transaktionen sind nicht an Partitionsgrenzen gebunden. Delta Lake garantiert ACID-Eigenschaften über Transaktionslogs. Man muss einen Datenbatch also nicht nach Partition trennen, um Atomarität zu garantieren.
- Databricks-Compute-Cluster haben keine Datenlokalität, die an physische Medien gebunden ist. Ins Lakehouse aufgenommene Daten liegen in Cloud Object Storage. Während der Datenverarbeitung werden Daten zwar lokal zwischengespeichert, aber Databricks nutzt dateibasierte Statistiken, um die minimale Datenmenge für paralleles Laden zu bestimmen.

## Z-Order und Partitionen

> **Hinweis:** Databricks empfiehlt Liquid Clustering statt Z-Ordering für alle neuen Tabellen.

Man kann Z-Order-Indizes zusammen mit Partitionen nutzen, um Abfragen auf großen Datensätzen zu beschleunigen. Die meisten Tabellen nutzen Ingestion Time Clustering, sodass ein Tuning von Z-Order und Partitionen nicht nötig ist.

Folgende Regeln sollte man bei der Planung einer Optimierungsstrategie mit Partitionsgrenzen und Z-Order beachten:

- Z-Order benötigt den Befehl `OPTIMIZE`. Dateien können nicht über Partitionsgrenzen hinweg zusammengeführt werden. Z-Order-Clustering funktioniert deshalb nur innerhalb einer Partition. Bei unpartitionierten Tabellen können Dateien über die gesamte Tabelle hinweg zusammengeführt werden.
- Partitionierung funktioniert nur gut bei Feldern mit niedriger oder bekannter Kardinalität, zum Beispiel Datumsfeldern oder physischen Standorten. Bei Feldern mit hoher Kardinalität, etwa Timestamps, funktioniert sie nicht gut. Z-Order funktioniert dagegen für alle Felder, auch für Felder mit hoher oder unbegrenzt wachsender Kardinalität, zum Beispiel Timestamps oder die Kunden-ID in einer Transaktions- oder Bestelltabelle.
- Man kann kein Z-Order auf Feldern anwenden, die zur Partitionierung genutzt werden.

## Wie Databricks um bestehende Partitionen herum optimiert

Viele Kunden migrieren von Parquet-basierten Data Lakes zu Delta Lake, zum Beispiel mit der Anweisung `CONVERT TO DELTA`. Damit wird eine bestehende Parquet-basierte Tabelle in eine Delta-Lake-Tabelle umgewandelt, ohne bestehende Daten neu zu schreiben. Da die Konvertierung bestehende Daten nicht neu schreibt, übernehmen große Tabellen oft frühere Partitionierungsstrategien.

Manche Databricks-Optimierungen nutzen diese Partitionen, wo möglich. Das mildert negative Performance-Effekte von Partitionierungsstrategien ab, die nicht für Delta Lake optimiert wurden.

Delta Lake und Apache Spark sind Open-Source-Technologien. Databricks hat zwar Features, die die Abhängigkeit von Partitionierung reduzieren. Die Open-Source-Community kann aber neue Features bauen, die zusätzliche Komplexität mit sich bringen.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/partitions  
**Stand:** 2026-08-06
