# MLOps-Workflow

Der vollständige MLOps-Referenzworkflow auf Databricks über drei Umgebungen (Development, Staging, Production) mit je eigenen Pipeline-Schritten — von der Datenexploration bis zu Retraining-Triggern. Teil der [Testing](../Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Was ist MLOps?](#was-ist)
2. [Allgemeine Empfehlungen](#empfehlungen)
3. [Development-Stufe](#development)
4. [Staging-Stufe](#staging)
5. [Production-Stufe](#production)
6. [Quelle](#quelle)

---

## <a id="was-ist">1. Was ist MLOps?</a>

MLOps ist „eine Menge von Prozessen und automatisierten Schritten zur Verwaltung von Code, Daten und Modellen, um Performance, Stabilität und langfristige Effizienz zu verbessern." Es integriert DevOps, DataOps und ModelOps in ein einheitliches Framework zur Verwaltung von ML-Systemen über ihren gesamten Lebenszyklus.

## <a id="empfehlungen">2. Allgemeine Empfehlungen</a>

### Umgebungen nach Entwicklungsstufe trennen

Drei aufeinanderfolgende Stufen mit eigenen Umgebungen: **Development** (explorativ, weniger kontrollierter Zugriff), **Staging** (Zwischentest-Phase), **Production** (streng kontrolliert, finales Deployment). Jede Umgebung umfasst Compute-Instanzen, Runtimes, Bibliotheken und automatisierte Jobs mit klar definierten Übergängen.

### Zugriffskontrolle und Versionierung

Vier Kernpraktiken: **Git-Integration** (Versionskontrolle mit Git Folders über Workspaces hinweg synchronisieren); **Delta-Lake-Storage** (Roh- und Feature-Daten als Delta-Tabellen mit Zugriffskontrollen); **MLflow-Management** (Modellentwicklung mit Parametern, Metriken, Metadaten nachverfolgen); **Unity-Catalog-Modelle** (Versionierung, Governance und Deployment-Status über Models in Unity Catalog verwalten).

### Code deployen, nicht Modelle

Der empfohlene Ansatz promotet Code über Umgebungen hinweg statt trainierter Modelle — sichert konsistente Code-Review-Prozesse und garantiert, dass Produktionsmodelle produktionsvalidierten Code nutzen.

## <a id="development">3. Development-Stufe</a>

**Schritt 1 — Datenquellen:** Data Scientists erhalten Lese-/Schreibzugriff auf den Development-Catalog in Unity Catalog zur Erstellung temporärer Tabellen und Feature-Tabellen. Idealerweise zusätzlich Nur-Lese-Zugriff auf Produktionsdaten. Ist Produktionszugriff nicht verfügbar, können Daten-Snapshots in den Development-Catalog geschrieben werden.

**Schritt 2 — Explorative Datenanalyse (EDA):** interaktive, iterative Analyse über Notebooks, um zu prüfen, ob verfügbare Daten das Geschäftsproblem adressieren können. AutoML beschleunigt diese Phase durch generierte Baseline-Modelle und reproduzierbare Python-Notebooks mit Trial-Quellcode und zusammenfassenden Statistiken.

**Schritt 3 — Code-Repository-Management:** Projektcode lebt in einem versionskontrollierten Repository. Data Scientists erstellen und aktualisieren Pipelines in einem Development-Branch.

**Schritt 4 — Modell trainieren (Development):** Die Trainings-Pipeline führt zwei Kernaufgaben aus:

- **Training und Tuning:** protokolliert Modellparameter, Metriken und Artefakte in MLflow Tracking. Modell-Artefakte erfassen Verbindungen zwischen Modell, Eingabedaten und generierendem Code.
- **Evaluation:** Modelle werden auf zurückgehaltenen Daten getestet, Ergebnisse werden in MLflow protokolliert — bestimmt, ob neu entwickelte Modelle aktuelle Produktionsversionen übertreffen.

**Schritt 5 — Modell validieren und deployen (Development):** zwei unterstützende Pipelines:

- **Model Validation:** akzeptiert eine Model-URI aus dem Training, lädt das Modell aus Unity Catalog und führt Validierungsprüfungen aus (Format, Metadaten, Compliance, Performance auf Daten-Slices). Bestehende Modelle erhalten den Alias „Challenger"; fehlschlagende Modelle stoppen die Weiterverarbeitung.
- **Model Deployment:** promotet entweder direkt „Challenger" zu „Champion" per Alias-Update, oder ermöglicht den Vergleich zwischen bestehendem und neuem Modell.

**Schritt 6 — Code committen:** nach Entwicklung von Trainings-, Validierungs-, Deployment- und zugehörigem Pipeline-Code werden Development-Branch-Änderungen in die Versionskontrolle committet.

## <a id="staging">4. Staging-Stufe</a>

**Schritt 1 — Datenmanagement:** die Staging-Umgebung pflegt einen eigenen Unity Catalog zum Testen von ML-Pipelines und Registrieren von Modellen — Assets darin sind typischerweise temporär.

**Schritt 2 — Code mergen und Unit Testing:** Deployment beginnt, wenn Pull Requests auf den Main-Branch des Projekts zielen. Der CI-Prozess baut automatisch den Quellcode und führt Unit Tests aus — Testfehlschläge führen zur Ablehnung des Pull Requests.

**Schritt 3 — Integrationstests (CI):** CI-Prozesse führen anschließend Integrationstests aus, die alle Pipelines (Feature Engineering, Modelltraining, Inferenz, Monitoring) durchlaufen, um korrektes Zusammenspiel zu verifizieren. Die Staging-Umgebung sollte Production so genau wie möglich widerspiegeln. Für Echtzeit-Inferenz-Anwendungen muss Serving-Infrastruktur in Staging erstellt und getestet werden.

**Schritt 4 — In Staging-Branch mergen:** nach Bestehen aller Tests wird Code in den Main-Branch des Projekts gemerged.

**Schritt 5 — Release-Branch erstellen:** nach erfolgreichem CI-Testing und Dev-zu-Main-Merge erstellen ML Engineers einen Release-Branch, der das CI/CD-System zur Aktualisierung der Produktions-Jobs auslöst.

## <a id="production">5. Production-Stufe</a>

**Schritt 1 — Modell trainieren:** Produktions-Trainings-Pipelines laufen über Code-Änderungen oder automatisierte Retraining-Jobs unter Nutzung von Produktions-Catalog-Tabellen. Produktions-Training berücksichtigt typischerweise nur die leistungsstärksten Algorithmen und Hyperparameter. Nach Abschluss werden Modell-Artefakte als registrierte Modellversionen im Production-Catalog innerhalb von Unity Catalog gespeichert.

**Schritt 2 — Modell validieren:** lädt Modelle aus Unity Catalog über Model-URIs und führt Validierungsprüfungen aus. Erfolgreich validierte Modelle erhalten den Alias „Challenger" in Unity Catalog; nicht erfolgreiche Modelle stoppen die Weiterverarbeitung und lösen Benachrichtigungen aus.

**Schritt 3 — Modell deployen:** Angenommen, neu validierte Modelle haben den Alias „Challenger" und bestehende Produktionsmodelle den Alias „Champion" — der erste Deployment-Schritt vergleicht deren Performance.

- **Modelle vergleichen:** Offline-Vergleiche evaluieren beide Modelle gegen zurückgehaltene Datensätze, Ergebnisse werden über MLflow verfolgt. Echtzeit-Serving-Szenarien können längerlaufende Online-Vergleiche wie A/B-Tests oder graduelle Rollouts nutzen. Überlegene „Challenger"-Performance löst den Alias-Wechsel aus.
- **Modell deployen:** Batch- oder Streaming-Inferenz-Pipelines nutzen Modelle mit „Champion"-Alias. Echtzeit-Anwendungsfälle benötigen REST-API-Endpoint-Infrastruktur über Model Serving.

**Schritt 4 — Model Serving:** Model-Serving-Endpoints spezifizieren Modellnamen und -versionen aus Unity Catalog. Mit Features aus Unity-Catalog-Tabellen trainierte Modelle speichern Feature-Abhängigkeiten — Model Serving nutzt automatisch Abhängigkeitsgraphen, um Features zur Inferenzzeit aus Online-Stores nachzuschlagen. Einzelne Endpoints können mehrere Modelle mit festgelegten Traffic-Splits hosten (Online-„Champion"-vs.-„Challenger"-Vergleiche).

**Schritt 5 — Inferenz: Batch oder Streaming:** Inferenz-Pipelines lesen aktuelle Produktions-Catalog-Daten, berechnen On-Demand-Features, laden „Champion"-Modelle, scoren Daten und geben Vorhersagen zurück. Batch- oder Streaming-Ansätze bieten optimale Kosteneffizienz bei höherem Durchsatz/höherer Latenz.

**Schritt 6 — Data Profiling:** überwacht statistische Eigenschaften wie Data Drift und Modell-Performance für Eingaben und Vorhersagen. Metriken lösen Alerts aus oder befüllen Dashboards. Databricks SQL erstellt Monitoring-Dashboards, die Modell-Performance verfolgen, mit Benachrichtigungen bei Schwellenwert-Überschreitung.

**Schritt 7 — Retraining:** diese Architektur unterstützt automatisches Retraining über die Produktions-Trainings-Pipeline.

- **Geplantes Retraining:** wenn regelmäßig neue Daten eintreffen, führen geplante Jobs Trainingscode auf den neuesten Daten aus.
- **Getriggertes Retraining:** wenn Monitoring-Pipelines Performance-Probleme identifizieren und Alerts senden, können sie Retraining auslösen. Signifikante Änderungen der Datenverteilung oder Modell-Performance-Verschlechterung können automatisches Retraining und Redeployment aktivieren.

## <a id="quelle">6. Quelle</a>

- https://docs.databricks.com/aws/en/machine-learning/mlops/mlops-workflow

**Stand:** 2026-08-21.
