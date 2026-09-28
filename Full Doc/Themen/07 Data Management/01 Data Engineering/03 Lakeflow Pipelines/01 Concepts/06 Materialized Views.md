# Materialized Views

Referenz zum Konzept "Materialized View" in Lakeflow-Pipelines, basierend auf `https://docs.databricks.com/aws/en/ldp/concepts/materialized-views`.

## Abschnittsübersicht

1. [Überblick: Cache statt Neuberechnung](#ueberblick)
2. [Kerneigenschaften](#kerneigenschaften)
3. [Funktionsweise und Speicherung](#funktionsweise)
4. [Beispiel](#beispiel)
5. [Inkrementelle Updates](#inkrementelle-updates)
6. [Einschränkungen](#einschraenkungen)
7. [Materialized View als Flow-Typ](#flow-typ)
8. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick: Cache statt Neuberechnung</a>

Materialized Views cachen Query-Ergebnisse und aktualisieren sie in einem festgelegten Intervall — im Gegensatz zu regulären Views, die bei jeder Abfrage neu berechnet werden. Laut Doku gilt: "Abfragen dagegen können deutlich schneller laufen als gegen reguläre Views."

## <a id="kerneigenschaften">2. Kerneigenschaften</a>

Materialized Views sind deklarative Pipeline-Objekte, die:

- Änderungen an vorgelagerten (upstream) Daten nachverfolgen.
- Geänderte Daten bei einem Update inkrementell verarbeiten.
- Ausgabetabellen synchron zu den konfigurierten Refresh-Intervallen halten.

Die Doku betont, dass Materialized Views ideal sind, wenn man "über gecachte Ergebnisse statt über einzelne Zeilen argumentiert (reasoning)", und dass sie "zum Zeitpunkt ihres Updates stets korrekt sind".

## <a id="funktionsweise">3. Funktionsweise und Speicherung</a>

Eine einzelne Pipeline definiert und aktualisiert eine Materialized View. Databricks nutzt Unity Catalog für die Metadatenspeicherung und Cloud-Speicher für die gecachten Daten. Die zugrunde liegenden Daten werden im Katalog `__databricks_internal` abgelegt.

## <a id="beispiel">4. Beispiel</a>

```sql
CREATE OR REPLACE MATERIALIZED VIEW regional_sales
AS SELECT *
FROM partners
  INNER JOIN sales ON
    partners.partner_id = sales.partner_id;
```

## <a id="inkrementelle-updates">5. Inkrementelle Updates</a>

Das System "versucht, nur die Daten zu verarbeiten, die verarbeitet werden müssen", um die Aktualität sicherzustellen. Dabei gilt: "Eine Materialized View zeigt immer das korrekte Ergebnis, auch wenn dafür eine vollständige Neuberechnung nötig ist."

## <a id="einschraenkungen">6. Einschränkungen</a>

- **Nicht für Low-Latency-Anwendungsfälle gedacht** — gemeint sind Sekunden/Minuten, nicht Millisekunden.
- **Nicht jede Berechnung lässt sich inkrementell durchführen.**
- **Keine Unterstützung für `CLONE`-Operationen.**
- Änderungen im Verhalten von UDFs (User-Defined Functions) erfordern in manchen Fällen ein manuelles vollständiges Refresh.

**Ungeklärt:** Welche konkreten Berechnungsarten "nicht inkrementell" verarbeitet werden können (z. B. bestimmte nicht-deterministische Funktionen, bestimmte Aggregationstypen), wurde auf dieser Seite nur allgemein benannt, nicht mit einer vollständigen, zitierbaren Liste belegt.

## <a id="flow-typ">7. Materialized View als Flow-Typ</a>

Laut der Concepts-Übersichtsseite ist eine Materialized View zugleich ein eigener **Flow-Typ**: ein Batch-Flow, der — anders als Append- oder Auto-CDC-Flows, die stets Streaming-Flows sind — nur neue Daten und Änderungen in den Quelltabellen verarbeitet, wann immer das möglich ist. Der Flow wird dabei stets implizit als Teil der Materialized-View-Definition angelegt; anders als bei Streaming Tables lässt er sich nicht separat vom Ziel definieren (siehe `06 Flows/Flows.md`, Abschnitt 2).

Eine vollständige Entscheidungshilfe View vs. Materialized View vs. Streaming Table (inkl. Diagramm) steht in `Views.md` in diesem Ordner.

## <a id="quellen">8. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/concepts/materialized-views
- What are Lakeflow pipelines? — Concepts-Übersicht: https://learn.microsoft.com/en-us/azure/databricks/ldp/concepts/

**Stand:** 2026-08-20.
