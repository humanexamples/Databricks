# `DataFrameWriter.partitionBy()`

Partitioniert die Ausgabe im Dateisystem nach den angegebenen Spalten, gemäß Hive's Partitionierungsschema (`spalte=wert`-Unterverzeichnisse).

## Signatur

```python
partitionBy(*cols)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `*cols` | `str` oder `list` | Namen der Spalten, nach denen partitioniert werden soll. |

## Rückgabewert

`DataFrameWriter`

## Beispiel

```python
import tempfile, os
with tempfile.TemporaryDirectory(prefix="partitionBy") as d:
    spark.createDataFrame(
        [{"age": 100, "name": "Alice"}, {"age": 120, "name": "Ruifeng Zheng"}]
    ).write.partitionBy("name").mode("overwrite").format("parquet").save(d)
    spark.read.parquet(d).sort("age").show()
    # +---+-------------+
    # |age|         name|
    # +---+-------------+
    # |100| Alice|
    # |120|Ruifeng Zheng|
    # +---+-------------+
    # Read one partition as a DataFrame.
    spark.read.parquet(f"{d}{os.path.sep}name=Alice").show()
    # +---+
    # |age|
    # +---+
    # |100|
    # +---+
```

Das Beispiel zeigt, dass sich eine einzelne Partition auch direkt über ihren Unterordner (`name=Alice`) gezielt einlesen lässt.

## Quellen

- DataFrameWriter.partitionBy: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/partitionBy

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
