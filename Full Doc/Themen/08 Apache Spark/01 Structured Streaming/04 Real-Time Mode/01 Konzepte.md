# Real-Time-Mode-Konzepte — Referenz

Dieses Dokument beschreibt die Konzepte hinter Real-Time Mode in Structured Streaming: was er ist, wie er niedrige Latenz erreicht und wann er gegenüber dem Standard-Micro-Batch-Modus eingesetzt werden sollte. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/concepts`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte.

## Abschnittsübersicht

1. [Was ist Real-Time Mode?](#was-ist-real-time-mode)
2. [Wie Real-Time Mode niedrige Latenz erreicht](#niedrige-latenz)
3. [Wann Real-Time Mode eingesetzt werden sollte](#wann-einsetzen)
4. [Feature-Unterstützung und Einschränkungen](#feature-unterstuetzung)
5. [Quellen](#quellen)

---

## <a id="was-ist-real-time-mode">1. Was ist Real-Time Mode?</a>

Real-Time Mode ist ein Trigger-Typ für Structured Streaming, der ultra-niedrige Latenz bei der Datenverarbeitung ermöglicht — mit einer End-to-End-Latenz von bis zu fünf Millisekunden. Real-Time Mode wird für operative Workloads eingesetzt, die eine sofortige Reaktion auf Streaming-Daten erfordern, etwa Betrugserkennung (Fraud Detection) und Echtzeit-Personalisierung.

Real-Time Mode ist außerdem in Lakeflow-Pipelines verfügbar (siehe "Use real-time mode in Lakeflow pipelines").

## <a id="niedrige-latenz">2. Wie Real-Time Mode niedrige Latenz erreicht</a>

Real-Time Mode verbessert die Ausführungsarchitektur durch:

- Ausführung lang laufender Batches (Standard: fünf Minuten), in denen das System Daten verarbeitet, sobald sie in der Quelle verfügbar werden.
- Gleichzeitige Planung (Scheduling) aller Query-Stages. Dies erfordert, dass die Anzahl verfügbarer Task-Slots gleich oder größer ist als die Anzahl der Tasks über alle Stages eines Batches hinweg.
- Weitergabe von Daten zwischen Stages sofort nach deren Erzeugung mittels Streaming-Shuffle.

Zwischen den Batches checkpointet Structured Streaming den Fortschritt und veröffentlicht Metriken. Die Batch-Dauer beeinflusst die Checkpointing-Häufigkeit:

- Bei längeren Batches erfolgt Checkpointing seltener, was längere Replays im Fehlerfall und eine verzögerte Verfügbarkeit von Metriken bedeutet.
- Bei kürzeren Batches erfolgt Checkpointing häufiger, was sich auf die Latenz auswirken kann.

Databricks empfiehlt, Real-Time Mode gegen den jeweiligen Ziel-Workload zu benchmarken, um das passende Trigger-Intervall zu finden.

## <a id="wann-einsetzen">3. Wann Real-Time Mode eingesetzt werden sollte</a>

Real-Time Mode auswählen, wenn der Anwendungsfall Folgendes erfordert:

- **Latenz unter einer Sekunde:** Anwendungen, die innerhalb von Millisekunden auf Daten reagieren müssen. Beispiel: eine Kreditkartentransaktion in Echtzeit blockieren oder markieren, wenn ein Betrugs-Score aufgrund ungewöhnlichen Standorts, großer Transaktionssumme oder schneller Ausgabenmuster einen Schwellenwert überschreitet.
- **Operative Entscheidungsfindung:** Systeme, die aufgrund eingehender Daten sofort Aktionen auslösen. Beispiel: eine Werbenachricht ausliefern, wenn Clickstream-Daten zeigen, dass ein Nutzer nach einem Produkt sucht, und einen Rabatt anbieten, falls er innerhalb der nächsten 15 Minuten kauft.
- **Kontinuierliche Verarbeitung:** Workloads, bei denen Daten sofort bei Eintreffen verarbeitet werden müssen, statt in periodischen Batches.

Micro-Batch-Modus (der Standard-Trigger von Structured Streaming) einsetzen, wenn der Anwendungsfall Folgendes erfordert:

- **Analytische Verarbeitung:** ETL-Pipelines, Datentransformationen und Medallion-Architektur-Implementierungen, bei denen Latenzanforderungen in Sekunden oder Minuten gemessen werden.
- **Kostenoptimierung:** Workloads, bei denen keine Sub-Sekunden-Latenz erforderlich ist, da Real-Time Mode dedizierte Compute-Ressourcen benötigt.
- **Schnellere Wiederherstellung:** Workloads, die häufige Checkpoints benötigen, um die Replay-Zeit nach einem Fehler zu minimieren.

## <a id="feature-unterstuetzung">4. Feature-Unterstützung und Einschränkungen</a>

Eine vollständige Liste unterstützter Umgebungen, Sprachen, Compute-Typen, Quellen, Senken und Operatoren sowie bekannter Einschränkungen findet sich in der Real-Time-Mode-Referenz (siehe Datei `Referenz.md`).

---

## <a id="quellen">5. Quellen</a>

- Real-time mode concepts (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/real-time/concepts
- Real-time mode concepts (Mirror, Azure, verifiziert/vollständig abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/concepts
- Real-time mode concepts (AWS): https://docs.databricks.com/aws/en/structured-streaming/real-time/concepts

**Stand:** 2026-08-22.
