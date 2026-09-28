# 14L Bonus - Adding ML to Engineering Workflows with DABs/Solution - Lab DABs Workflow/src/dlt_pipelines/ingest-bronze-silver_dlt.py

```python

####################################################
# Simple Ingest-Bronze-Silver SDP Pipeline Example
####################################################
# Diese SDP ist ein einfaches Beispiel, das zeigt, wie Expectations auf Tabellen gesetzt werden. Sie dient als Ausgangspunkt, und Sie können je nach Bedarf problemlos weitere Tabellen oder Expectations hinzufügen. Der Einfachheit halber konzentriert sich dieses Beispiel auf das Wesentliche.

# Weitere Informationen finden Sie in den folgenden Ressourcen.

# - [Manage data quality with pipeline expectations](https://docs.databricks.com/en/delta-live-tables/expectations.html#manage-data-quality-with-pipeline-expectations)

# - [Expectation recommendations and advanced patterns](https://docs.databricks.com/en/delta-live-tables/expectation-patterns.html#expectation-recommendations-and-advanced-patterns)

# - [Applying software development & DevOps best practices to Delta Live Table pipelines](https://www.databricks.com/blog/applying-software-development-devops-best-practices-delta-live-table-pipelines)

from pyspark import pipelines as dp
import pyspark.sql.functions as F

## Übergeordneten Ordner zum Python-Pfad hinzufügen, um unser helpers-Paket zu importieren
import sys
sys.path.append('../.')
from helpers import project_functions



####################################################
## Konfigurationsvariablen abrufen
####################################################
# Dieser Pfad zu den Rohdaten und der Katalog werden dynamisch über die Konfigurationsvariable gesetzt, die in der SDP-Pipeline für jede Umgebung festgelegt ist: **development**, **stage** oder **production**.

# - **development** – Liest die Dev-CSV-Datei aus **your_unique_catalog_1_dev.default.health.dev_health.csv**.

# - **stage** – Liest die Stage-CSV-Datei aus **your_unique_catalog_2_stage.default.health.stage_health.csv**.

# - **production** – Liest die CSV-Dateien im Produktions-Volume **your_unique_catalog_2_stage.default.health/*.csv**.

## Die Zielumgebung der Konfiguration in der Variablen target speichern
target = spark.conf.get("target")

## Die Konfiguration des Rohdatenpfads in der Variablen raw_data_path speichern
raw_data_path = spark.conf.get("raw_data_path")


####################################################
# A. Ingest CSV Files -> health_bronze
####################################################
## Die Tabelle health_bronze wird anhand des Werts der Variablen target erstellt.
## development - die DEV-CSV importieren
## stage - die STAGE-CSV importieren
## production - die täglichen CSV-Dateien aus unserem Produktions-Quell-Volume importieren


## Einfache Expectations für die Bronze-Tabelle
valid_rows = {
        "not_null_pii": "PII IS NOT NULL", 
        "valid_date": "date IS NOT NULL"
    }

@dp.table(
    comment = "This table will be used to ingest the raw CSV files and add metadata columns to the bronze table.",
    table_properties = {"quality": "bronze"}
)

## Prozess fehlschlagen lassen, wenn die Expectation nicht erfüllt ist
@dp.expect_all_or_fail(valid_rows)

def health_bronze():
    return (
        spark
        .readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header","true")
        .schema(project_functions.get_health_csv_schema())   ## Das von uns erstellte benutzerdefinierte Schema verwenden
        .load(raw_data_path)   ## <--------------- Pfad basiert auf dem gesetzten Konfigurationsparameter (DEV, STAGE, PROD)
        .select(
            "*",
            "_metadata.file_name",
            "_metadata.file_modification_time",
            F.current_timestamp().alias("processing_time")
            )
    )

####################################################
## B. Silver Table
####################################################
@dp.table(
    comment = "This table will create, drop and categorize columns from the bronze table.",
    table_properties = {"quality": "bronze"}
)
def health_silver():
    return (
        dp
        .read_stream("health_bronze")
        .withColumn("HighCholest_Group", project_functions.high_cholest_map("HighCholest"))  # UDF - highcholest_map 
        .withColumn("Age_Group", project_functions.group_ages_map("Age"))                   # UDF - group_ages_map Age
        .drop("file_name", "file_modification_time", "processing_time")         # Nicht benötigte Metadatenspalten entfernen
    )
```
