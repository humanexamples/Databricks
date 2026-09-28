# 11 Lab – Unit-Tests erstellen und ausführen


**Code in der Datei transforms.py:**
```python
from pyspark.sql import functions as F


def convert_miles_to_km(df, new_column_name, miles_column):
    return df.withColumn(new_column_name, F.round(F.col(miles_column) * 1.60934, 2))


def uppercase_columns_names(df):
    return df.select([F.col(col).alias(col.upper()) for col in df.columns])
```

```python
from src_lab.lab_functions import transforms
```

---

Vervollständigen Sie die Unit-Test-Funktion `test_uppercase_columns_function`, um die eigene Funktion `transforms.uppercase_column_names()` zu testen.

**LÖSUNG:** Die Lösung finden Sie in der Datei **[./tests_lab/lab_unit_test_solution.md]($./tests_lab/lab_unit_test_solution.md)**.

---

```python
def test_uppercase_columns_function():

    ## Fake DataFrame with random column names
    data = [(1, 5.0, 1, 1, 1, 1)]
    columns = [
        "id", "trip_distance", "My_Column", "WithNumbers123", "WithSymbolX@#", "With Space"]
    df = spark.createDataFrame(data, columns)

    actual_df = transforms.uppercase_columns_names(df)
    actual_columns = actual_df.columns

        ## Expected column names
    expected_columns = [
        'ID', 'TRIP_DISTANCE', 'MY_COLUMN', 'WITHNUMBERS123', 'WITHSYMBOLX@#', "WITH SPACE"]

    ## Perform tests
    assert actual_columns == expected_columns, 'Test Passed!'
    
    print('Test Passed!')
    
## Den Unit-Test ausführen
test_uppercase_columns_function()
```

---

```python
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, DoubleType
from pyspark.testing.utils import assertDataFrameEqual


def test_convert_miles_to_km_function():
    # Prepare a DataFrame with sample data
    data = [(1.0,), (5.5,), (None,)]
    schema = StructType([
        StructField("trip_distance_miles", DoubleType(), True)  # Setting nullable=True
    ])
    actual_df = spark.createDataFrame(data, schema)


    ## Die Funktion auf die Beispieldaten anwenden und den tatsächlichen DataFrame speichern
    actual_df = transforms.convert_miles_to_km(
        df = actual_df, 
        new_column_name="trip_distance_km",   ## Name der neuen Spalte
        miles_column="trip_distance_miles")   ## Name der Quellspalte in Meilen


    ## Mit StructField einen erwarteten DataFrame mit definiertem Schema erstellen 
    data = [
        (1.0, 1.61),   # Row with values
        (5.5, 8.85),   # Row with values
        (None, None) # Row with null values
    ]

    ## Define schema
    schema = StructType([
        StructField("trip_distance_miles", DoubleType(), True),
        StructField("trip_distance_km", DoubleType(), True)
    ])

    ## Create expected DataFrame
    expected_df = spark.createDataFrame(data, schema)


    ## Den tatsächlichen und den erwarteten DataFrame mit assertDataFrameEqual vergleichen
    assertDataFrameEqual(actual_df, expected_df)
    print('Test Passed!')


## Den Unit-Test ausführen
test_convert_miles_to_km_function()
```

---

```python
!pip install pytest==8.3.4
```

---

Wenn Sie für die Challenge Ihre eigene **.py**-Datei erstellen, können Sie die autoreload-Erweiterung aktivieren, um importierte Module automatisch neu zu laden, sodass die Befehlsausführungen diese Aktualisierungen übernehmen, während Sie sie in der .py-Datei vornehmen. Verwenden Sie die folgenden Befehle in einer beliebigen Notebook-Zelle oder Python-Datei, um die autoreload-Erweiterung zu aktivieren.

```python
%load_ext autoreload
%autoreload 2
```

Führen Sie `pytest` für die Datei **./tests_lab/lab_unit_test_solution.py** aus. Führen Sie die Zelle aus und bestätigen Sie, dass beide Unit-Tests bestehen.

```python
import pytest
import sys

sys.dont_write_bytecode = True

# Parameter-Erklärung:
# ".../..": Pfad zur Testdatei, die ausgeführt wird.
# "-v": Zeigt detaillierte Testergebnisse an.
# "-p", "no:cacheprovider": verhindert die Verwendung des Cache.
retcode = pytest.main(["./tests_lab/lab_unit_test_solution.py", "-v", "-p", "no:cacheprovider"])

assert retcode == 0, "The pytest invocation failed. See the log for details."
```
