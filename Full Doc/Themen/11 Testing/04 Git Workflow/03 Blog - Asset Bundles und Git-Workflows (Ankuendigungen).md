# Blog: Asset Bundles und Git-Workflows (Ankündigungen)

Kuratierte Zusammenfassung von drei Databricks-Ankündigungs-/Tutorial-Blogartikeln: Dashboard-Deployment mit Asset Bundles, Bundles im Workspace, und Git-Support für Lakeflow Jobs. Teil der [Testing](../Uebersicht.md)-Reihe. Blog-Inhalte, keine normative Referenzdokumentation — für die aktuelle, vollständige Referenz siehe [Developers/Databricks Asset Bundles](../../Developers/Databricks%20Asset%20Bundles/).

## Abschnittsübersicht

1. [AI/BI-Dashboard-Änderungen sicher mit Asset Bundles ausliefern](#dashboard-tutorial)
2. [Ankündigung: Asset Bundles jetzt im Workspace](#bundles-workspace)
3. [Git-Support für Databricks Workflows](#git-jobs)
4. [Quelle](#quelle)

---

## <a id="dashboard-tutorial">1. AI/BI-Dashboard-Änderungen sicher mit Asset Bundles ausliefern</a>

**Kernproblem:** Produktions-Dashboards treiben kritische Geschäftsentscheidungen (Hiring-Pläne, Produkteinführungen, Umsatzprognosen), werden aber oft manuell ohne Versionierung, Review oder kontrollierte Bereitstellung gepflegt. Leitprinzip: „produktionsreife, geschäftskritische Dashboards müssen mit derselben Disziplin verwaltet werden wie Produktionscode."

**Voraussetzungen:** mehrere Databricks-Workspaces (mind. Dev/Prod), Git-Backed Folders, konfigurierte Declarative Automation Bundles.

**Workflow:**

1. **Dashboard zum Bundle hinzufügen** — Git Folder anlegen und mit Repository verbinden; im Bundle-Editor **Add** → **Add existing dashboard**; Baseline committen (**Commit & Push**) als bekannt-guten Checkpoint.
2. **Dashboard aktualisieren** — Branch über **Create Branch** anlegen (mit aussagekräftigem Namen), Änderungen im Standard-UI-Editor vornehmen, committen.
3. **Änderung reviewen** — Pull Request beim Git-Provider erstellen; die Produktions-Version bleibt währenddessen unberührt; automatisierte Test-Deployments bei PR-Eröffnung ermöglichen Vorab-Review.
4. **In Production deployen** — `${variable}`-Syntax in `databricks.yml` für umgebungsspezifische Werte (Catalogs, Schemas, SQL-Warehouses); nach PR-Merge automatisiertes Deployment mit den passenden Werten je Zielumgebung.

**Zusatzfunktionen:** **Historie einsehen** (jedes Update als Zeitstempel-Eintrag mit Autor); **Änderungen zurücksetzen** über **Revert** (erzeugt eine „Undo"-Änderung, die nur diese eine Modifikation rückgängig macht, „Reaktion auf einen Ausfall in Minuten"); **Koordinierte Datenquellen-Updates** — Bundles gruppieren Dashboards und ihre Daten-Pipelines in ein Deployment-Paket, sodass Datenmodell- und Visualisierungsänderungen gemeinsam deployen.

## <a id="bundles-workspace">2. Ankündigung: Asset Bundles jetzt im Workspace</a>

Public-Preview-Ankündigung von Declarative Automation Bundles direkt in der Workspace-UI — adressiert die häufige Nutzerfrage „Kann ich das direkt im Workspace nutzen, ohne CLI oder VS Code?"

**Kernfeatures:** Zusammenspiel aus Workspace, Git Folders und Asset Bundles; Jobs/Pipelines weiterhin „as Code" definierbar und CI/CD-fähig; expliziter **Deploy**-Schritt für bewusste Dev-zu-Prod-Übergänge; `source_linked_deployment` für schnellere Iteration (Ressourcen referenzieren automatisch die neuesten Dateien ohne manuelle Synchronisation).

**Möglich seither:** Git-Repositories mit Bundles in den Workspace klonen; Bundles aus vordefinierten Templates erstellen; Jobs/Pipelines über die UI definieren; Deployments per Klick ausführen; Deployments über visuelle Panels verfolgen; Änderungen zurück nach Git committen.

*Hinweis:* Diese Ankündigung ist in der aktuellen, vollständigen Form in [Developers/Databricks Asset Bundles/06 Bundles im Workspace (Web-UI).md](../../Developers/Databricks%20Asset%20Bundles/06%20Bundles%20im%20Workspace%20%28Web-UI%29.md) dokumentiert.

## <a id="git-jobs">3. Git-Support für Databricks Workflows</a>

Ankündigung der nativen Git-Integration für Databricks Workflows (heute Lakeflow Jobs) — erlaubt Remote-Git-Repositories als Quelle für Workflow-Tasks.

**Kernfeatures:** Unterstützung mehrerer Git-Provider (GitHub, GitLab, Bitbucket, Azure DevOps, AWS CodeCommit); jeder Job-Lauf ist an einen bestimmten Commit-Hash gebunden — garantiert, dass alle Notebook-Tasks eines Multi-Task-Jobs vom selben Commit laufen, mit protokollierter Commit-SHA je Ausführung (Reproduzierbarkeit, Audit-Trail).

**Produktionssicherheit:** Git als Single Source of Truth eliminiert Risiken durch versehentliche Bearbeitung von Produktionscode; keine separaten Produktionskopien von Code im Workspace mehr nötig.

**Setup (vier Schritte):** Git-Provider-PAT-Credentials hinzufügen → Job mit Remote-Repository/Referenz/Notebook-Pfad erstellen → weitere Tasks hinzufügen → Job ausführen und Details in der UI prüfen. Integriert mit Jobs-API-Versionen 2.1 und 2.0.

**Einschränkung bei Multi-Task-Jobs:** Notebook-Tasks, die Databricks-Workspace/Repos referenzieren, können nicht mit Tasks gemischt werden, die Remote-Repositories nutzen — gilt nicht für Nicht-Notebook-Tasks.

**Kundenzitate:** „vereinfachte unser CI/CD, ersetzte eine Mischung aus Python-Skripten … befreite uns von der Verwaltung" von Produktionskopien; „reduzierte die Komplexität unserer Produktions-Deployments um ein Drittel."

*Hinweis:* Die aktuelle, vollständige Referenz (inkl. Sparse Checkout) findet sich in [01 Jobs mit Git-Quellcode.md](01%20Jobs%20mit%20Git-Quellcode.md).

## <a id="quelle">4. Quelle</a>

- https://www.databricks.com/blog/tutorial-how-ship-aibi-dashboard-changes-safely-scale-databricks-asset-bundles
- https://www.databricks.com/blog/announcing-databricks-asset-bundles-now-workspace
- https://www.databricks.com/blog/2022/06/21/build-reliable-production-data-and-ml-pipelines-with-git-support-for-databricks-workflows.html

**Stand:** 2026-08-21.
