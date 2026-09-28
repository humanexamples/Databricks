Durch die Umsetzung von Continuous Deployment können Databricks-Engineers Effizienz, Zuverlässigkeit und Skalierbarkeit ihrer Datenoperationen erheblich verbessern. Das führt letztlich zu schnelleren und effektiveren datengetriebenen Entscheidungen in ihren Organisationen. Wenn wir an CD denken, denken wir an
- Schnellere Time-to-Market
- Verbesserte Zusammenarbeit
- Skalierbarkeit
- Konsistenz über verschiedene Workspaces und Umgebungen hinweg
- Automatisierung von Bereitstellungen

In dieser Vorlesung erhalten Sie einen Überblick über die Bereitstellung von Databricks-Assets und erkunden Bereitstellungsoptionen, Declarative Automation Bundles und wie man sie in einen Entwicklungs- und CI/CD-Workflow integriert.

## Lernziele

Am Ende dieser Vorlesung können Sie:
1. Den Unterschied zwischen den Anwendungsfällen der Databricks REST API, CLI und des SDK verstehen und demonstrieren
2. Verstehen, wie Best Practices der Softwareentwicklung mit DABs unterstützt werden
3. Verstehen, wie DABs für CI/CD verwendet werden

---

## A. Bereitstellungsoptionen

### REST API

![REST-API-Symbol](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_deploying_databricks_assets_overview/rest_API_databricks.png)

### Databricks CLI

![Databricks-CLI-Symbol](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_deploying_databricks_assets_overview/databricks_CLI.png)

Kommandozeilen-Schnittstelle, die die REST API kapselt. Ideal für einmalige Aufgaben, Experimente und Shell-Skripting.

### Databricks SDKs

![Databricks-SDK-Symbol](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_deploying_databricks_assets_overview/databricks_SDK.png)

- Verfügbar für mehrere Programmiersprachen (Python, Java, Go, R)
- Ermöglicht die Entwicklung von Anwendungen, eigenen Databricks Lakeflow Jobs und robuster Fehlerbehandlung
- Programmatische Möglichkeit, mit Databricks-Ressourcen zu interagieren

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> **Wichtige Vergleiche:**
>
> - **Benutzerfreundlichkeit:** SDK > CLI > REST API
> - **Flexibilität:** REST API > SDK > CLI
>
> **REST API** – Postman und Databricks
>
> **CLI** – Kommandozeile
>
> **SDK** – Python, Go, R, Java
>
> **REST API:** Am flexibelsten, aber komplex – am besten für eigene Integrationen.
>
> **CLI:** Vereinfacht REST-API-Operationen, hat aber begrenzte Flexibilität.
>
> **SDK:** Am entwicklerfreundlichsten – am besten, um Databricks-Funktionalität in Anwendungen einzubetten.

---

## B. Declarative Automation Bundles und Praktiken der Softwareentwicklung

> Databricks empfiehlt Declarative Automation Bundles zum Erstellen, Entwickeln, Bereitstellen und Testen von Jobs und anderen Databricks-Ressourcen.

**Declarative Automation Bundles → Praktiken der Softwareentwicklung**

- **Versionskontrolle** – Die Praxis, Änderungen an Code und anderen Entwicklungsartefakten über die Zeit zu verfolgen und zu verwalten.
- **Code-Review** – Systematische Untersuchung von Quellcode mit dem Ziel, Fehler zu finden und zu beheben, die Qualität zu verbessern und Coding-Standards durchzusetzen.
- **Testing** – Der Prozess, die erwartete Ausgabe relevanter Funktionen zu validieren und vorab festgelegte Anforderungen einzuhalten.
- **Continuous Integration** – Der Prozess, Entwicklung, Testen und Bereitstellung zu automatisieren, um Zuverlässigkeit sicherzustellen.

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> Declarative Automation Bundles (DABs) sind darauf ausgelegt, die Einführung von Best Practices der Softwareentwicklung zu erleichtern, insbesondere für Daten- und KI-Projekte. Hier benennen wir 4 Kernkomponenten der SWE-Praktiken, die von DABs unterstützt werden.
>
> - **Versionskontrolle:** Wie verfolgen wir Änderungen und pflegen eine Historie von Codeänderungen?
> - **Code-Review:** Wie wahren wir die Codequalität, und halten wir Coding-Standards ein?
> - **Testing:** Ist unser Coding-Verhalten konsistent und vorhersehbar?
> - **Continuous Integration:** Automatisieren wir verschiedene Prozesse für die Integration von Codeänderungen in unser Repository?
>
> Declarative Automation Bundles bieten einen strukturierten Ansatz zum Verwalten von Databricks-Projekten unter Einhaltung von Best Practices der Softwareentwicklung. Durch die Kombination von Infrastructure-as-Code-Prinzipien mit Automatisierungsfähigkeiten straffen sie die Zusammenarbeit, verbessern die Qualitätssicherung und ermöglichen die effiziente Lieferung datengetriebener Lösungen.
>
> - DABs integrieren sich nahtlos in Git-basierte Lakeflow Jobs und ermöglichen Nutzenden, ihre Databricks-Ressourcen zusammen mit dem Quellcode zu versionieren
> - Indem Databricks-Ressourcen als Code behandelt werden, ermöglichen DABs Peer-Review über Standard-Git-Lakeflow-Jobs wie Pull Requests
> - Entwickler können die Databricks-CLI mit DABs verwenden, um Tests für Bundles in isolierten Umgebungen auszuführen und sicherzustellen, dass Lakeflow Jobs wie beabsichtigt funktionieren
> - DABs integrieren sich in CI/CD-Werkzeuge wie GitHub Actions oder Azure DevOps, um Validierung, Bereitstellung und Ausführung von Databricks Lakeflow Jobs zu automatisieren

---

## C. Declarative Automation Bundles

- **Code einmal schreiben, überall bereitstellen** – **YAML**-Dateien, die die **Artefakte, Ressourcen** und **Konfigurationen** eines Databricks-Projekts angeben. Das führt zu einfacher Konfiguration komplexer Notebook- und Pipeline-Interaktionen und **Reproduzierbarkeit** Ihrer Lakeflow Jobs.
- **Was sind Declarative Automation Bundles?** – DABs sind ein Werkzeug, das diesen Prozess für **Databricks-Projekte** **strafft**. Diese Bundles kapseln alle notwendigen Konfigurationen und Artefakte.
- **Wie funktionieren Bundles?** – Bundles bieten eine exakte **Definition** der Databricks-Ressourcen, die in Ihrem Projekt verwendet werden sollen, mit Unterstützung für **Validierungs-** und **Bereitstellungsanweisungen**.

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> Erstellen Sie Code, der ohne Änderung über mehrere Umgebungen hinweg bereitgestellt werden kann. Das stellt Konsistenz sicher, reduziert manuelle Fehler und beschleunigt die Lieferung durch die Automatisierung von Bereitstellungsprozessen.
>
> DABs sind ein Werkzeug, das diesen Prozess für Databricks-Projekte strafft. Sie ermöglichen Entwicklern, Databricks-Ressourcen (wie Jobs, Pipelines und Notebooks) als Quelldateien und Metadaten im YAML-Format zu definieren.
>
> DABs funktionieren, indem Sie zunächst Ihre Ressourcen und Anforderungen in einer databricks.yml-Datei definieren. Anschließend validieren Sie das Bundle mit der Databricks-CLI und deployen es in Ihren gewählten Workspace. Nach der Bereitstellung können die im Bundle beschriebenen Lakeflow Jobs oder Pipelines ausgeführt werden.

---

## D. Entwicklung und CI/CD mit DABs

- Entwicklung und CI/CD mit DABs
- Databricks Workspaces

![Architektur von Entwicklung und CI/CD mit DABs](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_deploying_databricks_assets_overview/development_ci_cd_with_dabs.png)

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> Hier präsentieren wir eine Übersicht der Architektur für Entwicklung und CI/CD mit DABs.
>
> - Wenn Sie lokal arbeiten, bauen Sie das Projekt-Bundle mit Ihrem Team über ein lokales Umgebungs-Setup.
> - Als Nächstes führen Sie Versionskontrolle mit dem Projekt-Repository durch, wo Nutzende Änderungen committen.
> - Nutzende können manuell deployen, um die Änderungen in ihrem Entwicklungs-Workspace zu testen
> - Wenn Nutzende Änderungen committen, wird eine Benachrichtigung ausgelöst, um die CI/CD-Pipeline nach Staging und Produktion umzusetzen.
>
> Zusammengefasst: Declarative Automation Bundles (DABs) sind ein Werkzeug, das die Verwaltung und Bereitstellung von Daten- und KI-Projekten auf der Databricks-Plattform vereinfacht. Sie folgen einem Infrastructure-as-Code-Ansatz (IaC) und ermöglichen Nutzenden, Databricks-Ressourcen – wie Jobs, Pipelines, Notebooks und Machine-Learning-Modelle – über YAML-Konfigurationsdateien zu definieren und zu verwalten. Diese Bundles straffen Zusammenarbeit, Testen, Bereitstellung und Versionskontrolle über verschiedene Umgebungen hinweg.

---

## E. Fazit

- Zu den Bereitstellungsoptionen zählen REST API, Databricks CLI und Databricks SDKs.
- Declarative Automation Bundles helfen, Databricks-Ressourcen, -Konfigurationen und -Artefakte für wiederholbare Bereitstellungen zu definieren.
- DABs unterstützen Praktiken der Softwareentwicklung sowie Entwicklungs- und CI/CD-Workflows über Databricks Workspaces hinweg.

### Nächste Schritte

In der nächsten Demo führen Sie durch, wie das Projekt bereitgestellt wird.

---

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
