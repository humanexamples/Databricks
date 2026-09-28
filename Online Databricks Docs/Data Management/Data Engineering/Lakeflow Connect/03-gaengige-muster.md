# Gängige Muster für Managed-Ingestion-Pipelines

Diese Seite fasst Konfigurationsmuster zusammen, mit denen sich Lakeflow-Connect-Ingestion-Pipelines optimieren lassen. Nicht alle Konnektoren unterstützen alle hier beschriebenen Muster.

## Verfügbare Muster

1. **Spaltenauswahl** – Datenvolumen reduzieren, indem bestimmte Spalten bei der Aufnahme ein- oder ausgeschlossen werden.
2. **Delta-Tabelleneigenschaften** – Delta-Lake-Konfigurationen wie Type Widening über die Pipeline-Spezifikation auf Zieltabellen anwenden.
3. **Full Refresh** – vollständiges Neuladen der Daten aus dem Quellsystem.
4. **Liquid Clustering** – Datenlayout und Abfrageperformance der Zieltabelle optimieren.
5. **History Tracking** – Slowly Changing Dimension (SCD) Typ 2 zur Nachverfolgung historischer Änderungen implementieren.
6. **Kosten überwachen** – Systemtabellen zur Kostenverfolgung und Nutzungsanalyse von Pipelines nutzen.
7. **Multi-Destination-Pipelines** – Daten aus einer Quelle in mehrere Zieltabellen oder -kataloge routen.
8. **Pipeline-Wartung** – Updates, Pausen und Troubleshooting verwalten.
9. **Pipeline-Tagging** – organisatorische Tags für Ressourcenverwaltung und Kostenzuordnung vergeben.
10. **Zeilenfilterung** – SQL-ähnliche Bedingungen zur Filterung von Zeilen bei der Aufnahme anwenden.
11. **Smart Closure** – automatische Beendigung von CDC-Pipelines, sobald die Quelle eingeholt wurde.
12. **Run as-Identität** – Berechtigungsidentität für die Pipeline-Ausführung festlegen.
13. **Herkunft der Quelldaten (Lineage)** – Herkunft der Quelltabellen in Unity Catalog nachverfolgen.
14. **Zieltabellen benennen** – individuelle Benennung von Zieltabellen, nützlich bei doppelten Quellen.
15. **TLS-Server-Zertifikatsprüfung** – Sicherheit von Datenbank-Konnektoren überprüfen und Man-in-the-Middle-Angriffe verhindern.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/common-patterns  
**Stand:** 2026-08-07
