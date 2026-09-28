# 06L - Deploy a Simple DAB/src/our_project_code.sql

*(Databricks-Notebook, konvertiert nach Markdown)*

```python
my_catalog = dbutils.widgets.get('catalog_name')
target = dbutils.widgets.get('display_target')

set_default_catalog = spark.sql(f'USE CATALOG {my_catalog}')

print(f'Using the {my_catalog} catalog.')
print(f'Deploying as the {target} pipeline.')
```

```sql
DROP TABLE IF EXISTS nyctaxi_bronze;

CREATE TABLE nyctaxi_bronze AS
SELECT 
  *,
  _metadata.file_modification_time as file_modification_time,
  _metadata.file_name as file_name
FROM nyctaxi_raw
```

```sql
SELECT * 
FROM nyctaxi_bronze 
LIMIT 10;
```

```sql
DROP TABLE IF EXISTS nyctaxi_silver;

CREATE TABLE nyctaxi_silver AS
SELECT 
  * EXCEPT (file_modification_time, file_name),
  round(try_divide(fare_amount,trip_distance),2) AS price_per_mile
FROM nyctaxi_bronze;
```

```sql
SELECT * 
FROM nyctaxi_silver;
```
