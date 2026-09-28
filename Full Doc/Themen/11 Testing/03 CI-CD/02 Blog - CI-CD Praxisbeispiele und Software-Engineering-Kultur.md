# Blog: CI/CD-Praxisbeispiele und Software-Engineering-Kultur

Kuratierte Zusammenfassung von acht Databricks-Blogartikeln zu CI/CD-Praxis, historischen Fallstudien und Tooling. Teil der [Testing](../Uebersicht.md)-Reihe. Diese Zusammenfassungen geben Blog-Inhalte wieder — im Gegensatz zu den übrigen Dateien dieses Projekts handelt es sich um Marketing-/Engineering-Blog-Artikel, nicht um offizielle Referenz-Dokumentation; Aussagen sind entsprechend als Blog-Narrativ, nicht als normative Spezifikation zu verstehen.

## Abschnittsübersicht

1. [DevOps für Delta Live Tables](#dlt-devops)
2. [Software-Engineering-Best-Practices für Notebooks](#notebook-best-practices)
3. [CI/CD für Data Pipelines (2017)](#cicd-2017)
4. [Metacogs CI/CD-Pipeline für Apache Spark (2016)](#metacog)
5. [Produktionsreif und automatisiert (2020)](#productionize)
6. [Databricks Labs CI/CD Templates](#labs-templates)
7. [CI/CD mit Notebooks und Azure DevOps (Teil 1)](#azure-devops-notebooks)
8. [GitHub Actions für Databricks](#github-actions)
9. [Quelle](#quelle)

---

## <a id="dlt-devops">1. DevOps für Delta Live Tables</a>

Artikel von Alex Ott (28. April 2023) zu Software-Development- und DevOps-Best-Practices für Delta-Live-Table-(DLT)-Pipelines, inkl. Teststrategien und CI/CD-Automatisierung.

**Kernprinzip:** Standard-DevOps-Praktiken (Versionskontrolle, Code-Reviews, Umgebungstrennung, automatisiertes Testen, CI/CD) lassen sich effektiv auf Data-Pipeline-Entwicklung anwenden — ermöglicht durch Databricks Repos (Git-Integration), Databricks CLI/REST-API und den Databricks-Terraform-Provider.

**Entwicklungs-Workflow:** Feature-Branch erstellen → Commit und Pull Request → CI/CD aktualisiert Staging-Repo und führt Unit Tests aus → nach erfolgreichem Review Merge in Main → Release-Pipeline deployt in Production.

**Interaktiver Entwicklungszyklus:** Typischerweise wird Code im Notebook geschrieben, die Pipeline im **Development-Modus** ausgeführt (vermeidet wiederholte Ressourcen-Initialisierung bei jedem Lauf), Ergebnisse analysiert und iteriert. Bei komplexen Pipelines wird dieser Zyklus langsam — die Lösung: Code so strukturieren, dass sich einzelne Transformationen unabhängig mit Beispieldaten auf einem interaktiven Cluster testen lassen (siehe Code-Struktur unten).

**Code-Struktur für Testbarkeit:** Transformationslogik von DLT-Pipeline-Definitionen trennen — Python-Module über „Files in Repos" organisieren, sodass DLT-Pipeline-Code dünn bleibt und primär Datenfluss durch importierte Transformationsfunktionen orchestriert. Empfohlenes Layout: ein dedizierter Ordner für die Transformationsfunktionen (als Python-Package), getrennte Testverzeichnisse für Unit- und Integrationstests, sowie DLT-Pipeline-Notebooks, die nur noch diese paketierten Funktionen aufrufen:

```python
from transformations.data_processing import clean_bronze_data

@dlt.table
def silver_layer():
    bronze_data = dlt.read("bronze_table")
    return clean_bronze_data(bronze_data)
```

Dieses Layout ermöglicht leichteres interaktives Testen, echte Unit-Testbarkeit und Code-Wiederverwendung über mehrere Pipelines hinweg.

**Unit Testing:** zwei Ansätze:

- **Lokal (pytest-basiert):** Entwicklung und Test in der lokalen IDE; Code-Sync über die VS-Code-Extension oder (historisch) `dbx sync` — zu `dbx` siehe [06 dbx (Legacy, archiviert).md](../05%20Andere%20Themen/06%20dbx%20%28Legacy%2C%20archiviert%29.md); Ausführung in CI/CD, ohne Databricks-Ressourcen zu verbrauchen; volles Debugging, Coverage-Analyse und Refactoring-Tooling der IDE nutzbar.
- **Notebook-basiert:** schnelleres interaktives Feedback; Tools wie Nutter triggern die Ausführung aus CI/CD und sammeln Ergebnisse fürs Reporting.

Beide Ansätze funktionieren für Python-basierte DLT-Pipelines; SQL-basierte Pipelines sind auf den Integrationstest-Ansatz angewiesen.

**Integrationstests:** zwei Methoden werden vorgestellt:

- **Databricks-Workflows-Ansatz:** ein mehrstufiger Workflow aus Daten-Setup → Pipeline-Ausführung → Ergebnisvalidierung. **Nachteil:** benötigt erheblichen Zusatzcode sowie zusätzliche Compute-Ressourcen.
- **DLT-Expectations-Ansatz (empfohlen):** die DLT-Pipeline um zusätzliche Tabellen mit angehängten Expectations im `fail`-Modus erweitern, um z. B. zu prüfen, dass die Silver-Tabelle in der `type`-Spalte nur erlaubte Werte enthält:

  ```python
  @dlt.table
  @dlt.expect("valid_types", "type IN ('A', 'B', 'C')")
  def silver_validation():
      return dlt.read("silver_layer")
  ```

  Benötigt keine zusätzlichen Compute-Ressourcen, integriert sich in die bestehende DLT-Ausführung (Cluster-Wiederverwendung), validiert ohne Zusatzcode und protokolliert Ergebnisse ins DLT-Event-Log.

**Umgebungs-Promotion:** Zu promovierende Assets sind zum einen der Quellcode der Transformationen, zum anderen die Pipeline-Konfiguration. **Code-Promotion** erfolgt über die Databricks-Repos-REST-API oder -CLI; DLT trennt bewusst Code von Pipeline-Konfiguration, sodass identische Transformationslogik mit umgebungsspezifischen Einstellungen (Schemas, Datenpfade, Clustergrößen) kombiniert werden kann. Für die **Konfigurationsverwaltung** selbst sind REST-API und CLI zwar nutzbar, empfohlen wird aber der **Databricks-Terraform-Provider** — insbesondere für Instance Pools, Cluster-Policies und Abhängigkeiten, da Terraform-Module wiederverwendbare Infrastruktur-Patterns ermöglichen.

**Azure-DevOps-Beispiel:** zwei Stages — `onPush` (auf jedem Branch außer dem Release-Branch: Checkout, Poetry-Installation, Staging-Repo-Update, lokale + notebook-basierte Unit Tests via Nutter, Testergebnisse veröffentlichen) und `onRelease` (nur auf dem Release-Branch: zusätzlich Integrationstests gegen die DLT-Pipeline, danach separate Release-Pipeline mit Production-Repo-Update, sodass Codeänderungen beim nächsten DLT-Lauf wirksam werden).

**Praxis-Ressource:** Der Artikel verlinkt ein vollständiges Demo-Repository mit funktionierenden Python- und SQL-DLT-Implementierungen, lokalen und notebook-basierten Unit Tests, Azure-DevOps-Pipeline-Konfiguration sowie Terraform-Deployment-Code für ein Multi-Umgebungs-Setup.

**Kernbotschaft des Artikels:** Der empfohlene Entwicklungsworkflow behandelt DLT-Pipelines wie reguläre Softwareprodukte — mit Versionskontrolle, Test-Gates und stufenweiser Promotion — statt wie Ad-hoc-Skripte.

**Im Artikel referenzierte Diagramme** (Bildmaterial nicht in dieses Projekt übernommen, nur Themen aufgeführt): High-Level-DLT-Entwicklungsworkflow, Beispiel-Bronze-/Silver-Layer-Pipeline-Struktur, Python-Package-Organisation innerhalb von Repos, Integrationstest-Workflow über DLT-Expectations, Workflow-basierte Integrationstest-Struktur, Aufgabenorganisation der Azure-DevOps-Build-Pipeline.

## <a id="notebook-best-practices">2. Software-Engineering-Best-Practices für Notebooks</a>

Inhaltsgleich mit der offiziellen Doku-Seite `notebooks/best-practices` — vollständig behandelt in [01 Unit Test/06 Notebook Best Practices (Software Engineering).md](../01%20Unit%20Test/06%20Notebook%20Best%20Practices%20%28Software%20Engineering%29.md).

## <a id="cicd-2017">3. CI/CD für Data Pipelines (2017)</a>

Früher Grundlagenartikel zu CI/CD-Herausforderungen bei Data Pipelines, gegliedert in fünf Phasen: Datenexploration, iterative Entwicklung mit Unit Tests, Continuous Integration/Build, Staging-Umgebungs-Testing, Production-Deployment.

**Empfohlenes Team-Setup:** eine Entwicklungsumgebung je Nutzer (eigene Workspace-Ordner, eigene kleine Cluster). Workflow: Git-Branch erstellen → Workspace-CLI zum Kopieren von Notebooks → DBFS-CLI für Bibliotheken → persönlicher Cluster via API/UI → Bibliotheken über Libraries API anhängen.

**Hybrider Notebook-+-Library-Ansatz:** Kernlogik in Java-/Scala-Klassen oder Python-Packages in lokalen IDEs refaktorieren, leichtgewichtige, häufig wechselnde Geschäftslogik bleibt in Notebooks. Vorteile: Parametrisierung ohne Neukompilierung, einfaches Verketten mit Fail-Fast, Performance-Analyse pro Zelle, visuelles Troubleshooting, programmatischer Exit-Status.

**Blue/Green-Production-Deployment:** neue Libraries an neuen DBFS-Speicherort pushen, neue Notebooks in neuen Unterordner eines zugriffsbeschränkten Produktionsbereichs deployen, Job-Konfiguration auf neue Pfade umstellen — ermöglicht einfachen Rollback.

## <a id="metacog">4. Metacogs CI/CD-Pipeline für Apache Spark (2016)</a>

Fallstudie: Metacog (Learning-Analytics-API-Plattform, verarbeitet Aktivitätsdaten von zig Millionen gleichzeitigen Lernenden) implementierte CI/CD für gesamten Spark-Code mit Jenkins.

**Pipeline:** Commit auf GitHub-Master-Branch → Jenkins testet und baut automatisch → JAR mit inkrementierter Versionsnummer nach S3 → Python-Skript nutzt Databricks-„libraries/create"-API mit S3-Pre-Signed-URL → Deployment via Jobs API (`deployJar`-Job kopiert JAR von S3 nach `dbfs:/FileStore/job-jars`) → `jobs/reset`-Endpoint aktualisiert Produktions-/Staging-Jobs.

**Ergebnisse:** Feature-Deployment-Zeit von ~1 Monat auf 1–2 Wochen reduziert (Release-Kadenz von 12 auf 24+ pro Jahr verdoppelt); mindestens 28 % AWS-EC2-Kosteneinsparung durch automatisches Cluster-Lifecycle-Management; neue Data Scientists in 1 statt 4 Wochen produktiv; ca. 20 % der Entwicklerzeit durch Wegfall manueller Infrastrukturpflege eingespart; Performance-Bugs auf großen Datensätzen in halber Zeit gelöst.

## <a id="productionize">5. Produktionsreif und automatisiert (2020)</a>

Behandelt drei Hauptprobleme beim Skalieren von Daten-/ML-Betrieb: inkonsistente Entwicklungsumgebungen, fehlende DevOps-Prozesse, eingeschränkte Sichtbarkeit.

**Automatisierte Umgebungs-Provisionierung** in fünf Schritten: Workspace deployen (Workspace-REST-APIs/Terraform), Datenquellen verbinden, Nutzer/Gruppen provisionieren (SCIM/IdP-Sync), Cluster und Policies erstellen, Berechtigungen vergeben.

**Dreistufige CI/CD-Architektur:** Development (Notebooks + Databricks Connect + Git), Staging/Integration (Jenkins/Azure DevOps, Databricks Pools), Production (gesperrter Workspace, REST-APIs).

**Operatives Monitoring:** Infrastruktur (Ganglia/Datadog), Plattform (Cluster-/Job-Performance via REST-API), Anwendung (Spark-Logs).

## <a id="labs-templates">6. Databricks Labs CI/CD Templates</a>

Open-Source-Cookiecutter-Tool zur Vereinfachung von CI/CD auf Databricks.

**Quick Start:** `pip install cookiecutter` → `cookiecutter https://github.com/databrickslabs/cicd-templates.git` → Credentials konfigurieren, zu GitHub committen. Die generierte Pipeline testet automatisch bei Commits und deployt in Production bei GitHub Releases.

**Problem:** `%run`-basierte Workarounds fehlt Code-Wiederverwendbarkeit, automatisiertes Testen, Job-/Cluster-Automatisierung und Dependency-Management.

**Projektstruktur:** Hauptpaket (Ingestion, Validierung, Transformation, Feature Engineering, ML-Logik), `pipelines`-Verzeichnis (je Pipeline ein `pipeline_runner.py` + cloud-spezifische Job-JSON), getrennte Developer-/Integration-Test-Ordner.

**Lifecycle:** lokale Entwicklung (Databricks Connect) → GitHub-Push löst GitHub Actions aus (pytest, Wheel-Build, Deployment, Developer-Tests) → GitHub Release löst Integrationstests + automatisches Production-Deployment als Databricks Jobs aus.

**Multi-Cloud-Support:** Templates funktionieren auf Azure und AWS.

## <a id="azure-devops-notebooks">7. CI/CD mit Notebooks und Azure DevOps (Teil 1)</a>

Zweiteilige Serie zum Aufbau von MLOps-Lösungen mit Notebooks, der Repos API und Azure DevOps — demonstriert an einem Kreditscoring-Modell (Kaggle Lending Club Dataset).

**Entwicklungszyklus:** Feature-Entwicklung in Feature-Branches mit Notebook-Unit-Tests → Push löst CI/CD aus → Azure DevOps ruft die Databricks-Repos-API zur Aktualisierung des Test-Projekts auf → Integrationstest-Jobs via Jobs API → Ergebnisauswertung.

**Drei-Umgebungen-Architektur:** Development (lockere Zugriffskontrolle), Staging, Production (strikte Berechtigungsverwaltung) — gemeinsames Versionskontrollsystem, getrennte Daten- und MLflow-Instanzen (Shared-Nothing-Prinzip).

**Deploy-Skript (`deploy.py`):** erstellt temporäres Repo und pullt die neueste Revision, triggert Integrationstest-Job, wartet auf Abschluss und prüft Ergebnisse. Die Azure-Pipeline-YAML behandelt Databricks-Notebooks „wie einfache Python-Dateien".

## <a id="github-actions">8. GitHub Actions für Databricks</a>

Ankündigung erster First-Party-GitHub-Actions von Databricks zur CI/CD-Automatisierung für Daten-/ML-Anwendungen.

**Fähigkeiten:** Notebooks aus dem Repository auf Databricks ausführen und auf Abschluss warten; Notebooks mit Bibliotheksabhängigkeiten aus Repo und PyPI ausführen; bestehende Workspace-Notebooks ausführen; mehrere Workspaces sequenziell ansteuern (z. B. Staging dann Production); mehrere Notebooks in Serie mit Output-Weitergabe ausführen.

**Anwendungsfälle:** Integrationstests bei Pull Requests, ML-Trainings-Pipelines bei Push auf Main, beschleunigte Deployment-Zyklen.

*Hinweis:* Diese ursprüngliche Ankündigung wird durch die aktuelle, vollständige GitHub-Actions-Referenz in [Developers/CI-CD/04 GitHub Actions Integration.md](../../Developers/CI-CD/04%20GitHub%20Actions%20Integration.md) ersetzt/vertieft.

## <a id="quelle">9. Quelle</a>

- https://www.databricks.com/blog/applying-software-development-devops-best-practices-delta-live-table-pipelines
- https://www.databricks.com/blog/2022/06/25/software-engineering-best-practices-with-databricks-notebooks.html
- https://www.databricks.com/blog/2017/10/30/continuous-integration-continuous-delivery-databricks.html
- https://www.databricks.com/blog/2016/04/06/continuous-integration-and-delivery-of-apache-spark-applications-at-metacog.html
- https://www.databricks.com/blog/2020/03/16/productionize-and-automate.html
- https://www.databricks.com/blog/2020/06/05/automate-continuous-integration-and-continuous-delivery-on-databricks-using-databricks-labs-ci-cd-templates.html
- https://www.databricks.com/blog/2021/09/20/part-1-implementing-ci-cd-on-databricks-using-databricks-notebooks-and-azure-devops.html
- https://www.databricks.com/blog/2022/06/02/automate-your-data-and-ml-workflows-with-github-actions-for-databricks.html

**Stand:** 2026-09-01.
