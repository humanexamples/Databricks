# Was ist Spark Declarative Pipelines?

Dieses Dokument fasst drei eng verwandte Übersichtsseiten der offiziellen Databricks-Dokumentation zusammen: die Lakeflow-Pipelines-Startseite (`/ldp/`), die Concepts-Übersichtsseite (`/ldp/concepts/`) und die Seite zu Apache Spark™ Declarative Pipelines als technischem Fundament (`/ldp/concepts/spark-declarative-pipelines`). Jede Aussage wurde per `WebFetch` gegen die Online-Dokumentation verifiziert.

## Abschnittsübersicht

1. [Lakeflow-Pipelines-Startseite](#startseite)
2. [Concepts-Übersicht: Die vier Grundbausteine](#concepts-uebersicht)
3. [Apache Spark Declarative Pipelines als Fundament](#sdp-fundament)
4. [Was Lakeflow zu SDP hinzufügt](#lakeflow-erweiterungen)
5. [Quellen](#quellen)

---

## <a id="startseite">1. Lakeflow-Pipelines-Startseite</a>

Die Einstiegsseite (`https://docs.databricks.com/aws/en/ldp/`) definiert Lakeflow-Pipelines (früher Delta Live Tables / DLT) als "ein deklaratives Framework zum Erstellen von Batch- und Streaming-Datenpipelines in SQL und Python". Lakeflow-Pipelines erweitern Apache Spark Declarative Pipelines und laufen auf der Databricks Runtime.

### Typische Anwendungsfälle

Laut Doku werden Lakeflow-Pipelines häufig eingesetzt für:

- Das Einlesen von Daten aus Cloud-Speicher (S3, ADLS Gen2, Google Cloud Storage) und aus Message-Bussen (Kafka, Kinesis, Pub/Sub, EventHub, Pulsar).
- Inkrementelle Batch- und Streaming-Transformationen.

### Einstiegspunkte laut Doku

Die Startseite gliedert weiterführende Themen in zwei Kategorien:

- **Erste Schritte:** Eine Seite zur Verwendung von Lakeflow-Pipelines über den gesamten Lebenszyklus hinweg sowie eine Seite zu Pipeline-Konzepten (Flows, Streaming Tables, Materialized Views).
- **Vertiefende Themen:** Tutorials für praktische Erfahrung, Entwicklung und Testen von Pipelines, Planung und Konfiguration, Monitoring und Troubleshooting, Python- und SQL-Entwicklungsanleitungen, Standalone-Pipelines in Databricks SQL **oder Python** sowie Best Practices für zuverlässige und effiziente Pipelines.

Zusätzlich verweist die Seite auf die Dokumentation zu Pipeline-Einschränkungen sowie auf Referenzmaterial für Entwickler.

---

## <a id="concepts-uebersicht">2. Concepts-Übersicht: Die vier Grundbausteine</a>

Die Concepts-Übersichtsseite (`https://docs.databricks.com/aws/en/ldp/concepts/`) beschreibt Lakeflow-Pipelines als deklaratives Framework, das Apache Spark Declarative Pipelines erweitert und dabei Orchestrierung sowie inkrementelle Aktualisierungen automatisch übernimmt. Die vollständige, eigenständige Übersetzung dieser Seite — mit allen Grundbausteinen (Datasets, Flows, Sinks, Pipelines, Data Ingestion, Data Quality, Delta-Integration) und dem Kernkonzepte-Diagramm — steht in `Uebersicht.md` in diesem Ordner. Für die vorliegende Datei ist von dieser Seite nur ein Punkt relevant: die drei zentralen Vorteile, die Lakeflow-Pipelines gegenüber manuell orchestriertem Spark bieten und die im nächsten Abschnitt in den direkten Vergleich mit reinem SDP einfließen.

### Die drei zentralen Vorteile

1. **Automatische Orchestrierung:** Prozesse laufen in der korrekten Reihenfolge, mit maximaler Parallelität und progressiver Retry-Logik.
2. **Deklarative Verarbeitung:** Reduziert umfangreichen Code auf knappe Definitionen, inklusive eingebauter CDC-Verarbeitung (Change Data Capture).
3. **Inkrementelle Verarbeitung:** Eine Engine hält Materialized Views aktuell, indem sie nur neue oder geänderte Daten neu verarbeitet.

---

## <a id="sdp-fundament">3. Apache Spark Declarative Pipelines als Fundament</a>

Die dritte Quellseite (`https://docs.databricks.com/aws/en/ldp/concepts/spark-declarative-pipelines`) stellt klar: "Lakeflow-Pipelines basieren auf Apache Spark™ Declarative Pipelines (SDP)." Dieses Fundament hält den Transformationscode über verschiedene SDP-Laufzeiten hinweg portabel, statt ihn an ein proprietäres System zu binden.

### Was SDP leistet

Apache Spark Declarative Pipelines wird als "ein deklaratives Framework zur Entwicklung und Ausführung von Batch- und Streaming-Datenpipelines in SQL und Python" beschrieben, das Orchestrierung und Abhängigkeitsmanagement automatisiert.

Typische Anwendungsfälle laut Doku:

- Batch-Dateneingang aus Cloud-Speicher-Quellen.
- Inkrementeller Dateneingang aus Message-Bussen wie Kafka und Kinesis.
- Sowohl Batch- als auch Streaming-Transformationen.

### Gemeinsame Fähigkeiten von SDP und Lakeflow

Beide unterstützen deklarative SQL/Python-Entwicklung, Streaming Tables, Materialized Views und automatische Abhängigkeitsauflösung.

---

## <a id="lakeflow-erweiterungen">4. Was Lakeflow zu SDP hinzufügt</a>

Die Doku listet konkrete, produktionsorientierte Erweiterungen, die Lakeflow-Pipelines gegenüber dem reinen SDP-Fundament hinzufügen:

- **AUTO-CDC-Funktionalität** (mit Unterstützung für SCD Type 1 und Type 2).
- **Datenqualitäts-Expectations.**
- **Abfragbares Event-Logging.**
- **Update-Flows und Continuous-Processing-Modi.**

Diese Erweiterungen sind der Grund, warum Databricks empfiehlt, Lakeflow-Pipelines (statt reines SDP) für produktive Workloads auf der Databricks-Plattform zu verwenden — der zugrunde liegende, portable SDP-Kern bleibt dabei erhalten.

**Ungeklärt:** Die genaue technische Abgrenzung, ab welcher Apache-Spark-Version (laut Doku "beginning in Apache Spark 4.1", vgl. die Seite "Wo ist DLT geblieben") SDP als eigenständiges Open-Source-Framework nutzbar ist und wie es sich im Detail zu Lakeflow-Pipelines auf Databricks verhält, wurde auf diesen drei Übersichtsseiten nicht vollständig ausgeführt — hierzu verweist die Doku auf eine gesonderte Seite zum Vergleich von prozeduralem und deklarativem Ansatz sowie auf eine detaillierte Property-Referenz.

---

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/
- https://docs.databricks.com/aws/en/ldp/concepts/
- https://docs.databricks.com/aws/en/ldp/concepts/spark-declarative-pipelines
