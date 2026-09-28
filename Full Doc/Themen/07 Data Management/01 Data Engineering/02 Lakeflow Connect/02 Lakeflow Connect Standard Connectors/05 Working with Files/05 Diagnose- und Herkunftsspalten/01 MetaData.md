```python
-- Drop the table if it exists for demonstration purposes
DROP TABLE IF EXISTS historical_users_bronze;


-- Create an empty table
CREATE TABLE historical_users_bronze AS
SELECT
  *,
  _metadata.file_modification_time AS file_modification_time,      -- Last data source file modification time
  _metadata.file_name AS source_file,                              -- Ingest data source file name
  current_timestamp() as ingestion_time                            -- Ingestion timestamp
FROM read_files(
  "/Volumes/dbacademy_ecommerce/v01/raw/users-historical",
  format => 'parquet');


-- View the final bronze table
SELECT * FROM historical_users_bronze LIMIT 10;
```

```python
from pyspark.sql.functions import col, from_unixtime, current_timestamp
from pyspark.sql.types import DateType

# 1. Read parquet files in cloud storage into a Spark DataFrame
df = (spark
      .read
      .format("parquet")
      .load("/Volumes/dbacademy_ecommerce/v01/raw/users-historical")
    )


# 2. Add metadata columns
df_with_metadata = (
    df.withColumn("file_modification_time", col("_metadata.file_modification_time"))
      .withColumn("source_file", col("_metadata.file_name"))
      .withColumn("ingestion_time", current_timestamp())
)


# 3. Save as a Delta table
(df_with_metadata
 .write
 .format("delta")
 .mode("overwrite")
 .saveAsTable(f"dbacademy.{DA.schema_name}.historical_users_bronze_python_metadata")
)


# 4. Read and display the table
historical_users_bronze_python_metadata = spark.table(f"dbacademy.{DA.schema_name}.historical_users_bronze_python_metadata")

display(historical_users_bronze_python_metadata)
```
