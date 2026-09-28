# `DataFrameWriter.insertInto()`

Fügt den Inhalt des DataFrames in eine bereits existierende Tabelle ein.

## Signatur

```python
insertInto(tableName, overwrite=None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `tableName` | `str` | Name der Zieltabelle. |
| `overwrite` | `bool`, optional | Wenn `True`, werden bestehende Daten überschrieben. Standardmäßig deaktiviert. |

## Rückgabewert

`None`

## Wichtiger Hinweis

> Anders als `DataFrameWriter.saveAsTable` ignoriert `DataFrameWriter.insertInto` die Spaltennamen und verwendet eine **positionsbasierte** Auflösung.

Das bedeutet: Die Spalten werden anhand ihrer Reihenfolge in die Zieltabelle geschrieben, nicht anhand ihrer Namen — auch wenn die Namen im DataFrame anders lauten als in der Tabelle.

## Beispiel

```python
spark.sql("DROP TABLE IF EXISTS tblA")
df = spark.createDataFrame([
    (100, "Alice"), (120, "Alice"), (140, "Bob")],
    schema=["age", "name"])
df.write.saveAsTable("tblA")
df.selectExpr("age AS col1", "name AS col2").write.insertInto("tblA")
spark.read.table("tblA").sort("age").show()
# +---+------------+
# |age|        name|
# +---+------------+
# |100|      Alice|
# |100|      Alice|
# |120|      Alice|
# |120|      Alice|
# |140|        Bob|
# |140|        Bob|
# +---+------------+
spark.sql("DROP TABLE tblA")
```

Im Beispiel werden die Spalten `col1`/`col2` trotz abweichender Namen positionsbasiert in `age`/`name` von `tblA` geschrieben — daher verdoppelt sich die Tabelle nach dem `insertInto`-Aufruf.

## Quellen

- DataFrameWriter.insertInto: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/insertInto

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
