# Tutorials-Übersicht

Referenz zur Übersichtsseite der Lakeflow-Pipelines-Tutorials, basierend auf `https://docs.databricks.com/aws/en/ldp/tutorials`.

## Abschnittsübersicht

1. [Einleitung](#einleitung)
2. [Erste-Schritte-Tutorial](#erste-schritte)
3. [Die sieben Haupt-Tutorials](#haupt-tutorials)
4. [Quellen](#quellen)

---

## <a id="einleitung">1. Einleitung</a>

Die Seite fasst zusammen: "Diese Tutorials vermitteln praktische Erfahrung im Erstellen von Lakeflow-Pipelines — von der ersten Pipeline über ETL mit CDC bis hin zu geografischem Dateneingang und quellcodeverwalteten Bundles."

## <a id="erste-schritte">2. Erste-Schritte-Tutorial</a>

Ein einführendes Tutorial wird gesondert hervorgehoben:

- **"Tutorial: Eine ETL-Pipeline mit Lakeflow-Pipelines bauen"** — zeigt, "wie eine einfache ETL-Pipeline (Extract, Transform, Load) für Datenorchestrierung und Auto Loader erstellt und bereitgestellt wird." Dieses Tutorial entspricht der Datei "Tutorial - Erste Pipeline.md" in diesem Ordner.

## <a id="haupt-tutorials">3. Die sieben Haupt-Tutorials</a>

Die Übersichtsseite listet insgesamt sieben Tutorials:

1. **Erste Pipeline erstellen** — "führt durch die Erstellung der ersten Pipeline, indem der beim Anlegen einer neuen Pipeline mitgelieferte Beispielcode erweitert wird." *(→ "Tutorial - Erste Pipeline.md")*
2. **CDC-Pipeline** — "führt durch die Schritte zum Erstellen und Bereitstellen einer ETL-Pipeline mit Change Data Capture (CDC)." *(→ "Tutorial - Pipelines mit mehreren Quellen.md")*
3. **SQL-ETL** — konzentriert sich auf "den Aufbau einer inkrementellen ETL-Pipeline in Databricks SQL mit Streaming Tables, AUTO CDC und Materialized Views."
4. **Geodaten-Pipeline** — beschreibt "den Aufbau einer geografischen Pipeline, die GPS-Daten aufnimmt, Koordinaten in native räumliche Typen umwandelt und sie gegen Lager-Geofences abgleicht." *(→ "Tutorial - Geodaten-Pipelines.md")*
5. **Datei-Verarbeitungs-Pipeline** — behandelt "das Einlesen unstrukturierter Dateien als `FILE`-Referenzen und das Parsen von Dokumentinhalten mit KI-Funktionen." *(→ "Tutorial - Datei-Pipelines.md")*
6. **Quellcode-verwaltete Pipeline** — zeigt, "wie eine quellcodeverwaltete Pipeline mithilfe von Declarative Automation Bundles und Git-Ordnern erstellt wird."
7. **Bundle-Konvertierung** — zeigt, "wie eine bestehende Pipeline in ein Declarative-Automation-Bundles-Projekt umgewandelt wird."

**Hinweis:** In diesem Themenblock werden die Tutorials 1 ("Erste Pipeline"), 2 ("CDC-Pipeline", hier unter dem Titel "Pipelines mit mehreren Quellen"), 4 ("Geodaten-Pipeline") und 5 ("Datei-Verarbeitungs-Pipeline") als eigene Dateien vollständig mit Code-Beispielen ausgearbeitet — entsprechend der Zielstruktur dieses Ordners. Die Tutorials 3, 6 und 7 (SQL-ETL, Bundles, Bundle-Konvertierung) liegen außerhalb des zugewiesenen Themenblocks "Concepts"/"Tutorials" dieses Dokuments und werden hier nicht vertieft.

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/tutorials
