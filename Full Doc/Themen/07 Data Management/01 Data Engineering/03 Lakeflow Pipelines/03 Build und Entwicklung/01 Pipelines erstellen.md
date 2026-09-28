# Pipelines erstellen — Referenz

Dieses Dokument fasst die Databricks-Dokumentationsseite "Build pipelines" zusammen — die Einstiegs-/Übersichtsseite des Doku-Bereichs zum Erstellen und Betreiben von Lakeflow Declarative Pipelines (LDP, früher DLT). Jede faktische Aussage wurde per `WebFetch` gegen die offizielle Databricks-Online-Dokumentation (AWS-Seite `docs.databricks.com/aws/en/ldp/build-pipelines`) verifiziert. Die Seite selbst ist inhaltlich bewusst schlank gehalten: Sie besteht im Kern aus zwei kurzen Absätzen, einer Themen-Tabelle mit Verweisen auf die vertiefenden Unterseiten sowie einer Liste weiterführender Ressourcen — sie ist also eine **Landing-/Hub-Seite**, keine inhaltlich eigenständige Detailseite. Entsprechend fällt dieses Dokument kürzer aus als andere Referenzdateien dieser Reihe; es bildet die Seite vollständig und wörtlich ab, extrapoliert aber nicht über deren knappen Inhalt hinaus.

## Abschnittsübersicht

1. [Einordnung und Zweck der Seite](#einordnung)
2. [Themenübersicht: Build und Betrieb von Pipelines](#themenueberblick)
3. [Weiterführende Ressourcen](#weiterfuehrende-ressourcen)
4. [Programmatische Pipeline-Erstellung (Kursbeispiel, nicht dokuverifiziert)](#programmatisch-kursbeispiel)
5. [Quellen](#quellen)

---

## <a id="einordnung">1. Einordnung und Zweck der Seite</a>

Die Seite "Build pipelines" führt Lakeflow-Pipelines, indem Daten geladen und transformiert, Datenqualitätsprüfungen angewendet und Ergebnisse in Zieltabellen geschrieben werden. Die Seite deckt laut Doku die Aufgaben ab, die beim Erstellen und Ausführen von Pipelines anfallen.

Für die deklarativen Konzepte hinter Pipelines (Datasets, Flows und den Pipeline-Graphen) verweist die Seite auf den Artikel "What are Lakeflow pipelines?". Für eine schrittweise Anleitung verweist sie auf das Tutorial "Build an ETL pipeline using change data capture".

---

## <a id="themenueberblick">2. Themenübersicht: Build und Betrieb von Pipelines</a>

Die Seite listet folgende Themen tabellarisch auf, jeweils mit kurzer Beschreibung und Link auf die jeweilige Unterseite:

| Thema | Beschreibung laut Doku | Doku-Pfad |
|---|---|---|
| Develop in the Lakeflow Pipelines Editor | Pipelines im Editor erstellen, ausführen und debuggen — mit Pipeline-Graph, Datenvorschauen und selektiver Ausführung. | `/ldp/multi-file-editor` |
| Use Genie Code for pipeline development | Pipeline-Code aus einem einzigen Prompt heraus generieren, bearbeiten und debuggen — mit dem Genie-Code-Agent-Modus im Editor. | `/ldp/de-agent` |
| Manage identities and privileges | Steuert die Identität, unter der eine Pipeline läuft, sowie wer Pipelines und ihre Ausgabe erstellen, ausführen, aktualisieren und einsehen darf. | `/ldp/privileges` |
| Load data | Daten aus Cloud-Objektspeicher und Streaming-Message-Bussen in die Pipeline laden. | `/ldp/load` |
| Transform data | Transformationen, Joins und Aggregationen anwenden, um abgeleitete Datasets zu erstellen. | `/ldp/transform` |
| Full refresh for streaming tables | Alle Quelldaten neu verarbeiten, um eine Streaming Table komplett neu aufzubauen. | `/ldp/full-refresh-st` |
| Data quality | Datensätze mit Expectations validieren und steuern, was bei einem fehlgeschlagenen Datensatz passiert. | `/ldp/expectations` |
| Write datasets | Pipeline-Ergebnisse in Sinks wie Apache Kafka und Azure Event Hubs schreiben; Flows verwenden, um in Streaming-Ziele zu schreiben. | `/ldp/ldp-sinks` |

**Einordnung im Gesamtprojekt:** Der erste Eintrag dieser Tabelle ("Develop in the Lakeflow Pipelines Editor") entspricht inhaltlich der Doku-Seite `/ldp/multi-file-editor` und ist in diesem Themenblock als eigenständiges Dokument `Multi-File-Editor.md` ausgearbeitet. Die übrigen Themen der Tabelle sind laut Aufgabenstellung nicht Teil der drei Dateien, für die dieses Dokument zuständig ist; ob sie an anderer Stelle dieses Gesamtprojekts (Themenblock "03 Build und Entwicklung", 10 Dateien insgesamt) separat behandelt werden, war im Rahmen dieser Recherche nicht zu prüfen.

---

## <a id="weiterfuehrende-ressourcen">3. Weiterführende Ressourcen</a>

Am Ende der Seite listet Databricks unter "Additional resources" folgende weiterführende Artikel, ohne eigene Beschreibungstexte:

- Optimize stateful processing with watermarks (`/ldp/stateful-processing`)
- Incremental refresh for materialized views (`/ldp/incremental-refresh`)
- Access materialized views and streaming tables using external systems (`/ldp/external-access`)
- Develop and debug pipelines with a notebook (legacy) (`/ldp/notebook-devex`)
- Develop pipeline code in your local development environment (`/ldp/develop-locally`)
- Use parameters with pipelines (`/ldp/parameters`)
- Convert a pipeline into a bundle project (`/ldp/convert-to-dab`)
- Prepare your data for GDPR compliance (`/ldp/gdpr`)

**Einordnung im Gesamtprojekt:** Der Eintrag "Develop and debug pipelines with a notebook (legacy)" (`/ldp/notebook-devex`) entspricht der Doku-Seite, die in diesem Themenblock als eigenständiges Dokument `Notebook-Entwicklungserfahrung.md` ausgearbeitet ist.

**Zuletzt aktualisiert laut Doku-Seite:** Jul 10, 2026 (Angabe am Seitenende der Original-Doku).

---

## <a id="programmatisch-kursbeispiel">4. Programmatische Pipeline-Erstellung (Kursbeispiel, nicht dokuverifiziert)</a>

Aus einer privaten Kursnotiz übernommen. Der folgende Code nutzt `DeclarativePipelineCreator` — eine kurseigene SDK-Hilfsklasse der Databricks-Academy-Trainingsumgebung, **keine öffentliche Databricks-API**. Er dient hier nur als Beleg dafür, dass sich eine Pipeline-Erstellung und der Start eines Updates auch rein programmatisch anstoßen lassen (z. B. aus einem CI/CD-Skript heraus), nicht als Referenz auf ein reales SDK-Interface:

```python
pipeline = DeclarativePipelineCreator(
                            pipeline_name=f"sdk_health_etl_{DA.catalog_dev}",
                            catalog_name = DA.catalog_name,
                            schema_name = 'default',
                            root_path_folder_name='src',
                            source_folder_names=[
                                'src/sdp/**',
                                'tests/integration_test/**'],
                            configuration = {
                                'target': 'development',
                                'raw_data_path':f'/Volumes/{DA.catalog_name}/default/health'
                            })

pipeline.create_pipeline()
pipeline.start_pipeline()
```

Für die produktionsreife, dokumentierte Variante programmatischer Pipeline-Erstellung (Databricks CLI, REST API, Asset Bundles) siehe die Doku-Verweise "Convert a pipeline into a bundle project" in Abschnitt 3 sowie `Konvertierung zu Databricks Asset Bundles.md` in diesem Ordner.

---

## <a id="quellen">5. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/build-pipelines (abgerufen 2026-08-19)
