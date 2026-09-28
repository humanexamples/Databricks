```python
## Diese Datei muss von pytest ausgeführt werden. Wenn Sie die .py-Datei hier ausführen, wird ein Fehler zurückgegeben.
import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, DoubleType
from pyspark.testing.utils import assertDataFrameEqual


## Die Funktionen aus src > helpers importieren
from src_lab.lab_functions import transforms


## Definiert die Spark-Session, die vor den Testfunktionen ausgeführt wird
@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder.getOrCreate()
    
    yield spark



def test_uppercase_columns_function(spark):

    ## Fake DataFrame with random column names
    data = [(1, 5.0, 1, 1, 1, 1)]
    columns = ["id", "trip_distance", "My_Column", "WithNumbers123", "WithSymbolX@#", "With Space"]
    df = spark.createDataFrame(data, columns)

    ## Apply function and return column names
    actual_df = transforms.uppercase_columns_names(df)
    actual_columns = actual_df.columns

    ## Expected column names
    expected_columns = ['ID', 'TRIP_DISTANCE', 'MY_COLUMN', 'WITHNUMBERS123', 'WITHSYMBOLX@#', "WITH SPACE"]

    ## Perform tests
    assert actual_columns == expected_columns, 'Test Passed!'




def test_convert_miles_to_km_function(spark):
    # Prepare a DataFrame with sample data
    data = [(1.0,), (5.5,), (None,)]
    schema = StructType([
        StructField("trip_distance_miles", DoubleType(), True)  # Allow null values by setting nullable=True
    ])
    actual_df = spark.createDataFrame(data, schema)


    ## Die Funktion auf die Beispieldaten anwenden und den tatsächlichen DataFrame speichern
    actual_df = transforms.convert_miles_to_km(df = actual_df, 
                                                new_column_name="trip_distance_km",   ## Name der neuen Spalte
                                                miles_column="trip_distance_miles")   ## Name der Quellspalte in Meilen


    ## Einen DataFrame mit den erwarteten Werten erstellen
    data = [
        (1.0, 1.61),   # Row with values
        (5.5, 8.85),   # Row with values
        (None, None) # Row with null values
    ]

    ## Define schema (optional but recommended for clarity)
    schema = StructType([
        StructField("trip_distance_miles", DoubleType(), True),
        StructField("trip_distance_km", DoubleType(), True)
    ])

    ## Create expected DataFrame
    expected_df = spark.createDataFrame(data, schema)


    ## Den tatsächlichen und den erwarteten DataFrame mit assertDataFrameEqual vergleichen
    assertDataFrameEqual(actual_df,expected_df), 'Test Passed!'
```
