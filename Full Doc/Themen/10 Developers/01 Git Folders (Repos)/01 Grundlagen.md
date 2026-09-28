# Git Folders — Grundlagen

Databricks Git Folders (früher „Repos") sind „ein visueller Git-Client und eine API, die Git-Repositories in den Workspace integriert." Sie erlauben es, an Code in Notebooks und Dateien zu arbeiten und dabei Software-Engineering-Best-Practices wie Versionskontrolle, Zusammenarbeit und CI/CD einzuhalten.

## Abschnittsübersicht

1. [Struktur der Doku-Reihe](#struktur)
2. [Fähigkeiten von Git Folders](#faehigkeiten)
3. [Git-Folders-API](#api)
4. [Git-Provider](#provider)
5. [Unterstützte Asset-Typen](#asset-typen)
6. [Namensregeln](#namensregeln)
7. [Nicht unterstützte Asset-Typen](#nicht-unterstuetzt)
8. [Quelle](#quelle)

---

## <a id="struktur">1. Struktur der Doku-Reihe</a>

Die offizielle Doku gliedert sich in vier Bereiche:

- **Erste Schritte:** Konzepte, Git-Integration konfigurieren, Git Folders erstellen/verwalten, unterstützte Asset-Typen.
- **Automatisierung und CI/CD:** CI/CD mit Git Folders, Automatisierung mit Service Principal, Automatisierung mit Terraform.
- **Fortgeschrittene Konfiguration:** Git aktivieren/deaktivieren, private Git-Konnektivität (Proxy), Serverless Private Git.
- **Troubleshooting und Support:** Einschränkungen und FAQ, Fehler und Troubleshooting, Migration von Repos zu Git Folders.

## <a id="faehigkeiten">2. Fähigkeiten von Git Folders</a>

- **Repository-Operationen:** Klonen, Push, Pull auf/von Remote-Git-Repositories.
- **Branch-Management:** Branches erstellen, verwalten, mergen, rebasen, Konflikte lösen.
- **Datei-Erstellung/-Bearbeitung:** Notebooks (inkl. `.ipynb`) und andere Dateitypen.
- **Suchfunktion:** Text-Suche und -Ersetzung über mehrere Dateien hinweg im Notebook-Editor.
- **Visueller Vergleich:** Side-by-Side-Diff-Ansicht bei Commits und Merge-Konflikt-Auflösung.

## <a id="api">3. Git-Folders-API</a>

Databricks bietet eine API zur programmatischen Integration mit CI/CD-Pipelines. Ein zentraler Anwendungsfall: automatisches Aktualisieren von Workspace-Git-Folders, um den Code aktuell zu halten (siehe [04 CI-CD und Automatisierung.md](04%20CI-CD%20und%20Automatisierung.md)).

## <a id="provider">4. Git-Provider</a>

Git-Provider existieren in zwei Formen: Cloud-gehostete Dienste (vom Anbieter verwaltet) oder On-Premises-Installationen (intern von der Organisation verwaltet). Viele Provider bieten beide Bereitstellungsformen an.

**Unterstützte Cloud-Provider:** GitHub (inkl. GitHub Advanced Enterprise und GitHub Enterprise Cloud), Atlassian Bitbucket Cloud, GitLab und GitLab Enterprise Edition, Microsoft Azure DevOps (Azure Repos), AWS CodeCommit.

**Unterstützte On-Premises-Provider:** GitHub Enterprise Server, Atlassian Bitbucket Server und Data Center, GitLab Self-Managed, Microsoft Azure DevOps Server (erfordert Admin-Allowlisting für nicht-standardmäßige URLs).

**Wichtiger Hinweis:** „Organisationen hosten selbstverwaltete Provider oft hinter einem VPN, was sie vom öffentlichen Internet aus unzugänglich machen kann." Für On-Premises-Repositories, die Internetzugriff benötigen, muss ein Proxy für Git-Authentifizierungsanfragen innerhalb der VPN-Infrastruktur deployt werden (siehe [05 Administration und private Netzwerke.md](05%20Administration%20und%20private%20Netzwerke.md)).

## <a id="asset-typen">5. Unterstützte Asset-Typen</a>

- **Files:** „Serialisierte Daten wie Bibliotheken, Binärdateien, Code oder Bilder."
- **Notebooks:** erkannt an `.ipynb`-Endung oder speziellen Markern wie `# Databricks notebook source` in `.py`-Dateien — werden nicht wie andere Dateitypen serialisiert.
- **Folders:** logische Gruppierungen, die im Workspace und in der CLI als Ordner erscheinen.
- **Queries** (Public Preview): gespeichert als `.dbquery.ipynb`-Dateien, erfordert den neuen SQL-Editor. Queries aus dem Legacy-SQL-Editor können nicht committet werden.
- **Dashboards** (Public Preview): AI/BI-Dashboard-Entwürfe im `.lvdash.json`-Format. Publishing- und Zeitplan-Konfigurationen werden nicht nachverfolgt.
- **Alerts** (Public Preview): gespeichert als `.dbalert.json`-Dateien. Alert-Zeitpläne werden nachverfolgt, aber geklonte Alerts starten pausiert und müssen manuell fortgesetzt werden.

## <a id="namensregeln">6. Namensregeln</a>

- **Eindeutige Notebook-Namen:** „Ein Ordner kann kein Notebook mit demselben Namen wie ein anderes Notebook, eine Datei oder einen Ordner enthalten, selbst bei unterschiedlichen Endungen."
- **Keine Schrägstriche:** Dateinamen dürfen kein `/`-Zeichen enthalten.
- **Maximale Länge:** einzelne Datei-/Ordnernamen dürfen 255 Byte nicht überschreiten.

## <a id="nicht-unterstuetzt">7. Nicht unterstützte Asset-Typen</a>

Legacy Alerts, MLflow-Experimente, Genie Agents. Nicht unterstützte Assets lassen sich zwar in Git Folders verschieben, ihre Änderungen können aber nicht ins Remote-Repository committet werden.

## <a id="quelle">8. Quelle</a>

- https://docs.databricks.com/aws/en/repos/
- https://docs.databricks.com/aws/en/repos/git-folders-concepts
- https://docs.databricks.com/aws/en/repos/supported-artifact-types

**Stand:** 2026-08-21.
