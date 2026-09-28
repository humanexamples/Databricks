```sql
-- Tabelle zu Demonstrationszwecken löschen, falls sie existiert
DROP TABLE IF EXISTS historical_users_bronze;

-- Eine leere Tabelle erstellen
CREATE TABLE historical_users_bronze AS
SELECT
  *,
  cast(from_unixtime(user_first_touch_timestamp / 1000000) AS DATE) AS first_touch_date,
  _metadata.file_modification_time AS file_modification_time,
  _metadata.file_name AS source_file,file name
  current_timestamp() as ingestion_time
FROM read_files(
  "/Volumes/dbacademy_ecommerce/v01/raw/users-historical",
  format => 'parquet');
```

## D. (BONUS) Python-Entsprechung

```python
from pyspark.sql.functions import col, from_unixtime, current_timestamp
from pyspark.sql.types import DateType

df = (spark
      .read
      .format("parquet")
      .load("/Volumes/dbacademy_ecommerce/v01/raw/users-historical")
    )


# 2. Metadatenspalten hinzufügen
df_with_metadata = (
    df.withColumn("first_touch_date", from_unixtime(col("user_first_touch_timestamp") / 1_000_000).cast(DateType()))
      .withColumn("file_modification_time", col("_metadata.file_modification_time"))
      .withColumn("source_file", col("_metadata.file_name"))
      .withColumn("ingestion_time", current_timestamp())
)


# Ohne .format("delta") nutzt Databricks standardmäßig Delta-Lake, solange kein anderes Format konfiguriert wurde. Mit .format("delta") gibst du explizit das Delta-Format an, was mehr Klarheit und Robustheit bietet. Das Ergebnis ist ansonsten gleich.
(df_with_metadata
 .write
 .format("delta")
 .mode("overwrite")
 .saveAsTable(f"{my_catalog}.data_ingestion.historical_users_bronze_python_metadata")
)


# 4. Die Tabelle lesen und anzeigen
historical_users_bronze_python_metadata = spark.table(f"{my_catalog}.data_ingestion.historical_users_bronze_python_metadata")

display(historical_users_bronze_python_metadata)
```
