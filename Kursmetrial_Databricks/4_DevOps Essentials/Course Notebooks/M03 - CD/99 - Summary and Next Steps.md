![Databricks Academy](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/icons/databricks_academy.png)

---

# Zusammenfassung und nächste Schritte

---

## A. Was Sie erreicht haben

Im Laufe dieses Kurses haben Sie ein einzelnes Data-Engineering-Projekt – eine End-to-End-Medallion-Pipeline (Bronze → Silber → Gold) – genommen und es mit Best Practices der Softwareentwicklung und von DevOps gehärtet, eine Disziplin nach der anderen.

```
  Modularer Code  →  Unit-Tests  →  Integrationstests  →  Versionskontrolle (Git)  →  Deployment (DABs)
  ───────────────────────── Continuous Integration ──────────────────────────         ──── CD ────
```

| Schritt | Modul | Was Sie getan haben |
|------|--------|--------------|
| 1 | M02 | **Best Practices der Softwareentwicklung** überprüft – Lesbarkeit, Benennung, Dokumentation, Testing, Versionskontrolle und Code-Review – und wo CI/CD hineinpasst |
| 2 | M02 | **PySpark-Code modularisiert** und Inline-Pipeline-Logik in wiederverwendbare Funktionen verwandelt |
| 3 | M02 | **DevOps- und DataOps-Grundlagen** und den Lebenszyklus als kontinuierliche Praxis gelernt |
| 4 | M02 | **Die Rolle von CI/CD**, die Testpyramide und die Branching-Strategie erkundet |
| 5 | M02 | **Das Projekt geplant** und Dev, Stage und Prod mit Workspace- und Unity-Catalog-Isolierung isoliert |
| 6 | M02 | **Unit-Tests** für PySpark mit `pytest` und `pyspark.testing.utils` geschrieben und ausgeführt |
| 7 | M02 | **Integrationstests** mit SDP-Expectations und Lakeflow-Jobs-Aufgaben durchgeführt |
| 8 | M02 | **Versionskontrolle** mit Databricks Git Folders und GitHub angewendet |
| 9 | M03 | Bereitstellungsoptionen verglichen und **Databricks-Assets** mit Declarative Automation Bundles (DABs) **bereitgestellt** |

---

## B. Wichtigste Erkenntnisse

- **Modularität ist der Wegbereiter.** Sie können Code nicht sauber per Unit-Test testen oder wiederverwenden, bevor er in Funktionen zerlegt ist – daher kommt die Modularisierung zuerst, und alles andere baut darauf auf.
- **Die Testpyramide leitet, wo investiert werden sollte:** viele günstige, schnelle **Unit-Tests** an der Basis; weniger, langsamere **Integrationstests** in der Mitte; kostspielige **Systemtests** an der Spitze.
- **In Databricks hat Integrationstesten zwei idiomatische Wege:** SDP-**Expectations** (deklarative Datenqualitätsregeln innerhalb der Pipeline) und **Lakeflow-Jobs**-Aufgaben (orchestrierte Validierungsschritte).
- **Umgebungsisolierung** – separate Workspaces und Unity-Catalog-Kataloge/-Schemas für Dev, Stage und Prod – macht sicheres CI/CD überhaupt erst möglich.
- **Declarative Automation Bundles (DABs) sind das empfohlene Bereitstellungsmittel**, weil sie Code und Konfiguration deklarativ paketieren und sich direkt in einen CI/CD-Workflow einfügen. Die REST API, CLI und das SDK sind Low-Level-Alternativen für spezifische Anforderungen.

---

## C. Zusätzliche Ressourcen

Erkunden Sie die folgenden Ressourcen, um Ihr Verständnis von DevOps und CI/CD in Databricks zu vertiefen.

### C1. Dokumentation

- **CI/CD in Databricks** – der End-to-End-Workflow und die verfügbaren Werkzeuge:
[AWS](https://docs.databricks.com/aws/en/dev-tools/ci-cd/) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/ci-cd/) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/ci-cd/)

- **Best Practices und empfohlene CI/CD-Workflows** – Versionskontrolle, Testing und Umgebungsisolierung:
[AWS](https://docs.databricks.com/aws/en/dev-tools/ci-cd/best-practices) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/ci-cd/best-practices) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/ci-cd/best-practices)

- **Was sind Declarative Automation Bundles (DABs)?** – Infrastructure-as-Code für Databricks-Projekte:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/)

- **CI/CD mit Declarative Automation Bundles ausführen** – Validieren, Bereitstellen und Ausführen automatisieren:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/ci-cd) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/ci-cd) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/ci-cd)

- **Unit-Testing für Databricks-Notebooks** – `pytest` und sprachspezifische Test-Frameworks:
[AWS](https://docs.databricks.com/aws/en/notebooks/testing) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/notebooks/testing) |
[GCP](https://docs.databricks.com/gcp/en/notebooks/testing)

- **Databricks Git Folders verwenden** – Versionskontrolle mit GitHub und anderen Git-Providern:
[AWS](https://docs.databricks.com/aws/en/repos/) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/repos/) |
[GCP](https://docs.databricks.com/gcp/en/repos/)

### C2. Blogs und Ankündigungen

- [Announcing the General Availability of Databricks Asset Bundles](https://www.databricks.com/blog/announcing-general-availability-databricks-asset-bundles) – Wie DABs es Ihnen ermöglichen, Jobs, Pipelines und Notebooks als eine Einheit zu versionieren, zu testen, bereitzustellen und gemeinsam daran zu arbeiten.

---

## D. Nächste Schritte

### D1. Wenden Sie das Gelernte an

- Führen Sie die Labs mit den Daten Ihres eigenen Projekts erneut aus: **modularisieren** Sie Ihr PySpark, fügen Sie **Unit-Tests** hinzu und richten Sie dann einen **Integrationstest** sowohl mit einer SDP-Expectation als auch mit einer Jobs-Aufgabe ein, sodass Sie beide Methoden erlebt haben.
- Treiben Sie die Versionskontrolle weiter: erstellen Sie einen **Feature-Branch**, öffnen Sie einen **Pull Request** und üben Sie ein **Code-Review** – die eine DevOps-Disziplin, die der Kurs beschreibt, aber nicht erzwingt.
- Bauen Sie ein echtes **Declarative Automation Bundle** (`databricks.yml`) für Ihr Projekt, deployen Sie es auf ein **dev**-Ziel und promoten Sie es dann nach **stage** und **prod**. Automatisieren Sie von dort aus `bundle validate` und `bundle deploy` in einem CI-Werkzeug wie GitHub Actions, um den vollständigen CI/CD-Kreis zu schließen.

### D2. Setzen Sie Ihr Lernen fort

Dieser Kurs ist Teil des **Data Engineer Learning Path**. Bauen Sie Ihre Daten- und KI-Kompetenzen weiter aus – über selbstgesteuertes und von Trainern geleitetes Databricks-Training.

Besuchen Sie [Databricks Training and Certification](https://www.databricks.com/learn/training/home).

### D3. Erwerben Sie eine Zertifizierung

Weisen Sie Ihre Expertise mit den Zertifikaten **Databricks Certified Data Engineer Associate** und **Professional** nach, die Best Practices der Softwareentwicklung und des Produktionsbetriebs auf der Plattform abdecken.

Besuchen Sie [Databricks Certification and Badging](https://www.databricks.com/learn/training/certification).

---

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
