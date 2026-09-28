# `DataStreamReader.schema()`

Legt das Eingabeschema fest.

## Signatur

```python
schema(schema)
```

## Beschreibung

Legt das Eingabeschema fest. Manche Datenquellen können dadurch die Schema-Inferenz überspringen und das Laden der Daten beschleunigen (*"skip schema inference and speed up data loading"*).

Für dateibasierte Streaming-Quellen ist ein Schema in der Regel **erforderlich** (Ausnahme: Auto Loader mit `cloudFiles.schemaLocation` inferiert selbst).

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `schema` | `StructType` oder `str` | Ein `StructType`-Objekt oder ein DDL-formatierter String wie `col0 INT, col1 DOUBLE`. |

## Rückgabewert

`DataStreamReader`

## Beispiele

```python
from pyspark.sql.types import StructField, StructType, StringType
spark.readStream.schema(StructType([StructField("data", StringType(), True)]))
spark.readStream.schema("col0 INT, col1 DOUBLE")
```

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="schema") as d:
    spark.readStream.schema("col0 INT, col1 STRING").format("csv").load(d).printSchema()
# root
#  |-- col0: integer (nullable = true)
#  |-- col1: string (nullable = true)
```

## Quellen

- DataStreamReader.schema: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/schema

**Stand:** 2026-09-14, per `WebFetch` verifiziert.
