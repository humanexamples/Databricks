# `DataFrameReader.option()`

Fügt eine einzelne Option für die zugrunde liegende Datenquelle hinzu.

## Signatur

```python
option(key, value)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `key` | `str` | Der Options-Schlüssel. |
| `value` | `str`, `int`, `float` oder `bool` | Der Options-Wert. |

## Rückgabewert

`DataFrameReader`

## Verfügbare Optionen (Common)

Die folgenden Optionen gelten laut [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options) formatübergreifend für die meisten Batch-Lesevorgänge (`spark.read`, `read_files`, `COPY INTO`):

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `ignoreCorruptFiles` | `false` | boolean | „Whether to ignore corrupt files. If true, the Spark jobs will continue to run when encountering corrupted files" (ab Databricks Runtime 11.3 LTS). |
| `ignoredPathSegmentRegex` | `^[._]` | Regex-String | „Controls which files and directories are skipped as hidden during file listing" (ab Databricks Runtime 19). |
| `ignoreMissingFiles` | `false` (Auto Loader); `true` (COPY INTO, Legacy) | boolean | „Whether to ignore missing files. If true, the Spark jobs continue to run when encountering missing files" (ab Databricks Runtime 11.3 LTS). |
| `modifiedAfter` | `None` | Timestamp | „An optional timestamp as a filter to only ingest files that have a modification timestamp after the specified timestamp." |
| `modifiedBefore` | `None` | Timestamp | „An optional timestamp as a filter to only ingest files that have a modification timestamp before the specified timestamp." |
| `pathGlobFilter` / `fileNamePattern` | `None` | Glob-Muster | „A potential glob pattern for choosing files." |
| `recursiveFileLookup` | `false` | boolean | „When `true`, this option searches through nested directories even if their names do not follow a partition naming scheme." |

Darüber hinaus akzeptiert `option()`/`options()` **formatspezifische** Schlüssel (z. B. `header`/`inferSchema`/`sep` für CSV, `multiLine` für JSON, `mergeSchema` für Parquet) — vollständige, formatspezifische Optionstabellen stehen in [07 Data Management/.../03 Spark API Options/](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/) (je eine Datei für Avro, CSV, Excel, JSON, Kafka, ORC, Parquet, State store, Text, XML).

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="option") as d:
    df = spark.createDataFrame([{"age": 100, "name": "Alice"}])
    df.write.mode("overwrite").format("csv").save(d)
    spark.read.schema(df.schema).option(
        "nullValue", "Alice").format('csv').load(d).show()
    # +---+----+
    # |age|name|
    # +---+----+
    # |100|NULL|
    # +---+----+
```

Für die vollständige Liste verfügbarer Optionen verweist die Dokumentation auf die `DataFrameReader`-Batch-Read-Optionen (`/aws/en/spark/api-options#batch-read-options`).

## Quellen

- DataFrameReader.option: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader/option

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
