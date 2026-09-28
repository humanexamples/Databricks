# Real-Time Mode in Structured Streaming — Referenz

Dieses Dokument ist die Einstiegs-/Übersichtsseite (Landing Page) zum Thema "Real-Time Mode" in Apache Spark Structured Streaming auf Databricks. Es fasst zusammen, was Real-Time Mode ist, und verlinkt auf die vertiefenden Detailseiten. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte (die GCP-Originalseite selbst lieferte über WebFetch nur eine gekürzte/paraphrasierte Fassung).

## Abschnittsübersicht

1. [Was ist Real-Time Mode?](#was-ist-real-time-mode)
2. [Erste Schritte](#erste-schritte)
3. [Real-Time-Anwendungen bauen](#anwendungen-bauen)
4. [Quellen](#quellen)

---

## <a id="was-ist-real-time-mode">1. Was ist Real-Time Mode?</a>

Real-Time Mode ist ein Trigger-Typ von Structured Streaming mit einer End-to-End-Latenz von bis zu fünf Millisekunden. Er wird für operative Workloads eingesetzt, die sofort auf Streaming-Daten reagieren müssen, etwa Betrugserkennung (Fraud Detection) und Echtzeit-Personalisierung.

Real-Time Mode verwendet dieselben Structured-Streaming-APIs wie der Micro-Batch-Verarbeitungsmodus. Aktiviert wird er, indem der Real-Time-Trigger auf einer Streaming-Query gesetzt wird. Zum Vergleich mit den anderen Structured-Streaming-Trigger-Typen siehe die Doku-Seite "Configure Structured Streaming trigger intervals".

Real-Time Mode ist außerdem in Lakeflow-Pipelines verfügbar (siehe "Use real-time mode in Lakeflow pipelines").

## <a id="erste-schritte">2. Erste Schritte</a>

| Seite | Beschreibung |
| --- | --- |
| Real-Time Mode einrichten (`setup`) | Klassisches Compute konfigurieren, den Real-Time-Trigger aktivieren und die Cluster-Größe festlegen. |
| Real-Time-Mode-Konzepte (`concepts`) | Lernen, wie Real-Time Mode funktioniert und wann er statt Micro-Batch-Modus eingesetzt werden sollte. |
| Tutorial: Einen Real-Time-Streaming-Workload ausführen (`tutorial`) | Die erste Streaming-Query mit dem Real-Time-Trigger und einer Rate-Quelle ausführen. |

## <a id="anwendungen-bauen">3. Real-Time-Anwendungen bauen</a>

| Seite | Beschreibung |
| --- | --- |
| Performance von Real-Time-Mode-Queries optimieren und überwachen (`performance`) | Compute abstimmen, End-to-End-Latenz reduzieren und Query-Performance mit eingebauten Metriken überwachen. |
| Real-Time-Mode-Einschränkungen (`limitations`) | Bekannte Einschränkungen für Quellen, Unions und `mapPartitions` verstehen. |
| Real-Time-Mode-Referenz (`reference`) | Unterstützte Umgebungen, Sprachen, Compute-Typen, Quellen, Senken und Operatoren nachschlagen. |
| Real-Time-Mode-Beispiele (`examples`) | Code-Beispiele für Kafka, Kinesis, Lakebase, zustandsbehaftete Queries und benutzerdefinierte Senken erkunden. |

---

## <a id="quellen">4. Quellen</a>

- Real-time mode in Structured Streaming (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/real-time/
- Real-time mode in Structured Streaming (Mirror, Azure, verifiziert/vollständig abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/
- Real-time mode in Structured Streaming (AWS): https://docs.databricks.com/aws/en/structured-streaming/real-time/

**Stand:** 2026-08-22.
