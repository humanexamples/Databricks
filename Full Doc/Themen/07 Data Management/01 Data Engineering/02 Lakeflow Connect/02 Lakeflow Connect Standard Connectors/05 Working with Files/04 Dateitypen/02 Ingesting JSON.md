### JSON Data Types
String,
Number (INT/FLOAT/DOUBLE),
Boolean,
Object,
Array of Objects

# Working with JSON-Formated Columns

We'll explore techniques to parse, extract, and manipulate those JSON strings using SQL or DataFrame operations.

```python
-- Step1: we read json File and save it
DROP TABLE IF EXISTS bronze_raw;


-- Create the Delta table
CREATE TABLE bronze_raw AS
SELECT *
FROM read_files(
  "/Volumes/dbacademy_ecommerce/v01/raw/events-kafka",
  format => "json"
);
```

```python
-- Step2: We decode it

CREATE OR REPLACE TABLE bronze_decoded AS
SELECT
  cast(unbase64(key) AS STRING) AS decoded_key,
  offset,
  partition,
  timestamp,
  topic,
  cast(unbase64(value) AS STRING) AS decoded_value
FROM bronze_raw;
```

## Approach 1: [Query JSON Strings](https://docs.databricks.com/aws/en/semi-structured/json)

One technique for working with a JSON-formatted string column is to access values directly from the STRING data type column.
- A column can simply store JSON data as a plain STRING
- Since it is stored as a string, the column can hold any JSON string without constraints
- However, this approach is **less performant compared to typed approaches like STRUCT**

```python
CREATE OR REPLACE TABLE bronze_string_flattened AS
SELECT
  decoded_key,
  offset,
  partition,
  timestamp,
  topic,
  decoded_value:device,
  decoded_value:traffic_source,
  decoded_value:geo,       ----- Contains another JSON formatted string
  decoded_value:items      ----- Contains a nested-array of JSON formatted strings
FROM bronze_decoded;
```

## Approach 2: STRUCT Data Type
Another method to work with a JSON-formatted string column is to convert the column to a STRUCT data type.

- You can parse JSON data into a STRUCT type by defining a schema
- The **STRUCT enforces the JSON schema**, ensuring data types and structure are consistent
- Querying a STRUCT is **more efficient than working with a raw JSON-formatted STRING**.

```python
-- Step 1: schema_of_json() function returns the schema inferred from a JSON-formatted string.
SELECT schema_of_json('{..}') AS schema

-- Step2:
CREATE OR REPLACE TABLE bronze_struct AS
SELECT 
  * EXCEPT (decoded_value),
  from_json(
      decoded_value,    -- JSON formatted string column
      'schema string') AS value
FROM bronze_decoded;


SELECT 
  decoded_key,
  value.device as device,  -- <----- Field
  value.geo.city as city,  -- <----- Nested-field from geo field
  value.items as items,
  array_size(items) AS number_elements_in_array -- <----- Count the number of elements in the array column items
FROM bronze_struct
ORDER BY number_elements_in_array DESC;
```

### [Explode Arrays](https://docs.databricks.com/aws/en/pyspark/reference/functions/explode)

Exploding an array transforms each element of an array column into a separate row, effectively flattening the array. There are a few things to keep in mind when using this function.
It returns a set of rows composed of the elements of the array or the keys and values of the map.
If the array is `NULL` no rows are produced. To return a single row with `NULL`s for the array or map values use the [explode_outer()](https://docs.databricks.com/gcp/en/sql/language-manual/functions/explode_outer) function.

Run the cell to see how the ARRAY of values in the `value.items` explodes the array into one row for each element in the array.

```python
CREATE OR REPLACE TABLE bronze_explode_array AS
SELECT
  decoded_key,
  array_size(value.items) AS number_elements_in_array,
  explode(value.items) AS item_in_array,
  value.items
FROM bronze_struct
ORDER BY number_elements_in_array DESC;
```

## Approach 3: VARIANT Data Type
The VARIANT data type is the newest approach for working with JSON data in Databricks.
As of 2025 Q2, VARIANT is in public preview. Key benefits include:

- Can store any type of data, including JSON, making it ideal for semi-structured data
- Highly flexible, adapting to different data shapes without rigid schemas
- Offers improved performance over existing methods (STRING and STRUCT)

**BENEFITS**
- **Open**- Fully open-sourced, no proprietary data lock-in.
- **Flexible** - No strict schema. You can put any type of semi-structured data into VARIANT.
- **Performant** - Improved performance over existing methods.

**CONSIDERATIONS**
- Currently in public preview as of 2025 Q2.
- [Variant support in Delta Lake](https://docs.databricks.com/aws/en/tables/features/variant)

RESOURCES:
- [Introducing the Open Variant Data Type in Delta Lake and Apache Spark](https://www.databricks.com/blog/introducing-open-variant-data-type-delta-lake-and-apache-spark)
- [Say goodbye to messy JSON headaches with VARIANT](https://www.youtube.com/watch?v=fWdxF7nL3YI)
- [Variant Data Type - Making Semi-Structured Data Fast and Simple](https://www.youtube.com/watch?v=jtjOfggD4YY)

NOTE: Variant data type will not work on Serverless Version 1.

Use the [parse_json](https://docs.databricks.com/aws/en/sql/language-manual/functions/parse_json) function to returns a VARIANT value from the JSON formatted string.

```python
CREATE OR REPLACE TABLE bronze_variant AS
SELECT
  decoded_key,
  offset,
  partition,
  timestamp,
  topic,
  parse_json(decoded_value) AS json_variant_value   -- Convert the decoded_value column to a variant data type
FROM bronze_decoded;
```

You can parse the VARIANT data type column using `:` to create your desired table.

[VARIANT type](https://docs.databricks.com/aws/en/sql/language-manual/data-types/variant-type)

```python
SELECT
  json_variant_value,
  json_variant_value:device :: STRING,  -- Obtain the value of device and cast to a string
  json_variant_value:items
FROM bronze_variant
LIMIT 10;
```

---

*Verschoben aus `_read_files.md`, Abschnitt 3 (Vollständige Optionsreferenz):*

### JSON-spezifische Optionen (Auswahl, gemeinsam mit `spark.read`)

| Option | Standardwert | Beschreibung |
|---|---|---|
| `mode` | `PERMISSIVE` | `PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`. |
| `multiLine` | `false` | Ob JSON-Datensätze mehrere Zeilen umfassen. |
| `columnNameOfCorruptRecord` | `_corrupt_record` | Spalte für nicht parsbare Datensätze. |
| `inferTimestamp` | `false` | Ob Zeitstempel-Strings als `TimestampType` inferiert werden sollen (kann die Inferenz spürbar verlangsamen). Bei Auto Loader zusätzlich `inferColumnTypes` aktivieren. |
| `prefersDecimal` | `false` | Versucht, Strings als `DecimalType` statt `float`/`double` zu inferieren. |
| `primitivesAsString` | `false` | Ob primitive Typen (Zahlen, Booleans) als `StringType` inferiert werden. |
| `dropFieldIfAllNull` | `false` | Ignoriert bei der Schema-Inferenz Spalten, die durchgehend `null`/leere Arrays/Structs sind. |
| `allowComments` | `false` | Ob Java-/C-/C++-Stil-Kommentare im JSON erlaubt sind. |
| `allowSingleQuotes` | `true` | Ob einfache Anführungszeichen für Strings erlaubt sind. |
| `maxNestingDepth` | `500` | Maximale Verschachtelungstiefe für JSON-Objekte/Arrays. |
| `singleVariantColumn` | keiner | Liest den gesamten JSON-Datensatz in eine einzelne `VARIANT`-Spalte. |
| `rescuedDataColumn` | keiner | Standardmäßig aktiv bei Auto Loader/`read_files`. |
| `upgradeExceptionAsBadRecord` | `false` | Behandelt Typ-Upgrade-Exceptions (z. B. Wert kann nicht auf den deklarierten Spaltentyp erweitert werden) als fehlerhaften Datensatz statt eine Exception zu werfen. |

---

*Verschoben aus `_spark_read.md`, Abschnitt 3 (Vollständige Optionsreferenz):*

### JSON-spezifische Optionen (Auswahl, `spark.read`)

| Option | Standardwert | Beschreibung |
|---|---|---|
| `mode` | `PERMISSIVE` | `PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`. |
| `multiLine` | `false` | Ob JSON-Datensätze mehrere Zeilen umfassen. |
| `columnNameOfCorruptRecord` | `_corrupt_record` | Spalte für nicht parsbare Datensätze. |
| `inferTimestamp` | `false` | Ob Zeitstempel-Strings als `TimestampType` inferiert werden. |
| `prefersDecimal` | `false` | Versucht, Strings als `DecimalType` statt `float`/`double` zu inferieren. |
| `primitivesAsString` | `false` | Ob primitive Typen (Zahlen, Booleans) als `StringType` inferiert werden. |
| `dropFieldIfAllNull` | `false` | Ignoriert bei der Schema-Inferenz Spalten, die durchgehend `null`/leere Arrays/Structs sind. |
| `allowComments` | `false` | Ob Java-/C-/C++-Stil-Kommentare im JSON erlaubt sind. |
| `allowSingleQuotes` | `true` | Ob einfache Anführungszeichen für Strings erlaubt sind. |
| `maxNestingDepth` | `500` | Maximale Verschachtelungstiefe für JSON-Objekte/Arrays. |
| `singleVariantColumn` | keiner | Liest den gesamten JSON-Datensatz in eine einzelne `VARIANT`-Spalte. |
| `rescuedDataColumn` | keiner | Bei `spark.read` **nicht** standardmäßig aktiv — muss explizit gesetzt werden. |
| `upgradeExceptionAsBadRecord` | `false` | Behandelt Typ-Upgrade-Exceptions als fehlerhaften Datensatz statt eine Exception zu werfen. |

```python
df = (spark.read
      .option("multiLine", True)
      .option("mode", "PERMISSIVE")
      .option("columnNameOfCorruptRecord", "_corrupt_record")
      .json("s3://bucket/path"))
```
