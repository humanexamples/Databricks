# CI/CD — Grundlagen und Empfehlungen

Behandelt die siebenstufige CI/CD-Pipeline auf Databricks, die empfohlenen Tools sowie Databricks Asset Bundles als primären Ansatz gegenüber Alternativen (Git Folder, Git mit Jobs). Teil der [CI/CD](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [High-Level-CI/CD-Flow](#flow)
2. [Empfohlene Tools](#tools)
3. [Databricks Asset Bundles als primärer Ansatz](#bundles)
4. [Alternative Source-Control-Optionen](#alternativen)
5. [Quelle](#quelle)

---

## <a id="flow">1. High-Level-CI/CD-Flow</a>

Siebenstufige Pipeline:

1. **Version:** Code in Versionskontrollsystemen wie Git speichern, Git Folders zum Verfassen und Testen vor dem Commit nutzen (siehe [Git Folders (Repos)](../Git%20Folders%20%28Repos%29/)).
2. **Code:** Notebooks im Workspace oder lokal per IDE entwickeln — über den Lakeflow Pipelines Editor oder die Databricks-VS-Code-Extension.
3. **Build:** Databricks-Asset-Bundles-Einstellungen zum automatischen Bauen von Artefakten nutzen; Pylint mit dem Databricks-Labs-Plugin für Code-Qualitätsdurchsetzung erweitern.
4. **Deploy:** Databricks Asset Bundles mit Azure DevOps, GitHub Actions oder Jenkins zum Deployen von Workspace-Änderungen nutzen.
5. **Test:** automatisiertes Testen mit Tools wie pytest zur Validierung von Code-Änderungen implementieren.
6. **Run:** Runs über die Databricks CLI mit Bundles automatisieren (`databricks bundle run`).
7. **Monitor:** Performance mit Job-Monitoring-Tools überwachen, um Produktionsprobleme zu identifizieren.

## <a id="tools">2. Empfohlene Tools</a>

| Tool | Zweck |
|---|---|
| **Databricks Asset Bundles** | Primäre Empfehlung zur programmatischen Definition, Deployment und Ausführung von Databricks-Ressourcen (Jobs, Pipelines, MLOps Stacks) |
| **Databricks Terraform Provider** | Provisionierung und Verwaltung von Workspaces und Infrastruktur |
| **Azure DevOps Integration** | CI/CD-Pipelines mit Azure DevOps entwickeln |
| **GitHub Actions** | Databricks-spezifische GitHub Actions in CI/CD-Workflows einbinden |
| **Jenkins** | CI/CD-Pipelines mit der Jenkins-Plattform entwickeln |
| **Apache Airflow** | Data Pipelines orchestrieren und zeitplanen |
| **Service Principals** | CI/CD-Authentifizierung ohne Nutzerkonten ermöglichen |
| **OAuth Token Federation** | sicherste Authentifizierungsmethode, eliminiert die Notwendigkeit für Secrets |

## <a id="bundles">3. Databricks Asset Bundles als primärer Ansatz</a>

Die Doku bezeichnet Databricks Asset Bundles als „den empfohlenen Ansatz für CI/CD auf Databricks." Sie erlauben es, Ressourcen als gebündelte Quelldateien zu beschreiben, die eine vollständige Projektdefinition ergeben.

**Kernmerkmale:** Kompatibilität mit Versionskontrolle; benutzerdefinierte Templates für organisationsweite Konsistenz; umfassende Unterstützung für Ressourcen-Deployment; erfordert Kenntnis der Bundle-Konfigurationssyntax.

Vertiefte Referenz siehe [Databricks Asset Bundles](../Databricks%20Asset%20Bundles/).

## <a id="alternativen">4. Alternative Source-Control-Optionen</a>

### Git-Folder-Ansatz

„Git Folders lassen sich nutzen, um den Zustand eines Remote-Git-Repositories widerzuspiegeln." Diese Methode erlaubt das Anlegen produktionsreifer Ordner, die quellcodeverwaltete Dateien und Notebooks verwalten — sinnvoll, wenn externe CI/CD-Pipelines nicht verfügbar sind (siehe [Git Folders (Repos)/04 CI-CD und Automatisierung.md](../Git%20Folders%20%28Repos%29/04%20CI-CD%20und%20Automatisierung.md)).

### Git mit Jobs

Erlaubt, Job-Typen so zu konfigurieren, dass sie Remote-Repositories als Code-Quelle nutzen — Databricks erstellt beim Job-Lauf einen Snapshot des Repositories. Einschränkung: „Nur Code-Dateien (Notebooks und andere Dateien) sind quellcodeverwaltet. Job-Konfigurationen wie Task-Sequenzen, Compute-Einstellungen und Zeitpläne sind nicht quellcodeverwaltet."

## <a id="quelle">5. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/ci-cd/

**Stand:** 2026-08-21.
