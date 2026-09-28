During data ingestion there are times when the input data does not match the schema in your table.

Ingestion techniques like `read_files()`, `spark.read`, or Auto Loader provide a rescued data column during ingestion:

The rescued data column ensures that columns that do not match the schema are **rescued instead of being dropped**
Mismatched values are stored as **JSON-formatted strings** in the _rescued_data column
If a row has no schema mismatches, the _rescued_data column will be null
This preserves all input data and prevents silent data loss

You can define a schema for the `read_files()` function to read in the data with a specific structure.

a. Use the schema option to define the schema. In this case, we'll read in the following:

    - order_id as `INT`
    - email as `STRING`
    - transactions_timestamp as `BIGINT`
b. Use the `rescuedDataColumn` option to collect all data that can’t be parsed due to data type mismatches or schema mismatches into a separate column for review.

Run the cell and review the results. Notice that row 1 (aaa) could not be read using the defined schema, so it was placed in the **_rescued_data** column. Keeping rows that don’t conform to the schema allows you to inspect and process them as needed.

NOTE: Defining a schema when using `read_files` in Databricks improves performance by skipping the expensive schema inference step and ensures consistent, reliable data parsing. It's especially beneficial for large or semi-structured datasets.

```python
SELECT *
FROM read_files(
        DA.paths_working_dir || '/csv_demo_files/malformed_example_1_data.csv',
        format => "csv",
        sep => "|",
        header => true,
        schema => '''
            order_id INT, 
            email STRING, 
            transactions_timestamp BIGINT''', 
        rescueddatacolumn => '_rescued_data'    -- Create the _rescued_data column
      );
```

```python
-- COMPLETE THE QUERY BELOW TO CLEAN UP THE _RESCUED_DATA column to create the price_fixed column
CREATE TABLE 10_lab_challenge
SELECT
  item_id,
  name,
  price,
  <FILL-IN> AS price_fixed,   -- CLEAN the rescued data column and return it as a numeric value with the other prices
  _rescued_data,
  _metadata.file_modification_time AS file_modification_time,
  _metadata.file_name AS source_file, 
  current_timestamp() as ingestion_timestamp
FROM read_files(
        DA.paths_working_dir || '/csv_demo_files/lab_malformed_data.csv',
        format => "csv",
        sep => ",",
        header => true,
        schema => 'item_id STRING, name STRING, price DOUBLE', 
        rescueddatacolumn => "_rescued_data"
      );
```

# Extract Values from _rescued_data column

The _rescued_data column is a JSON-formatted string. We won’t go into detail on how to handle this type of data here, as it will be covered in a later demo and lab.

However, it's important to note that you can extract values from the _rescued_data column and add them to your bronze table. To obtain the value from the _c0 field, you can use the _rescued_data:_c0 syntax, as shown in the next cell.

```python
SELECT
  cast(_rescued_data:_c0 AS BIGINT) AS order_id,
  *
FROM read_files(
        DA.paths_working_dir || '/csv_demo_files/malformed_example_2_data.csv',
        format => "csv",
        sep => "|",
        header => true
      )
```
