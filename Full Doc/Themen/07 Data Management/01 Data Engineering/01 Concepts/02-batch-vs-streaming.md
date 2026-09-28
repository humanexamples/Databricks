# Batch vs. Streaming Datenverarbeitung

Databricks unterstützt zwei unterschiedliche Verarbeitungsansätze für Data-Engineering-Workloads. Die einheitliche Architektur auf Basis von Apache Spark und Structured Streaming erlaubt es, Datenquellen flexibel für beide Methoden zu nutzen.

## Kernunterschiede

**Batch-Verarbeitung:** Die Engine verarbeitet alle aktuell in der Quelle verfügbaren Daten, ohne frühere Ausführungen zu berücksichtigen – bei jedem Lauf werden alle verfügbaren Daten verarbeitet. Dieser Ansatz nutzt meist eine logische Partitionierung, um die Neuverarbeitung zu begrenzen.

**Streaming-Verarbeitung:** Das System merkt sich, welche Daten bereits verarbeitet wurden, und verarbeitet in nachfolgenden Läufen nur neue Daten.

## Vor- und Nachteile

| Ansatz | Stärken | Herausforderungen |
| --- | --- | --- |
| Batch | Einfache Logik; präzise Ergebnisse über alle verfügbaren Daten | Ineffiziente Neuverarbeitung; höhere Latenz (Stunden bis Minuten) |
| Streaming | Verarbeitet nur neue Daten; Latenz im Sekunden-/Millisekundenbereich | Komplexe zustandsbehaftete Operationen; mögliche Genauigkeitsprobleme bei verspätet eintreffenden Daten |

## Empfohlene Strategie nach Medallion-Architektur

- **Bronze-Schicht (Ingestion):** Streaming empfohlen für zustandslose Append-Operationen.
- **Silver-Schicht (Transformation):** Batch mit inkrementellem Refresh bevorzugt; Streaming optional, wenn niedrige Latenz wichtiger ist als Genauigkeit.
- **Gold-Schicht (Aggregationen):** Batch-Verarbeitung mit inkrementellem Refresh empfohlen.

Der Umgang mit verspätet eintreffenden Daten unterscheidet sich deutlich: Batch berechnet frühere Ergebnisse automatisch neu, während Streaming zusätzliche Logik zur Zustandsverwaltung benötigt.

---
**Quelle:** https://docs.databricks.com/aws/en/data-engineering/batch-vs-streaming  
**Stand:** 2026-08-07
