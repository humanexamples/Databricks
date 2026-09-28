# SQL vs. Python für Lakeflow Declarative Pipelines

## Abschnittsübersicht

1. [Grundregel](#grundregel)
2. [Wann SQL](#sql)
3. [Wann Python](#python)
4. [Gemischte Pipelines](#gemischt)
5. [Feature-Lücken zwischen den Sprachen](#luecken)
6. [Quellen](#quellen)

---

## <a id="grundregel">1. Grundregel</a>

Die Doku formuliert die Entscheidungsregel denkbar knapp: *"If you can express your logic in SQL, use SQL. If you need programmatic control or a Python-only feature, use Python."* — lässt sich die Logik in SQL ausdrücken, soll SQL verwendet werden; wird programmatische Kontrolle oder ein Python-exklusives Feature benötigt, Python.

---

## <a id="sql">2. Wann SQL</a>

SQL eignet sich laut Doku für Szenarien, die "lesbare, deklarative Definitionen" (*"readable, declarative definitions"*) und "lineare Transformationsketten" (*"linear transformation chains"*) erfordern — also für Standard-Tabellentypen und geradlinige Datenflüsse ohne prozedurale Logik.

---

## <a id="python">3. Wann Python</a>

Python wird empfohlen, wenn eine der folgenden Anforderungen besteht:

- **Programmatische Kontrolle** über Schleifen und Bedingungen (`for`, `if`),
- externe Bibliotheken wie `faker` oder `boto3`,
- benutzerdefinierte Funktionen (UDFs),
- Python-exklusive Features wie `create_auto_cdc_from_snapshot_flow()` und Sink-Operationen.

---

## <a id="gemischt">4. Gemischte Pipelines</a>

Eine einzelne Pipeline kann SQL- und Python-Definitionen kombinieren, aber jede Sprache muss in einer eigenen Quelldatei stehen — wörtlich: *"a single pipeline can combine SQL and Python definitions, but each language must be in a separate source file."*

---

## <a id="luecken">5. Feature-Lücken zwischen den Sprachen</a>

Manche Fähigkeiten existieren laut Doku nur in einer der beiden Sprachen:

| Nur in... | Feature |
|---|---|
| SQL | Iceberg-kompatible Materialized Views |
| Python | `create_auto_cdc_from_snapshot_flow()` (Auto CDC from Snapshots) |
| Python | Sinks allgemein |
| Python | `foreach_batch_sink()` |

Beide Sprachen unterstützen dagegen Streaming-Tabellen, Materialized Views, temporäre Sichten (Temporary Views), private Tabellen sowie Expectations — allerdings jeweils mit unterschiedlicher Syntax.

---

## <a id="quellen">6. Quellen</a>

- SQL vs Python (Entscheidungsregel, Feature-Vergleichstabelle SQL-only/Python-only): https://docs.databricks.com/aws/en/ldp/developer/sql-vs-python

**Stand:** 2026-08-19.
