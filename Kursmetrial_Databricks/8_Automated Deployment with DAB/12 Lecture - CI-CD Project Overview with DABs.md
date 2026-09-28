

In dieser Vorlesung betrachten Sie das **End-to-End-Projekt**, das für den Rest des Kurses verwendet wird: was es liefert, seine Architektur über Dev, Stage und Production hinweg, die Teststrategie (Unit-, Integrations- und Systemtests) und wie CI/CD mit Declarative Automation Bundles zusammenpasst.

## Lernziele

Am Ende dieser Vorlesung können Sie:

1. **Die Anforderungen und Architektur des Kursprojekts beschreiben.**
2. **Die Rolle von Unit-, Integrations- und Systemtests in CI/CD erklären.**
3. **Unit-Testing mit pytest und Pipeline-Expectations für Integrationstests wiederholen.**
4. **Beschreiben, wie CI/CD mit DABs über Development, Stage und Production hinweg funktioniert.**

## A. Das Projekt planen

### A1. Anforderungen

**Deliverable**
- Gesundheitsdaten visualisieren

**Tasks**
- Tägliche inkrementelle CSV-Dateien in eine Bronze-Tabelle ingesten
- Eine bereinigte Silver-Tabelle erstellen
- Gold-Tabellen erstellen, um sie mit Konsumenten zu teilen

**Databricks-Assets**
- Workspace mit Notebooks, SDP, Workflows, Compute

> **Zusätzliche Notizen:**
>
> - Das Projekt-Deliverable ist die Visualisierung von Gesundheitsdaten.
> - Die Tasks: tägliche inkrementelle CSV-Dateien in eine Bronze-Tabelle ingesten, eine bereinigte Silver-Tabelle erstellen und Gold-Tabellen erstellen, um sie mit Konsumenten zu teilen.
> - Die beteiligten Databricks-Assets umfassen einen Workspace mit Notebooks, Spark Declarative Pipelines (SDP), Workflows und Compute.

### A2. Architektur des Kursprojekts

Drei **Catalogs** (dev, stage, prod) speisen einen **Lakeflow Job**: Unit-Tests laufen zuerst, dann transformiert eine Spark Declarative Pipeline mit Expectations die Daten und erzeugt das Deliverable **Datenvisualisierung**.

> **Zusätzliche Notizen:**
>
> - Drei Catalogs halten die Daten in unterschiedlichen Umfängen: dev (eine kleine Teilmenge von prod), stage (eine größere Teilmenge von prod) und prod (die täglichen CSV-Dateien).
> - Innerhalb des Lakeflow Jobs laufen Unit-Tests zuerst, dann transformiert eine Spark Declarative Pipeline mit Expectations die Daten.
> - Das endgültige Deliverable ist die Datenvisualisierung, die auf der Ausgabe der Pipeline aufbaut.

## B. Teststrategie

### B1. Die Rolle des CI/CD-Testens wiederholen

Die Testpyramide reicht von vielen **schnellen** Unit-Tests an der Basis bis zu wenigen **langsamen** Systemtests an der Spitze.

- **Systemtests** – testen die gesamte Anwendung und sichern, dass alle Teile in einem realen Szenario zusammen funktionieren.
  *Bsp.:* End-to-End-Datenpipeline in einem Workflow. (Langsamer.)
- **Integrationstests** – testen die Interaktion zwischen verschiedenen Komponenten oder Systemen.
  *Bsp.:* Notebooks / Declarative Pipelines / Jobs.
- **Unit-Tests** – testen **einzelne** Funktionen oder Methoden isoliert. Schnell, kostengünstig, hohe Abdeckung und automatisiert.
  *Bsp.:* Benutzerdefinierte PySpark-Funktionen. (Die Basis.)

### B2. Wiederholung des Unit-Testens mit pytest

**Pytest** ist ein beliebtes Testframework für Python, das es einfach macht, einfache und skalierbare Testfälle zu schreiben.

- **Verwendet einfache Syntax** – minimale Syntax, definieren Sie einfach Funktionen, die mit **`test_`** beginnen
- **Bietet Assertions** – verwenden Sie **`assert`**-Anweisungen, um bei Fehlschlag detaillierte Fehlermeldungen zu liefern
- **Automatische Discovery** – findet und führt alle Tests **automatisch** mit einer einfachen Konfiguration aus
- **Reiches Ökosystem** – **erweitern** Sie die Funktionalität mit Plugins für Coverage, parallele Tests und mehr

> Dieser Kurs bietet eine einfache Einführung in **pytest**. Es gibt viele Testframeworks – wählen Sie das, das die Bedürfnisse Ihrer Organisation am besten erfüllt.

> **Zusätzliche Notizen:**
>
> - Pytest ist ein beliebtes Python-Testframework zum Schreiben einfacher und skalierbarer Testfälle.
> - Verwendet einfache Syntax: definieren Sie Funktionen, die mit `test_` beginnen.
> - Bietet Assertions: verwenden Sie `assert`-Anweisungen für detaillierte Fehlermeldungen bei Fehlschlag.
> - Automatische Discovery: findet und führt alle Tests automatisch mit einer einfachen Konfiguration aus.
> - Reiches Ökosystem: erweitern Sie die Funktionalität mit Plugins für Coverage, parallele Tests und mehr.

### B3. Wiederholung von Pipeline-Expectations für Integrationstests

**Derselbe** Spark-Declarative-Pipeline-Code (Notebooks) läuft über dev, stage und production. Test-Tabellen nutzen **Expectations** in dev und stage, um die Daten zu validieren – Validieren der Zeilenanzahl in Bronze- und Silver-Tabellen und der Distinct-Werte in der aggregierten View.

![Bild](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/lecture_ci_cd/pipeline-expectations.png)

> **Zusätzliche Notizen:**
>
> - Derselbe SDP-Code (Notebooks) definiert die Transformationslogik mit benutzerdefinierten Funktionen und wird in dev, stage und production verwendet.
> - Die Eingabequelle wird basierend auf Pipeline-Konfigurationsvariablen umgeschaltet und abstrahiert die Eingabedateien für dev (Dev-CSV), stage (Stage-CSV) und production (Production-CSV-Dateien).
> - Test-Tabellen nutzen Expectations in dev und stage – zum Beispiel Validieren der Zeilenanzahl in Bronze- und Silver-Tabellen und Validieren der Distinct-Werte in den neuen Spalten der aggregierten View.

## C. CI/CD mit DABs

### C1. Überblick über den CI/CD-Workflow auf hoher Ebene

Eine CI/CD-Pipeline führt aus: **Develop → Build → Test → Version Control** (Continuous Integration), dann **Deploy to Stage → Deploy to Production** (Continuous Delivery / Deployment). Mit DABs bewegen sich **dasselbe Bundle und derselbe Code** über die Targets – nur das `-t`-Target ändert sich.

> **Zusätzliche Notizen:**
>
> - Ein CI/CD-Workflow bewegt sich durch Develop, Build, Test und Version Control (Continuous Integration), dann Deploy to Stage und Deploy to Production (Continuous Delivery / Continuous Deployment).
> - Mit DABs werden dasselbe Bundle und derselbe Code über Umgebungen hinweg befördert; nur das Target ändert sich: `databricks bundle deploy -t development`, dann `-t stage`, dann `-t production`.
> - Das Deployen nach development geschieht während der CI-Phase; das Deployen nach stage und production geschieht während der CD-Phase.

## D. Fazit

- Das Kursprojekt ingestet tägliche CSVs über **bronze → silver → gold** und liefert eine **Datenvisualisierung**, über die Catalogs **dev, stage und production** hinweg.
- Das Testen reicht von schnellen **Unit-Tests** (pytest) über **Integrationstests** (Pipeline-Expectations) bis zu **Systemtests** (End-to-End-Workflow).
- **CI** deckt develop, build, test und version control ab; **CD** deckt Deploy to Stage und Production ab.
- Mit DABs bewegen sich **dasselbe Bundle und derselbe Code** über die Targets – nur das `-t`-Target ändert sich.
