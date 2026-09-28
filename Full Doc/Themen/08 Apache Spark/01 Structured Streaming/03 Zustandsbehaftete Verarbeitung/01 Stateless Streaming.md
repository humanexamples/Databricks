# Stateless Streaming optimieren — Referenz

Dieses Dokument beschreibt Optimierungsfunktionen für zustandslose ("stateless") Structured-Streaming-Queries in Databricks Runtime 18.0 und höher. Verifiziert per `WebFetch` gegen die GCP-Original-URL sowie ergänzend gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/stateless-streaming`), die eine vollständige, wörtliche Wiedergabe des Roh-Inhalts lieferte.

## Abschnittsübersicht
1. [Überblick](#ueberblick)
2. [Adaptive Query Execution und Auto Optimized Shuffle](#aqe-aos)
3. [Shuffle-Partitionen beim Neustart einer Query ändern](#shuffle-partitionen-aendern)
4. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick</a>

Zustandslose ("stateless") Structured-Streaming-Queries verarbeiten Daten, ohne Zwischenzustand ("intermediate state") zu pflegen. Solche Queries verwenden keine zustandsbehafteten Operatoren wie Streaming-Aggregationen, `dropDuplicates` oder Stream-Stream-Joins. Beispiele hierfür sind Queries, die Stream-Static-Joins, `MERGE INTO` mit Delta-Lake-Tabellen sowie weitere Operationen verwenden, die lediglich nachverfolgen, welche Zeilen von der Quelle bis zur Senke bereits verarbeitet wurden.

## <a id="aqe-aos">2. Adaptive Query Execution und Auto Optimized Shuffle</a>

Databricks unterstützt Adaptive Query Execution (AQE) und Auto Optimized Shuffle (AOS) für zustandslose Streaming-Queries. Diese Funktionen helfen dabei, Streaming-Workloads zu optimieren, die Stream-Static-Joins, `MERGE INTO` mit Delta-Lake-Tabellen und ähnliche Operationen verwenden.

Um AQE für zustandslose Streaming-Queries zu aktivieren, wird die folgende Konfiguration auf `true` gesetzt. Sie ist standardmäßig aktiviert:

```ini
spark.sql.adaptive.streaming.stateless.enabled true
```

Um AOS für zustandslose Streaming-Queries zu aktivieren, muss AQE aktiviert sein und zusätzlich folgende Konfiguration gesetzt werden:

```ini
spark.sql.shuffle.partitions auto
```

## <a id="shuffle-partitionen-aendern">3. Shuffle-Partitionen beim Neustart einer Query ändern</a>

Zustandslose Streaming-Queries unterstützen es, die Anzahl der Shuffle-Partitionen beim Neustart einer Query zu ändern. Dadurch lässt sich der Parallelitätsgrad an unterschiedliche Eingabedatenmengen anpassen.

Diese Funktion ist besonders nützlich für historische Backfill-Szenarien. Beispielsweise kann ein historischer Backfill mit höherer Parallelität verarbeitet und die Parallelität anschließend für Echtzeit-Eingaben reduziert werden.

Um die Anzahl der Shuffle-Partitionen zu ändern, wird folgende Konfiguration auf den gewünschten Wert gesetzt und die Query neu gestartet:

```ini
spark.sql.shuffle.partitions <number>
```

---

## <a id="quellen">4. Quellen</a>
- Optimize stateless streaming queries (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/stateless-streaming
- Optimize stateless streaming queries (Mirror, verifiziert/vollständig abgerufen, Azure): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/stateless-streaming

**Stand:** 2026-08-22.
