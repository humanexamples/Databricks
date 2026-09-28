In dieser Demonstration erstellen Sie einen einfachen Databricks-Job, untersuchen dessen YAML-Konfiguration und durchlaufen den vollständigen Lebenszyklus eines **Declarative Automation Bundle (DAB)**: validieren, bereitstellen, ausführen, ändern, erneut bereitstellen und zerstören. Alles läuft aus Gründen der Trainingsbequemlichkeit in einem Databricks-Notebook ab. 

Dieses Notebook erfordert **All-Purpose Compute** (Dedicated). Serverless wird für dieses Notebook nicht unterstützt.

**Job erstellen**

```python
job_tasks = [
    {
        'task_name': 'create_bronze_table',
        'notebook_path': '/01 - Deploying a Simple DAB/src/create_bronze_table',
        'depends_on': None
    },
    {
        'task_name': 'create_silver_table',
        'notebook_path': '/01 - Deploying a Simple DAB/src/create_silver_table',
        'depends_on': [{'task_key': 'create_bronze_table'}]
    }
]

myjob = DAJobConfig(job_name=f'demo1_simple_dab_{my_catalog}',
                    job_tasks=job_tasks,
                    job_parameters=[
                      {'name':'display_target', 'default':'development'},
                      {'name':'catalog_name', 'default':catalog_dev}
                    ])
```

### B2. Erkunden der Job-Konfigurationen
Führen Sie die folgenden Schritte aus, um die YAML-Konfiguration des Jobs zu erkunden:

1. Klicken Sie in der linken Hauptnavigationsleiste mit der rechten Maustaste auf **Jobs and Pipelines** und wählen Sie **Open in a new tab**.

2. Suchen Sie Ihren bereitgestellten Job mit dem Namen **demo1_simple_dab_LABUSER_UNIQUE_ID**.

3. Wählen Sie Ihren Job aus.

4. Scrollen Sie im rechten Bereich **Job details** nach unten und finden Sie **Job parameters**. Beachten Sie, dass für diesen Job zwei Parameter festgelegt wurden:
   | Job-Parameter | Beschreibung |
   |---|---|
   | `catalog_name` | Verweist auf Ihren **labuser_UNIQUE_ID**-Katalog. |
   | `display_target` | Textwert, der die Umgebung angibt, in der der Job ausgeführt wird. In diesem Beispiel verwenden wir `development`. |

5. Wählen Sie in der oberen Navigationsleiste **Tasks**. Beachten Sie, dass dieser Job zwei Tasks hat:
| Task | Beschreibung |
|---|---|
| **TASK 1** | - Führt das Notebook **create_bronze_table** aus; - Liest aus der Development-CSV-Datei im Katalog **labuser_UNIQUE_ID_dev**; - Verwendet den Job-Parameter `catalog_name`; - Erstellt die Tabelle **health_bronze_demo_1** |
| **TASK 2** | - Führt das Notebook **create_silver_table** aus; - Liest aus der Bronze-Tabelle im Katalog **labuser_UNIQUE_ID_dev**; - Verwendet den Job-Parameter `catalog_name`; - Erstellt die Tabelle **health_silver_demo_1**; - Hängt vom erfolgreichen Abschluss von **TASK 1** ab |

#### Kontrollpunkt - Beispiel-YAML-Konfiguration (Ihre Werte weichen geringfügig ab)
```yaml
resources:
  jobs:
    demo1_simple_dab_labuser123:
      name: demo1_simple_dab_labuser123
      tasks:
        - task_key: create_bronze_table
          notebook_task:
            notebook_path: /../create_bronze_table
            source: WORKSPACE
        - task_key: create_silver_table
          depends_on:
            - task_key: create_bronze_table
          notebook_task:
            notebook_path: /../create_silver_table
            source: WORKSPACE
      parameters:
        - name: display_target
          default: development
        - name: catalog_name
          default: labuser123_1_dev
```

## C. Bereitstellen Ihres Jobs mithilfe von Declarative Automation Bundles (DABs)

### C1. Ausführen von Databricks CLI-Befehlen

1. Führen Sie den Befehl `databricks -v` aus, um die Version der Databricks CLI anzuzeigen.

Bestätigen Sie, dass die Zelle die Version **v0.298.0** zurückgibt.

**CLI-Version**

```bash
%sh
databricks -v
```

**
FEHLERBEHEBUNG BEI DATABRICKS CLI-FEHLERN:
**

  - Wenn ein Databricks CLI-Authentifizierungsfehler auftritt, bedeutet dies, dass die Authentifizierung nicht erfolgreich war. Bestätigen Sie, dass Sie das Notebook mit Ihrem **All-Purpose Compute** ausgeführt haben.

  - Wenn der folgende Fehler auftritt, bedeutet dies, dass Ihre Datei **databricks.yml** aufgrund einer Änderung Syntaxprobleme aufweist. Auch für Nicht-DAB-CLI-Befehle wird die Datei **databricks.yml** weiterhin benötigt, da sie wichtige Authentifizierungsdetails wie Host und Profil enthalten kann, die von den CLI-Befehlen verwendet werden.

![CLI Invalid YAML](../Includes/images/databricks_cli_error_invalid_yaml.png)

2. Verwenden Sie den Befehl `pwd`, um das aktuelle Arbeitsverzeichnis anzuzeigen.

Es sollte anzeigen, dass Sie sich im Ordner **01 - Deploying a Simple DAB** befinden.
- Die CLI verwendet das aktuelle Verzeichnis dieses Notebooks.

**Aktueller Pfad**

```bash
%sh
pwd
```

3. Verwenden Sie den Befehl `ls`, um die verfügbaren Dateien im aktuellen Verzeichnis anzuzeigen.

Bestätigen Sie, dass Sie die Datei **databricks.yml** sehen.

**Dateien auflisten**

```bash
%sh
ls
```

**
Hinweise
**

Ein Bundle muss genau eine Konfigurationsdatei mit dem Namen **databricks.yml** im Stammverzeichnis des Bundle-Projektordners enthalten.

Die Datei **databricks.yml** ist die Hauptkonfigurationsdatei, die ein Bundle definiert, kann aber über die include-Zuordnung auf andere Konfigurationsdateien verweisen, etwa Ressourcen-Konfigurationsdateien.

Eine Bundle-Konfigurationsdatei muss im YAML-Format vorliegen und mindestens die oberste `bundle`-Zuordnung enthalten.

### C2. Erkunden der einfachen Bundle-Konfigurationsdatei **databricks.yml**

Nachdem wir bestätigt haben, dass wir uns im Arbeitsverzeichnis der Datei **databricks.yml** befinden, öffnen wir die Bundle-Konfigurationsdatei in einem neuen Tab und erkunden die Bundle-Konfiguration.

Die vollständige Liste der Bundle-Konfigurationsschlüssel finden Sie in der Dokumentation **Configuration reference**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/reference) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/reference) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/reference)

1. Wählen Sie in der linken Workspace-Navigation das Ordnersymbol aus und bestätigen Sie, dass Sie sich im Ordner **01 - Deploying a Simple DAB** befinden.

2. Klicken Sie mit der rechten Maustaste auf die Datei **databricks.yml** und wählen Sie *Open in a new tab*.

3. In der Datei **databricks.yml** darf eine Konfiguration nur eine oberste `bundle`-Zuordnung enthalten.
- Diese `bundle`-Zuordnung muss eine `name`-Zuordnung enthalten, die einen programmatischen (oder logischen) Namen für das Bundle angibt.
```
        bundle:                   # Erforderlich
          name: demo01_bundle     # Erforderlich
```

4. Die `resources`-Zuordnung (beachten Sie, dass diese im YAML leer ist) gibt Folgendes an:
- Informationen über die vom Bundle verwendeten Databricks-Ressourcen.
- Diese Bundle-Konfiguration definiert eine Job-Ressource. Wir fügen unseren spezifischen Job im nächsten Abschnitt hinzu und überprüfen die Konfiguration.

5. Die `targets`-Zuordnung gibt Folgendes an:
- Eine oder mehrere Zielumgebungen, in denen ein Databricks-Workflow ausgeführt wird.
- Jedes Target ist eine eindeutige Sammlung von Artefakten, Databricks-Workspace-Einstellungen sowie Databricks-Job- oder -Pipeline-Details.
- In diesem Beispiel haben wir ein Target namens `development`, das eine einfache Konfiguration verwendet.

6. Die Zuordnung `mode: development`:
- Definiert dieses Target als `development`-Modus.
- Der Development-Modus implementiert eine Vielzahl von Verhaltensweisen. Zum Beispiel:
- Fügt allen Ressourcen, die nicht als Dateien oder Notebooks bereitgestellt werden, das Präfix **[dev ${workspace.current_user.short_name}]** voran
- Versieht jeden bereitgestellten Job und jede Pipeline mit einem `dev`-Databricks-Tag.
- Weitere Verhaltensweisen finden Sie in der Dokumentation **Development mode**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/deployment-modes#development-mode) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/deployment-modes#development-mode) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/deployment-modes#development-mode)

7. Die Zuordnung `default: true` gibt Folgendes an:
- Dies ist die Standard-Zielumgebung, wenn mehrere Targets verfügbar sind.
- Das Setzen des Standard-Targets auf **development** hilft, versehentliches Bereitstellen in einer Produktionsumgebung zu vermeiden.

8. In der `workspace`-Zuordnung werden folgende Angaben gemacht:
- `host` gibt den Workspace an, in dem dies ausgeführt werden soll. Standardmäßig wird der aktuelle Workspace verwendet. Wir lassen dies auskommentiert.
- `root_path` gibt an, wo die Dateien bereitgestellt werden.

### C3. Hinzufügen unserer Job-Konfiguration zur Datei **databricks.yml**

Nachdem wir die Bundle-Konfiguration in der Datei **databricks.yml** untersucht haben, gehen wir zurück zu unserem Job und kopieren die YAML-Konfiguration (falls erforderlich).

1. Fügen Sie in Ihrer Datei **databricks.yml** Ihre Job-YAML-Konfiguration in der **resources**-Zuordnung mit Ihrer spezifischen Job-YAML-Konfiguration ein (unter dem RESOURCES-Kommentar).

Nachdem Sie Ihre spezifische Job-Konfiguration in Ihre Datei **databricks.yml** eingefügt haben, ändern wir einige der Pfade, sodass sie relative Pfade werden, fügen die Notebook-Erweiterungen hinzu und geben ihr einen einfachen Job-Schlüsselnamen.

2. Unter `resources` > `jobs` sehen Sie einen Schlüssel namens `demo1_simple_dab_username`.
- Ersetzen Sie diesen Schlüssel durch `demo01_simple_dab`.

   ```
   resources:
      jobs:
        demo1_simple_dab_labuser1234:    ## <--------ÄNDERN SIE DIESEN WERT HIER ZU demo01_simple_dab
          name: demo1_simple_dab_labuser1234
   ```

3. Für `task_key: create_bronze_table`:
- Ändern Sie `notebook_path` zu: `./src/create_bronze_table.ipynb`.

4. Für `task_key: create_silver_table`:
- Ändern Sie `notebook_path` zu: `./src/create_silver_table.ipynb`.

5. Schließen Sie die Datei **databricks.yml**.

#### Kontrollpunkt - Beispiel-YAML-Konfiguration (Ihre Werte weichen geringfügig ab)
```
...
resources:
  jobs:
    demo01_simple_dab:
      name: demo1_simple_dab_labuser1234
      tasks:
        - task_key: create_bronze_table
          notebook_task:
            notebook_path: ./src/create_bronze_table.ipynb
            source: WORKSPACE
        - task_key: create_silver_table
          depends_on:
            - task_key: create_bronze_table
          notebook_task:
            notebook_path: ./src/create_silver_table.ipynb
            source: WORKSPACE
      parameters:
        - name: display_target
          default: development
        - name: catalog_name
          default: labuser1234_1_dev
...
```

**
Informationen zum Notebook-Format
**

Notebooks können in verschiedenen Dateierweiterungen vorliegen: `.ipynb`, `.sql`, `.py`. Bestätigen Sie stets die Erweiterung.

- Wählen Sie in der oberen Navigationsleiste unterhalb des Notebook-Namens **File**.

- Scrollen Sie nach unten und suchen Sie die Option **Notebook format**, und wählen Sie sie aus.

- Hier sollten Sie sehen, dass das Notebook-Format als **Source (.ipynb, .py, .sql, etc)** aufgeführt ist.

### C4. Validieren Ihres Bundles
Validieren wir unsere Bundle-Konfigurationsdatei **databricks.yml** mithilfe der Databricks CLI.

1. Führen Sie die Zelle aus und bestätigen Sie, dass die Validierung des Bundles erfolgreich war.

**Bundle validieren**

```bash
%sh
databricks bundle validate
```

**
Fehlerbehebung
**

Wenn nach der Validierung Ihres Bundles der folgende Fehler angezeigt wird, könnte das Format Ihres Notebooks falsch sein.

`Error: notebook src/create_bronze_table.ipynb not found`.

Überprüfen Sie das Format Ihres Notebooks und passen Sie es entsprechend an.

2. Stellen Sie das Bundle mithilfe der Databricks CLI bereit. Führen Sie den untenstehenden Befehl aus, um das Bundle bereitzustellen.

- Der Befehl `databricks bundle deploy -t development` gibt an, das Bundle in der Umgebung `development` bereitzustellen.
- Standardmäßig würde, wenn wir die Zielumgebung nicht angegeben hätten, das zuvor festgelegte Standard-Target (development) verwendet.

**HINWEIS:** Dies dauert etwa eine Minute.

**Bundle bereitstellen**

```bash
%sh
databricks bundle deploy -t development
```

### C5. Anzeigen des bereitgestellten Jobs

1. Sehen wir uns an, wo die Databricks-Assets bereitgestellt wurden.

a. Klicken Sie in der Hauptnavigationsleiste mit der rechten Maustaste auf **Workspace** und wählen Sie **Open in a New Tab**.

b. Navigieren Sie zu **Workspace > Users > Ihr Benutzername** > Ordner **.bundle**.

c. Öffnen Sie **demo01_bundle** (der Bundle-Name, den wir in **databricks.yml** angegeben haben).

d. Hier können wir sehen, dass wir das Target **development** bereitgestellt haben.

- Im Ordner **development** befinden sich verschiedene Ordner und Dateien.

e. Schließen Sie den Workspace-Tab.

**
Information
**

Da Sie das Bundle **innerhalb des Databricks-Workspace** bereitgestellt haben, wurde für das Target **development** eine **quellverknüpfte Bereitstellung** (source-linked deployment) verwendet.

Bei einer quellverknüpften Bereitstellung:
  - Die Quelldateien werden **nicht** in den Ziel-Bereitstellungsordner kopiert
  - Die Bereitstellung verweist direkt auf die vorhandenen Workspace-Dateien

Sie können dies überprüfen, indem Sie den folgenden Ordner kontrollieren. Er wird leer sein:

```text
.bundle/demo01_bundle/development/files
```

2. Führen Sie die folgenden Schritte aus, um den mit einem DAB bereitgestellten Job zu erkunden.

a. Klicken Sie in der linken Hauptnavigationsleiste mit der rechten Maustaste auf **Jobs & Pipelines** und wählen Sie *Open in a new tab*.

b. Suchen Sie Ihren bereitgestellten Job mit dem Namen **[dev username] demo01_simple_dab**.

- Standardmäßig fügt der Development-Modus allen Ressourcen, die nicht als Dateien oder Notebooks bereitgestellt werden, das Präfix `[dev ${workspace.current_user.short_name}]` voran und versieht jeden bereitgestellten Job und jede Pipeline mit einem `dev`-Databricks-Tag.

- Weitere Verhaltensweisen des **Development mode** finden Sie in der Dokumentation:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/deployment-modes#development-mode) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/deployment-modes#development-mode) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/deployment-modes#development-mode)

c. Wählen Sie den Job aus.

d. Beachten Sie den Hinweis oben im Job: **Connected to Declarative Automation Bundles**.

e. Wählen Sie den Link **Learn more** aus und lesen Sie den Hinweis.

f. Scrollen Sie im rechten Navigationsbereich nach unten zu **Job parameters**. Beachten Sie die Werte der Job-Parameter:

- `catalog_name` - Ihr dev-Katalog
- `display_target` - der Wert `development`

g. Lassen Sie den Job-Tab geöffnet.

### C6. Ausführen des Jobs mithilfe der Databricks CLI

1. Führen Sie die untenstehende Zelle aus, um den Job aus der Datei **databricks.yml** mithilfe des CLI-Befehls auszuführen, und bestätigen Sie, dass der Job erfolgreich ausgeführt wird.

- `databricks bundle run -t development demo01_simple_dab` gibt an, diesen Job in der Development-Umgebung auszuführen.

- Dieser Job-Schlüssel findet sich unter der `resources`-Zuordnung in der Datei **databricks.yml**.

**Beispiel (Ihr tatsächlicher Job-`name` wird abweichen)**:
```
resources:
  jobs:
    demo01_simple_dab:    # <--- Der Job-Schlüssel. Ihr Job-Schlüssel sollte sein: demo01_simple_dab
      name: demo1_simple_dab_labuser1234   # <--- Der Job-Name (automatisch generiert, wird abweichen)
```

**Job ausführen**

```bash
%sh
databricks bundle run -t development demo1_simple_dab_labuser15933383_1784705641
```

**
Fehlerbehebung
**

Wenn die Bundle-Ausführung den folgenden Fehler zurückgibt: `Error: resource with key "demo01_simple_dab" not found`.

Das bedeutet, dass Sie den Job-Schlüssel nicht korrekt geändert haben. Überprüfen Sie Ihre `resources`-Zuordnung und bestätigen Sie, dass der Job-Schlüssel `demo01_simple_dab` lautet.

```yaml
resources:
  jobs:
    demo01_simple_dab:   # <--- Dieser Job-Schlüssel hier
      name: demo1_simple_dab_labuser1234
      tasks:
```

2. Nachdem der Job erfolgreich ausgeführt wurde, navigieren Sie zurück zum Job-Tab.

Beachten Sie, dass die obige Zelle automatisch den angegebenen Job unter Verwendung unseres Development-Katalogs ausgeführt hat, den wir in den Job-Parametern in der Datei **databricks.yml** angegeben haben.

![Job Run 1](../Includes/images/simple-dab/job-run-1.png)

3. Führen Sie die untenstehende Zelle aus und bestätigen Sie, dass die folgenden Tabellen durch den Job in unserem Katalog **labuser_UNIQUE_ID_1_dev** erstellt wurden:
- **health_bronze_demo_01**
- **health_silver_demo_01**

**Neue Tabellen anzeigen**

```python
tables = spark.sql(f'''
SHOW TABLES IN {catalog_dev}.default
''')

tables.display()
```

### C7. Ändern der **databricks.yml** und erneutes Bereitstellen des Jobs

1. Nehmen wir eine Änderung an unserer Bundle-Konfiguration in der Datei **databricks.yml** vor.

a. (Falls noch nicht geöffnet) Klicken Sie mit der rechten Maustaste auf die Datei **databricks.yml** und wählen Sie *Open in a new tab*.

b. Ändern Sie in der **resources**-Zuordnung Folgendes:

- Den Standardwert des Job-Parameters `display_target` zu `development_updating_the_value_test`.

c. Führen Sie die untenstehende Zelle aus, um das neue Bundle zu validieren und bereitzustellen.

- Warten Sie, bis die Zelle abgeschlossen ist (etwa 1 Minute).

**Bundle validieren und bereitstellen**

```bash
%sh
databricks bundle validate
databricks bundle deploy -t development
```

**
Information - Erneute Bereitstellung erforderlich, wenn Sie die Konfigurationsdatei databricks.yml aktualisieren
**

Wenn Sie eine Änderung an Ihrer Konfigurationsdatei vornehmen, müssen Sie das Bundle erneut bereitstellen.

Warten Sie nach dem Ändern der Datei **databricks.yml** etwa 30 Sekunden, bis die automatische Speicherung die Datei gespeichert hat, bevor Sie erneut bereitstellen.

2. Nachdem die Bereitstellung abgeschlossen ist, betrachten Sie den neu bereitgestellten Job, indem Sie:
- Zurück zu Ihrem Job navigieren
- Dann die **Job parameters** ansehen (falls die Seite bereits geöffnet ist, aktualisieren Sie die Seite).

Beachten Sie, dass der Standardwert für den Parameter **display_target** basierend auf der Änderung, die wir in der Datei **databricks.yml** vorgenommen haben, aktualisiert wurde.

![Job Run 2](../Includes/images/simple-dab/job-run-2.png)

## D. Zerstören des bereitgestellten Jobs

1. Da wir mit diesem Bundle fertig sind, löschen wir es abschließend mit dem Befehl `databricks bundle destroy`.

Standardmäßig werden Sie aufgefordert, die dauerhafte Löschung der zuvor bereitgestellten Jobs, Pipelines und Artefakte zu bestätigen. Um diese Aufforderungen zu überspringen und eine automatische dauerhafte Löschung durchzuführen, fügen Sie dem Bundle-Destroy-Befehl die Option `--auto-approve` hinzu.

```bash
%sh
databricks bundle destroy --auto-approve
```

**Warnung zum Zerstören**

Das Zerstören eines Bundles löscht dauerhaft die zuvor bereitgestellten Jobs, Pipelines und Artefakte eines Bundles. Diese Aktion kann nicht rückgängig gemacht werden.

Weitere Informationen finden Sie in der Dokumentation **Destroy the bundle**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/work-tasks#step-6-destroy-the-bundle) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/work-tasks#step-6-destroy-the-bundle) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/work-tasks#step-6-destroy-the-bundle)

## Fazit

In dieser Demonstration haben Sie den vollständigen Lebenszyklus eines Declarative Automation Bundle (DAB) für einen einfachen Databricks-Job durchlaufen:

1. Eine YAML-Job-Konfiguration aus einem bestehenden Job mithilfe von **View as code** generiert.
2. Diese Konfiguration in die **databricks.yml** des Bundles unter der `resources.jobs`-Zuordnung eingefügt.
3. Das Bundle mit `databricks bundle validate` validiert.
4. Das Bundle mit `databricks bundle deploy -t development` im Target `development` bereitgestellt.
5. Den bereitgestellten Job mit `databricks bundle run -t development demo01_simple_dab` ausgeführt.
6. Einen Job-Parameter geändert, erneut bereitgestellt und die Änderung in der UI überprüft.
7. Durch Zerstören des Bundles mit `databricks bundle destroy --auto-approve` aufgeräumt.
