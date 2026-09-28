# Python-Entwicklung auf Databricks

Übersichtsseite für Python-Entwickler auf Databricks: Einstieg, Tutorials, Python-APIs (PySpark/Pandas API on Spark), Debugging, Code-Management, Cluster/Libraries, Visualisierungen, Jobs, Machine Learning und IDE-Integration. Teil der [Testing](../Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Einstiegsschritte](#einstieg)
2. [Tutorials](#tutorials)
3. [Debugging in Python-Notebooks](#debugging)
4. [Python-APIs: PySpark und Pandas API on Spark](#apis)
5. [Code-Management: Notebooks und Git Folders](#code-management)
6. [Cluster und Libraries](#cluster-libraries)
7. [Visualisierungen](#visualisierungen)
8. [Jobs](#jobs)
9. [Machine Learning](#ml)
10. [IDEs, Entwicklertools und SDKs](#ides)
11. [Weitere Ressourcen](#ressourcen)
12. [Quelle](#quelle)

---

## <a id="einstieg">1. Einstiegsschritte</a>

1. **Code importieren** — eigenen Code aus Dateien oder Git-Repositories importieren, oder Tutorials ausprobieren. Databricks empfiehlt den Einstieg über interaktive Databricks-Notebooks.
2. **Code auf einem Cluster ausführen** — eigenen Cluster erstellen oder Berechtigungen für einen gemeinsam genutzten Cluster erhalten, dann Notebook anhängen und ausführen.
3. **Fortgeschrittene Fähigkeiten** — größere Datensätze mit Apache Spark verarbeiten, Visualisierungen hinzufügen, Workloads als Jobs automatisieren, Machine Learning implementieren, in IDEs entwickeln, oder „Python-Unit-Tests im Workspace ausführen und verwalten" (siehe [01 Unit Test](../01%20Unit%20Test/)).

## <a id="tutorials">2. Tutorials</a>

**Data Engineering:** „Load and transform data using Apache Spark DataFrames"; „Create and manage Delta Lake tables"; „Build an ETL pipeline using change data capture".

**Data Science und ML:** Apache-Spark-DataFrames-Tutorial (cross-gelistet); „End-to-end classic ML models on Databricks"; **AutoML** — „Glass-Box-Ansatz generiert Notebooks mit dem vollständigen ML-Workflow, die geklont, modifiziert und erneut ausgeführt werden können"; „Manage model lifecycle in Unity Catalog".

## <a id="debugging">3. Debugging in Python-Notebooks</a>

Ein Beispiel-Notebook „illustriert die Nutzung des Python-Debuggers (pdb) in Databricks-Notebooks." Voraussetzung: Databricks Runtime 11.3 LTS oder höher. Ab Runtime 12.2 LTS zusätzlich ein Variable Explorer, der „den aktuellen Wert von Python-Variablen in der Notebook-UI nachverfolgt" und Werte beim Durchlaufen von Breakpoints beobachtet.

**Wichtige Einschränkung:** „`breakpoint()` wird in IPython nicht unterstützt und funktioniert daher in Databricks-Notebooks nicht. Stattdessen `import pdb; pdb.set_trace()` verwenden."

## <a id="apis">4. Python-APIs: PySpark und Pandas API on Spark</a>

„Python-Code, der außerhalb von Databricks läuft, kann grundsätzlich auch innerhalb von Databricks laufen, und umgekehrt." Databricks unterstützt sowohl Single-Machine- als auch verteilte Python-Workloads. Single-Machine-Computing nutzt Standard-Python-APIs und -Bibliotheken (pandas, scikit-learn). Für verteilte Workloads gibt es zwei Haupt-APIs:

**PySpark:** „die offizielle Python-API für Apache Spark" — „flexibler als die Pandas API on Spark, mit umfangreicher Unterstützung für Data-Science- und -Engineering-Funktionalität wie Spark SQL, Structured Streaming, MLlib und GraphX."

**Pandas API on Spark:** Das Koalas-Open-Source-Projekt „empfiehlt inzwischen den Wechsel zur Pandas API on Spark". Verfügbar ab Databricks Runtime 10.0 (für Runtime 9.1 LTS und darunter: Koalas nutzen). „pandas skaliert nicht auf Big Data" — die Pandas API on Spark „füllt diese Lücke, indem sie pandas-äquivalente APIs bereitstellt, die auf Apache Spark laufen" — ideal für mit pandas, aber nicht mit Apache Spark vertraute Data Scientists.

## <a id="code-management">5. Code-Management: Notebooks und Git Folders</a>

Databricks-Notebooks bieten „Funktionalität ähnlich der von Jupyter, mit Ergänzungen wie eingebauten Visualisierungen für Big Data, Apache-Spark-Integrationen für Debugging und Performance-Monitoring, und MLflow-Integrationen zur Nachverfolgung von ML-Experimenten."

**Notebook-State zurücksetzen:** entspricht dem Neustart des iPython-Kernels — für Jupyter-Nutzer die Entsprechung zu „restart kernel". Methode: Compute-Selector anklicken und **New session** wählen.

**Git Folders** synchronisieren Notebooks und andere Dateien mit Git-Repositories — hilft bei Code-Versionierung und Zusammenarbeit, vereinfacht den Import ganzer Code-Repositories, das Einsehen vergangener Notebook-Versionen und die IDE-Integration (siehe [Developers/Git Folders (Repos)](../../Developers/Git%20Folders%20%28Repos%29/)).

## <a id="cluster-libraries">6. Cluster und Libraries</a>

Databricks Compute „bietet Compute-Management für Cluster jeder Größe: von Single-Node-Clustern bis zu großen Clustern." Für kleinere Bedürfnisse bietet „Single Node Compute" Kosteneinsparungen. Administratoren können Cluster-Policies etablieren, um die Cluster-Erstellung zu vereinfachen und zu lenken.

**Databricks Runtime** liefert „viele populäre Bibliotheken von Haus aus, darunter Apache Spark, Delta Lake, pandas und mehr." Drei Anpassungsansätze:

1. **Default Libraries** — verfügbar in den Databricks-Runtime-Release-Notes; „Databricks Runtime for Machine Learning" für ML-Workloads empfohlen.
2. **Notebook-scoped Libraries** — über `%pip install my_library` aus PyPI oder anderen Repositories installieren, „auf allen Knoten des aktuell angehängten Clusters, ohne andere Workloads auf Compute mit Standard-Access-Mode zu beeinträchtigen."
3. **Compute-scoped Libraries** — für die Installation von Nicht-Python-Bibliotheken.

## <a id="visualisierungen">7. Visualisierungen</a>

Databricks-Python-Notebooks bieten „eingebaute Unterstützung für viele Visualisierungstypen." Legacy-Visualisierungsoptionen sind ebenfalls zugänglich. Populäre Drittanbieter-Bibliotheken: Bokeh, Matplotlib, Plotly (teils vorinstalliert, teils nachinstallierbar).

## <a id="jobs">8. Jobs</a>

Python-Workloads lassen sich als geplante oder getriggerte Jobs automatisieren — Jobs können Notebooks, Python-Skripte und Python-Wheel-Dateien ausführen.

**Erstellungs- und Verwaltungsoptionen:** Databricks-UI; REST-API; Python SDK (erlaubt programmatisches Erstellen, Bearbeiten, Löschen von Jobs); CLI.

**Tipp:** Um ein Python-Skript statt eines Notebooks zeitzuplanen, das Feld `spark_python_task` unter `tasks` im Body eines Create-Job-Requests nutzen.

## <a id="ml">9. Machine Learning</a>

„Databricks unterstützt eine breite Vielfalt an ML-Workloads, einschließlich traditionellem ML auf tabellarischen Daten, Deep Learning für Computer Vision und NLP, Empfehlungssysteme, Graph Analytics und mehr."

**ML-Bibliotheken:** „Databricks Runtime for Machine Learning enthält populäre Python-Tools wie scikit-learn, TensorFlow, Keras, PyTorch, Apache Spark MLlib und XGBoost."

**MLOps und Tracking:** Databricks bietet „einen verwalteten Dienst für die Open-Source-Bibliothek MLflow": **MLflow Tracking** (Modellentwicklung protokollieren, Modelle in wiederverwendbaren Formaten speichern); **MLflow Model Registry** (Promotion von Modellen Richtung Produktion verwalten und automatisieren); **Jobs und Model Serving** (Modelle als Batch-/Streaming-Jobs sowie als REST-Endpoints hosten).

## <a id="ides">10. IDEs, Entwicklertools und SDKs</a>

Externe Entwicklung mit IDEs wie PyCharm, Jupyter und Visual Studio Code. Synchronisationsmethoden:

1. **Code-Synchronisation via Git** — über Databricks Git Folders.
2. **Libraries und Jobs** — Bibliotheken (Python-Wheel-Dateien) extern erstellen, zu Databricks hochladen, in Notebooks oder Jobs nutzen.
3. **Remote Execution** — „Databricks Connect" erlaubt die Ausführung von Code aus lokalen IDEs für „interaktive Entwicklung und Testing", wobei die IDE mit Databricks kommuniziert, um „Apache Spark und große Berechnungen auf Databricks-Clustern auszuführen."

Databricks bietet „eine Reihe von SDKs, einschließlich eines Python-SDK, die Automatisierung und Integration mit externem Tooling unterstützen" — verwalten Ressourcen wie Cluster und Bibliotheken, Code und andere Workspace-Objekte, Workloads und Jobs.

## <a id="ressourcen">11. Weitere Ressourcen</a>

- **Databricks Academy** — selbstgesteuerte und Instructor-led-Kurse.
- **Databricks Labs** — Tools inkl. eines pytest-Plugins und eines pylint-Plugins für Python-Entwicklung.
- Interoperabilität: pandas Function APIs, pandas User-Defined Functions, Konvertierung zwischen PySpark- und pandas-DataFrames.
- **Databricks SQL Connector for Python** — SQL-Befehle per Python-Code auf Databricks-Ressourcen ausführen.
- **pyodbc** — Verbindung von lokalem Python-Code über ODBC zu im Databricks-Lakehouse gespeicherten Daten.

## <a id="quelle">12. Quelle</a>

- https://docs.databricks.com/aws/en/languages/python

**Stand:** 2026-08-21.
