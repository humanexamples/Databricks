

Vorlesung – Lokal entwickeln mit Visual Studio Code (VS Code)

kurze Einführung in die Entwicklerwerkzeuge, mit denen Sie lokal aus VS Code mit Databricks arbeiten können: die Databricks CLI, Databricks Connect V2 und die Databricks VS Code Extension.

### A1. Überblick über die Entwicklerwerkzeuge

Drei Werkzeuge bringen Databricks aus VS Code in die lokale Entwicklung. Jedes eignet sich für eine andere Art von Arbeit.

**Databricks CLI**
- Ideal für **Shell-Scripting** und leichtgewichtige Kommandozeilenaufgaben
- Nützlich in Entwicklungs- und CI/CD-Prozessen
- Unterstützt vereinheitlichte Authentifizierung (OAuth, PATs usw.)
- Interaktiveres Debugging im Vergleich zu Notebooks

**Databricks Connect V2**
- Führt Apache-Spark-Code **remote** auf einem Databricks-Cluster aus einer lokalen Umgebung aus
- Ideal für interaktives Debugging und Remote-Ausführung von Spark-Jobs
- Einfaches Setup mit `pip install databricks-connect>=` Ihre Version

**Databricks VS Code Extension**
- Integriert Databricks in VS Code für Batch- und interaktive Entwicklung
- Vereinfacht das Setup mit Resource Explorern und der Databricks CLI
- Unterstützt das Ausführen und Debuggen von Python-Dateien auf Databricks-Clustern
- Hält Entwickler innerhalb von VS Code und bietet **DAB-Funktionen**

> **Zusätzliche Notizen:**
>
> - Für viele Entwickler ist eine IDE wie VS Code die bevorzugte Wahl – Sie können auf mehrere Weisen mit Databricks interagieren, während Sie in der IDE bleiben, und vermeiden einen Wechsel zur Databricks-Browser-UI.
> - Die **Databricks CLI** erlaubt schnelle Interaktionen über die Kommandozeile. Sie ist ideal für Shell-Scripting und leichtgewichtige Kommandozeilenaufgaben, nützlich in Entwicklungs- und CI/CD-Prozessen, unterstützt vereinheitlichte Authentifizierung (OAuth, PATs usw.) und bietet interaktiveres Debugging im Vergleich zu Notebooks.
> - **Databricks Connect V2** führt Apache-Spark-Code remote auf einem Databricks-Cluster aus einer lokalen Umgebung aus. Es ist ideal für interaktives Debugging und Remote-Ausführung von Spark-Jobs, mit einfachem Setup: `pip install databricks-connect>=<your version>`.
> - Die **Databricks VS Code Extension** integriert Databricks in VS Code für Batch- und interaktive Entwicklung, vereinfacht das Setup mit Resource Explorern und der Databricks CLI, unterstützt das Ausführen und Debuggen von Python-Dateien auf Clustern und hält Entwickler innerhalb von VS Code, während sie DAB-Funktionen bietet.

### A2. Die Databricks-Erweiterung für VS Code

- **Einfaches Setup** – Finden Sie uns im VS Code Marketplace und verbinden Sie sich in Minuten mit Compute.
- **Native Erfahrung** – Schreiben Sie Code mit den Produktivitätsfunktionen, die Sie an VS Code lieben.
- **Auf Databricks ausführen** – Führen Sie Batch-Workloads aus oder starten Sie interaktives Debugging direkt aus Ihrer IDE.

![Bild](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/lecture_vscode/vscode-extension-demo.gif)

> **Zusätzliche Notizen:**
>
> - Die VS Code Extension hat ein einfaches Setup aus dem VS Code Marketplace und verbindet Sie in Minuten mit Compute.
> - Sie bietet eine native Erfahrung für Entwickler, die VS Code bevorzugen, und lässt Sie Code mit den Produktivitätsfunktionen schreiben, die Sie bereits verwenden.
> - Sie können Code direkt aus Ihrer IDE auf Databricks ausführen – Batch-Workloads ausführen oder interaktives Debugging starten.

## B. Fazit

- Drei Werkzeuge bringen Databricks in die lokale Entwicklung: die **CLI** (Scripting, CI/CD), **Databricks Connect V2** (Remote-Spark, Debugging) und die **VS Code Extension** (vollständige IDE-Integration mit DAB-Funktionen).
- Zusammen lassen sie Sie Bundles von Ihrer eigenen Maschine bauen, debuggen und deployen.
