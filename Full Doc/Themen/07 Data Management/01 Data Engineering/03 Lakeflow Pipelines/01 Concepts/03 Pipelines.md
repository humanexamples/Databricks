# Pipelines

Referenz zum Konzept "Pipeline" in Lakeflow-Pipelines, basierend auf `https://docs.databricks.com/aws/en/ldp/concepts/pipelines`.

## Abschnittsübersicht

1. [Was ist eine Pipeline?](#definition)
2. [Quellcode: SQL oder Python](#quellcode)
3. [Der Pipeline-Graph](#graph)
4. [Pipeline-Updates: Triggered vs. Continuous](#updates)
5. [Vier Pipeline-Typen](#typen)
6. [Der Lakeflow-Pipelines-Editor](#editor)
7. [Delta-Integration](#delta-integration)
8. [Quellen](#quellen)

---

## <a id="definition">1. Was ist eine Pipeline?</a>

Eine Pipeline ist "die Haupteinheit der Entwicklung und Ausführung von Apache Spark™ Declarative Pipelines (SDP) in Lakeflow". Sie kombiniert Quellcode-Dateien mit Konfigurationseinstellungen, um Datasets zu deklarieren und Ausführungsparameter festzulegen.

Eine Pipeline ist der Container für alle Flows, Streaming Tables, Materialized Views und Sinks, die innerhalb ihres Quellcodes definiert werden. Das Gesamtbild aller Kernkonzepte und wie sie zusammenspielen zeigt das Diagramm in `Uebersicht.md` in diesem Ordner; Details zu den einzelnen Bausteinen stehen in `06 Flows/Flows.md`, `Streaming Tables.md`, `Materialized Views.md`, `Views.md` und `09 Sinks/Sinks.md`.

## <a id="quellcode">2. Quellcode: SQL oder Python</a>

Pipelines unterstützen sowohl Python als auch SQL, wobei jede einzelne Datei jeweils nur eine dieser Sprachen verwenden kann. Das System analysiert Abhängigkeiten zwischen den Dateien automatisch — unabhängig davon, in welcher Reihenfolge die Dateien organisiert sind.

## <a id="graph">3. Der Pipeline-Graph</a>

Das System inferiert automatisch die Abhängigkeiten zwischen Datasets und ordnet sie in einem gerichteten azyklischen Graphen (DAG) an, um die Ausführungsreihenfolge zu bestimmen.

## <a id="updates">4. Pipeline-Updates: Triggered vs. Continuous</a>

Ein Pipeline-Update berechnet den aktuellen Zustand der Datasets, indem es das Compute initialisiert, den Abhängigkeitsgraphen aufbaut und die Datasets in der ermittelten Reihenfolge berechnet. Dabei gibt es zwei Ausführungsmodi:

- **Triggered:** Läuft einmal bis zur vollständigen Fertigstellung.
- **Continuous:** Läuft fortlaufend und verarbeitet neu eintreffende Daten.

Die ausführliche Gegenüberstellung dieser beiden Modi ist Gegenstand der Datei "Pipeline-Modi (Triggered vs Continuous).md" in diesem Ordner.

## <a id="typen">5. Vier Pipeline-Typen</a>

Die Doku unterscheidet vier Pipeline-Typen:

- **ETL** — eine Lakeflow-Pipeline (das in diesem Ordner behandelte Standard-Szenario).
- **Ingestion** — eine verwaltete Ingestion-Pipeline, erstellt über Lakeflow Connect.
- **MV/ST** — eine Standalone-Pipeline für eine einzelne Materialized View bzw. Streaming Table (siehe `Standalone Pipelines.md`).
- **Database Table Sync** — eine Pipeline, die eine Tabelle mit einer Lakebase-Datenbank synchronisiert.

Diese Kurzdefinitionen sind durch die `pipeline_type`-Enum-Werte des Event Logs bestätigt (`WORKSPACE`, `MANAGED_INGESTION`, `DBSQL`, `DATABASE_TABLE_SYNC` — siehe `13 Observability/Event-Log-Schema.md`, Origin-Objekt). Detailliertere technische Abgrenzungen der einzelnen Typen liefert die Concepts-Seite selbst nicht — dafür verweist sie auf die jeweiligen produktspezifischen Unterseiten (z. B. Lakeflow Connect für "Ingestion").

## <a id="editor">6. Der Lakeflow-Pipelines-Editor</a>

Der Lakeflow-Pipelines-Editor bietet eine integrierte Entwicklungsumgebung (IDE) mit folgenden Merkmalen:

- Bearbeitung mehrerer Dateien gleichzeitig (Multi-File-Editing)
- Visuelle Abhängigkeitsgraphen
- Datenvorschauen (Data Previews)
- Unterstützung für Git-Versionskontrolle

## <a id="delta-integration">7. Delta-Integration</a>

Alle von einer Pipeline erzeugten und verwalteten Tabellen sind Delta-Tabellen — mit denselben Garantien wie Delta Lake generell: ACID-Transaktionen, Time Travel und Schema Enforcement. Pipelines ergänzen zusätzliche Tabelleneigenschaften und führen automatische Wartung über Predictive Optimization aus, einschließlich `OPTIMIZE`- und `VACUUM`-Operationen.

Details zur Compute- und Optimierungskonfiguration stehen in `11 Konfiguration und Compute/Compute konfigurieren.md`; Details zu Tabelleneigenschaften in `12 Unity Catalog und Schema-Verwaltung/Properties.md`.

## <a id="quellen">8. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/concepts/pipelines
- What are Lakeflow pipelines? — Concepts-Übersicht (Kernkonzepte-Diagramm, Delta-Integration): https://learn.microsoft.com/en-us/azure/databricks/ldp/concepts/

**Stand:** 2026-08-20.
