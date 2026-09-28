# `DataStreamWriter.toTable()`

Startet die Ausführung der Streaming-Query und gibt ihr Ergebnis kontinuierlich in die angegebene Tabelle aus, sobald neue Daten eintreffen. Liefert ein `StreamingQuery`-Objekt zurück.

## Signatur

```python
toTable(tableName, format=None, outputMode=None, partitionBy=None, queryName=None, **options)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `tableName` | `str` | Name der Tabelle. |
| `format` | `str`, optional | Format, in dem gespeichert wird. |
| `outputMode` | `str`, optional | Wie Daten in die Senke geschrieben werden: `append`, `complete` oder `update`. |
| `partitionBy` | `str` oder `list`, optional | Namen der Partitionierungsspalten. Wird bei bereits existierenden v2-Tabellen ignoriert. |
| `queryName` | `str`, optional | Eindeutiger Name für die Query. |
| `**options` | — | Alle weiteren String-Optionen. Für die meisten Streams `checkpointLocation` angeben. |

## Rückgabewert

`StreamingQuery`

## Hinweise

Bei v1-Tabellen werden die `partitionBy`-Spalten immer berücksichtigt. Bei v2-Tabellen wird `partitionBy` nur berücksichtigt, wenn die Tabelle noch nicht existiert.

## Beispiel

```python
import tempfile
import time

_ = spark.sql("DROP TABLE IF EXISTS my_table2")
with tempfile.TemporaryDirectory(prefix="toTable") as d:
    q = spark.readStream.format("rate").option(
        "rowsPerSecond", 10).load().writeStream.toTable(
            "my_table2",
            queryName='that_query',
            outputMode="append",
            format='parquet',
            checkpointLocation=d)
    time.sleep(3)
    q.stop()
    spark.read.table("my_table2").show()
    _ = spark.sql("DROP TABLE my_table2")
```

## Quellen

- DataStreamWriter.toTable: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/toTable

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
