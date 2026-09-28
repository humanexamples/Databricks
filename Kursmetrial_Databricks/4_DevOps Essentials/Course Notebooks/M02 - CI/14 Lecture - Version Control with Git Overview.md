Git-Versionskontrolle ist wichtig, weil sie eine strukturierte Möglichkeit bietet, Codeänderungen in Softwareprojekten zu verwalten, zu verfolgen und gemeinsam daran zu arbeiten. 

## Sichere Codeänderungen durch Branching

- Ergänzendes Konzept zu CI/CD → Ermöglicht effektive CI
- Änderungen versionieren und vor dem Merge in den Main-Branch und der Bereitstellung durch die Qualitätskontrolle laufen lassen
- Beispiel: Gitflow

![Sichere Codeänderungen durch Branching](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_version_control/gitflow_example.png)

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> Dies ist ein Beispiel für Versionskontrolle und Codeverwaltung über die Zeit mit Gitflow, einer gängigen Branching-Strategie, die Branches für Features, Releases und Hotfixes organisiert.
>
> Ausgehend von der ersten Version v0.1 im Main-Branch erfolgt das Branching in den Feature-Branch, wo Tests isoliert ordnungsgemäß durchgeführt werden können.
>
> Nachdem wir nun wissen, wie kompliziert Versionskontrolle sein kann, und ein Beispiel dafür gesehen haben, wie das Absichern von Codeänderungen aussieht, sehen wir uns an, wie Git mit Databricks verwendet werden kann.

---

## C. Überblick über Git mit Databricks

> Git ist ein kostenloses und quelloffenes Software-Framework, das entwickelt wurde, um Änderungen am Quellcode während der Softwareentwicklung zu verfolgen.

### Gängige Git-Werkzeuge und Git-basierte Dienste

![Gängige Git-Werkzeuge und Git-basierte Dienste](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_version_control/tools_git-based_services.png)

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN



> **Git-Werkzeuge & -Dienste:**
>
> - GitHub, GitLab, Bitbucket, Azure DevOps – Cloud-basierte Repositories mit CI/CD, Issue-Tracking und Teamzusammenarbeit.
>- Git-CLI & -GUI-Clients (z. B. SourceTree, GitKraken, VS Code Git-Integration) – Bieten unterschiedliche Oberflächen zum Verwalten von Repositories.
> - CI/CD-Integration – Automatisierte Test- und Bereitstellungspipelines.
>- Code-Review & Zusammenarbeit – Funktionen wie Pull Requests und Merge-Freigaben straffen die Teamarbeit.
> - Sicherheit & Zugriffssteuerung – Rollenbasierte Berechtigungen und Audit-Logs erhöhen die Sicherheit des Repositories.
> 
> **Visueller Git-Client** – Databricks bietet eine benutzerfreundliche Oberfläche für gängige Git-Operationen, die wir auf der nächsten Folie besprechen.
> 
> **Nahtlose Integration** – Nutzende können entfernte Git-Repos verwenden, während sie Code innerhalb von Databricks-Notebooks entwickeln.
>
> **CI/CD-Fähigkeiten** – Die Repos-REST-API ermöglicht die Integration von Daten- und KI-Projekten in CI/CD-Pipelines und erlaubt Nutzenden, Git-Lakeflow-Jobs zu automatisieren.

---

## D. Ein GitHub Personal Access Token (PAT) erzeugen

Um einen **Personal Access Token (PAT) in GitHub** zu erzeugen, gehen Sie zu **Settings → Developer settings**, wählen Sie entweder **Fine-grained- oder Classic-Token** und klicken Sie auf Generate new token. Konfigurieren Sie die erforderlichen Repository-Berechtigungen, kopieren Sie den Token und verwenden Sie ihn in Databricks für die Integration.

---

## E. Verbindung mit Databricks über einen GitHub PAT

1. **Profilmenü** – Öffnen Sie das Databricks-Benutzerprofilmenü.
2. **Settings** – Wählen Sie **Settings** aus dem Profilmenü.
3. **Developer** – Wählen Sie in Settings **Developer**.
4. **Token** – Verwenden Sie den GitHub-**Token**, um Databricks mit GitHub zu verbinden.
5. **Linked Accounts** – Wählen Sie unter **Linked accounts** GitHub aus und geben Sie den Personal Access Token ein.

![Ablauf: Databricks mit GitHub PAT verbinden](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_version_control/seamless_integration.png)

## F. Databricks Git Folders

Ein **Databricks Git Folder** ist ein Ordner in Ihrem Workspace, der mit einem entfernten Git-Repository verknüpft ist. Er lässt Sie gängige Git-Operationen – klonen, committen, pushen, pullen und branchen – direkt über die Databricks-UI ausführen, ohne den Workspace zu verlassen.

### 1. Repo klonen

**Ein entferntes Repository klonen** – Erstellen Sie einen Git Folder, indem Sie die **HTTPS-URL** Ihres Repositories in den Dialog *Create Git folder* einfügen. Databricks erkennt den Provider automatisch und klont das Repo in Ihren Workspace.

Beispiel-Dialog *Create Git folder*:

- Git repository URL: `https://github.com/<your-username>/databricks_devops.git`
- Git provider: GitHub (automatisch erkannt)
- Schaltfläche: **Create Git folder**

### 2. Commit & Push

**Änderungen über die UI committen und pushen** – Stagen Sie Ihre Änderungen, schreiben Sie eine Commit-Nachricht und pushen Sie zum Remote – alles über die Databricks-UI, ohne Terminal.

- Branch: `main`
- Änderungen: `A README.md` (hinzugefügt)
- Commit-Nachricht: `First commit`
- Schaltfläche: **Commit & Push**

### 3. Aktualisierungen pullen

**Branch-Aktualisierungen pullen** – Pullen Sie die neuesten Commits vom entfernten Branch, damit Ihr Workspace mit den Änderungen des restlichen Teams synchron bleibt.

- Branch: `main`
- Status: 2 neue Commits auf `origin/main`
- Schaltfläche: **Pull**

### 4. Branches verwalten

**Branches verwalten** – Erstellen und wechseln Sie Branches direkt im Git Folder, um Feature-Arbeit von **main** zu isolieren – die Grundlage eines sicheren Branching-Workflows.

- Aktueller Branch: `main` ✓
- Weiterer Branch: `dev`
- Schaltfläche: **Create Branch**

### 5. Visuelle Validierung

**Visuelle Validierung beim Committen** – Überprüfen Sie vor dem Commit einen visuellen Diff dessen, was sich genau geändert hat, sodass Sie nur das pushen, was Sie beabsichtigen.

```diff
 # Databricks DevOps Training
- My first push.
+ My first push and commit.
+ Added project overview.
```

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> Databricks Git Folders straffen die Entwicklung, indem sie Versionskontrollsysteme eng in das Databricks-Ökosystem integrieren, wodurch es einfacher wird, Code gemeinsam zu verwalten und dabei Best Practices einzuhalten.
>
> Anwendungsfälle umfassen:
>
> - Gemeinsame Entwicklung von Machine-Learning-Modellen und ETL-Pipelines.
> - Versionierung von SQL-Abfragen für Analytics-Workloads.
> - Automatisierung von Bereitstellungen über CI/CD-Pipelines.
>
> Gehen Sie die obigen Reiter durch, um die zentralen Git-Folder-Operationen zu sehen: ein Repo klonen, indem Sie seine GitHub-URL in den Dialog **Create Git folder** einfügen, Änderungen über die UI committen und pushen, Aktualisierungen pullen, Branches verwalten und vor dem Commit einen visuellen Diff überprüfen.

---

## G. Git-basierte Repos in Databricks

![Repos-API zur Automatisierung von CI/CD](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_version_control/repos_API_automate_CI-CD.png)

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> 1. Aha!-Feature:
>
> DB-3749 W2.0: Projects API private preview with tag and commit based checkouts | Aha!
>
> 2. Beschreibung der Features:
>
> Die Repos-API bietet programmatischen Zugriff auf Git-basierte Repos, die Teil der Workspace-2.0-Initiative sind. Mit der API können Kunden Databricks Repos in ihren CI/CD-Workflow integrieren. Sie können Repos programmatisch erstellen/aktualisieren/löschen, Git-Operationen durchführen und Git-Versionen angeben, wenn sie Jobs auf Basis von Notebooks in Repos ausführen.
>
> 3. Wert des Features (also wie Databricks vor diesem Feature war und was dieses Feature für Databricks leistet)
>
> Derzeit haben viele Kunden Behelfslösungen mit der Databricks-CLI gebaut, um Notebooks aus Databricks zu ziehen, sie in Git einzuchecken, sie aus Git zu ziehen und sie zurück nach Databricks zu pushen. Das ist keine sehr robuste Lösung. Mit Repos und der Repos-API bieten wir ein natives Feature, um Code aus einem Git-Repository zu ziehen, Aktualisierungen zurück in Git einzuchecken und diese Repos programmatisch mit der Repos-API zu aktualisieren.
>
> 4. Zugehörige Stichpunkte der Zusammenfassungsfolie: Repos-API für CI/CD-Integration
>
> 5. Cloud: Alle
>
> 6. Deployment (MT, ST, Azure): GA

---

## H. Unterstützung beliebiger Dateien in Repos

- **Portabilität von Code** – Bibliotheksdateien: Python-/R-Dateien als Pakete verwenden.
- **Portabilität der Umgebungsspezifikation** – Pakete aus demselben Repo bauen.
- **Einfache Nutzung kleiner Daten** – Relative Importe.
- Alles, was Sie mit Dateien tun können, „funktioniert einfach“.

![Unterstützung beliebiger Dateien in Repos](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/lecture_version_control/arbitrary_files_support_in_repos.png)

Unterstützte Dateitypen: `.txt`, `.yml`, `.py`, `.csv`, …

---

##### FÜR ZUSÄTZLICHE NOTIZEN AUSKLAPPEN

> Beliebige Dateien werden in Repos unterstützt, was die Portabilität von Code für Bibliotheksdateien wie Python und R ermöglicht. Dadurch ist es möglich, Pakete aus demselben Repository zu bauen, relative Importe zu verwenden und Ihr Projekt so zu strukturieren, wie es Ihren Anforderungen am besten entspricht.

---

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
