# Verarbeitungsgarantien in Lakeflow Pipelines

Dieses Dokument beschreibt Idempotenz und Exactly-once-Verarbeitung in Lakeflow-Pipelines sowie deren Grenzen.

## Abschnittsübersicht

1. [Grundbegriffe: Idempotenz und Verarbeitungsgarantie](#grundbegriffe)
2. [Funktionsweise: Exactly-once bei verwalteten Tabellen](#funktionsweise)
3. [`AUTO CDC` statt handgeschriebenem `MERGE`](#auto-cdc)
4. [Transformationen idempotent halten](#idempotent)
5. [Umgang mit At-least-once-Quellen](#at-least-once)
6. [Grenzen der Exactly-once-Garantie](#grenzen)
7. [Quellen](#quellen)

---

## <a id="grundbegriffe">1. Grundbegriffe: Idempotenz und Verarbeitungsgarantie</a>

**Idempotenz** bedeutet: "a pipeline produces the same result no matter how many times you run it over the same input" — eine Pipeline liefert unabhängig von der Anzahl der Ausführungen über dieselben Eingabedaten dasselbe Ergebnis.

**Verarbeitungsgarantie** beschreibt, wie oft ein Datensatz das Ergebnis beeinflusst:

- **At-least-once:** garantiert, dass jeder Datensatz verarbeitet wird, kann bei Wiederholungen aber zu Duplikaten führen.
- **Exactly-once:** garantiert, dass "every record affects the result as if it were processed precisely one time" — jeder Datensatz beeinflusst das Ergebnis so, als wäre er genau einmal verarbeitet worden.

Laut Doku gilt: "Lakeflow pipelines are idempotent by default for the pieces they manage, and give you exactly-once processing within their own managed tables." — Lakeflow-Pipelines sind für die von ihnen verwalteten Bestandteile standardmäßig idempotent und bieten Exactly-once-Verarbeitung innerhalb ihrer eigenen verwalteten Tabellen.

## <a id="funktionsweise">2. Funktionsweise: Exactly-once bei verwalteten Tabellen</a>

Innerhalb verwalteter Tabellen sorgt das Zusammenspiel aus "Structured Streaming checkpoints combined with Delta Lake's transactional writes" für Exactly-once-Verarbeitung. Jeder Micro-Batch committet Quell-Offsets und Ausgabe gemeinsam — wiederholte Batches gelingen entweder vollständig oder werden vollständig zurückgerollt.

## <a id="auto-cdc">3. `AUTO CDC` statt handgeschriebenem `MERGE`</a>

Die Doku empfiehlt `AUTO CDC INTO`, da es "inherently idempotent with respect to its `keys` and `sequence_by`" ist — von sich aus idempotent bezüglich seiner `keys`- und `sequence_by`-Parameter.

## <a id="idempotent">4. Transformationen idempotent halten</a>

Leitlinien:

- Nicht-deterministische Funktionen in Materialized Views vermeiden.
- Full Refreshes sicher gestalten, indem sichergestellt wird, dass Upstream-Quellen die vollständige Historie erneut produzieren können.

## <a id="at-least-once">5. Umgang mit At-least-once-Quellen</a>

Empfohlen wird die Verwendung von `dropDuplicatesWithinWatermark`, da diese Funktion Watermark-bewusst ist und keinen unbegrenzten State benötigt, um Duplikate zu erkennen.

## <a id="grenzen">6. Grenzen der Exactly-once-Garantie</a>

"Exactly-once processing applies to managed Delta-to-Delta flows." — die Garantie gilt für verwaltete Delta-zu-Delta-Flows. Folgende Bereiche sind als At-least-once zu behandeln:

- `foreach_batch_sink` und benutzerdefinierte externe Writes
- Kafka als Sink
- Benutzerdefinierte Python-Datenquellen

---

## <a id="quellen">7. Quellen</a>

1. Processing guarantees in Lakeflow pipelines (AWS): https://docs.databricks.com/aws/en/ldp/best-practices/processing-guarantees
