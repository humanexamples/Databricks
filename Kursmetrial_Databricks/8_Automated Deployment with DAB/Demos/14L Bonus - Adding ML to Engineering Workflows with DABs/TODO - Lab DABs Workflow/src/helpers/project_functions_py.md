# 14L Bonus - Adding ML to Engineering Workflows with DABs/TODO - Lab DABs Workflow/src/helpers/project_functions.py

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType
from pyspark.sql.functions import when, col


# Funktion zur Definition des Schemas für die Gesundheitsdaten-CSV
def get_health_csv_schema():
    """
    Gibt das Schema für die Gesundheitsdaten-CSVs zurück.

    Diese Funktion definiert die Struktur der CSV-Dateien mit gesundheitsbezogenen Daten. 

    Returns:
        StructType: Das Schema, das die Datentypen für jede Spalte der CSV definiert.
    """
    return StructType([
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



def high_cholest_map(col_name: str):
    """
    Ordnet einem Cholesterinwert eine kategoriale Bezeichnung zu.

    Diese Funktion wandelt eine numerische Spalte mit Cholesterinwerten 
    anhand vordefinierter Bereiche in eine kategoriale Bezeichnung um:
        - 0 -> 'Normal'
        - 1 -> 'Above Average'
        - 2 -> 'High'
        - Jeder andere Wert -> 'Unknown'

    Args:
        col_name (str): Der Name der zu transformierenden Spalte.

    Returns:
        pyspark.sql.column.Column: Eine neue Spalte mit kategorialen Bezeichnungen.
    """
    return (
        when(col(col_name) == 0, 'Normal')
        .when(col(col_name) == 1, 'Above Average')
        .when(col(col_name) == 2, 'High')
        .otherwise('Unknown')
    )

    

def group_ages_map(col_name: str):
    """
    Ordnet einem Alterswert eine Altersgruppe zu.

    Diese Funktion wandelt eine numerische Spalte mit Alterswerten 
    anhand vordefinierter Bereiche in kategoriale Altersgruppen um:
        - 0-9 -> "0-9"
        - 10-19 -> "10-19"
        - 20-29 -> "20-29"
        - 30-39 -> "30-39"
        - 40-49 -> "40-49"
        - 50+ -> "50+"
        - Jeder andere Wert -> "Unknown"

    Args:
        col_name (str): Der Name der zu transformierenden Spalte.

    Returns:
        pyspark.sql.column.Column: Eine neue Spalte mit kategorisierten Altersgruppen.
    """
    return (
        when((col(col_name) >= 0) & (col(col_name) <= 9), "0-9")  # Alter zwischen 0-9 -> Bezeichnung "0-9"
        .when((col(col_name) >= 10) & (col(col_name) <= 19), "10-19")  # Alter zwischen 10-19 -> Bezeichnung "10-19"
        .when((col(col_name) >= 20) & (col(col_name) <= 29), "20-29")  # Alter zwischen 20-29 -> Bezeichnung "20-29"
        .when((col(col_name) >= 30) & (col(col_name) <= 39), "30-39")  # Alter zwischen 30-39 -> Bezeichnung "30-39"
        .when((col(col_name) >= 40) & (col(col_name) <= 49), "40-49")  # Alter zwischen 40-49 -> Bezeichnung "40-49"
        .when(col(col_name) >= 50, "50+")  # Alter 50 oder älter -> Bezeichnung "50+"
        .otherwise('Unknown')  # Jeder andere Alterswert -> Bezeichnung "Unknown"
    )
```
