
Wir wandeln traditionellen Apache-Spark-ETL-Code in eine modularere, wartbarere und besser testbare Struktur um.

Schauen wir uns kurz eine typische Codestruktur an, um Daten zu ingestieren und eine Bronze-, Silber- und Gold-Tabelle zu erstellen.

### Wir gehen nicht tief auf den PySpark- und SQL-Code unten ein, da er Ihnen vertraut sein sollte.

```python
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType
from pyspark.sql.functions import when, col, current_timestamp

##
## CSV -> Bronze
##

# Den Pfad zur CSV-Datei im DEV-Volume festlegen
csv_path = f'/Volumes/{DA.catalog_name}/default/health'


# Das Schema für die CSV-Datei definieren
health_csv_schema = StructType([
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


# Die CSV-Datei ingestieren und Metadatenspalten für die ingestierten Daten hinzufügen
health_raw = (
    spark
    .read
    .format("csv") 
    .option("header", "true")             # Die Kopfzeile für die Spaltennamen verwenden
    .schema(health_csv_schema)            # Apply the defined schema
    .load(csv_path)                       # Load the CSV data
    .select(
        "*",
        "_metadata.file_name",                        # Include file name from metadata
        "_metadata.file_modification_time",           # Include file modification timestamp
        current_timestamp().alias("processing_time")  # Add a processing time column
    )
)


# Die ingestierten Daten als Bronze-Tabelle im Delta-Format speichern
(health_raw
 .write
 .format("delta")
 .mode('overwrite')  # Overwrite existing data
 .saveAsTable(f"{DA.catalog_name}.default.health_bronze_dev")
)

health_bronze = spark.table(f'{DA.catalog_name}.default.health_bronze_dev')


##
## Bronze -> Silver
##

health_silver = (
    health_bronze
    # Eine neue Spalte zur Kategorisierung der Spalte HighCholest erstellen
    .withColumn(
        "HighCholest_Group", 
        when(col("HighCholest") == 0, 'Normal')
        .when(col("HighCholest") == 1, 'Above Average')
        .when(col("HighCholest") == 2, 'High')
        .otherwise('Unknown')
    )
    # Eine neue Spalte zur Kategorisierung der Spalte Age_Group erstellen
    .withColumn(
        "Age_Group", 
        when(col("Age") <= 9, "0-9")
        .when((col("Age") >= 10) & (col("Age") <= 19), "10-19")
        .when((col("Age") >= 20) & (col("Age") <= 29), "20-29")
        .when((col("Age") >= 30) & (col("Age") <= 39), "30-39")
        .when((col("Age") >= 40) & (col("Age") <= 49), "40-49")
        .when(col("Age") >= 50, "50+")
        .otherwise('Unknown')
    )
    # Drop unnecessary columns (e.g., metadata columns)
    .drop("file_name", "file_modification_time", "processing_time")
)

# Die transformierten Daten als Silber-Tabelle speichern
(health_silver
 .write
 .format("delta")
 .mode("overwrite")  # Overwrite any existing data
 .saveAsTable(f"{DA.catalog_name}.default.health_silver_dev")
)



##
## Silver - Gold
##
chol_age_agg = spark.sql(f'''
    CREATE OR REPLACE TABLE {DA.catalog_name}.default.chol_age_agg_dev AS
    SELECT 
        HighCholest_Group, 
        Age_Group, 
        count(*) as Total
    FROM {DA.catalog_name}.default.health_silver_dev
    GROUP BY HighCholest_Group, Age_Group
''')

## Display the final gold table
spark.table(f'{DA.catalog_name}.default.chol_age_agg_dev').display()
```

---

## C. Den PySpark-Code modularisieren

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType
from pyspark.sql.functions import when, col, current_timestamp


##
## Ingest Cloud to Bronze
##

# a. Funktion zur Definition des Schemas für die Gesundheitsdaten-CSV
def get_health_csv_schema():
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


# b. Funktion, die die CSV-Daten in einen DataFrame liest und Metadatenspalten hinzufügt
def read_health_data(csv_path, schema):
    return (
        spark
        .read
        .format("csv")
        .option("header", "true")  # Die Kopfzeile für die Spaltennamen verwenden
        .schema(schema)            # Apply the defined schema
        .load(csv_path)            # Load the CSV data
        .select(
            "*",
            "_metadata.file_name",                # Include file name from metadata
            "_metadata.file_modification_time",   # Include file modification timestamp
            current_timestamp().alias("processing_time")  # Add a processing time column
        )
    )


##
## Mapping Functions for Data Transformation
##

# c. Die Spalte 'HighCholest' Kategorien zuordnen
def high_cholest_map(col_name):
    return (
        when(col(col_name) == 0, 'Normal')
        .when(col(col_name) == 1, 'Above Average')
        .when(col(col_name) == 2, 'High')
        .otherwise('Unknown')
    )


# d. Die Spalte 'Age' Altersgruppen zuordnen
def group_ages_map(col_name):
    return (
        when(col(col_name) <= 9, "0-9")
        .when((col(col_name) >= 10) & (col(col_name) <= 19), "10-19")
        .when((col(col_name) >= 20) & (col(col_name) <= 29), "20-29")
        .when((col(col_name) >= 30) & (col(col_name) <= 39), "30-39")
        .when((col(col_name) >= 40) & (col(col_name) <= 49), "40-49")
        .when(col(col_name) >= 50, "50+")
        .otherwise('Unknown')
    )


##
## Save a DataFrame to Delta Table
##

# e. Funktion zum Speichern des DataFrames in einer Delta-Tabelle
def save_df_to_delta(dataframe, uc_table, mode):
    (dataframe
     .write
     .format("delta")
     .mode(mode)             # Specify the save mode (e.g., 'overwrite', 'append')
     .saveAsTable(uc_table)  # Den DataFrame als Tabelle speichern
    )


##
## Gold Aggregation
##

# f. Funktion zum Erstellen einer Gold-Tabelle mit aggregierten Anzahlen
def get_cholest_age_agg(catalog, schema, table_name):
    query = f'''
        CREATE OR REPLACE TABLE {catalog}.{schema}.{table_name} AS
        SELECT 
            HighCholest_Group, 
            Age_Group, 
            count(*) as Total
        FROM {catalog}.{schema}.health_silver_dev
        GROUP BY HighCholest_Group, Age_Group
    '''
    return spark.sql(query)
```

---

2. Verwenden Sie die obigen Funktionen, um Ihre Ingest-, Bronze-, Silber- und Gold-Pipeline aufzubauen.

---

```python
##
## CSV to Bronze
##

# Die Gesundheits-CSV-Daten in einen DataFrame lesen und in der Bronze-Tabelle speichern
health_csv_df = read_health_data(
    csv_path = f"/Volumes/{DA.catalog_name}/default/health", 
    schema = get_health_csv_schema()
)

# Die Rohdaten als Bronze-Tabelle im Delta-Format speichern
save_df_to_delta(health_csv_df, f"{DA.catalog_name}.default.health_bronze_dev", mode="overwrite")


##
## Bronze to Silver
##

# Die Daten transformieren, indem neue Spalten hinzugefügt und Metadaten bereinigt werden
health_bronze = spark.table(f'{DA.catalog_name}.default.health_bronze_dev')

silver_df = (
    health_bronze
    # Categorize HighCholest
    .withColumn("HighCholest_Group", high_cholest_map("HighCholest"))
    # Categorize Age
    .withColumn("Age_Group", group_ages_map("Age"))
    # Drop unnecessary metadata columns
    .drop("file_name", "file_modification_time", "processing_time")
)

# Die transformierten Daten als Silber-Tabelle im Delta-Format speichern
save_df_to_delta(silver_df, f"{DA.catalog_name}.default.health_silver_dev", mode="overwrite")


##
## Gold Table
##

# Die Daten auf Gold-Ebene nach Cholesterin- und Altersgruppen aggregieren
get_cholest_age_agg(catalog = DA.catalog_name, schema = 'default', table_name ='chol_age_agg_dev')
```

```python
spark.table(f'{DA.catalog_name}.default.health_bronze_dev').display()

spark.table(f'{DA.catalog_name}.default.health_silver_dev').display()

spark.table(f'{DA.catalog_name}.default.chol_age_agg_dev').display()
```

```python
def delete_demo03_tables(catalog):
    spark.sql(f"DROP TABLE IF EXISTS {catalog}.default.health_bronze_dev")
    spark.sql(f"DROP TABLE IF EXISTS {catalog}.default.health_silver_dev")
    spark.sql(f"DROP TABLE IF EXISTS {catalog}.default.chol_age_agg_dev")

delete_demo03_tables(DA.catalog_name)
```
