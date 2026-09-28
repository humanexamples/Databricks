# 14L Bonus - Adding ML to Engineering Workflows with DABs/Solution - Lab DABs Workflow/tests/unit_tests/test_spark_helper_functions.py

```python
##
## Die Datei importiert pytest und eine Reihe weiterer PySpark-Pakete.
##
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType, LongType
from pyspark.sql.functions import when, col
from pyspark.testing.utils import assertDataFrameEqual, assertSchemaEqual


## Diese Datei muss von pytest ausgeführt werden. Wenn Sie die .py-Datei hier direkt ausführen, wird ein Fehler zurückgegeben. Sie müssen den Pfad zu den Modulen src.helpers mit sys.path.append(sys.path.append('/path/to/file')) hinzufügen
## Die Funktionen aus src > helpers importieren
from src.helpers import project_functions


# Dies ist eine pytest-Fixture, die eine Spark-Session für die Tests einrichtet.
# Die Fixture heißt 'spark' und wird einmal pro Testsitzung eingerichtet.
@pytest.fixture(scope="session")
def spark():
    # Eine Spark-Session erstellen. Falls bereits eine existiert, wird sie wiederverwendet.
    spark = SparkSession.builder.getOrCreate()
    
    # Die Spark-Session an die Testfunktion übergeben.
    yield spark
    # Nach dem Test können Sie bei Bedarf Aufräumcode hinzufügen.



def test_get_health_csv_schema_match():
    # Das erwartete Schema definieren, das die Funktion zurückgeben soll, und damit testen
    # Dies ist das Referenzschema, mit dem die Ausgabe der Funktion verglichen wird.
    # Ändert sich das Verhalten der Funktion, schlägt der Test fehl, wenn das Schema nicht übereinstimmt.
    expected_schema = StructType([
        StructField("ID", IntegerType(), True),
        StructField("PII", StringType(), True),
        StructField("date", DateType(), True),
        StructField("HighCholest", IntegerType(), True),
        StructField("HighBP", DoubleType(), True),
        StructField("BMI", DoubleType(), True),
        StructField("Age", DoubleType(), True),
        StructField("Education", DoubleType(), True),
        StructField("income", IntegerType(), True)
    ])

    # Die Funktion aufrufen, die das Schema für die Gesundheits-CSV liefert.
    # Sie sollte ein Schema zurückgeben, das gegen das erwartete Schema validiert wird.
    actual_schema = project_functions.get_health_csv_schema()

    # Prüfen, dass das von der Funktion zurückgegebene tatsächliche Schema dem erwarteten Schema entspricht.
    # Stimmen die Schemas nicht überein, schlägt der Test fehl und weist auf ein Problem mit der Ausgabe der Funktion hin.
    assertSchemaEqual(actual_schema, expected_schema)




def test_high_cholest_column_valid_map(spark):
    # Die Beispieldaten definieren und einen Spark DataFrame zum Testen erstellen
    data = [
        (0,),
        (1,), 
        (2,), 
        (3,), 
        (4,), 
        (None,)
    ]
    sample_df = spark.createDataFrame(data, ["value"])

    # Die Transformation auf die Beispieldaten anwenden
    actual_df = sample_df.withColumn("actual", project_functions.high_cholest_map("value")) ## das Modul vor der Funktion angeben

    # Einen statischen DataFrame mit den erwarteten Ergebnissen der obigen Funktion highcholest_map erstellen. Wird highcholest_map geändert und liefert diese Ergebnisse nicht mehr, wird ein Fehler zurückgegeben
    expected_df = spark.createDataFrame(
        [
            (0, "Normal"),
            (1, "Above Average"),
            (2, "High"),
            (3, "Unknown"),
            (4, "Unknown"),
            (None, "Unknown")
        ],
        schema=StructType([
            StructField("value", LongType(), True),
            StructField("actual", StringType(), True)
        ])
    )

    ## Prüfen, dass die Spalte im Beispiel-DataFrame und im erwarteten DataFrame identisch ist. Sind sie nicht gleich, wird ein Fehler zurückgegeben.
    assertDataFrameEqual(actual_df.select(col('value')), expected_df.select(col('value')))




def test_age_group_column_valid_map(spark):
    # Die Beispieldaten definieren und einen Spark DataFrame zum Testen erstellen
    data = [
        (0,),
        (9,), 
        (10,), 
        (20,), 
        (30,), 
        (40,),
        (50,), 
        (60,),
        (-1,), 
        (None,)
    ]
    sample_df = spark.createDataFrame(data, ["value"])

    # Die Transformation auf die Beispieldaten anwenden
    actual_df = sample_df.withColumn("actual", project_functions.group_ages_map("value"))  ## das Modul vor der Funktion angeben

    # Einen statischen DataFrame mit den erwarteten Ergebnissen der obigen Funktion highcholest_map erstellen. Wird highcholest_map geändert und liefert diese Ergebnisse nicht mehr, wird ein Fehler zurückgegeben
    data = [
        (0, "0-9"),
        (9, "0-9"),
        (10, "10-19"),
        (20, "20-29"),
        (30, "30-39"),
        (40, "40-49"),
        (50, "50+"),
        (60, "50+"),
        (-1, "Unknown"),
        (None, "Unknown")  # Nullwert
    ]

    # Das Schema des DataFrames definieren
    schema = StructType([
        StructField("value", LongType(), True),
        StructField("actual", StringType(), True)
    ])

    # Den DataFrame erstellen
    expected_df = spark.createDataFrame(data, schema)

    ## Prüfen, dass die Spalte im Beispiel-DataFrame und im erwarteten DataFrame identisch ist. Sind sie nicht gleich, wird ein Fehler zurückgegeben.
    assertDataFrameEqual(actual_df.select(col('value')), expected_df.select(col('value')))
```
