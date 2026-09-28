# `DataFrame.inputFiles()`

Gibt einen Best-Effort-Snapshot der Dateien zurück, aus denen dieser DataFrame besteht. Die Methode fragt jede zugrunde liegende `BaseRelation` nach ihren Dateien und bildet die Vereinigung aller Ergebnisse. Je nach Quell-Relation werden dabei eventuell nicht alle Eingabedateien gefunden. Duplikate werden entfernt.

## Signatur

```python
inputFiles()
```

## Rückgabewert

`list`: Liste von Dateipfaden.

## Beispiel

```python
import os
import tempfile
with tempfile.TemporaryDirectory(prefix="inputFiles") as d:
    spark.createDataFrame(
        [{"age": 100, "name": "Alice"}]
    ).repartition(1).write.json(d, mode="overwrite")

    df = spark.read.format("json").load(d)

    if os.environ.get('PYTEST_DBCONNECT_MODE') is None:
        len(df.inputFiles())
    else:
        1  # dbconnect doesn't support inputFiles.
# 1
```

## Quellen

- DataFrame.inputFiles: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/inputFiles

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
