# 15 Lab – Versionskontrolle mit Databricks Git Folders und GitHub

Dieses Lab erfordert ein PERSÖNLICHES GitHub-Konto. Absolvieren Sie dieses Lab, wenn Sie die Nutzung von GitHub und Databricks üben möchten. Es behandelt die Grundlagen der Arbeit mit Databricks und GitHub und bietet eine einfache Einführung in Git Folders und GitHub.

## Überblick
Git ist ein Open-Source-Framework, aber wir nutzen einen Git-Provider namens [GitHub](https://github.com/). Dort wird Ihre Codebasis für die Entwicklung gehostet, der:
- Git-Repos hostet
- Einen Mechanismus zur Zugriffssteuerung bereitstellt
- Werkzeuge für Merge Requests bereitstellt
- Werkzeuge und Funktionen für CI/CD-Pipeline-Tests bereitstellt ([GitHub Actions](https://docs.databricks.com/en/dev-tools/bundles/ci-cd-bundles.html))


### Lernziele
Am Ende dieses Labs können Sie:
- Ihr GitHub-Konto über einen Personal Access Token (PAT) mit Databricks Git Folders verbinden.
- Grundlegende Git-Operationen wie Push, Commit, Pull in Databricks und Merge innerhalb von GitHub durchführen.

**HINWEIS:** Dieser Kurs behandelt GitHub Actions nicht. Weiterführende Informationen zu diesem Thema finden Sie über den oben angegebenen Link.

---

## A. Ein GitHub-Konto erstellen
Wenn Sie bereits ein **nicht arbeitsbezogenes GitHub-Konto** haben, melden Sie sich bitte an.

Andernfalls müssen Sie den [hier](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github) bereitgestellten Anweisungen folgen, um Ihr eigenes persönliches GitHub-Konto zu erstellen.

### 🚨 Verwenden Sie kein arbeitsbezogenes GitHub-Konto 🚨

---

## B. Ein GitHub-Repository erstellen
Um ein GitHub-Repository (Repo) zu erstellen, folgen Sie den [hier](https://docs.github.com/en/repositories/creating-and-managing-repositories/quickstart-for-repositories#create-a-repository) beschriebenen Schritten.

Stellen Sie beim Erstellen Ihres GitHub-Repos sicher, dass Folgendes festgelegt ist:

1. Benennen Sie das Repo **databricks_devops**.

2. Fügen Sie keine **README**-Datei hinzu.

3. Fügen Sie keine **gitignore**-Datei hinzu.

4. Fügen Sie keine Lizenz hinzu.

5. Nachdem Sie ein GitHub-Repo erstellt haben, erhalten Sie einen Hinweis, der wie folgt aussieht: ![GitHub](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/05_github_new_repo.png)

6. Wählen Sie **HTTPS** und lassen Sie die Seite offen. Sie benötigen den HTTP-Link, um Ihren Git Folder in Databricks zu erstellen.

---

## C. GitHub mit Databricks einrichten

Hier integrieren wir das gerade auf GitHub erstellte GitHub-Repository mit Databricks unter Verwendung von Databricks Git Folders.

---

### C1. Über einen Personal Access Token (PAT) mit einem GitHub-Repo verbinden

Für diese Demonstration funktioniert jeder der folgenden Ansätze.

---

#### Option 1 (empfohlen): Konfiguration mit Fine-grained PAT

Für feingranularen Zugriff sollten Sie sich mit einem Fine-grained PAT mit dem Repository verbinden. Details finden Sie unter [Connect to a GitHub repo using a fine-grained personal access token](https://docs.databricks.com/en/repos/get-access-tokens-from-git-provider.html#connect-to-a-github-repo-using-a-fine-grained-personal-access-token).

Hier ist eine Tabelle, die die Berechtigungen und Zugriffsebenen zusammenfasst, die Sie beim Konfigurieren Ihres Fine-grained PAT benötigen.
| Berechtigung   | Zugriffsebene   |
|---------------|----------------|
| Administration | Read and Write |
| Contents      | Read and Write |
| Pull Requests | Read and Write |
| Webhooks      | Read and Write |

Beachten Sie, dass Metadata als zwingende Konfiguration automatisch auf schreibgeschützt gesetzt wird.

**HINWEIS:** Wählen Sie ein benutzerdefiniertes Ablaufdatum von morgen, da Sie das Databricks-Academy-Lab verwenden. Der PAT wird jedoch entfernt, wenn das Lab geschlossen wird.

---

#### Option 2: Legacy-PAT-Konfiguration

Folgen Sie den in [Connect to a GitHub repo using a personal access token](https://docs.databricks.com/en/repos/get-access-tokens-from-git-provider.html#connect-to-a-github-repo-using-a-personal-access-token) beschriebenen Schritten, um sich über einen Personal Access Token (PAT) mit breitem Zugriff auf Ressourcen mit GitHub zu verbinden.

Hier ist eine Tabelle, die die Berechtigungen und Zugriffsebenen zusammenfasst, die Sie benötigen, falls Sie einen Legacy-PAT konfigurieren müssen.
| Berechtigung      | Zugriffsebene             |
|------------------|-------------------------|
| Repo            | Full control of private repositories |
| Workflow        | Lese- und Schreibzugriff auf Workflows |
| Admin:Repo_Hook | Manage repository hooks |
| Delete_Repo     | Delete repositories |

**HINWEIS:** Wählen Sie ein benutzerdefiniertes Ablaufdatum von morgen, da Sie das Databricks-Academy-Lab verwenden. Der PAT wird jedoch entfernt, wenn das Lab geschlossen wird.

---

### C2. Einen Git Folder in Databricks erstellen

Als Nächstes verbinden wir uns mit dem GitHub-Repo, das Sie in einem vorherigen Abschnitt erstellt haben.

Git Folders in Databricks (früher als Repos bekannt) werden für die Versionskontrolle verwendet und sind in Ihrem Databricks-Workspace standardmäßig aktiviert. Nach dem Einrichten eines Git Folders können Sie gängige Git-Operationen wie clone, checkout, commit, push, pull und das Verwalten von Branches direkt über die Databricks-UI durchführen.

Führen Sie Folgendes aus:

1. Navigieren Sie in Ihrem GitHub-Konto zu dem zuvor erstellten Repository und kopieren Sie die HTTPS-Adresse. Sie sollte so aussehen: `https://github.com/<github_username>/<repo_name>.git`.

2. Gehen Sie in Databricks in einem neuen Tab zu **Workspace**, klicken Sie auf **Users** und finden Sie Ihren Benutzernamen für diesen Kurs.

3. Klicken Sie oben rechts auf die blaue Schaltfläche **Create**.

4. Wählen Sie **Git folder** aus dem Dropdown.

5. Fügen Sie die kopierte URL in das Textfeld unter **Git repository URL** ein.

6. Klicken Sie unten auf die blaue Schaltfläche mit der Aufschrift **Create Git folder**.

7. Wählen Sie im Workspace Ihren Ordner **databricks_devops** aus.

8. Rechts neben Ihrem Ordnernamen sollte der **main**-Branch aufgeführt sein.


**Git Folder**

![Git Folder](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/05_devops_db_git_folder.png)

---

## D. Ihr erster Push und Commit

Fügen wir eine Datei zu Ihrem **Databricks Git Folder** innerhalb des Databricks-Workspace hinzu und pushen und committen dann die Änderungen zu GitHub.

1. Navigieren Sie in Databricks zu Ihrem **Git Folder in Ihrem Workspace** und erstellen Sie in diesem Ordner eine Datei namens **README.md**.

2. Fügen Sie der Datei **README.md** den folgenden Text hinzu:
    ```
    # Databricks DevOps Training
    My first push and commit.
    ```

3. Oben in der Datei, neben dem Dateinamen **README.md**, sehen Sie den Namen Ihres Repo-Branches, **main**.

4. Wählen Sie den **main**-Branch (Ihren einzigen Branch). Sie sollten Folgendes sehen:

![Änderungen](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/05_first_push.png)

**HINWEIS:** Auf dieser Seite sehen Sie den Branch, an dem Sie arbeiten, welche Änderungen vorgenommen wurden, Einstellungen, und Sie haben die Möglichkeit, Änderungen an Ihr GitHub-Repo zu committen und zu pushen.

5. Wir möchten die neue Datei **README.md**, die wir im Databricks Git Folder erstellt haben, committen und pushen. Geben Sie eine Commit-Nachricht ein (z. B. „First commit“) und klicken Sie auf **Commit & Push**.

6. Sobald Sie eine Bestätigungsmeldung erhalten, dass Commit und Push erfolgreich waren, schließen Sie das Git-Pop-up.

7. Gehen Sie zu Ihrem GitHub-Repo und aktualisieren Sie die Seite.

8. Wählen Sie oben den Reiter **Code** (falls Sie nicht bereits dort sind). Hier finden Sie Ihre neu hochgeladene Datei zusammen mit der Commit-Nachricht.

---

#### D1. Einen neuen Branch erstellen

Erstellen wir einen **dev**-Branch innerhalb des **Databricks Git Folder**, um ein neues Feature zu entwickeln, und zeigen wir, wie sich ein Pull Request in GitHub in unserem Git Folder widerspiegelt.

Führen Sie Folgendes aus:

1. Wählen Sie im Databricks-Workspace den **main**-Branch Ihres Ordners aus. Klicken Sie im Databricks-Git-Folder-Pop-up auf **Create Branch**, benennen Sie den Branch **dev** und klicken Sie dann auf **Create**.

2. Schließen Sie das Databricks-Git-Folder-Pop-up.

3. Sie sollten sich jetzt im **dev**-Branch befinden.

**HINWEIS:** Stellen Sie sicher, dass **dev** standardmäßig ausgewählt ist, da wir zuerst in diesen Branch committen. Zu diesem Zeitpunkt sind die Branches **dev** und **main** identisch.

---

#### D2. Ein Feature zum Dev-Branch hinzufügen

Tun wir so, als würden wir ein neues Feature in unserem **dev**-Branch erstellen.

Führen Sie Folgendes aus:

1. Gehen Sie zu Ihrem Git Folder im Databricks-Workspace und stellen Sie sicher, dass der **dev**-Branch ausgewählt ist.

2. Erstellen Sie im **dev**-Branch ein Notebook und benennen Sie es **new_feature**. Fügen Sie in der ersten Zelle eine einfache Python-Anweisung hinzu: `print('hello world')`.

3. Wählen Sie oben neben dem Notebook-Namen in Ihrem Databricks-Workspace den **dev**-Branch aus.

4. Sie sollten nun sehen, dass eine Datei geändert wurde. Fügen Sie die Commit-Nachricht *update feature* hinzu und klicken Sie auf **Commit & Push**.

5. Der Push sollte erfolgreich zu Ihrem GitHub-Repo abgeschlossen werden. Schließen Sie das GitHub-Pop-up in Databricks.

6. Gehen Sie zu GitHub und stellen Sie sicher, dass Sie sich im **main**-Branch befinden. Sie sollten feststellen, dass Ihr neues Feature noch nicht im **main**-Branch ist.

7. Wechseln Sie in GitHub zum **dev**-Branch (Standard ist **main**). Aktualisieren Sie die Seite bei Bedarf. Das neue Notebook, **new_feature.ipynb**, sollte in Ihrem GitHub-Repo erscheinen.

8. Lassen Sie GitHub offen.

---

## E. Einen neuen Pull Request erstellen

Ein Pull Request ist ein Vorschlag, eine Reihe von Änderungen von einem Branch in einen anderen zu mergen. In einem Pull Request können Mitarbeitende die vorgeschlagenen Änderungen überprüfen und diskutieren, bevor sie in die Haupt-Codebasis integriert werden.

---

1. Führen Sie die folgenden Schritte aus, um einen Pull Request in den **main**-Branch durchzuführen:

   a. Wählen Sie in GitHub in der oberen Navigationsleiste den Reiter **Pull requests**.

   b. Klicken Sie auf **New pull request**.

   c. Sie sehen zwei Dropdown-Menüs. Wählen Sie in den Dropdowns **base** und **compare** Folgendes:
      - Ändern Sie das erste Dropdown links auf **main** (dies ist die Basis),
      - Wählen Sie rechts **dev** (**compare**) als den Branch, mit dem **main** verglichen werden soll.

   d. Scrollen Sie nach unten und beachten Sie die Aktualisierungen in **dev**, die nicht in **main** sind (dazu gehört das neue Notebook, das Sie erstellt haben).

   e. Klicken Sie auf **Create pull request**.

   f. Im Abschnitt **Open a pull request** haben Sie mehrere Optionen. Sie können einen Titel und eine Beschreibung für den Pull Request hinzufügen. Rechts können Sie **Reviewers**, **Assignees**, **Labels** und mehr angeben.

   g. Füllen Sie einen Titel und eine Beschreibung aus und klicken Sie dann auf **Create pull request**.

   h. Lassen Sie die GitHub-Seite offen.

---

2. Führen Sie als Nächstes die folgenden Schritte aus, um den Pull Request zu mergen. Alle Commits aus dem **dev**-Branch werden dem **main**-Branch hinzugefügt.

   a. Auf dem nächsten Bildschirm sehen Sie nach einigen Momenten in der Mitte Ihres Bildschirms eine Meldung mit der Aufschrift **This branch has no conflicts with the base branch** mit einem grünen Häkchen.

   b. Sie können dem Pull Request einen Kommentar hinzufügen.

   c. Mergen Sie den **dev**-Branch in **main**, indem Sie **Merge pull request** auswählen. Wählen Sie dann **Confirm merge**. Ein Hinweis mit der Aufschrift **Pull request successfully merged and closed** sollte erscheinen. Sie können den **dev**-Branch löschen, wenn Sie möchten, wir behalten ihn jedoch.

   d. Navigieren Sie in GitHub in der oberen Navigationsleiste zu **Code** und stellen Sie sicher, dass Sie sich im **main**-Branch befinden. Bestätigen Sie, dass die Datei **new_feature.ipynb** jetzt im **main**-Branch ist und dass die beiden Branches synchron sind.

---

## F. Pull innerhalb von Databricks
Als letzten Schritt pullen wir die GitHub-Änderungen in unseren lokalen Workspace.

1. Gehen Sie zu **Workspace** und navigieren Sie zum Speicherort Ihres Git Folders.

2. Wählen Sie den **main**-Branch in Ihrem Git Folder aus, um das Git-Folder-Pop-up zu öffnen.

3. Klicken Sie oben rechts im Pop-up auf **Pull**, um die neuesten Änderungen in Ihren Workspace zu pullen.

4. Schließen Sie das Git-Folder-Pop-up und beachten Sie, dass die neue Datei jetzt im **main**-Branch Ihres Workspace ist.

---

## G. Ihren PAT löschen
Am Ende dieses Labs sollten Sie den PAT, den Sie in diesem Lab erstellt haben, aus Ihrem GitHub-Konto löschen.

Wenn dieses Lab jedoch endet, wird dieses Vocareum-Lab-Konto geleert.

---

# Nächste Schritte (fortgeschrittene Bereitstellung)

Der nächste Schritt auf Ihrer DevOps-Reise ist die Umsetzung von [GitHub Actions mit DABs](https://docs.databricks.com/en/dev-tools/bundles/ci-cd-bundles.html). GitHub Actions können für Continuous Integration und Delivery verwendet werden und sind jetzt in Public Preview. Eine Liste Databricks-spezifischer GitHub Actions wie databricks/run-notebook finden Sie in der Dokumentation [hier](https://docs.databricks.com/aws/en/dev-tools/ci-cd/). Ziel von GitHub Actions im Allgemeinen ist es, CI/CD-Workflows zu automatisieren, indem vorkonfigurierte Aktionen automatisch als Reaktion auf etwas ausgelöst werden, das in oder an Ihrem GitHub-Repo geschieht – ein sogenanntes **Event**. Eine vollständige Liste der GitHub-Event-Typen finden Sie in [dieser](https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28) Dokumentation.

---

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
