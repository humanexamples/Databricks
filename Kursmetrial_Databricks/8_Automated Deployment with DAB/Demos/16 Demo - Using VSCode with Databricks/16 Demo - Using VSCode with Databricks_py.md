

```python
# Die URL Ihres Databricks-Workspace ermitteln
lab_databricks_url = f'{spark.conf.get("spark.databricks.workspaceUrl")}/'
print(lab_databricks_url)
```

## C. Ein Personal Access Token (PAT) generieren

Generieren Sie im Workspace ein PAT, damit sich VS Code authentifizieren kann.

1. Klicken Sie in der oberen Leiste auf Ihren Benutzernamen, klicken Sie im Dropdown mit der rechten Maustaste auf **User Settings** und wählen Sie **Open in a New Tab**.

2. Wählen Sie unter **Settings** die Option **Developer** und dann links neben **Access tokens** die Option **Manage**.

3. Klicken Sie auf **Generate new token**.

4. Setzen Sie **Scope** auf **Other APIs**.

5. Setzen Sie **API Scope** und aktivieren Sie **all APIs (not recommended)**.
 - Nur für Schulungszwecke. Befolgen Sie beim Festlegen von Token-Berechtigungen die Sicherheits- und Governance-Richtlinien Ihrer Organisation.

6. Klicken Sie auf **Generate**.

7. Kopieren Sie das angezeigte Token in die Zwischenablage. **Sie können das Token danach nicht erneut ansehen.** Wenn Sie es verlieren, müssen Sie es löschen und ein neues erstellen.

8. Fügen Sie das PAT in Ihrem Texteditor unterhalb der Workspace-URL ein.

**Referenz:** Personal Access Tokens (PATs):
[AWS](https://docs.databricks.com/aws/en/dev-tools/auth/pat) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/pat) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/auth/pat)

**
 Probleme beim Kopieren im Vocareum-Lab
 **

- Wenn die Zwischenablage-Schaltfläche der Lab-Umgebung Probleme macht, markieren Sie das PAT und kopieren Sie es manuell. Bestätigen Sie, dass das Kopieren erfolgreich war, bevor Sie den Dialog schließen.

- Für Schulungszwecke erlauben wir dem Token vorübergehend den Zugriff auf alle APIs. Für die Produktion wird dies in der Regel **nicht** empfohlen. Befolgen Sie beim Festlegen von Token-Berechtigungen die Sicherheits- und Governance-Richtlinien Ihrer Organisation.

## D. Die VS-Code-Lab-Umgebung öffnen

1. Öffnen Sie VS Code in Ihrer Lab-Umgebung:

 - Wählen Sie im Vocareum-iframe **Lab > vscode**.

 - Öffnen Sie den Link bei Bedarf in einem neuen Browser-Tab.

 - Ein neuer Tab mit VS Code sollte sich öffnen.

2. Öffnen Sie in VS Code die bereitgestellte Markdown-Datei und folgen Sie den Anweisungen.

![VSCode Access](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/demo_vscode/selectvscode.png)

## Fazit

Sie haben VS Code nun mit Ihrer Workspace-URL und einem Personal Access Token mit dem Databricks-Workspace verbunden. Ab hier können Sie mit der **Databricks-Erweiterung für VS Code**:

- **databricks.yml** mit Autovervollständigung und Schemavalidierung bearbeiten.
- `databricks bundle validate`, `deploy`, `run` und `destroy` direkt aus dem Editor ausführen.
- Lokalen Code für schnelle Iterationen mit dem Workspace synchronisieren.

Den vollständigen Funktionsüberblick finden Sie in der Dokumentation **Databricks extension for VS Code**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/vscode-ext) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/vscode-ext) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/vscode-ext).

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
