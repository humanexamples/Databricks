
### A1. Woraus besteht ein Databricks-Projekt?

Jedes Databricks-Projekt, von einem einfachen Report bis zu einer vollständigen MLOps-Pipeline, ist aus denselben drei Arten von **Komponenten** aufgebaut:

**Code** – die Logik, die Ihre Datenprodukte erzeugt.
- Notebooks, Python-`.whl`, JAR, dbt
- SQL / Python / R

**Ressourcen** – die Databricks-Objekte, auf denen Ihr Code läuft.
- Lakeflow Jobs / Workflows
- MLflow Tracking Server & Registry
- Spark Declarative Pipelines (SDP)

**Ausführungsumgebung** – wo und wie das Projekt läuft.
- Databricks Workspace
- Unity Catalog
- Compute-Konfiguration(en)

**Projekte erzeugen eine Vielzahl von Datenprodukten:**
- Tabellen
- Pipelines
- Jobs
- Machine-Learning-Modelle
- Dashboards
- Aufrufe externer Dienste
- usw.

**Das Deliverable bestimmt die Komponenten:**
- **Ein einfacher Report** könnte aus einem Notebook bestehen, das auf Single-Node-Compute läuft.
- **Eine vollständige MLOps-Pipeline** würde Komponenten wie MLflow, Feature Store und Model Serving erfordern.

> **Zusätzliche Notizen (Sprechernotizen):**
>
> - Ein Databricks-Projekt besteht aus mehreren Komponenten, darunter Code, Notebooks, Python-Dateien, Python-Wheel-Dateien, JARs, dbt und mehr.
> - Es umfasst außerdem eine Ausführungsumgebung innerhalb eines oder mehrerer Databricks-Workspaces, zusammen mit spezifischen Compute-Konfigurationen für die Verarbeitung.
> - Schließlich kann das Projekt weitere Databricks-Ressourcen umfassen, etwa Lakeflow Jobs, MLflow, Spark Declarative Pipelines und mehr.
> - Ein Databricks-Projekt erzeugt typischerweise eine Vielzahl von Datenprodukten, darunter Tabellen, Pipelines, Modelle, Jobs, Dashboards und mehr.
> - Die Deliverables Ihres Projekts bestimmen die benötigten Komponenten. Ein einfacher Report könnte ein oder mehrere Notebooks auf einfachem Single-Node-Compute umfassen; eine vollständige MLOps-Pipeline würde mehrere Komponenten erfordern, etwa MLflow, den Feature Store, Model-Serving-Komponenten, Notebooks und mehr.

### A2. Komponenten eines einfachen Beispielprojekts

Ein konkretes Beispiel: die drei Komponententypen, abgebildet auf ein einfaches Databricks-Projekt. Der Workspace enthält die Assets; die Zuordnung ist:

**Code**
- Python-/SQL-/R-Notebooks

**Ressourcen**
- Lakeflow Jobs
- Spark Declarative Pipelines (SDP)

**Ausführungsumgebung**
- Databricks Workspace
- Unity Catalog
- Compute-Konfiguration(en)

> **Zusätzliche Notizen (Sprechernotizen):**
>
> - Ein einfaches Data-Engineering-Databricks-Projekt könnte Notebooks, Spark Declarative Pipelines, einen Workflow, Catalogs innerhalb von Unity Catalog und spezifische Compute-Konfigurationen für das Projekt umfassen.

## B. Die CI/CD-Reise zur Produktion

Code bewegt sich über die Versionskontrolle – ein **Pull Request** in Stage, ein **Release** in Main – und jeder Branch wird in seine eigene Umgebung deployed.

```
Versionskontrolle:  dev  --Pull Request-->  stage  --Release-->  main
                     |                       |                    |
                   Deploy                  Deploy               Deploy
                     v                       v                    v
                 development              staging             production
```

Jede Umgebung enthält Notebooks, SDP, Workflows und Unity Catalog, aber mit unterschiedlicher Konfiguration:

| Umgebung | Konfiguration |
| --- | --- |
| **development** | Single Node · Run as User · Dev-Daten und -Umgebung verwenden |
| **staging** | **Serverless** · Run as **Service Principal** · Staging-Daten und -Umgebung verwenden |
| **production** | **Serverless** · Run as **Service Principal** · **wöchentlicher** Zeitplan |

> **Zusätzliche Notizen (Sprechernotizen):**
>
> - Zunächst brauchen Sie eine Versionskontrollstrategie. Ihre Strategie könnte z. B. Dev-, Stage- und Main-Branches umfassen.
> - Beginnen Sie damit, Ihr Databricks-Projekt in die Entwicklungsumgebung zu deployen. Das erlaubt Ihnen, Änderungen oder Updates auf Entwicklungsdaten mit spezifischen Entwicklungskonfigurationen zu testen.
> - Nach Abschluss der Entwicklung und dem Erstellen eines Pull Requests in Ihren Stage-Branch deployen Sie in die Staging-Umgebung. Das sichert, dass das Testen Ihres Projekts auf neuen Staging-Daten mit den passenden Staging-Konfigurationen weitergeht.
> - Sobald sowohl Entwicklungs- als auch Staging-Umgebung getestet wurden und alle Tests bestanden haben, können Sie in Ihren Main- bzw. Production-Branch deployen. Das deployt Ihr Projekt vollständig in die Produktion und nutzt Produktionsdaten und die notwendigen Produktionskonfigurationen.
> - Für die Entwicklung konfigurieren wir die Umgebung so, dass sie Single-Node-Compute verwendet, da unsere Daten klein sind und kein großes Cluster erfordern. Wir führen das Projekt mit unserem Benutzerkonto auf den Entwicklungsdaten aus.
> - In Staging streben wir an, der Produktionsumgebung nahezukommen. Hier verwenden wir Serverless Compute, um Ressourcen nach Bedarf zu skalieren. Wir führen das Projekt mit einer Service-Principal-Identität aus, die automatisierten Werkzeugen nur Zugriff auf die notwendigen Databricks-Ressourcen gibt – bessere Sicherheit als Benutzer- oder Gruppenzugriff. Das erfolgt mit unseren Staging-Daten.
> - Für die Produktion verwenden wir weiterhin Serverless Compute und die Service-Principal-Identität. Das Projekt läuft mit Produktionsdaten, und wir stellen es so ein, dass es wöchentlich läuft, um die Daten für unsere Konsumenten zu aktualisieren.

## C. Die CI/CD-Reise orchestrieren

Databricks bietet drei Wege, das Deployment zu automatisieren: die **REST-API**, die **Databricks-SDKs** und die **Databricks CLI**. Dieser Kurs verwendet die CLI mit Declarative Automation Bundles (DABs).

Vor DABs gab es drei Wege, das Deployment zu orchestrieren, jeder mit Kompromissen.

| Ansatz | Werkzeug | Vorteile | Nachteile |
| --- | --- | --- | --- |
| **Manuell** | Die **UI** | Leicht zu erlernen, hohes Abstraktionsniveau | Zeitaufwendig; fehleranfällig; keine praktikable Option für den CI/CD-Prozess |
| **Programmatisch** | Databricks **REST-API** oder **SDK** | Low-Level-Kontrolle | Viele APIs zu erlernen; viele Klassen zu erlernen; zeitaufwendig, den gesamten CI/CD-Prozess zu automatisieren |
| **Terraform** | Databricks-**Terraform**-Provider | Sehr mächtig und ausdrucksstark; bevorzugtes Admin-Werkzeug für Konfiguration | Kann für Data Scientists und Engineers schwer zu erlernen sein |

> **Zusätzliche Notizen (Sprechernotizen):**
>
> - Erstens können wir das manuell tun. Vorteil: Die UI ist leicht zu erlernen und zu navigieren. Aber es ist extrem zeitaufwendig, das Projekt jedes Mal manuell zu deployen, hochgradig fehleranfällig durch menschliche Interaktion und keine praktikable Option für den CI/CD-Prozess, in dem wir das Deployment automatisieren wollen.
> - Zweitens können wir das programmatisch mit der Databricks REST-API oder dem SDK tun. Vorteil: Low-Level-Kontrolle. Nachteile: erfordert mittlere bis fortgeschrittene Programmierkenntnisse, Sie müssen viele APIs oder Klassen lernen, und alles zu codieren, um den gesamten CI/CD-Prozess zu automatisieren, kann extrem zeitaufwendig sein.
> - Schließlich können erfahrene Terraform-Nutzer das verwenden. Es ist ein sehr mächtiges und ausdrucksstarkes Werkzeug, das Administratoren typischerweise zur Infrastrukturverwaltung nutzen. Aber es kann für Data Scientists und Engineers herausfordernd sein und fügt ein weiteres zu erlernendes und zu verwaltendes Werkzeug hinzu.

## D. Vereinfachung mit DABs

### D1. Wie kann der CI/CD-Prozess vereinfacht werden?

Das Ziel: **Code einmal schreiben und dann leicht in mehrere Umgebungen deployen.** Die Wunschliste unten ist genau das, was Declarative Automation Bundles liefern – eine Definition, die sich zu Development, Staging und Production auffächert.

**Was wäre, wenn wir …**
- Code zusammen mit allen Konfigurationen in einem einfachen, leicht verständlichen Format wie YAML versionieren könnten?
- Databricks-Ressourcen mit bestehenden REST-API-Parametern definieren könnten?
- Benutzerisolation während des Deployments sicherstellen könnten?
- umgebungsbasierte Overrides und Variablen angeben könnten?

Deploy von **Assets** und **Konfigurationseinstellungen** in mehrere Umgebungen:

| Umgebung | Konfiguration |
| --- | --- |
| **development** | Single Node · Run as User · Dev-Daten und -Umgebung verwenden |
| **staging** | Serverless · Run as Service Principal · Staging-Daten und -Umgebung verwenden |
| **production** | Serverless · Run as Service Principal · wöchentlicher Zeitplan |

> **Zusätzliche Notizen (Sprechernotizen):**
>
> - Wie können wir Code einmal für unser Projekt schreiben und ihn dann leicht in mehrere Umgebungen deployen, während wir unsere Konfigurationen anpassen?
> - Was, wenn wir Code zusammen mit allen Konfigurationen in einem einfachen, leicht verständlichen Format wie YAML versionieren könnten? YAML ist ein menschenlesbares Format, das Daten über Einrückung und minimale Syntax organisiert, was es leichter verständlich und editierbar macht als XML oder JSON.
> - Databricks-Ressourcen mit bestehenden REST-API-Parametern definieren? Das hält Parameter konsistent mit den anderen Techniken.
> - Benutzerisolation während des Deployments sicherstellen? Das hilft zu verhindern, dass Benutzer sich während des Deployments gegenseitig in die Quere kommen.
> - Umgebungsbasierte Overrides und Variablen angeben? Das lässt uns Werte je nach Zielumgebung leicht überschreiben und sichert Flexibilität für jede Umgebung.

### D2. Vorstellung der Declarative Automation Bundles (DABs)!

**Declarative Automation Bundles (DABs)** – ein Werkzeug, das die Einführung von Software-Engineering-Best-Practices erleichtert – einschließlich Source Control, Code Review, Testen und **Continuous Integration and Delivery (CI/CD) – für Ihre Daten- und KI-Projekte.**

> **Zusätzliche Notizen (Sprechernotizen):**
>
> - Ein Werkzeug, das die Einführung von Software-Engineering-Best-Practices erleichtert, einschließlich Source Control, Code Review, Testen und Continuous Integration and Delivery (CI/CD), für Ihre Daten- und KI-Projekte.
> - Databricks empfiehlt DABs für das Erstellen, Entwickeln, Deployen und Testen von Jobs und anderen Databricks-Ressourcen als Quellcode.
