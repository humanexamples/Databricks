# `DataFrame.transpose()`

Transponiert einen DataFrame so, dass die Werte der angegebenen Indexspalte zu den neuen Spalten des DataFrames werden. Ohne Indexspalte wird standardmäßig die erste Spalte verwendet.

## Signatur

```python
transpose(indexColumn: Optional["ColumnOrName"] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `indexColumn` | `str` oder `Column`, optional | Die einzelne Spalte, die als Index für die Transposition dient. Ihre Werte werden zu den neuen Spalten des transponierten DataFrames. Ohne Angabe wird die erste Spalte des DataFrames verwendet. |

## Rückgabewert

`DataFrame`: Transponierter DataFrame.

## Hinweise

- Alle Spalten außer der Indexspalte müssen einen gemeinsamen kleinsten Datentyp haben. Sind sie nicht vom selben Typ, werden alle in den nächstgelegenen gemeinsamen Datentyp gecastet.
- Die Spalte, in die die ursprünglichen Spaltennamen transponiert werden, heißt standardmäßig `"key"`.
- NULL-Werte in der Indexspalte werden bei den Spaltennamen der transponierten Tabelle ausgelassen; die Spaltennamen werden aufsteigend sortiert.
- Unterstützt Spark Connect.

## Beispiel

```python
df = spark.createDataFrame(
    [("A", 1, 2), ("B", 3, 4)],
    ["id", "val1", "val2"],
)
df.show()
# +---+----+----+
# | id|val1|val2|
# +---+----+----+
# |  A|   1|   2|
# |  B|   3|   4|
# +---+----+----+

df.transpose().show()
# +----+---+---+
# | key|  A|  B|
# +----+---+---+
# |val1|  1|  3|
# |val2|  2|  4|
# +----+---+---+

df.transpose(df.id).show()
# +----+---+---+
# | key|  A|  B|
# +----+---+---+
# |val1|  1|  3|
# |val2|  2|  4|
# +----+---+---+
```

## Quellen

- DataFrame.transpose: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/transpose

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
