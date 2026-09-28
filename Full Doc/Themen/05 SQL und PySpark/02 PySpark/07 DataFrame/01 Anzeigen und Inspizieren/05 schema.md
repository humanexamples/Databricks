# `DataFrame.schema` (Eigenschaft)

Gibt das Schema dieses `DataFrame` als `StructType` zurück.

## Rückgabewert

`StructType`

## Beispiele

Das inferierte Schema des aktuellen DataFrames abrufen:

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df.schema
# StructType([StructField('age', LongType(), True),
#             StructField('name', StringType(), True)])
```

Das Schema des aktuellen DataFrames aus einem DDL-formatierten Schema-String abrufen:

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")],
    "age INT, name STRING")
df.schema
# StructType([StructField('age', IntegerType(), True),
#             StructField('name', StringType(), True)])
```

Das explizit angegebene Schema des aktuellen DataFrames abrufen:

```python
from pyspark.sql.types import StructType, StructField, StringType
df = spark.createDataFrame(
    [("a",), ("b",), ("c",)],
    StructType([StructField("value", StringType(), False)]))
df.schema
# StructType([StructField('value', StringType(), False)])
```

Siehe auch [`printSchema`](02%20printSchema.md), [`dtypes`](04%20dtypes.md).

## Quellen

- DataFrame.schema: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/schema

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
