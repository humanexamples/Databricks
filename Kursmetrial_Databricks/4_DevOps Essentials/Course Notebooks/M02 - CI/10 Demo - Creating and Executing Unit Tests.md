# 10 - Unit-Tests erstellen und ausführen

Ein Unit-Test ist eine Art von Softwaretest, die sich darauf konzentriert, die kleinsten Teile einer Anwendung zu überprüfen, typischerweise einzelne Funktionen oder Methoden isoliert. 

Benennen Sie die Testfunktion mit dem Schlüsselwort `test_` gefolgt von einer Beschreibung dessen, was Sie testen.  

**c. Die Unit-Test-Funktionen ausführen**  
Führen Sie den Test mit einem Test-Framework wie `pytest` aus und überprüfen Sie ihn. Überprüfen Sie die Ergebnisse, um sicherzustellen, dass sich die Funktion wie erwartet verhält, und beheben Sie Probleme, falls der Test fehlschlägt.

**HINWEIS:** Es gibt viele verfügbare Frameworks, die Sie verwenden können. Wir verwenden in diesem Kurs `pytest`. Das von Ihnen gewählte Framework sollte mit Ihrem Team oder Ihrer Organisation abgestimmt werden.



**HINWEIS:** `sys.path.append()` fügt den Pfad des Root-Ordners zum Systempfad hinzu (dadurch können Sie Module aus diesem Ordner importieren).

---

```python
# Fügt das übergeordnete Verzeichnis des aktuellen Arbeitsverzeichnisses zum Python-Suchpfad hinzu
import sys
import os

# Get the current working directory
current_path = os.getcwd()

# Den Pfad des Root-Ordners ermitteln, indem vom aktuellen Pfad zwei Ebenen nach oben navigiert wird
root_folder_path = os.path.dirname(os.path.dirname(current_path))

# Den Pfad des Root-Ordners zum Systempfad hinzufügen (so können Module aus diesem Ordner importiert werden)
sys.path.append(root_folder_path)

# Eine Meldung ausgeben, die bestätigt, dass der Root-Ordner zu sys.path hinzugefügt wurde
print(f'Add the following path: {root_folder_path}')
```

---

```python
## Import the custom functions
from src.helpers import project_functions
```

---

```python
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType, LongType
from pyspark.sql.functions import when, col

from pyspark.testing.utils import assertSchemaEqual

def test_get_health_csv_schema_match():

    # Das Schema aus unserer Funktion abrufen
    actual_schema = project_functions.get_health_csv_schema()
    
    # Das erwartete Schema definieren, das die Funktion zurückgeben soll. Wird die Funktion während der Entwicklung geändert, erkennt der Unit-Test den Fehler und schlägt fehl.
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

    # Prüfen, dass das tatsächliche Schema dem erwarteten Schema entspricht
    assertSchemaEqual(actual_schema, expected_schema)
    print('Test passed!')

test_get_health_csv_schema_match()
```

---

```python
## assertDataFrameEqual importieren, um Ihre DataFrames zu vergleichen
from pyspark.testing.utils import assertDataFrameEqual

def test_high_cholest_column_valid_map():

    # Den Beispiel-DataFrame zum Testen der Funktion erstellen
    data = [(0,),(1,),(2,),(None,)]
    sample_df = spark.createDataFrame(data, ["value"])

    # Die Funktion auf die Beispieldaten anwenden
    actual_df = sample_df.withColumn("actual", project_functions.high_cholest_map("value"))

    # Einen statischen DataFrame mit den erwarteten Ergebnissen der Funktion highcholest_map erstellen
    expected_df = spark.createDataFrame(
        [(0, "Normal"),(1, "Above Average"),(2, "High"),(None, "Unknown")],
        schema=StructType([
            StructField("value", LongType(), True),
            StructField("actual", StringType(), True)
        ])
    )


    assertDataFrameEqual(actual_df, expected_df)
    print('Test passed!')

test_high_cholest_column_valid_map()
```

---

```python
################################################################################
## Die Zelle verursacht einen Fehler, weil der tatsächliche df nicht dem erwarteten df entspricht
################################################################################

def test_high_cholest_column_invalid_map():

    # Den Beispiel-DataFrame erstellen, an dem die Funktion getestet wird
    data = [
        (0,),
        (1,), 
        (2,), 
        (3,), 
        (4,), 
        (None,)
    ]
    sample_df = spark.createDataFrame(data, ["value"])

    # Die Funktion auf die Beispieldaten anwenden
    actual_df = sample_df.withColumn("actual", project_functions.high_cholest_map("value"))

    # Einen statischen DataFrame mit den erwarteten Ergebnissen der obigen Funktion highcholest_map erstellen
    expected_df = spark.createDataFrame(
        [
            (0, "Bad Value Cause Error"),     ####### <--- Wert wurde geändert, um einen Fehler zu verursachen
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
    assertDataFrameEqual(actual_df, expected_df)

test_high_cholest_column_invalid_map()
```

---

```python
!pip install pytest==8.3.4
```

---

```python
## Die Module `pytest` und `sys` importieren.
import pytest  
import sys     
import importlib  

sys.dont_write_bytecode = False  

# Das Testmodul neu laden, damit die neuesten Änderungen vor dem Ausführen der Tests übernommen werden
importlib.reload(importlib.import_module('tests.unit_tests.test_spark_helper_functions'))

# pytest mit ausführlicher Ausgabe auf der angegebenen Testdatei ausführen
# Parameter-Erklärung:
# ".../test_spark_helper_functions.py": Pfad zur Testdatei, die ausgeführt wird.
# "-v": Aktiviert den ausführlichen Modus (zeigt detaillierte Testergebnisse an).
# "-p", "no:cacheprovider": verhindert die Verwendung des Cache.
retcode = pytest.main(["../../tests/unit_tests/test_spark_helper_functions.py", "-v", "-p", "no:cacheprovider"])
```


#### Zusätzliche Ressourcen zu Unit-Testing
- [pytest](https://docs.pytest.org/en/stable/)
- [chispa](https://github.com/MrPowers/chispa)
- [nutter](https://github.com/microsoft/nutter)
- [unittest](https://docs.python.org/3/library/unittest.html)
- [Best Practices for Unit Testing PySpark](https://www.youtube.com/watch?v=TbWcCyP2MgE)

