# 14L Bonus - Adding ML to Engineering Workflows with DABs/Lab - Adding ML to Engineering Workflows with DABs.py

*(Databricks-Notebook, konvertiert nach Markdown)*

![DB Academy](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/common/db-academy.png)

**Lab-Informationen**

Dies ist eine umfassende Demonstration dazu, wie ein ML-Modell zu einem DAB hinzugefügt wird. Aufgrund der begrenzten Zeit im Live-Unterricht ist dieser Inhalt optional und lässt sich am besten am Ende des Kurses erkunden.

# 14L Bonus – ML in Engineering-Workflows mit Declarative Automation Bundles (DABs) integrieren

### Geschätzte Dauer: 25–30 Minuten

## Überblick

Ihr Data-Engineering-Workflow ist in gutem Zustand. Das ML-Team hat Sie nun gebeten, einen Task für Modell-Inferenz hinzuzufügen, damit der Workflow Vorhersagen mit einem registrierten Unity-Catalog-Modell ausführt, das das Team bereits trainiert hat. **Für dieses Lab benötigen Sie keine ML-Kenntnisse.** Ihr Ziel ist es, das vorhandene Modell in das Bundle einzubinden: die richtigen Variablen deklarieren, einen neuen Task hinzufügen, der das Inferenz-Notebook aufruft, und dasselbe Bundle über die Ziele `development` und `stage` weiterreichen.

## Lernziele

Am Ende dieses Labs können Sie:

1. **Neue Bundle-Variablen** (einschließlich einer `lookup`-Variablen für `cluster_id`) zu einer vorhandenen `variables.yml` **hinzufügen**.
2. **Eine vorhandene Job-YAML** um einen neuen Task **erweitern**, der von vorherigen Tasks abhängt und Parameter an ein Notebook übergibt.
3. **`databricks bundle summary` verwenden**, um vor dem Deployment zu prüfen, was bereitgestellt wird.
4. **Das Bundle gegen `development` validieren, bereitstellen, ausführen und entfernen** und anschließend dasselbe Bundle nach `stage` weiterreichen.

## ERFORDERLICH – EINE COMPUTE-UMGEBUNG AUSWÄHLEN

 **All-Purpose-Compute auswählen**

Dieses Notebook benötigt **All-Purpose-Compute** (Dedicated). Serverless wird für dieses Notebook nicht unterstützt.

Gehen Sie wie folgt vor, um einen All-Purpose-Compute-Cluster anzuhängen:

1. Klicken Sie oben rechts in diesem Notebook auf das Dropdown-Menü, um Ihren Cluster `labuser_USERNAME` auszuwählen.
 - Standardmäßig verwendet das Notebook möglicherweise **Serverless**.

2. Wenn Ihr Cluster verfügbar ist, wählen Sie ihn aus und fahren Sie mit der nächsten Zelle fort. Wenn der Cluster nicht angezeigt wird:

 - Wählen Sie im Dropdown **More**.

 - Wählen Sie im Pop-up **Attach to an existing compute resource** das erste Dropdown. Dort sehen Sie einen eindeutigen Clusternamen. Bitte wählen Sie diesen Cluster aus.

⚠️ **HINWEIS:** Wenn der Cluster den Status **terminated** anzeigt (roter Punkt in der Clusterauswahl), muss er gestartet werden, bevor Sie ihn anhängen können. Klicken Sie auf den Cluster, dann auf **Start**, und warten Sie einige Minuten, bis ein grüner Punkt erscheint.

## ERFORDERLICH – DATEN-SETUP

 **Daten-Setup**

Denken Sie daran, dass Ihre Umgebung mit dem Notebook **02 - REQUIRED - Course Setup and Authentication** eingerichtet wurde.

Wenn Sie Ihr Lab beenden oder Ihre Lab-Sitzung abläuft, wird Ihre Umgebung zurückgesetzt. Sie müssen dann das Notebook **02 - REQUIRED - Course Setup and Authentication** erneut ausführen, um die Kataloge neu zu erstellen und Ihre Anmeldeinformationen für die Databricks CLI zu aktualisieren.

## A. Classroom-Setup

Führen Sie die folgende Zelle aus, um Ihre Arbeitsumgebung für diesen Kurs zu konfigurieren.

**HINWEIS:** Das Objekt `DA` wird nur in Databricks-Academy-Kursen verwendet und ist außerhalb dieser Kurse nicht verfügbar. Es referenziert dynamisch die Informationen, die zum Ausführen des Kurses benötigt werden.

**HINWEIS:** Das Einrichten und Erstellen der Modelle dauert 2–3 Minuten.

```text
%run ../Includes/Classroom-Setup-14L
```

## B. Lab-Szenario

Herzlichen Glückwunsch! Sie haben den Großteil Ihres Workflows erfolgreich aufgebaut. 

Das ML-Team hat Sie gebeten sicherzustellen, dass Ihre Tests die Anforderungen für die Inferenz mit einem Modell erfüllen, das das Team in der Dev-Umgebung bereitgestellt hat. **Für dieses Lab müssen Sie kein ML lernen.** Hängen Sie das Modell einfach mithilfe des bereits erstellten Bundles an den Workflow an.

**Optionale Aufgabe vor dem Start:** Wenn Sie ML-Kenntnisse haben, können Sie das vortrainierte Modell unter **Experiments** untersuchen. Andernfalls besteht Ihr Ziel einfach darin, es zu Ihrem Bundle hinzuzufügen.

### B1. Lab-Gliederung – Einen ML-Task einbinden

Dieses Lab erweitert das CI/CD-mit-DABs-Projekt aus der Demo um einen ML-Task. Die Struktur unten entspricht dem zuvor erstellten siebenstufigen Bundle, wobei die ML-Ergänzungen grün hervorgehoben sind: ein Pipeline-Notebook `silver_sample_dlt` und ein Notebook `Inference` unter `src/` sowie die Variablen `base_model_name` und `silver_table_name` in `variables.yml`.

Lab-Gliederung
Einen ML-Task einbinden

*(Diagramm – siehe Original-Notebook)*

## C. Vorabprüfungen

Bestätigen Sie vor Beginn der Lab-Aufgaben, dass die Databricks CLI gegenüber Ihrem Workspace authentifiziert ist. Führen Sie die folgenden Zellen aus und prüfen Sie auf Fehler.

```bash
databricks catalogs list
```

## D. Aufgabe 1 – `variables.yml` aktualisieren

Im Ordner dieses Notebooks finden Sie einen Unterordner namens **TODO - Lab DABs Workflow**. 

Dort bearbeiten Sie einige Dateien, um das registrierte ML-Modell an den Workflow anzuhängen. 

**Sie müssen nicht wissen, was das Modell tut** – Ihr Ziel ist es zu verstehen, wie Sie ein zusätzliches Unity-Catalog-Asset (in diesem Fall ein registriertes ML-Modell) anhängen.

#### Was im Bundle enthalten ist

1. Navigieren Sie zum Ordner **src/**. Dort finden Sie:
 - **dlt_pipelines/**
 - **helpers/**,
 - Zwei Notebooks: **Final Visualization** und **Inference**. 
 - Dieses Lab konzentriert sich auf das Notebook **Inference**.

2. Sehen Sie sich im Notebook **Inference** den Abschnitt **Parameterize the notebook for our workflow and passing variables** an. Das Notebook liest zwei Variablen:
 - **base_model_name**: der Name des registrierten Modells
 - **silver_table_name**: Name und Speicherort der Silber-Tabelle, erwartet als **catalog.schema.silver_sample_ml**

3. Öffnen Sie in einem separaten Tab **resources/variables.yml**. Hier fügen Sie einige Variablen hinzu.

### Schritt 1.1 – `base_model_name` zu **variables.yml** hinzufügen

Fügen Sie im markierten Abschnitt eine Variable `base_model_name` hinzu 

- Um den Standardwert zu finden, suchen Sie das Modell in Ihrem Dev-Katalog (**labuser_UNIQUE_ID_1_dev.default**) unter **Models**.

### Schritt 1.2 – `silver_table_name` in **variables.yml** ansehen

Sehen Sie sich die Variable `silver_table_name` an. 
 - Der Standardwert sollte auf `${var.username}_1_dev.default.silver_sample_ml` gesetzt sein.

### Schritt 1.3 – `cluster_id` zu **variables.yml** hinzufügen

Der Inferenz-Task benötigt einen vorhandenen Cluster. Definieren Sie eine Variable `cluster_id`. Sie haben vier Möglichkeiten:

- **Option 1:** Eine `lookup`-Variable auf `username` definieren und über `${var.username}` referenzieren.
- **Option 2:** `lookup` verwenden und den Wert `cluster` auf `${workspace.current_user.userName}` setzen.
- **Option 3:** Den Standardwert mit der `lookup`-Methode fest codieren.
- **Option 4:** Ihre Cluster-ID ermitteln, indem Sie im linken Menü zu **Compute** navigieren, Ihren Cluster öffnen, auf das Kebab-Menü klicken und **View JSON** wählen. Kopieren Sie die Cluster-ID im oberen Bereich des JSON. Alternativ führen Sie `print(spark.conf.get("spark.databricks.clusterUsageTags.clusterId"))` in einer neuen Zelle aus. 
 - Fügen Sie diesen Wert als `default` für `cluster_id` ein.

**
 Zusammenfassung
 **

Nach dieser Aufgabe sollte **variables.yml** drei neue Variablen enthalten: `base_model_name`, `silver_table_name` und `cluster_id`. Jede hat eine Beschreibung und einen Standardwert.

**TIPP:** Dokumentation zu Variablenersetzung und Lookups:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/variables) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/variables) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/variables)

## E. Aufgabe 2 – `resources/job/dabs_workflow_with_ml.job.yml` aktualisieren

Nachdem **variables.yml** aktualisiert ist, erweitern Sie den Workflow um einen neuen Inferenz-Task. (In diesem Schritt konfigurieren Sie die Spark Declarative Pipeline nicht.)

Navigieren Sie zu **resources/job/** und öffnen Sie **dabs_workflow_with_ml.job.yml**. Sie sehen alle vorhandenen Tasks. 

Fügen Sie unter dem Kommentar `### Complete your ML TASK HERE` einen neuen Task mit den folgenden Vorgaben hinzu:

1. Task-Name (`task_key`) **ML_test** hinzufügen.

2. Der Task muss über `depends_on` von **Health_ETL** abhängen.

3. Einen Schlüssel `existing_cluster_id` hinzufügen, dessen Wert auf die in Aufgabe 1 erstellte Variable `cluster_id` verweist.
 - Referenzieren Sie Ihre Variable `cluster_id`: `${var.cluster_id}`. 

4. Einen `notebook_task` mit `notebook_path`, `base_parameters` und `source` hinzufügen:

 - `notebook_path` sollte auf das Notebook **Inference** verweisen (**TIPP**: In der Ordnerstruktur zurückgehen).

 - `base_parameters` sollte **3** Schlüssel haben: 
 - Zwei, die auf die neuen Variablen verweisen (`base_model_name` und `silver_table_name`)
 - Einen, der auf den Dev-Katalog verweist. 
 - **TIPP:** Verwenden Sie eine Variable, die bereits in **variables.yml** vorkonfiguriert ist.

 - Wenn Sie möchten, können Sie auch eine Beschreibung hinzufügen.

**TIPP:** Verwenden Sie die vorhandenen Tasks in dieser Datei als Vorlagen.

**
 Zusammenfassung
 **

Nach dieser Aufgabe enthält **dabs_workflow_with_ml.job.yml** einen neuen Task, der an die vorhandene Abhängigkeit **Health_ETL** angebunden ist, und Sie können das Bundle validieren.

## F. Aufgabe 3 – Die Bundle-Zusammenfassung ansehen

Verwenden Sie `databricks bundle summary`, um die im Projekt definierten Ressourcen und die Namen auszugeben, die nach dem Deployment des Bundles erzeugt werden.

**HINWEIS:** Jede `%sh`-Zelle startet eine neue Shell, daher müssen Sie in **derselben** Zelle mit `cd` in den Ordner **TODO - Lab DABs Workflow** wechseln *und* den CLI-Befehl ausführen.

```bash
cd "./TODO - Lab DABs Workflow"
databricks bundle summary
```

**
 Fehlerbehebung
 **

Wenn Sie nach dem Validieren Ihres Bundles den folgenden Fehler sehen, ist das Format Ihres Notebooks möglicherweise falsch.

`Error: notebook xxx not found`. 

Prüfen Sie das Format Ihres Notebooks und passen Sie es entsprechend an.

## G. Aufgabe 4 – Das Bundle validieren

Validieren Sie Ihre Bundle-Konfigurationsdatei **databricks.yml** mit der Databricks CLI für das Ziel `development`. Bestätigen Sie, dass die Validierung erfolgreich ist. Bei einem Fehler korrigieren Sie das YAML und führen die Zelle erneut aus.

**TIPP:** Dokumentation zu den CLI-Befehlen `databricks bundle`:
[AWS](https://docs.databricks.com/aws/en/dev-tools/cli/bundle-commands) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/cli/bundle-commands) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/cli/bundle-commands)

```python
# <FILL-IN>
```

##### LÖSUNG

<details>
 <summary>FÜR DEN LÖSUNGSCODE AUFKLAPPEN</summary>

```
<!-------------------ADD SOLUTION CODE BELOW------------------->
cd "./TODO - Lab DABs Workflow"
pwd
databricks bundle validate -t development
<!-------------------END SOLUTION CODE------------------->
```

</details>

## H. Aufgabe 5 – In das Ziel `development` bereitstellen

Stellen Sie das Bundle im Ziel `development` bereit.

```python
# <FILL-IN>
```

##### LÖSUNG

<details>
 <summary>FÜR DEN LÖSUNGSCODE AUFKLAPPEN</summary>

```
<!-------------------ADD SOLUTION CODE BELOW------------------->
cd "./TODO - Lab DABs Workflow"
databricks bundle deploy -t development
<!-------------------END SOLUTION CODE------------------->
```

</details>

Navigieren Sie zu **Jobs & Pipelines** und öffnen Sie den Job `[dev labuser_UNIQUE_ID] ml_health_etl_workflow_development`

#### Checkpoint – Dev-Deployment
![Ml Job Deploy](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/ml-lab/dev-deployment-job-checkpoint.png)

## I. Aufgabe 6 – Den `development`-Workflow ausführen

Führen Sie den bereitgestellten Workflow gegen das Ziel `development` aus. 

Der Job-Schlüssel im Bundle lautet `ml_health_etl_workflow`.

```python
# <FILL-IN>
```

#### Checkpoint – Dev-Run 
![Ml Job Deploy](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/ml-lab/dev-job-run.png)

**
 Fehlerbehebung
 **

Wenn Sie nach dem Ausführen Ihres Bundles den folgenden Fehler sehen, ist das Format Ihres Notebooks möglicherweise falsch.

```
Error: Task Health_ETL failed!
Error:
Please refer to the logs for this pipeline in the pipelines page.
```

Prüfen Sie das Format Ihres Notebooks für die SDP und passen Sie es entsprechend an!

##### LÖSUNG

<details>
 <summary>FÜR DEN LÖSUNGSCODE AUFKLAPPEN</summary>

```
<!-------------------ADD SOLUTION CODE BELOW------------------->
cd "./TODO - Lab DABs Workflow"
databricks bundle run ml_health_etl_workflow -t development
<!-------------------END SOLUTION CODE------------------->
```

</details>

## J. Aufgabe 7 – Das `development`-Bundle entfernen

Räumen Sie das `development`-Deployment auf.

```bash
cd "./TODO - Lab DABs Workflow"
databricks bundle destroy -t development --auto-approve
```

## K. Aufgabe 8 – Das Bundle nach `stage` weiterreichen

Stellen Sie sich vor, Sie haben Ihren Code überprüft, die Testabdeckung analysiert usw. und sind bereit, in einer Staging-Umgebung bereitzustellen und zu testen. DABs machen das einfach: Sie ändern ein CLI-Flag (`-t stage`), und die Überschreibungen des Ziels `stage` im Bundle erledigen den Rest.

Durchlaufen Sie denselben Lebenszyklus, diesmal gegen das Ziel `stage`. Sehen Sie sich zunächst den Block `stage` in **databricks.yml** an und beachten Sie, welche Überschreibungen bereits für Sie gesetzt wurden.

### Schritt 8.1 – Bundle-Zusammenfassung für `stage`

```bash
cd "./TODO - Lab DABs Workflow"
databricks bundle summary -t stage
```

### Schritt 8.2 – `stage` validieren

```bash
cd "./TODO - Lab DABs Workflow"
databricks bundle validate -t stage
```

### Schritt 8.3 – In `stage` bereitstellen

```bash
cd "./TODO - Lab DABs Workflow"
databricks bundle deploy -t stage
```

### Schritt 8.4 – Den `stage`-Workflow ausführen

```bash
cd "./TODO - Lab DABs Workflow"
databricks bundle run ml_health_etl_workflow -t stage
```

#### Checkpoint – Stage-Run

![Ml Job Deploy Stage](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/ml-lab/stage-job-run.png)

### Schritt 8.5 – Das `stage`-Bundle entfernen

```bash
cd "./TODO - Lab DABs Workflow"
databricks bundle destroy -t stage --auto-approve
```

## Fazit

Gute Arbeit. In diesem Lab haben Sie ein registriertes Unity-Catalog-ML-Modell in ein bestehendes Engineering-Bundle eingebunden, ohne den Rest des Workflows zu ändern:

1. Die Variablen `base_model_name`, `silver_table_name` und `cluster_id` zu **variables.yml** hinzugefügt.
2. Einen neuen Inferenz-Task zu **dabs_workflow_with_ml.job.yml** hinzugefügt, der von **Health_ETL** abhängt und das Notebook **Inference** mit drei `base_parameters` aufruft.
3. Mit `databricks bundle summary` das aufgelöste Bundle vor dem Deployment untersucht.
4. Das Bundle gegen `development` validiert, bereitgestellt, ausgeführt und entfernt.
5. Dasselbe Bundle mit einem einzigen Flag `-t stage` nach `stage` weitergereicht und dort denselben Lebenszyklus durchlaufen.

## Nächste Schritte

Versuchen Sie, mit dem hier Gelernten ein eigenes DAB von Grund auf zu erstellen. Es hilft, den Workflow schrittweise – Task für Task – auszubauen und nach jeder Änderung zu validieren, damit Probleme leicht einzugrenzen bleiben.

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
