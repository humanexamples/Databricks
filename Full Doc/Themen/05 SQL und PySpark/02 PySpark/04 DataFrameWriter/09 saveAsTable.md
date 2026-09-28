# `DataFrameWriter.saveAsTable()`

Speichert den Inhalt des DataFrames als die angegebene Tabelle (z. B. in Unity Catalog).

## Signatur

```python
saveAsTable(name, format=None, mode=None, partitionBy=None, **options)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `name` | `str` | Der Tabellenname. |
| `format` | `str`, optional | Format, in dem gespeichert wird. |
| `mode` | `str`, optional | Verhalten, wenn Daten bereits existieren. Zulässige Werte: `'append'`, `'overwrite'`, `'error'`/`'errorifexists'` (Standard), `'ignore'`. |
| `partitionBy` | `str` oder `list`, optional | Namen der Partitionierungsspalten. |
| `**options` | `dict` | Zusätzliche String-Optionen. |

## Rückgabewert

`None`

## Beispiel

```python
spark.sql("DROP TABLE IF EXISTS tblA")
spark.createDataFrame([
    (100, "Alice"), (120, "Bob"), (140, "Tom")],
    schema=["age", "name"]
).write.saveAsTable("tblA")
spark.read.table("tblA").sort("age").show()
# +---+------------+
# |age|        name|
# +---+------------+
# |100|       Alice|
# |120|        Bob|
# |140|        Tom|
# +---+------------+
spark.sql("DROP TABLE tblA")
```

## Abgrenzung zu `insertInto`

Anders als `insertInto` löst `saveAsTable` die Zielspalten **namensbasiert** auf; `insertInto` löst sie **positionsbasiert** auf. Siehe [10 insertInto.md](10%20insertInto.md).

## Quellen

- DataFrameWriter.saveAsTable: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/saveAsTable

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
