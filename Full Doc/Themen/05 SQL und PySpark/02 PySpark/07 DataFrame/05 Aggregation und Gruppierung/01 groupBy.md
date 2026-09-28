# `DataFrame.groupBy()`

Gruppiert den DataFrame nach den angegebenen Spalten, damit darauf Aggregationen ausgeführt werden können. Alle verfügbaren Aggregatfunktionen siehe `GroupedData`.

## Signatur

```python
groupBy(*cols: "ColumnOrNameOrOrdinal")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `cols` | `list`, `str`, `int` oder `Column` | Die Gruppierungsspalten. Jedes Element kann ein Spaltenname (String), ein Ausdruck (`Column`), eine Spaltenordinalzahl (`int`, 1-basiert) oder eine Liste davon sein. |

## Rückgabewert

`GroupedData`: Objekt, das die nach den angegebenen Spalten gruppierten Daten repräsentiert.

## Hinweise

Spaltenordinalzahlen beginnen bei 1 – anders als das 0-basierte `__getitem__`.

## Beispiel

```python
df = spark.createDataFrame([
    ("Alice", 2), ("Bob", 2), ("Bob", 2), ("Bob", 5)], schema=["name", "age"])

df.groupBy().avg().show()
# +--------+
# |avg(age)|
# +--------+
# |    2.75|
# +--------+

df.groupBy("name").agg({"age": "sum"}).sort("name").show()
# +-----+--------+
# | name|sum(age)|
# +-----+--------+
# |Alice|       2|
# |  Bob|       9|
# +-----+--------+

df.groupBy(df.name).max().sort("name").show()
# +-----+--------+
# | name|max(age)|
# +-----+--------+
# |Alice|       2|
# |  Bob|       5|
# +-----+--------+

df.groupBy(["name", df.age]).count().sort("name", "age").show()
# +-----+---+-----+
# | name|age|count|
# +-----+---+-----+
# |Alice|  2|    1|
# |  Bob|  2|    2|
# |  Bob|  5|    1|
# +-----+---+-----+
```

Siehe auch [`agg`](02%20agg.md), [`rollup`](03%20rollup.md), [`cube`](04%20cube.md), [`groupingSets`](05%20groupingSets.md).

## Quellen

- DataFrame.groupBy: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/groupBy

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
