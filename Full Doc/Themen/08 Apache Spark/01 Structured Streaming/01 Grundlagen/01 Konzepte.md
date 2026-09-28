# Structured Streaming Konzepte — Referenz

Dieses Dokument beschreibt die Kernkonzepte für die Konfiguration inkrementeller und Near-Realtime-Workloads mit Apache Spark Structured Streaming auf Databricks. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/concepts`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte; die Original-GCP-Seite lieferte nur eine gerenderte Kurzfassung.

## Abschnittsübersicht
1. [Überblick](#ueberblick)
2. [Daten aus einem Stream lesen](#lesen)
3. [In eine Datensenke schreiben](#schreiben)
4. [Zustandsbehaftete und zustandslose Verarbeitung](#zustand)
5. [Überwachen und verwalten](#monitoring)
6. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick</a>

Apache Spark Structured Streaming ist eine Near-Realtime-Verarbeitungs-Engine, die durchgängige Fehlertoleranz mit Exactly-once-Verarbeitungsgarantien bietet und dabei vertraute Spark-APIs verwendet. Structured Streaming erlaubt es, Berechnungen auf Streaming-Daten auf dieselbe Weise auszudrücken wie eine Batch-Berechnung auf statischen Daten. Die Structured-Streaming-Engine führt die Berechnung inkrementell aus und aktualisiert das Ergebnis fortlaufend, sobald Streaming-Daten eintreffen.

Ein schrittweises Tutorial findet sich unter [Führen Sie Ihren ersten Structured-Streaming-Workload aus](https://docs.databricks.com/gcp/en/structured-streaming/tutorial) (siehe auch `Tutorial.md` in diesem Ordner).

## <a id="lesen">2. Daten aus einem Stream lesen</a>

Structured Streaming wird verwendet, um Daten aus unterstützten Datenquellen inkrementell einzulesen.

| Feature | Beschreibung |
| --- | --- |
| [Auto Loader](https://docs.databricks.com/gcp/en/ingestion/cloud-object-storage/auto-loader/) | Neue Datendateien inkrementell und effizient verarbeiten, sobald sie im Cloud-Speicher eintreffen. |
| [Delta-Lake-Tabellen-Streaming-Reads und -Writes](https://docs.databricks.com/gcp/en/structured-streaming/delta-lake) | Delta-Lake-Tabellen als Streaming-Quellen und -Senken mit Exactly-once-Verarbeitungsgarantien verwenden. |
| [Standard-Connectors](https://docs.databricks.com/gcp/en/ingestion/) | Verbindung zu Message Bussen, Queues und Unternehmensanwendungen über Standard-Connectors herstellen. |
| [Micro-Batch-Größe](https://docs.databricks.com/gcp/en/structured-streaming/batch-size) | Eingaberaten begrenzen, um konsistente Batch-Größen zu erhalten und Verarbeitungsverzögerungen zu vermeiden. |

## <a id="schreiben">3. In eine Datensenke schreiben</a>

Konfiguriert, wie Structured Streaming Daten an Zielsysteme ausliefert.

| Feature | Beschreibung |
| --- | --- |
| [Checkpoints](https://docs.databricks.com/gcp/en/structured-streaming/checkpoints) | Verarbeitungszustand speichern, um Fehlertoleranz und Exactly-once-Zustellsemantik zu ermöglichen. |
| [Output-Modus](https://docs.databricks.com/gcp/en/structured-streaming/output-mode) | Zwischen den Modi Append, Update und Complete für zustandsbehaftete Streaming-Queries wählen. |
| [Trigger-Intervalle](https://docs.databricks.com/gcp/en/structured-streaming/triggers) | Trigger-Intervalle setzen, um Latenz und Kosten für die jeweiligen Verarbeitungsanforderungen auszubalancieren. |
| [Real-Time-Modus in Structured Streaming](https://docs.databricks.com/gcp/en/structured-streaming/real-time/) | Daten für Realtime-Workloads mit einer End-to-End-Latenz von bis zu fünf Millisekunden verarbeiten. |

## <a id="zustand">4. Zustandsbehaftete und zustandslose Verarbeitung</a>

Zustandslose Queries verarbeiten Zeilen, ohne Zustand vorzuhalten. Zustandsbehaftete Queries pflegen Zwischenzustand für Aggregationen, Joins und Deduplizierung.

| Feature | Beschreibung |
| --- | --- |
| [Zustandslose Streaming-Queries](https://docs.databricks.com/gcp/en/structured-streaming/stateless-streaming) | Queries optimieren, die Daten verarbeiten, ohne Zwischenzustand vorzuhalten. |
| [Watermarks](https://docs.databricks.com/gcp/en/structured-streaming/watermarks) | Steuern, wie lange Structured Streaming bei zustandsbehafteten Operationen auf verspätet eintreffende Daten wartet. |
| [Zustandsbehaftetes Streaming](https://docs.databricks.com/gcp/en/structured-streaming/stateful-streaming) | Aggregationen, Stream-Stream-Joins und Deduplizierung mithilfe zustandsbehafteter Operatoren verwalten. |

## <a id="monitoring">5. Überwachen und verwalten</a>

Query-Performance verfolgen, Optimierungen anwenden und den Datenzugriff für produktive Structured-Streaming-Workloads steuern.

| Feature | Beschreibung |
| --- | --- |
| [Überwachung mit StreamingQueryListener](https://docs.databricks.com/gcp/en/structured-streaming/stream-monitoring) | Query-Fortschritt und Performance-Metriken über die Spark-UI und die Listener-API verfolgen. |
| [Governance mit Unity Catalog](https://docs.databricks.com/gcp/en/structured-streaming/unity-catalog) | Unity Catalog für Streaming-Workloads mit Governance und Zugriffskontrolle konfigurieren. |

---

## <a id="quellen">6. Quellen</a>

- Structured Streaming concepts (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/concepts
- Structured Streaming concepts (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/concepts

**Stand:** 2026-08-22.
