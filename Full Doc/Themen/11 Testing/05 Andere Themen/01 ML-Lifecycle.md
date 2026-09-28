# ML-Lifecycle

Der End-to-End-ML-Weg auf Databricks über drei Stufen (Development, Staging, Production) und acht Phasen. Teil der [Testing](../Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Die acht Phasen](#phasen)
3. [Unterstützende Tools und Konzepte](#tools)
4. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

Der Weg umfasst drei Stufen — Development, Staging, Production — und acht übergeordnete Phasen, die Projekte vom ersten Konzept bis zum operativen Monitoring führen.

## <a id="phasen">2. Die acht Phasen</a>

### 2.1 Anwendungsfall abgrenzen und Erfolg definieren

Vor Entwicklungsbeginn müssen Teams sich über Ziele einig werden. Wichtige Überlegungen: das Vorhersageziel identifizieren und welche ML-Problemklasse das impliziert (Klassifikation, Regression, Forecasting, Empfehlung, Ranking, Anomalieerkennung o. Ä.); verfügbare Eingabedaten bewerten; Erfolgsmetriken definieren; Produktionsanforderungen zu Latenz und Durchsatz festlegen; Freigabeprozesse und Erklärbarkeitsanforderungen der Stakeholder klären.

### 2.2 Daten explorieren und verstehen

**Exploratory Data Analysis (EDA)** ist entscheidend für das Verständnis von Datenstruktur und -qualität. Der Prozess deckt „Verteilungen, Korrelationen, fehlende Werte und Ausreißer auf, die nachgelagerte Modellierungsentscheidungen prägen." EDA untersucht prädiktive Eingabevariablen, identifiziert Datenqualitätsprobleme und validiert die Ausreichendheit des Datensatzes. Databricks unterstützt diese Phase durch Notebooks, Dashboards, Genie Chat für natürlichsprachliche Abfragen und Genie Code für automatisierte Analyse.

### 2.3 Daten und Features vorbereiten

Rohdaten werden über Data-Engineering- und Feature-Engineering-Workflows zu ML-fertigen Features. Die Plattform vereinheitlicht diese Funktionen innerhalb von Unity Catalog zur Governance. Teams können den Feature Store nutzen, um wiederverwendbare, verwaltete Features zu definieren, die sowohl für Training als auch Produktion gelten — mit Unterstützung für Batch- und Echtzeit-Ingestion-Muster.

### 2.4 Modelle trainieren und Experimente nachverfolgen

Diese Phase umfasst die Wahl geeigneter Compute-Ressourcen und die systematische Protokollierung von Experimenten. Databricks bietet standardmäßig Serverless Compute mit optionaler GPU-Beschleunigung über die AI Runtime. **MLflow Tracking** erfasst Experiment-Metadaten — „Parameter, Metriken und Artefakte" — sowohl automatisch als auch manuell. Model Logging erfasst vollständige Provenienz-Informationen, die Modelle mit ihren Trainingsdatensätzen, Code und Umgebungen verknüpfen.

### 2.5 Evaluieren

Die Qualitätsbewertung definiert Erfolg anhand etablierter Metriken. Über Standard-ML-Metriken wie Accuracy und AUC hinaus kann die Evaluation „Bias und Fairness über Bevölkerungssegmente hinweg" umfassen, gemessen durch den Vergleich von Basismetriken über Segmente hinweg. Alle Metriken sollten in MLflow-Runs protokolliert werden, für Reproduzierbarkeit und künftige Referenz.

### 2.6 Modelle registrieren, staged testen

Modelle wandern in die MLflow Model Registry innerhalb von Unity Catalog zur Governance und zum Lifecycle-Management. Der Prozess umfasst das Kennzeichnen von Modellversionen mit Aliassen („Staging", „Production") sowie Integrationstests, A/B-Tests und Shadow-Deployments vor der Produktions-Promotion.

### 2.7 In Produktion deployen

Zwei primäre Serving-Muster unterstützen unterschiedliche Anwendungsfälle. **Real-Time Serving** deployt Modelle als latenzarme REST-Endpoints für sofortige Entscheidungen, während **Batch Inference** größere Datensätze periodisch verarbeitet. Beide Muster nutzen dasselbe trainierte Modell-Artefakt — „Train once"-Deployment-Flexibilität.

### 2.8 Überwachen und Neu-Trainieren

Operative ML-Systeme erfordern kontinuierliches Monitoring. Die Plattform protokolliert Serving-Ein-/Ausgaben automatisch über Inference-Tabellen (Echtzeit) und Delta-Tabellen (Batch). Datenqualitäts-Monitoring verfolgt Feature Drift und Vorhersageverteilungen, mit Anomalieerkennungs-Alerts, die eingreifen, bevor sich die Performance deutlich verschlechtert.

## <a id="tools">3. Unterstützende Tools und Konzepte</a>

- **Unity Catalog** für verwaltete Daten- und Modellverwaltung.
- **MLflow** für Experiment- und Modell-Lifecycle-Tracking.
- **Genie Code** für KI-gestützte Notebook-Generierung und Troubleshooting.
- **Workspace-Suche** zur Asset-Auffindung.
- **Feature Store** für wiederverwendbares Feature-Management.
- **Model Serving** für Endpoint-Deployment.

## <a id="quelle">4. Quelle</a>

- https://docs.databricks.com/aws/en/machine-learning/concepts/ml-lifecycle

**Stand:** 2026-08-21.
