In dieser Demonstration bauen Sie auf allem auf, was Sie über DABs gelernt haben, und wenden es auf einen CI/CD-Workflow mit drei Umgebungen (`development`, `stage`, `production`) an. 

Das Bundle stellt einen Workflow bereit, der **Unit-Tests**, eine **Apache Spark™ Declarative Pipeline (SDP)** für ETL und Integrationstests sowie ein **Visualisierungs-Notebook** ausführt. Jedes Ziel überschreibt Katalog, Rohdatenpfad und (für dev/stage) das Compute, während Production auf Serverless läuft.



```text
%run ../Includes/Classroom-Setup-13
```

Führen Sie die folgende Zelle aus, um zu bestätigen, dass die Databricks CLI funktioniert.

```bash
databricks catalogs list
```

```python
%sh 
cd "Full Project" 
pwd;
databricks bundle validate -t development

databricks bundle deploy -t development

databricks bundle run health_etl_workflow
```

```python
%sh
cd "Full Project" 
databricks bundle validate -t stage

databricks bundle deploy -t stage

databricks bundle run health_etl_workflow -t stage
```

```python
%sh
cd "Full Project" 
databricks bundle validate -t production

databricks bundle deploy -t production

databricks bundle run health_etl_workflow -t production
```

```python
# Destroy all bundles
%sh
cd "Full Project";
databricks bundle destroy -t development --auto-approve;
databricks bundle destroy -t stage --auto-approve;
databricks bundle destroy -t production --auto-approve;
```

Dieses Projekt definiert über ein Declarative Automation Bundle (DAB) einen **Workflow** namens `health_etl_workflow`, der aus **drei Tasks** besteht, die als CI/CD-Pipeline durch die Umgebungen `development`, `stage` und `production` deployed werden.

**1. Task: `Unit_Tests`** (Einstiegspunkt, keine Abhängigkeiten)

- Führt das Notebook `run_unit_tests` aus, das via pytest drei Tests in `test_spark_helper_functions.py` startet:
  - `test_get_health_csv_schema_match` — prüft, ob das CSV-Schema aus `project_functions.get_health_csv_schema()` exakt der erwarteten Struktur entspricht (ID, PII, date, HighCholest, HighBP, BMI, Age, Education, income).
  - `test_high_cholest_column_valid_map` — validiert, dass die UDF `high_cholest_map` Werte korrekt auf „Normal", „Above Average", „High" oder „Unknown" abbildet.
  - `test_age_group_column_valid_map` — validiert, dass `group_ages_map` Alterswerte korrekt in Gruppen wie „0-9", „10-19", …, „50+" kategorisiert.

**2. Task: `Health_ETL`** (abhängig von `Unit_Tests`)

- Startet eine **Spark Declarative Pipeline** (`health_etl_pipeline`), die aus drei Notebooks besteht:
  - **`ingest-bronze-silver_dlt.py`** — liest per Auto Loader CSV-Dateien aus einem umgebungsabhängigen Volume-Pfad (`raw_data_path`). Erzeugt die Streaming-Tabelle `health_bronze` (mit Expectations: `PII IS NOT NULL`, `date IS NOT NULL`) und transformiert sie zu `health_silver`, wobei die UDFs `high_cholest_map` und `group_ages_map` aus `project_functions.py` die Spalten `HighCholest_Group` und `Age_Group` hinzufügen.
  - **`gold_tables_dlt.sql`** — erstellt die Materialized View `chol_age_agg`, die `health_silver` nach `HighCholest_Group` und `Age_Group` aggregiert (COUNT).
  - **`integration_tests_dlt`** — führt Integrationstests innerhalb der Pipeline aus: In dev/stage wird die exakte Zeilenanzahl von `health_bronze` und `health_silver` geprüft (7.500 in dev, 35.000 in stage); in allen Umgebungen werden die Spaltenwerte der Gold-Tabelle `chol_age_agg` auf gültige Kategorien validiert. Fehlschläge brechen die Pipeline ab (`expect_all_or_fail`).

**3. Task: `Visualization`** (abhängig von `Health_ETL`)

- Führt das Notebook `Final Visualization` aus, das den Job-Parameter `catalog_name` entgegennimmt, die Gold-Tabelle `chol_age_agg` aus dem jeweiligen Zielkatalog liest und ein gestapeltes Balkendiagramm (Cholesterinverteilung nach Altersgruppe) mit matplotlib erzeugt.

## Nächste Schritte

![ci_cd](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/13 Demo - Continuous Integration and Continuous Deployment with DABs/images/ci_cd_overview.png)

Überlegen Sie, wie Sie DABs nutzen können, um die Entwicklung durch programmatische Verwaltung Ihrer Workflows zu beschleunigen. Mit DABs können Sie Ihre verschiedenen Assets und Artefakte für CI/CD-Workflows konsistent und wiederholbar erstellen, verwalten und bereitstellen.

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
