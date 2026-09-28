# 13 - Integrationstests durchführen

Integrationstests für Data Engineering stellen sicher, dass verschiedene Komponenten der Datenpipeline – etwa Datenaufnahme, Transformation, Speicherung und Abruf – in einer realitätsnahen Umgebung nahtlos zusammenarbeiten. Diese Tests validieren den Datenfluss über Systeme hinweg und prüfen auf Probleme wie Dateninkonsistenz, Formatabweichungen und Verarbeitungsfehler, wenn Komponenten wie erwartet interagieren.

Es gibt mehrere Wege, Integrationstests innerhalb von Databricks umzusetzen:

1. **Apache Spark™ Declarative Pipeline (früher DLT)**: Mit Apache Spark™ Declarative Pipelines können Sie Expectations verwenden, um die Ergebnisse der Pipeline zu prüfen.
    - [Manage data quality with pipeline expectations](https://docs.databricks.com/aws/en/ldp/expectations#manage-data-quality-with-pipeline-expectations)

2. **Jobs**: Sie können Integrationstests auch als Databricks Job mit Aufgaben durchführen – ähnlich dem, was typischerweise für Nicht-Spark-Declarative-Pipeline-Code gemacht wird.

---

## B. Option 1 – Spark Declarative Pipeline mit Integrationstests

In diesem Abschnitt erstellen wir eine Spark Declarative Pipeline mit den modularisierten Funktionen aus der Datei `src.helpers`, die wir im vorherigen Notebook mit Unit-Tests getestet haben. In der Pipeline verwenden wir diese Funktionen, um Tabellen zu erstellen, und setzen dann einige einfache Integrationstests für die Ausgabetabellen in unserer ETL-Pipeline für dieses Projekt um.

1. Wir erstellen die Spark Declarative Pipeline für dieses Projekt mit der Databricks-Academy-Klasse **`DAPipelineConfig`**, die speziell für diesen Kurs mit dem **Databricks SDK** entwickelt wurde. Dadurch vermeiden wir das manuelle Erstellen der Pipeline für diese Demo. Normalerweise würden Sie die Pipeline während der Entwicklung manuell über die UI aufbauen.

    **HINWEIS:** Das Databricks SDK liegt außerhalb des Umfangs dieses Kurses. 


![Vollständige Spark Declarative Pipeline](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/04_dlt_pipeline.png)

---

```python
# DeclarativePipelineCreator() befindet sich in Includes/Classroom-Setup-Common.ipynb
pipeline = DeclarativePipelineCreator(
                            pipeline_name=f"sdk_health_etl_{DA.catalog_dev}", 
                            catalog_name = DA.catalog_name,
                            schema_name = 'default',
                            root_path_folder_name='src',
                            source_folder_names=[
                                'src/sdp/**', 
                                'tests/integration_test/**'],
                            configuration = {
                                'target': 'development',
                                'raw_data_path':f'/Volumes/{DA.catalog_name}/default/health'
                            })

pipeline.create_pipeline()

pipeline.start_pipeline()
```

---

Öffnen Sie jedes Notebook in einem neuen Tab, um sie zu untersuchen:

 - **Notebook 1: [..../src/sdp/ingest-bronze-silver_sdp]($../../src/sdp/ingest-bronze-silver_sdp.py)** – Ruft die Konfigurationsvariablen der Spark Declarative Pipeline ab, die Ziel und Rohdaten festlegen, und erstellt die Bronze- und Silber-Tabellen basierend auf diesen Variablenwerten.

 - **Notebook 2: [..../src/sdp/gold_tables_sdp]($../../src/sdp/gold_tables_sdp.sql)** – Erstellt die Gold-Tabelle.

 - **Notebook 3: [..../tests/integration_test/integration_tests_sdp]($../../tests/integration_test/integration_tests_sdp)** – Führt einfache Integrationstests für die Bronze-, Silber- und Gold-Tabellen basierend auf der Zielumgebung durch.

![SDP-Pipeline erklärt](https://files.training.databricks.com/binder/prod_main/devops-essentials-for-data-engineering-en_us-2.2.1/images/20260819T031042Z/DevOps Essentials for Data Engineering/Course Notebooks/Includes/images/04_sdp_explain_integrations.png)

---

## C. Option 2 – Integrationstests mit Notebooks und Databricks Jobs
Sie können Integrationstests auch **mit Notebooks** durchführen und sie als Aufgaben in Jobs für Ihre Pipeline hinzufügen.

**HINWEIS:** Wir betrachten lediglich, wie man Integrationstests mit Jobs umsetzt, falls das die von Ihnen bevorzugte Methode ist. Die finale Bereitstellung für diesen Kurs verwendet die Integrationstests der Spark Declarative Pipeline mit Expectations.

#### Zu unternehmende Schritte:
1. Erstellen Sie ein Setup-Notebook, um jegliches erforderliche dynamische Setup mit Job-Parametern für Ihre Zielumgebung und Datenspeicherorte zu handhaben.

2. Erstellen Sie zusätzliche Notebooks oder Dateien, um die Integrationstests zu speichern, die Sie als Aufgaben ausführen möchten.

3. Organisieren Sie die neuen Notebooks oder Dateien innerhalb Ihres Ordners **tests**.

4. Erstellen Sie einen Workflow. Innerhalb des Workflows:

   - a. Erstellen Sie die notwendigen Tabellen oder Ansichten mit einer Spark Declarative Pipeline oder mit Code.

   - b. Fügen Sie Aufgaben hinzu, um Ihre Integrationstests einzurichten (z. B. das Setzen dynamischer Job-Parameter, die gesetzt werden müssen).

   - c. Führen Sie die Validierung durch, indem Sie Ihre Notebooks als Aufgaben verwenden, und legen Sie fest, dass alle Aufgaben erfolgreich sein müssen.

**HINWEISE:** Ein großer Nachteil dieses Ansatzes ist, dass Sie mehr Code für Setup- und Validierungsaufgaben schreiben müssen sowie die Job-Parameter verwalten müssen, um den Code je nach Zielumgebung dynamisch anzupassen.
