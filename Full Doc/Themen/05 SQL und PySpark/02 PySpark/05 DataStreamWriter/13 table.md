# `DataStreamWriter.table()`

Alias für [`toTable()`](12%20toTable.md). Startet die Ausführung der Streaming-Query und gibt ihr Ergebnis kontinuierlich in die angegebene Tabelle aus, sobald neue Daten eintreffen.

## Signatur

```python
table(tableName)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `tableName` | `str` | Name der Tabelle. |

## Rückgabewert

`StreamingQuery`

## Beispiel

```python
df = spark.readStream.format("rate").load()
q = (df.writeStream
       .option("checkpointLocation", "/Volumes/catalog/schema/_chk/rate")
       .table("catalog.schema.rate_events"))
```

## Quellen

- DataStreamWriter.table: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/table

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
