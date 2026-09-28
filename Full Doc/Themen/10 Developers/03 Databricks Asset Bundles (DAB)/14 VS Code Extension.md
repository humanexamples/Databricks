# VS Code Extension

Die Databricks IDE Extension für Visual Studio Code (und Cursor) verbindet eine lokale Entwicklungsumgebung mit einem Databricks-Workspace, inklusive einer eigenen Integration für Declarative Automation Bundles (früher Databricks Asset Bundles). Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Voraussetzungen](#voraussetzungen)
3. [Authentifizierung](#authentifizierung)
4. [Kern-Features der Extension](#kern-features)
5. [Bundles in der Extension](#bundles-feature)
6. [Praktischer Ablauf: Workspace-URL und PAT ermitteln](#praktischer-ablauf)
7. [Abweichungen vom Kursmaterial](#abweichungen)
8. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick</a>

Die offizielle Bezeichnung laut Doku lautet **„Databricks IDE extension"** (auch als „Databricks extension for Visual Studio Code and Cursor" bezeichnet). Sie ermöglicht lokale Entwicklung mit Remote-Ausführung auf Databricks: Python-Dateien auf einem Cluster oder Serverless Compute ausführen, Notebooks als Jobs im Remote-Workspace ausführen (Python, R, Scala und SQL werden als Job-Format unterstützt — „the extension supports running R, Scala, and SQL notebooks as automated jobs but does not provide any deeper support for these languages within Visual Studio Code"), interaktives Debugging über Databricks-Connect-Integration mit zellenweisem Notebook-Debugging, Code-Synchronisation zwischen lokalem Projekt und Remote-Workspace, sowie das Deployen von Declarative Automation Bundles über die VS-Code-UI.

Zusätzlich enthält die Extension einen Workspace-File-System-Viewer und einen Unity-Catalog-Explorer für den Umgang mit Daten-Assets direkt in VS Code.

## <a id="voraussetzungen">2. Voraussetzungen</a>

- Visual Studio Code Version **1.86.0 oder höher**.
- VS Code muss für Python-Entwicklung konfiguriert sein, einschließlich eines verfügbaren Python-Interpreters.
- Mindestens ein Databricks-Workspace mit mindestens einem Databricks-Cluster.
- **Nicht unterstützt:** Databricks SQL Warehouses („Databricks SQL warehouses are not supported by this extension").

## <a id="authentifizierung">3. Authentifizierung</a>

Die Doku beschreibt drei Authentifizierungsmethoden:

1. **OAuth User-to-Machine (U2M)** — von Databricks empfohlene Methode, „easy to configure using the Databricks IDE extension", mit automatischem Token-Refresh. Ablauf über die Command Palette: **Select authentication method** → **OAuth (user to machine)**, dann **Login to Databricks**; anschließend browserbasierte Authentifizierung mit Zugriffsgewährung.
2. **Personal Access Token (PAT)** — von der Doku als **Legacy-Methode** eingeordnet, weiterhin unterstützt. Ablauf: in der Command Palette **Personal Access Token** wählen, das Token im Databricks-Workspace generieren und dessen Wert in die Extension eintragen.
3. **Service Principal OAuth** — für Machine-to-Machine-Autorisierung.

Nach der Authentifizierung legt die Extension eine Datei `.databricks/databricks.env` mit Workspace-Host und Konfigurationsdetails an und ergänzt automatisch entsprechende `.databricks/`-Einträge in `.gitignore`-Dateien.

## <a id="kern-features">4. Kern-Features der Extension</a>

Laut Doku stehen folgende Kernfunktionen zur Verfügung:

- **Declarative-Automation-Bundles deployen** über die VS-Code-UI, um CI/CD-Muster auf Jobs und Pipelines anzuwenden.
- **Python-Dateien ausführen** auf einem Databricks-Cluster oder auf Serverless Compute.
- **Notebooks als Jobs ausführen** im Remote-Workspace (Python, R, Scala, SQL als Format unterstützt).
- **Interaktives Debugging** über die Databricks-Connect-Integration mit zellenweisem Notebook-Debugging.
- **Code-Synchronisation** zwischen lokalem VS-Code-Projekt und Remote-Workspace.
- **Umgebungskonfiguration** über eine geführte Checkliste mit Auswahldialogen.
- **Workspace File System Viewer** und **Unity Catalog Explorer** als zusätzliche Werkzeuge.

## <a id="bundles-feature">5. Bundles in der Extension</a>

Die Unterseite zu Declarative Automation Bundles beschreibt folgende bundle-spezifische Funktionen:

- **Authentifizierung und Konfiguration:** „easy authentication and configuration of your Declarative Automation Bundles through the Visual Studio Code UI", inklusive Auswahl des Auth-Typ-Profils.
- **Target-Selector:** schneller Wechsel zwischen Bundle-Zielumgebungen (Targets).
- **Bundle Resource Explorer:** Ansicht der Bundle-Ressourcen direkt in der VS-Code-UI. Wörtliches Zitat: „A Bundles Resource Explorer view, which allows you to browse your bundle resources using the Visual Studio Code UI, deploy your local Databricks Asset Bundle's resources to your remote Databricks workspace with a single click." Von dort aus lässt sich direkt zu den deployten Ressourcen im Workspace navigieren.
- **Deploy- und Run-Icons:** dedizierte Symbole, um Bundles zu deployen und einzelne Ressourcen (z. B. Jobs oder Pipelines) auszuführen, ohne den Editor zu verlassen.
- **Pipeline-Validierung:** für Pipelines lässt sich eine Validierung und ein partielles Update auslösen; Diagnosen erscheinen im VS-Code-Problems-Panel.
- **Bundle Variables View:** eigenes Panel zum Durchsuchen, Bearbeiten und Überschreiben benutzerdefinierter Variablen aus den Bundle-Konfigurationsdateien.
- **Cluster-Override:** Option „Override Jobs cluster in bundle" für schnelle Cluster-Anpassungen.

## <a id="praktischer-ablauf">6. Praktischer Ablauf: Workspace-URL und PAT ermitteln</a>

**Nicht-Databricks-Quelle: privates Kursmaterial** (`Kursmetrial_Databricks/8_Automated Deployment with Declarative Automation Bundles/08_Using VSCode with Databricks/08 - Using VSCode with Databricks.md`). Der Kurs demonstriert den PAT-basierten Authentifizierungsweg (Abschnitt 3) anhand folgender Schritte:

1. **Workspace-URL ermitteln**, z. B. in einem Notebook über:

   ```python
   lab_databricks_url = f'{spark.conf.get("spark.databricks.workspaceUrl")}/'
   print(lab_databricks_url)
   ```

2. **PAT generieren:** im Workspace auf den Nutzernamen klicken → **User Settings** → **Developer** → neben **Access tokens** auf **Manage** → **Generate new token** → Scope **Other APIs** mit API-Scope **all APIs** (nur für Trainingszwecke geeignet; produktiv sollten Token-Berechtigungen nach den Governance-Richtlinien der eigenen Organisation eingeschränkt werden) → **Generate** → Token kopieren (wird nur einmal angezeigt).
3. **VS Code öffnen** und über die Command Palette mit Workspace-URL und PAT authentifizieren (siehe Abschnitt 3 für die aktuelle, von Databricks empfohlene Methode).

Nach erfolgreicher Authentifizierung lässt sich laut Kursmaterial `databricks.yml` mit Autocomplete und Schema-Validierung bearbeiten, und `databricks bundle validate`, `deploy`, `run` sowie `destroy` lassen sich direkt aus dem Editor ausführen (zu diesen konkreten Editor-Komfortfunktionen siehe die Einordnung in Abschnitt 7).

## <a id="abweichungen">7. Abweichungen vom Kursmaterial</a>

Bei der Verifizierung gegen die aktuelle Live-Doku (`docs.databricks.com/aws/en/dev-tools/vscode-ext` und `.../vscode-ext/bundles`) zeigen sich zwei Abweichungen von der Kurs-Notiz:

- **Begriffe „syntax highlighting", „schema validation" und „autocomplete" für `databricks.yml`:** Diese vom Kurs genannten Editor-Komfortfunktionen tauchen auf den genannten Doku-Seiten nicht als explizite Begriffe auf. Die Doku beschreibt stattdessen konkret belegte Funktionen wie den Bundle Resource Explorer, den Target-Selector und das Single-Click-Deployment (siehe Abschnitt 5). Es ist plausibel, dass die Extension im Hintergrund YAML-Schema-Unterstützung für `databricks.yml` nutzt, dies wird auf den geprüften Seiten aber nicht wörtlich bestätigt.
- **PAT vs. OAuth U2M:** Der Kurs stellt die PAT-Erstellung als den zu vermittelnden Authentifizierungsweg dar. Die aktuelle Doku stuft PAT-Authentifizierung dagegen explizit als **Legacy-Methode** ein und empfiehlt stattdessen **OAuth User-to-Machine (U2M)** mit automatischem Token-Refresh (siehe Abschnitt 3). Der PAT-Weg funktioniert weiterhin, ist aber nicht mehr der von Databricks empfohlene Standardweg.

Die „One-Click"-Eigenschaft aus dem Kurs ist hingegen durch die Doku bestätigt — allerdings bezogen auf das Deployment im Bundle Resource Explorer („deploy ... with a single click"), nicht als allgemeines Merkmal der gesamten Extension.

## <a id="quellen">8. Quellen</a>

- https://docs.databricks.com/aws/en/dev-tools/vscode-ext
- https://docs.databricks.com/aws/en/dev-tools/vscode-ext/bundles
- https://docs.databricks.com/aws/en/dev-tools/vscode-ext/authentication
- https://docs.databricks.com/aws/en/dev-tools/vscode-ext/install
- Nicht-Databricks-Quelle (privates Kursmaterial): `Kursmetrial_Databricks/8_Automated Deployment with Declarative Automation Bundles/08_Using VSCode with Databricks/08 - Using VSCode with Databricks.md`

**Stand:** 2026-08-21.
