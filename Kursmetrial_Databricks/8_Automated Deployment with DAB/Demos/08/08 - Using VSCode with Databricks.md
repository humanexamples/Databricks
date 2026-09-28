![DB Academy](../Includes/images/common/db-academy.png)

# [Video-Tutorial](https://customer-academy.databricks.com/learn/courses/3724/automated-deployment-with-declarative-automation-bundles/lessons/33997/demo-using-vscode-with-databricks)

# 08 Bonus - Verwendung von VS Code mit Databricks - Aktualisiert

## Überblick

Bis zu diesem Punkt haben Sie Bundles vollständig innerhalb des Databricks-Workspace erstellt und bereitgestellt. In der realen Produktionsarbeit erstellen die meisten Teams Bundles in **VS Code** mit der **Databricks-Extension**, die Ihnen Syntaxhervorhebung, Schemavalidierung, Autovervollständigung für **databricks.yml** sowie Bundle-Deploy/Run per Klick direkt aus dem Editor bietet.

Diese Bonus-Anleitung zeigt Ihnen, wie Sie VS Code gegenüber Ihrem Databricks-Workspace mithilfe der Workspace-URL und eines Personal Access Token (PAT) authentifizieren, damit Sie von der notebookbasierten Bundle-Arbeit zu einem lokalen Editor wechseln können.

## Lernziele

Am Ende dieser Demonstration werden Sie in der Lage sein:

1. **Die Databricks-Workspace-URL zu finden**, die die VS Code-Extension für die Authentifizierung benötigt.
2. **Ein Personal Access Token (PAT)** aus den Workspace-**Benutzereinstellungen** zu erstellen.
3. **Die VS Code-Lab-Umgebung zu öffnen** und sie mit der Workspace-URL und dem PAT zu authentifizieren.

## Referenzdokumentation

- **Databricks-Extension für VS Code**: [AWS](https://docs.databricks.com/aws/en/dev-tools/vscode-ext) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/vscode-ext) | [GCP](https://docs.databricks.com/gcp/en/dev-tools/vscode-ext)
- **DABs in der VS Code-Extension**: [AWS](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/bundles) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/vscode-ext/bundles) | [GCP](https://docs.databricks.com/gcp/en/dev-tools/vscode-ext/bundles)
- **Personal Access Tokens (PATs)**: [AWS](https://docs.databricks.com/aws/en/dev-tools/auth/pat) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/pat) | [GCP](https://docs.databricks.com/gcp/en/dev-tools/auth/pat)

## ERFORDERLICH - WÄHLEN SIE EINE COMPUTE-UMGEBUNG AUS

**Wählen Sie All-Purpose Compute**

Sie können **Serverless**-Compute oder Ihren **All-Purpose-Cluster** auswählen.

## A. Öffnen eines Texteditors

1. Öffnen Sie einen einfachen Texteditor auf Ihrem Computer.

2. Führen Sie die folgenden Schritte aus, um die folgenden Informationen in die Datei einzufügen, damit Sie sie später bei der Authentifizierung mit VS Code verwenden können:

   - Ihre Databricks-Workspace-URL

   - Ihr Personal Access Token (PAT)

## B. Abrufen Ihrer Databricks-Workspace-URL

1. Führen Sie die untenstehende Zelle aus, um Ihre Workspace-URL auszugeben. Lassen Sie die Ausgabe sichtbar. Sie fügen sie in Ihren Texteditor und erneut in VS Code ein.

```python
lab_databricks_url = f'{spark.conf.get("spark.databricks.workspaceUrl")}/'
print(lab_databricks_url)
```

## C. Erstellen eines Personal Access Token (PAT)

Erstellen Sie ein PAT im Workspace, damit VS Code sich authentifizieren kann.

1. Klicken Sie oben in der Leiste auf Ihren Benutzernamen, klicken Sie im Dropdown-Menü mit der rechten Maustaste auf **User Settings** und wählen Sie **Open in a New Tab**.

2. Wählen Sie in **Settings** die Option **Developer** und dann links neben **Access tokens** die Option **Manage**.

3. Klicken Sie auf **Generate new token**.

4. Setzen Sie **Scope** auf **Other APIs**.

5. Setzen Sie **API Scope** und aktivieren Sie **all APIs (not recommended)**.
   - Nur für Trainingszwecke. Befolgen Sie die Sicherheits- und Governance-Richtlinien Ihrer Organisation beim Festlegen von Token-Berechtigungen.

6. Klicken Sie auf **Generate**.

7. Kopieren Sie das angezeigte Token in die Zwischenablage. **Sie können das Token danach nicht mehr einsehen.** Wenn Sie es verlieren, müssen Sie es löschen und ein neues erstellen.

8. Fügen Sie das PAT unterhalb der Workspace-URL in Ihren Texteditor ein.

**Referenz:** Personal Access Tokens (PATs):
[AWS](https://docs.databricks.com/aws/en/dev-tools/auth/pat) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/pat) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/auth/pat)

**
Probleme beim Kopieren im Vocareum-Lab
**

- Falls die Kopieren-Schaltfläche der Lab-Umgebung Probleme verursacht, markieren Sie das PAT und kopieren Sie es manuell. Bestätigen Sie, dass das Kopieren erfolgreich war, bevor Sie den Dialog schließen.

- Zu Trainingszwecken aktivieren wir vorübergehend, dass das Token auf alle APIs zugreifen kann. Dies wird für die Produktion **nicht** empfohlen. Befolgen Sie die Sicherheits- und Governance-Richtlinien Ihrer Organisation beim Festlegen von Token-Berechtigungen.

## D. Öffnen der VS Code-Lab-Umgebung

1. Öffnen Sie VS Code in Ihrer Lab-Umgebung:

   - Wählen Sie im Vocareum-iframe **Lab > vscode**.

   - Öffnen Sie den Link bei Bedarf in einem neuen Browser-Tab.

   - Ein neuer Tab mit VS Code sollte sich öffnen.

2. Öffnen Sie in VS Code die bereitgestellte Markdown-Datei und folgen Sie den Anweisungen.

![VSCode Access](./images/selectvscode.png)

## Fazit

Sie haben nun VS Code mithilfe Ihrer Workspace-URL und eines Personal Access Token mit dem Databricks-Workspace verbunden. Von hier aus ermöglicht Ihnen die **Databricks-Extension für VS Code**:

- Bearbeiten von **databricks.yml** mit Autovervollständigung und Schemavalidierung.
- Ausführen von `databricks bundle validate`, `deploy`, `run` und `destroy` direkt aus dem Editor.
- Synchronisieren von lokalem Code mit dem Workspace für schnelle Iteration.

Die vollständige Feature-Tour finden Sie in der Dokumentation zur **Databricks-Extension für VS Code**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/vscode-ext) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/vscode-ext) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/vscode-ext).

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
