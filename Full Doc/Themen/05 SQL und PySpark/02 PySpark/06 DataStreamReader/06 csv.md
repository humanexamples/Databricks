# `DataStreamReader.csv()`

Lädt einen CSV-Datei-Stream und gibt das Ergebnis als DataFrame zurück.

## Signatur

```python
csv(path, schema=None, **options)
```

## Beschreibung

*"Loads a CSV file stream and returns the result as a DataFrame. If `inferSchema` is enabled, the function goes through the input once to determine the schema. To avoid this pass, disable `inferSchema` or specify the schema explicitly using `schema`."*

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str` | Pfad für die CSV-Eingabe. |
| `schema` | `StructType` oder `str`, optional | Schema als `StructType` oder DDL-String (z. B. `col0 INT, col1 DOUBLE`). |

Wichtige `**options` (`header`, `inferSchema`, `sep`, `encoding`, `multiLine`, `mode`, `rescuedDataColumn` …) werden per `.option()`/`.options()` gesetzt — siehe [03 option.md](03%20option.md) und die [Spark-API-Optionsreferenz](https://docs.databricks.com/aws/en/spark/api-options).

## Rückgabewert

`DataFrame`

## Beispiel

```python
import tempfile
import time
with tempfile.TemporaryDirectory(prefix="csv") as d:
    spark.createDataFrame([(100, "Hyukjin Kwon"),], ["age", "name"]) \
        .write.mode("overwrite").format("csv").save(d)
    q = spark.readStream.schema(
        "age INT, name STRING"
    ).csv(d).writeStream.format("console").start()
    time.sleep(3)
    q.stop()
```

## Quellen

- DataStreamReader.csv: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/csv

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
