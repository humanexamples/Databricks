# Reading Files

```python
-- Databricks SQL function read_files

SELECT * 
FROM read_files(
  '/Volumes/dbacademy_ecommerce/v01/raw/users-historical',
  format => 'parquet'
)
LIMIT 10;
```

```python
# Reading parquet with Apache Spark API
df = (spark
      .read
      .format("parquet")
      .load("/Volumes/dbacademy_ecommerce/v01/raw/users-historical")
    )
```

```python
# Reading CSV 

SELECT *
FROM read_files(
  '/Volumes/dbacademy/' || DA.schema_name || '/csv_files_autoloader_source',
  format => 'CSV',
  sep => '|',
  header => true
);
```

```python
spark.sql(f'''
    SELECT *
    FROM text.`{DA.paths.working_dir}/csv_demo_files/malformed_example_1_data.csv`
''').display()
```

# Write Files

```python
SELECT * FROM text.`<FILL-IN>`;
```

```python
# Write with Apache Spark API

(df
 .write
 .mode("overwrite")
 .saveAsTable(f"dbacademy.{DA.schema_name}.historical_users_bronze_python")
)
```
