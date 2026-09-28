# 13 Demo - Continuous Integration and Continuous Deployment with DABs/Full Project/tests/integration_test/integration_tests_dlt.py

*(Databricks-Notebook, konvertiert nach Markdown)*

# Integrationstests für Spark Declarative Pipelines mit Expectations

**HINWEIS:** DLT wurde in **Spark Declarative Pipelines** umbenannt

Diese Pipeline ist eine einfache Beispiel-Pipeline, die anhand eines einfachen Projekts einige Integrationsprüfungen mit Expectations enthält, um die Grundlagen zu vermitteln. Es gibt weitere Expectations, die Sie setzen, oder Unit-Tests, die Sie erstellen können, um das Projekt zu optimieren, aber wir halten es einfach.

Weitere Informationen finden Sie in den folgenden Ressourcen.

- [Manage data quality with pipeline expectations](https://docs.databricks.com/en/delta-live-tables/expectations.html#manage-data-quality-with-pipeline-expectations)

- [Expectation recommendations and advanced patterns](https://docs.databricks.com/en/delta-live-tables/expectation-patterns.html#expectation-recommendations-and-advanced-patterns)

- [Applying software development & DevOps best practices to Delta Live Table pipelines](https://www.databricks.com/blog/applying-software-development-devops-best-practices-delta-live-table-pipelines)

## Die Konfigurationsvariable für die Zielumgebung abrufen
Dieser Pfad verwendet die Konfigurationsvariable, die in der Pipeline für **development, stage und production** gesetzt ist.

- Ist das Ziel **development** oder **stage**, werden alle Integrationstests ausgeführt. 
- Ist das Ziel **production**, wird nur der Integrationstest für die Gold-Tabelle ausgeführt.

```python
import dlt

## Die Zielumgebung der Konfiguration in der Variablen target speichern
target = spark.conf.get("target")
```

### Ein Dictionary für die Werte der Integrationstests erstellen

Erstellen Sie ein Dictionary mit den für die Integrationstests benötigten Werten sowohl für die Umgebung **development** als auch für **stage**. Es gibt mehrere Ansätze dafür, dies ist eine einfache Methode.

Weitere Informationen finden Sie in der Dokumentation [Portable and Reusable Expectations](https://docs.databricks.com/en/delta-live-tables/expectation-patterns.html#portable-and-reusable-expectations).

```python
## Je nach bereitgestelltem Ziel die spezifischen Validierungskennzahlen für die Tabellen abrufen.
target_integration_tests_validation = {
    'development': {
        'health_bronze': {
            'total_rows': 7500
        },
        'health_silver': {
            'total_rows': 7500
        }
    },
    'stage': {
        'health_bronze': {
            'total_rows': 35000
        },
        'health_silver': {
            'total_rows': 35000
        }
    }
}


## Die erwarteten Werte für die Gesamtzeilenzahl der Tabellen je nach Ziel (development oder stage) in den Variablen speichern
if target in ('development', 'stage'):
    total_expected_bronze = target_integration_tests_validation[target]['health_bronze']['total_rows']
    total_expected_silver = target_integration_tests_validation[target]['health_silver']['total_rows']
```

### Eine Funktion erstellen, die die Gesamtzahl der Zeilen einer Tabelle zählt
Die Funktion `test_count_table_total_rows` erstellt eine Materialized View, die die Gesamtzahl der Zeilen in der angegebenen Tabelle zählt.

```python
def test_count_table_total_rows(table_name, total_count, target):
    '''
    Count the number of rows in the specified table and compare with the expected values for development and stage data. 
    Fail the update if the count does not match the specified values.
    '''
    @dlt.table(
        name=f"TEST_{target}_{table_name}_total_rows_verification",
        comment=f"Confirms all rows were ingested from the {target} raw data to {table_name}"
    )

    @dlt.expect_all_or_fail({"valid count": f"total_rows = {total_count}"}) 

    def count_table_total_rows():
        return spark.sql(f"""
            SELECT COUNT(*) AS total_rows FROM LIVE.{table_name}
        """)
```

### Eine Funktion erstellen, die die Spaltenwerte in der Gold-Materialized-View bestätigt
Die Funktion `test_gold_table_columns` erstellt eine Materialized View, die die Werte in den Spalten **Age_Group** und **HighCholest_Group** in **chol_age_agg** prüft.

```python
def test_gold_table_columns():
    '''
    Diese Funktion prüft die eindeutigen Werte in den Spalten Age_Group und HighCholest_Group der Gold-Tabelle chol_age_agg.

    Damit wird bestätigt, dass die unterschiedlichen Werte dieser Spalten in der Gold-Tabelle korrekt sind.
    ''' 
    ## Expectations für die Spalten festlegen
    check_silver_calc_columns = {
        "valid age group": "Age_Group in ('0-9', '10-19', '20-29', '30-39', '40-49', '50+', 'Unknown')",
        "valid cholest group": "HighCholest_Group in ('Normal', 'Above Average', 'High', 'Unknown')"
    }

    @dlt.table(comment="Check age group and high cholest group in the gold table")

    ## Fehlschlagen, wenn die Expectations nicht erfüllt sind
    @dlt.expect_all_or_fail(check_silver_calc_columns)

    def test_calculated_columns_age_cholesterol():
        return (dlt
                .read("chol_age_agg")
                .select("Age_Group", "HighCholest_Group")
            )
```

### Die angegebenen Integrationstests ausführen
Führen Sie die angegebenen Integrationstests abhängig von der Zielumgebung aus.

```python
## Die angegebenen Tests abhängig von der Zielumgebung ausführen (development, stage oder production)

if target in ('development','stage'):  ## Dynamischer Integrationstest für Dev- oder Stage-Tabellen
    test_count_table_total_rows('health_bronze',  total_expected_bronze, target)
    test_count_table_total_rows('health_silver',  total_expected_silver, target)
    test_gold_table_columns()
elif target == 'production':  ## In der Produktion nur die Gold-Tabelle testen
    test_gold_table_columns()
```
