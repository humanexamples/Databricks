# Dynamische Dateibereinigung (Dynamic File Pruning)

Dynamic File Pruning kann die Performance vieler Abfragen auf Delta-Lake-Tabellen deutlich verbessern. Diese Seite erklärt die Funktionsweise und die Konfiguration.

## Wie funktioniert Dynamic File Pruning?

Der Query-Optimizer aktiviert Dynamic File Pruning für Abfragen mit Filterbedingungen oder `WHERE`-Klauseln. Bei `MERGE`, `UPDATE` und `DELETE` ist dafür Photon-fähiges Compute nötig. Bei `SELECT`-Anweisungen liefert Photon eine breitere und zuverlässigere Dateibereinigung. Auch ohne Photon kann Dynamic File Pruning bei `SELECT`-Anweisungen greifen. Das hängt von der Form der Abfrage und dem Ausführungsplan ab.

Die Funktion arbeitet besonders effizient bei nicht partitionierten Tabellen. Sie hilft auch bei Joins über nicht partitionierte Spalten. Der Performance-Effekt hängt stark vom Clustering der Daten ab. Databricks empfiehlt deshalb Liquid Clustering, um den Nutzen zu maximieren.

## Konfiguration

Drei Apache-Spark-Konfigurationsoptionen steuern Dynamic File Pruning:

- `spark.databricks.optimizer.dynamicFilePruning` (Standard: `true`): Hauptschalter für die Filter-Pushdown-Logik des Optimizers. Bei `false` ist Dynamic File Pruning deaktiviert.
- `spark.databricks.optimizer.deltaTableSizeThreshold` (Standard: 10.000.000.000 Bytes, also 10 GB): Mindestgröße der Delta-Tabelle auf der Probe-Seite des Joins, damit Dynamic File Pruning ausgelöst wird. Ist die Probe-Seite klein, lohnt sich der Filter-Pushdown meist nicht, dann wird einfach die ganze Tabelle gescannt. Die Größe einer Tabelle ermitteln Sie mit dem Befehl `DESCRIBE DETAIL table_name` in der Spalte `sizeInBytes`.
- `spark.databricks.optimizer.deltaTableFilesThreshold` (Standard: 10): Mindestanzahl an Dateien der Delta-Tabelle auf der Probe-Seite, damit Dynamic File Pruning ausgelöst wird. Hat die Tabelle auf der Probe-Seite weniger Dateien als dieser Schwellenwert, wird die Optimierung nicht aktiviert. Hat eine Tabelle nur wenige Dateien, lohnt sich Dynamic File Pruning meist nicht. Die Dateianzahl ermitteln Sie ebenfalls mit `DESCRIBE DETAIL table_name`, in der Spalte `numFiles`.

---
**Quelle:** https://docs.databricks.com/aws/en/optimizations/dynamic-file-pruning  
**Stand:** 2026-08-06
