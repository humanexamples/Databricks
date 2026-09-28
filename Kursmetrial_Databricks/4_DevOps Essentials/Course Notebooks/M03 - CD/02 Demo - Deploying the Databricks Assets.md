In Databricks haben Sie mehrere Optionen zur Bereitstellung Ihrer Databricks-Assets, etwa die UI, REST APIs, die Databricks CLI, das Databricks SDK oder Declarative Automation Bundles (DABs). Databricks empfiehlt Declarative Automation Bundles zum Erstellen, Entwickeln, Bereitstellen und Testen von Jobs und anderen Databricks-Ressourcen als Quellcode.

In dieser Demonstration deployen wir unser Projekt und erkunden den Job und die Pipeline über die Jobs-and-Pipelines-UI. Anschließend untersuchen wir die JSON- und YAML-Strukturen des Workflows und besprechen, wie wir diese in unserem CI/CD-Prozess verwenden können.

**FINALER JOB**

![Finaler SDK-Workflow](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/05_final_sdk_workflow.png)

---

2. Während der Entwicklung ist es vorteilhaft, Ihren Workflow und/oder Ihre Spark Declarative Pipeline über die UI aufzubauen. Die UI bietet eine einfache Möglichkeit, Ihren gewünschten Job zu erstellen, und sie generiert die notwendigen JSON- oder YAML-Dateien, um Ihre Bereitstellung über verschiedene Umgebungen hinweg zu automatisieren.

 **HINWEIS:** In der Zelle unten erstellen wir den Job mit von Databricks Academy bereitgestellten eigenen Funktionen, die im Hintergrund das Databricks SDK nutzen. **Dieser Ansatz spart in der Klasse Zeit, indem er das manuelle Erstellen des Workflows über die UI für die Demonstration vermeidet. Workflows sind eine Voraussetzung für diesen Kurs.**

---

```python
## Bestätigen, dass die Pipeline aus der vorherigen Demonstration existiert. Falls nicht, die Spark Declarative Pipeline erstellen und die ID speichern
my_pipeline_id = obtain_pipeline_id_or_create_if_not_exists()
print(my_pipeline_id)

# ## Den Job erstellen
create_demo_cd_job(my_pipeline_id = my_pipeline_id, job_name = f'Dev Workflow Using the SDK_{DA.catalog_name}')
```

---

3. Führen Sie die folgenden Schritte aus, um den neuen Job anzusehen und auszuführen:

    a. Klicken Sie in der ganz linken Navigationsleiste mit der rechten Maustaste auf **Jobs and Pipelines** und wählen Sie *Open Link in New Tab*.

    b. Im Tab **Jobs & Pipelines** sollten Sie einen Job namens **Dev Workflow Using the SDK_user_name** sehen.

    c. Wählen Sie den Job **Dev Workflow Using the SDK_user_name** aus.

    d. Wählen Sie **Run now**, um den Job auszuführen.

    e. Lassen Sie den Job offen.

---

4. Erkunden Sie die Job-Aufgaben, während der Job läuft. Der Job benötigt zwischen 5 und 7 Minuten. Navigieren Sie zum Tab **Runs** des Jobs. Hier sollten Sie sehen, wie der Job ausgeführt wird.

**Beschreibungen der Job-Aufgaben**
![Beschreibung des finalen SDK-Workflows](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/05_Final_Workflow_Desc.png)

#####4a. Aufgabe 1: Unit_Tests

- a. Klicken Sie im Tab **Runs** des Jobs mit der rechten Maustaste auf das Kästchen für **Unit_Tests** und wählen Sie *Open Link in New Tab*.

- b. Beachten Sie, dass das Notebook **Run Unit Tasks** die Unit-Tests ausführt, die wir zuvor erstellt haben.

- c. Schließen Sie den Tab.


#####4b. Aufgabe 2: Health_ETL

- a. Wählen Sie den Tab **Tasks** und wählen Sie die Aufgabe **Health_ETL**.

- b. Suchen Sie im Abschnitt **Task** den Wert **Pipeline** und wählen Sie das Symbol rechts neben dem Pipeline-Namen, um die Pipeline zu öffnen.

   **HINWEIS:** Wenn die Spark Declarative Pipeline bereits abgeschlossen ist, wählen Sie einfach den Pipeline-Link.

- c. Beachten Sie, dass die Pipeline die zuvor erstellte ETL-Pipeline ausführt (bzw. ausführen wird).

- d. Schließen Sie die Spark Declarative Pipeline.


#####4c. Aufgabe 3: Visualization

- a. Wählen Sie den Tab **Runs** des Jobs, klicken Sie mit der rechten Maustaste auf das Kästchen für **Visualization** und wählen Sie *Open Link in New Tab*.

- b. Beachten Sie, dass das Notebook **Final Visualization** die finale Visualisierung für das Projekt erstellt.

- c. Schließen Sie den Tab.


Lassen Sie den Job offen, während er weiterläuft, und fahren Sie mit den nächsten Schritten fort.

---

5. Führen Sie Folgendes aus, um die JSON-Datei zum Bereitstellen dieses Jobs anzusehen:

   a. Navigieren Sie zurück zum Haupt-Workflow-Job, indem Sie den Tab **Tasks** auswählen.

   b. Wählen Sie oben rechts im Job das Kebab-Menü (Symbol mit drei Punkten in der Nähe der Schaltfläche **Run now**).

   c. Wählen Sie **View as code** und wählen Sie dann im oberen Tab **JSON**.

   d. Beachten Sie, dass Sie die JSON-Definition für den Job zur Verwendung mit der REST API ansehen können. Das ist eine gute Möglichkeit, die notwendigen Werte einfach zu erhalten, um Ihre Bereitstellung für die REST API zu automatisieren (die SDK-Werte sind ähnlich).

   e. Schließen Sie das Pop-up **Job JSON**.

---

6. Führen Sie Folgendes aus, um die YAML-Datei zum Bereitstellen dieses Jobs anzusehen:

   a. Bestätigen Sie, dass Sie sich im Tab **Tasks** befinden.

   b. Wählen Sie oben rechts im Job das Kebab-Menü (Symbol mit drei Punkten in der Nähe der Schaltfläche **Run now**).

   c. Wählen Sie **Edit as YAML**.

   d. Beachten Sie, dass Sie den Job als YAML ansehen können. Das ist eine gute Möglichkeit, die notwendigen Werte für die YAML-Bereitstellung einfach zu erhalten (diese YAML-Datei ist bei der Bereitstellung mit **Declarative Automation Bundles** äußerst hilfreich).

   e. Wählen Sie oben rechts **Close editor**.

---

7. Der Job sollte inzwischen abgeschlossen sein. Sehen Sie sich den abgeschlossenen Job an und bestätigen Sie, dass die drei Aufgaben erfolgreich abgeschlossen wurden. Sie können sich die abgeschlossenen Aufgaben gerne ansehen.

---

8. Führen Sie die folgenden Schritte aus, um den Databricks-SDK-Code zum Erstellen des Workflows anzusehen.

    a. SDK-Code: **[../Includes/Classroom-Setup-CD]($../Includes/Classroom-Setup-CD)**

    b. Scrollen Sie nach unten zu Zelle 4: `def create_demo_cd_job(my_pipeline_id, job_name)`

    c. Beachten Sie die Menge an Python-Code, die verwendet wird, um den Job zur Bereitstellung unseres Entwicklungscodes zu erstellen.

**HINWEIS:** Details des Databricks-SDK-Codes liegen außerhalb des Umfangs dieses Kurses.

Das SDK bietet zwar Low-Level-Kontrolle über Ihre Bereitstellung, erfordert aber auch erheblichen Zeit- und Arbeitsaufwand, um den gesamten notwendigen Code zu schreiben.

In diesem Beispiel deployen wir nur den Entwicklungs-Job. Für die Bereitstellung sowohl der Staging- als auch der Produktions-Jobs sind zusätzliche Anpassungen nötig.

---

## Nächste Schritte für CI/CD

Denken Sie über Folgendes nach, um dieses Projekt unter Nutzung des gesamten CI/CD-Prozesses bereitzustellen:
- Wie deploye ich die Databricks-Assets automatisch für die Umgebungen **dev**, **stage** und **prod**?
- Wie parametrisiere ich alle benötigten Werte basierend auf der Zielumgebung?
- Wie konfiguriere ich die notwendigen Variablen für die Spark Declarative Pipeline bei jeder Bereitstellung?
- Wie pflege ich den gesamten Code?
- Wie automatisiere ich diesen gesamten Prozess?
- Wie kann ich ein System für Continuous Integration und Continuous Delivery oder Deployment (CI/CD), etwa GitHub Actions, einrichten, um Ihre Unit-Tests automatisch auszuführen, wann immer sich Ihr Code ändert? Ein Beispiel finden Sie in der Behandlung von GitHub Actions in [Software engineering best practices for notebooks](https://docs.databricks.com/en/notebooks/best-practices.html).

### Nächste Schritte:

In diesem Kurs haben Sie die Grundlagen von CI/CD mit einem Fokus auf Continuous Integration (CI) in Databricks erkundet. Als Nächstes sollten Sie in die andere Hälfte der DevOps-Pipeline eintauchen, Continuous Deployment (CD), indem Sie lernen, wie man Assets mit **Declarative Automation Bundles (DABs)** bereitstellt.

#### DABs-Dokumentation [What are Declarative Automation Bundles?](https://docs.databricks.com/en/dev-tools/bundles/index.html)

#### Databricks-Academy-Kurs: [Automated Deployment with Declarative Automation Bundles](https://www.databricks.com/training/catalog/automated-deployment-with-declarative-automation-bundles-3724)

---

# Nächste Schritte für Python-Unit-Testing in Databricks

Sie haben nun:
- **Ein Databricks-Projekt organisiert** in `src/`- und `tests/`-Ordner mit einer `pyproject.toml`-Konfigurationsdatei.
- **Reine Python-Hilfsfunktionen und Unit-Tests geschrieben** mit `pytest` und `@pytest.mark.parametrize`.
- **PySpark-Transformationsfunktionen geschrieben** und sie mit einer gemeinsamen `SparkSession`-Fixture aus `conftest.py` getestet.
- **Unit-Tests ausgeführt** – interaktiv in der Databricks-Workspace-UI und aus einer Notebook-Zelle.
- **Fehler in der Transformationslogik erkannt und behoben** mit automatisierten Unit-Tests.

### Wohin als Nächstes:

- `pytest` als **Databricks-Workflow-Aufgabe** für die CI/CD-Integration ausführen
- **Declarative Automation Bundles** erkunden, um Tests zusammen mit Pipelines zu paketieren
- Die Databricks-Dokumentation zu [Python unit testing](https://docs.databricks.com/aws/en/files/python-unit-tests) im Workspace für weitere Details ansehen

---

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
