



```python
# Import necessary libraries
from pyspark.sql import functions as F

# Die Daten laden und eine neue Spalte namens trip_distance_km erstellen
new_taxi = (spark
            .read
            .table("samples.nyctaxi.trips")
            .withColumn("trip_distance_km", F.round(F.col("trip_distance") * 1.60934, 2))
        )


## Upper case all columns
new_taxi = new_taxi.select([F.col(col).alias(col.upper()) for col in new_taxi.columns])


## Die Tabelle in Ihrem Katalog speichern
(new_taxi
 .write
 .mode('overwrite')
 .saveAsTable(f'{DA.catalog_name}.default.nyc_lab_solution_table')
)

## Die finale Tabelle anzeigen
display(spark.table(f'{DA.catalog_name}.default.nyc_lab_solution_table'))
```

## C. Den PySpark-Code modularisieren

```python
## convert_miles_to_km
def convert_miles_to_km(df, new_column_name, miles_column):
    return df.withColumn(new_column_name, F.round(F.col(miles_column) * 1.60934, 2))

## uppercase_columns_names
def uppercase_columns_names(df):
    return df.select([F.col(col).alias(col.upper()) for col in df.columns])
```

```python
## Load table
df = load_data("samples.nyctaxi.trips")

## Convert miles to km
df = convert_miles_to_km(df, new_column_name = "trip_distance_km", miles_column = "trip_distance")

## Upcase column
df = uppercase_columns_names(df)

## Den DataFrame als Tabelle in Ihrem Katalog speichern
save_to_catalog(df, catalog_name = DA.catalog_name, schema_name="default", table_name = "my_lab_table")
```

Führen Sie die folgende Zelle aus, um zu testen, ob die ursprünglich in Zelle 11 erstellte Tabelle (**nyc_lab_solution_table**) mit Ihrer neuen, durch die obigen Funktionen erstellten Tabelle (**my_lab_table**) identisch ist. Der Test verwendet die PySpark-Methode `assertDataFrameEqual`.

Falls ein Fehler auftritt, bedeutet das, dass die ursprüngliche Tabelle nicht mit Ihrer neuen Tabelle übereinstimmt und Sie Ihre Funktionen korrigieren müssen.

```python
from pyspark.testing.utils import assertDataFrameEqual

# Die Tabellen lesen (Lösung und die von Ihnen erstellte Tabelle)
solution_df = spark.read.table(f"{DA.catalog_name}.default.nyc_lab_solution_table")
user_df = spark.read.table(f"{DA.catalog_name}.default.my_lab_table")

# Mit assertDataFrameEqual die beiden Tabellen vergleichen. Bei Unterschieden einen Fehler zurückgeben.
assertDataFrameEqual(solution_df, user_df)

print("The tables are identical! Functions were created correctly.")
```
