# Testing — Überblick

Sammelt alles rund um das Testen von Notebooks, Lakeflow-Pipelines und ML-Workflows auf Databricks, sowie die dazugehörige CI/CD- und Git-Workflow-Kultur — gegliedert entlang der klassischen Testpyramide (Unit Test → Integrationstest) plus Delivery-Themen (CI/CD, Git Workflow) und einer Restkategorie für angrenzende, nicht eindeutig zuordenbare Themen.

## Bereits an anderer Stelle abgedeckt (nicht dupliziert)

Ein Teil der angefragten URLs deckt sich mit Inhalten, die bereits ausführlich unter [Developers](../Developers/) dokumentiert sind:

- `repos/`, `repos/repos-setup`, `repos/git-operations-with-repos`, `repos/ci-cd` → [Developers/Git Folders (Repos)](../Developers/Git%20Folders%20%28Repos%29/)
- `dev-tools/ci-cd/`, `dev-tools/ci-cd/flows`, `dev-tools/ci-cd/github`, `dev-tools/ci-cd/azure-devops`, `dev-tools/ci-cd/jenkins` → [Developers/CI-CD](../Developers/CI-CD/)
- `dev-tools/bundles/workspace` → [Developers/Databricks Asset Bundles/06 Bundles im Workspace (Web-UI).md](../Developers/Databricks%20Asset%20Bundles/06%20Bundles%20im%20Workspace%20%28Web-UI%29.md)
- Die `gcp/en/...`-Spiegelseiten von `notebooks/testing`, `dev-tools/vscode-ext/pytest`, `dev-tools/ci-cd`, `dev-tools/ci-cd/azure-devops` wurden geprüft — inhaltlich/strukturell deckungsgleich mit den AWS-Fassungen, daher nicht separat dokumentiert.

## Struktur dieses Kapitels

Die Gliederung folgt der klassischen Testpyramide (Unit → Integration) plus den beiden Delivery-Themen, nach denen ausdrücklich gefragt wurde (CI/CD, Git Workflow), plus einer Restkategorie für Inhalte, die keiner der vier Hauptkategorien eindeutig zuzuordnen sind (z. B. ML-Lifecycle, allgemeine Developer-Best-Practices, Python-Entwicklung), aber im Kontext relevant bleiben.

## Themen in diesem Kapitel

### 1. [Unit Test](01%20Unit%20Test/)

Testen einzelner, in sich geschlossener Code-Einheiten (Funktionen) — in Notebooks, im Workspace, über die VS-Code-Extension und mit Databricks Connect.

1. [01 Notebook-Testing Grundlagen.md](01%20Unit%20Test/01%20Notebook-Testing%20Grundlagen.md) — unittest/pytest/testthat/ScalaTest, Organisationsansätze je Sprache, praktische Testmuster (Widgets, `%run`-Auslagerung).
2. [02 Python-Unit-Tests im Workspace (UI).md](01%20Unit%20Test/02%20Python-Unit-Tests%20im%20Workspace%20%28UI%29.md) — Testing-Sidebar, Inline-Ausführung, Ergebnis-Panel.
3. [03 Testing mit Databricks Connect.md](01%20Unit%20Test/03%20Testing%20mit%20Databricks%20Connect.md) — lokales pytest gegen Remote-Cluster.
4. [04 pytest in der VS-Code-Extension.md](01%20Unit%20Test/04%20pytest%20in%20der%20VS-Code-Extension.md) — pytest vs. Databricks Connect in der IDE.
5. [05 Notebook Workflows als Testing-Orchestrierung (Legacy-Beispiel).md](01%20Unit%20Test/05%20Notebook%20Workflows%20als%20Testing-Orchestrierung%20%28Legacy-Beispiel%29.md) — `dbutils.notebook.run()`/`exit()`.
6. [06 Notebook Best Practices (Software Engineering).md](01%20Unit%20Test/06%20Notebook%20Best%20Practices%20%28Software%20Engineering%29.md) — Versionskontrolle, Modularität, Teststrategie, CI/CD-Trigger.
7. [07 PySpark-Testing-Utilities und Praxisbeispiel.md](01%20Unit%20Test/07%20PySpark-Testing-Utilities%20und%20Praxisbeispiel.md) — `assertDataFrameEqual`/`assertSchemaEqual`, vollständiges Health-Datensatz-Beispiel mit pytest-Fixtures (privates Kursmaterial).
8. [08 pytest — Grundlagen und Referenz.md](01%20Unit%20Test/08%20pytest%20%E2%80%94%20Grundlagen%20und%20Referenz.md) — offizielle pytest-Doku: Kernfunktionen, Minimalbeispiel, Dokumentationsstruktur.
9. [09 chispa — PySpark-Testbibliothek.md](01%20Unit%20Test/09%20chispa%20%E2%80%94%20PySpark-Testbibliothek.md) — Community-Assertion-Bibliothek: Spalten-/DataFrame-Gleichheit, Vergleichsoptionen, Näherungsvergleich, eigene Fehlerformatierung.
10. [10 nutter — Databricks-Notebook-Testing.md](01%20Unit%20Test/10%20nutter%20%E2%80%94%20Databricks-Notebook-Testing.md) — Microsofts Notebook-Testing-Framework: `NutterFixture`, Lifecycle-Methoden, CLI, Azure-DevOps-Integration.
11. [11 unittest — Python-Standardbibliothek-Referenz.md](01%20Unit%20Test/11%20unittest%20%E2%80%94%20Python-Standardbibliothek-Referenz.md) — vollständige `unittest`-API-Referenz: Assertions, Setup/Teardown, Discovery, Skipping, Async-Tests.
12. [12 assertDataFrameEqual und assertSchemaEqual (API-Referenz).md](01%20Unit%20Test/12%20assertDataFrameEqual%20und%20assertSchemaEqual%20%28API-Referenz%29.md) — vollständige Parameter- und Beispiel-Referenz beider `pyspark.testing`-Kernfunktionen, direkt aus dem Docstring der Referenzimplementierung.

### 2. [Integrationstest](02%20Integrationstest/)

Testen des Zusammenspiels mehrerer Komponenten — Tabellenketten, ganze Pipelines, Pipeline+Anwendung gemeinsam.

1. [01 Lakeflow Pipelines Unit Testing.md](02%20Integrationstest/01%20Lakeflow%20Pipelines%20Unit%20Testing.md) — offizielles Beta-Framework (trotz Namens funktional Integrationstest für Tabellenketten, Auto-CDC, Joins).
2. [02 Integrationstest-Konzepte auf Databricks.md](02%20Integrationstest/02%20Integrationstest-Konzepte%20auf%20Databricks.md) — Synthese: Drei-Ebenen-Testmodell, Workflow-basierte Tests, DLT-Expectations, MLOps-Staging-Integrationstests, Data-Contract-/Regression-Tests, Bundle-Validierung.
3. [03 SDP-Integrationstest-Patterns (Praxisbeispiel).md](02%20Integrationstest/03%20SDP-Integrationstest-Patterns%20%28Praxisbeispiel%29.md) — vollständiges Codebeispiel: umgebungsparametrisierte `@dp.expect_all_or_fail`-Tests (dev/stage/prod) sowie Job-Tasks-Alternative (privates Kursmaterial).

### 3. [CI-CD](03%20CI-CD/)

1. [01 CI-CD Best Practices.md](03%20CI-CD/01%20CI-CD%20Best%20Practices.md) — die sechs offiziellen Kernprinzipien.
2. [02 Blog - CI-CD Praxisbeispiele und Software-Engineering-Kultur.md](03%20CI-CD/02%20Blog%20-%20CI-CD%20Praxisbeispiele%20und%20Software-Engineering-Kultur.md) — acht Blogartikel: DLT-DevOps, historische Fallstudien (2016–2022), CI/CD-Templates, Azure DevOps, GitHub Actions.

Vertiefte offizielle CI/CD-Referenz (Grundlagen, Workflows, Azure DevOps/GitHub Actions/Jenkins im Detail) siehe [Developers/CI-CD](../Developers/CI-CD/).

### 4. [Git Workflow](04%20Git%20Workflow/)

1. [01 Jobs mit Git-Quellcode.md](04%20Git%20Workflow/01%20Jobs%20mit%20Git-Quellcode.md) — Remote-Git-Repositories als Job-Quelle, Sparse Checkout.
2. [02 Blog - Repos-Historie und Features.md](04%20Git%20Workflow/02%20Blog%20-%20Repos-Historie%20und%20Features.md) — Produktionsreife (2021), GA-Ankündigung, Konfliktauflösung, OAuth-2.0-Support.
3. [03 Blog - Asset Bundles und Git-Workflows (Ankuendigungen).md](04%20Git%20Workflow/03%20Blog%20-%20Asset%20Bundles%20und%20Git-Workflows%20%28Ankuendigungen%29.md) — Dashboard-Deployment via Bundles, Bundles im Workspace, Git-Support für Jobs.
4. [04 Blog - Lakebase Database Branching.md](04%20Git%20Workflow/04%20Blog%20-%20Lakebase%20Database%20Branching.md) — Git-artiges Copy-on-Write-Branching für Postgres/Lakebase (thematisch verwandt, kein Databricks-Git-Feature im engeren Sinn).

Vertiefte offizielle Git-Referenz (Konfiguration, Operationen, Automatisierung, private Netzwerke, Troubleshooting) siehe [Developers/Git Folders (Repos)](../Developers/Git%20Folders%20%28Repos%29/).

### 5. [Andere Themen](05%20Andere%20Themen/)

Inhalte, die im Kontext von Testing/CI-CD/Git relevant sind, aber keiner der vier Hauptkategorien eindeutig zuzuordnen sind.

1. [01 ML-Lifecycle.md](05%20Andere%20Themen/01%20ML-Lifecycle.md) — der Acht-Phasen-ML-Weg (Development/Staging/Production).
2. [02 MLOps-Workflow.md](05%20Andere%20Themen/02%20MLOps-Workflow.md) — vollständiger MLOps-Referenzworkflow.
3. [03 Python-Entwicklung auf Databricks.md](05%20Andere%20Themen/03%20Python-Entwicklung%20auf%20Databricks.md) — Übersichtsseite für Python-Entwickler.
4. [04 Allgemeine Developer Best Practices.md](05%20Andere%20Themen/04%20Allgemeine%20Developer%20Best%20Practices.md) — Source Control, Workspace-Konfiguration, Bundle-Management.
5. [05 Blog - MLOps, DataOps und KI-gestuetzte Entwicklung.md](05%20Andere%20Themen/05%20Blog%20-%20MLOps%2C%20DataOps%20und%20KI-gestuetzte%20Entwicklung.md) — MLOps vs. DevOps, DataOps-Strategie, Coding-Agent-Benchmarking.
6. [06 dbx (Legacy, archiviert).md](05%20Andere%20Themen/06%20dbx%20%28Legacy%2C%20archiviert%29.md) — Hinweis zur nicht mehr verfügbaren Archiv-Seite.

**Stand:** 2026-09-01.
