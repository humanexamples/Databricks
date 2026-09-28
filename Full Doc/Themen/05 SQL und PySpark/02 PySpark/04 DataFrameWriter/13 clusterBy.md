# `DataFrameWriter.clusterBy()`

Clustert die Daten beim Schreiben nach den angegebenen Spalten, um die spätere Query-Performance zu optimieren (Liquid Clustering).

## Signatur

```python
clusterBy(*cols)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `*cols` | `str` oder `list` | Namen der Spalten, nach denen geclustert werden soll. |

## Rückgabewert

`DataFrameWriter`

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="clusterBy") as d:
    spark.createDataFrame(
        [{"age": 100, "name": "Alice"}, {"age": 120, "name": "Ruifeng Zheng"}]
    ).write.clusterBy("name").mode("overwrite").format("parquet").save(d)
```

Das Beispiel schreibt ein DataFrame als Parquet-Datei, geclustert nach der Spalte `name`.

## Quellen

- DataFrameWriter.clusterBy: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/clusterBy

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
