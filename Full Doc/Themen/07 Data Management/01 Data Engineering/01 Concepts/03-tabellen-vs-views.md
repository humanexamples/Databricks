# Tabellen und Views in Databricks

Databricks bietet vier zentrale Datenobjekte für Data Engineering: Tabellen, Views, materialisierte Views und Streaming-Tabellen. Sie unterscheiden sich in Speicherung und Aktualisierungsverhalten.

## Tabellen

Eine Tabelle ist ein strukturierter Datensatz, der an einem bestimmten Ort gespeichert wird. Der Standardtyp in Databricks ist eine von Unity Catalog verwaltete (Managed) Tabelle. Tabellen unterstützen SQL-Operationen wie `INSERT`, `UPDATE`, `DELETE` und `MERGE INTO`.

## Views

Views sind virtuelle Tabellen, die durch eine Abfrage definiert werden und selbst keine Daten speichern. Sie vereinfachen komplexe Abfragen und kapseln Geschäftslogik, während sie Daten aus einer oder mehreren zugrunde liegenden Tabellen darstellen.

## Materialisierte Views

Wie normale Views, aber mit einem entscheidenden Unterschied: Eine materialisierte View berechnet das Ergebnis der Abfrage vorab und speichert es. Das ermöglicht schnellere Abfragen als bei Standard-Views, kostet aber zusätzlichen Speicherplatz. Sowohl Databricks SQL als auch Lakeflow-Pipelines können diese Objekte erstellen und aktualisieren.

## Streaming-Tabellen

Eine Streaming-Tabelle ist eine von Unity Catalog verwaltete Tabelle, die ihre Verarbeitungslogik über Flows definiert. Sie kann über Databricks SQL oder Lakeflow-Pipelines erstellt und gepflegt werden.

## Materialisierte Views vs. Streaming-Tabellen

Der wesentliche Unterschied liegt in der Verarbeitungsart: <mark style="background:#fff59d;color:#1b1f23;">Materialisierte Views verwenden Batch-Semantik</mark>, <mark style="background:#fff59d;color:#1b1f23;">Streaming-Tabellen verwenden Streaming-Semantik</mark>. Die Wahl zwischen beiden hängt von den Anforderungen des jeweiligen Data-Engineering-Workloads ab.

---
**Quelle:** https://docs.databricks.com/aws/en/data-engineering/tables-views  
**Stand:** 2026-08-07
